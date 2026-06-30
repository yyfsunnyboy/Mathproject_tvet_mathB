"""Single authoritative domain operation registry for Gencode V3.

Every domain operation is registered here exactly once.
taxonomy_registry, skill_fixed_domain_authority, resolver, scaffold, validator,
manifest and runtime all read from this module.

No layer may maintain its own independent operation allowlist. Adding a new
operation requires only one call to register_domain_spec() (or updating the
operations dict of an existing DomainCapabilitySpec) — all downstream layers
are automatically aware.

Verified bootstrap candidates are registered separately via
core.gencode.domain_bootstrap.candidate_registry and merged at resolution time.
Do not register AI bootstrap drafts here until promotion succeeds.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any


# ── data model ────────────────────────────────────────────────────────────────

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


# ── registry ──────────────────────────────────────────────────────────────────

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


# ── consistency check ─────────────────────────────────────────────────────────

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


# ── helper for decorator-style registration ───────────────────────────────────

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


# ── canonical registrations ───────────────────────────────────────────────────
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
        "coordinate_geometry_word_problem",
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
        "line_through_intersection_parallel_to_line":   _op("line_through_intersection_parallel_to_line",   "build_line_equation_matrix", supported_answer_types=("expression",)),
        "line_through_point_perpendicular_to_segment":  _op("line_through_point_perpendicular_to_segment",  "build_line_equation_matrix", supported_answer_types=("expression",)),
        "perpendicular_bisector_application":           _op("perpendicular_bisector_application",           "build_line_equation_matrix", supported_answer_types=("expression",)),
        "coordinate_geometry_word_problem":             _op("coordinate_geometry_word_problem",             "build_line_equation_matrix", supported_answer_types=("expression",)),
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
        # ── generic table-chart operations ──────────────────────────────────
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
        # ── cumulative frequency polygon operations (formally registered) ───
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
