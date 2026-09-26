"""Bridge from administrative skill_id to domain entrypoints via taxonomy config."""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

from core.registry.domain_operation_registry import (
    get_domain_operations,
    list_registered_domains,
)

REGISTRY_REVISION = "2026-09-10-v1.10"

_B2_13_SKILL_OPERATIONS = {
    "vh_數學B2_SubSection_1_3_1": ("classify_standard_position_angle",),
    "vh_數學B2_SubSection_1_3_2": ("compute_terminal_ray_trig_ratios",),
    "vh_數學B2_SubSection_1_3_4": ("solve_signed_trig_constraints", "classify_trig_derived_point_quadrant"),
    "vh_數學B2_SubSection_1_3_5": ("evaluate_exact_arbitrary_angle_trig_expression",),
    "vh_數學B2_SubSection_1_3_6": ("evaluate_exact_arbitrary_angle_trig_expression", "solve_arbitrary_angle_vertical_projection"),
    "vh_數學B2_SubSection_1_3_7": (
        "evaluate_exact_arbitrary_angle_trig_expression",
        "complete_reference_angle_conversion",
        "classify_trig_derived_point_quadrant",
        "simplify_fundamental_trig_expression",
    ),
}

_B2_14_OPERATIONS = (
    "compare_trig_values_by_monotonicity", "solve_trig_value_quadratic_constraint",
    "analyze_affine_transformed_trig_graph", "calculate_trig_period_from_argument_scale",
    "classify_trig_expression_sign_change", "classify_trig_equation_feasibility",
    "analyze_tangent_absolute_graph_period", "evaluate_trig_decimal",
    "count_sine_cosine_intersections",
)
_B2_14_SKILLS = tuple(f"vh_數學B2_SubSection_1_4_{index}" for index in range(1, 5))

_B2_21_SINE_OPERATIONS = (
    "compute_triangle_area_sas",
    "solve_side_and_circumradius_by_sines",
    "solve_angle_by_law_of_sines",
    "compute_sin_from_side_and_circumradius",
    "solve_side_ratio_by_law_of_sines",
    "solve_side_by_law_of_sines",
)
_B2_21_SINE_SKILL = "vh_數學B2_SubSection_2_1_1"

_B2_21_COSINE_OPERATIONS = (
    "solve_side_by_law_of_cosines",
    "solve_angle_by_law_of_cosines",
    "solve_cosine_identity_angle",
    "solve_detour_extra_distance_by_cosines",
    "compute_circumradius_from_three_sides",
)
_B2_21_COSINE_SKILL = "vh_數學B2_SubSection_2_1_2"

_B2_223_MEASUREMENT_OPERATIONS = (
    "solve_height_from_sight_line_elevation",
    "solve_adjacent_from_hypotenuse_ground_angle",
    "solve_opposite_from_adjacent_elevation",
    "solve_horizontal_from_height_elevation",
    "solve_horizontal_from_height_depression",
    "solve_two_elevation_horizontal_shift",
    "solve_two_elevation_unknown_height",
    "solve_building_height_with_flagpole_elevations",
    "solve_broken_tree_original_height",
    "solve_height_decimal_from_sight_line_elevation",
)
_B2_223_MEASUREMENT_SKILL = "vh_數學B2_SubSection_2_2_3"

_B2_224_OBLIQUE_OPERATIONS = (
    "solve_side_by_law_of_sines",
    "solve_side_by_law_of_cosines",
)
_B2_224_OBLIQUE_SKILL = "vh_數學B2_SubSection_2_2_4"

_B2_225_SOLID_OPERATIONS = (
    "solve_tower_two_elevation_path_and_river_width",
    "solve_height_from_two_elevation_tan_ratios",
    "solve_height_from_isosceles_bearing_walk_elevation",
)
_B2_225_SOLID_SKILL = "vh_數學B2_SubSection_2_2_5"

# B2 Chapter 3 plane-vector skills (algebraic / coordinate families).
_B2_CH3_COORD_OPS = (
    "compute_vector_components_and_magnitude",
    "solve_equal_vector_coordinates",
    "compute_directed_segment_and_magnitude",
    "solve_parallelogram_fourth_vertex",
    "compute_triangle_perimeter_from_two_vectors",
)
_B2_CH3_ARITH_OPS = (
    "compute_vector_sum_difference",
    "compute_point_vectors_linear_combination",
    "compute_triangle_chain_and_perimeter",
    "solve_parallelogram_fourth_vertex",
    "compute_vector_linear_combination",
)
_B2_CH3_SCALAR_OPS = (
    "compute_scalar_multiple_coordinates",
    "compute_vector_linear_combination",
)
_B2_CH3_PARALLEL_OPS = ("solve_parallel_vector_parameter",)
_B2_CH3_UNIT_OPS = (
    "compute_unit_vector",
    "compute_scaled_direction_vector",
)
_B2_CH3_ANGLE_OPS = (
    "compute_cosine_of_angle_from_dot",
)
_B2_CH3_DOT_DEF_OPS = (
    "compute_dot_product_from_magnitudes_angle",
)
_B2_CH3_DOT_COORD_OPS = (
    "compute_dot_product_coordinates",
    "compute_cosine_of_angle_from_dot",
)
_B2_CH3_PERP_OPS = ("solve_perpendicular_vector_parameter",)
_B2_CH3_DOT_PROP_OPS = (
    "compute_dot_product_from_magnitudes_angle",
)
_B2_CH3_DIAGRAM_SKILLS = tuple(f"vh_數學B2_SubSection_3_1_{i}" for i in range(1, 5))
_B2_CH3_SKILL_OPERATIONS = {
    "vh_數學B2_SubSection_3_1_1": ('express_named_vectors_in_given_basis', 'identify_equal_vector_mcq'),
    "vh_數學B2_SubSection_3_1_2": ('simplify_vector_path_expression',),
    "vh_數學B2_SubSection_3_1_3": ('simplify_vector_path_expression',),
    "vh_數學B2_SubSection_3_1_4": ('construct_linear_combination_choice', 'express_linear_combination_from_givens', 'express_section_point_vector', 'identify_resultant_path_mcq', 'solve_scalar_multiple_relation_fill', 'solve_section_coefficient_pair'),
    "vh_數學B2_SubSection_3_2_1": ('compute_directed_segment_and_magnitude', 'compute_directed_segment_mixed_multipart', 'compute_triangle_perimeter_from_two_vectors', 'compute_vector_components_and_magnitude', 'solve_equal_vector_coordinates', 'solve_parallelogram_fourth_vertex'),
    "vh_數學B2_SubSection_3_2_2": ('compute_chain_closure_vector_mcq', 'compute_point_vectors_linear_combination', 'compute_triangle_chain_and_perimeter', 'compute_vector_linear_combination', 'compute_vector_sum_difference', 'solve_parallelogram_fourth_vertex'),
    "vh_數學B2_SubSection_3_2_3": ('solve_collinear_ratio_mcq', 'solve_point_from_vector_combination'),
    "vh_數學B2_SubSection_3_2_4": ('compute_vector_linear_combination', 'solve_unknown_vector_linear_equation'),
    "vh_數學B2_SubSection_3_2_5": ('solve_parallel_then_magnitude_mcq', 'solve_parallel_vector_parameter'),
    "vh_數學B2_SubSection_3_2_6": ('compute_scaled_direction_vector', 'identify_unit_vector_mcq'),
    "vh_數學B2_SubSection_3_3_1": ('classify_angle_quality_from_dot_mcq', 'compute_cosine_of_angle_from_dot', 'solve_navigation_heading_correction'),
    "vh_數學B2_SubSection_3_3_2": ('compute_dot_identity_multipart', 'compute_dot_product_from_magnitudes_angle', 'compute_regular_polygon_edge_dot'),
    "vh_數學B2_SubSection_3_3_3": ('compute_cosine_of_angle_from_dot', 'compute_dot_product_coordinates', 'compute_midpoint_dot_product', 'plot_navigation_points_coordinates', 'solve_dot_product_parameter_mcq'),
    "vh_數學B2_SubSection_3_3_4": ('solve_perpendicular_composite_parameter', 'solve_perpendicular_vector_parameter'),
    "vh_數學B2_SubSection_3_3_5": ('classify_dot_sign_from_diagram_mcq', 'compute_dot_product_from_magnitudes_angle', 'expand_perpendicular_dot_product', 'solve_angle_from_magnitude_identity'),
}

# B2 Ch4 circle plane — 4-1.1 / 4-1.2 only (4-2 remains unbound / needs_capability).
_B2_CH4_CIRCLE_SKILL_OPERATIONS = {
    "vh_數學B2_SubSection_4_1_1": (
        "identify_center_radius_from_standard",
        "write_circle_from_center_radius",
        "write_circle_from_center_point",
        "write_circle_equations_from_conditions",
        "interpret_circular_locus_equation",
        "circle_from_diameter_endpoints",
        "circle_equal_radius_at_origin",
        "translate_and_scale_circle",
        "circle_origin_through_lines_intersection",
        "circle_same_center_scaled_area",
        "circle_center_tangent_to_line",
    ),
    "vh_數學B2_SubSection_4_1_2": (
        "identify_center_radius_from_general",
        "solve_circle_parameter_range",
        "circle_through_three_points",
        "circle_center_on_axis_area",
        "classify_general_circle_graph",
        "translate_and_scale_circle",
        "compute_circle_area_from_general",
        "identify_circle_from_product_form",
        "evaluate_center_radius_expression",
        "solve_circle_parameter_range_mcq",
    ),
    "vh_數學B2_SubSection_4_2_1": (
        "classify_point_vs_circles_multipart",
        "solve_point_circle_parameter_range",
        "identify_point_on_circle_mcq",
    ),
    "vh_數學B2_SubSection_4_2_2": (
        "classify_line_circle_relation",
        "classify_lines_vs_circle_multipart",
        "solve_line_circle_parameter_range",
        "solve_line_circle_tangent_parameter",
        "compute_chord_length",
        "solve_line_circle_relation_ranges_multipart",
        "count_line_circle_intersections",
        "compute_storm_path_length_in_circle",
        "classify_line_circle_relation_mcq",
        "solve_diameter_chord_parameter_mcq",
        "compute_triangle_center_chord_area",
        "solve_axis_tangent_parameter",
    ),
    "vh_數學B2_SubSection_4_2_3": (
        "tangent_at_point_on_circle",
        "tangents_parallel_to_line",
        "tangents_perpendicular_to_line",
        "compute_tangents_from_point_quad_area",
        "tangent_at_point_on_circle_mcq",
    ),
    "vh_數學B2_SubSection_4_2_4": (
        "compute_tangent_segment_lengths",
        "count_line_vs_two_circles_intersections",
        "compute_tangent_segment_length_mcq",
    ),
}


class SkillDomainNotRegisteredError(KeyError):
    """Raised when skill_id has no fixed domain binding in Registry."""


# fixed_domain_key -> allowed_operations.
# Single source of truth is domain_operation_registry; this dict is derived
# from it so all downstream callers see a consistent view without each module
# importing the registry directly.
DOMAIN_ALLOWED_OPERATIONS: dict[str, list[str]] = {
    dk: get_domain_operations(dk)
    for dk in list_registered_domains()
}

# Administrative profile: skill_id -> fixed_domain_key + curriculum.
SKILL_DOMAIN_PROFILE: dict[str, dict[str, Any]] = {
    "vh_數學B1_PointSlopeForm": {
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "domain": "coordinate_geometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
    },
    "vh_數學B1_HorizontalAndVerticalLineEquations": {
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "domain": "coordinate_geometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
    },
    "vh_數學B1_SlopeInterceptForm": {
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "domain": "coordinate_geometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
    },
    "vh_數學B1_InterceptForm": {
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "domain": "coordinate_geometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
    },
    "vh_數學B1_GeneralFormOfLinearEquation": {
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "domain": "coordinate_geometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
    },
    "vh_數學B1_SlopeOfALine": {
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "domain": "coordinate_geometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_slope_of_a_line",
    },
    "vh_數學B1_DistanceBetweenPointAndLine": {
        "fixed_domain_key": "coordinate_geometry.point_line_distance",
        "domain": "coordinate_geometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
    },
    "vh_數學B1_DistanceBetweenTwoParallelLines": {
        "fixed_domain_key": "coordinate_geometry.parallel_lines_distance",
        "domain": "coordinate_geometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_parallel_lines_distance",
    },
    "vh_數學B1_PolynomialBasicConcepts": {
        "fixed_domain_key": "algebra.polynomial",
        "domain": "algebra",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_polynomial_basic_concepts",
    },
    "vh_數學B1_PolynomialArithmeticOperations": {
        "fixed_domain_key": "algebra.polynomial",
        "domain": "algebra",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_polynomial_arithmetic",
    },
    "vh_數學B1_PolynomialEquality": {
        "fixed_domain_key": "algebra.polynomial",
        "domain": "algebra",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_polynomial_equality",
    },
    "vh_數學B1_RemainderTheorem": {
        "fixed_domain_key": "algebra.polynomial",
        "domain": "algebra",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_remainder_theorem",
    },
    "vh_數學B1_FactorTheorem": {
        "fixed_domain_key": "algebra.polynomial",
        "domain": "algebra",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_factor_theorem",
    },
    "vh_數學B1_PolynomialFactoring": {
        "fixed_domain_key": "algebra.polynomial",
        "domain": "algebra",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_polynomial_factoring",
    },
    "vh_數學B2_AngleMeasurementAndConversion": {
        "fixed_domain_key": "trigonometry.angle",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_angle_measurement_and_conversion",
    },
    "vh_數學B2_RatioAndRatioValue": {
        "fixed_domain_key": "geometry.similarity",
        "domain": "geometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_similar_triangle_proportion",
    },
    "vh_數學B2_TrigonometricFunctionsOfAcuteAngles": {
        "fixed_domain_key": "trigonometry.acute",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_right_triangle_trig_ratios",
    },
    "vh_數學B2_TrigonometricValuesOfSpecialAngles": {
        "fixed_domain_key": "trigonometry.acute",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_exact_special_angles",
    },
    "vh_數學B2_CalculatingFunctionValuesUsingCalculator": {
        "fixed_domain_key": "trigonometry.acute",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_acute_trig_decimal_evaluation",
    },
    "vh_數學B2_FundamentalTrigonometricIdentities": {
        "fixed_domain_key": "trigonometry.acute",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_cofunction_identity",
    },
    "vh_數學B2_ArcLengthAndAreaOfSector": {
        "fixed_domain_key": "trigonometry.angle",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_arc_length_and_area_of_sector",
    },
    "vh_數學B2_ArcLengthAndSectorArea": {
        "fixed_domain_key": "trigonometry.angle",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_arc_length_and_sector_area_alias",
    },
    "vh_數學B2_CoterminalAngles": {
        "fixed_domain_key": "trigonometry.angle",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_coterminal_angles",
    },
    "vh_數學B1_RationalExpressionArithmeticOperations": {
        "fixed_domain_key": "algebra.polynomial",
        "domain": "algebra",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_rational_expression_arithmetic",
    },
    "vh_數學B1_RationalEquation": {
        "fixed_domain_key": "algebra.polynomial",
        "domain": "algebra",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_rational_equation",
    },
    "vh_數學B4_FrequencyDistributionTableConstruction": {
        "fixed_domain_key": "statistics.frequency_distribution",
        "domain": "statistics",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_frequency_distribution_table",
    },
    "vh_數學B4_CumulativeFrequencyTablesAndGraphs": {
        "fixed_domain_key": "statistics.frequency_distribution",
        "domain": "statistics",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_cumulative_frequency_distribution",
    },
    "vh_數學B4_StatisticalChartReading": {
        "fixed_domain_key": "statistics.table_chart",
        "domain": "statistics",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_statistical_chart_reading",
    },
    "vh_數學B4_NormalDistributionAndEmpiricalRule": {
        "fixed_domain_key": "statistics.descriptive_statistics",
        "domain": "statistics",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_normal_distribution_empirical_rule",
    },
}

# Runtime domain module routing (YAML may extend this mapping).
SKILL_TO_DOMAIN: dict[str, dict[str, Any]] = {
    "vh_數學B1_PointSlopeForm": {
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_line_equation_matrix",
        "default_curriculum_profile": "vocational_high_b",
    },
    "vh_數學B1_HorizontalAndVerticalLineEquations": {
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_line_equation_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": ["horizontal_line", "vertical_line"],
    },
    "vh_數學B1_SlopeInterceptForm": {
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_line_equation_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": [
            "slope_intercept_equation",
            "slope_intercept_find_x_intercept",
            "slope_intercept_read_slope_and_intercept",
        ],
    },
    "vh_數學B1_InterceptForm": {
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_line_equation_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": [
            "intercept_form_equation",
            "intercept_form_triangle_area",
            "intercept_form_equation_and_triangle_area",
        ],
    },
    "vh_數學B1_GeneralFormOfLinearEquation": {
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_line_equation_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": [
            "slope_from_general_or_intercept_form",
            "slope_from_general_form",
            "slope_of_horizontal_or_vertical_line",
            "line_through_point_parallel_to_line",
            "line_through_point_perpendicular_to_line",
            "parallel_line_slope",
            "perpendicular_line_slope",
            "parallel_condition_parameter",
            "perpendicular_condition_parameter",
            "compare_line_slopes",
            "line_through_intersection_parallel_to_line",
            "line_through_point_perpendicular_to_segment",
            "perpendicular_bisector_application",
            "coordinate_geometry_word_problem",
        ],
    },
    "vh_數學B1_SlopeOfALine": {
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_line_equation_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": [
            "slope_from_two_points",
            "solve_parameter_from_known_slope",
            "solve_parameter_from_known_slope_choice",
            "collinear_three_points_parameter",
            "non_triangle_collinear_parameter",
            "parallel_segments_parameter",
            "perpendicular_segments_parameter",
            "collinear_three_points_parameter_choice",
            "slopes_of_named_segments",
            "classify_and_compare_figure_slopes",
        ],
    },
    "vh_數學B1_DistanceBetweenPointAndLine": {
        "fixed_domain_key": "coordinate_geometry.point_line_distance",
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_coordinate_geometry_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": [
            "distance_from_point_to_line",
            "distance_from_point_to_line_parameter",
            "compare_point_to_line_distances",
        ],
    },
    "vh_數學B1_DistanceBetweenTwoParallelLines": {
        "fixed_domain_key": "coordinate_geometry.parallel_lines_distance",
        "domain_module": "core.domain.coordinate_geometry.parallel_lines_distance_domain",
        "entrypoint": "build_parallel_lines_distance_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": [
            "distance_between_parallel_lines",
            "solve_parameter_from_parallel_distance",
            "construct_parallel_line_at_distance",
            "parallel_lines_distance_single_choice",
            "area_using_parallel_distance",
        ],
    },
    "vh_數學B4_FrequencyDistributionTableConstruction": {
        "fixed_domain_key": "statistics.frequency_distribution",
        "domain_module": "core.domain.statistics.frequency_distribution_domain",
        "entrypoint": "build_frequency_distribution_table_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": [
            "frequency_table_construction_review",
            "frequency_table_single_bin_count",
        ],
    },
    "vh_數學B4_CumulativeFrequencyTablesAndGraphs": {
        "fixed_domain_key": "statistics.frequency_distribution",
        "domain_module": "core.domain.statistics.frequency_distribution_domain",
        "entrypoint": "build_frequency_distribution_table_matrix",
        "default_curriculum_profile": "vocational_high_b",
    },
    "vh_數學B4_StatisticalChartReading": {
        "fixed_domain_key": "statistics.table_chart",
        "domain_module": "core.domain.statistics.table_chart_domain",
        "entrypoint": "build_statistical_chart_reading_matrix",
        "default_curriculum_profile": "vocational_high_b",
        # All domain operations allowed for this skill; derived from registry.
        "allowed_types": get_domain_operations("statistics.table_chart"),
    },
    "vh_數學B4_NormalDistributionAndEmpiricalRule": {
        "fixed_domain_key": "statistics.descriptive_statistics",
        "domain_module": "core.domain.statistics.descriptive_statistics_domain",
        "entrypoint": "build_descriptive_statistics_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": [
            "empirical_rule_probability",
            "empirical_rule_population_count",
            "compare_distribution_spread",
        ],
    },
    "vh_數學B2_AngleMeasurementAndConversion": {
        "fixed_domain_key": "trigonometry.angle",
        "domain_module": "core.domain.trigonometry_angle_domain",
        "entrypoint": "build_trigonometry_angle_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": ["convert_angle_measure"],
    },
    **{
        skill_id: {
            "fixed_domain_key": "trigonometry.arbitrary_angle",
            "domain": "trigonometry",
            "curriculum_profile": "vocational_high_b",
            "registry_revision": REGISTRY_REVISION,
            "mapping_reason": "textbook_skill_arbitrary_angle_trigonometry",
        }
        for skill_id in _B2_13_SKILL_OPERATIONS
    },
    **{
        skill_id: {
            "fixed_domain_key": "trigonometry.function_graph", "domain": "trigonometry",
            "curriculum_profile": "vocational_high_b", "registry_revision": REGISTRY_REVISION,
            "mapping_reason": "textbook_skill_trigonometric_function_graph",
        }
        for skill_id in _B2_14_SKILLS
    },
    _B2_21_SINE_SKILL: {
        "fixed_domain_key": "trigonometry.law_of_sines",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_law_of_sines",
    },
    _B2_21_COSINE_SKILL: {
        "fixed_domain_key": "trigonometry.law_of_cosines",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_law_of_cosines",
    },
    _B2_223_MEASUREMENT_SKILL: {
        "fixed_domain_key": "trigonometry.right_triangle_measurement",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_right_triangle_measurement",
    },
    _B2_224_OBLIQUE_SKILL: {
        "fixed_domain_key": "trigonometry.oblique_triangle_measurement",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_oblique_triangle_measurement_compose_sines_cosines",
    },
    _B2_225_SOLID_SKILL: {
        "fixed_domain_key": "trigonometry.solid_measurement",
        "domain": "trigonometry",
        "curriculum_profile": "vocational_high_b",
        "registry_revision": REGISTRY_REVISION,
        "mapping_reason": "textbook_skill_simple_solid_measurement",
    },
    **{
        skill_id: {
            "fixed_domain_key": "vector.plane",
            "domain": "vector",
            "curriculum_profile": "vocational_high_b",
            "registry_revision": REGISTRY_REVISION,
            "mapping_reason": "textbook_skill_b2_ch3_plane_vector",
        }
        for skill_id in list(_B2_CH3_SKILL_OPERATIONS)
    },
    **{
        skill_id: {
            "fixed_domain_key": "circle.plane",
            "domain": "circle",
            "curriculum_profile": "vocational_high_b",
            "registry_revision": REGISTRY_REVISION,
            "mapping_reason": "textbook_skill_b2_ch4_circle_standard_general",
        }
        for skill_id in list(_B2_CH4_CIRCLE_SKILL_OPERATIONS)
    },
    "vh_數學B2_RatioAndRatioValue": {
        "fixed_domain_key": "geometry.similarity",
        "domain_module": "core.domain.geometry_similarity_domain",
        "entrypoint": "build_geometry_similarity_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": ["solve_similar_triangle_proportion"],
    },
    "vh_數學B2_TrigonometricFunctionsOfAcuteAngles": {
        "fixed_domain_key": "trigonometry.acute",
        "domain_module": "core.domain.trigonometry_acute_domain",
        "entrypoint": "build_trigonometry_acute_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": [
            "compute_right_triangle_trig_ratios",
            "solve_acute_trig_constraints",
            "simplify_fundamental_trig_expression",
            "collinear_three_points_parameter",
            "compute_chord_and_arc_length",
        ],
    },
    "vh_數學B2_TrigonometricValuesOfSpecialAngles": {
        "fixed_domain_key": "trigonometry.acute",
        "domain_module": "core.domain.trigonometry_acute_domain",
        "entrypoint": "build_trigonometry_acute_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": ["evaluate_exact_special_angle_expression", "solve_right_triangle_projection"],
    },
    "vh_數學B2_CalculatingFunctionValuesUsingCalculator": {
        "fixed_domain_key": "trigonometry.acute",
        "domain_module": "core.domain.trigonometry_acute_domain",
        "entrypoint": "build_trigonometry_acute_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": ["evaluate_trig_decimal"],
    },
    "vh_數學B2_FundamentalTrigonometricIdentities": {
        "fixed_domain_key": "trigonometry.acute",
        "domain_module": "core.domain.trigonometry_acute_domain",
        "entrypoint": "build_trigonometry_acute_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": [
            "simplify_fundamental_trig_expression",
            "complete_cofunction_identity",
            "solve_acute_trig_constraints",
        ],
    },
    "vh_數學B2_ArcLengthAndAreaOfSector": {
        "fixed_domain_key": "trigonometry.angle",
        "domain_module": "core.domain.trigonometry_angle_domain",
        "entrypoint": "build_trigonometry_angle_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": ["sector_arc_and_area"],
    },
    "vh_數學B2_ArcLengthAndSectorArea": {
        "fixed_domain_key": "trigonometry.angle",
        "domain_module": "core.domain.trigonometry_angle_domain",
        "entrypoint": "build_trigonometry_angle_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": ["sector_arc_and_area"],
    },
    "vh_數學B2_CoterminalAngles": {
        "fixed_domain_key": "trigonometry.angle",
        "domain_module": "core.domain.trigonometry_angle_domain",
        "entrypoint": "build_trigonometry_angle_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": ["coterminal_angles"],
    },
    **{
        skill_id: {
            "fixed_domain_key": "trigonometry.arbitrary_angle",
            "domain_module": "core.domain.trigonometry_arbitrary_domain",
            "entrypoint": "build_trigonometry_arbitrary_matrix",
            "default_curriculum_profile": "vocational_high_b",
            "allowed_types": list(_B2_13_SKILL_OPERATIONS[skill_id]),
        }
        for skill_id in _B2_13_SKILL_OPERATIONS
    },
    **{
        skill_id: {
            "fixed_domain_key": "trigonometry.function_graph",
            "domain_module": "core.domain.trigonometry_function_graph_domain",
            "entrypoint": "build_trigonometry_function_graph_matrix",
            "default_curriculum_profile": "vocational_high_b",
            "allowed_types": list(_B2_14_OPERATIONS),
        }
        for skill_id in _B2_14_SKILLS
    },
    _B2_21_SINE_SKILL: {
        "fixed_domain_key": "trigonometry.law_of_sines",
        "domain_module": "core.domain.trigonometry_law_of_sines_domain",
        "entrypoint": "build_trigonometry_law_of_sines_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": list(_B2_21_SINE_OPERATIONS),
    },
    _B2_21_COSINE_SKILL: {
        "fixed_domain_key": "trigonometry.law_of_cosines",
        "domain_module": "core.domain.trigonometry_law_of_cosines_domain",
        "entrypoint": "build_trigonometry_law_of_cosines_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": list(_B2_21_COSINE_OPERATIONS),
    },
    _B2_223_MEASUREMENT_SKILL: {
        "fixed_domain_key": "trigonometry.right_triangle_measurement",
        "domain_module": "core.domain.trigonometry_right_triangle_measurement_domain",
        "entrypoint": "build_trigonometry_right_triangle_measurement_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": list(_B2_223_MEASUREMENT_OPERATIONS),
    },
    _B2_224_OBLIQUE_SKILL: {
        "fixed_domain_key": "trigonometry.oblique_triangle_measurement",
        "domain_module": "core.domain.trigonometry_oblique_triangle_measurement_domain",
        "entrypoint": "build_trigonometry_oblique_triangle_measurement_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": list(_B2_224_OBLIQUE_OPERATIONS),
    },
    _B2_225_SOLID_SKILL: {
        "fixed_domain_key": "trigonometry.solid_measurement",
        "domain_module": "core.domain.trigonometry_solid_measurement_domain",
        "entrypoint": "build_trigonometry_solid_measurement_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": list(_B2_225_SOLID_OPERATIONS),
    },
    **{
        skill_id: {
            "fixed_domain_key": "vector.plane",
            "domain_module": "core.domain.vector_plane_domain",
            "entrypoint": "build_vector_plane_matrix",
            "default_curriculum_profile": "vocational_high_b",
            "allowed_types": list(ops),
        }
        for skill_id, ops in _B2_CH3_SKILL_OPERATIONS.items()
    },
    **{
        skill_id: {
            "fixed_domain_key": "circle.plane",
            "domain_module": "core.domain.circle_plane_domain",
            "entrypoint": "build_circle_plane_matrix",
            "default_curriculum_profile": "vocational_high_b",
            "allowed_types": list(ops),
        }
        for skill_id, ops in _B2_CH4_CIRCLE_SKILL_OPERATIONS.items()
    },
}

# Try loading from YAML (extends SKILL_TO_DOMAIN; profile keys merged below).
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    YAML_PATH = PROJECT_ROOT / "configs" / "gencode_taxonomy" / "k12_component_taxonomy.yaml"
    if YAML_PATH.is_file():
        with open(YAML_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        skills = data.get("skills", {})
        if isinstance(skills, dict) and skills:
            for skill_id, skill_meta in skills.items():
                if isinstance(skill_meta, dict):
                    SKILL_TO_DOMAIN[skill_id] = skill_meta
except Exception:
    pass


def _skill_registered(skill_id: str) -> bool:
    return str(skill_id or "").strip() in SKILL_TO_DOMAIN


def is_confirmed_skill_binding(skill_id: str) -> bool:
    """Return True when skill_id has an explicit confirmed registry binding."""
    return _skill_registered(skill_id)


def get_confirmed_skill_binding(skill_id: str) -> dict[str, Any] | None:
    """Return merged confirmed binding metadata, or None when unbound."""
    key = str(skill_id or "").strip()
    if not key or not _skill_registered(key):
        return None
    try:
        return resolve_domain_for_skill(key)
    except SkillDomainNotRegisteredError:
        return None


def get_fixed_domain_key(skill_id: str) -> str:
    """Return the single fixed routing domain key for a skill."""
    key = str(skill_id or "").strip()
    if not key or not _skill_registered(key):
        raise SkillDomainNotRegisteredError(f"skill_domain_not_registered: {skill_id!r}")

    profile = SKILL_DOMAIN_PROFILE.get(key) or {}
    routing = SKILL_TO_DOMAIN.get(key) or {}
    fixed = str(
        profile.get("fixed_domain_key")
        or routing.get("fixed_domain_key")
        or ""
    ).strip()
    if not fixed:
        # Legacy fallback: coordinate_geometry token only — not ideal but preserves older skills.
        legacy = str(profile.get("domain") or routing.get("domain") or "").strip()
        if legacy == "coordinate_geometry":
            fixed = "coordinate_geometry.line_equation"
    if not fixed:
        raise SkillDomainNotRegisteredError(f"skill_domain_not_registered: {skill_id!r}")
    return fixed


def get_allowed_operations(domain_key: str, *, skill_id: str | None = None) -> list[str]:
    """Return allowed operations for a fixed domain key (optionally narrowed by skill YAML)."""
    dk = str(domain_key or "").strip()
    if not dk:
        raise SkillDomainNotRegisteredError("skill_domain_not_registered: empty domain_key")

    base = list(DOMAIN_ALLOWED_OPERATIONS.get(dk, []))
    if skill_id:
        routing = SKILL_TO_DOMAIN.get(str(skill_id).strip()) or {}
        yaml_allowed = routing.get("allowed_types") or routing.get("allowed_operations")
        if isinstance(yaml_allowed, list) and yaml_allowed:
            narrowed = [str(x).strip() for x in yaml_allowed if str(x).strip()]
            if base:
                return [op for op in narrowed if op in base] or narrowed
            return narrowed
    return base


def get_registry_revision(skill_id: str) -> str:
    key = str(skill_id or "").strip()
    profile = SKILL_DOMAIN_PROFILE.get(key) or {}
    return str(profile.get("registry_revision") or REGISTRY_REVISION)


def resolve_domain_for_skill(skill_id: str) -> dict[str, Any]:
    """Return merged administrative profile + domain routing metadata."""
    key = str(skill_id or "").strip()
    if key not in SKILL_TO_DOMAIN:
        raise SkillDomainNotRegisteredError(f"skill_domain_not_registered: {skill_id!r}")

    merged = dict(SKILL_TO_DOMAIN[key])
    profile = SKILL_DOMAIN_PROFILE.get(key)
    if isinstance(profile, dict):
        merged.update(profile)
        if profile.get("curriculum_profile") and not merged.get("default_curriculum_profile"):
            merged["default_curriculum_profile"] = profile["curriculum_profile"]

    fixed_domain_key = get_fixed_domain_key(key)
    merged["fixed_domain_key"] = fixed_domain_key
    merged["allowed_operations"] = (
        list(_B2_13_SKILL_OPERATIONS[key])
        if key in _B2_13_SKILL_OPERATIONS
        else list(_B2_14_OPERATIONS) if key in _B2_14_SKILLS
        else list(_B2_21_SINE_OPERATIONS) if key == _B2_21_SINE_SKILL
        else list(_B2_21_COSINE_OPERATIONS) if key == _B2_21_COSINE_SKILL
        else list(_B2_CH3_SKILL_OPERATIONS[key]) if key in _B2_CH3_SKILL_OPERATIONS
        else list(_B2_CH4_CIRCLE_SKILL_OPERATIONS[key]) if key in _B2_CH4_CIRCLE_SKILL_OPERATIONS
        else get_allowed_operations(fixed_domain_key, skill_id=key)
    )
    merged["registry_revision"] = get_registry_revision(key)
    return merged



