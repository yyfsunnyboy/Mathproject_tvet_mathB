"""Bridge from administrative skill_id to domain entrypoints via taxonomy config."""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

from core.registry.domain_operation_registry import (
    get_domain_operations,
    list_registered_domains,
)

REGISTRY_REVISION = "2026-06-23-v1.8"


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
    merged["allowed_operations"] = get_allowed_operations(fixed_domain_key, skill_id=key)
    merged["registry_revision"] = get_registry_revision(key)
    return merged



