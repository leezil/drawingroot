import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from server import TestHandler


class LocalServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path, body=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            connection.request(method, path, body, {"Content-Type": "application/json"})
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def test_serves_test_screen(self):
        status, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("선 전체 길이 테스트", body.decode("utf-8"))

    def test_returns_python_length_and_segments(self):
        status, body = self.request("POST", "/api/length", json.dumps({"points": [[0, 0], [3, 4], [6, 4]]}))
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"length": 8.0, "segments": [5.0, 3.0], "point_count": 3})

    def test_empty_points_return_zero(self):
        status, body = self.request("POST", "/api/length", '{"points": []}')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["length"], 0.0)

    def test_rejects_invalid_coordinate_types(self):
        for points in ([[True, 0]], [["3", 4]], [[1]], None, [[float("inf"), 0]]):
            with self.subTest(points=points):
                status, body = self.request("POST", "/api/length", json.dumps({"points": points}))
                self.assertEqual(status, 400)
                self.assertIn("error", json.loads(body))

    def test_rejects_malformed_json(self):
        status, body = self.request("POST", "/api/length", "not json")
        self.assertEqual(status, 400)
        self.assertIn("error", json.loads(body))

    def test_does_not_serve_source_or_env_files(self):
        for path in ("/geometry.py", "/.env", "/../README.md"):
            with self.subTest(path=path):
                status, _ = self.request("GET", path)
                self.assertEqual(status, 404)

    def test_returns_point_to_segment_distance(self):
        payload = {"point": [3, 4], "start": [0, 0], "end": [6, 0]}
        status, body = self.request("POST", "/api/segment-distance", json.dumps(payload))
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"distance": 4.0})

    def test_segment_endpoint_and_degenerate_cases(self):
        cases = (
            ({"point": [9, 0], "start": [0, 0], "end": [6, 0]}, 3.0),
            ({"point": [3, 4], "start": [0, 0], "end": [0, 0]}, 5.0),
        )
        for payload, expected in cases:
            with self.subTest(payload=payload):
                status, body = self.request("POST", "/api/segment-distance", json.dumps(payload))
                self.assertEqual(status, 200)
                self.assertEqual(json.loads(body)["distance"], expected)

    def test_rejects_missing_or_invalid_segment_coordinates(self):
        for point in (None, [1], [True, 4], [float("nan"), 4], ["3", 4]):
            with self.subTest(point=point):
                payload = {"point": point, "start": [0, 0], "end": [6, 0]}
                status, body = self.request("POST", "/api/segment-distance", json.dumps(payload))
                self.assertEqual(status, 400)
                self.assertIn("error", json.loads(body))
        status, _ = self.request("POST", "/api/segment-distance", '{"point": [3,4]}')
        self.assertEqual(status, 400)

    def test_unrepresentable_segment_returns_error(self):
        payload = {"point": [0, 0], "start": [-1e308, 0], "end": [1e308, 0]}
        status, body = self.request("POST", "/api/segment-distance", json.dumps(payload))
        self.assertEqual(status, 400)
        self.assertIn("error", json.loads(body))


    def test_returns_point_to_polyline_distance(self):
        payload = {"point": [4, 4], "points": [[0, 0], [6, 0], [6, 6]]}
        status, body = self.request("POST", "/api/polyline-distance", json.dumps(payload))
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"distance": 2.0})

    def test_polyline_with_one_point_returns_distance(self):
        payload = {"point": [3, 4], "points": [[0, 0]]}
        status, body = self.request("POST", "/api/polyline-distance", json.dumps(payload))
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["distance"], 5.0)

    def test_empty_polyline_returns_error_not_zero(self):
        payload = {"point": [3, 4], "points": []}
        status, body = self.request("POST", "/api/polyline-distance", json.dumps(payload))
        self.assertEqual(status, 400)
        self.assertIn("error", json.loads(body))

    def test_rejects_invalid_polyline_inputs(self):
        cases = (
            {"points": [[0, 0], [6, 0]]},
            {"point": [4, 4]},
            {"point": [True, 4], "points": [[0, 0]]},
            {"point": [4, 4], "points": "not a list"},
            {"point": [4, 4], "points": [[0, 0], [6]]},
            {"point": [4, 4], "points": [[float("inf"), 0]]},
        )
        for payload in cases:
            with self.subTest(payload=payload):
                status, body = self.request("POST", "/api/polyline-distance", json.dumps(payload))
                self.assertEqual(status, 400)
                self.assertIn("error", json.loads(body))

    def test_polyline_point_count_limit_excludes_query_point(self):
        payload = {"point": [3, 4], "points": [[0, 0]] * 1000}
        status, body = self.request("POST", "/api/polyline-distance", json.dumps(payload))
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["distance"], 5.0)
        payload["points"].append([0, 0])
        status, _ = self.request("POST", "/api/polyline-distance", json.dumps(payload))
        self.assertEqual(status, 400)


    def test_returns_resampled_points_and_spacing(self):
        payload = {"points": [[0, 0], [1, 0], [9, 0], [10, 0]], "count": 6}
        status, body = self.request("POST", "/api/resample", json.dumps(payload))
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"points": [[0, 0], [2, 0], [4, 0], [6, 0], [8, 0], [10, 0]],
                                           "point_count": 6, "spacing": 2.0})

    def test_resample_zero_length_line_returns_repeated_points(self):
        payload = {"points": [[3, 4]], "count": 3}
        status, body = self.request("POST", "/api/resample", json.dumps(payload))
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"points": [[3, 4]] * 3, "point_count": 3, "spacing": 0.0})

    def test_resample_empty_line_returns_error(self):
        status, body = self.request("POST", "/api/resample", '{"points": [], "count": 6}')
        self.assertEqual(status, 400)
        self.assertIn("error", json.loads(body))

    def test_rejects_invalid_or_missing_resample_count(self):
        for count in (None, 0, 1, -1, True, 6.0, "6", 1001):
            with self.subTest(count=count):
                payload = {"points": [[0, 0], [10, 0]], "count": count}
                status, body = self.request("POST", "/api/resample", json.dumps(payload))
                self.assertEqual(status, 400)
                self.assertIn("error", json.loads(body))

    def test_resample_api_allows_maximum_count(self):
        payload = {"points": [[0, 0], [10, 0]], "count": 1000}
        status, body = self.request("POST", "/api/resample", json.dumps(payload))
        self.assertEqual(status, 200)
        sampled = json.loads(body)["points"]
        self.assertEqual(len(sampled), 1000)
        self.assertEqual(sampled[0], [0, 0])
        self.assertEqual(sampled[-1], [10, 0])

    def test_rejects_invalid_resample_coordinates(self):
        for points in (None, "bad", [[0]], [[True, 0]], [[float("nan"), 0]], [[0, 0]] * 1001):
            with self.subTest(points=points):
                payload = {"points": points, "count": 6}
                status, body = self.request("POST", "/api/resample", json.dumps(payload))
                self.assertEqual(status, 400)
                self.assertIn("error", json.loads(body))


if __name__ == "__main__":
    unittest.main()
