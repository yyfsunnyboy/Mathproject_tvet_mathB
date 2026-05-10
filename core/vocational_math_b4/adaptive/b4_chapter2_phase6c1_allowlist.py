"""
B4 Chapter 2 deterministic adaptive allowlist – Phase 6C-1 + 6C-2 + 6D + 6E + 6F + 6K.

Phase 6C-1 (3 problem types):
    1. classical_probability_fraction  → vh_數學B4_ProbabilityDefinition
    2. complement_probability           → vh_數學B4_ProbabilityProperties
    3. sample_space_count_numeric       → vh_數學B4_SampleSpaceAndEvents

Phase 6C-2 (2 additional problem types):
    4. union_intersection_probability   → vh_數學B4_ProbabilityProperties
    5. dice_coin_probability_count      → vh_數學B4_ProbabilityDefinition

Phase 6D (2 additional problem types):
    6. conditional_probability_basic                   → vh_數學B4_ConditionalProbability
    7. without_replacement_conditional_probability     → vh_數學B4_ConditionalProbability

Phase 6E (2 additional problem types):
    8. independent_joint_probability                   → vh_數學B4_IndependentEvents
    9. independent_at_least_one_probability            → vh_數學B4_IndependentEvents

Phase 6F (2 additional problem types):
    10. expectation_discrete_basic                    → vh_數學B4_MathematicalExpectationDefinition
    11. expectation_from_distribution                 → vh_數學B4_MathematicalExpectationDefinition

Phase 6K (6 additional problem types — remaining deterministic skill coverage):
    12. event_operation_probability                   → vh_數學B4_ProbabilityOperations
    13. probability_algebra_mixed                     → vh_數學B4_ProbabilityOperations
    14. set_operation_count                           → vh_數學B4_BasicConceptsOfSets
    15. inclusion_exclusion_count                     → vh_數學B4_BasicConceptsOfSets
    16. expectation_word_problem_profit_fairness      → vh_數學B4_ApplicationsOfExpectation
    17. expectation_assessment_numeric                → vh_數學B4_MathematicalExpectation

Explicitly excluded (not_ready / handwriting – must NEVER enter this allowlist):
    - sample_space_listing
    - event_set_listing
    - subset_listing
    - tree_diagram_listing

Skills NOT enabled in any phase yet (no legacy fallback permitted):
    (After Phase 6K: empty — Chap2 has no remaining gated runtime skills.)

Note: vh_數學B4_ConditionalProbability, vh_數學B4_IndependentEvents,
      vh_數學B4_MathematicalExpectationDefinition (Phase 6D/6E/6F) and
      vh_數學B4_ProbabilityOperations, vh_數學B4_BasicConceptsOfSets,
      vh_數學B4_ApplicationsOfExpectation, vh_數學B4_MathematicalExpectation
      (Phase 6K) are ENABLED and not in NOT_ENABLED_SKILL_IDS.

Adaptive scoring / mastery / APR / remediation: NOT modified in any phase so far.
"""

from __future__ import annotations

# ─── Chap2 deterministic skill allowlist (6C-1 + 6C-2 + 6D + 6E + 6F + 6K) ────

B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST: frozenset[str] = frozenset(
    {
        "vh_數學B4_ProbabilityDefinition",   # classical_probability_fraction, dice_coin_probability_count
        "vh_數學B4_ProbabilityProperties",   # complement_probability, union_intersection_probability
        "vh_數學B4_SampleSpaceAndEvents",    # sample_space_count_numeric
        # Phase 6D:
        "vh_數學B4_ConditionalProbability",  # conditional_probability_basic, without_replacement_conditional_probability
        # Phase 6E:
        "vh_數學B4_IndependentEvents",       # independent_joint_probability, independent_at_least_one_probability
        # Phase 6F:
        "vh_數學B4_MathematicalExpectationDefinition",  # expectation_discrete_basic, expectation_from_distribution
        # Phase 6K:
        "vh_數學B4_ProbabilityOperations",   # event_operation_probability, probability_algebra_mixed
        "vh_數學B4_BasicConceptsOfSets",     # set_operation_count, inclusion_exclusion_count
        "vh_數學B4_ApplicationsOfExpectation",  # expectation_word_problem_profit_fairness
        "vh_數學B4_MathematicalExpectation",    # expectation_assessment_numeric
    }
)

# All problem types opened across Phase 6C-1, 6C-2, 6D, 6E, 6F, AND 6K
B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES: frozenset[str] = frozenset(
    {
        # Phase 6C-1
        "classical_probability_fraction",
        "complement_probability",
        "sample_space_count_numeric",
        # Phase 6C-2
        "union_intersection_probability",
        "dice_coin_probability_count",
        # Phase 6D
        "conditional_probability_basic",
        "without_replacement_conditional_probability",
        # Phase 6E
        "independent_joint_probability",
        "independent_at_least_one_probability",
        # Phase 6F
        "expectation_discrete_basic",
        "expectation_from_distribution",
        # Phase 6K
        "event_operation_probability",
        "probability_algebra_mixed",
        "set_operation_count",
        "inclusion_exclusion_count",
        "expectation_word_problem_profit_fairness",
        "expectation_assessment_numeric",
    }
)

# Problem types that must NEVER appear in Chap2 deterministic adaptive,
# regardless of what metadata says.
B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES: frozenset[str] = frozenset(
    {
        "sample_space_listing",
        "event_set_listing",
        "subset_listing",
        "tree_diagram_listing",
    }
)

# Curriculum progression order for Chap2 skills (section order)
B4_CHAPTER_2_PHASE6C1_CURRICULUM_PROGRESSION_ORDER: tuple[str, ...] = (
    "vh_數學B4_BasicConceptsOfSets",       # Phase 6K (2-1 集合的基本概念)
    "vh_數學B4_SampleSpaceAndEvents",
    "vh_數學B4_ProbabilityDefinition",
    "vh_數學B4_ProbabilityProperties",
    "vh_數學B4_ProbabilityOperations",     # Phase 6K (2-2 機率的運算)
    "vh_數學B4_ConditionalProbability",   # Phase 6D
    "vh_數學B4_IndependentEvents",       # Phase 6E
    "vh_數學B4_MathematicalExpectationDefinition",  # Phase 6F
    "vh_數學B4_ApplicationsOfExpectation",  # Phase 6K (2-3 數學期望值的應用)
    "vh_數學B4_MathematicalExpectation",    # Phase 6K (2-3 數學期望值 — 自評綜合)
)

# Chap2 skills that MUST NOT fallback to legacy `skills.<skill_id>` import — return a clear gate error.
# Phase 6K closure: this set is now EMPTY for Chap2; all four previously-gated
# skills (BasicConceptsOfSets, ProbabilityOperations, ApplicationsOfExpectation,
# MathematicalExpectation) are now enabled via deterministic generators.
# The constant name is kept for backward compatibility with imports/tests.
B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS: frozenset[str] = frozenset()


def is_b4_chapter2_skill_not_enabled_in_phase6c1(skill_id: str) -> bool:
    """True if Chap2 rollout blocks this skill (no legacy generator import fallback)."""
    sid = str(skill_id or "").strip()
    return sid in B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS


def is_b4_chapter2_phase6c1_deterministic_skill(skill_id: str) -> bool:
    """Return True if skill_id is in the Chap2 deterministic allowlist (6C through 6F)."""
    sid = str(skill_id or "").strip()
    return sid in B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST


def is_b4_chapter2_excluded_problem_type(problem_type_id: str) -> bool:
    """Return True if this problem_type must never enter deterministic runtime."""
    pid = str(problem_type_id or "").strip()
    return pid in B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES


def validate_b4_chap2_phase6c1_generator_payload(
    skill_id: str,
    payload: dict,
) -> tuple[bool, str | None]:
    """Validate that a Chap2 payload is well-formed and in the 6C-1/6C-2/6D allowlist.

    Returns (True, None) on success; (False, reason_str) on failure.
    """
    if not isinstance(payload, dict):
        return False, "payload_not_dict"

    pid = payload.get("problem_type_id")
    if not isinstance(pid, str) or not pid.strip():
        return False, "missing_or_invalid_problem_type_id"

    if pid in B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES:
        return False, f"excluded_handwriting_problem_type:{pid}"

    if pid not in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES:
        return False, f"not_in_phase6c1_allowlist:{pid}"

    sid = str(skill_id or "").strip()
    if sid and sid.startswith("vh_數學B4_"):
        if sid not in B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST:
            return False, f"skill_not_in_phase6c1_allowlist:{sid}"

    return True, None
