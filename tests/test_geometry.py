import math
import unittest

from geometry import distance, length, polyline_distance, resample, segment_distance


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


class PolylineDistanceTests(unittest.TestCase):
    def test_uses_nearest_segment_not_first_segment(self):
        self.assertEqual(polyline_distance((4, 4), [(0, 0), (6, 0), (6, 6)]), 2.0)

    def test_nearest_location_can_be_inside_segment(self):
        self.assertEqual(polyline_distance((3, 4), [(0, 0), (6, 0)]), 4.0)

    def test_point_on_line_has_zero_distance(self):
        self.assertEqual(polyline_distance((6, 3), [(0, 0), (6, 0), (6, 6)]), 0.0)

    def test_one_point_uses_point_distance(self):
        self.assertEqual(polyline_distance((3, 4), [(0, 0)]), 5.0)

    def test_empty_line_is_rejected(self):
        with self.assertRaises(ValueError):
            polyline_distance((3, 4), [])

    def test_repeated_points_are_supported(self):
        self.assertEqual(polyline_distance((3, 4), [(0, 0), (0, 0), (6, 0)]), 4.0)

    def test_line_with_only_repeated_points(self):
        self.assertEqual(polyline_distance((3, 4), [(0, 0), (0, 0)]), 5.0)

    def test_line_does_not_automatically_close(self):
        self.assertEqual(polyline_distance((3, 3), [(0, 0), (6, 0), (6, 6)]), 3.0)

    def test_explicit_closing_segment_is_included(self):
        gap = polyline_distance((3, 3), [(0, 0), (6, 0), (6, 6), (0, 0)])
        self.assertAlmostEqual(gap, 0.0)

    def test_reversing_line_preserves_distance(self):
        self.assertEqual(polyline_distance((4, 4), [(6, 6), (6, 0), (0, 0)]), 2.0)

    def test_point_beyond_endpoint(self):
        self.assertEqual(polyline_distance((9, 10), [(0, 0), (6, 0), (6, 6)]), 5.0)

    def test_input_is_not_modified(self):
        points = [(0, 0), (6, 0), (6, 6)]
        original = points.copy()
        polyline_distance((4, 4), points)
        self.assertEqual(points, original)


class ResampleTests(unittest.TestCase):
    def test_uneven_straight_line_becomes_evenly_spaced(self):
        self.assertEqual(resample([(0, 0), (1, 0), (9, 0), (10, 0)], 6),
                         [(0, 0), (2, 0), (4, 0), (6, 0), (8, 0), (10, 0)])

    def test_two_samples_preserve_only_endpoints(self):
        self.assertEqual(resample([(0, 0), (3, 0), (3, 4)], 2), [(0, 0), (3, 4)])

    def test_interpolation_follows_corner_instead_of_endpoint_chord(self):
        self.assertEqual(resample([(0, 0), (3, 0), (3, 4)], 3),
                         [(0, 0), (3, 0.5), (3, 4)])

    def test_integer_arc_length_positions_along_corner(self):
        expected = [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4)]
        self.assertEqual(resample([(0, 0), (3, 0), (3, 4)], 8), expected)

    def test_repeated_vertices_are_skipped_without_division_by_zero(self):
        points = [(0, 0), (0, 0), (3, 0), (3, 0), (6, 0), (6, 0)]
        self.assertEqual(resample(points, 7), [(i, 0) for i in range(7)])

    def test_one_point_is_repeated(self):
        self.assertEqual(resample([(3, 4)], 4), [(3, 4)] * 4)

    def test_zero_length_line_is_repeated(self):
        self.assertEqual(resample([(3, 4), (3, 4)], 4), [(3, 4)] * 4)

    def test_empty_line_is_rejected(self):
        with self.assertRaises(ValueError):
            resample([], 6)

    def test_invalid_counts_are_rejected(self):
        for count in (0, 1, -1, True, 6.0, "6", None):
            with self.subTest(count=count), self.assertRaises(ValueError):
                resample([(0, 0), (10, 0)], count)

    def test_input_and_mutable_endpoints_are_not_reused(self):
        points = [[0, 0], [3, 0], [3, 4]]
        original = [point.copy() for point in points]
        sampled = resample(points, 4)
        self.assertEqual(points, original)
        self.assertIsNot(sampled[0], points[0])
        self.assertIsNot(sampled[-1], points[-1])

    def test_closed_input_preserves_repeated_endpoint_and_count(self):
        sampled = resample([(0, 0), (3, 0), (3, 4), (0, 0)], 9)
        self.assertEqual(len(sampled), 9)
        self.assertEqual(sampled[0], (0, 0))
        self.assertEqual(sampled[-1], (0, 0))

    def test_samples_remain_on_original_polyline(self):
        points = [(-3, -2), (1, 4), (7, -1), (2, -6)]
        sampled = resample(points, 37)
        self.assertEqual(len(sampled), 37)
        for point in sampled:
            self.assertAlmostEqual(polyline_distance(point, points), 0.0)

    def test_tiny_lengths_are_not_treated_as_zero(self):
        sampled = resample([(0, 0), (1e-200, 0)], 3)
        self.assertAlmostEqual(sampled[1][0] / 1e-200, 0.5)

    def test_unrepresentable_length_is_rejected(self):
        with self.assertRaises(ValueError):
            resample([(-1e308, 0), (1e308, 0)], 3)


if __name__ == "__main__":
    unittest.main()
