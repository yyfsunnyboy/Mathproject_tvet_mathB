"""Single authoritative domain operation registry for Gencode V3.

Every domain operation is registered here exactly once.
taxonomy_registry, skill_fixed_domain_authority, resolver, scaffold, validator,
manifest and runtime all read from this module.

No layer may maintain its own independent operation allowlist. Adding a new
operation requires only one call to register_domain_spec() (or updating the
operations dict of an existing DomainCapabilitySpec) â all downstream layers
are automatically aware.

Verified bootstrap candidates are registered separately via
core.gencode.domain_bootstrap.candidate_registry and merged at resolution time.
Do not register AI bootstrap drafts here until promotion succeeds.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any


# ââ data model ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

@dataclass(frozen=True)
class OperationSpec:
    """Canonical specification for a single domain operation."""

    operation_key: str
    handler: str
    scaffold_builder: str | None = None
    payload_adapter: str | None = None
    validator: str | None = None
    supported_answer_types: tuple[str, ...] = ()
    supported_presentation_modes: tuple[str, ...] = ("short_answer",)
    required_source_features: tuple[str, ...] = ()
    runtime_contract: str | None = None
    provided_capabilities: tuple[str, ...] = ()


@dataclass
class DomainCapabilitySpec:
    """Canonical specification for a routing domain and all its operations."""

    domain_key: str
    domain_module: str
    entrypoint: str
    capabilities: frozenset[str]
    operations: dict[str, OperationSpec]

    @property
    def allowed_operations(self) -> list[str]:
        return list(self.operations.keys())


# ââ registry ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

_REGISTRY: dict[str, DomainCapabilitySpec] = {}


def register_domain_spec(spec: DomainCapabilitySpec) -> DomainCapabilitySpec:
    """Register a DomainCapabilitySpec.  Called at module-load time.

    All downstream layers (resolver / scaffold / validator / runtime) discover
    the new operations automatically because they call get_domain_operations().
    """
    _REGISTRY[spec.domain_key] = spec
    return spec


def get_domain_spec(domain_key: str) -> DomainCapabilitySpec | None:
    """Return the DomainCapabilitySpec for a domain key, or None."""
    return _REGISTRY.get(str(domain_key or "").strip())


def get_domain_operations(domain_key: str) -> list[str]:
    """Return ordered list of registered operation keys for a domain."""
    spec = get_domain_spec(domain_key)
    return spec.allowed_operations if spec is not None else []


def get_operation_spec(domain_key: str, operation_key: str) -> OperationSpec | None:
    """Return OperationSpec for a specific domain+operation pair, or None."""
    spec = get_domain_spec(domain_key)
    if spec is None:
        return None
    return spec.operations.get(str(operation_key or "").strip())


def list_registered_domains() -> list[str]:
    """Return all registered domain keys."""
    return list(_REGISTRY.keys())


def operation_is_registered(domain_key: str, operation_key: str) -> bool:
    """True iff the operation is registered for the domain."""
    return get_operation_spec(domain_key, operation_key) is not None


# ââ consistency check âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def check_registry_consistency() -> list[dict[str, Any]]:
    """Check registry for missing layers.

    Returns a list of finding dicts.  An empty list means the registry is
    internally consistent.  Called by the domain_consistency_validator at
    startup / test time.

    Each finding has shape::

        {
            "code":          "DOMAIN_OPERATION_REGISTRY_INCONSISTENT",
            "domain_key":    "statistics.table_chart",
            "operation":     "cumulative_above_fail_count",   # optional
            "missing_layers": ["runtime_dispatch"],
            "detail":        "<human-readable message>",
        }
    """
    issues: list[dict[str, Any]] = []

    for domain_key, spec in _REGISTRY.items():
        # 1. domain module must be importable
        try:
            module = importlib.import_module(spec.domain_module)
        except ModuleNotFoundError:
            issues.append({
                "code": "DOMAIN_OPERATION_REGISTRY_INCONSISTENT",
                "domain_key": domain_key,
                "missing_layers": ["domain_module"],
                "detail": f"module not found: {spec.domain_module}",
            })
            continue

        # 2. entrypoint must be callable
        if not callable(getattr(module, spec.entrypoint, None)):
            issues.append({
                "code": "DOMAIN_OPERATION_REGISTRY_INCONSISTENT",
                "domain_key": domain_key,
                "missing_layers": ["domain_entrypoint"],
                "detail": f"entrypoint not callable: {spec.entrypoint} in {spec.domain_module}",
            })

        # 3. every operation must have a non-empty handler
        for op_key, op_spec in spec.operations.items():
            missing: list[str] = []
            if not str(op_spec.handler or "").strip():
                missing.append("handler")
            if missing:
                issues.append({
                    "code": "DOMAIN_OPERATION_REGISTRY_INCONSISTENT",
                    "domain_key": domain_key,
                    "operation": op_key,
                    "missing_layers": missing,
                    "detail": f"incomplete OperationSpec for {op_key!r}",
                })

    return issues


# ââ helper for decorator-style registration âââââââââââââââââââââââââââââââââââ

def register_domain_operation(
    domain_key: str,
    operation_key: str,
    *,
    handler: str | None = None,
    scaffold_builder: str | None = None,
    payload_adapter: str | None = None,
    validator: str | None = None,
    supported_answer_types: tuple[str, ...] = (),
    supported_presentation_modes: tuple[str, ...] = ("short_answer",),
    required_source_features: tuple[str, ...] = (),
    runtime_contract: str | None = None,
) -> None:
    """Register a single operation into an existing domain spec.

    Usage::

        register_domain_operation(
            domain_key="statistics.table_chart",
            operation_key="my_new_operation",
            handler="build_statistical_chart_reading_matrix",
            supported_answer_types=("expression",),
        )

    If the domain spec does not yet exist this raises KeyError.
    Use register_domain_spec() to register a brand-new domain.
    """
    spec = get_domain_spec(domain_key)
    if spec is None:
        raise KeyError(
            f"register_domain_operation: domain {domain_key!r} not registered; "
            "call register_domain_spec() first"
        )
    effective_handler = str(handler or spec.entrypoint)
    op_spec = OperationSpec(
        operation_key=operation_key,
        handler=effective_handler,
        scaffold_builder=scaffold_builder,
        payload_adapter=payload_adapter,
        validator=validator,
        supported_answer_types=supported_answer_types,
        supported_presentation_modes=supported_presentation_modes,
        required_source_features=required_source_features,
        runtime_contract=runtime_contract,
    )
    spec.operations[operation_key] = op_spec


# ââ canonical registrations âââââââââââââââââââââââââââââââââââââââââââââââââââ
# Each domain is registered once.  All downstream layers read from _REGISTRY.

_op = OperationSpec  # convenience alias


register_domain_spec(DomainCapabilitySpec(
    domain_key="algebra.absolute_value",
    domain_module="core.domain.absolute_value_domain",
    entrypoint="build_absolute_value_matrix",
    capabilities=frozenset({
        "solve_basic_absolute_value_equation",
        "solve_basic_absolute_value_equation_no_solution",
        "number_line_distance_between_two_points",
        "absolute_value_inequality_zero_center_basic",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_interval_interpretation",
    }),
    operations={
        "solve_basic_absolute_value_equation": _op(
            "solve_basic_absolute_value_equation",
            "solve_basic_absolute_value_equation",
            supported_answer_types=("solution_set",),
            provided_capabilities=("solve_basic_absolute_value_equation",),
        ),
        "solve_basic_absolute_value_equation_no_solution": _op(
            "solve_basic_absolute_value_equation_no_solution",
            "solve_basic_absolute_value_equation_no_solution",
            supported_answer_types=("solution_set",),
            provided_capabilities=("solve_basic_absolute_value_equation_no_solution",),
        ),
        "number_line_distance_between_two_points": _op(
            "number_line_distance_between_two_points",
            "number_line_distance",
            supported_answer_types=("integer", "numeric"),
            provided_capabilities=("number_line_distance_between_two_points",),
        ),
        "absolute_value_inequality_zero_center_basic": _op(
            "absolute_value_inequality_zero_center_basic",
            "build_absolute_value_matrix",
            supported_answer_types=("interval_set",),
            provided_capabilities=("absolute_value_inequality_zero_center_basic",),
        ),
        "absolute_value_inequality_linear_expression_basic": _op(
            "absolute_value_inequality_linear_expression_basic",
            "build_absolute_value_matrix",
            supported_answer_types=("interval_set",),
            provided_capabilities=("absolute_value_inequality_linear_expression_basic",),
        ),
        "absolute_value_inequality_shifted_basic": _op(
            "absolute_value_inequality_shifted_basic",
            "build_absolute_value_matrix",
            supported_answer_types=("interval_set",),
            provided_capabilities=("absolute_value_inequality_shifted_basic",),
        ),
        "absolute_value_inequality_integer_solution_count_choice": _op(
            "absolute_value_inequality_integer_solution_count_choice",
            "build_absolute_value_matrix",
            supported_answer_types=("choice",),
            provided_capabilities=("absolute_value_inequality_integer_solution_count_choice",),
        ),
        "absolute_value_inequality_interval_interpretation": _op(
            "absolute_value_inequality_interval_interpretation",
            "build_absolute_value_matrix",
            supported_answer_types=("choice", "interval_set", "numeric", "expression"),
            provided_capabilities=("absolute_value_inequality_interval_interpretation",),
        ),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="coordinate_geometry.line_equation",
    domain_module="core.domain.coordinate_geometry.line_equation_domain",
    entrypoint="build_line_equation_matrix",
    capabilities=frozenset({
        "slope", "line_equation", "horizontal_line", "vertical_line",
        "point_slope", "intercept_form", "general_form", "two_points",
        "line_through_point_parallel_to_line", "line_through_point_perpendicular_to_line",
        "compare_line_slopes", "line_through_intersection_parallel_to_line",
        "line_through_point_perpendicular_to_segment", "perpendicular_bisector_application",
        "coordinate_geometry_word_problem", "graph_intercepts_and_linear_equation",
        "draw_constant_function_graph",
        "draw_linear_function_graph",
        "graph_based_linear_application_inverse",
        "linear_equation_from_two_points_choice",
        "linear_graph_feasibility_choice",
        "graph_based_linear_model_equation",
        "robust_budget_feasibility_choice",
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
        "parallel_segments_parameter_choice",
        "parallel_two_point_lines_parameter_choice",
        "parallel_and_perpendicular_slopes_from_reference",
        "triangle_right_angle_verification",
        "perpendicular_two_point_lines_parameter",
        "perpendicular_slope_quadrant_choice",
    }),
    operations={
        "two_points":                                   _op("two_points",                                   "build_line_equation_matrix", supported_answer_types=("expression",)),
        "point_slope":                                  _op("point_slope",                                  "build_line_equation_matrix", supported_answer_types=("expression",)),
        "horizontal_line":                              _op("horizontal_line",                              "build_line_equation_matrix", supported_answer_types=("expression",)),
        "vertical_line":                                _op("vertical_line",                                "build_line_equation_matrix", supported_answer_types=("expression",)),
        "oblique_line":                                 _op("oblique_line",                                 "build_line_equation_matrix", supported_answer_types=("expression",)),
        "slope_intercept_equation":                     _op("slope_intercept_equation",                     "build_line_equation_matrix", supported_answer_types=("expression",)),
        "slope_intercept_find_x_intercept":             _op("slope_intercept_find_x_intercept",             "build_line_equation_matrix", supported_answer_types=("expression",)),
        "slope_intercept_read_slope_and_intercept":     _op("slope_intercept_read_slope_and_intercept",     "build_line_equation_matrix", supported_answer_types=("expression",)),
        "intercept_form_equation":                      _op("intercept_form_equation",                      "build_line_equation_matrix", supported_answer_types=("expression",)),
        "intercept_form_triangle_area":                 _op("intercept_form_triangle_area",                 "build_line_equation_matrix", supported_answer_types=("expression",)),
        "intercept_form_equation_and_triangle_area":    _op("intercept_form_equation_and_triangle_area",    "build_line_equation_matrix", supported_answer_types=("expression",)),
        "intercept_form_from_intercept_sum_and_slope":  _op("intercept_form_from_intercept_sum_and_slope",  "build_line_equation_matrix", supported_answer_types=("expression",)),
        "parabola_secant_parallel_line_choice":         _op("parabola_secant_parallel_line_choice",         "build_line_equation_matrix", supported_answer_types=("choice",)),
        "triangle_area_bisector_line_equation":         _op("triangle_area_bisector_line_equation",         "build_line_equation_matrix", supported_answer_types=("expression",)),
        "slope_from_general_or_intercept_form":         _op("slope_from_general_or_intercept_form",         "build_line_equation_matrix", supported_answer_types=("expression",)),
        "slope_from_general_form":                      _op("slope_from_general_form",                      "build_line_equation_matrix", supported_answer_types=("expression",)),
        "slope_of_horizontal_or_vertical_line":         _op("slope_of_horizontal_or_vertical_line",         "build_line_equation_matrix", supported_answer_types=("expression",)),
        "line_through_point_parallel_to_line":          _op("line_through_point_parallel_to_line",          "build_line_equation_matrix", supported_answer_types=("expression",)),
        "line_through_point_perpendicular_to_line":     _op("line_through_point_perpendicular_to_line",     "build_line_equation_matrix", supported_answer_types=("expression",)),
        "parallel_line_slope":                          _op("parallel_line_slope",                          "build_line_equation_matrix", supported_answer_types=("expression",)),
        "perpendicular_line_slope":                     _op("perpendicular_line_slope",                     "build_line_equation_matrix", supported_answer_types=("expression",)),
        "parallel_condition_parameter":                 _op("parallel_condition_parameter",                 "build_line_equation_matrix", supported_answer_types=("expression",)),
        "perpendicular_condition_parameter":            _op("perpendicular_condition_parameter",            "build_line_equation_matrix", supported_answer_types=("expression",)),
        "compare_line_slopes":                          _op("compare_line_slopes",                          "build_line_equation_matrix", supported_answer_types=("choice",)),
        "slope_from_two_points":                        _op("slope_from_two_points",                        "build_line_equation_matrix", supported_answer_types=("expression",)),
        "solve_parameter_from_known_slope":              _op("solve_parameter_from_known_slope",              "build_line_equation_matrix", supported_answer_types=("expression",)),
        "solve_parameter_from_known_slope_choice":       _op("solve_parameter_from_known_slope_choice",       "build_line_equation_matrix", supported_answer_types=("choice",)),
        "collinear_three_points_parameter":             _op("collinear_three_points_parameter",             "build_line_equation_matrix", supported_answer_types=("expression",)),
        "non_triangle_collinear_parameter":             _op("non_triangle_collinear_parameter",             "build_line_equation_matrix", supported_answer_types=("expression",)),
        "parallel_segments_parameter":                  _op("parallel_segments_parameter",                  "build_line_equation_matrix", supported_answer_types=("expression",)),
        "perpendicular_segments_parameter":             _op("perpendicular_segments_parameter",             "build_line_equation_matrix", supported_answer_types=("expression",)),
        "collinear_three_points_parameter_choice":      _op("collinear_three_points_parameter_choice",      "build_line_equation_matrix", supported_answer_types=("choice",)),
        "slopes_of_named_segments":                     _op("slopes_of_named_segments",                     "build_line_equation_matrix", supported_answer_types=("multi_part",)),
        "classify_and_compare_figure_slopes":           _op("classify_and_compare_figure_slopes",           "build_line_equation_matrix", supported_answer_types=("multi_part",)),
        "parallel_segments_parameter_choice":           _op("parallel_segments_parameter_choice",           "build_line_equation_matrix", supported_answer_types=("choice",)),
        "parallel_two_point_lines_parameter_choice":    _op("parallel_two_point_lines_parameter_choice",    "build_line_equation_matrix", supported_answer_types=("choice",)),
        "parallel_and_perpendicular_slopes_from_reference": _op("parallel_and_perpendicular_slopes_from_reference", "build_line_equation_matrix", supported_answer_types=("multi_part",)),
        "triangle_right_angle_verification":            _op("triangle_right_angle_verification",            "build_line_equation_matrix", supported_answer_types=("expression",)),
        "perpendicular_two_point_lines_parameter":      _op("perpendicular_two_point_lines_parameter",      "build_line_equation_matrix", supported_answer_types=("expression",)),
        "perpendicular_slope_quadrant_choice":          _op("perpendicular_slope_quadrant_choice",          "build_line_equation_matrix", supported_answer_types=("choice",)),
        "line_through_intersection_parallel_to_line":   _op("line_through_intersection_parallel_to_line",   "build_line_equation_matrix", supported_answer_types=("expression",)),
        "line_through_point_perpendicular_to_segment":  _op("line_through_point_perpendicular_to_segment",  "build_line_equation_matrix", supported_answer_types=("expression",)),
        "perpendicular_bisector_application":           _op("perpendicular_bisector_application",           "build_line_equation_matrix", supported_answer_types=("expression",)),
        "coordinate_geometry_word_problem":             _op("coordinate_geometry_word_problem",             "build_line_equation_matrix", supported_answer_types=("expression",)),
        "graph_intercepts_and_linear_equation":         _op("graph_intercepts_and_linear_equation",         "build_graph_intercepts_and_linear_equation_matrix", supported_answer_types=("multi_part",), provided_capabilities=("graph_intercepts_and_linear_equation",)),
        "draw_constant_function_graph":                 _op("draw_constant_function_graph",                 "build_draw_constant_function_graph_matrix", supported_answer_types=("drawing",), supported_presentation_modes=("canvas",), provided_capabilities=("draw_constant_function_graph",)),
        "draw_linear_function_graph":                   _op("draw_linear_function_graph",                   "build_draw_linear_function_graph_matrix", supported_answer_types=("drawing",), supported_presentation_modes=("canvas",), provided_capabilities=("draw_linear_function_graph",)),
        "graph_based_linear_application_inverse":       _op("graph_based_linear_application_inverse",       "build_graph_based_linear_application_inverse_matrix", supported_answer_types=("numeric",), supported_presentation_modes=("graph_short_answer",), provided_capabilities=("graph_based_linear_application_inverse",)),
        "linear_equation_from_two_points_choice":       _op("linear_equation_from_two_points_choice",       "build_linear_equation_from_two_points_choice_matrix", supported_answer_types=("single_choice",), supported_presentation_modes=("single_choice",), provided_capabilities=("linear_equation_from_two_points_choice",)),
        "linear_graph_feasibility_choice":              _op("linear_graph_feasibility_choice",              "build_linear_graph_feasibility_choice_matrix", supported_answer_types=("single_choice",), supported_presentation_modes=("graph_single_choice",), provided_capabilities=("linear_graph_feasibility_choice",)),
        "graph_based_linear_model_equation":            _op("graph_based_linear_model_equation",            "build_graph_based_linear_model_equation_matrix", supported_answer_types=("single_choice",), supported_presentation_modes=("graph_single_choice",), provided_capabilities=("graph_based_linear_model_equation",)),
        "robust_budget_feasibility_choice":             _op("robust_budget_feasibility_choice",             "build_robust_budget_feasibility_choice_matrix", supported_answer_types=("single_choice",), supported_presentation_modes=("single_choice",), provided_capabilities=("robust_budget_feasibility_choice",)),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="coordinate_geometry.point_line_distance",
    domain_module="core.domain.coordinate_geometry.line_equation_domain",
    entrypoint="build_coordinate_geometry_matrix",
    capabilities=frozenset({"distance_from_point_to_line", "compare_point_to_line_distances"}),
    operations={
        "distance_from_point_to_line":                           _op("distance_from_point_to_line",                           "build_coordinate_geometry_matrix", supported_answer_types=("expression",)),
        "distance_from_point_to_line_parameter":                 _op("distance_from_point_to_line_parameter",                 "build_coordinate_geometry_matrix", supported_answer_types=("expression",)),
        "distance_from_point_to_line_parameter_single_choice_scalar": _op("distance_from_point_to_line_parameter_single_choice_scalar", "build_coordinate_geometry_matrix", supported_answer_types=("choice",)),
        "compare_point_to_line_distances":                       _op("compare_point_to_line_distances",                       "build_coordinate_geometry_matrix", supported_answer_types=("choice",)),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="coordinate_geometry.parallel_lines_distance",
    domain_module="core.domain.coordinate_geometry.parallel_lines_distance_domain",
    entrypoint="build_parallel_lines_distance_matrix",
    capabilities=frozenset({
        "distance_between_parallel_lines", "parallel_lines_distance",
        "solve_parameter_from_parallel_distance", "construct_parallel_line_at_distance",
        "parallel_lines_distance_single_choice", "area_using_parallel_distance",
    }),
    operations={
        "distance_between_parallel_lines":      _op("distance_between_parallel_lines",      "build_parallel_lines_distance_matrix", supported_answer_types=("expression",)),
        "solve_parameter_from_parallel_distance": _op("solve_parameter_from_parallel_distance", "build_parallel_lines_distance_matrix", supported_answer_types=("expression",)),
        "construct_parallel_line_at_distance":  _op("construct_parallel_line_at_distance",  "build_parallel_lines_distance_matrix", supported_answer_types=("expression",)),
        "parallel_lines_distance_single_choice": _op("parallel_lines_distance_single_choice", "build_parallel_lines_distance_matrix", supported_answer_types=("choice",)),
        "area_using_parallel_distance":         _op("area_using_parallel_distance",         "build_parallel_lines_distance_matrix", supported_answer_types=("expression",)),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="statistics.frequency_distribution",
    domain_module="core.domain.statistics.frequency_distribution_domain",
    entrypoint="build_frequency_distribution_table_matrix",
    capabilities=frozenset({
        "frequency_table", "class_interval", "class_boundary", "class_midpoint",
        "histogram", "frequency_polygon", "chart_consistency_validation",
        "frequency_distribution",
        "cumulative_frequency_table", "cumulative_frequency_graph",
        "less_than_cumulative", "greater_than_cumulative",
        "class_frequency_from_cumulative", "cumulative_monotonicity",
    }),
    operations={
        "frequency_table_construction_review":       _op("frequency_table_construction_review",       "build_frequency_distribution_table_matrix", supported_answer_types=("expression",)),
        "frequency_table_single_bin_count":          _op("frequency_table_single_bin_count",          "build_frequency_distribution_table_matrix", supported_answer_types=("expression",)),
        "histogram_reading":                         _op("histogram_reading",                         "build_frequency_distribution_table_matrix", supported_answer_types=("expression",)),
        "frequency_polygon_reading":                 _op("frequency_polygon_reading",                 "build_frequency_distribution_table_matrix", supported_answer_types=("expression",)),
        "frequency_distribution_chart_construction": _op("frequency_distribution_chart_construction", "build_frequency_distribution_table_matrix", supported_answer_types=("expression",)),
        "histogram_distribution_update":             _op("histogram_distribution_update",             "build_frequency_distribution_table_matrix", supported_answer_types=("expression",)),
        "cumulative_frequency_table_construction":   _op("cumulative_frequency_table_construction",   "build_cumulative_frequency_matrix", supported_answer_types=("expression",)),
        "less_than_cumulative_frequency_reading":    _op("less_than_cumulative_frequency_reading",    "build_cumulative_frequency_matrix", supported_answer_types=("expression",)),
        "greater_than_cumulative_frequency_reading": _op("greater_than_cumulative_frequency_reading", "build_cumulative_frequency_matrix", supported_answer_types=("expression",)),
        "class_frequency_from_cumulative_difference": _op("class_frequency_from_cumulative_difference", "build_cumulative_frequency_matrix", supported_answer_types=("expression",)),
        "cumulative_frequency_graph_reading":        _op("cumulative_frequency_graph_reading",        "build_cumulative_frequency_matrix", supported_answer_types=("expression",)),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="statistics.table_chart",
    domain_module="core.domain.statistics.table_chart_domain",
    entrypoint="build_statistical_chart_reading_matrix",
    capabilities=frozenset({
        "statistical_chart_reading", "table_chart",
        "read_category_value", "compare_category_values",
        "calculate_total_ratio_percent", "validate_chart_statement",
        "cumulative_above_fail_count", "cumulative_above_interval_count",
        "cumulative_below_interval_count",
    }),
    operations={
        # ââ generic table-chart operations ââââââââââââââââââââââââââââââââââ
        "read_category_value": _op(
            "read_category_value",
            "build_statistical_chart_reading_matrix",
            supported_answer_types=("expression",),
            supported_presentation_modes=("short_answer",),
        ),
        "compare_category_values": _op(
            "compare_category_values",
            "build_statistical_chart_reading_matrix",
            supported_answer_types=("expression",),
            supported_presentation_modes=("short_answer",),
        ),
        "calculate_total_ratio_percent": _op(
            "calculate_total_ratio_percent",
            "build_statistical_chart_reading_matrix",
            supported_answer_types=("expression",),
            supported_presentation_modes=("short_answer",),
        ),
        "validate_chart_statement": _op(
            "validate_chart_statement",
            "build_statistical_chart_reading_matrix",
            supported_answer_types=("choice",),
            supported_presentation_modes=("short_answer",),
        ),
        # ââ cumulative frequency polygon operations (formally registered) âââ
        "cumulative_above_fail_count": _op(
            "cumulative_above_fail_count",
            "build_statistical_chart_reading_matrix",
            supported_answer_types=("expression",),
            supported_presentation_modes=("short_answer",),
            required_source_features=("cumulative_frequency_polygon",),
            runtime_contract="cumulative_frequency_polygon_source_required",
        ),
        "cumulative_above_interval_count": _op(
            "cumulative_above_interval_count",
            "build_statistical_chart_reading_matrix",
            supported_answer_types=("expression",),
            supported_presentation_modes=("short_answer",),
            required_source_features=("cumulative_frequency_polygon",),
            runtime_contract="cumulative_frequency_polygon_source_required",
        ),
        "cumulative_below_interval_count": _op(
            "cumulative_below_interval_count",
            "build_statistical_chart_reading_matrix",
            supported_answer_types=("expression",),
            supported_presentation_modes=("short_answer",),
            required_source_features=("cumulative_frequency_polygon",),
            runtime_contract="cumulative_frequency_polygon_source_required",
        ),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="statistics.descriptive_statistics",
    domain_module="core.domain.statistics.descriptive_statistics_domain",
    entrypoint="build_descriptive_statistics_matrix",
    capabilities=frozenset({
        "arithmetic_mean",
        "weighted_mean",
        "median",
        "mode",
        "range",
        "variance",
        "standard_deviation",
        "sample_variance",
        "sample_standard_deviation",
        "quartile",
        "interquartile_range",
        "dispersion_comparison",
        "conceptual_dispersion_judgment",
        "frequency_weighted_statistics",
        "descriptive_statistics_table_completion",
        "descriptive_statistics",
        "empirical_rule_probability",
        "empirical_rule_population_count",
        "compare_distribution_spread",
    }),
    operations={
        "compute_arithmetic_mean_from_raw_values": _op(
            "compute_arithmetic_mean_from_raw_values",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric"),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("arithmetic_mean",),
        ),
        "compute_arithmetic_mean_from_frequency_table": _op(
            "compute_arithmetic_mean_from_frequency_table",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric"),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("arithmetic_mean", "frequency_weighted_statistics"),
        ),
        "compute_weighted_mean": _op(
            "compute_weighted_mean",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric"),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("weighted_mean",),
        ),
        "compute_median_from_raw_values": _op(
            "compute_median_from_raw_values",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric"),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("median",),
        ),
        "compute_mode_from_raw_values": _op(
            "compute_mode_from_raw_values",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric", "text_short", "unordered_set"),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("mode",),
        ),
        "compute_mode_from_frequency_table": _op(
            "compute_mode_from_frequency_table",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric", "text_short", "unordered_set"),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("mode", "frequency_weighted_statistics"),
        ),
        "compute_range": _op(
            "compute_range",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric"),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("range",),
        ),
        "compute_population_variance": _op(
            "compute_population_variance",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric"),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("variance",),
        ),
        "compute_population_standard_deviation": _op(
            "compute_population_standard_deviation",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric"),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("standard_deviation", "variance"),
        ),
        "compute_sample_variance": _op(
            "compute_sample_variance",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric"),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("sample_variance",),
        ),
        "compute_sample_standard_deviation": _op(
            "compute_sample_standard_deviation",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric"),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("sample_standard_deviation", "sample_variance"),
        ),
        "complete_descriptive_statistics_table": _op(
            "complete_descriptive_statistics_table",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("multi_blank", "table_fill"),
            supported_presentation_modes=("multi_blank", "table_fill"),
            provided_capabilities=(
                "descriptive_statistics_table_completion",
                "arithmetic_mean",
                "median",
                "range",
                "variance",
                "standard_deviation",
            ),
        ),
        "compute_quartiles_and_iqr": _op(
            "compute_quartiles_and_iqr",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("multi_part",),
            supported_presentation_modes=("short_answer", "multi_part"),
            provided_capabilities=("range", "quartile", "interquartile_range"),
        ),
        "compare_dispersion": _op(
            "compare_dispersion",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("multi_part",),
            supported_presentation_modes=("short_answer", "multi_part"),
            provided_capabilities=(
                "dispersion_comparison",
                "range",
                "quartile",
                "interquartile_range",
            ),
        ),
        "conceptual_dispersion_judgment": _op(
            "conceptual_dispersion_judgment",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("single_choice",),
            supported_presentation_modes=("single_choice",),
            provided_capabilities=("conceptual_dispersion_judgment",),
        ),
        "compute_linear_transform_median_and_range": _op(
            "compute_linear_transform_median_and_range",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("multi_part", "single_choice"),
            supported_presentation_modes=("single_choice", "multi_part"),
            provided_capabilities=("median", "range"),
        ),
        "empirical_rule_probability": _op(
            "empirical_rule_probability",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric", "multi_part", "table_fill", "multi_blank"),
            supported_presentation_modes=("short_answer", "multi_blank", "table_fill"),
            provided_capabilities=("empirical_rule_probability",),
        ),
        "empirical_rule_population_count": _op(
            "empirical_rule_population_count",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("expression", "numeric", "multi_part", "table_fill", "multi_blank", "single_choice"),
            supported_presentation_modes=("short_answer", "multi_blank", "table_fill", "single_choice"),
            provided_capabilities=("empirical_rule_population_count",),
        ),
        "compare_distribution_spread": _op(
            "compare_distribution_spread",
            "build_descriptive_statistics_matrix",
            supported_answer_types=("single_choice",),
            supported_presentation_modes=("single_choice",),
            provided_capabilities=("compare_distribution_spread",),
        ),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="coordinate_geometry.cartesian_coordinate",
    domain_module="core.domain.coordinate_geometry.cartesian_coordinate_domain",
    entrypoint="build_cartesian_coordinate_matrix",
    capabilities=frozenset({
        "cartesian_coordinate_quadrant_symbol_reasoning",
    }),
    operations={
        "cartesian_coordinate_quadrant_symbol_reasoning": _op(
            "cartesian_coordinate_quadrant_symbol_reasoning",
            "build_cartesian_coordinate_matrix",
            supported_answer_types=("choice", "single_choice"),
            supported_presentation_modes=("single_choice",),
            provided_capabilities=("cartesian_coordinate_quadrant_symbol_reasoning",),
        ),
    },
))

register_domain_spec(DomainCapabilitySpec(
    domain_key="coordinate_geometry.division_point_coordinates",
    domain_module="core.gencode.division_point_slot_engine",
    entrypoint="generate_division_point_payload",
    capabilities=frozenset({
        "compute_internal_division_point_coordinates",
        "compute_centroid_coordinates",
        "compute_section_point_distance_from_origin",
        "compute_midpoint_coordinates",
        "midpoint_coordinate",
        "midpoint_distance_from_origin",
        "parallelogram_fourth_vertex",
        "centroid_coordinate",
        "inverse_centroid_vertex",
        "triangle_median_length",
        "multi_part_midpoint_application",
        "graph_based_tiered_linear_application_multi_part",
        "collinear_trisection_coordinate",
    }),
    operations={
        "compute_internal_division_point_coordinates": _op(
            "compute_internal_division_point_coordinates",
            "generate_division_point_payload",
            supported_answer_types=("coordinate_pair", "single_choice"),
            supported_presentation_modes=("short_answer", "single_choice"),
            provided_capabilities=("compute_internal_division_point_coordinates",),
        ),
        "compute_centroid_coordinates": _op(
            "compute_centroid_coordinates",
            "generate_division_point_payload",
            supported_answer_types=("coordinate_pair", "single_choice"),
            supported_presentation_modes=("short_answer", "single_choice"),
            provided_capabilities=("compute_centroid_coordinates",),
        ),
        "compute_section_point_distance_from_origin": _op(
            "compute_section_point_distance_from_origin",
            "generate_division_point_payload",
            supported_answer_types=("single_choice",),
            supported_presentation_modes=("single_choice",),
            provided_capabilities=("compute_section_point_distance_from_origin",),
        ),
        "compute_midpoint_coordinates": _op(
            "compute_midpoint_coordinates",
            "generate_division_point_payload",
            supported_answer_types=("coordinate_pair", "single_choice"),
            supported_presentation_modes=("short_answer", "single_choice"),
            provided_capabilities=("compute_midpoint_coordinates",),
        ),
        "midpoint_coordinate": _op(
            "midpoint_coordinate",
            "generate_division_point_payload",
            supported_answer_types=("coordinate_pair",),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("midpoint_coordinate",),
        ),
        "midpoint_distance_from_origin": _op(
            "midpoint_distance_from_origin",
            "generate_division_point_payload",
            supported_answer_types=("radical_scalar",),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("midpoint_distance_from_origin",),
        ),
        "parallelogram_fourth_vertex": _op(
            "parallelogram_fourth_vertex",
            "generate_division_point_payload",
            supported_answer_types=("coordinate_pair",),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("parallelogram_fourth_vertex",),
        ),
        "centroid_coordinate": _op(
            "centroid_coordinate",
            "generate_division_point_payload",
            supported_answer_types=("coordinate_pair",),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("centroid_coordinate",),
        ),
        "inverse_centroid_vertex": _op(
            "inverse_centroid_vertex",
            "generate_division_point_payload",
            supported_answer_types=("coordinate_pair",),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("inverse_centroid_vertex",),
        ),
        "triangle_median_length": _op(
            "triangle_median_length",
            "generate_division_point_payload",
            supported_answer_types=("choice", "single_choice"),
            supported_presentation_modes=("single_choice",),
            provided_capabilities=("triangle_median_length",),
        ),
        "multi_part_midpoint_application": _op(
            "multi_part_midpoint_application",
            "generate_division_point_payload",
            supported_answer_types=("multi_part_scalar", "choice", "single_choice"),
            supported_presentation_modes=("short_answer", "single_choice"),
            provided_capabilities=("multi_part_midpoint_application",),
        ),
        "graph_based_tiered_linear_application_multi_part": _op(
            "graph_based_tiered_linear_application_multi_part",
            "build_graph_based_tiered_linear_application_multi_part_matrix",
            supported_answer_types=("multi_part",),
            supported_presentation_modes=("graph_multi_part", "multiple_inputs"),
            provided_capabilities=("graph_based_tiered_linear_application_multi_part",),
        ),
        "collinear_trisection_coordinate": _op(
            "collinear_trisection_coordinate",
            "build_collinear_trisection_coordinate_matrix",
            supported_answer_types=("coordinate_pair",),
            supported_presentation_modes=("short_answer",),
            provided_capabilities=("collinear_trisection_coordinate",),
        ),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="coordinate_geometry.distance_between_two_points",
    domain_module="core.domain.coordinate_geometry.distance_between_two_points_domain",
    entrypoint="build_distance_between_two_points_matrix",
    capabilities=frozenset({
        "compute_distance_between_two_points",
        "solve_unknown_coordinate_from_two_point_distance",
    }),
    operations={
        "compute_distance_between_two_points": _op(
            "compute_distance_between_two_points",
            "build_distance_between_two_points_matrix",
            supported_answer_types=("expression",),
            provided_capabilities=("short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",),
        ),
        "solve_unknown_coordinate_from_two_point_distance": _op(
            "solve_unknown_coordinate_from_two_point_distance",
            "build_distance_between_two_points_matrix",
            supported_answer_types=("expression", "solution_set"),
            provided_capabilities=("short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",),
        ),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="algebra.function_concept",
    domain_module="core.domain.function_concept_domain",
    entrypoint="build_function_concept_matrix",
    capabilities=frozenset({
        "free_fall_function_value_choice",
        "piecewise_utility_bill_savings_choice",
        "function_concept_free_fall_evaluation",
        "function_concept_piecewise_evaluation",
    }),
    operations={
        "free_fall_function_value_choice": _op(
            "free_fall_function_value_choice",
            "build_function_concept_matrix",
            supported_answer_types=("single_choice", "choice"),
            supported_presentation_modes=("single_choice",),
            provided_capabilities=("free_fall_function_value_choice",),
        ),
        "piecewise_utility_bill_savings_choice": _op(
            "piecewise_utility_bill_savings_choice",
            "build_function_concept_matrix",
            supported_answer_types=("single_choice", "choice"),
            supported_presentation_modes=("single_choice",),
            provided_capabilities=("piecewise_utility_bill_savings_choice",),
        ),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="algebra.polynomial",
    domain_module="core.domain.polynomial_domain",
    entrypoint="build_polynomial_matrix",
    capabilities=frozenset({
        "polynomial_descending_power_properties",
        "polynomial_param_degree_constraint",
        "polynomial_descending_power_table",
        "zero_polynomial_find_coeffs",
        "polynomial_degree_product_sum",
        "polynomial_add_sub",
        "polynomial_multiply",
        "polynomial_product_term_coefficient",
        "polynomial_long_division",
        "polynomial_synthetic_division",
        "polynomial_remainder_param_solve",
        "polynomial_shifted_basis_eval",
        "polynomial_equality_identity",
        "remainder_theorem_evaluate",
        "factor_theorem_root_factor",
        "polynomial_factoring",
        "rational_expression_arithmetic",
        "rational_equation_solve",
    }),
    operations={
        "polynomial_descending_power_properties": _op(
            "polynomial_descending_power_properties",
            "build_polynomial_matrix",
            supported_answer_types=("multi_part", "expression"),
            supported_presentation_modes=("short_answer", "multiple_inputs"),
            provided_capabilities=("polynomial_descending_power_properties",),
        ),
        "polynomial_param_degree_constraint": _op(
            "polynomial_param_degree_constraint",
            "build_polynomial_matrix",
            supported_answer_types=("multi_part", "expression"),
            supported_presentation_modes=("short_answer", "multiple_inputs"),
            provided_capabilities=("polynomial_param_degree_constraint",),
        ),
        "polynomial_descending_power_table": _op(
            "polynomial_descending_power_table",
            "build_polynomial_matrix",
            supported_answer_types=("multi_part", "expression"),
            supported_presentation_modes=("short_answer", "multiple_inputs"),
            provided_capabilities=("polynomial_descending_power_table",),
        ),
        "zero_polynomial_find_coeffs": _op(
            "zero_polynomial_find_coeffs",
            "build_polynomial_matrix",
            supported_answer_types=("multi_part", "expression"),
            supported_presentation_modes=("short_answer", "multiple_inputs"),
            provided_capabilities=("zero_polynomial_find_coeffs",),
        ),
        "polynomial_degree_product_sum": _op(
            "polynomial_degree_product_sum",
            "build_polynomial_matrix",
            supported_answer_types=("multi_part", "expression", "integer", "single_choice", "choice"),
            supported_presentation_modes=("short_answer", "multiple_inputs", "single_choice"),
            provided_capabilities=("polynomial_degree_product_sum",),
        ),
        "polynomial_add_sub": _op(
            "polynomial_add_sub",
            "build_polynomial_matrix",
            supported_answer_types=("multi_part", "expression"),
            provided_capabilities=("polynomial_add_sub",),
        ),
        "polynomial_multiply": _op(
            "polynomial_multiply",
            "build_polynomial_matrix",
            supported_answer_types=("multi_part", "expression"),
            provided_capabilities=("polynomial_multiply",),
        ),
        "polynomial_product_term_coefficient": _op(
            "polynomial_product_term_coefficient",
            "build_polynomial_matrix",
            supported_answer_types=("integer", "expression", "choice", "single_choice", "multi_part"),
            supported_presentation_modes=("short_answer", "single_choice"),
            provided_capabilities=("polynomial_product_term_coefficient",),
        ),
        "polynomial_long_division": _op(
            "polynomial_long_division",
            "build_polynomial_matrix",
            supported_answer_types=("multi_part", "expression", "single_choice", "choice"),
            supported_presentation_modes=("short_answer", "multiple_inputs", "single_choice"),
            provided_capabilities=("polynomial_long_division",),
        ),
        "polynomial_synthetic_division": _op(
            "polynomial_synthetic_division",
            "build_polynomial_matrix",
            supported_answer_types=("multi_part", "expression"),
            provided_capabilities=("polynomial_synthetic_division",),
        ),
        "polynomial_remainder_param_solve": _op(
            "polynomial_remainder_param_solve",
            "build_polynomial_matrix",
            supported_answer_types=("multi_part", "expression", "integer", "single_choice", "choice"),
            supported_presentation_modes=("short_answer", "multiple_inputs", "single_choice"),
            provided_capabilities=("polynomial_remainder_param_solve",),
        ),
        "polynomial_shifted_basis_eval": _op(
            "polynomial_shifted_basis_eval",
            "build_polynomial_matrix",
            supported_answer_types=("multi_part", "expression", "integer"),
            provided_capabilities=("polynomial_shifted_basis_eval",),
        ),
        "polynomial_equality_identity": _op(
            "polynomial_equality_identity",
            "build_polynomial_matrix",
            supported_answer_types=("multi_part", "expression", "integer", "single_choice", "choice"),
            supported_presentation_modes=("short_answer", "multiple_inputs", "single_choice"),
            provided_capabilities=("polynomial_equality_identity",),
        ),
        "remainder_theorem_evaluate": _op(
            "remainder_theorem_evaluate",
            "build_polynomial_matrix",
            supported_answer_types=("expression", "integer", "multi_part", "single_choice", "choice"),
            supported_presentation_modes=("short_answer", "multiple_inputs", "single_choice"),
            provided_capabilities=("remainder_theorem_evaluate",),
        ),
        "factor_theorem_root_factor": _op(
            "factor_theorem_root_factor",
            "build_polynomial_matrix",
            supported_answer_types=("expression", "multi_part", "single_choice", "choice"),
            supported_presentation_modes=("short_answer", "multiple_inputs", "single_choice"),
            provided_capabilities=("factor_theorem_root_factor",),
        ),
        "polynomial_factoring": _op(
            "polynomial_factoring",
            "build_polynomial_matrix",
            supported_answer_types=("expression", "multi_part", "single_choice", "choice"),
            supported_presentation_modes=("short_answer", "multiple_inputs", "single_choice"),
            provided_capabilities=("polynomial_factoring",),
        ),
        "rational_expression_arithmetic": _op(
            "rational_expression_arithmetic",
            "build_polynomial_matrix",
            supported_answer_types=("expression", "multi_part", "single_choice", "choice"),
            supported_presentation_modes=("short_answer", "multiple_inputs", "single_choice"),
            provided_capabilities=("rational_expression_arithmetic",),
        ),
        "rational_equation_solve": _op(
            "rational_equation_solve",
            "build_polynomial_matrix",
            supported_answer_types=("solution_set", "expression", "multi_part", "single_choice", "choice"),
            supported_presentation_modes=("short_answer", "multiple_inputs", "single_choice"),
            provided_capabilities=("rational_equation_solve",),
        ),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="geometry.similarity",
    domain_module="core.domain.geometry_similarity_domain",
    entrypoint="build_geometry_similarity_matrix",
    capabilities=frozenset({"solve_similar_triangle_proportion"}),
    operations={
        "solve_similar_triangle_proportion": _op(
            "solve_similar_triangle_proportion",
            "build_geometry_similarity_matrix",
            payload_adapter="core.gencode.b2_12_capability_adapter.adapt_b2_12_batch1_matrix",
            validator="validate_similarity_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("similar_triangle_correspondence", "one_unknown_proportion"),
            runtime_contract="b2_12_exact_symbolic_v1",
            provided_capabilities=("solve_similar_triangle_proportion",),
        ),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="trigonometry.acute",
    domain_module="core.domain.trigonometry_acute_domain",
    entrypoint="build_trigonometry_acute_matrix",
    capabilities=frozenset({
        "compute_right_triangle_trig_ratios",
        "solve_acute_trig_constraints",
        "evaluate_exact_special_angle_expression",
        "solve_right_triangle_projection",
        "evaluate_trig_decimal",
        "simplify_fundamental_trig_expression",
        "complete_cofunction_identity",
        "collinear_three_points_parameter",
        "sector_arc_and_area",
        "compute_chord_and_arc_length",
    }),
    operations={
        "compute_right_triangle_trig_ratios": _op(
            "compute_right_triangle_trig_ratios",
            "build_trigonometry_acute_matrix",
            payload_adapter="core.gencode.b2_12_capability_adapter.adapt_b2_12_batch1_matrix",
            validator="validate_acute_trigonometry_matrix",
            supported_answer_types=("multi_part", "expression", "short_answer"),
            supported_presentation_modes=("multiple_inputs", "short_answer"),
            required_source_features=("right_triangle_side_roles",),
            runtime_contract="b2_12_exact_symbolic_v1",
            provided_capabilities=("compute_right_triangle_trig_ratios",),
        ),
        "evaluate_exact_special_angle_expression": _op(
            "evaluate_exact_special_angle_expression",
            "build_trigonometry_acute_matrix",
            payload_adapter="core.gencode.b2_12_capability_adapter.adapt_b2_12_batch1_matrix",
            validator="validate_acute_trigonometry_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("exact_special_angle_terms",),
            runtime_contract="b2_12_exact_symbolic_v1",
            provided_capabilities=("evaluate_exact_special_angle_expression",),
        ),
        "complete_cofunction_identity": _op(
            "complete_cofunction_identity",
            "build_trigonometry_acute_matrix",
            payload_adapter="core.gencode.b2_12_capability_adapter.adapt_b2_12_batch1_matrix",
            validator="validate_acute_trigonometry_matrix",
            supported_answer_types=("multi_part", "expression", "short_answer"),
            supported_presentation_modes=("multiple_inputs", "short_answer"),
            required_source_features=("acute_angle", "cofunction_pair"),
            runtime_contract="b2_12_exact_symbolic_v1",
            provided_capabilities=("complete_cofunction_identity",),
        ),
        "solve_acute_trig_constraints": _op(
            "solve_acute_trig_constraints",
            "build_trigonometry_acute_matrix",
            payload_adapter="core.gencode.b2_12_capability_adapter.adapt_b2_12_batch1_matrix",
            validator="validate_acute_trigonometry_matrix",
            supported_answer_types=("multi_part", "single_choice", "short_answer"),
            supported_presentation_modes=("multiple_inputs", "single_choice", "short_answer"),
            required_source_features=("acute_angle", "trig_constraint", "target_expression"),
            runtime_contract="b2_12_exact_symbolic_v1",
            provided_capabilities=("solve_acute_trig_constraints",),
        ),
        "solve_right_triangle_projection": _op(
            "solve_right_triangle_projection",
            "build_trigonometry_acute_matrix",
            payload_adapter="core.gencode.b2_12_capability_adapter.adapt_b2_12_batch1_matrix",
            validator="validate_acute_trigonometry_matrix",
            supported_answer_types=("multi_part", "short_answer", "classification"),
            supported_presentation_modes=("multiple_inputs", "short_answer"),
            required_source_features=("hypotenuse", "acute_angle", "projection_target"),
            runtime_contract="b2_12_exact_symbolic_v1",
            provided_capabilities=("solve_right_triangle_projection",),
        ),
        "evaluate_trig_decimal": _op(
            "evaluate_trig_decimal",
            "build_trigonometry_acute_matrix",
            payload_adapter="core.gencode.b2_12_capability_adapter.adapt_b2_12_batch1_matrix",
            validator="validate_acute_trigonometry_matrix",
            supported_answer_types=("multi_part", "short_answer", "expression"),
            supported_presentation_modes=("multiple_inputs", "short_answer"),
            required_source_features=("degree_minute_angle", "precision", "rounding_policy"),
            runtime_contract="b2_12_decimal_round_half_up_v1",
            provided_capabilities=("evaluate_trig_decimal",),
        ),
        "simplify_fundamental_trig_expression": _op(
            "simplify_fundamental_trig_expression",
            "build_trigonometry_acute_matrix",
            payload_adapter="core.gencode.b2_12_capability_adapter.adapt_b2_12_batch1_matrix",
            validator="validate_acute_trigonometry_matrix",
            supported_answer_types=("multi_part", "short_answer"),
            supported_presentation_modes=("multiple_inputs", "short_answer"),
            required_source_features=("trig_expression", "fundamental_identity"),
            runtime_contract="b2_12_exact_symbolic_v1",
            provided_capabilities=("simplify_fundamental_trig_expression",),
        ),
        "collinear_three_points_parameter": _op(
            "collinear_three_points_parameter",
            "build_trigonometry_acute_matrix",
            payload_adapter="core.gencode.b2_12_capability_adapter.adapt_b2_12_batch1_matrix",
            validator="validate_acute_trigonometry_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("three_collinear_points", "one_coordinate_parameter"),
            runtime_contract="b2_12_coordinate_geometry_delegate_v1",
            provided_capabilities=("collinear_three_points_parameter",),
        ),
        "sector_arc_and_area": _op(
            "sector_arc_and_area",
            "build_trigonometry_acute_matrix",
            payload_adapter="core.gencode.b2_12_capability_adapter.adapt_b2_12_batch1_matrix",
            validator="validate_acute_trigonometry_matrix",
            supported_answer_types=("multi_part", "short_answer"),
            supported_presentation_modes=("multiple_inputs", "short_answer"),
            required_source_features=("radius", "central_angle"),
            runtime_contract="b2_12_sector_delegate_v1",
            provided_capabilities=("sector_arc_and_area",),
        ),
        "compute_chord_and_arc_length": _op(
            "compute_chord_and_arc_length",
            "build_trigonometry_acute_matrix",
            payload_adapter="core.gencode.b2_12_capability_adapter.adapt_b2_12_batch1_matrix",
            validator="validate_acute_trigonometry_matrix",
            supported_answer_types=("multi_part",),
            supported_presentation_modes=("multiple_inputs",),
            required_source_features=("radius", "central_angle", "chord_and_arc_targets"),
            runtime_contract="b2_12_exact_chord_sector_delegate_v1",
            provided_capabilities=("compute_chord_and_arc_length",),
        ),
    },
))


register_domain_spec(DomainCapabilitySpec(
    domain_key="trigonometry.angle",
    domain_module="core.domain.trigonometry_angle_domain",
    entrypoint="build_trigonometry_angle_matrix",
    capabilities=frozenset({
        "convert_angle_measure",
        "sector_arc_and_area",
        "coterminal_angles",
    }),
    operations={
        "convert_angle_measure": _op(
            "convert_angle_measure",
            "build_trigonometry_angle_matrix",
            supported_answer_types=("multi_part", "table_fill", "expression", "short_answer"),
            supported_presentation_modes=("short_answer", "multiple_inputs", "inline_table_input"),
            provided_capabilities=("convert_angle_measure",),
        ),
        "sector_arc_and_area": _op(
            "sector_arc_and_area",
            "build_trigonometry_angle_matrix",
            supported_answer_types=("multi_part", "expression", "short_answer"),
            supported_presentation_modes=("short_answer", "multiple_inputs"),
            provided_capabilities=("sector_arc_and_area",),
        ),
        "coterminal_angles": _op(
            "coterminal_angles",
            "build_trigonometry_angle_matrix",
            supported_answer_types=("multi_part", "single_choice", "choice", "solution_set", "short_answer"),
            supported_presentation_modes=("short_answer", "multiple_inputs", "single_choice"),
            provided_capabilities=("coterminal_angles",),
        ),
    },
))


_B2_14_ADAPTER = "core.gencode.b2_14_capability_adapter.adapt_b2_14_function_graph_matrix"
_B2_14_OPERATIONS = (
    "compare_trig_values_by_monotonicity", "solve_trig_value_quadratic_constraint",
    "analyze_affine_transformed_trig_graph", "calculate_trig_period_from_argument_scale",
    "classify_trig_expression_sign_change", "classify_trig_equation_feasibility",
    "analyze_tangent_absolute_graph_period", "evaluate_trig_decimal",
    "count_sine_cosine_intersections",
)
register_domain_spec(DomainCapabilitySpec(
    domain_key="trigonometry.function_graph",
    domain_module="core.domain.trigonometry_function_graph_domain",
    entrypoint="build_trigonometry_function_graph_matrix",
    capabilities=frozenset(_B2_14_OPERATIONS),
    operations={operation: _op(
        operation, "build_trigonometry_function_graph_matrix",
        payload_adapter=_B2_14_ADAPTER,
        validator="validate_trigonometry_function_graph_matrix",
        supported_answer_types=("short_answer", "single_choice", "multi_part"),
        supported_presentation_modes=("short_answer", "single_choice", "multiple_inputs"),
        required_source_features=("trig_function_contract",),
        runtime_contract="b2_14_exact_trig_function_graph_v1",
        provided_capabilities=(operation,),
    ) for operation in _B2_14_OPERATIONS},
))


_B2_13_ADAPTER = "core.gencode.b2_13_capability_adapter.adapt_b2_13_arbitrary_matrix"
register_domain_spec(DomainCapabilitySpec(
    domain_key="trigonometry.arbitrary_angle",
    domain_module="core.domain.trigonometry_arbitrary_domain",
    entrypoint="build_trigonometry_arbitrary_matrix",
    capabilities=frozenset({
        "classify_standard_position_angle",
        "compute_terminal_ray_trig_ratios",
        "solve_signed_trig_constraints",
        "evaluate_exact_arbitrary_angle_trig_expression",
        "complete_reference_angle_conversion",
        "classify_trig_derived_point_quadrant",
        "solve_arbitrary_angle_vertical_projection",
        "simplify_fundamental_trig_expression",
    }),
    operations={
        "classify_standard_position_angle": _op(
            "classify_standard_position_angle", "build_trigonometry_arbitrary_matrix",
            payload_adapter=_B2_13_ADAPTER, validator="validate_trigonometry_arbitrary_matrix",
            supported_answer_types=("multi_part", "short_answer"),
            supported_presentation_modes=("multiple_inputs", "short_answer"),
            required_source_features=("angle", "angle_unit"),
            runtime_contract="b2_13_exact_angle_location_v1",
            provided_capabilities=("classify_standard_position_angle",)),
        "compute_terminal_ray_trig_ratios": _op(
            "compute_terminal_ray_trig_ratios", "build_trigonometry_arbitrary_matrix",
            payload_adapter=_B2_13_ADAPTER, validator="validate_trigonometry_arbitrary_matrix",
            supported_answer_types=("multi_part",), supported_presentation_modes=("multiple_inputs",),
            required_source_features=("terminal_point",), runtime_contract="b2_13_exact_terminal_ratios_v1",
            provided_capabilities=("compute_terminal_ray_trig_ratios",)),
        "solve_signed_trig_constraints": _op(
            "solve_signed_trig_constraints", "build_trigonometry_arbitrary_matrix",
            payload_adapter=_B2_13_ADAPTER, validator="validate_trigonometry_arbitrary_matrix",
            supported_answer_types=("multi_part", "short_answer"),
            supported_presentation_modes=("multiple_inputs", "short_answer"),
            required_source_features=("signed_trig_constraints",), runtime_contract="b2_13_exact_signed_constraints_v1",
            provided_capabilities=("solve_signed_trig_constraints",)),
        "evaluate_exact_arbitrary_angle_trig_expression": _op(
            "evaluate_exact_arbitrary_angle_trig_expression", "build_trigonometry_arbitrary_matrix",
            payload_adapter=_B2_13_ADAPTER, validator="validate_trigonometry_arbitrary_matrix",
            supported_answer_types=("multi_part", "short_answer"),
            supported_presentation_modes=("multiple_inputs", "short_answer"),
            required_source_features=("structured_trig_expression",), runtime_contract="b2_13_exact_arbitrary_expression_v1",
            provided_capabilities=("evaluate_exact_arbitrary_angle_trig_expression",)),
        "complete_reference_angle_conversion": _op(
            "complete_reference_angle_conversion", "build_trigonometry_arbitrary_matrix",
            payload_adapter=_B2_13_ADAPTER, validator="validate_trigonometry_arbitrary_matrix",
            supported_answer_types=("table_fill", "multi_part"),
            supported_presentation_modes=("inline_table_input", "multiple_inputs"),
            required_source_features=("angle", "function", "structured_required_form"),
            runtime_contract="b2_13_reference_angle_ast_v1",
            provided_capabilities=("complete_reference_angle_conversion",)),
        "classify_trig_derived_point_quadrant": _op(
            "classify_trig_derived_point_quadrant", "build_trigonometry_arbitrary_matrix",
            payload_adapter=_B2_13_ADAPTER, validator="validate_trigonometry_arbitrary_matrix",
            supported_answer_types=("single_choice", "short_answer", "classification"),
            supported_presentation_modes=("single_choice", "short_answer"),
            required_source_features=("trig_derived_point",), runtime_contract="b2_13_exact_derived_point_sign_v1",
            provided_capabilities=("classify_trig_derived_point_quadrant",)),
        "solve_arbitrary_angle_vertical_projection": _op(
            "solve_arbitrary_angle_vertical_projection", "build_trigonometry_arbitrary_matrix",
            payload_adapter=_B2_13_ADAPTER, validator="validate_trigonometry_arbitrary_matrix",
            supported_answer_types=("short_answer", "expression"), supported_presentation_modes=("short_answer",),
            required_source_features=("radius", "arbitrary_angle", "base_elevation"),
            runtime_contract="b2_13_exact_signed_projection_v1",
            provided_capabilities=("solve_arbitrary_angle_vertical_projection",)),
        "simplify_fundamental_trig_expression": _op(
            "simplify_fundamental_trig_expression", "build_trigonometry_arbitrary_matrix",
            payload_adapter="core.gencode.b2_12_capability_adapter.adapt_b2_12_batch1_matrix",
            validator="validate_trigonometry_arbitrary_matrix",
            supported_answer_types=("multi_part", "short_answer"),
            supported_presentation_modes=("multiple_inputs", "short_answer"),
            required_source_features=("trig_expression", "fundamental_identity"),
            runtime_contract="b2_12_exact_symbolic_v1",
            provided_capabilities=("simplify_fundamental_trig_expression",)),
    },
))


_B2_21_SINE_ADAPTER = "core.gencode.b2_21_law_of_sines_capability_adapter.adapt_b2_21_law_of_sines_matrix"

register_domain_spec(DomainCapabilitySpec(
    domain_key="trigonometry.law_of_sines",
    domain_module="core.domain.trigonometry_law_of_sines_domain",
    entrypoint="build_trigonometry_law_of_sines_matrix",
    capabilities=frozenset({
        "compute_triangle_area_sas",
        "solve_side_and_circumradius_by_sines",
        "solve_angle_by_law_of_sines",
        "compute_sin_from_side_and_circumradius",
        "solve_side_ratio_by_law_of_sines",
        "solve_side_by_law_of_sines",
    }),
    operations={
        "compute_triangle_area_sas": _op(
            "compute_triangle_area_sas",
            "build_trigonometry_law_of_sines_matrix",
            payload_adapter=_B2_21_SINE_ADAPTER,
            validator="validate_trigonometry_law_of_sines_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("two_sides", "included_angle"),
            runtime_contract="b2_21_law_of_sines_exact_v1",
            provided_capabilities=("compute_triangle_area_sas",),
        ),
        "solve_side_and_circumradius_by_sines": _op(
            "solve_side_and_circumradius_by_sines",
            "build_trigonometry_law_of_sines_matrix",
            payload_adapter=_B2_21_SINE_ADAPTER,
            validator="validate_trigonometry_law_of_sines_matrix",
            supported_answer_types=("multi_part", "short_answer"),
            supported_presentation_modes=("multiple_inputs", "short_answer"),
            required_source_features=("two_angles", "one_side", "circumradius"),
            runtime_contract="b2_21_law_of_sines_exact_v1",
            provided_capabilities=("solve_side_and_circumradius_by_sines",),
        ),
        "solve_angle_by_law_of_sines": _op(
            "solve_angle_by_law_of_sines",
            "build_trigonometry_law_of_sines_matrix",
            payload_adapter=_B2_21_SINE_ADAPTER,
            validator="validate_trigonometry_law_of_sines_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("ssa", "unique_angle"),
            runtime_contract="b2_21_law_of_sines_exact_v1",
            provided_capabilities=("solve_angle_by_law_of_sines",),
        ),
        "compute_sin_from_side_and_circumradius": _op(
            "compute_sin_from_side_and_circumradius",
            "build_trigonometry_law_of_sines_matrix",
            payload_adapter=_B2_21_SINE_ADAPTER,
            validator="validate_trigonometry_law_of_sines_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("side", "circumradius_or_area"),
            runtime_contract="b2_21_law_of_sines_exact_v1",
            provided_capabilities=("compute_sin_from_side_and_circumradius",),
        ),
        "solve_side_ratio_by_law_of_sines": _op(
            "solve_side_ratio_by_law_of_sines",
            "build_trigonometry_law_of_sines_matrix",
            payload_adapter=_B2_21_SINE_ADAPTER,
            validator="validate_trigonometry_law_of_sines_matrix",
            supported_answer_types=("single_choice", "expression"),
            supported_presentation_modes=("single_choice", "short_answer"),
            required_source_features=("two_angles", "side_ratio"),
            runtime_contract="b2_21_law_of_sines_exact_v1",
            provided_capabilities=("solve_side_ratio_by_law_of_sines",),
        ),
        "solve_side_by_law_of_sines": _op(
            "solve_side_by_law_of_sines",
            "build_trigonometry_law_of_sines_matrix",
            payload_adapter=_B2_21_SINE_ADAPTER,
            validator="validate_trigonometry_law_of_sines_matrix",
            supported_answer_types=("single_choice", "expression"),
            supported_presentation_modes=("single_choice", "short_answer"),
            required_source_features=("aas_or_asa", "target_side"),
            runtime_contract="b2_21_law_of_sines_exact_v1",
            provided_capabilities=("solve_side_by_law_of_sines",),
        ),
    },
))


_B2_21_COSINE_ADAPTER = "core.gencode.b2_21_law_of_cosines_capability_adapter.adapt_b2_21_law_of_cosines_matrix"

register_domain_spec(DomainCapabilitySpec(
    domain_key="trigonometry.law_of_cosines",
    domain_module="core.domain.trigonometry_law_of_cosines_domain",
    entrypoint="build_trigonometry_law_of_cosines_matrix",
    capabilities=frozenset({
        "solve_side_by_law_of_cosines",
        "solve_angle_by_law_of_cosines",
        "solve_cosine_identity_angle",
        "solve_detour_extra_distance_by_cosines",
        "compute_circumradius_from_three_sides",
    }),
    operations={
        "solve_side_by_law_of_cosines": _op(
            "solve_side_by_law_of_cosines",
            "build_trigonometry_law_of_cosines_matrix",
            payload_adapter=_B2_21_COSINE_ADAPTER,
            validator="validate_trigonometry_law_of_cosines_matrix",
            supported_answer_types=("expression", "single_choice", "short_answer"),
            supported_presentation_modes=("short_answer", "single_choice"),
            required_source_features=("two_sides", "included_angle"),
            runtime_contract="b2_21_law_of_cosines_exact_v1",
            provided_capabilities=("solve_side_by_law_of_cosines",),
        ),
        "solve_angle_by_law_of_cosines": _op(
            "solve_angle_by_law_of_cosines",
            "build_trigonometry_law_of_cosines_matrix",
            payload_adapter=_B2_21_COSINE_ADAPTER,
            validator="validate_trigonometry_law_of_cosines_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("three_sides",),
            runtime_contract="b2_21_law_of_cosines_exact_v1",
            provided_capabilities=("solve_angle_by_law_of_cosines",),
        ),
        "solve_cosine_identity_angle": _op(
            "solve_cosine_identity_angle",
            "build_trigonometry_law_of_cosines_matrix",
            payload_adapter=_B2_21_COSINE_ADAPTER,
            validator="validate_trigonometry_law_of_cosines_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("cosine_identity",),
            runtime_contract="b2_21_law_of_cosines_exact_v1",
            provided_capabilities=("solve_cosine_identity_angle",),
        ),
        "solve_detour_extra_distance_by_cosines": _op(
            "solve_detour_extra_distance_by_cosines",
            "build_trigonometry_law_of_cosines_matrix",
            payload_adapter=_B2_21_COSINE_ADAPTER,
            validator="validate_trigonometry_law_of_cosines_matrix",
            supported_answer_types=("single_choice", "expression"),
            supported_presentation_modes=("single_choice", "short_answer"),
            required_source_features=("application_path", "included_angle"),
            runtime_contract="b2_21_law_of_cosines_exact_v1",
            provided_capabilities=("solve_detour_extra_distance_by_cosines",),
        ),
        "compute_circumradius_from_three_sides": _op(
            "compute_circumradius_from_three_sides",
            "build_trigonometry_law_of_cosines_matrix",
            payload_adapter=_B2_21_COSINE_ADAPTER,
            validator="validate_trigonometry_law_of_cosines_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("three_sides", "circumradius"),
            runtime_contract="b2_21_law_of_cosines_exact_v1",
            provided_capabilities=("compute_circumradius_from_three_sides",),
        ),
    },
))


_B2_223_MEASUREMENT_ADAPTER = (
    "core.gencode.b2_223_right_triangle_measurement_capability_adapter"
    ".adapt_b2_223_right_triangle_measurement_matrix"
)

register_domain_spec(DomainCapabilitySpec(
    domain_key="trigonometry.right_triangle_measurement",
    domain_module="core.domain.trigonometry_right_triangle_measurement_domain",
    entrypoint="build_trigonometry_right_triangle_measurement_matrix",
    capabilities=frozenset({
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
    }),
    operations={
        "solve_height_from_sight_line_elevation": _op(
            "solve_height_from_sight_line_elevation",
            "build_trigonometry_right_triangle_measurement_matrix",
            payload_adapter=_B2_223_MEASUREMENT_ADAPTER,
            validator="validate_trigonometry_right_triangle_measurement_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("sight_line", "elevation_angle"),
            runtime_contract="b2_223_right_triangle_measurement_exact_v1",
            provided_capabilities=("solve_height_from_sight_line_elevation",),
        ),
        "solve_adjacent_from_hypotenuse_ground_angle": _op(
            "solve_adjacent_from_hypotenuse_ground_angle",
            "build_trigonometry_right_triangle_measurement_matrix",
            payload_adapter=_B2_223_MEASUREMENT_ADAPTER,
            validator="validate_trigonometry_right_triangle_measurement_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("ladder_or_hypotenuse", "ground_angle"),
            runtime_contract="b2_223_right_triangle_measurement_exact_v1",
            provided_capabilities=("solve_adjacent_from_hypotenuse_ground_angle",),
        ),
        "solve_opposite_from_adjacent_elevation": _op(
            "solve_opposite_from_adjacent_elevation",
            "build_trigonometry_right_triangle_measurement_matrix",
            payload_adapter=_B2_223_MEASUREMENT_ADAPTER,
            validator="validate_trigonometry_right_triangle_measurement_matrix",
            supported_answer_types=("expression", "short_answer", "single_choice"),
            supported_presentation_modes=("short_answer", "single_choice"),
            required_source_features=("adjacent_distance", "elevation_angle"),
            runtime_contract="b2_223_right_triangle_measurement_exact_v1",
            provided_capabilities=("solve_opposite_from_adjacent_elevation",),
        ),
        "solve_horizontal_from_height_elevation": _op(
            "solve_horizontal_from_height_elevation",
            "build_trigonometry_right_triangle_measurement_matrix",
            payload_adapter=_B2_223_MEASUREMENT_ADAPTER,
            validator="validate_trigonometry_right_triangle_measurement_matrix",
            supported_answer_types=("expression", "short_answer", "single_choice"),
            supported_presentation_modes=("short_answer", "single_choice"),
            required_source_features=("known_height", "elevation_angle"),
            runtime_contract="b2_223_right_triangle_measurement_exact_v1",
            provided_capabilities=("solve_horizontal_from_height_elevation",),
        ),
        "solve_horizontal_from_height_depression": _op(
            "solve_horizontal_from_height_depression",
            "build_trigonometry_right_triangle_measurement_matrix",
            payload_adapter=_B2_223_MEASUREMENT_ADAPTER,
            validator="validate_trigonometry_right_triangle_measurement_matrix",
            supported_answer_types=("expression", "short_answer", "single_choice"),
            supported_presentation_modes=("short_answer", "single_choice"),
            required_source_features=("known_height", "depression_angle"),
            runtime_contract="b2_223_right_triangle_measurement_exact_v1",
            provided_capabilities=("solve_horizontal_from_height_depression",),
        ),
        "solve_two_elevation_horizontal_shift": _op(
            "solve_two_elevation_horizontal_shift",
            "build_trigonometry_right_triangle_measurement_matrix",
            payload_adapter=_B2_223_MEASUREMENT_ADAPTER,
            validator="validate_trigonometry_right_triangle_measurement_matrix",
            supported_answer_types=("expression", "short_answer", "single_choice"),
            supported_presentation_modes=("short_answer", "single_choice"),
            required_source_features=("known_height", "two_elevations"),
            runtime_contract="b2_223_right_triangle_measurement_exact_v1",
            provided_capabilities=("solve_two_elevation_horizontal_shift",),
        ),
        "solve_two_elevation_unknown_height": _op(
            "solve_two_elevation_unknown_height",
            "build_trigonometry_right_triangle_measurement_matrix",
            payload_adapter=_B2_223_MEASUREMENT_ADAPTER,
            validator="validate_trigonometry_right_triangle_measurement_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("advance_distance", "two_elevations"),
            runtime_contract="b2_223_right_triangle_measurement_exact_v1",
            provided_capabilities=("solve_two_elevation_unknown_height",),
        ),
        "solve_building_height_with_flagpole_elevations": _op(
            "solve_building_height_with_flagpole_elevations",
            "build_trigonometry_right_triangle_measurement_matrix",
            payload_adapter=_B2_223_MEASUREMENT_ADAPTER,
            validator="validate_trigonometry_right_triangle_measurement_matrix",
            supported_answer_types=("expression", "short_answer", "single_choice"),
            supported_presentation_modes=("short_answer", "single_choice"),
            required_source_features=("flagpole_length", "two_elevations_same_station"),
            runtime_contract="b2_223_right_triangle_measurement_exact_v1",
            provided_capabilities=("solve_building_height_with_flagpole_elevations",),
        ),
        "solve_broken_tree_original_height": _op(
            "solve_broken_tree_original_height",
            "build_trigonometry_right_triangle_measurement_matrix",
            payload_adapter=_B2_223_MEASUREMENT_ADAPTER,
            validator="validate_trigonometry_right_triangle_measurement_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("broken_tree", "tan_and_cos"),
            runtime_contract="b2_223_right_triangle_measurement_exact_v1",
            provided_capabilities=("solve_broken_tree_original_height",),
        ),
        "solve_height_decimal_from_sight_line_elevation": _op(
            "solve_height_decimal_from_sight_line_elevation",
            "build_trigonometry_right_triangle_measurement_matrix",
            payload_adapter=_B2_223_MEASUREMENT_ADAPTER,
            validator="validate_trigonometry_right_triangle_measurement_matrix",
            supported_answer_types=("expression", "short_answer"),
            supported_presentation_modes=("short_answer",),
            required_source_features=("sight_line", "non_special_elevation", "decimal_round"),
            runtime_contract="b2_223_right_triangle_measurement_decimal_v1",
            provided_capabilities=("solve_height_decimal_from_sight_line_elevation",),
        ),
    },
))


_B2_224_OBLIQUE_ADAPTER = (
    "core.gencode.b2_224_oblique_triangle_measurement_capability_adapter"
    ".adapt_b2_224_oblique_triangle_measurement_matrix"
)

register_domain_spec(DomainCapabilitySpec(
    domain_key="trigonometry.oblique_triangle_measurement",
    domain_module="core.domain.trigonometry_oblique_triangle_measurement_domain",
    entrypoint="build_trigonometry_oblique_triangle_measurement_matrix",
    capabilities=frozenset({
        "solve_side_by_law_of_sines",
        "solve_side_by_law_of_cosines",
    }),
    operations={
        "solve_side_by_law_of_sines": _op(
            "solve_side_by_law_of_sines",
            "build_trigonometry_oblique_triangle_measurement_matrix",
            payload_adapter=_B2_224_OBLIQUE_ADAPTER,
            validator="validate_trigonometry_oblique_triangle_measurement_matrix",
            supported_answer_types=("single_choice", "expression", "short_answer"),
            supported_presentation_modes=("single_choice", "short_answer"),
            required_source_features=("oblique_triangle", "law_of_sines", "measurement"),
            runtime_contract="b2_224_oblique_measurement_delegate_sines_v1",
            provided_capabilities=("solve_side_by_law_of_sines",),
        ),
        "solve_side_by_law_of_cosines": _op(
            "solve_side_by_law_of_cosines",
            "build_trigonometry_oblique_triangle_measurement_matrix",
            payload_adapter=_B2_224_OBLIQUE_ADAPTER,
            validator="validate_trigonometry_oblique_triangle_measurement_matrix",
            supported_answer_types=("expression", "short_answer", "single_choice"),
            supported_presentation_modes=("short_answer", "single_choice"),
            required_source_features=("oblique_triangle", "law_of_cosines", "measurement"),
            runtime_contract="b2_224_oblique_measurement_delegate_cosines_v1",
            provided_capabilities=("solve_side_by_law_of_cosines",),
        ),
    },
))


_B2_225_SOLID_ADAPTER = (
    "core.gencode.b2_225_solid_measurement_capability_adapter"
    ".adapt_b2_225_solid_measurement_matrix"
)

register_domain_spec(DomainCapabilitySpec(
    domain_key="trigonometry.solid_measurement",
    domain_module="core.domain.trigonometry_solid_measurement_domain",
    entrypoint="build_trigonometry_solid_measurement_matrix",
    capabilities=frozenset({
        "solve_tower_two_elevation_path_and_river_width",
        "solve_height_from_two_elevation_tan_ratios",
        "solve_height_from_isosceles_bearing_walk_elevation",
    }),
    operations={
        "solve_tower_two_elevation_path_and_river_width": _op(
            "solve_tower_two_elevation_path_and_river_width",
            "build_trigonometry_solid_measurement_matrix",
            payload_adapter=_B2_225_SOLID_ADAPTER,
            validator="validate_trigonometry_solid_measurement_matrix",
            supported_answer_types=("multi_part", "short_answer"),
            supported_presentation_modes=("multiple_inputs", "short_answer"),
            required_source_features=("tower_height", "two_elevations", "right_path_river"),
            runtime_contract="b2_225_solid_measurement_compose_v1",
            provided_capabilities=("solve_tower_two_elevation_path_and_river_width",),
        ),
        "solve_height_from_two_elevation_tan_ratios": _op(
            "solve_height_from_two_elevation_tan_ratios",
            "build_trigonometry_solid_measurement_matrix",
            payload_adapter=_B2_225_SOLID_ADAPTER,
            validator="validate_trigonometry_solid_measurement_matrix",
            supported_answer_types=("single_choice", "expression"),
            supported_presentation_modes=("single_choice", "short_answer"),
            required_source_features=("advance_distance", "two_tan_elevations"),
            runtime_contract="b2_225_solid_measurement_tan_ratio_v1",
            provided_capabilities=("solve_height_from_two_elevation_tan_ratios",),
        ),
        "solve_height_from_isosceles_bearing_walk_elevation": _op(
            "solve_height_from_isosceles_bearing_walk_elevation",
            "build_trigonometry_solid_measurement_matrix",
            payload_adapter=_B2_225_SOLID_ADAPTER,
            validator="validate_trigonometry_solid_measurement_matrix",
            supported_answer_types=("single_choice", "expression"),
            supported_presentation_modes=("single_choice", "short_answer"),
            required_source_features=("bearing_walk", "elevation", "isosceles_horizontal"),
            runtime_contract="b2_225_solid_measurement_bearing_v1",
            provided_capabilities=("solve_height_from_isosceles_bearing_walk_elevation",),
        ),
    },
))


_VECTOR_PLANE_ADAPTER = "core.gencode.vector_plane_capability_adapter.adapt_vector_plane_matrix"
_VECTOR_PLANE_VALIDATOR = "validate_vector_plane_matrix"
_VECTOR_PLANE_BUILDER = "build_vector_plane_matrix"
_VECTOR_PLANE_CONTRACT = "b2_ch3_vector_plane_exact_v1"


def _vector_op(
    key: str,
    *,
    answer_types: tuple[str, ...] = ("expression", "short_answer"),
    presentation_modes: tuple[str, ...] = ("short_answer",),
    features: tuple[str, ...] = (),
) -> OperationSpec:
    return _op(
        key,
        _VECTOR_PLANE_BUILDER,
        payload_adapter=_VECTOR_PLANE_ADAPTER,
        validator=_VECTOR_PLANE_VALIDATOR,
        supported_answer_types=answer_types,
        supported_presentation_modes=presentation_modes,
        required_source_features=features,
        runtime_contract=_VECTOR_PLANE_CONTRACT,
        provided_capabilities=(key,),
    )


register_domain_spec(DomainCapabilitySpec(
    domain_key="vector.plane",
    domain_module="core.domain.vector_plane_domain",
    entrypoint="build_vector_plane_matrix",
    capabilities=frozenset({
        "compute_vector_components_and_magnitude",
        "solve_equal_vector_coordinates",
        "compute_directed_segment_and_magnitude",
        "solve_parallelogram_fourth_vertex",
        "compute_triangle_perimeter_from_two_vectors",
        "compute_vector_sum_difference",
        "compute_point_vectors_linear_combination",
        "compute_scalar_multiple_coordinates",
        "solve_parallel_vector_parameter",
        "compute_unit_vector",
        "compute_dot_product_coordinates",
        "compute_dot_product_from_magnitudes_angle",
        "solve_perpendicular_vector_parameter",
        "compute_cosine_of_angle_from_dot",
        "compute_vector_linear_combination",
        "compute_scaled_direction_vector",
        "compute_triangle_chain_and_perimeter",
        "simplify_vector_path_expression",
        "express_named_vectors_in_given_basis",
        "solve_scalar_multiple_relation_fill",
        "express_section_point_vector",
        "solve_section_coefficient_pair",
        "identify_equal_vector_mcq",
        "identify_resultant_path_mcq",
        "construct_linear_combination_choice",
        "express_linear_combination_from_givens",
        "compute_directed_segment_mixed_multipart",
        "compute_chain_closure_vector_mcq",
        "solve_point_from_vector_combination",
        "solve_collinear_ratio_mcq",
        "solve_unknown_vector_linear_equation",
        "solve_parallel_then_magnitude_mcq",
        "identify_unit_vector_mcq",
        "solve_navigation_heading_correction",
        "classify_angle_quality_from_dot_mcq",
        "compute_regular_polygon_edge_dot",
        "compute_dot_identity_multipart",
        "plot_navigation_points_coordinates",
        "compute_midpoint_dot_product",
        "solve_dot_product_parameter_mcq",
        "solve_perpendicular_composite_parameter",
        "classify_dot_sign_from_diagram_mcq",
        "expand_perpendicular_dot_product",
        "solve_angle_from_magnitude_identity",
    }),
    operations={
        "compute_vector_components_and_magnitude": _vector_op(
            "compute_vector_components_and_magnitude",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("vector_components", "magnitude"),
        ),
        "solve_equal_vector_coordinates": _vector_op(
            "solve_equal_vector_coordinates",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("equal_vectors", "unknown_coordinates"),
        ),
        "compute_directed_segment_and_magnitude": _vector_op(
            "compute_directed_segment_and_magnitude",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("two_points", "directed_segment"),
        ),
        "solve_parallelogram_fourth_vertex": _vector_op(
            "solve_parallelogram_fourth_vertex",
            features=("parallelogram", "three_vertices"),
        ),
        "compute_triangle_perimeter_from_two_vectors": _vector_op(
            "compute_triangle_perimeter_from_two_vectors",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("two_side_vectors", "perimeter"),
        ),
        "compute_vector_sum_difference": _vector_op(
            "compute_vector_sum_difference",
            answer_types=("expression", "multi_part", "short_answer"),
            presentation_modes=("short_answer", "multiple_inputs"),
            features=("vector_add_sub",),
        ),
        "compute_point_vectors_linear_combination": _vector_op(
            "compute_point_vectors_linear_combination",
            features=("named_points", "segment_sum"),
        ),
        "compute_scalar_multiple_coordinates": _vector_op(
            "compute_scalar_multiple_coordinates",
            features=("scalar_multiple",),
        ),
        "solve_parallel_vector_parameter": _vector_op(
            "solve_parallel_vector_parameter",
            features=("parallel_condition", "parameter"),
        ),
        "compute_unit_vector": _vector_op(
            "compute_unit_vector",
            features=("unit_vector",),
        ),
        "compute_dot_product_coordinates": _vector_op(
            "compute_dot_product_coordinates",
            features=("dot_product", "coordinates"),
        ),
        "compute_dot_product_from_magnitudes_angle": _vector_op(
            "compute_dot_product_from_magnitudes_angle",
            answer_types=("expression", "multi_part", "short_answer"),
            presentation_modes=("short_answer", "multiple_inputs"),
            features=("magnitudes", "included_angle"),
        ),
        "solve_perpendicular_vector_parameter": _vector_op(
            "solve_perpendicular_vector_parameter",
            answer_types=("expression", "multi_part", "short_answer"),
            presentation_modes=("short_answer", "multiple_inputs"),
            features=("perpendicular_condition", "parameter"),
        ),
        "compute_cosine_of_angle_from_dot": _vector_op(
            "compute_cosine_of_angle_from_dot",
            answer_types=("expression", "single_choice"),
            presentation_modes=("short_answer", "single_choice"),
            features=("angle_cosine", "dot_product"),
        ),
        "compute_vector_linear_combination": _vector_op(
            "compute_vector_linear_combination",
            features=("linear_combination",),
        ),
        "compute_scaled_direction_vector": _vector_op(
            "compute_scaled_direction_vector",
            answer_types=("expression", "multi_part", "short_answer"),
            presentation_modes=("short_answer", "multiple_inputs"),
            features=("scaled_unit", "direction"),
        ),
        "compute_triangle_chain_and_perimeter": _vector_op(
            "compute_triangle_chain_and_perimeter",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("chain_sides", "perimeter"),
        ),
        "simplify_vector_path_expression": _vector_op(
            "simplify_vector_path_expression",
            answer_types=("expression", "short_answer"),
            presentation_modes=("short_answer",),
            features=("gap_coverage",),
        ),
        "express_named_vectors_in_given_basis": _vector_op(
            "express_named_vectors_in_given_basis",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("gap_coverage",),
        ),
        "solve_scalar_multiple_relation_fill": _vector_op(
            "solve_scalar_multiple_relation_fill",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("gap_coverage",),
        ),
        "express_section_point_vector": _vector_op(
            "express_section_point_vector",
            answer_types=("expression", "short_answer"),
            presentation_modes=("short_answer",),
            features=("gap_coverage",),
        ),
        "solve_section_coefficient_pair": _vector_op(
            "solve_section_coefficient_pair",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("gap_coverage",),
        ),
        "identify_equal_vector_mcq": _vector_op(
            "identify_equal_vector_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage",),
        ),
        "identify_resultant_path_mcq": _vector_op(
            "identify_resultant_path_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage",),
        ),
        "construct_linear_combination_choice": _vector_op(
            "construct_linear_combination_choice",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage",),
        ),
        "express_linear_combination_from_givens": _vector_op(
            "express_linear_combination_from_givens",
            answer_types=("expression", "short_answer"),
            presentation_modes=("short_answer",),
            features=("gap_coverage",),
        ),
        "compute_directed_segment_mixed_multipart": _vector_op(
            "compute_directed_segment_mixed_multipart",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("gap_coverage",),
        ),
        "compute_chain_closure_vector_mcq": _vector_op(
            "compute_chain_closure_vector_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage",),
        ),
        "solve_point_from_vector_combination": _vector_op(
            "solve_point_from_vector_combination",
            answer_types=("expression", "short_answer"),
            presentation_modes=("short_answer",),
            features=("gap_coverage",),
        ),
        "solve_collinear_ratio_mcq": _vector_op(
            "solve_collinear_ratio_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage",),
        ),
        "solve_unknown_vector_linear_equation": _vector_op(
            "solve_unknown_vector_linear_equation",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage",),
        ),
        "solve_parallel_then_magnitude_mcq": _vector_op(
            "solve_parallel_then_magnitude_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage",),
        ),
        "identify_unit_vector_mcq": _vector_op(
            "identify_unit_vector_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage",),
        ),
        "solve_navigation_heading_correction": _vector_op(
            "solve_navigation_heading_correction",
            answer_types=("expression", "short_answer"),
            presentation_modes=("short_answer",),
            features=("gap_coverage",),
        ),
        "classify_angle_quality_from_dot_mcq": _vector_op(
            "classify_angle_quality_from_dot_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage",),
        ),
        "compute_regular_polygon_edge_dot": _vector_op(
            "compute_regular_polygon_edge_dot",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("gap_coverage",),
        ),
        "compute_dot_identity_multipart": _vector_op(
            "compute_dot_identity_multipart",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("gap_coverage",),
        ),
        "plot_navigation_points_coordinates": _vector_op(
            "plot_navigation_points_coordinates",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("gap_coverage",),
        ),
        "compute_midpoint_dot_product": _vector_op(
            "compute_midpoint_dot_product",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage",),
        ),
        "solve_dot_product_parameter_mcq": _vector_op(
            "solve_dot_product_parameter_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage",),
        ),
        "solve_perpendicular_composite_parameter": _vector_op(
            "solve_perpendicular_composite_parameter",
            answer_types=("expression", "short_answer"),
            presentation_modes=("short_answer",),
            features=("gap_coverage",),
        ),
        "classify_dot_sign_from_diagram_mcq": _vector_op(
            "classify_dot_sign_from_diagram_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage",),
        ),
        "expand_perpendicular_dot_product": _vector_op(
            "expand_perpendicular_dot_product",
            answer_types=("expression", "short_answer"),
            presentation_modes=("short_answer",),
            features=("gap_coverage",),
        ),
        "solve_angle_from_magnitude_identity": _vector_op(
            "solve_angle_from_magnitude_identity",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("gap_coverage",),
        ),
    },
))


_CIRCLE_PLANE_ADAPTER = "core.gencode.circle_plane_capability_adapter.adapt_circle_plane_matrix"
_CIRCLE_PLANE_VALIDATOR = "validate_circle_plane_matrix"
_CIRCLE_PLANE_BUILDER = "build_circle_plane_matrix"
_CIRCLE_PLANE_CONTRACT = "b2_ch4_circle_plane_exact_v1"


def _circle_op(
    key: str,
    *,
    answer_types: tuple[str, ...] = ("expression", "short_answer"),
    presentation_modes: tuple[str, ...] = ("short_answer",),
    features: tuple[str, ...] = (),
) -> OperationSpec:
    return _op(
        key,
        _CIRCLE_PLANE_BUILDER,
        payload_adapter=_CIRCLE_PLANE_ADAPTER,
        validator=_CIRCLE_PLANE_VALIDATOR,
        supported_answer_types=answer_types,
        supported_presentation_modes=presentation_modes,
        required_source_features=features,
        runtime_contract=_CIRCLE_PLANE_CONTRACT,
        provided_capabilities=(key,),
    )


register_domain_spec(DomainCapabilitySpec(
    domain_key="circle.plane",
    domain_module="core.domain.circle_plane_domain",
    entrypoint="build_circle_plane_matrix",
    capabilities=frozenset({
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
        "identify_center_radius_from_general",
        "solve_circle_parameter_range",
        "circle_through_three_points",
        "circle_center_on_axis_area",
        "classify_general_circle_graph",
        "compute_circle_area_from_general",
        "identify_circle_from_product_form",
        "evaluate_center_radius_expression",
        # 4-2.1 point vs circle
        "classify_point_vs_circles_multipart",
        "solve_point_circle_parameter_range",
        "identify_point_on_circle_mcq",
        # 4-2.2 line vs circle
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
        # 4-2.3 tangent lines
        "tangent_at_point_on_circle",
        "tangents_parallel_to_line",
        "tangents_perpendicular_to_line",
        "compute_tangents_from_point_quad_area",
        # 4-2.4 tangent segments
        "compute_tangent_segment_lengths",
        "count_line_vs_two_circles_intersections",
        "compute_tangent_segment_length_mcq",
        "solve_circle_parameter_range_mcq",
        "tangent_at_point_on_circle_mcq",
    }),
    operations={
        "identify_center_radius_from_standard": _circle_op(
            "identify_center_radius_from_standard",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("standard_form", "center_radius"),
        ),
        "write_circle_from_center_radius": _circle_op(
            "write_circle_from_center_radius",
            features=("center", "radius", "standard_form"),
        ),
        "write_circle_from_center_point": _circle_op(
            "write_circle_from_center_point",
            features=("center", "point_on_circle"),
        ),
        "write_circle_equations_from_conditions": _circle_op(
            "write_circle_equations_from_conditions",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("multipart_conditions",),
        ),
        "interpret_circular_locus_equation": _circle_op(
            "interpret_circular_locus_equation",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("locus", "center_radius"),
        ),
        "circle_from_diameter_endpoints": _circle_op(
            "circle_from_diameter_endpoints",
            answer_types=("expression", "single_choice", "short_answer"),
            presentation_modes=("short_answer", "single_choice"),
            features=("diameter", "midpoint"),
        ),
        "circle_equal_radius_at_origin": _circle_op(
            "circle_equal_radius_at_origin",
            features=("equal_radius", "origin_center"),
        ),
        "translate_and_scale_circle": _circle_op(
            "translate_and_scale_circle",
            answer_types=("expression", "single_choice", "short_answer"),
            presentation_modes=("short_answer", "single_choice"),
            features=("translate", "scale_radius"),
        ),
        "circle_origin_through_lines_intersection": _circle_op(
            "circle_origin_through_lines_intersection",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("line_intersection", "origin_center"),
        ),
        "circle_same_center_scaled_area": _circle_op(
            "circle_same_center_scaled_area",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("same_center", "area_scale"),
        ),
        "circle_center_tangent_to_line": _circle_op(
            "circle_center_tangent_to_line",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("tangent", "point_line_distance"),
        ),
        "identify_center_radius_from_general": _circle_op(
            "identify_center_radius_from_general",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("general_form", "complete_square"),
        ),
        "solve_circle_parameter_range": _circle_op(
            "solve_circle_parameter_range",
            answer_types=("expression", "single_choice", "short_answer"),
            presentation_modes=("short_answer", "single_choice"),
            features=("parameter", "validity"),
        ),
        "circle_through_three_points": _circle_op(
            "circle_through_three_points",
            answer_types=("expression", "single_choice", "short_answer"),
            presentation_modes=("short_answer", "single_choice"),
            features=("three_points", "circumcircle"),
        ),
        "circle_center_on_axis_area": _circle_op(
            "circle_center_on_axis_area",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("center_constraint", "area"),
        ),
        "classify_general_circle_graph": _circle_op(
            "classify_general_circle_graph",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("validity", "degenerate"),
        ),
        "compute_circle_area_from_general": _circle_op(
            "compute_circle_area_from_general",
            features=("general_form", "area"),
        ),
        "identify_circle_from_product_form": _circle_op(
            "identify_circle_from_product_form",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("expand", "identify"),
        ),
        "evaluate_center_radius_expression": _circle_op(
            "evaluate_center_radius_expression",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("center_radius", "expression"),
        ),
        # ââ 4-2.1 point vs circle ââââââââââââââââââââââââââââââââââââââââââââ
        "classify_point_vs_circles_multipart": _circle_op(
            "classify_point_vs_circles_multipart",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("point_vs_circle", "classification"),
        ),
        "solve_point_circle_parameter_range": _circle_op(
            "solve_point_circle_parameter_range",
            answer_types=("multi_part", "expression", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("point_vs_circle", "parameter"),
        ),
        "identify_point_on_circle_mcq": _circle_op(
            "identify_point_on_circle_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("point_vs_circle", "identify"),
        ),
        # ââ 4-2.2 line vs circle âââââââââââââââââââââââââââââââââââââââââââââ
        "classify_line_circle_relation": _circle_op(
            "classify_line_circle_relation",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("line_vs_circle", "point_line_distance", "classification"),
        ),
        "classify_lines_vs_circle_multipart": _circle_op(
            "classify_lines_vs_circle_multipart",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("line_vs_circle", "classification"),
        ),
        "solve_line_circle_parameter_range": _circle_op(
            "solve_line_circle_parameter_range",
            answer_types=("multi_part", "expression", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("line_vs_circle", "parameter"),
        ),
        "solve_line_circle_tangent_parameter": _circle_op(
            "solve_line_circle_tangent_parameter",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("tangent", "parameter"),
        ),
        "compute_chord_length": _circle_op(
            "compute_chord_length",
            answer_types=("multi_part", "expression", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("chord", "point_line_distance"),
        ),
        "solve_line_circle_relation_ranges_multipart": _circle_op(
            "solve_line_circle_relation_ranges_multipart",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("line_vs_circle", "parameter", "classification"),
        ),
        "count_line_circle_intersections": _circle_op(
            "count_line_circle_intersections",
            answer_types=("multi_part", "expression", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("line_vs_circle", "intersection_count"),
        ),
        "compute_storm_path_length_in_circle": _circle_op(
            "compute_storm_path_length_in_circle",
            answer_types=("multi_part", "expression", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("chord", "application"),
        ),
        "classify_line_circle_relation_mcq": _circle_op(
            "classify_line_circle_relation_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("line_vs_circle", "classification"),
        ),
        "solve_diameter_chord_parameter_mcq": _circle_op(
            "solve_diameter_chord_parameter_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("diameter", "parameter"),
        ),
        "compute_triangle_center_chord_area": _circle_op(
            "compute_triangle_center_chord_area",
            answer_types=("multi_part", "expression", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("chord", "area"),
        ),
        "solve_axis_tangent_parameter": _circle_op(
            "solve_axis_tangent_parameter",
            answer_types=("multi_part", "expression", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("tangent", "parameter", "general_form"),
        ),
        # ââ 4-2.3 tangent lines ââââââââââââââââââââââââââââââââââââââââââââââ
        "tangent_at_point_on_circle": _circle_op(
            "tangent_at_point_on_circle",
            answer_types=("multi_part", "expression", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("tangent", "point_on_circle"),
        ),
        "tangents_parallel_to_line": _circle_op(
            "tangents_parallel_to_line",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("tangent", "parallel"),
        ),
        "tangents_perpendicular_to_line": _circle_op(
            "tangents_perpendicular_to_line",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("tangent", "perpendicular"),
        ),
        "compute_tangents_from_point_quad_area": _circle_op(
            "compute_tangents_from_point_quad_area",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("tangent_segment", "area"),
        ),
        # ââ 4-2.4 tangent segments âââââââââââââââââââââââââââââââââââââââââââ
        "compute_tangent_segment_lengths": _circle_op(
            "compute_tangent_segment_lengths",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("tangent_segment",),
        ),
        "count_line_vs_two_circles_intersections": _circle_op(
            "count_line_vs_two_circles_intersections",
            answer_types=("multi_part", "short_answer"),
            presentation_modes=("multiple_inputs", "short_answer"),
            features=("line_vs_circle", "intersection_count"),
        ),
        "compute_tangent_segment_length_mcq": _circle_op(
            "compute_tangent_segment_length_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("tangent_segment",),
        ),
        "solve_circle_parameter_range_mcq": _circle_op(
            "solve_circle_parameter_range_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage", "mcq"),
        ),
        "tangent_at_point_on_circle_mcq": _circle_op(
            "tangent_at_point_on_circle_mcq",
            answer_types=("single_choice", "expression"),
            presentation_modes=("single_choice", "short_answer"),
            features=("gap_coverage", "mcq"),
        ),
    },
))


# --- B3 Chapter 1: sequence / series ---
_SEQ_SERIES_ADAPTER = "core.gencode.sequence_series_capability_adapter.adapt_sequence_series_matrix"
_SEQ_SERIES_VALIDATOR = "validate_sequence_series_matrix"
_SEQ_SERIES_BUILDER = "build_sequence_series_matrix"
_SEQ_SERIES_CONTRACT = "b3_ch1_sequence_series_exact_v1"
_SEQ_SERIES_OPS = (
    "expand_general_term_first_n",
    "arithmetic_nth_from_a1_d",
    "arithmetic_d_from_a1_an",
    "arithmetic_from_two_terms",
    "arithmetic_insert_terms",
    "arithmetic_mean_solve",
    "arithmetic_recurrence_general",
    "arithmetic_series_sum_given",
    "arithmetic_series_recover_param",
    "arithmetic_series_from_two_terms",
    "arithmetic_sum_multiples_range",
    "arithmetic_odd_count_mid_total",
    "geometric_nth_from_a1_r",
    "geometric_r_from_a1_an",
    "geometric_from_two_terms",
    "geometric_insert_terms",
    "geometric_mean_value",
    "geometric_mean_solve_x",
    "geometric_recurrence_general",
    "geometric_series_sum_given",
    "geometric_series_recover_param",
    "geometric_ratio_from_shifted_pair_sums",
    "geometric_ratio_from_product_quotient",
    "arithmetic_index_and_total_sum",
    "arithmetic_first_threshold_crossing",
    "geometric_first_threshold_crossing",
    "ap_gp_mixed_mean_middle",
)
_SEQ_SERIES_MULTIPART = frozenset({
    "expand_general_term_first_n",
    "arithmetic_from_two_terms",
    "arithmetic_recurrence_general",
    "geometric_mean_value",
    "geometric_recurrence_general",
    "arithmetic_index_and_total_sum",
})


def _seq_op(key: str) -> OperationSpec:
    multipart = key in _SEQ_SERIES_MULTIPART
    return _op(
        key,
        _SEQ_SERIES_BUILDER,
        payload_adapter=_SEQ_SERIES_ADAPTER,
        validator=_SEQ_SERIES_VALIDATOR,
        supported_answer_types=(("multi_part", "short_answer") if multipart else ("expression", "short_answer")),
        supported_presentation_modes=(("multiple_inputs", "short_answer") if multipart else ("short_answer",)),
        required_source_features=("sequence_or_series",),
        runtime_contract=_SEQ_SERIES_CONTRACT,
        provided_capabilities=(key,),
    )


register_domain_spec(DomainCapabilitySpec(
    domain_key="sequence.series",
    domain_module="core.domain.sequence_series_domain",
    entrypoint="build_sequence_series_matrix",
    capabilities=frozenset(_SEQ_SERIES_OPS),
    operations={op: _seq_op(op) for op in _SEQ_SERIES_OPS},
))
