"""
B4 Chapter 1 deterministic adaptive allowlist (Phase 4F Preflight).

Source of truth:
- Phase 4E-Final runtime_ready skill coverage intent (deterministic int-answer practice path).
- Post-enrichment skills explicitly wired with wrappers + router (e.g. PermutationOfNonDistinctObjects).

This module MUST NOT import or rewrite `b4_ch1_runtime_coverage_matrix.csv`.
"""

from __future__ import annotations

from typing import TypeVar

B4_SKILL_PREFIX = "vh_數學B4_"

TEntry = TypeVar("TEntry")

# Phase 4E-Final Chapter 1 deterministic `runtime_ready` skills (skill_id),
# plus Postcheck-D2 deterministic enrichment skill NOT counted in original 28-row matrix.
B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST: frozenset[str] = frozenset(
    {
        "vh_數學B4_AdditionPrinciple",
        "vh_數學B4_MultiplicationPrinciple",
        "vh_數學B4_FactorialNotation",
        "vh_數學B4_PermutationOfDistinctObjects",
        "vh_數學B4_RepeatedPermutation",
        "vh_數學B4_PermutationWithRepetition",
        "vh_數學B4_PermutationOfNonDistinctObjects",
        "vh_數學B4_CombinationDefinition",
        "vh_數學B4_CombinationApplications",
        "vh_數學B4_CombinationProperties",
        "vh_數學B4_Combination",
        "vh_數學B4_BinomialCoefficientIdentities",
        "vh_數學B4_BinomialTheorem",
    }
)

# Skill pages gated friendly-unavailable / manual_review / future_ai_judged for deterministic runtime.
B4_MANUAL_REVIEW_OR_UNAVAILABLE_SKILL_IDS: frozenset[str] = frozenset(
    {
        "vh_數學B4_TreeDiagramCounting",
        "vh_數學B4_PascalTriangle",
    }
)

# Problem types that must never surface in deterministic adaptive, even if metadata regresses.
B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES: frozenset[str] = frozenset(
    {
        "binomial_expansion_basic",
        "tree_diagram_listing",
        "pascal_triangle_derivation",
    }
)


def is_b4_vocational_skill_id(skill_id: str) -> bool:
    return isinstance(skill_id, str) and skill_id.startswith(B4_SKILL_PREFIX)


def filter_skill_pool_for_b4_chapter1_deterministic_adaptive(
    skill_ids: list[str],
) -> tuple[list[str], list[dict[str, str]]]:
    """
    Filter an adaptive candidate skill pool.

    - Non-B4 ids pass through unchanged (no audit noise).
    - B4 ids must be allowlisted AND not manual_review gated.

    Returns:
        filtered_skill_ids, audit_rows (skipped entries only).
    """
    audit_rows: list[dict[str, str]] = []
    out: list[str] = []

    for sid in skill_ids:
        if not is_b4_vocational_skill_id(sid):
            out.append(sid)
            continue

        if sid in B4_MANUAL_REVIEW_OR_UNAVAILABLE_SKILL_IDS:
            audit_rows.append(
                {
                    "skill_id": sid,
                    "action": "skipped",
                    "reason": "manual_review_or_future_ai_judged_skill_not_for_deterministic_adaptive",
                }
            )
            continue

        if sid not in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST:
            audit_rows.append(
                {
                    "skill_id": sid,
                    "action": "skipped",
                    "reason": "not_in_b4_chapter1_deterministic_allowlist",
                }
            )
            continue

        out.append(sid)

    return out, audit_rows


def filter_catalog_entries_for_b4_chapter1_deterministic_adaptive(
    entries: list[TEntry],
) -> tuple[list[TEntry], list[dict[str, str]]]:
    """
    Filter adaptive catalog rows (objects with `.skill_id`) for session_engine / adaptive v2.

    Same rules as `filter_skill_pool_for_b4_chapter1_deterministic_adaptive`, but preserves entry objects.
    Non-B4 entries pass through unchanged.
    """
    audit_rows: list[dict[str, str]] = []
    out: list[TEntry] = []

    for entry in entries:
        sid = getattr(entry, "skill_id", None)
        if not isinstance(sid, str) or not sid.strip():
            out.append(entry)
            continue
        if not is_b4_vocational_skill_id(sid):
            out.append(entry)
            continue

        if sid in B4_MANUAL_REVIEW_OR_UNAVAILABLE_SKILL_IDS:
            audit_rows.append(
                {
                    "skill_id": sid,
                    "action": "skipped",
                    "reason": "manual_review_or_future_ai_judged_skill_not_for_deterministic_adaptive",
                }
            )
            continue

        if sid not in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST:
            audit_rows.append(
                {
                    "skill_id": sid,
                    "action": "skipped",
                    "reason": "not_in_b4_chapter1_deterministic_allowlist",
                }
            )
            continue

        out.append(entry)

    return out, audit_rows


def validate_b4_deterministic_adaptive_generator_payload(
    skill_id: str,
    payload: dict,
) -> tuple[bool, str | None]:
    """
    Defensive validation after `skills.<skill_id>.generate()` for vocational B4.

    Non-B4 skills: always OK (caller should not rely on this for non-B4 semantics).
    """
    if not is_b4_vocational_skill_id(skill_id):
        return True, None

    pid = payload.get("problem_type_id")
    if not isinstance(pid, str) or not pid.strip():
        return False, "missing_or_invalid_problem_type_id"

    if pid in B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES:
        return False, f"excluded_problem_type:{pid}"

    return True, None


def format_adaptive_question_audit_dict(
    skill_id: str,
    payload: dict,
    *,
    source_type: str | None = None,
) -> dict[str, object]:
    """Structured audit blob for logs / optional JSON debug."""
    router_trace = payload.get("router_trace") if isinstance(payload.get("router_trace"), dict) else {}
    out: dict[str, object] = {
        "skill_id": skill_id,
        "problem_type_id": payload.get("problem_type_id"),
        "generator_key": payload.get("generator_key"),
        "subskill_id": payload.get("subskill_id"),
        "selection_reason": router_trace.get("selection_reason"),
        "router_trace": router_trace or None,
    }
    if source_type is not None:
        out["source_type"] = source_type
    return out


def is_pure_b4_allowlisted_adaptive_pool(skill_ids: list[str]) -> bool:
    """True when every skill_id is a vocational B4 id on the Chapter 1 deterministic allowlist."""
    if not skill_ids:
        return False
    return all(sid in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST for sid in skill_ids)


def allowlisted_b4_candidates(skill_ids: list[str]) -> list[str]:
    """B4 Chapter 1 deterministic candidates present in this pool (post Preflight filter)."""
    return [sid for sid in skill_ids if sid in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST]
