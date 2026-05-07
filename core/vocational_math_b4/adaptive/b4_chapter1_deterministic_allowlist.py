"""
B4 Chapter 1 deterministic adaptive allowlist (Phase 4F Preflight).

Source of truth:
- Phase 4E-Final runtime_ready skill coverage intent (deterministic int-answer practice path).
- Post-enrichment skills explicitly wired with wrappers + router (e.g. PermutationOfNonDistinctObjects).

This module MUST NOT import or rewrite `b4_ch1_runtime_coverage_matrix.csv`.
"""

from __future__ import annotations

from urllib.parse import urlencode
from typing import Iterable, TypeVar

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

B4_CHAPTER_1_GUIDED_PROGRESSION_STEPS = 10

B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER: tuple[str, ...] = (
    "vh_數學B4_AdditionPrinciple",
    "vh_數學B4_MultiplicationPrinciple",
    "vh_數學B4_FactorialNotation",
    "vh_數學B4_PermutationOfDistinctObjects",
    "vh_數學B4_RepeatedPermutation",
    "vh_數學B4_PermutationWithRepetition",
    "vh_數學B4_PermutationOfNonDistinctObjects",
    "vh_數學B4_CombinationDefinition",
    "vh_數學B4_Combination",
    "vh_數學B4_CombinationProperties",
    "vh_數學B4_CombinationApplications",
    "vh_數學B4_BinomialCoefficientIdentities",
    "vh_數學B4_BinomialTheorem",
)

B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILLS: tuple[str, ...] = (
    "vh_數學B4_TreeDiagramCounting",
    "vh_數學B4_PascalTriangle",
)

B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILL_METADATA: dict[str, dict[str, str]] = {
    "vh_數學B4_TreeDiagramCounting": {
        "display_name": "樹狀圖",
        "problem_type_id": "tree_diagram_listing",
        "answer_type": "handwriting",
        "grading_mode": "ai_judged_free_response",
        "index_param": "tree_diagram_index",
        "default_variant": "early_stopping_game",
        "practice_url_mode": "practice_handwriting",
        "adaptive_role": "free_response_checkpoint",
        "mastery_scoring": "deferred_teacher_review",
    },
    "vh_數學B4_PascalTriangle": {
        "display_name": "巴斯卡三角形",
        "problem_type_id": "pascal_triangle_handwriting",
        "answer_type": "handwriting",
        "grading_mode": "ai_judged_free_response",
        "index_param": "pascal_triangle_index",
        "default_variant": "pascal_row_listing",
        "practice_url_mode": "practice_handwriting",
        "adaptive_role": "free_response_checkpoint",
        "mastery_scoring": "deferred_teacher_review",
    },
}

B4_CHAPTER_1_CURRICULUM_PROGRESSION_WITH_FREE_RESPONSE: tuple[str, ...] = (
    "vh_數學B4_AdditionPrinciple",
    "vh_數學B4_MultiplicationPrinciple",
    "vh_數學B4_TreeDiagramCounting",
    "vh_數學B4_FactorialNotation",
    "vh_數學B4_PermutationOfDistinctObjects",
    "vh_數學B4_RepeatedPermutation",
    "vh_數學B4_PermutationWithRepetition",
    "vh_數學B4_PermutationOfNonDistinctObjects",
    "vh_數學B4_CombinationDefinition",
    "vh_數學B4_Combination",
    "vh_數學B4_CombinationProperties",
    "vh_數學B4_CombinationApplications",
    "vh_數學B4_BinomialCoefficientIdentities",
    "vh_數學B4_PascalTriangle",
    "vh_數學B4_BinomialTheorem",
)

_B4_CH1_FREE_RESPONSE_FALLBACK_INSERT_AFTER: dict[str, str] = {
    "vh_數學B4_TreeDiagramCounting": "vh_數學B4_MultiplicationPrinciple",
    "vh_數學B4_PascalTriangle": "vh_數學B4_BinomialCoefficientIdentities",
}
_B4_CH1_FREE_RESPONSE_FALLBACK_INSERT_BEFORE: dict[str, str] = {
    "vh_數學B4_PascalTriangle": "vh_數學B4_BinomialTheorem",
}

# Deterministic Chapter 1 starter order for first adaptive bootstrap only.
# Keep this list bounded and foundational; no expansion of problem-type coverage.
B4_CHAPTER_1_ADAPTIVE_STARTER_SKILL_ORDER: tuple[str, ...] = (
    "vh_數學B4_AdditionPrinciple",
    "vh_數學B4_MultiplicationPrinciple",
    "vh_數學B4_FactorialNotation",
    "vh_數學B4_PermutationOfDistinctObjects",
    "vh_數學B4_CombinationDefinition",
)

# Phase 5B-Fix-E:
# Minimal deterministic remediation bridge for B4 Chapter 1 teaching path.
# Keep routes inside deterministic allowlist and avoid manual_review/future_ai_judged skills.
B4_CHAPTER_1_REMEDIATION_BRIDGE: dict[str, tuple[str, ...]] = {
    "vh_數學B4_AdditionPrinciple": (
        "vh_數學B4_AdditionPrinciple",
    ),
    "vh_數學B4_MultiplicationPrinciple": (
        "vh_數學B4_AdditionPrinciple",
        "vh_數學B4_MultiplicationPrinciple",
    ),
    "vh_數學B4_FactorialNotation": (
        "vh_數學B4_MultiplicationPrinciple",
        "vh_數學B4_FactorialNotation",
    ),
    "vh_數學B4_PermutationOfDistinctObjects": (
        "vh_數學B4_FactorialNotation",
        "vh_數學B4_MultiplicationPrinciple",
    ),
    "vh_數學B4_RepeatedPermutation": (
        "vh_數學B4_MultiplicationPrinciple",
        "vh_數學B4_PermutationOfDistinctObjects",
    ),
    "vh_數學B4_PermutationWithRepetition": (
        "vh_數學B4_PermutationOfDistinctObjects",
        "vh_數學B4_MultiplicationPrinciple",
    ),
    "vh_數學B4_PermutationOfNonDistinctObjects": (
        "vh_數學B4_FactorialNotation",
        "vh_數學B4_PermutationOfDistinctObjects",
    ),
    "vh_數學B4_CombinationDefinition": (
        "vh_數學B4_MultiplicationPrinciple",
        "vh_數學B4_AdditionPrinciple",
    ),
    "vh_數學B4_CombinationApplications": (
        "vh_數學B4_CombinationDefinition",
        "vh_數學B4_MultiplicationPrinciple",
    ),
    "vh_數學B4_CombinationProperties": (
        "vh_數學B4_CombinationDefinition",
        "vh_數學B4_CombinationApplications",
    ),
    "vh_數學B4_Combination": (
        "vh_數學B4_CombinationDefinition",
        "vh_數學B4_CombinationProperties",
    ),
    "vh_數學B4_BinomialCoefficientIdentities": (
        "vh_數學B4_CombinationDefinition",
        "vh_數學B4_CombinationProperties",
    ),
    "vh_數學B4_BinomialTheorem": (
        "vh_數學B4_BinomialCoefficientIdentities",
        "vh_數學B4_CombinationDefinition",
    ),
}


def is_b4_vocational_skill_id(skill_id: str) -> bool:
    return isinstance(skill_id, str) and skill_id.startswith(B4_SKILL_PREFIX)


def is_b4_chapter1_ai_judged_free_response_skill(skill_id: str) -> bool:
    sid = str(skill_id or "").strip()
    return sid in B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILLS


def get_b4_chapter1_ai_judged_free_response_metadata(skill_id: str) -> dict[str, str] | None:
    sid = str(skill_id or "").strip()
    metadata = B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILL_METADATA.get(sid)
    return dict(metadata) if isinstance(metadata, dict) else None


def build_b4_chapter1_ai_judged_free_response_audit(
    include_practice_urls: bool = True,
) -> dict[str, object]:
    checkpoints: list[dict[str, object]] = []
    for sid in B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILLS:
        metadata = get_b4_chapter1_ai_judged_free_response_metadata(sid) or {}
        index_param = str(metadata.get("index_param") or "").strip()
        default_index = 0
        checkpoint: dict[str, object] = {
            "skill_id": sid,
            "display_name": str(metadata.get("display_name") or ""),
            "problem_type_id": str(metadata.get("problem_type_id") or ""),
            "answer_type": str(metadata.get("answer_type") or ""),
            "grading_mode": str(metadata.get("grading_mode") or ""),
            "index_param": index_param,
            "default_index": default_index,
        }
        if include_practice_urls:
            query = {
                "skill": sid,
                "problem_type": str(metadata.get("problem_type_id") or ""),
                "answer_type": str(metadata.get("answer_type") or ""),
                "grading_mode": str(metadata.get("grading_mode") or ""),
            }
            if index_param:
                query[index_param] = str(default_index)
            checkpoint["practice_url"] = f"/practice?{urlencode(query)}"
        checkpoints.append(checkpoint)

    return {
        "enabled": True,
        "scope": {
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "1",
            "chapter_name": "1 排列組合",
        },
        "scoring_policy": "visibility_only_not_mastery_scored",
        "adaptive_insertion_policy": "registered_checkpoint_not_auto_scored",
        "checkpoints": checkpoints,
    }


def get_b4_chapter1_curriculum_progression(include_free_response: bool = False) -> list[str]:
    if include_free_response:
        return list(B4_CHAPTER_1_CURRICULUM_PROGRESSION_WITH_FREE_RESPONSE)
    return list(B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER)


def _fetch_b4_chapter1_db_order_skill_ids() -> list[str]:
    """Best-effort DB order fetch for vocational/B4/chapter1 skill_ids."""
    try:
        from models import SkillCurriculum, db
    except Exception:
        return []
    try:
        rows = (
            db.session.query(SkillCurriculum.skill_id)
            .filter(
                SkillCurriculum.curriculum == "vocational",
                SkillCurriculum.volume == "數學B4",
                SkillCurriculum.chapter.in_(["1 排列組合", "1"]),
            )
            .order_by(
                SkillCurriculum.display_order.asc(),
                SkillCurriculum.difficulty_level.asc(),
                SkillCurriculum.id.asc(),
            )
            .all()
        )
    except Exception:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for row in rows:
        sid = str(getattr(row, "skill_id", "") or "").strip()
        if sid and sid not in seen:
            seen.add(sid)
            out.append(sid)
    return out


def _insert_with_fallback_anchor(sequence: list[str], skill_id: str) -> None:
    if skill_id in sequence:
        return
    anchor_after = _B4_CH1_FREE_RESPONSE_FALLBACK_INSERT_AFTER.get(skill_id)
    if anchor_after and anchor_after in sequence:
        sequence.insert(sequence.index(anchor_after) + 1, skill_id)
        return
    anchor_before = _B4_CH1_FREE_RESPONSE_FALLBACK_INSERT_BEFORE.get(skill_id)
    if anchor_before and anchor_before in sequence:
        sequence.insert(sequence.index(anchor_before), skill_id)
        return
    sequence.append(skill_id)


def get_b4_chapter1_curriculum_progression_from_db_or_fallback(
    include_free_response: bool = False,
) -> list[str]:
    """
    Prefer DB `skill_curriculum` ordering for B4 Chapter 1; fallback to constants only when unavailable.
    """
    db_order = _fetch_b4_chapter1_db_order_skill_ids()
    deterministic_db_order = [sid for sid in db_order if sid in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST]
    if not deterministic_db_order:
        return get_b4_chapter1_curriculum_progression(include_free_response=include_free_response)

    if not include_free_response:
        return deterministic_db_order

    combined_db_order = [
        sid
        for sid in db_order
        if sid in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST
        or sid in B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILLS
    ]
    for sid in B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILLS:
        _insert_with_fallback_anchor(combined_db_order, sid)
    return combined_db_order


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


def ordered_b4_chapter1_skills(skill_ids: Iterable[str]) -> list[str]:
    """Order a B4 Chapter 1 pool by teacher-designed curriculum progression."""
    ordered_rank = {
        sid: idx for idx, sid in enumerate(B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER)
    }
    seen: set[str] = set()
    candidates: list[tuple[int, str]] = []
    for input_idx, raw_sid in enumerate(skill_ids):
        sid = str(raw_sid or "").strip()
        if not sid or sid in seen:
            continue
        seen.add(sid)
        if sid in B4_MANUAL_REVIEW_OR_UNAVAILABLE_SKILL_IDS:
            continue
        candidates.append((input_idx, sid))
    candidates.sort(
        key=lambda item: (
            ordered_rank.get(item[1], len(ordered_rank)),
            item[0],
        )
    )
    return [sid for _, sid in candidates]


def ordered_b4_chapter1_skills_with_free_response(skill_ids: Iterable[str]) -> list[str]:
    ordered_rank = {
        sid: idx for idx, sid in enumerate(B4_CHAPTER_1_CURRICULUM_PROGRESSION_WITH_FREE_RESPONSE)
    }
    seen: set[str] = set()
    candidates: list[tuple[int, str]] = []
    for input_idx, raw_sid in enumerate(skill_ids):
        sid = str(raw_sid or "").strip()
        if not sid or sid in seen:
            continue
        seen.add(sid)
        candidates.append((input_idx, sid))
    candidates.sort(
        key=lambda item: (
            ordered_rank.get(item[1], len(ordered_rank)),
            item[0],
        )
    )
    return [sid for _, sid in candidates]


def starter_b4_candidates(skill_ids: list[str]) -> list[str]:
    """
    Keep only foundational Chapter 1 starter skills from the current pool, preserving starter order.
    """
    pool = set(skill_ids)
    ordered = [
        sid
        for sid in ordered_b4_chapter1_skills(B4_CHAPTER_1_ADAPTIVE_STARTER_SKILL_ORDER)
        if sid in pool
    ]
    return ordered


def synthetic_subskill_for_b4_skill(skill_id: str) -> str:
    sid = str(skill_id or "").strip()
    return f"b4_skill::{sid}" if sid else "b4_chapter1_synthetic_bootstrap"


def get_b4_chapter1_remediation_targets(skill_id: str) -> list[str]:
    sid = str(skill_id or "").strip()
    targets = list(B4_CHAPTER_1_REMEDIATION_BRIDGE.get(sid) or ())
    out = [
        target
        for target in targets
        if target in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST
        and target not in B4_MANUAL_REVIEW_OR_UNAVAILABLE_SKILL_IDS
    ]
    if not out and sid in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST:
        out = [sid]
    return out
