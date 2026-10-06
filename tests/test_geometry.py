import unittest

from geometry import distance


class DistanceTests(unittest.TestCase):
    def test_diagonal_distance(self):
        self.assertEqual(distance((0, 0), (3, 4)), 5.0)

    def test_same_point_has_zero_distance(self):
        self.assertEqual(distance((7, 9), (7, 9)), 0.0)

    def test_vertical_distance_with_negative_coordinates(self):
        self.assertEqual(distance((-2, -5), (-2, 3)), 8.0)

    def test_direction_and_position_do_not_change_distance(self):
        self.assertEqual(distance((3, 4), (0, 0)), 5.0)
        self.assertEqual(distance((10, 20), (13, 24)), 5.0)


if __name__ == "__main__":
    unittest.main()
