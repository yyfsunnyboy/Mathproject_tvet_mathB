"""Canonical answer schema registry for V3 Full Matrix Dictionary contracts."""

from __future__ import annotations

from typing import Any

ANSWER_SCHEMAS: dict[str, dict[str, frozenset[str]]] = {
    "line_equation": {
        "required_fields": frozenset({"canonical_form", "general_form"}),
    },
    "slope_intercept": {
        "required_fields": frozenset({"slope", "intercept"}),
    },
    "distance_scalar": {
        "required_fields": frozenset({"distance"}),
    },
    "coordinate_pair": {
        "required_fields": frozenset({"point"}),
    },
    "parameter_scalar": {
        "required_fields": frozenset({"parameter"}),
    },
    "parameter_solution_set": {
        "required_fields": frozenset({"solutions"}),
    },
    "comparison_label": {
        "required_fields": frozenset(
            {
                "comparison_result",
                "target_direction",
                "closer_line",
                "farther_line",
                "comparison_relation",
                "distances",
            }
        ),
    },
    "choice_label": {
        "required_fields": frozenset({"correct_label"}),
    },
    "multi_part_equation_area": {
        "required_fields": frozenset({"equation", "area"}),
    },
    "numeric_scalar": {
        "required_fields": frozenset({"canonical_form"}),
    },
}

# Deterministic migration: domain_operation / legacy task_type -> schema key.
DOMAIN_OPERATION_ANSWER_SCHEMA: dict[str, str] = {
    "point_to_line_distance": "distance_scalar",
    "distance_from_point_to_line": "distance_scalar",
    "parallel_lines_distance": "distance_scalar",
    "distance_between_parallel_lines": "distance_scalar",
    "solve_parameter_from_parallel_distance": "parameter_scalar",
    "construct_parallel_line_at_distance": "distance_scalar",
    "parallel_lines_distance_single_choice": "choice_label",
    "area_using_parallel_distance": "numeric_scalar",
    "find_parameter_from_point_line_distance": "parameter_scalar",
    "distance_from_point_to_line_parameter": "parameter_scalar",
    "distance_from_point_to_line_parameter_single_choice_scalar": "parameter_scalar",
    "foot_of_perpendicular": "coordinate_pair",
    "point_reflection_across_line": "coordinate_pair",
    "distance_comparison": "comparison_label",
    "compare_point_to_line_distances": "comparison_label",
    "point_slope": "line_equation",
    "two_points": "line_equation",
    "horizontal_line": "line_equation",
    "vertical_line": "line_equation",
    "oblique_line": "line_equation",
    "slope_intercept_equation": "line_equation",
    "slope_intercept_find_x_intercept": "numeric_scalar",
    "intercept_form_triangle_area": "numeric_scalar",
    "slope_intercept_read_slope_and_intercept": "slope_intercept",
    "intercept_form_equation": "line_equation",
    "intercept_form_triangle_area": "parameter_scalar",
    "intercept_form_equation_and_triangle_area": "multi_part_equation_area",
    "slope_from_general_or_intercept_form": "slope_intercept",
    "slope_from_general_form": "slope_intercept",
    "slope_of_horizontal_or_vertical_line": "slope_intercept",
    "parallel_line_slope": "slope_intercept",
    "perpendicular_line_slope": "slope_intercept",
    "parallel_condition_parameter": "parameter_scalar",
    "perpendicular_condition_parameter": "parameter_scalar",
    "compare_line_slopes": "choice_label",
    "line_through_point_parallel_to_line": "line_equation",
    "line_through_point_perpendicular_to_line": "line_equation",
    "line_through_intersection_parallel_to_line": "line_equation",
    "line_through_point_perpendicular_to_segment": "line_equation",
    "perpendicular_bisector_application": "line_equation",
    # Statistics table_chart single-choice operations → choice_label schema
    "read_category_value": "choice_label",
    "compare_category_values": "choice_label",
    "calculate_total_ratio_percent": "choice_label",
    "cumulative_above_fail_count": "choice_label",
    "cumulative_above_interval_count": "choice_label",
    "cumulative_below_interval_count": "choice_label",
    "compute_arithmetic_mean_from_raw_values": "numeric_scalar",
    "compute_arithmetic_mean_from_frequency_table": "numeric_scalar",
    "compute_weighted_mean": "numeric_scalar",
    "compute_median_from_raw_values": "numeric_scalar",
    "compute_mode_from_raw_values": "numeric_scalar",
    "compute_mode_from_frequency_table": "numeric_scalar",
    "compute_range": "numeric_scalar",
    "compute_population_variance": "numeric_scalar",
    "compute_population_standard_deviation": "numeric_scalar",
    "complete_descriptive_statistics_table": "numeric_scalar",
    "compute_quartiles_and_iqr": "numeric_scalar",
    "compare_dispersion": "numeric_scalar",
    "conceptual_dispersion_judgment": "choice_label",
}

PROBLEM_TYPE_ANSWER_SCHEMA: dict[str, str] = dict(DOMAIN_OPERATION_ANSWER_SCHEMA)


class AnswerSchemaMismatchError(ValueError):
    """Raised when matrix answer fields do not match the declared schema key."""


def resolve_answer_schema_key(
    *,
    answer_schema_key: str | None = None,
    domain_operation: str | None = None,
    problem_type_id: str | None = None,
    task_type: str | None = None,
) -> str | None:
    """Resolve schema key from explicit key or deterministic legacy identifiers."""
    explicit = str(answer_schema_key or "").strip()
    if explicit:
        return explicit
    for candidate in (domain_operation, problem_type_id, task_type):
        key = str(candidate or "").strip()
        if not key:
            continue
        mapped = PROBLEM_TYPE_ANSWER_SCHEMA.get(key)
        if mapped:
            return mapped
    return None


def validate_answer_schema(
    answer: dict[str, Any],
    *,
    answer_schema_key: str,
    component_id: str | None = None,
    problem_type_id: str | None = None,
    domain_operation: str | None = None,
) -> bool:
    """Validate matrix answer dict against a canonical schema key (fail-fast)."""
    if not isinstance(answer, dict):
        raise AnswerSchemaMismatchError("matrix['answer'] must be a dict.")

    schema_key = str(answer_schema_key or "").strip()
    schema = ANSWER_SCHEMAS.get(schema_key)
    if schema is None:
        raise AnswerSchemaMismatchError(
            f"answer_schema_unknown: answer_schema_key={schema_key!r}"
        )

    required = schema["required_fields"]
    actual = set(answer.keys())
    missing = sorted(field for field in required if field not in answer)
    if missing:
        raise AnswerSchemaMismatchError(
            "answer_schema_mismatch:\n"
            f"component_id={component_id or ''}\n"
            f"problem_type_id={problem_type_id or ''}\n"
            f"domain_operation={domain_operation or ''}\n"
            f"answer_schema_key={schema_key}\n"
            f"expected={sorted(required)}\n"
            f"actual={sorted(actual)}"
        )
    return True
