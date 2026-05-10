"""B4 Chapter 2 lightweight chapter mode handler — Phase 6N.

This module implements a deterministic, stage-balanced chapter-mode adaptive
flow for B4 Chapter 2 (機率).  It mirrors the Chap1 chapter-mode pattern
(resolve → synthetic bundle → guided progression → question generation)
but is self-contained:

  • No changes to core/adaptive/session_engine.py
  • Uses generate_for_chap2_skill (question_router) for question generation
  • Uses b4_chap2_visibility_audit for audit logging
  • Uses the same /api/adaptive/submit_and_get_next endpoint (branched by chapter_id)

Diagnostic plan (10 steps, 4 stages):

  Stage 1 — 集合與樣本空間
    step 0: BasicConceptsOfSets     → set_operation_count
    step 1: SampleSpaceAndEvents    → sample_space_count_numeric

  Stage 2 — 基本機率與運算
    step 2: ProbabilityDefinition   → classical_probability_fraction
    step 3: ProbabilityProperties   → complement_probability
    step 4: ProbabilityOperations   → event_operation_probability

  Stage 3 — 條件機率與獨立事件
    step 5: ConditionalProbability  → conditional_probability_basic
    step 6: IndependentEvents       → independent_joint_probability

  Stage 4 — 數學期望值
    step 7: MathematicalExpectationDefinition → expectation_discrete_basic
    step 8: ApplicationsOfExpectation         → expectation_word_problem_profit_fairness
    step 9: MathematicalExpectation           → expectation_assessment_numeric

Guardrails:
  - No mastery / APR / remediation updates
  - No handwriting / free-response
  - No reserved listing problem_types
  - Reserved listing problem_types are hard-excluded
"""
from __future__ import annotations

import hashlib
import uuid
from fractions import Fraction
from typing import Any

from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
    B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES,
    B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES,
)
from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
from core.vocational_math_b4.domain.b4_validators import (
    check_expected_value_answer,
    check_integer_answer,
    check_rational_answer,
)

# ─── Diagnostic plan ─────────────────────────────────────────────────────────

_B4_CHAP2_CHAPTER_PLAN: list[dict[str, str]] = [
    # Stage 1: 集合與樣本空間
    {
        "stage": "stage_1_sets_and_sample_space",
        "stage_label": "集合與樣本空間",
        "skill_id": "vh_數學B4_BasicConceptsOfSets",
        "problem_type_id": "set_operation_count",
        "answer_type": "integer",
        "checker": "check_integer_answer",
        "synthetic_family_id": "B4C2_SYN_01",
    },
    {
        "stage": "stage_1_sets_and_sample_space",
        "stage_label": "集合與樣本空間",
        "skill_id": "vh_數學B4_SampleSpaceAndEvents",
        "problem_type_id": "sample_space_count_numeric",
        "answer_type": "integer",
        "checker": "check_integer_answer",
        "synthetic_family_id": "B4C2_SYN_02",
    },
    # Stage 2: 基本機率與運算
    {
        "stage": "stage_2_basic_probability",
        "stage_label": "基本機率與運算",
        "skill_id": "vh_數學B4_ProbabilityDefinition",
        "problem_type_id": "classical_probability_fraction",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "synthetic_family_id": "B4C2_SYN_03",
    },
    {
        "stage": "stage_2_basic_probability",
        "stage_label": "基本機率與運算",
        "skill_id": "vh_數學B4_ProbabilityProperties",
        "problem_type_id": "complement_probability",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "synthetic_family_id": "B4C2_SYN_04",
    },
    {
        "stage": "stage_2_basic_probability",
        "stage_label": "基本機率與運算",
        "skill_id": "vh_數學B4_ProbabilityOperations",
        "problem_type_id": "event_operation_probability",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "synthetic_family_id": "B4C2_SYN_05",
    },
    # Stage 3: 條件機率與獨立事件
    {
        "stage": "stage_3_conditional_independent",
        "stage_label": "條件機率與獨立事件",
        "skill_id": "vh_數學B4_ConditionalProbability",
        "problem_type_id": "conditional_probability_basic",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "synthetic_family_id": "B4C2_SYN_06",
    },
    {
        "stage": "stage_3_conditional_independent",
        "stage_label": "條件機率與獨立事件",
        "skill_id": "vh_數學B4_IndependentEvents",
        "problem_type_id": "independent_joint_probability",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "synthetic_family_id": "B4C2_SYN_07",
    },
    # Stage 4: 數學期望值
    {
        "stage": "stage_4_expectation",
        "stage_label": "數學期望值",
        "skill_id": "vh_數學B4_MathematicalExpectationDefinition",
        "problem_type_id": "expectation_discrete_basic",
        "answer_type": "expected_value",
        "checker": "check_expected_value_answer",
        "synthetic_family_id": "B4C2_SYN_08",
    },
    {
        "stage": "stage_4_expectation",
        "stage_label": "數學期望值",
        "skill_id": "vh_數學B4_ApplicationsOfExpectation",
        "problem_type_id": "expectation_word_problem_profit_fairness",
        "answer_type": "expected_value",
        "checker": "check_expected_value_answer",
        "synthetic_family_id": "B4C2_SYN_09",
    },
    {
        "stage": "stage_4_expectation",
        "stage_label": "數學期望值",
        "skill_id": "vh_數學B4_MathematicalExpectation",
        "problem_type_id": "expectation_assessment_numeric",
        "answer_type": "expected_value",
        "checker": "check_expected_value_answer",
        "synthetic_family_id": "B4C2_SYN_10",
    },
]

B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS: int = len(_B4_CHAP2_CHAPTER_PLAN)

# ─── Session-local remediation bridges (Phase 6N-T) ──────────────────────────
# Each stage maps to a "bridge" problem that is simpler / more concrete.
# These are NOT in the main plan; they are extra remediation-only questions.
# Reserved listing types (sample_space_listing etc.) are hard-excluded.
_CHAP2_REMEDIATION_BRIDGES: dict[str, dict[str, str]] = {
    "stage_1_sets_and_sample_space": {
        "stage": "stage_1_sets_and_sample_space",
        "stage_label": "集合與樣本空間",
        "skill_id": "vh_數學B4_BasicConceptsOfSets",
        "problem_type_id": "inclusion_exclusion_count",
        "answer_type": "integer",
        "checker": "check_integer_answer",
        "synthetic_family_id": "B4C2_BRIDGE_01",
    },
    "stage_2_basic_probability": {
        "stage": "stage_2_basic_probability",
        "stage_label": "基本機率與運算",
        "skill_id": "vh_數學B4_ProbabilityDefinition",
        "problem_type_id": "dice_coin_probability_count",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "synthetic_family_id": "B4C2_BRIDGE_02",
    },
    "stage_3_conditional_independent": {
        "stage": "stage_3_conditional_independent",
        "stage_label": "條件機率與獨立事件",
        "skill_id": "vh_數學B4_ConditionalProbability",
        "problem_type_id": "without_replacement_conditional_probability",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "synthetic_family_id": "B4C2_BRIDGE_03",
    },
    "stage_4_expectation": {
        "stage": "stage_4_expectation",
        "stage_label": "數學期望值",
        "skill_id": "vh_數學B4_MathematicalExpectationDefinition",
        "problem_type_id": "expectation_from_distribution",
        "answer_type": "expected_value",
        "checker": "check_expected_value_answer",
        "synthetic_family_id": "B4C2_BRIDGE_04",
    },
}

# Problem_type-level remediation map (Phase 6P runtime integration).
_CHAP2_REMEDIATION_MAP: dict[str, dict[str, Any]] = {
    "set_operation_count": {
        "stage": "stage_1_sets_and_sample_space",
        "skill_id": "vh_數學B4_BasicConceptsOfSets",
        "problem_type_id": "set_operation_count",
        "answer_type": "integer",
        "checker": "check_integer_answer",
        "direct_prerequisites": [],
        "remediation_candidates": ["set_operation_count", "inclusion_exclusion_count"],
        "fallback_stage": "same_stage",
        "scoring_signal_class": "deterministic_checked",
    },
    "inclusion_exclusion_count": {
        "stage": "stage_1_sets_and_sample_space",
        "skill_id": "vh_數學B4_BasicConceptsOfSets",
        "problem_type_id": "inclusion_exclusion_count",
        "answer_type": "integer",
        "checker": "check_integer_answer",
        "direct_prerequisites": ["set_operation_count"],
        "remediation_candidates": ["inclusion_exclusion_count", "set_operation_count"],
        "fallback_stage": "same_stage",
        "scoring_signal_class": "deterministic_checked",
    },
    "sample_space_count_numeric": {
        "stage": "stage_1_sets_and_sample_space",
        "skill_id": "vh_數學B4_SampleSpaceAndEvents",
        "problem_type_id": "sample_space_count_numeric",
        "answer_type": "integer",
        "checker": "check_integer_answer",
        "direct_prerequisites": ["set_operation_count"],
        "remediation_candidates": ["sample_space_count_numeric", "set_operation_count"],
        "fallback_stage": "same_stage",
        "scoring_signal_class": "deterministic_checked",
    },
    "classical_probability_fraction": {
        "stage": "stage_2_basic_probability",
        "skill_id": "vh_數學B4_ProbabilityDefinition",
        "problem_type_id": "classical_probability_fraction",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "direct_prerequisites": ["sample_space_count_numeric"],
        "remediation_candidates": [
            "classical_probability_fraction",
            "dice_coin_probability_count",
            "sample_space_count_numeric",
        ],
        "fallback_stage": "previous_stage",
        "scoring_signal_class": "deterministic_checked",
    },
    "dice_coin_probability_count": {
        "stage": "stage_2_basic_probability",
        "skill_id": "vh_數學B4_ProbabilityDefinition",
        "problem_type_id": "dice_coin_probability_count",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "direct_prerequisites": ["sample_space_count_numeric", "classical_probability_fraction"],
        "remediation_candidates": [
            "dice_coin_probability_count",
            "classical_probability_fraction",
            "sample_space_count_numeric",
        ],
        "fallback_stage": "previous_stage",
        "scoring_signal_class": "deterministic_checked",
    },
    "complement_probability": {
        "stage": "stage_2_basic_probability",
        "skill_id": "vh_數學B4_ProbabilityProperties",
        "problem_type_id": "complement_probability",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "direct_prerequisites": ["classical_probability_fraction"],
        "remediation_candidates": [
            "complement_probability",
            "classical_probability_fraction",
            "dice_coin_probability_count",
        ],
        "fallback_stage": "same_stage",
        "scoring_signal_class": "deterministic_checked",
    },
    "union_intersection_probability": {
        "stage": "stage_2_basic_probability",
        "skill_id": "vh_數學B4_ProbabilityProperties",
        "problem_type_id": "union_intersection_probability",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "direct_prerequisites": ["classical_probability_fraction", "complement_probability"],
        "remediation_candidates": [
            "union_intersection_probability",
            "complement_probability",
            "classical_probability_fraction",
        ],
        "fallback_stage": "same_stage",
        "scoring_signal_class": "deterministic_checked",
    },
    "event_operation_probability": {
        "stage": "stage_2_basic_probability",
        "skill_id": "vh_數學B4_ProbabilityOperations",
        "problem_type_id": "event_operation_probability",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "direct_prerequisites": ["classical_probability_fraction", "union_intersection_probability"],
        "remediation_candidates": [
            "event_operation_probability",
            "union_intersection_probability",
            "complement_probability",
        ],
        "fallback_stage": "same_stage",
        "scoring_signal_class": "deterministic_checked",
    },
    "probability_algebra_mixed": {
        "stage": "stage_2_basic_probability",
        "skill_id": "vh_數學B4_ProbabilityOperations",
        "problem_type_id": "probability_algebra_mixed",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "direct_prerequisites": [
            "complement_probability",
            "union_intersection_probability",
            "event_operation_probability",
        ],
        "remediation_candidates": [
            "probability_algebra_mixed",
            "event_operation_probability",
            "union_intersection_probability",
            "complement_probability",
        ],
        "fallback_stage": "same_stage",
        "scoring_signal_class": "conservative",
    },
    "conditional_probability_basic": {
        "stage": "stage_3_conditional_independent",
        "skill_id": "vh_數學B4_ConditionalProbability",
        "problem_type_id": "conditional_probability_basic",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "direct_prerequisites": ["classical_probability_fraction", "sample_space_count_numeric"],
        "remediation_candidates": [
            "conditional_probability_basic",
            "without_replacement_conditional_probability",
            "classical_probability_fraction",
            "sample_space_count_numeric",
        ],
        "fallback_stage": "previous_stage",
        "scoring_signal_class": "deterministic_checked",
    },
    "without_replacement_conditional_probability": {
        "stage": "stage_3_conditional_independent",
        "skill_id": "vh_數學B4_ConditionalProbability",
        "problem_type_id": "without_replacement_conditional_probability",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "direct_prerequisites": [
            "conditional_probability_basic",
            "classical_probability_fraction",
            "sample_space_count_numeric",
        ],
        "remediation_candidates": [
            "without_replacement_conditional_probability",
            "conditional_probability_basic",
            "classical_probability_fraction",
        ],
        "fallback_stage": "previous_stage",
        "scoring_signal_class": "conservative",
    },
    "independent_joint_probability": {
        "stage": "stage_3_conditional_independent",
        "skill_id": "vh_數學B4_IndependentEvents",
        "problem_type_id": "independent_joint_probability",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "direct_prerequisites": ["classical_probability_fraction", "probability_multiplication_concept"],
        "remediation_candidates": [
            "independent_joint_probability",
            "conditional_probability_basic",
            "classical_probability_fraction",
        ],
        "fallback_stage": "previous_stage",
        "scoring_signal_class": "deterministic_checked",
    },
    "independent_at_least_one_probability": {
        "stage": "stage_3_conditional_independent",
        "skill_id": "vh_數學B4_IndependentEvents",
        "problem_type_id": "independent_at_least_one_probability",
        "answer_type": "rational_fraction",
        "checker": "check_rational_answer",
        "direct_prerequisites": ["complement_probability", "independent_joint_probability"],
        "remediation_candidates": [
            "independent_at_least_one_probability",
            "independent_joint_probability",
            "complement_probability",
        ],
        "fallback_stage": "previous_stage",
        "scoring_signal_class": "conservative",
    },
    "expectation_discrete_basic": {
        "stage": "stage_4_expectation",
        "skill_id": "vh_數學B4_MathematicalExpectationDefinition",
        "problem_type_id": "expectation_discrete_basic",
        "answer_type": "expected_value",
        "checker": "check_expected_value_answer",
        "direct_prerequisites": ["classical_probability_fraction"],
        "remediation_candidates": [
            "expectation_discrete_basic",
            "expectation_from_distribution",
            "classical_probability_fraction",
        ],
        "fallback_stage": "previous_stage",
        "scoring_signal_class": "deterministic_checked",
    },
    "expectation_from_distribution": {
        "stage": "stage_4_expectation",
        "skill_id": "vh_數學B4_MathematicalExpectationDefinition",
        "problem_type_id": "expectation_from_distribution",
        "answer_type": "expected_value",
        "checker": "check_expected_value_answer",
        "direct_prerequisites": ["expectation_discrete_basic", "classical_probability_fraction"],
        "remediation_candidates": [
            "expectation_from_distribution",
            "expectation_discrete_basic",
            "classical_probability_fraction",
        ],
        "fallback_stage": "previous_stage",
        "scoring_signal_class": "deterministic_checked",
    },
    "expectation_word_problem_profit_fairness": {
        "stage": "stage_4_expectation",
        "skill_id": "vh_數學B4_ApplicationsOfExpectation",
        "problem_type_id": "expectation_word_problem_profit_fairness",
        "answer_type": "expected_value",
        "checker": "check_expected_value_answer",
        "direct_prerequisites": [
            "expectation_discrete_basic",
            "expectation_from_distribution",
            "classical_probability_fraction",
        ],
        "remediation_candidates": [
            "expectation_word_problem_profit_fairness",
            "expectation_from_distribution",
            "expectation_discrete_basic",
            "classical_probability_fraction",
        ],
        "fallback_stage": "previous_stage",
        "scoring_signal_class": "conservative",
    },
    "expectation_assessment_numeric": {
        "stage": "stage_4_expectation",
        "skill_id": "vh_數學B4_MathematicalExpectation",
        "problem_type_id": "expectation_assessment_numeric",
        "answer_type": "expected_value",
        "checker": "check_expected_value_answer",
        "direct_prerequisites": ["expectation_discrete_basic", "expectation_from_distribution"],
        "remediation_candidates": [
            "expectation_assessment_numeric",
            "expectation_from_distribution",
            "expectation_discrete_basic",
            "classical_probability_fraction",
        ],
        "fallback_stage": "previous_stage",
        "scoring_signal_class": "conservative",
    },
}

# Strict stage order for remediation forward-stage guard (Phase 6N-T-R2)
_CHAP2_STAGE_ORDER: dict[str, int] = {
    "stage_1_sets_and_sample_space": 1,
    "stage_2_basic_probability": 2,
    "stage_3_conditional_independent": 3,
    "stage_4_expectation": 4,
}


# Consecutive-wrong threshold to trigger remediation within a stage
_CHAP2_FAIL_STREAK_THRESHOLD: int = 2
# Maximum remediation attempts per trigger (prevents infinite loops)
_CHAP2_MAX_REMEDIATION_ATTEMPTS: int = 2

# Ordered list of all 10 Chap2 skills in curriculum order (mirrors the plan)
B4_CHAP2_CHAPTER_SKILL_IDS: list[str] = [
    "vh_數學B4_BasicConceptsOfSets",
    "vh_數學B4_SampleSpaceAndEvents",
    "vh_數學B4_ProbabilityDefinition",
    "vh_數學B4_ProbabilityProperties",
    "vh_數學B4_ProbabilityOperations",
    "vh_數學B4_ConditionalProbability",
    "vh_數學B4_IndependentEvents",
    "vh_數學B4_MathematicalExpectationDefinition",
    "vh_數學B4_ApplicationsOfExpectation",
    "vh_數學B4_MathematicalExpectation",
]

# Stage labels in order
B4_CHAP2_CHAPTER_STAGES: list[dict[str, object]] = [
    {
        "stage_id": "stage_1_sets_and_sample_space",
        "stage_label": "集合與樣本空間",
        "step_range": [0, 1],
    },
    {
        "stage_id": "stage_2_basic_probability",
        "stage_label": "基本機率與運算",
        "step_range": [2, 4],
    },
    {
        "stage_id": "stage_3_conditional_independent",
        "stage_label": "條件機率與獨立事件",
        "step_range": [5, 6],
    },
    {
        "stage_id": "stage_4_expectation",
        "stage_label": "數學期望值",
        "step_range": [7, 9],
    },
]


# ─── Helper functions ─────────────────────────────────────────────────────────

def get_b4_chap2_chapter_plan() -> list[dict[str, str]]:
    """Return a copy of the diagnostic plan (immutable public access)."""
    return [dict(step) for step in _B4_CHAP2_CHAPTER_PLAN]


def is_b4_chap2_chapter_complete(step_number: int) -> bool:
    """Return True when all plan steps have been answered."""
    return step_number >= B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS


def get_plan_step(step_index: int) -> dict[str, str] | None:
    """Return the plan entry for a given step index, or None if out of range."""
    if 0 <= step_index < len(_B4_CHAP2_CHAPTER_PLAN):
        return dict(_B4_CHAP2_CHAPTER_PLAN[step_index])
    return None


def get_chap2_remediation_bridge(stage_id: str) -> dict[str, str] | None:
    """Return the remediation bridge spec for a given stage, or None."""
    return dict(_CHAP2_REMEDIATION_BRIDGES[stage_id]) if stage_id in _CHAP2_REMEDIATION_BRIDGES else None


def get_chap2_remediation_map() -> dict[str, dict[str, Any]]:
    return {k: dict(v) for k, v in _CHAP2_REMEDIATION_MAP.items()}


def _stage_rank(stage_id: str) -> int:
    return int(_CHAP2_STAGE_ORDER.get(str(stage_id or ""), 0))


def _select_guarded_remediation_stage(
    *,
    failed_stage: str,
    remediation_stage: str,
) -> str:
    """
    Select remediation bridge stage with strict anti-forward guard.

    Bridge stage must never be after the failed stage. If failed_stage is missing
    or invalid, remediation_stage is used as fallback ceiling. Final fallback is
    the nearest available prior/equal stage in bridge catalog.
    """
    failed = str(failed_stage or "")
    current = str(remediation_stage or "")
    failed_rank = _stage_rank(failed)
    current_rank = _stage_rank(current)
    ceiling = failed_rank or current_rank
    if ceiling <= 0:
        if failed in _CHAP2_REMEDIATION_BRIDGES:
            return failed
        if current in _CHAP2_REMEDIATION_BRIDGES:
            return current
        return ""
    if failed in _CHAP2_REMEDIATION_BRIDGES and failed_rank <= ceiling:
        return failed
    candidates = [
        stage_id
        for stage_id in _CHAP2_REMEDIATION_BRIDGES
        if _stage_rank(stage_id) > 0 and _stage_rank(stage_id) <= ceiling
    ]
    if not candidates:
        return ""
    candidates.sort(key=_stage_rank, reverse=True)
    return candidates[0]


def _stage_label(stage_id: str) -> str:
    for s in B4_CHAP2_CHAPTER_STAGES:
        if str(s.get("stage_id") or "") == str(stage_id or ""):
            return str(s.get("stage_label") or stage_id or "")
    return str(stage_id or "")


def _build_stage_fallback_entry(stage_id: str) -> dict[str, Any] | None:
    stage_key = str(stage_id or "")
    bridge = _CHAP2_REMEDIATION_BRIDGES.get(stage_key)
    if not bridge:
        return None
    return {
        "stage": stage_key,
        "stage_label": bridge.get("stage_label") or _stage_label(stage_key),
        "skill_id": bridge.get("skill_id", ""),
        "problem_type_id": bridge.get("problem_type_id", ""),
        "answer_type": bridge.get("answer_type", "rational_fraction"),
        "checker": bridge.get("checker", "check_rational_answer"),
        "synthetic_family_id": bridge.get("synthetic_family_id", ""),
    }


def _select_remediation_target(
    *,
    failed_problem_type_id: str,
    failed_stage: str,
    remediation_stage: str,
) -> tuple[dict[str, Any] | None, str, list[str]]:
    source = "stage_fallback"
    considered: list[str] = []
    failed_stage_key = _select_guarded_remediation_stage(
        failed_stage=failed_stage,
        remediation_stage=remediation_stage,
    )
    ceiling_rank = _stage_rank(failed_stage_key)
    failed_pt = str(failed_problem_type_id or "")
    map_entry = _CHAP2_REMEDIATION_MAP.get(failed_pt)
    if map_entry:
        for candidate in list(map_entry.get("remediation_candidates") or []):
            pid = str(candidate or "")
            if not pid:
                continue
            considered.append(pid)
            if pid not in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES:
                continue
            if pid in B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES:
                continue
            candidate_entry = _CHAP2_REMEDIATION_MAP.get(pid)
            if not candidate_entry:
                continue
            candidate_rank = _stage_rank(str(candidate_entry.get("stage") or ""))
            if ceiling_rank > 0 and candidate_rank > ceiling_rank:
                continue
            selected = dict(candidate_entry)
            selected["stage_label"] = _stage_label(str(selected.get("stage") or ""))
            selected["synthetic_family_id"] = f"B4C2_REMED_MAP_{pid}".upper()
            return selected, "problem_type_map", considered
    stage_candidates: list[str] = []
    if failed_stage_key:
        stage_candidates.append(failed_stage_key)
    if ceiling_rank > 1:
        for rank in range(ceiling_rank - 1, 0, -1):
            for stage_id, stage_rank in _CHAP2_STAGE_ORDER.items():
                if stage_rank == rank:
                    stage_candidates.append(stage_id)
    for stage_id in stage_candidates:
        fallback = _build_stage_fallback_entry(stage_id)
        if not fallback:
            continue
        pid = str(fallback.get("problem_type_id") or "")
        considered.append(pid)
        if pid not in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES:
            continue
        if pid in B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES:
            continue
        return fallback, source, considered
    return None, source, considered


def _derive_question_seed(session_id: str, step_index: int) -> int:
    """Stable seed per (session_id, step_index) — deterministic for a given session."""
    raw = f"b4c2chap::{session_id}::{step_index}"
    return (int(hashlib.sha256(raw.encode()).hexdigest()[:8], 16) % 1_000_000) + 1


def _derive_remediation_seed(session_id: str, stage_id: str, attempt: int) -> int:
    """Stable seed per (session_id, stage_id, attempt) for remediation questions."""
    raw = f"b4c2remediation::{session_id}::{stage_id}::{attempt}"
    return (int(hashlib.sha256(raw.encode()).hexdigest()[:8], 16) % 1_000_000) + 1


def _check_answer_for_plan_step(
    plan_step: dict[str, str],
    user_answer: str,
    correct_answer: str,
) -> tuple[bool, str]:
    """
    Run the appropriate Chap2 checker for the given plan step.

    Returns (is_correct, checker_name).
    """
    answer_type = plan_step.get("answer_type", "")
    user_ans = str(user_answer or "").strip()
    correct = str(correct_answer or "").strip()

    if answer_type == "integer":
        try:
            expected_int = int(correct)
        except (TypeError, ValueError):
            return False, "check_integer_answer"
        return check_integer_answer(user_ans, expected_int), "check_integer_answer"

    if answer_type == "expected_value":
        return check_expected_value_answer(user_ans, correct), "check_expected_value_answer"

    # default: rational_fraction
    if "/" in correct:
        parts = correct.split("/", 1)
        try:
            num, den = int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            return False, "check_rational_answer"
        return check_rational_answer(user_ans, num, den), "check_rational_answer"

    try:
        val = int(correct)
        return check_rational_answer(user_ans, val, 1), "check_rational_answer"
    except (TypeError, ValueError):
        return check_rational_answer(user_ans, 0, 1), "check_rational_answer"


def _build_question_data(payload: dict[str, Any], plan_step: dict[str, str]) -> dict[str, Any]:
    """Extract question data from a generator payload, normalized for the frontend."""
    correct = str(payload.get("correct_answer") or payload.get("answer") or "")
    question_text = str(payload.get("question_text") or "")
    return {
        "question_text": question_text,
        "question": question_text,
        "answer": correct,
        "correct_answer": correct,
        "choices": list(payload.get("choices") or []),
        "explanation": str(payload.get("explanation") or ""),
        "skill_id": str(payload.get("skill_id") or plan_step.get("skill_id", "")),
        "problem_type_id": str(payload.get("problem_type_id") or plan_step.get("problem_type_id", "")),
        "answer_type": str(payload.get("answer_type") or plan_step.get("answer_type", "")),
        "family_id": plan_step.get("synthetic_family_id", ""),
        "family_name": f"B4 Chapter2 {plan_step.get('stage_label', '')} Step",
        "subskill_nodes": [
            f"b4_chap2_skill::{plan_step.get('skill_id', '')}",
            "b4_chapter2_synthetic_bootstrap",
        ],
        "difficulty": int(payload.get("difficulty") or 1),
        "generator_key": str(payload.get("generator_key") or ""),
        "diagnosis_tags": list(payload.get("diagnosis_tags") or []),
        "source": "b4_chap2_chapter_mode",
        "b4_chap2_chapter_mode": True,
    }


def _compute_display_apr(
    *,
    step_index: int,
    correct_count: int,
    attempt_count: int,
    total_steps: int = 10,
) -> float:
    """
    Compute a display-only APR (0.0–1.0) for the Chap2 chapter mode UI.

    Formula:
        display_apr = 0.5 * (step_index / total_steps)
                    + 0.5 * (correct_count / max(1, attempt_count))

    This is NOT stored to the DB and is not a formal mastery score.
    """
    progress_ratio = min(1.0, step_index / max(1, total_steps))
    correct_rate = correct_count / max(1, attempt_count) if attempt_count > 0 else 0.0
    raw = 0.5 * progress_ratio + 0.5 * correct_rate
    return round(min(1.0, max(0.0, raw)), 4)


def _build_trajectory_points(
    *,
    runtime: dict[str, Any],
    step_index: int,
    correct_count: int,
    attempt_count: int,
    is_correct: bool | None,
) -> list[dict[str, Any]]:
    """Build a list of trajectory point dicts from history stored in runtime."""
    history: list[dict[str, Any]] = list(runtime.get("chap2_trajectory_history") or [])
    if is_correct is not None:
        last_plan_step_index = int(runtime.get("chap2_step_index") or 0)
        plan_step = get_plan_step(last_plan_step_index)
        apr = _compute_display_apr(
            step_index=last_plan_step_index + 1,
            correct_count=correct_count,
            attempt_count=attempt_count,
        )
        history.append({
            "step_index": last_plan_step_index,
            "stage": plan_step.get("stage", "") if plan_step else "",
            "skill_id": plan_step.get("skill_id", "") if plan_step else "",
            "problem_type_id": plan_step.get("problem_type_id", "") if plan_step else "",
            "answered": True,
            "is_correct": is_correct,
            "display_apr": apr,
            "progress_percent": round(100.0 * (last_plan_step_index + 1) / B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS, 1),
            "display_mastery_percent": round(apr * 100),
        })
    return history


def _build_completed_response(
    session_id: str,
    step_number: int,
    *,
    correct_count: int = 0,
    attempt_count: int = 0,
    trajectory_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a completion response when all plan steps are done."""
    final_apr = _compute_display_apr(
        step_index=B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
        correct_count=correct_count,
        attempt_count=attempt_count,
    )
    correct_rate = correct_count / max(1, attempt_count) if attempt_count > 0 else 0.0
    return {
        "session_id": session_id,
        "step_number": step_number,
        "current_apr": final_apr,
        "ppo_strategy": 1,
        "frustration_index": 0,
        "execution_latency": 0,
        "completed": True,
        "unit_completed": True,
        "assessment_completed": True,
        "mode": "teaching",
        "new_question_data": {
            "question_text": "診斷已完成，共 10 題覆蓋 B4 第二章所有單元。",
            "question": "診斷已完成，共 10 題覆蓋 B4 第二章所有單元。",
            "answer": "",
            "correct_answer": "",
            "choices": [],
            "explanation": "",
            "skill_id": "",
            "problem_type_id": "",
            "answer_type": "",
            "family_id": "",
            "family_name": "",
            "subskill_nodes": [],
        },
        "target_family_id": "",
        "target_subskills": [],
        "is_correct": None,
        "b4_chap2_chapter_mode": True,
        "chapter_stage": "completed",
        "chapter_stage_label": "診斷完成",
        "chapter_total_steps": B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
        "chapter_current_step": step_number,
        "completed_steps": attempt_count,
        "total_steps": B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
        "progress_percent": 100.0,
        "session_correct_count": correct_count,
        "session_attempt_count": attempt_count,
        "session_correct_rate": round(correct_rate, 4),
        "display_mastery_percent": round(final_apr * 100),
        "trajectory_points": list(trajectory_history or []),
        "current_stage": "completed",
        "current_stage_label": "診斷完成",
        "current_skill_id": "",
        "current_problem_type_id": "",
        "next_skill_id": "",
        "next_problem_type_id": "",
    }


# ─── Main handler ─────────────────────────────────────────────────────────────

def build_b4_chap2_chapter_response(
    payload: dict[str, Any],
    *,
    runtime: dict[str, Any],
) -> dict[str, Any]:
    """
    Main handler for B4 Chapter 2 chapter-mode adaptive flow.

    Parameters
    ----------
    payload : dict
        The parsed JSON payload from the frontend.
        Relevant fields: step_number, session_id, user_answer, student_id.
    runtime : dict
        The per-session runtime dict from adaptive_runtime_store.
        Contains correct_answer, question_text from the previous step.

    Returns
    -------
    dict
        A response dict compatible with adaptive_practice_v2.html's renderQuestion().
    """
    step_number = int(payload.get("step_number") or 0)
    raw_session_id = str(payload.get("session_id") or "").strip()
    user_answer = str(payload.get("user_answer") or "").strip()
    is_answer_submission = bool(user_answer and raw_session_id)

    # New session or bootstrap
    if step_number == 0 or not raw_session_id:
        session_id = uuid.uuid4().hex
        mainline_step_index = 0
    else:
        session_id = raw_session_id
        mainline_step_index = int(runtime.get("chap2_step_index") or step_number)

    # --- Session-local counters (display only, no DB writes) ---
    correct_count: int = int(runtime.get("session_correct_count") or 0)
    attempt_count: int = int(runtime.get("session_attempt_count") or 0)
    trajectory_history: list[dict[str, Any]] = list(runtime.get("chap2_trajectory_history") or [])
    stage_fail_streak: dict[str, int] = dict(runtime.get("stage_fail_streak") or {})
    is_correct_this_step: bool | None = None

    # --- Phase 6N-T: session-local remediation state ---
    in_remediation: bool = bool(runtime.get("in_remediation"))
    remediation_stage: str = str(runtime.get("remediation_stage") or "")
    remediation_attempt: int = int(runtime.get("remediation_attempt") or 0)
    resume_step_index: int = int(runtime.get("resume_step_index") or mainline_step_index)
    return_ready: bool = bool(runtime.get("return_ready"))
    has_returned_to_main: bool = bool(runtime.get("has_returned_to_main"))
    remediation_reason: str = str(runtime.get("remediation_reason") or "")
    # Phase 6N-T-R: explicit failed-stage lock — preserved from remediation trigger moment
    failed_stage: str = str(runtime.get("failed_stage") or remediation_stage)
    failed_skill_id: str = str(runtime.get("failed_skill_id") or "")
    failed_problem_type_id: str = str(runtime.get("failed_problem_type_id") or "")
    remediation_source: str = str(runtime.get("remediation_source") or "")
    remediation_candidates_considered: list[str] = list(runtime.get("remediation_candidates_considered") or [])
    selected_remediation_problem_type_id: str = str(runtime.get("selected_remediation_problem_type_id") or "")
    selected_remediation_skill_id: str = str(runtime.get("selected_remediation_skill_id") or "")

    grading_analysis: dict[str, Any] | None = None

    # ─── Answer submission path ───────────────────────────────────────────────
    if is_answer_submission and runtime:
        last_correct_answer = str(runtime.get("correct_answer") or "").strip()
        last_skill_id = str(runtime.get("skill_id") or "").strip()

        if in_remediation:
            # ── Grading a REMEDIATION (bridge) question ──
            remediation_q_stage = str(runtime.get("remediation_selected_stage") or remediation_stage or failed_stage)
            remediation_q_spec = {
                "stage": remediation_q_stage,
                "stage_label": _stage_label(remediation_q_stage),
                "skill_id": str(runtime.get("skill_id") or ""),
                "problem_type_id": str(runtime.get("problem_type_id") or ""),
                "answer_type": str(runtime.get("answer_type") or "rational_fraction"),
                "checker": "check_expected_value_answer"
                if str(runtime.get("answer_type") or "") == "expected_value"
                else ("check_integer_answer" if str(runtime.get("answer_type") or "") == "integer" else "check_rational_answer"),
                "synthetic_family_id": str(runtime.get("family_id") or ""),
            }
            if last_correct_answer:
                is_correct_this_step, checker_name = _check_answer_for_plan_step(
                    remediation_q_spec, user_answer, last_correct_answer
                )
                attempt_count += 1
                if is_correct_this_step:
                    correct_count += 1
                apr_after = _compute_display_apr(
                    step_index=resume_step_index,
                    correct_count=correct_count,
                    attempt_count=attempt_count,
                )
                trajectory_history.append({
                    "step_index": None,
                    "stage": remediation_q_stage,
                    "skill_id": remediation_q_spec.get("skill_id", ""),
                    "problem_type_id": remediation_q_spec.get("problem_type_id", ""),
                    "answered": True,
                    "is_correct": is_correct_this_step,
                    "is_remediation": True,
                    "display_apr": apr_after,
                    "progress_percent": round(
                        100.0 * resume_step_index / B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS, 1
                    ),
                    "display_mastery_percent": round(apr_after * 100),
                })
                _maybe_write_audit_log(
                    skill_id=last_skill_id,
                    current_question=runtime,
                    user_answer=user_answer,
                    is_correct=is_correct_this_step,
                    checker_name=checker_name,
                )
                grading_analysis = {
                    "family_id": remediation_q_spec.get("synthetic_family_id", ""),
                    "error_mechanism": "remediation",
                    "step_focus": remediation_q_spec.get("stage_label", ""),
                    "main_issue": "補救正確，準備返回主線" if is_correct_this_step else "繼續補強",
                    "status": "correct" if is_correct_this_step else "incorrect",
                    "expected_answer": last_correct_answer,
                    "answer_feedback": "正確" if is_correct_this_step else f"正確答案為 {last_correct_answer}",
                    "analysis_source": checker_name,
                    "is_correct": is_correct_this_step,
                    "grading_step": resume_step_index,
                    "is_remediation": True,
                }
                payload["is_correct"] = is_correct_this_step
                payload["answer_feedback"] = grading_analysis["answer_feedback"]

                if is_correct_this_step:
                    # Remediation success → return to mainline
                    return_ready = True
                    in_remediation = False
                    has_returned_to_main = True
                    stage_fail_streak[remediation_q_stage] = 0
                    mainline_step_index = resume_step_index
                else:
                    remediation_attempt += 1
                    if remediation_attempt >= _CHAP2_MAX_REMEDIATION_ATTEMPTS:
                        # Forced return after max attempts
                        in_remediation = False
                        has_returned_to_main = True
                        mainline_step_index = resume_step_index
                    # else: stay in remediation with next attempt
        else:
            # ── Grading a MAINLINE question ──
            last_plan_step_index = int(runtime.get("chap2_step_index") or 0)
            last_plan_step = get_plan_step(last_plan_step_index)
            if last_plan_step and last_correct_answer:
                is_correct_this_step, checker_name = _check_answer_for_plan_step(
                    last_plan_step, user_answer, last_correct_answer
                )
                attempt_count += 1
                if is_correct_this_step:
                    correct_count += 1
                # Update stage fail streak
                current_stage_id = last_plan_step.get("stage", "")
                if is_correct_this_step:
                    stage_fail_streak[current_stage_id] = 0
                else:
                    stage_fail_streak[current_stage_id] = stage_fail_streak.get(current_stage_id, 0) + 1

                apr_after = _compute_display_apr(
                    step_index=last_plan_step_index + 1,
                    correct_count=correct_count,
                    attempt_count=attempt_count,
                )
                trajectory_history.append({
                    "step_index": last_plan_step_index,
                    "stage": current_stage_id,
                    "skill_id": last_plan_step.get("skill_id", ""),
                    "problem_type_id": last_plan_step.get("problem_type_id", ""),
                    "answered": True,
                    "is_correct": is_correct_this_step,
                    "is_remediation": False,
                    "display_apr": apr_after,
                    "progress_percent": round(
                        100.0 * (last_plan_step_index + 1) / B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS, 1
                    ),
                    "display_mastery_percent": round(apr_after * 100),
                })
                _maybe_write_audit_log(
                    skill_id=last_skill_id,
                    current_question=runtime,
                    user_answer=user_answer,
                    is_correct=is_correct_this_step,
                    checker_name=checker_name,
                )
                grading_analysis = {
                    "family_id": last_plan_step.get("synthetic_family_id", ""),
                    "error_mechanism": "unknown",
                    "step_focus": last_plan_step.get("stage_label", ""),
                    "main_issue": "正確" if is_correct_this_step else "答案有誤，請見解析。",
                    "status": "correct" if is_correct_this_step else "incorrect",
                    "expected_answer": last_correct_answer,
                    "answer_feedback": "正確" if is_correct_this_step else f"正確答案為 {last_correct_answer}",
                    "analysis_source": checker_name,
                    "is_correct": is_correct_this_step,
                    "grading_step": last_plan_step_index,
                    "is_remediation": False,
                }
                payload["is_correct"] = is_correct_this_step
                payload["answer_feedback"] = grading_analysis["answer_feedback"]

                # Advance mainline step BEFORE checking remediation
                mainline_step_index = last_plan_step_index + 1

                # --- Remediation trigger ---
                streak = stage_fail_streak.get(current_stage_id, 0)
                bridge_available = current_stage_id in _CHAP2_REMEDIATION_BRIDGES
                if (
                    streak >= _CHAP2_FAIL_STREAK_THRESHOLD
                    and not is_correct_this_step
                    and bridge_available
                    and not is_b4_chap2_chapter_complete(mainline_step_index)
                ):
                    in_remediation = True
                    remediation_stage = current_stage_id
                    remediation_attempt = 0
                    resume_step_index = mainline_step_index
                    return_ready = False
                    has_returned_to_main = False
                    remediation_reason = (
                        f"連續答錯 {streak} 題（{last_plan_step.get('stage_label', current_stage_id)}），"
                        f"進入近側發展區補救"
                    )
                    # Phase 6N-T-R: lock the failed stage at trigger moment
                    # These are NEVER overwritten by subsequent mainline_step advancement
                    failed_stage = current_stage_id
                    failed_skill_id = last_plan_step.get("skill_id", "")
                    failed_problem_type_id = last_plan_step.get("problem_type_id", "")
                    remediation_source = ""
                    remediation_candidates_considered = []
                    selected_remediation_problem_type_id = ""
                    selected_remediation_skill_id = ""

    # ─── Determine what to show next ─────────────────────────────────────────

    # --- If in remediation, serve bridge question ---
    if in_remediation:
        selected_target, remediation_source, remediation_candidates_considered = _select_remediation_target(
            failed_problem_type_id=failed_problem_type_id,
            failed_stage=failed_stage,
            remediation_stage=remediation_stage,
        )
        if not selected_target:
            # Safety fallback: exit remediation if no bridge found
            in_remediation = False
            mainline_step_index = resume_step_index
        selected_stage_key = str(selected_target.get("stage") or "") if selected_target else ""
        selected_remediation_problem_type_id = (
            str(selected_target.get("problem_type_id") or "") if selected_target else ""
        )
        selected_remediation_skill_id = str(selected_target.get("skill_id") or "") if selected_target else ""
        seed = _derive_remediation_seed(session_id, selected_stage_key, remediation_attempt)
        try:
            bridge_payload = generate_for_chap2_skill(
                skill_id=selected_remediation_skill_id,
                problem_type_id=selected_remediation_problem_type_id,
                seed=seed,
                level=1,
                multiple_choice=True,
            )
        except Exception:
            # Fallback: exit remediation and continue mainline
            in_remediation = False
            mainline_step_index = resume_step_index
            bridge_payload = None

        if in_remediation and bridge_payload is not None:
            bridge_question_data = _build_question_data(bridge_payload, selected_target)
            display_apr = _compute_display_apr(
                step_index=resume_step_index,
                correct_count=correct_count,
                attempt_count=attempt_count,
            )
            correct_rate = correct_count / max(1, attempt_count) if attempt_count > 0 else 0.0
            progress_pct = round(100.0 * resume_step_index / B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS, 1)
            stage_label = str(selected_target.get("stage_label") or _stage_label(selected_stage_key))
            next_plan_step = get_plan_step(resume_step_index)
            next_skill_id = next_plan_step.get("skill_id", "") if next_plan_step else ""
            next_problem_type_id = next_plan_step.get("problem_type_id", "") if next_plan_step else ""

            response: dict[str, Any] = {
                "session_id": session_id,
                "step_number": attempt_count,
                "current_apr": display_apr,
                "ppo_strategy": 2,
                "frustration_index": int(stage_fail_streak.get(selected_stage_key, 0)),
                "execution_latency": 0,
                "completed": False,
                "unit_completed": False,
                "assessment_completed": False,
                "mode": "teaching",
                "new_question_data": bridge_question_data,
                "target_family_id": selected_target.get("synthetic_family_id", ""),
                "target_subskills": list(bridge_question_data.get("subskill_nodes") or []),
                "is_correct": is_correct_this_step if is_answer_submission else None,
                "b4_chap2_chapter_mode": True,
                "chapter_stage": selected_stage_key,
                "chapter_stage_label": stage_label,
                "chapter_total_steps": B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
                "chapter_current_step": resume_step_index,
                # UI state
                "completed_steps": attempt_count,
                "total_steps": B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
                "progress_percent": progress_pct,
                "session_correct_count": correct_count,
                "session_attempt_count": attempt_count,
                "session_correct_rate": round(correct_rate, 4),
                "display_mastery_percent": round(display_apr * 100),
                "current_stage": selected_stage_key,
                "current_stage_label": stage_label,
                "current_skill_id": selected_remediation_skill_id,
                "current_problem_type_id": selected_remediation_problem_type_id,
                "next_skill_id": next_skill_id,
                "next_problem_type_id": next_problem_type_id,
                "trajectory_points": trajectory_history,
                # Remediation UI state (Phase 6N-T / 6N-T-R)
                "in_remediation": True,
                "return_ready": False,
                "has_returned_to_main": False,
                "remediation_reason": remediation_reason,
                "remediation_stage_id": selected_stage_key,
                "remediation_attempt": remediation_attempt,
                "stage_fail_streak": stage_fail_streak,
                "session_local_fail_streak": stage_fail_streak.get(selected_stage_key, 0),
                "current_strategy": "近側發展區補救",
                "display_mode": "remediation",
                # Phase 6N-T-R: failed-stage lock fields
                "failed_stage": failed_stage,
                "failed_skill_id": failed_skill_id,
                "failed_problem_type_id": failed_problem_type_id,
                "remediation_source": remediation_source,
                "remediation_candidates_considered": list(remediation_candidates_considered),
                "selected_remediation_problem_type_id": selected_remediation_problem_type_id,
                "selected_remediation_skill_id": selected_remediation_skill_id,
                "demo_route_msg": (
                    f"⚠ 補救中（{stage_label}）：第 {remediation_attempt + 1} 題　"
                    f"掌握度 {round(display_apr * 100)}%"
                ),
            }
            if grading_analysis:
                response["grading_analysis"] = grading_analysis
            if payload.get("answer_feedback"):
                response["answer_feedback"] = str(payload["answer_feedback"])
            return response

    # --- Mainline: check completion ---
    if is_b4_chap2_chapter_complete(mainline_step_index):
        resp = _build_completed_response(
            session_id,
            mainline_step_index,
            correct_count=correct_count,
            attempt_count=attempt_count,
            trajectory_history=trajectory_history,
        )
        if grading_analysis:
            resp["grading_analysis"] = grading_analysis
        resp["demo_route_msg"] = "B4 第二章診斷已完成！系統已完整掃描所有 4 個學習階段（10 題）。"
        return resp

    # --- Mainline: generate next question ---
    plan_step = get_plan_step(mainline_step_index)
    if plan_step is None:
        raise ValueError(f"b4_chap2_chapter_mode: invalid mainline_step_index {mainline_step_index}")

    seed = _derive_question_seed(session_id, mainline_step_index)
    question_payload = generate_for_chap2_skill(
        skill_id=plan_step["skill_id"],
        problem_type_id=plan_step["problem_type_id"],
        seed=seed,
        level=1,
        multiple_choice=True,
    )

    question_data = _build_question_data(question_payload, plan_step)
    stage_label = plan_step.get("stage_label", "")
    stage_id = plan_step.get("stage", "")

    # Look ahead for next step info
    next_plan_step = get_plan_step(mainline_step_index + 1)
    next_skill_id = next_plan_step.get("skill_id", "") if next_plan_step else ""
    next_problem_type_id = next_plan_step.get("problem_type_id", "") if next_plan_step else ""

    display_apr = _compute_display_apr(
        step_index=mainline_step_index,
        correct_count=correct_count,
        attempt_count=attempt_count,
    )
    correct_rate = correct_count / max(1, attempt_count) if attempt_count > 0 else 0.0
    progress_pct = round(100.0 * mainline_step_index / B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS, 1)

    response_msg_suffix = ""
    if has_returned_to_main:
        response_msg_suffix = "（已完成補救，返回主線）　"

    response = {
        "session_id": session_id,
        "step_number": mainline_step_index,
        "current_apr": display_apr,
        "ppo_strategy": 1,
        "frustration_index": 0,
        "execution_latency": 0,
        "completed": False,
        "unit_completed": False,
        "assessment_completed": False,
        "mode": "teaching",
        "new_question_data": question_data,
        "target_family_id": plan_step.get("synthetic_family_id", ""),
        "target_subskills": list(question_data.get("subskill_nodes") or []),
        "is_correct": is_correct_this_step if is_answer_submission else None,
        "b4_chap2_chapter_mode": True,
        "chapter_stage": stage_id,
        "chapter_stage_label": stage_label,
        "chapter_total_steps": B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
        "chapter_current_step": mainline_step_index,
        # UI state (Phase 6N-S)
        "completed_steps": attempt_count,
        "total_steps": B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
        "progress_percent": progress_pct,
        "session_correct_count": correct_count,
        "session_attempt_count": attempt_count,
        "session_correct_rate": round(correct_rate, 4),
        "display_mastery_percent": round(display_apr * 100),
        "current_stage": stage_id,
        "current_stage_label": stage_label,
        "current_skill_id": plan_step.get("skill_id", ""),
        "current_problem_type_id": plan_step.get("problem_type_id", ""),
        "next_skill_id": next_skill_id,
        "next_problem_type_id": next_problem_type_id,
        "trajectory_points": trajectory_history,
        # Remediation UI state (Phase 6N-T / 6N-T-R)
        "in_remediation": False,
        "return_ready": return_ready,
        "has_returned_to_main": has_returned_to_main,
        "remediation_reason": remediation_reason,
        "remediation_stage_id": "",
        "remediation_attempt": 0,
        "stage_fail_streak": stage_fail_streak,
        "session_local_fail_streak": stage_fail_streak.get(stage_id, 0),
        "current_strategy": "返回主線" if has_returned_to_main else "主線診斷",
        "display_mode": "mainline",
        # Phase 6N-T-R: failed-stage lock fields (persisted for display even after return)
        "failed_stage": failed_stage,
        "failed_skill_id": failed_skill_id,
        "failed_problem_type_id": failed_problem_type_id,
        "remediation_source": remediation_source,
        "remediation_candidates_considered": list(remediation_candidates_considered),
        "selected_remediation_problem_type_id": selected_remediation_problem_type_id,
        "selected_remediation_skill_id": selected_remediation_skill_id,
        "demo_route_msg": (
            f"診斷進行中{response_msg_suffix}（第 {mainline_step_index + 1}/{B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS} 題）"
            f"：{stage_label}　掌握度 {round(display_apr * 100)}%"
        ),
    }

    if grading_analysis:
        response["grading_analysis"] = grading_analysis
    if payload.get("answer_feedback"):
        response["answer_feedback"] = str(payload["answer_feedback"])

    return response


def build_b4_chap2_chapter_runtime_store_entry(
    response: dict[str, Any],
    step_index: int,
) -> dict[str, Any]:
    """Build the runtime store entry for the current Chap2 chapter question."""
    q = response.get("new_question_data") or {}
    in_remediation = bool(response.get("in_remediation"))
    resume_step = int(response.get("chapter_current_step") or step_index)
    return {
        "family_id": str(response.get("target_family_id") or ""),
        "subskill_nodes": list(response.get("target_subskills") or []),
        "correct_answer": str(q.get("correct_answer") or q.get("answer") or ""),
        "question_text": str(q.get("question_text") or q.get("question") or ""),
        "routing_state": {},
        "skill_id": str(q.get("skill_id") or ""),
        "problem_type_id": str(q.get("problem_type_id") or ""),
        "answer_type": str(q.get("answer_type") or ""),
        # Mainline step tracker (does not advance during remediation)
        "chap2_step_index": step_index,
        "b4_chap2_chapter_mode": True,
        # Session-local counters (display only, no DB write)
        "session_correct_count": int(response.get("session_correct_count") or 0),
        "session_attempt_count": int(response.get("session_attempt_count") or 0),
        "chap2_trajectory_history": list(response.get("trajectory_points") or []),
        # Phase 6N-T: session-local remediation state
        "in_remediation": in_remediation,
        # Phase 6N-T-R: remediation_stage uses explicit remediation_stage_id (not current_stage)
        "remediation_stage": str(response.get("remediation_stage_id") or "") if in_remediation else "",
        "remediation_attempt": int(response.get("remediation_attempt") or 0),
        "resume_step_index": resume_step if in_remediation else step_index,
        "return_ready": bool(response.get("return_ready")),
        "has_returned_to_main": bool(response.get("has_returned_to_main")),
        "remediation_reason": str(response.get("remediation_reason") or ""),
        "stage_fail_streak": dict(response.get("stage_fail_streak") or {}),
        # Phase 6N-T-R: explicit failed-stage lock — never derived from current_stage
        "failed_stage": str(response.get("failed_stage") or ""),
        "failed_skill_id": str(response.get("failed_skill_id") or ""),
        "failed_problem_type_id": str(response.get("failed_problem_type_id") or ""),
        "remediation_source": str(response.get("remediation_source") or ""),
        "remediation_candidates_considered": list(response.get("remediation_candidates_considered") or []),
        "selected_remediation_problem_type_id": str(response.get("selected_remediation_problem_type_id") or ""),
        "selected_remediation_skill_id": str(response.get("selected_remediation_skill_id") or ""),
        "remediation_selected_stage": str(response.get("remediation_stage_id") or "") if in_remediation else "",
    }


def _maybe_write_audit_log(
    *,
    skill_id: str,
    current_question: dict[str, Any],
    user_answer: str,
    is_correct: bool,
    checker_name: str,
) -> None:
    """Write B4Chap2VisibilityAuditLog — silently swallow all errors."""
    try:
        from core.vocational_math_b4.services.b4_chap2_visibility_audit import (
            persist_b4_chap2_deterministic_answer_event,
        )
        persist_b4_chap2_deterministic_answer_event(
            skill_id=skill_id,
            current_question=current_question,
            user_answer=user_answer,
            is_correct=is_correct,
            checker_name=checker_name,
        )
    except Exception:
        pass
