"""기하 함수를 직접 확인하는 로컬 전용 HTTP 서버: python server.py."""

import json
import math
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from geometry import distance, frechet, length, mean_distance, polyline_distance, resample, segment_distance, symmetric_mean_distance


class TestHandler(BaseHTTPRequestHandler):
    def respond(self, status, body, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/":
            self.respond(404, b'{"error":"Not found"}')
            return
        page = Path(__file__).with_name("index.html").read_bytes()
        self.respond(200, page, "text/html; charset=utf-8")

    def do_POST(self):
        if self.path not in ("/api/length", "/api/segment-distance", "/api/polyline-distance", "/api/resample", "/api/mean-distance", "/api/symmetric-mean-distance", "/api/frechet"):
            self.respond(404, b'{"error":"Not found"}')
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 65536:
                raise ValueError("입력은 1~65,536바이트 이내여야 합니다.")
            payload = json.loads(self.rfile.read(size).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("좌표를 포함한 JSON 객체를 보내주세요.")
            if self.path in ("/api/length", "/api/polyline-distance", "/api/resample"):
                points = payload.get("points")
            elif self.path in ("/api/mean-distance", "/api/symmetric-mean-distance", "/api/frechet"):
                points = payload.get("source")
            else:
                points = [payload.get("point"), payload.get("start"), payload.get("end")]
            if not isinstance(points, list) or len(points) > 1000:
                raise ValueError("좌표 목록은 최대 1,000개의 점을 담은 배열이어야 합니다.")
            validation_points = points
            if self.path == "/api/polyline-distance":
                validation_points = [payload.get("point")] + points
            elif self.path in ("/api/mean-distance", "/api/symmetric-mean-distance", "/api/frechet"):
                target = payload.get("target")
                if not isinstance(target, list) or len(target) > 1000:
                    raise ValueError("비교할 선은 최대 1,000개의 점을 담은 배열이어야 합니다.")
                validation_points = points + target
            for point in validation_points:
                if not isinstance(point, list) or len(point) != 2:
                    raise ValueError("각 점은 [x, y] 형태여야 합니다.")
                for value in point:
                    if type(value) not in (int, float) or not math.isfinite(value):
                        raise ValueError("좌표에는 유한한 숫자만 입력해주세요.")
            if self.path == "/api/length":
                total = length(points)
                if not math.isfinite(total):
                    raise ValueError("계산 가능한 범위를 넘었습니다. 좌표 크기를 줄여주세요.")
                segments = [distance(points[i - 1], points[i]) for i in range(1, len(points))]
                result = {"length": total, "segments": segments, "point_count": len(points)}
            elif self.path == "/api/frechet":
                gap = frechet(points, target)
                result = {"frechet_distance": gap, "source_point_count": len(points),
                          "target_point_count": len(target)}
            elif self.path in ("/api/mean-distance", "/api/symmetric-mean-distance"):
                count = payload.get("count", 64)
                if type(count) is not int or not 2 <= count <= 1000:
                    raise ValueError("샘플 점 개수는 2~1,000 사이의 정수여야 합니다.")
                if self.path == "/api/mean-distance":
                    gap = mean_distance(points, target, count)
                    result = {"mean_distance": gap, "sample_count": count}
                else:
                    gap = symmetric_mean_distance(points, target, count)
                    result = {"symmetric_mean_distance": gap, "sample_count": count}
            elif self.path == "/api/resample":
                count = payload.get("count")
                if type(count) is not int or not 2 <= count <= 1000:
                    raise ValueError("새 점 개수는 2~1,000 사이의 정수여야 합니다.")
                sampled = resample(points, count)
                result = {"points": sampled, "point_count": len(sampled),
                          "spacing": length(points) / (count - 1)}
            else:
                if self.path == "/api/segment-distance":
                    gap = segment_distance(points[0], points[1], points[2])
                else:
                    gap = polyline_distance(payload["point"], points)
                if not math.isfinite(gap):
                    raise ValueError("계산 가능한 범위를 넘었습니다. 좌표 크기를 줄여주세요.")
                result = {"distance": gap}
            self.respond(200, json.dumps(result, allow_nan=False).encode("utf-8"))
        except (ValueError, TypeError, OverflowError) as error:
            body = json.dumps({"error": str(error)}, ensure_ascii=False).encode("utf-8")
            self.respond(400, body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8081), TestHandler)
    print("drawingroot 로컬 테스트: http://localhost:8081/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
