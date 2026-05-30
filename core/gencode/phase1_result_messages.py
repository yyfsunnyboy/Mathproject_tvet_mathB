# -*- coding: utf-8 -*-
"""Phase 1 API/UI message mapping for alignment blockers (display only)."""

from __future__ import annotations

from typing import Any

MSG_MAJORITY_NEEDS_REVIEW = (
    "來源題型與技能名稱/語意不一致，請檢查來源例題或 skill mapping。"
)
MSG_LOW_CORE_SOURCE_EXAMPLES = (
    "核心短題來源不足。目前此技能的來源多為素養題、閱讀長題或 enrichment 題，"
    "無法進入一般 runtime generator Phase 2。請補充核心短題，或改走 static_textbook / ai_judged_static 路徑。"
)
MSG_SOURCE_QUALITY_REJECT = "來源題品質不可用，需人工修題。"
MSG_SEMANTIC_POLLUTION_REJECT = "來源題疑似跨主題污染或錯分 skill。"
MSG_SAME_FAMILY_EXTENSION = "同一題族內的延伸題型，保留於目前 skill。"
MSG_SAME_AS_MAIN_SKILL = "無法穩定細分子技能，已放入主技能同名子技能。"
MSG_LOW_SOURCE_EXAMPLES = "樣本數不足，題型先列為候選。"

SEMANTIC_MISMATCH_BLOCKERS = frozenset(
    {
        "majority_needs_review",
        "mixed_source_families",
        "source_examples_mismatch",
        "skill_id_mismatch",
        "low_alignment_score",
        "skill_problem_type_semantic_mismatch",
        "expected_family_mismatch",
    }
)

_LOW_CORE_ALLOWED_EXTRA = frozenset({"semantic_alignment_blocked"})


def blockers_include_semantic_mismatch(blockers: list[Any]) -> bool:
    return bool({str(b).strip() for b in blockers if str(b).strip()} & SEMANTIC_MISMATCH_BLOCKERS)


def is_only_low_core_blockers(blockers: list[Any]) -> bool:
    bs = {str(b).strip() for b in blockers if str(b).strip()}
    if not bs or "low_core_source_examples" not in bs:
        return False
    return bs <= ({"low_core_source_examples"} | _LOW_CORE_ALLOWED_EXTRA)


def enrichment_example_ids(payload: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for row in payload.get("skipped_enrichment_examples") or []:
        if isinstance(row, dict) and row.get("example_id") is not None:
            ids.append(str(row["example_id"]))
    if ids:
        return ids
    for row in payload.get("source_example_alignment") or []:
        if not isinstance(row, dict) or row.get("example_id") is None:
            continue
        kind = str(row.get("alignment_kind", "")).strip()
        tier = str(row.get("induction_tier", "")).strip()
        if kind == "enrichment_source" or tier == "enrichment":
            ids.append(str(row["example_id"]))
    return ids


def true_low_alignment_core_example_ids(payload: dict[str, Any]) -> list[str]:
    """Core-tier examples with semantic misalignment (not enrichment skips)."""
    enrichment = set(enrichment_example_ids(payload))
    low: list[str] = []
    for row in payload.get("source_example_alignment") or []:
        if not isinstance(row, dict):
            continue
        eid = str(row.get("example_id", "")).strip()
        if not eid or eid in enrichment:
            continue
        if str(row.get("induction_tier", "")).strip() == "enrichment":
            continue
        if str(row.get("alignment_kind", "")).strip() == "enrichment_source":
            continue
        if row.get("aligned_with_skill", True):
            continue
        if str(row.get("exclude_reason", "")).strip() == "enrichment_not_core_induction":
            continue
        low.append(eid)
    return low


def phase1_induction_summary(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "core_example_count": int(payload.get("core_example_count", 0) or 0),
        "enrichment_example_count": int(payload.get("enrichment_example_count", 0) or 0),
        "skipped_enrichment_examples": list(payload.get("skipped_enrichment_examples") or []),
        "future_ai_judged_candidates": list(payload.get("future_ai_judged_candidates") or []),
        "contextual_application_sources": list(payload.get("contextual_application_sources") or []),
        "rejected_source_examples": list(payload.get("rejected_source_examples") or []),
        "source_quality_issues": list(payload.get("source_quality_issues") or []),
        "semantic_mismatch_examples": list(payload.get("semantic_mismatch_examples") or []),
        "suspected_wrong_skill_examples": list(payload.get("suspected_wrong_skill_examples") or []),
        "same_family_extension_examples": list(payload.get("same_family_extension_examples") or []),
        "section_scope_subskill_extension_examples": list(payload.get("section_scope_subskill_extension_examples") or []),
        "same_as_main_skill_examples": list(payload.get("same_as_main_skill_examples") or []),
        "inherited_from_previous_context_examples": list(payload.get("inherited_from_previous_context_examples") or []),
        "low_source_examples": list(payload.get("low_source_examples") or []),
        "candidate_only_problem_types": list(payload.get("candidate_only_problem_types") or []),
        "subskills": list(payload.get("subskills") or []),
        "fallback_subskill_used": bool(payload.get("fallback_subskill_used", False)),
        "source_belongs_to_current_skill_by_default_count": int(payload.get("source_belongs_to_current_skill_by_default_count", 0) or 0),
        "blockers": list(payload.get("alignment_blockers") or []),
    }


def apply_phase1_display_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Attach user-facing Phase 1 labels/messages without changing induction policy."""
    blockers = list(payload.get("alignment_blockers") or [])
    only_low_core = is_only_low_core_blockers(blockers)
    semantic = blockers_include_semantic_mismatch(blockers)

    enrich_ids = enrichment_example_ids(payload)
    low_core_ids = true_low_alignment_core_example_ids(payload)

    source_quality_reject = bool(payload.get("rejected_source_examples"))
    same_family_extension = bool(payload.get("same_family_extension_examples") or payload.get("section_scope_subskill_extension_examples"))
    same_as_main = bool(payload.get("same_as_main_skill_examples"))
    low_source = bool(payload.get("low_source_examples"))

    if source_quality_reject:
        severity = "blocked"
        display_kind = "source_quality_reject"
        status_label = "需人工修題"
        user_message = MSG_SOURCE_QUALITY_REJECT
        example_ids_note = ""
    elif only_low_core:
        severity = "warning"
        display_kind = "low_core_sources"
        status_label = "需補核心短題"
        user_message = MSG_LOW_CORE_SOURCE_EXAMPLES
        example_ids_note = ""
        if enrich_ids:
            example_ids_note = (
                "已排除於 core induction 的 enrichment example_id: " + ", ".join(enrich_ids[:12])
            )
    elif semantic:
        severity = "semantic_error"
        display_kind = "semantic_mismatch"
        status_label = "語意對齊未通過"
        user_message = MSG_SEMANTIC_POLLUTION_REJECT if payload.get("suspected_wrong_skill_examples") else MSG_MAJORITY_NEEDS_REVIEW
        example_ids_note = ""
        if low_core_ids:
            example_ids_note = "低對齊 example_id: " + ", ".join(low_core_ids[:12])
        elif enrich_ids and not low_core_ids:
            example_ids_note = "素養／長題來源 example_id: " + ", ".join(enrich_ids[:12])
    elif same_family_extension:
        severity = "warning"
        display_kind = "same_family_extension"
        status_label = "同 family 延伸"
        user_message = MSG_SAME_FAMILY_EXTENSION
        example_ids_note = ""
    elif same_as_main:
        severity = "warning"
        display_kind = "same_as_main_skill"
        status_label = "使用 fallback 子技能"
        user_message = MSG_SAME_AS_MAIN_SKILL
        example_ids_note = ""
    elif low_source:
        severity = "warning"
        display_kind = "low_source_examples"
        status_label = "樣本不足"
        user_message = MSG_LOW_SOURCE_EXAMPLES
        example_ids_note = ""
    elif blockers:
        severity = "blocked"
        display_kind = "blocked"
        status_label = "暫停"
        user_message = f"Phase 1 對齊暫停。 blockers={blockers}"
        example_ids_note = ""
        if low_core_ids:
            example_ids_note = "低對齊 example_id: " + ", ".join(low_core_ids[:12])
    else:
        severity = "success"
        display_kind = "pass"
        status_label = ""
        user_message = ""
        example_ids_note = ""

    payload["alignment_severity"] = severity
    payload["alignment_display_kind"] = display_kind
    payload["alignment_status_label"] = status_label
    payload["alignment_user_message"] = user_message
    payload["example_ids_note"] = example_ids_note
    payload["phase1_induction_summary"] = phase1_induction_summary(payload)
    if only_low_core:
        payload["phase_status"] = "phase1_blocked_low_core_sources"
        payload["summary_message"] = f"{user_message} blockers={blockers}"
        if example_ids_note:
            payload["summary_message"] += f" {example_ids_note}"
    elif str(payload.get("phase_status", "")).strip() == "phase1_blocked_semantic_alignment":
        payload["summary_message"] = f"{user_message} blockers={blockers}"
        if example_ids_note:
            payload["summary_message"] += f" {example_ids_note}"
    return payload


def resolve_phase1_phase_status(
    *,
    source_count: int,
    source_alignment_status: str,
    alignment_blockers: list[Any],
    ex_gate_required: bool,
    has_fatal: bool,
    has_risk_examples: bool,
) -> str:
    if source_count <= 0:
        return "phase1_blocked_no_source"
    if str(source_alignment_status).strip() == "block" or alignment_blockers:
        if is_only_low_core_blockers(alignment_blockers):
            return "phase1_blocked_low_core_sources"
        return "phase1_blocked_semantic_alignment"
    if has_fatal:
        return "phase1_blocked_fatal_risk"
    if ex_gate_required:
        return "phase1_exception_review_required"
    if has_risk_examples:
        return "phase1_completed_with_warning"
    return "phase1_completed"

