"""Skill-Fixed Domain Authority — deterministic routing gates for Gencode V3."""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.registry.taxonomy_registry import (
    SkillDomainNotRegisteredError,
    get_allowed_operations,
    get_fixed_domain_key,
    get_registry_revision,
    resolve_domain_for_skill,
)
from core.gencode.v3_error_codes import (
    DOMAIN_BINDING_MISSING,
    DOMAIN_FUNCTION_MISSING,
    DOMAIN_OPERATION_MISSING,
    DOMAIN_OVERRIDE_NOT_FOUND,
    DOMAIN_CAPABILITY_PARTIAL,
    DOMAIN_CAPABILITY_UNRESOLVED,
    DOMAIN_PROVIDER_MISSING,
    DOMAIN_ADAPTER_FAILED,
)

logger = logging.getLogger(__name__)

# Routing blocker codes (also used as tracker gencode_status where applicable).
SKILL_DOMAIN_NOT_REGISTERED = DOMAIN_BINDING_MISSING
DOMAIN_OPERATION_NOT_ALLOWED = "domain_operation_not_allowed"
UNSUPPORTED_DOMAIN_OPERATION = "unsupported_domain_operation"
FIXED_DOMAIN_VIOLATION = "fixed_domain_violation"
OPERATION_CONTRACT_MISMATCH = "operation_contract_mismatch"

AI_IGNORED_ROUTING_FIELDS = frozenset(
    {
        "domain_key",
        "domain_family",
        "recommended_skill",
        "nearest_template",
        "domain",
        "fixed_domain_key",
    }
)

# Registry of domain capabilities & providers
DOMAIN_PROVIDERS = {
    "coordinate_geometry.line_equation": {
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_line_equation_matrix",
        "capabilities": {
            "slope", "line_equation", "horizontal_line", "vertical_line", 
            "point_slope", "intercept_form", "general_form", "two_points", 
            "line_through_point_parallel_to_line", "line_through_point_perpendicular_to_line",
            "compare_line_slopes", "line_through_intersection_parallel_to_line",
            "line_through_point_perpendicular_to_segment", "perpendicular_bisector_application",
            "coordinate_geometry_word_problem"
        },
        "allowed_operations": [
            "two_points", "point_slope", "horizontal_line", "vertical_line",
            "oblique_line", "slope_intercept_equation", "slope_intercept_find_x_intercept",
            "slope_intercept_read_slope_and_intercept", "intercept_form_equation",
            "intercept_form_triangle_area", "intercept_form_equation_and_triangle_area",
            "intercept_form_from_intercept_sum_and_slope", "parabola_secant_parallel_line_choice",
            "triangle_area_bisector_line_equation", "slope_from_general_or_intercept_form",
            "slope_from_general_form", "slope_of_horizontal_or_vertical_line",
            "line_through_point_parallel_to_line", "line_through_point_perpendicular_to_line",
            "parallel_line_slope", "perpendicular_line_slope", "parallel_condition_parameter",
            "perpendicular_condition_parameter", "compare_line_slopes",
            "line_through_intersection_parallel_to_line", "line_through_point_perpendicular_to_segment",
            "perpendicular_bisector_application", "coordinate_geometry_word_problem"
        ]
    },
    "coordinate_geometry.point_line_distance": {
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_coordinate_geometry_matrix",
        "capabilities": {
            "distance_from_point_to_line", "compare_point_to_line_distances"
        },
        "allowed_operations": [
            "distance_from_point_to_line", "distance_from_point_to_line_parameter",
            "distance_from_point_to_line_parameter_single_choice_scalar", "compare_point_to_line_distances"
        ]
    },
    "coordinate_geometry.parallel_lines_distance": {
        "domain_module": "core.domain.coordinate_geometry.parallel_lines_distance_domain",
        "entrypoint": "build_parallel_lines_distance_matrix",
        "capabilities": {
            "distance_between_parallel_lines", "parallel_lines_distance", "solve_parameter_from_parallel_distance",
            "construct_parallel_line_at_distance", "parallel_lines_distance_single_choice", "area_using_parallel_distance"
        },
        "allowed_operations": [
            "distance_between_parallel_lines", "solve_parameter_from_parallel_distance",
            "construct_parallel_line_at_distance", "parallel_lines_distance_single_choice",
            "area_using_parallel_distance"
        ]
    },
    "statistics.frequency_distribution": {
        "domain_module": "core.domain.statistics.frequency_distribution_domain",
        "entrypoint": "build_frequency_distribution_table_matrix",
        "capabilities": {
            "frequency_table", "class_interval", "class_boundary", "class_midpoint", 
            "histogram", "frequency_polygon", "chart_consistency_validation", "frequency_distribution"
        },
        "allowed_operations": [
            "frequency_table_construction_review",
            "frequency_table_single_bin_count",
            "histogram_reading",
            "frequency_polygon_reading",
            "frequency_distribution_chart_construction",
            "histogram_distribution_update"
        ]
    },
    "statistics.table_chart": {
        "domain_module": "core.domain.statistics.table_chart_domain",
        "entrypoint": "build_statistical_chart_reading_matrix",
        "capabilities": {
            "statistical_chart_reading",
            "table_chart",
            "read_category_value",
            "compare_category_values",
            "calculate_total_ratio_percent",
            "validate_chart_statement",
            "cumulative_above_fail_count",
            "cumulative_above_interval_count",
            "cumulative_below_interval_count",
        },
        "allowed_operations": [
            "read_category_value",
            "compare_category_values",
            "calculate_total_ratio_percent",
            "validate_chart_statement",
            "cumulative_above_fail_count",
            "cumulative_above_interval_count",
            "cumulative_below_interval_count",
        ]
    }
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_thread_local = threading.local()


class ComponentOverrideContext:
    def __init__(self, extra: dict[str, Any] | None = None, component_id: str | None = None):
        self.extra = extra or {}
        self.component_id = component_id

    def __enter__(self):
        if not hasattr(_thread_local, "contexts"):
            _thread_local.contexts = []
        _thread_local.contexts.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _thread_local.contexts.pop()


def get_current_component_override_context():
    if hasattr(_thread_local, "contexts") and _thread_local.contexts:
        return _thread_local.contexts[-1]
    return None


class SkillFixedDomainError(ValueError):
    """Base error for skill-fixed domain authority violations."""

    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = str(code)
        self.details = dict(details or {})


@dataclass(frozen=True)
class FixedDomainContext:
    skill_id: str
    fixed_domain_key: str
    allowed_operations: tuple[str, ...]
    registry_revision: str
    domain_module: str
    entrypoint: str
    curriculum_profile: str


def _append_unique(target: list[str], value: str) -> None:
    value = str(value or "").strip()
    if value and value not in target:
        target.append(value)


def _text_capability_hints(text: str) -> set[str]:
    normalized = str(text or "").lower()
    caps: set[str] = set()
    if any(token in normalized for token in ("histogram", "frequency polygon", "frequency distribution")):
        caps.update({"frequency_table", "histogram", "frequency_polygon", "frequency_distribution"})
    if any(token in normalized for token in ("table", "chart", "bar chart", "line chart", "pie chart")) and any(
        token in normalized for token in ("read", "value", "compare", "difference", "total", "ratio", "percent", "percentage", "statement", "largest", "smallest")
    ):
        caps.update({"statistical_chart_reading", "table_chart"})
    if any(token in normalized for token in ("point to line", "distance from point", "distance to line")):
        caps.update({"distance_from_point_to_line", "compare_point_to_line_distances"})
    if any(token in normalized for token in ("parallel line distance", "distance between parallel", "parallel lines")):
        caps.update({"distance_between_parallel_lines", "parallel_lines_distance"})
    if any(token in normalized for token in ("line equation", "slope", "point-slope", "intercept", "horizontal line", "vertical line")):
        caps.update({"slope", "line_equation"})
    return caps


def resolve_dynamic_fixed_domain_context(
    skill_id: str,
    original_exc: Exception,
    *,
    textbook_example: dict[str, Any] | None = None,
    problem_type_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> FixedDomainContext:
    resolver_path = []
    fallback_attempts = []
    
    ctx = get_current_component_override_context()
    component_id = ctx.component_id if ctx else ""
    extra_data = dict(ctx.extra if ctx else {})
    if extra:
        extra_data.update(extra)
    
    explicit_key = extra_data.get("fixed_domain_key") or extra_data.get("domain_key")
    if explicit_key:
        resolver_path.append("component_override")
        fallback_attempts.append(f"try override key {explicit_key}")
        if explicit_key in DOMAIN_PROVIDERS:
            prov = DOMAIN_PROVIDERS[explicit_key]
            allowed_ops = tuple(extra_data.get("allowed_operations") or prov["allowed_operations"])
            return FixedDomainContext(
                skill_id=skill_id,
                fixed_domain_key=explicit_key,
                allowed_operations=allowed_ops,
                registry_revision="2026-06-23-v1.8",
                domain_module=str(extra_data.get("domain_module") or prov["domain_module"]),
                entrypoint=str(extra_data.get("entrypoint") or prov["entrypoint"]),
                curriculum_profile=str(extra_data.get("curriculum_profile") or "vocational_high_b"),
            )
        else:
            raise SkillFixedDomainError(
                DOMAIN_OVERRIDE_NOT_FOUND,
                f"component_override_domain_not_found: {explicit_key}",
                details={
                    "skill_id": skill_id,
                    "component_id": component_id,
                    "problem_type_id": extra_data.get("problem_type_id") or "",
                    "required_capabilities": list(extra_data.get("required_capabilities") or []),
                    "matched_capabilities": [],
                    "missing_capabilities": [explicit_key],
                    "resolver_path": resolver_path,
                    "fallback_attempts": fallback_attempts,
                }
            )

    examples = []
    if isinstance(textbook_example, dict) and textbook_example:
        resolver_path.append("component_textbook_example")
        examples = [dict(textbook_example)]
    else:
        try:
            db_path = PROJECT_ROOT / "instance/kumon_math.db"
            if db_path.is_file():
                with sqlite3.connect(str(db_path)) as db_conn:
                    db_conn.row_factory = sqlite3.Row
                    rows = db_conn.execute(
                        "SELECT id, problem_text, correct_answer, detailed_solution, explanation, problem_type FROM textbook_examples WHERE skill_id = ? ORDER BY id ASC",
                        (skill_id,),
                    ).fetchall()
                    examples = [dict(r) for r in rows]
                    if examples:
                        resolver_path.append("skill_examples_from_db")
        except Exception as e:
            fallback_attempts.append(f"db_load_failed: {e}")

    required_caps = set()
    domain_families = set()
    problem_types = set()

    for key in ("problem_type_id", "domain_operation", "selected_operation", "line_type", "task_type"):
        value = str(extra_data.get(key) or "").strip()
        if value:
            problem_types.add(value)
            fallback_attempts.append(f"component_metadata:{key}={value}")
    if problem_type_id:
        problem_types.add(str(problem_type_id).strip())
        fallback_attempts.append(f"problem_type_id={problem_type_id}")
    
    for ex in examples:
        text = (
            str(ex.get("problem_text") or "") + " " +
            str(ex.get("correct_answer") or "") + " " +
            str(ex.get("detailed_solution") or "") + " " +
            str(ex.get("explanation") or "")
        ).lower()
        
        pt = str(ex.get("problem_type") or "").strip()
        if pt:
            problem_types.add(pt)
        pt2 = str(ex.get("problem_type_id") or ex.get("domain_operation") or ex.get("line_type") or ex.get("task_type") or "").strip()
        if pt2:
            problem_types.add(pt2)

        hinted_caps = _text_capability_hints(text)
        if hinted_caps:
            _append_unique(resolver_path, "text_answer_capability_inference")
            required_caps.update(hinted_caps)
            
        if any(kw in text for kw in ["直方圖", "折線圖", "次數分配", "組距", "組中點", "次數", "histogram", "polygon", "frequency"]):
            domain_families.add("statistics_chart")
            required_caps.update([
                "frequency_table",
                "class_interval",
                "class_boundary",
                "class_midpoint",
                "histogram",
                "frequency_polygon",
                "chart_consistency_validation"
            ])
        elif any(kw in text for kw in ["平行線", "兩平行線", "平行線的距離", "平行線之距離", "parallel line"]):
            domain_families.add("coordinate_geometry")
            required_caps.update(["distance_between_parallel_lines", "parallel_lines_distance", "solve_parameter_from_parallel_distance"])
        elif any(kw in text for kw in ["點到直線", "距離", "point to line", "distance"]):
            domain_families.add("coordinate_geometry")
            required_caps.update(["distance_from_point_to_line", "compare_point_to_line_distances"])
        elif any(kw in text for kw in ["直線方程式", "斜率", "點斜式", "截距式", "一般式", "垂直平分線", "line equation", "slope"]):
            domain_families.add("coordinate_geometry")
            required_caps.update(["slope", "line_equation", "horizontal_line", "vertical_line", "point_slope", "intercept_form", "general_form", "two_points"])

    if not required_caps:
        fallback_attempts.append("narrow_skill_name_inference")
        skill_lower = skill_id.lower()
        if "histogram" in skill_lower or "polygon" in skill_lower or "frequency" in skill_lower:
            domain_families.add("statistics_chart")
            required_caps.update(["frequency_table", "histogram", "frequency_polygon"])
        elif "chartreading" in skill_lower or "chart_reading" in skill_lower or "tablechart" in skill_lower:
            domain_families.add("statistics_table_chart")
            required_caps.update(["statistical_chart_reading", "table_chart"])
        elif "parallel" in skill_lower and "distance" in skill_lower:
            domain_families.add("coordinate_geometry")
            required_caps.update(["distance_between_parallel_lines", "parallel_lines_distance"])
        elif "distance" in skill_lower:
            domain_families.add("coordinate_geometry")
            required_caps.update(["distance_from_point_to_line"])
        elif "slope" in skill_lower or "line" in skill_lower or "equation" in skill_lower:
            domain_families.add("coordinate_geometry")
            required_caps.update(["slope", "line_equation"])

    best_provider_key = None
    best_match_score = 0
    best_matched_caps = []
    
    for prov_key, prov_val in DOMAIN_PROVIDERS.items():
        prov_caps = prov_val["capabilities"]
        matched = [c for c in required_caps if c in prov_caps]
        score = len(matched)
        
        pt_match = len([pt for pt in problem_types if pt in prov_val["allowed_operations"]])
        if pt_match > 0:
            score += pt_match * 2
            _append_unique(resolver_path, "problem_type_operation_match")
            
        if score > best_match_score:
            best_match_score = score
            best_provider_key = prov_key
            best_matched_caps = matched

    if best_provider_key:
        _append_unique(resolver_path, "reusable_capability_matching")
        prov = DOMAIN_PROVIDERS[best_provider_key]
        return FixedDomainContext(
            skill_id=skill_id,
            fixed_domain_key=best_provider_key,
            allowed_operations=tuple(prov["allowed_operations"]),
            registry_revision="2026-06-23-v1.8",
            domain_module=prov["domain_module"],
            entrypoint=prov["entrypoint"],
            curriculum_profile="vocational_high_b"
        )

    raise SkillFixedDomainError(
        DOMAIN_CAPABILITY_UNRESOLVED,
        f"DOMAIN_CAPABILITY_UNRESOLVED: cannot resolve domain for skill {skill_id}",
        details={
            "skill_id": skill_id,
            "component_id": component_id,
            "problem_type_id": extra_data.get("problem_type_id") or "",
            "required_capabilities": list(required_caps),
            "matched_capabilities": list(best_matched_caps),
            "missing_capabilities": list(required_caps),
            "resolver_path": resolver_path,
            "fallback_attempts": fallback_attempts,
            "inference_trace": {
                "layers": [
                    "component_metadata",
                    "problem_type_id",
                    "taxonomy_registry",
                    "text_answer_capability_inference",
                    "narrow_domain_fallback",
                    "unsupported",
                ],
                "problem_types": sorted(problem_types),
                "domain_families": sorted(domain_families),
                "original_error": f"{original_exc.__class__.__name__}:{original_exc}",
            },
        }
    )


def resolve_fixed_domain_context(
    skill_id: str,
    *,
    textbook_example: dict[str, Any] | None = None,
    problem_type_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> FixedDomainContext:
    """Resolve authoritative fixed-domain context for a skill."""
    key = str(skill_id or "").strip()
    
    # 1. Component-level explicit override takes highest precedence
    ctx = get_current_component_override_context()
    extra_data = dict(ctx.extra if ctx else {})
    if extra:
        extra_data.update(extra)
    explicit_key = extra_data.get("fixed_domain_key") or extra_data.get("domain_key")
    if explicit_key:
        return resolve_dynamic_fixed_domain_context(
            key,
            original_exc=ValueError("component_override_active"),
            textbook_example=textbook_example,
            problem_type_id=problem_type_id,
            extra=extra,
        )

    metadata_operation = str(
        extra_data.get("domain_operation")
        or extra_data.get("selected_operation")
        or extra_data.get("problem_type_id")
        or extra_data.get("line_type")
        or extra_data.get("task_type")
        or problem_type_id
        or ""
    ).strip()
    if metadata_operation:
        metadata_matches_known_operation = any(
            metadata_operation in tuple(provider.get("allowed_operations") or ())
            for provider in DOMAIN_PROVIDERS.values()
        )
        if metadata_matches_known_operation:
            try:
                return resolve_dynamic_fixed_domain_context(
                    key,
                    original_exc=ValueError("component_metadata_active"),
                    textbook_example=textbook_example,
                    problem_type_id=problem_type_id,
                    extra=extra,
                )
            except SkillFixedDomainError:
                pass

    # 2. Skill-level explicit override
    try:
        routing = resolve_domain_for_skill(key)
        fixed_domain_key = get_fixed_domain_key(key)
        allowed = tuple(get_allowed_operations(fixed_domain_key, skill_id=key))
        if not allowed:
            raise SkillFixedDomainError(
                UNSUPPORTED_DOMAIN_OPERATION,
                f"no_allowed_operations_for_domain: {fixed_domain_key!r}",
                details={"skill_id": key, "fixed_domain_key": fixed_domain_key},
            )

        return FixedDomainContext(
            skill_id=key,
            fixed_domain_key=fixed_domain_key,
            allowed_operations=allowed,
            registry_revision=get_registry_revision(key),
            domain_module=str(routing.get("domain_module") or ""),
            entrypoint=str(routing.get("entrypoint") or ""),
            curriculum_profile=str(
                routing.get("default_curriculum_profile")
                or routing.get("curriculum_profile")
                or "vocational_high_b"
            ),
        )
    except Exception as exc:
        return resolve_dynamic_fixed_domain_context(
            key,
            original_exc=exc,
            textbook_example=textbook_example,
            problem_type_id=problem_type_id,
            extra=extra,
        )



def strip_ai_routing_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove AI-suggested routing fields that must not influence dispatch."""
    cleaned = dict(payload or {})
    for field in AI_IGNORED_ROUTING_FIELDS:
        cleaned.pop(field, None)
    return cleaned


def assert_operation_allowed(
    *,
    skill_id: str,
    fixed_domain_key: str,
    selected_operation: str,
    allowed_operations: list[str] | tuple[str, ...] | None = None,
) -> str:
    """Hard gate: selected_operation must be in allowed_operations whitelist."""
    op = str(selected_operation or "").strip()
    if not op:
        raise SkillFixedDomainError(
            DOMAIN_OPERATION_NOT_ALLOWED,
            "domain_operation_not_allowed: empty operation",
            details={
                "skill_id": skill_id,
                "fixed_domain_key": fixed_domain_key,
                "selected_operation": op,
            },
        )

    whitelist = tuple(allowed_operations or get_allowed_operations(fixed_domain_key, skill_id=skill_id))
    if op not in whitelist:
        raise SkillFixedDomainError(
            DOMAIN_OPERATION_NOT_ALLOWED,
            f"domain_operation_not_allowed: {op!r} not in {list(whitelist)!r}",
            details={
                "skill_id": skill_id,
                "fixed_domain_key": fixed_domain_key,
                "selected_operation": op,
                "allowed_operations": list(whitelist),
            },
        )
    return op


def assert_template_dispatch(
    *,
    skill_id: str,
    fixed_domain_key: str,
    template_domain_key: str,
    template_operation_key: str,
    allowed_operations: list[str] | tuple[str, ...] | None = None,
) -> None:
    """Validate template slot domain/operation before dispatch."""
    if str(template_domain_key or "").strip() != str(fixed_domain_key or "").strip():
        raise SkillFixedDomainError(
            FIXED_DOMAIN_VIOLATION,
            f"fixed_domain_violation: template domain {template_domain_key!r} != {fixed_domain_key!r}",
            details={
                "skill_id": skill_id,
                "fixed_domain_key": fixed_domain_key,
                "template_domain_key": template_domain_key,
                "template_operation_key": template_operation_key,
            },
        )
    assert_operation_allowed(
        skill_id=skill_id,
        fixed_domain_key=fixed_domain_key,
        selected_operation=template_operation_key,
        allowed_operations=allowed_operations,
    )


def build_classifier_taxonomy_entry(ctx: FixedDomainContext) -> dict[str, Any]:
    """Taxonomy entry passed to semantic classifier — AI cannot override domain."""
    return {
        "skill_id": ctx.skill_id,
        "fixed_domain_key": ctx.fixed_domain_key,
        "allowed_operations": list(ctx.allowed_operations),
        "allowed_types": list(ctx.allowed_operations),
        "registry_revision": ctx.registry_revision,
    }


def normalize_ai_classification(
    classification: dict[str, Any],
    ctx: FixedDomainContext,
) -> dict[str, Any]:
    """Normalize AI/deterministic classification output under fixed domain authority."""
    cleaned = strip_ai_routing_fields(classification)
    selected = str(
        cleaned.get("selected_operation")
        or cleaned.get("domain_operation")
        or cleaned.get("problem_type_id")
        or ""
    ).strip()
    if selected:
        assert_operation_allowed(
            skill_id=ctx.skill_id,
            fixed_domain_key=ctx.fixed_domain_key,
            selected_operation=selected,
            allowed_operations=ctx.allowed_operations,
        )
    normalized = {
        **cleaned,
        "skill_id": ctx.skill_id,
        "fixed_domain_key": ctx.fixed_domain_key,
        "registry_revision": ctx.registry_revision,
        "selected_operation": selected or cleaned.get("selected_operation"),
        "domain_operation": selected or cleaned.get("domain_operation"),
    }
    if selected and not normalized.get("problem_type_id"):
        normalized["problem_type_id"] = selected
    return normalized


def log_dispatch_event(
    *,
    phase: str,
    skill_id: str,
    component_id: str = "",
    example_id: int | None = None,
    fixed_domain_key: str = "",
    selected_operation: str = "",
    problem_type_id: str = "",
    template_slot: str = "",
    template_domain_key: str = "",
    seed: int | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Structured dispatch log — required fields for audit trail."""
    record = {
        "phase": str(phase or "").strip(),
        "skill_id": str(skill_id or "").strip(),
        "component_id": str(component_id or "").strip(),
        "example_id": example_id,
        "fixed_domain_key": str(fixed_domain_key or "").strip(),
        "selected_operation": str(selected_operation or "").strip(),
        "problem_type_id": str(problem_type_id or "").strip(),
        "template_slot": str(template_slot or "").strip(),
        "template_domain_key": str(template_domain_key or "").strip(),
        "seed": seed,
    }
    if extra:
        record.update(extra)
    logger.info("[GENCODE_DISPATCH] %s", json.dumps(record, ensure_ascii=False, default=str))


def validate_publish_component_record(
    *,
    skill_id: str,
    component_skill_id: str,
    component_fixed_domain_key: str,
    component_operation: str,
    component_status: str,
    registry_skill_id: str | None = None,
) -> list[str]:
    """Return publish blockers for a single component; empty means eligible."""
    blockers: list[str] = []
    skill_key = str(skill_id or "").strip()
    if str(component_skill_id or "").strip() != skill_key:
        blockers.append("publish_skill_id_mismatch")
    try:
        ctx = resolve_fixed_domain_context(skill_key)
    except SkillFixedDomainError as exc:
        blockers.append(exc.code)
        return blockers

    if str(component_fixed_domain_key or "").strip():
        if str(component_fixed_domain_key or "").strip() != ctx.fixed_domain_key:
            blockers.append(FIXED_DOMAIN_VIOLATION)

    op = str(component_operation or "").strip()
    if op and op not in ctx.allowed_operations:
        blockers.append(DOMAIN_OPERATION_NOT_ALLOWED)

    status = str(component_status or "").strip()
    if status in {
        UNSUPPORTED_DOMAIN_OPERATION,
        FIXED_DOMAIN_VIOLATION,
        DOMAIN_OPERATION_NOT_ALLOWED,
        "needs_human_review",
    }:
        blockers.append(f"non_publishable_status:{status}")
    if status != "verified":
        blockers.append("component_not_verified")

    return blockers


