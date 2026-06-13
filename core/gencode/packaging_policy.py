from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

PACKAGING_READY_STATUSES = frozenset(
    {
        "runtime_ready",
        "limited_runtime_ready",
        "runtime_ready_with_warning",
        "ready",
        "passed",
    }
)

DIVERSITY_SAMPLING_OK_STATUSES = frozenset(
    {
        "passed",
        "runtime_ready_with_diversity_warning",
    }
)

# ── Phase 3 contract integrity ────────────────────────────────────────────────

_FILL_BLANK_SLOTS = frozenset(
    {
        "quadratic_graph_translation_fill_blank",
        "quadratic_graph_translation_short_answer",
        "linear_triangle_median_compute",
        "function_value_numeric",
        "symbolic_quadrant",
        "point_quadrant",
    }
)

_CHOICE_SLOTS = frozenset(
    {
        "quadratic_graph_vertex_axis_choice",
        "quadratic_vertex_form_properties",
        "quadratic_standard_to_vertex_properties",
        "point_quadrant_choice",
        "axis_distance_choice",
        "symbolic_quadrant_statement_choice",
        "linear_function_two_point_choice",
    }
)

_NUMERIC_CHECKERS = frozenset(
    {"integer_checker", "rational_checker", "numeric_checker", "fraction_checker"}
)


def validate_phase3_generator_spec_integrity(row: dict[str, Any]) -> list[str]:
    """Return blocker tokens when a GENERATOR_SPECS row has contract/slot mismatch.

    Called before writing the draft wrapper to prevent smoke-time surprises.
    """
    if not isinstance(row, dict):
        return ["invalid_generator_spec_row"]
    blockers: list[str] = []
    pt = str(row.get("problem_type_id", "")).strip()
    checker = str(row.get("checker_key") or row.get("checker") or "").strip()
    eq = str(row.get("equivalence_type") or row.get("answer_equivalence") or "").strip()
    answer_type = str(row.get("answer_type", "")).strip()
    answer_shape = str(row.get("answer_shape", "")).strip()
    slot = str(row.get("template_slot", "")).strip()
    readiness = str(row.get("generator_readiness", "")).strip()

    # 1. generator_not_ready must never enter wrapper
    if readiness == "generator_not_ready":
        blockers.append("phase3_generator_not_ready_in_wrapper")

    # 2. fill_blank slot + numeric checker → mismatch
    if slot in _FILL_BLANK_SLOTS and checker in _NUMERIC_CHECKERS:
        blockers.append("phase3_contract_slot_mismatch:fill_blank_slot_numeric_checker")

    # 3. choice slot + non-choice checker → mismatch
    if slot in _CHOICE_SLOTS and checker not in {"choice_label_checker", ""}:
        blockers.append("phase3_contract_slot_mismatch:choice_slot_non_choice_checker")

    # 4. answer_shape=text_short + answer_type integer/rational/numeric → shape/type mismatch
    if answer_shape in {"text_short", "short_answer"} and answer_type in {"integer", "numeric", "rational"}:
        blockers.append("phase3_answer_shape_type_mismatch")

    # 5. usable_for_phase3=true but no canonical fields (only for typed-prefix pt_ids)
    from core.gencode.problem_type_canonicalizer import _strip_typed_prefix
    _, base_pt = _strip_typed_prefix(pt)
    if base_pt != pt:  # has a typed prefix
        has_canonical = bool(row.get("base_problem_type_id") or row.get("canonical_base_problem_type_id"))
        if not has_canonical:
            blockers.append("phase3_canonicalized_spec_missing")

    return blockers

_STATUS_KEYS = ("generator_status", "status", "readiness_status")
_SMOKE_KEYS = (("checker_smoke_status", "checker_smoke"), ("dynamic_sampling_status", "dynamic_sampling"))


def generator_status_value(record: dict[str, Any]) -> str:
    if not isinstance(record, dict):
        return ""
    for key in _STATUS_KEYS:
        val = str(record.get(key, "")).strip()
        if val:
            return val
    return ""


def _passed_flag(record: dict[str, Any], primary: str, alt: str) -> bool:
    raw = record.get(primary)
    if raw is None:
        raw = record.get(alt)
    if isinstance(raw, bool):
        return raw
    val = str(raw or "").strip().lower()
    if val == "passed":
        return True
    if primary == "dynamic_sampling_status" and val in DIVERSITY_SAMPLING_OK_STATUSES:
        return True
    return False


def resolve_phase2_generator_status(
    *,
    blockers: list[str],
    warnings: list[str],
    checker_smoke_status: str = "passed",
    dynamic_sampling_status: str = "passed",
    base_status: str = "",
) -> tuple[str, bool]:
    """
    Map Phase 2 smoke/diversity outcome to generator_status and Phase 3 usability.
    Only non-empty blockers cause validation_failed; warnings yield runtime_ready_with_warning.
    """
    merged_blockers = sorted({str(b).strip() for b in blockers if str(b).strip()})
    merged_warnings = sorted({str(w).strip() for w in warnings if str(w).strip()})
    smoke = str(checker_smoke_status or "").strip().lower()
    dynamic = str(dynamic_sampling_status or "").strip().lower()

    if merged_blockers:
        return "validation_failed", False
    if smoke not in {"", "passed", "skipped_with_blockers"}:
        return "validation_failed", False
    if dynamic not in {"", "passed", "skipped_with_blockers"} and dynamic not in DIVERSITY_SAMPLING_OK_STATUSES:
        if dynamic in {"failed", "generator_diversity_blocked"}:
            return "validation_failed", False
    if merged_warnings:
        return "runtime_ready_with_warning", True
    normalized = str(base_status or "").strip()
    if normalized in PACKAGING_READY_STATUSES:
        return normalized, True
    if normalized in {"draft_planned", ""}:
        return "runtime_ready", True
    return normalized or "runtime_ready", normalized in PACKAGING_READY_STATUSES


def is_generator_usable_for_packaging(record: dict[str, Any]) -> tuple[bool, list[str]]:
    """Generic packaging gate aligned with Phase 2 runtime_ready semantics."""
    if not isinstance(record, dict):
        return False, ["invalid_record"]
    exclude: list[str] = []
    status = generator_status_value(record)
    if status not in PACKAGING_READY_STATUSES:
        exclude.append(f"status_not_packaging_ready:{status or 'missing'}")
    for primary, alt in _SMOKE_KEYS:
        if not _passed_flag(record, primary, alt):
            exclude.append(f"{primary}_not_passed")
    blockers = [str(b).strip() for b in (record.get("blockers") or []) if str(b).strip()]
    if blockers:
        exclude.append("blockers:" + ",".join(blockers))
    cap = str(record.get("checker_capability_status", "")).strip().lower()
    if cap in {"blocked", "unsupported", "missing"}:
        exclude.append(f"checker_capability_{cap or 'missing'}")
    if bool(record.get("requires_human_action")):
        exclude.append("requires_human_action")
    # warnings alone (e.g. low_source_examples) do not block packaging
    if record.get("usable_for_phase3") is False:
        exclude.append("usable_for_phase3_false")
    return len(exclude) == 0, exclude


def merge_generator_records(
    phase2_summary: dict[str, Any] | None,
    draft_spec: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Merge phase2 summary rows with generator_draft_spec by problem_type_id / generator_key."""
    merged: dict[str, dict[str, Any]] = {}

    def _merge_row(row: dict[str, Any], source: str) -> None:
        if not isinstance(row, dict):
            return
        pt = str(row.get("problem_type_id", "")).strip()
        gk = str(row.get("generator_key", "")).strip()
        key = gk or pt
        if not key:
            return
        base = dict(merged.get(key, {}))
        base.update(row)
        base["_merge_sources"] = sorted(set(list(base.get("_merge_sources", [])) + [source]))
        if pt:
            base["problem_type_id"] = pt
        if gk:
            base["generator_key"] = gk
        if not base.get("generator_status") and base.get("status"):
            base["generator_status"] = base["status"]
        if not base.get("status") and base.get("generator_status"):
            base["status"] = base["generator_status"]
        merged[key] = base

    for row in (draft_spec or {}).get("generator_results", []) or []:
        _merge_row(row, "generator_draft_spec")
    for row in (phase2_summary or {}).get("generator_results", []) or []:
        _merge_row(row, "phase2_summary")

    return list(merged.values())


def select_generators_for_packaging(
    phase2_summary: dict[str, Any] | None,
    draft_spec: dict[str, Any] | None,
    *,
    accepted_generator_keys: set[str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records = merge_generator_records(phase2_summary, draft_spec)
    if accepted_generator_keys:
        records = [r for r in records if str(r.get("generator_key", "")).strip() in accepted_generator_keys]
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for row in records:
        usable, reasons = is_generator_usable_for_packaging(row)
        pt = str(row.get("problem_type_id", "")).strip()
        entry = {
            "problem_type_id": pt,
            "generator_key": str(row.get("generator_key", "")).strip(),
            "generator_status": generator_status_value(row),
            "checker_smoke_status": row.get("checker_smoke_status", row.get("checker_smoke")),
            "dynamic_sampling_status": row.get("dynamic_sampling_status", row.get("dynamic_sampling")),
            "blockers": list(row.get("blockers") or []),
            "warnings": list(row.get("warnings") or []),
            "reasons": reasons,
        }
        if usable:
            included.append(row)
            logger.info("[PHASE3 PACKAGING] included problem_type=%s status=%s", pt, entry["generator_status"])
        else:
            excluded.append(entry)
            logger.info(
                "[PHASE3 PACKAGING] excluded problem_type=%s reason=%s",
                pt,
                ";".join(reasons) or "unknown",
            )
    diagnostics = {
        "candidate_count": len(records),
        "included_count": len(included),
        "excluded_count": len(excluded),
        "included": [
            {
                "problem_type_id": str(r.get("problem_type_id", "")),
                "generator_key": str(r.get("generator_key", "")),
                "generator_status": generator_status_value(r),
            }
            for r in included
        ],
        "excluded": excluded,
        "phase2_summary_exists": bool(phase2_summary),
        "generator_draft_spec_exists": bool(draft_spec),
    }
    return included, diagnostics


def format_packaging_blocked_message(diagnostics: dict[str, Any]) -> str:
    lines = [
        f"Phase 3 blocked: no usable generators for packaging "
        f"(candidates={diagnostics.get('candidate_count', 0)}, "
        f"included={diagnostics.get('included_count', 0)})."
    ]
    for ex in diagnostics.get("excluded", []) or []:
        if not isinstance(ex, dict):
            continue
        lines.append(
            f"  - {ex.get('problem_type_id', '?')}: "
            f"{';'.join(ex.get('reasons', []) or ['unknown'])}"
        )
    return "\n".join(lines)
