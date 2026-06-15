from __future__ import annotations

from typing import Any


GENERIC_FALLBACK_TASKS = frozenset(
    {
        "compute_numeric",
        "generic_numeric",
        "generic_numeric_family",
        "contextual_application",
        "fallback_contextual_application",
    }
)

GENERIC_FALLBACK_FAMILIES = frozenset(
    {
        "generic_numeric",
        "generic_numeric_family",
        "contextual_application",
        "fallback_contextual_application",
    }
)

GENERIC_FALLBACK_PT_TOKENS = frozenset(
    {
        "compute_numeric",
        "generic_numeric",
        "generic_numeric_family",
        "contextual_application",
        "fallback_contextual_application",
    }
)


def source_skill_scope_locked(anchor: dict[str, Any] | None) -> bool:
    return bool((anchor or {}).get("source_skill_scope_locked", False))


def source_binding_scope_active(meta: dict[str, Any] | None) -> bool:
    row = meta if isinstance(meta, dict) else {}
    return bool(row.get("source_skill_scope_locked")) or str(
        row.get("classification_scope", "")
    ).strip() == "within_current_skill"


def should_block_generic_fallback_for_scope(
    meta: dict[str, Any] | None,
    *,
    problem_type_id: str = "",
    target_task: str = "",
    task_family: str = "",
) -> bool:
    if not source_binding_scope_active(meta):
        return False
    return is_generic_fallback_problem_type(
        problem_type_id=problem_type_id,
        target_task=target_task,
        task_family=task_family,
    )


def source_binding_metadata(skill_id: str) -> dict[str, Any]:
    return {
        "source_skill_scope_locked": True,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": str(skill_id or "").strip(),
    }


def is_generic_fallback_problem_type(
    *,
    problem_type_id: str = "",
    target_task: str = "",
    task_family: str = "",
) -> bool:
    task = str(target_task or "").strip()
    family = str(task_family or "").strip()
    pt = str(problem_type_id or "").strip()
    if task in GENERIC_FALLBACK_TASKS or family in GENERIC_FALLBACK_FAMILIES:
        return True
    return any(token in pt for token in GENERIC_FALLBACK_PT_TOKENS)


def mark_unresolved_within_current_skill(
    feature: dict[str, Any],
    *,
    reason: str = "unresolved_within_current_skill",
) -> dict[str, Any]:
    feature["source_skill_scope_locked"] = True
    feature["skill_mapping_authority"] = "textbook_examples.skill_id"
    feature["classification_scope"] = "within_current_skill"
    feature["unresolved_within_current_skill"] = True
    feature["pending_problem_type_induction"] = True
    feature["requires_human_rule_pack"] = True
    feature["requires_human_action"] = True
    feature["unresolved_reason"] = reason
    feature["generator_readiness"] = "pending_problem_type_induction"
    feature["usable_for_phase3"] = False
    return feature


_GENERIC_FALLBACK_BLOCKER = "generic_fallback_blocked_by_source_skill_binding"


def demote_generic_fallback_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    row = dict(candidate)
    row["generator_readiness"] = "pending_problem_type_induction"
    row["usable_for_phase3"] = False
    row["requires_human_action"] = True
    row["requires_human_rule_pack"] = True
    row["pending_problem_type_induction"] = True
    row["promote_recommendation"] = "hold_pending_problem_type_induction"
    blockers = list(row.get("promote_blockers", []) or [])
    blockers.append(_GENERIC_FALLBACK_BLOCKER)
    row["promote_blockers"] = sorted(set(str(x) for x in blockers if str(x).strip()))
    risk_flags = list(row.get("risk_flags", []) or [])
    risk_flags.append(_GENERIC_FALLBACK_BLOCKER)
    row["risk_flags"] = sorted(set(str(x) for x in risk_flags if str(x).strip()))
    return row


def demote_unregistered_scope_locked_candidate(
    candidate: dict[str, Any],
    *,
    reason: str = "unregistered_current_skill_problem_type",
) -> dict[str, Any]:
    row = dict(candidate)
    original_pt = str(row.get("problem_type_id") or row.get("proposed_problem_type_id") or "").strip()
    original_target = str(row.get("target_task") or row.get("subskill_id") or "").strip()
    if original_pt:
        row["detected_weak_problem_type_id"] = original_pt
    if original_target:
        row["detected_weak_target_task"] = original_target
    row["problem_type_id"] = "unresolved_within_current_skill"
    row["proposed_problem_type_id"] = "unresolved_within_current_skill"
    row["generator_readiness"] = "pending_problem_type_induction"
    row["usable_for_phase3"] = False
    row["requires_human_action"] = True
    row["requires_human_rule_pack"] = True
    row["pending_problem_type_induction"] = True
    row["unresolved_reason"] = reason
    row["promote_recommendation"] = "hold_pending_problem_type_induction"
    blockers = list(row.get("promote_blockers", []) or [])
    blockers.append(reason)
    row["promote_blockers"] = sorted(set(str(x) for x in blockers if str(x).strip()))
    risk_flags = list(row.get("risk_flags", []) or [])
    risk_flags.append(reason)
    row["risk_flags"] = sorted(set(str(x) for x in risk_flags if str(x).strip()))
    return row
