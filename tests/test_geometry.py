import math
import unittest

from geometry import distance, length, segment_distance


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


class LengthTests(unittest.TestCase):
    def test_empty_points_have_zero_length(self):
        self.assertEqual(length([]), 0.0)

    def test_one_point_has_zero_length(self):
        self.assertEqual(length([(3, 4)]), 0.0)

    def test_two_points_use_distance(self):
        self.assertEqual(length([(0, 0), (3, 4)]), 5.0)

    def test_adds_each_segment_instead_of_endpoint_distance(self):
        self.assertEqual(length([(0, 0), (3, 4), (6, 4)]), 8.0)

    def test_repeated_points_do_not_add_length(self):
        self.assertEqual(length([(0, 0), (0, 0), (3, 4)]), 5.0)

    def test_does_not_automatically_close_line(self):
        self.assertEqual(length([(0, 0), (3, 0), (3, 4)]), 7.0)

    def test_explicit_return_to_start_counts_final_segment(self):
        self.assertEqual(length([(0, 0), (3, 0), (3, 4), (0, 0)]), 12.0)

    def test_input_order_changes_line_length(self):
        self.assertEqual(length([(0, 0), (6, 0), (3, 0)]), 9.0)

    def test_does_not_modify_input(self):
        points = [(0, 0), (3, 4), (6, 4)]
        original = points.copy()
        length(points)
        self.assertEqual(points, original)


class SegmentDistanceTests(unittest.TestCase):
    def test_horizontal_segment_interior_projection(self):
        self.assertEqual(segment_distance((3, 4), (0, 0), (6, 0)), 4.0)

    def test_vertical_segment(self):
        self.assertEqual(segment_distance((-4, 3), (0, 0), (0, 6)), 4.0)

    def test_diagonal_segment(self):
        self.assertAlmostEqual(segment_distance((3, 0), (0, 0), (4, 4)), math.sqrt(4.5))

    def test_point_on_segment_has_zero_distance(self):
        self.assertEqual(segment_distance((3, 0), (0, 0), (6, 0)), 0.0)

    def test_projection_before_start_uses_start(self):
        self.assertEqual(segment_distance((-3, 4), (0, 0), (6, 0)), 5.0)

    def test_projection_after_end_uses_end(self):
        self.assertEqual(segment_distance((9, 4), (0, 0), (6, 0)), 5.0)

    def test_point_on_extended_line_still_has_distance_to_segment(self):
        self.assertEqual(segment_distance((9, 0), (0, 0), (6, 0)), 3.0)

    def test_identical_endpoints_use_point_distance(self):
        self.assertEqual(segment_distance((3, 4), (0, 0), (0, 0)), 5.0)

    def test_reversing_endpoints_preserves_distance(self):
        self.assertEqual(segment_distance((9, 4), (6, 0), (0, 0)), 5.0)

    def test_translation_preserves_distance(self):
        self.assertEqual(segment_distance((13, 24), (10, 20), (16, 20)), 4.0)

    def test_tiny_nonzero_segment_is_not_treated_as_zero(self):
        gap = segment_distance((5e-201, 4e-201), (0, 0), (1e-200, 0))
        self.assertAlmostEqual(gap / 1e-201, 4.0)

    def test_unrepresentable_segment_length_is_rejected(self):
        with self.assertRaises(ValueError):
            segment_distance((0, 0), (-1e308, 0), (1e308, 0))


if __name__ == "__main__":
    unittest.main()
