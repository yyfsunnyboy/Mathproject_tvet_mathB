"""
B4 Chapter 2 deterministic adaptive allowlist – Phase 6C-1 minimal batch.

Only the following 3 problem types / skills are opened in this phase:

    1. classical_probability_fraction  → vh_數學B4_ProbabilityDefinition
    2. complement_probability           → vh_數學B4_ProbabilityProperties
    3. sample_space_count_numeric       → vh_數學B4_SampleSpaceAndEvents

Explicitly excluded (not_ready / handwriting – must NEVER enter this allowlist):
    - sample_space_listing
    - event_set_listing
    - subset_listing

Adaptive scoring / mastery / APR / remediation: NOT modified in this phase.
"""

from __future__ import annotations

# ─── Chap2 Phase 6C-1 deterministic skill allowlist ─────────────────────────

B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST: frozenset[str] = frozenset(
    {
        "vh_數學B4_ProbabilityDefinition",   # classical_probability_fraction
        "vh_數學B4_ProbabilityProperties",   # complement_probability
        "vh_數學B4_SampleSpaceAndEvents",    # sample_space_count_numeric
    }
)

# Problem types opened in Phase 6C-1
B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES: frozenset[str] = frozenset(
    {
        "classical_probability_fraction",
        "complement_probability",
        "sample_space_count_numeric",
    }
)

# Problem types that must NEVER appear in Chap2 deterministic adaptive,
# regardless of what metadata says.
B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES: frozenset[str] = frozenset(
    {
        "sample_space_listing",
        "event_set_listing",
        "subset_listing",
    }
)

# Curriculum progression order for Chap2 Phase 6C-1 skills (section order)
B4_CHAPTER_2_PHASE6C1_CURRICULUM_PROGRESSION_ORDER: tuple[str, ...] = (
    "vh_數學B4_SampleSpaceAndEvents",
    "vh_數學B4_ProbabilityDefinition",
    "vh_數學B4_ProbabilityProperties",
)

# Chap2 skills that MUST NOT fallback to legacy `skills.<skill_id>` import in Phase 6C-1R2 — return a clear gate error instead.
B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS: frozenset[str] = frozenset(
    {
        "vh_數學B4_BasicConceptsOfSets",
        "vh_數學B4_ConditionalProbability",
        "vh_數學B4_IndependentEvents",
        "vh_數學B4_ProbabilityOperations",
        "vh_數學B4_MathematicalExpectationDefinition",
        "vh_數學B4_ApplicationsOfExpectation",
        "vh_數學B4_MathematicalExpectation",
    }
)


def is_b4_chapter2_skill_not_enabled_in_phase6c1(skill_id: str) -> bool:
    """True if Chap2 rollout blocks this skill (no legacy generator import fallback)."""
    sid = str(skill_id or "").strip()
    return sid in B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS


def is_b4_chapter2_phase6c1_deterministic_skill(skill_id: str) -> bool:
    """Return True if skill_id is in the Chap2 Phase 6C-1 deterministic allowlist."""
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
    """Validate that a Chap2 Phase 6C-1 payload is well-formed and allowlisted.

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
        return False, f"problem_type_not_in_phase6c1_allowlist:{pid}"

    sid = str(skill_id or "").strip()
    if sid and sid.startswith("vh_數學B4_"):
        if sid not in B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST:
            return False, f"skill_not_in_phase6c1_allowlist:{sid}"

    return True, None
