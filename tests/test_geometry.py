import math
import unittest

from geometry import distance, frechet, length, mean_distance, polyline_distance, resample, segment_distance, symmetric_mean_distance


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


class MeanDistanceTests(unittest.TestCase):
    def test_same_polyline_has_near_zero_distance(self):
        points = [(0, 0), (3, 0), (3, 4)]
        self.assertAlmostEqual(mean_distance(points, points), 0.0)

    def test_parallel_lines_have_constant_offset(self):
        self.assertEqual(mean_distance([(0, 2), (10, 2)], [(0, 0), (10, 0)]), 2.0)

    def test_uneven_input_vertices_do_not_change_sampling(self):
        target = [(0, 0)]
        self.assertEqual(mean_distance([(0, 0), (10, 0)], target, 6),
                         mean_distance([(0, 0), (1, 0), (9, 0), (10, 0)], target, 6))

    def test_point_source_to_line(self):
        self.assertEqual(mean_distance([(3, 4)], [(0, 0), (6, 0)]), 4.0)

    def test_point_source_to_point(self):
        self.assertEqual(mean_distance([(3, 4)], [(0, 0)]), 5.0)

    def test_point_target_averages_sample_distances(self):
        self.assertEqual(mean_distance([(0, 0), (10, 0)], [(0, 0)], 3), 5.0)

    def test_target_corner_is_not_removed_by_resampling(self):
        self.assertEqual(mean_distance([(3, 0)], [(0, 0), (3, 0), (3, 4)], 2), 0.0)

    def test_measurement_is_directed_not_symmetric(self):
        short = [(0, 0), (2, 0)]
        long = [(0, 0), (10, 0)]
        self.assertEqual(mean_distance(short, long, 6), 0.0)
        self.assertAlmostEqual(mean_distance(long, short, 6), 20 / 6)

    def test_sampling_count_can_change_approximation(self):
        source = [(0, 0), (10, 0)]
        target = [(0, 0), (0, 10), (10, 10), (10, 0)]
        self.assertEqual(mean_distance(source, target, 2), 0.0)
        self.assertAlmostEqual(mean_distance(source, target, 3), 5 / 3)

    def test_empty_source_or_target_is_rejected(self):
        for source, target in (([], [(0, 0)]), ([(0, 0)], [])):
            with self.subTest(source=source, target=target), self.assertRaises(ValueError):
                mean_distance(source, target)

    def test_invalid_counts_are_rejected(self):
        for count in (None, True, 1, -1, 3.0, "3"):
            with self.subTest(count=count), self.assertRaises(ValueError):
                mean_distance([(0, 0)], [(0, 0)], count)

    def test_inputs_are_not_modified(self):
        source, target = [[0, 2], [10, 2]], [[0, 0], [10, 0]]
        mean_distance(source, target)
        self.assertEqual(source, [[0, 2], [10, 2]])
        self.assertEqual(target, [[0, 0], [10, 0]])

    def test_large_finite_average_does_not_overflow_sum(self):
        self.assertEqual(mean_distance([(1e308, 0)], [(0, 0)]), 1e308)

    def test_unrepresentable_gap_is_rejected(self):
        with self.assertRaises(ValueError):
            mean_distance([(-1e308, 0)], [(1e308, 0)])


class SymmetricMeanDistanceTests(unittest.TestCase):
    def test_same_line_has_near_zero_distance(self):
        line = [(0, 0), (3, 0), (3, 4)]
        self.assertAlmostEqual(symmetric_mean_distance(line, line), 0.0)

    def test_partial_overlap_is_not_zero(self):
        self.assertAlmostEqual(symmetric_mean_distance([(0, 0), (2, 0)], [(0, 0), (10, 0)], 6), 10 / 6)

    def test_swapping_inputs_preserves_result(self):
        a, b = [(0, 0), (3, 4), (6, 0)], [(1, 0), (4, 2), (8, 0)]
        self.assertEqual(symmetric_mean_distance(a, b, 17), symmetric_mean_distance(b, a, 17))

    def test_equals_average_of_two_directed_measurements(self):
        a, b = [(0, 0), (10, 0)], [(0, 1), (2, 3), (5, 4)]
        expected = (mean_distance(a, b, 9) + mean_distance(b, a, 9)) / 2
        self.assertAlmostEqual(symmetric_mean_distance(a, b, 9), expected)

    def test_parallel_lines_have_constant_offset(self):
        self.assertEqual(symmetric_mean_distance([(0, 2), (10, 2)], [(0, 0), (10, 0)]), 2.0)

    def test_point_inputs_are_supported(self):
        self.assertEqual(symmetric_mean_distance([(0, 0)], [(3, 4)]), 5.0)
        self.assertEqual(symmetric_mean_distance([(0, 0)], [(0, 0), (10, 0)], 3), 2.5)

    def test_repeated_vertices_do_not_change_same_shape(self):
        self.assertEqual(symmetric_mean_distance([(0, 0), (0, 0), (10, 0)], [(0, 0), (10, 0)]), 0.0)

    def test_empty_input_is_rejected_on_either_side(self):
        for a, b in (([], [(0, 0)]), ([(0, 0)], []), ([], [])):
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                symmetric_mean_distance(a, b)

    def test_invalid_sample_counts_are_rejected(self):
        for count in (None, True, 1, -1, 3.0, "3"):
            with self.subTest(count=count), self.assertRaises(ValueError):
                symmetric_mean_distance([(0, 0)], [(0, 0)], count)

    def test_input_lists_are_not_modified(self):
        a, b = [[0, 0], [2, 0]], [[0, 0], [10, 0]]
        symmetric_mean_distance(a, b, 6)
        self.assertEqual(a, [[0, 0], [2, 0]])
        self.assertEqual(b, [[0, 0], [10, 0]])

    def test_large_finite_average_does_not_overflow(self):
        self.assertEqual(symmetric_mean_distance([(0, 0)], [(1e308, 0)]), 1e308)

    def test_unrepresentable_distance_is_rejected(self):
        with self.assertRaises(ValueError):
            symmetric_mean_distance([(-1e308, 0)], [(1e308, 0)])

    def test_reversed_traversal_is_not_detected_as_error(self):
        line = [(0, 0), (3, 0), (3, 4)]
        self.assertAlmostEqual(symmetric_mean_distance(line, list(reversed(line))), 0.0)

    def test_retracing_same_line_is_not_detected_as_error(self):
        self.assertEqual(symmetric_mean_distance([(0, 0), (10, 0)], [(0, 0), (10, 0), (0, 0)]), 0.0)


class FrechetTests(unittest.TestCase):
    def test_identical_ordered_points_have_zero_distance(self):
        line = [(0, 0), (3, 0), (3, 4)]
        self.assertEqual(frechet(line, line), 0.0)

    def test_parallel_lines_have_constant_offset(self):
        self.assertEqual(frechet([(0, 2), (10, 2)], [(0, 0), (10, 0)]), 2.0)

    def test_two_single_points_use_distance(self):
        self.assertEqual(frechet([(0, 0)], [(3, 4)]), 5.0)

    def test_one_point_to_line_uses_maximum_vertex_distance(self):
        self.assertEqual(frechet([(0, 0)], [(0, 0), (3, 4), (0, 0)]), 5.0)
        self.assertEqual(frechet([(0, 0), (3, 4), (0, 0)], [(0, 0)]), 5.0)

    def test_reversed_direction_changes_result(self):
        line = [(0, 0), (10, 0)]
        self.assertEqual(frechet(line, list(reversed(line))), 10.0)

    def test_retrace_differs_from_mean_distance(self):
        a, b = [(0, 0), (10, 0)], [(0, 0), (10, 0), (0, 0)]
        self.assertEqual(symmetric_mean_distance(a, b), 0.0)
        self.assertEqual(frechet(a, b), 10.0)

    def test_internal_order_matters_even_with_same_endpoints_and_coverage(self):
        a = [(0, 0), (10, 0), (0, 0), (-10, 0), (0, 0)]
        b = [(0, 0), (-10, 0), (0, 0), (10, 0), (0, 0)]
        self.assertEqual(symmetric_mean_distance(a, b), 0.0)
        self.assertEqual(frechet(a, b), 10.0)

    def test_swapping_whole_inputs_preserves_result(self):
        a, b = [(0, 0), (3, 4), (6, 0)], [(1, 0), (2, 2), (4, 3), (8, 0)]
        self.assertEqual(frechet(a, b), frechet(b, a))

    def test_same_line_with_different_vertex_density_is_discrete(self):
        a, b = [(0, 0), (10, 0)], [(0, 0), (5, 0), (10, 0)]
        self.assertEqual(frechet(a, b), 5.0)
        self.assertEqual(frechet(resample(a, 3), resample(b, 3)), 0.0)

    def test_repeated_points_can_wait_without_error(self):
        self.assertEqual(frechet([(0, 0), (0, 0), (10, 0)], [(0, 0), (10, 0), (10, 0)]), 0.0)

    def test_empty_input_is_rejected(self):
        for a, b in (([], [(0, 0)]), ([(0, 0)], []), ([], [])):
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                frechet(a, b)

    def test_input_lists_are_not_modified(self):
        a, b = [[0, 0], [10, 0]], [[0, 0], [10, 0], [0, 0]]
        frechet(a, b)
        self.assertEqual(a, [[0, 0], [10, 0]])
        self.assertEqual(b, [[0, 0], [10, 0], [0, 0]])

    def test_tiny_distances_are_not_treated_as_zero(self):
        self.assertAlmostEqual(frechet([(0, 0)], [(3e-200, 4e-200)]) / 1e-200, 5.0)

    def test_large_finite_distance_is_supported(self):
        self.assertEqual(frechet([(0, 0)], [(1e308, 0)]), 1e308)

    def test_unrepresentable_optimal_distance_is_rejected(self):
        with self.assertRaises(ValueError):
            frechet([(-1e308, 0)], [(1e308, 0)])

    def test_overflowing_unused_pairs_do_not_reject_finite_optimum(self):
        line = [(-1e308, 0), (1e308, 0)]
        self.assertEqual(frechet(line, line), 0.0)

    def test_nan_distance_is_rejected(self):
        with self.assertRaises(ValueError):
            frechet([(float("nan"), 0)], [(0, 0)])

    def test_matches_exhaustive_monotone_pairings_for_small_inputs(self):
        # 검증용으로 모든 대응을 열거해 행을 재사용하는 본체와 독립적으로 확인한다.
        def enumerate_results(a, b, i=0, j=0, worst=0.0):
            worst = max(worst, distance(a[i], b[j]))
            if i == len(a) - 1 and j == len(b) - 1:
                return [worst]
            results = []
            for step_i, step_j in ((1, 0), (0, 1), (1, 1)):
                if i + step_i < len(a) and j + step_j < len(b):
                    results.extend(enumerate_results(a, b, i + step_i, j + step_j, worst))
            return results

        lines = ([(0, 0)], [(0, 0), (1, 0)], [(1, 0), (0, 0)],
                 [(0, 0), (1, 1), (2, 0)], [(0, 0), (2, 0), (1, 1)])
        for a in lines:
            for b in lines:
                with self.subTest(a=a, b=b):
                    self.assertEqual(frechet(a, b), min(enumerate_results(a, b)))


if __name__ == "__main__":
    unittest.main()
