"""Phase 6C-2R: Practice smoke regression tests.

Root cause: frontend getSkillId() in index.html extracted the URL path segment
(e.g. vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition) and passed it through
URLSearchParams.set(), which percent-encodes the value again → double-encoded.
The server's _url_unquote() only decoded one level, leaving it still encoded.

Fix: added decodeURIComponent() in frontend getSkillId() before setting params.
Backend _url_unquote is unchanged and handles any remaining encoding correctly.

Tests here cover:
  1. URL decode round-trips (server-side)
  2. 6C-1 + 6C-2 skills produce payloads via generate_for_chap2_skill
  3. Not-enabled skills return correct gate errors
  4. Excluded problem types are blocked
  5. check_rational_answer / check_integer_answer checker paths
  6. Chap1 regression unaffected
"""
from __future__ import annotations

import math
import pytest
from fractions import Fraction
from urllib.parse import unquote as _url_unquote, quote as _url_quote

from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
    is_b4_chapter2_phase6c1_deterministic_skill,
    is_b4_chapter2_skill_not_enabled_in_phase6c1,
    is_b4_chapter2_excluded_problem_type,
    validate_b4_chap2_phase6c1_generator_payload,
    B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES,
)
from core.vocational_math_b4.domain.b4_validators import (
    check_rational_answer,
    check_integer_answer,
)

SKILL_DEF   = "vh_數學B4_ProbabilityDefinition"
SKILL_PROP  = "vh_數學B4_ProbabilityProperties"
SKILL_SSE   = "vh_數學B4_SampleSpaceAndEvents"

ENCODED_DEF  = "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition"
ENCODED_PROP = "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityProperties"
ENCODED_SSE  = "vh_%E6%95%B8%E5%AD%B8B4_SampleSpaceAndEvents"

# Phase 6K closure: the Chap2 not-enabled set is now empty.
# These IDs are the historical "blocked" set, kept here only so the
# parametrized regressions below can re-assert the inverted state
# (now enabled, no legacy fallback). Direct gating is exercised through
# B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS below.
HISTORICALLY_BLOCKED_SKILLS = [
    "vh_數學B4_BasicConceptsOfSets",
    "vh_數學B4_ProbabilityOperations",
    "vh_數學B4_ApplicationsOfExpectation",
    "vh_數學B4_MathematicalExpectation",
]

HISTORICALLY_ENCODED_BLOCKED = [
    "vh_%E6%95%B8%E5%AD%B8B4_BasicConceptsOfSets",
    "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityOperations",
    "vh_%E6%95%B8%E5%AD%B8B4_ApplicationsOfExpectation",
    "vh_%E6%95%B8%E5%AD%B8B4_MathematicalExpectation",
]

# Backward-compatible aliases retained for any downstream test references;
# both are intentionally empty after Phase 6K opened the remaining 4 skills.
BLOCKED_SKILLS: list[str] = []
ENCODED_BLOCKED: set[str] = set()


# ═══ A. URL decode round-trip (server-side) ════════════════════════════════

class TestUrlDecodeRoundTrip:
    """Simulates what practice.py's _url_unquote() does at the backend."""

    @pytest.mark.parametrize("encoded,expected", [
        (ENCODED_DEF,  SKILL_DEF),
        (ENCODED_PROP, SKILL_PROP),
        (ENCODED_SSE,  SKILL_SSE),
        # already decoded → unchanged
        (SKILL_DEF, SKILL_DEF),
        (SKILL_PROP, SKILL_PROP),
        (SKILL_SSE, SKILL_SSE),
        # Blocked skill encoded → decoded
        ("vh_%E6%95%B8%E5%AD%B8B4_BasicConceptsOfSets",
         "vh_數學B4_BasicConceptsOfSets"),
        ("vh_%E6%95%B8%E5%AD%B8B4_ConditionalProbability",
         "vh_數學B4_ConditionalProbability"),
        ("vh_%E6%95%B8%E5%AD%B8B4_IndependentEvents",
         "vh_數學B4_IndependentEvents"),
    ])
    def test_single_decode(self, encoded, expected):
        assert _url_unquote(encoded) == expected

    def test_double_encode_single_decode_fails(self):
        """Reproduces the original bug: double-encoded string only partially decodes."""
        double_encoded = _url_quote(ENCODED_DEF, safe="")
        # One decode → back to single-encoded (still not readable skill_id)
        once = _url_unquote(double_encoded)
        assert once == ENCODED_DEF  # still encoded
        assert once != SKILL_DEF    # not yet the readable form

    def test_frontend_decode_then_reencoded_backend_decode(self):
        """Simulates fixed frontend: decodeURIComponent → URLSearchParams encodes once → backend unquote."""
        # Frontend: decodeURIComponent(ENCODED_DEF) → plain CJK string
        frontend_decoded = _url_unquote(ENCODED_DEF)  # equivalent to JS decodeURIComponent
        assert frontend_decoded == SKILL_DEF

        # URLSearchParams.set('skill', frontend_decoded) encodes CJK → single-encoded
        re_encoded = _url_quote(frontend_decoded, safe="")
        # Backend _url_unquote → plain skill_id
        backend_result = _url_unquote(re_encoded)
        assert backend_result == SKILL_DEF

    def test_idempotent_on_plain(self):
        """Already-decoded ids survive encode → decode cycle."""
        for sid in [SKILL_DEF, SKILL_PROP, SKILL_SSE]:
            re_enc = _url_quote(sid, safe="")
            assert _url_unquote(re_enc) == sid


# ═══ B. encoded → decoded → skill recognized ════════════════════════════════

class TestEncodedSkillRecognized:
    """After decode, Chap2 P0 skills must be recognized by allowlist."""

    @pytest.mark.parametrize("encoded,expected_decoded", [
        (ENCODED_DEF, SKILL_DEF),
        (ENCODED_PROP, SKILL_PROP),
        (ENCODED_SSE, SKILL_SSE),
    ])
    def test_decoded_recognized_as_chap2_p0(self, encoded, expected_decoded):
        decoded = _url_unquote(encoded)
        assert decoded == expected_decoded
        assert is_b4_chapter2_phase6c1_deterministic_skill(decoded)

    @pytest.mark.parametrize("encoded", HISTORICALLY_ENCODED_BLOCKED)
    def test_decoded_blocked_skills_recognized_as_not_enabled(self, encoded):
        # Phase 6K: the four historically-blocked Chap2 skills are now
        # in the deterministic allowlist and no longer in the not-enabled set.
        decoded = _url_unquote(encoded)
        assert is_b4_chapter2_skill_not_enabled_in_phase6c1(decoded) is False
        assert is_b4_chapter2_phase6c1_deterministic_skill(decoded) is True

    def test_encoded_skill_not_directly_recognized(self):
        """Without decode, encoded skill_id must NOT pass the allowlist."""
        assert not is_b4_chapter2_phase6c1_deterministic_skill(ENCODED_DEF)
        assert not is_b4_chapter2_phase6c1_deterministic_skill(ENCODED_PROP)
        assert not is_b4_chapter2_phase6c1_deterministic_skill(ENCODED_SSE)


# ═══ C. Generator can produce questions for all 5 problem types ═════════════

class TestGeneratorSmoke:
    """Simulates what next_question() does after decode."""

    @pytest.mark.parametrize("skill_id,pid", [
        # 6C-1
        (SKILL_DEF,  "classical_probability_fraction"),
        (SKILL_PROP, "complement_probability"),
        (SKILL_SSE,  "sample_space_count_numeric"),
        # 6C-2
        (SKILL_DEF,  "dice_coin_probability_count"),
        (SKILL_PROP, "union_intersection_probability"),
    ])
    def test_payload_generated(self, skill_id, pid):
        p = generate_for_chap2_skill(skill_id=skill_id, problem_type_id=pid, seed=42)
        assert p["problem_type_id"] == pid
        assert p["skill_id"] == skill_id
        assert p["question_text"].strip()
        assert p["answer_type"] not in ("handwriting", "ai_judged_free_response")

    @pytest.mark.parametrize("skill_id,pid", [
        (SKILL_DEF,  "classical_probability_fraction"),
        (SKILL_PROP, "complement_probability"),
        (SKILL_SSE,  "sample_space_count_numeric"),
        (SKILL_DEF,  "dice_coin_probability_count"),
        (SKILL_PROP, "union_intersection_probability"),
    ])
    def test_payload_passes_allowlist_gate(self, skill_id, pid):
        p = generate_for_chap2_skill(skill_id=skill_id, problem_type_id=pid, seed=7)
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(skill_id, p)
        assert ok is True, f"Blocked: {reason}"

    @pytest.mark.parametrize("encoded,pid", [
        (ENCODED_DEF,  "classical_probability_fraction"),
        (ENCODED_PROP, "complement_probability"),
        (ENCODED_SSE,  "sample_space_count_numeric"),
        (ENCODED_DEF,  "dice_coin_probability_count"),
        (ENCODED_PROP, "union_intersection_probability"),
    ])
    def test_encoded_then_decoded_generates_correctly(self, encoded, pid):
        """Simulate the fixed flow: frontend decode → reencoded → backend unquote."""
        decoded_skill = _url_unquote(encoded)
        p = generate_for_chap2_skill(skill_id=decoded_skill, problem_type_id=pid, seed=1)
        assert p["problem_type_id"] == pid
        assert p["skill_id"] == decoded_skill


# ═══ D. Not-enabled skills gate ══════════════════════════════════════════════

class TestNotEnabledGate:
    """Phase 6K: previously-blocked Chap2 skills are now enabled via deterministic generators."""

    @pytest.mark.parametrize("skill_id", HISTORICALLY_BLOCKED_SKILLS)
    def test_blocked_skills_recognized(self, skill_id):
        # Phase 6K: now enabled, gate must be False.
        assert is_b4_chapter2_skill_not_enabled_in_phase6c1(skill_id) is False
        assert is_b4_chapter2_phase6c1_deterministic_skill(skill_id) is True

    @pytest.mark.parametrize("encoded", HISTORICALLY_ENCODED_BLOCKED)
    def test_encoded_blocked_skills_recognized_after_decode(self, encoded):
        decoded = _url_unquote(encoded)
        # Phase 6K: now enabled.
        assert is_b4_chapter2_skill_not_enabled_in_phase6c1(decoded) is False
        assert is_b4_chapter2_phase6c1_deterministic_skill(decoded) is True

    @pytest.mark.parametrize("skill_id", [SKILL_DEF, SKILL_PROP, SKILL_SSE])
    def test_p0_skills_not_blocked(self, skill_id):
        assert is_b4_chapter2_skill_not_enabled_in_phase6c1(skill_id) is False

    @pytest.mark.parametrize("skill_id", HISTORICALLY_BLOCKED_SKILLS)
    def test_historically_blocked_skill_now_generates(self, skill_id):
        """Phase 6K: router must successfully generate for the historically blocked skills."""
        p = generate_for_chap2_skill(skill_id=skill_id, seed=11)
        assert p["skill_id"] == skill_id
        assert p["question_text"].strip()
        assert p["answer_type"] not in ("handwriting", "ai_judged_free_response")

    def test_chap2_not_enabled_set_is_empty(self):
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS,
        )
        assert B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS == frozenset()

    def test_truly_unsupported_skill_raises_in_router(self):
        with pytest.raises(ValueError, match="unsupported skill_id"):
            generate_for_chap2_skill(skill_id="vh_數學B4_NoSuchSkill")

    def test_error_message_uses_decoded_skill_id(self):
        """Error message must show decoded skill_id, not percent-encoded."""
        try:
            generate_for_chap2_skill(skill_id="vh_數學B4_NotARealSkill")
        except ValueError as e:
            err_msg = str(e)
            assert "vh_%E6%95%B8%E5%AD%B8B4" not in err_msg
            assert "NotARealSkill" in err_msg


# ═══ E. Excluded problem types blocked ═══════════════════════════════════════

class TestExcludedProblemTypes:
    @pytest.mark.parametrize("pid", ["sample_space_listing", "event_set_listing", "subset_listing"])
    def test_handwriting_excluded(self, pid):
        assert is_b4_chapter2_excluded_problem_type(pid) is True

    @pytest.mark.parametrize("pid", list(B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES))
    def test_allowed_types_not_excluded(self, pid):
        assert is_b4_chapter2_excluded_problem_type(pid) is False

    @pytest.mark.parametrize("pid", ["sample_space_listing", "event_set_listing", "subset_listing"])
    def test_validate_blocks_handwriting(self, pid):
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(
            SKILL_SSE, {"problem_type_id": pid}
        )
        assert ok is False
        assert "excluded_handwriting" in reason

    def test_sample_space_listing_not_in_router(self):
        with pytest.raises(ValueError):
            generate_for_chap2_skill(skill_id=SKILL_SSE, problem_type_id="sample_space_listing")


# ═══ F. check_answer path ════════════════════════════════════════════════════

class TestCheckAnswerPath:
    """Simulates check_answer() checker for rational and integer types."""

    # -- rational (classical / complement / union / dice) --

    def test_rational_fraction_correct(self):
        assert check_rational_answer("1/2", 1, 2) is True

    def test_rational_unreduced_correct(self):
        assert check_rational_answer("2/4", 1, 2) is True

    def test_rational_decimal_correct(self):
        assert check_rational_answer("0.5", 1, 2) is True

    def test_rational_percentage_correct(self):
        assert check_rational_answer("50%", 1, 2) is True

    def test_rational_wrong(self):
        assert check_rational_answer("3/4", 1, 2) is False

    def test_rational_empty(self):
        assert check_rational_answer("", 1, 2) is False

    def test_rational_none(self):
        assert check_rational_answer(None, 1, 2) is False

    # -- integer (sample_space_count_numeric) --

    def test_integer_correct(self):
        assert check_integer_answer("36", 36) is True

    def test_integer_int_correct(self):
        assert check_integer_answer(36, 36) is True

    def test_integer_decimal_wrong(self):
        assert check_integer_answer("36.0", 36) is False

    def test_integer_percentage_wrong(self):
        assert check_integer_answer("36%", 36) is False

    def test_integer_wrong_value(self):
        assert check_integer_answer("35", 36) is False

    # -- round-trip with real payload --

    @pytest.mark.parametrize("pid,skill_id", [
        ("classical_probability_fraction", SKILL_DEF),
        ("complement_probability", SKILL_PROP),
        ("union_intersection_probability", SKILL_PROP),
        ("dice_coin_probability_count", SKILL_DEF),
    ])
    def test_rational_round_trip(self, pid, skill_id):
        p = generate_for_chap2_skill(skill_id=skill_id, problem_type_id=pid, seed=10)
        ans = p["answer"]
        if "/" in ans:
            n, d = map(int, ans.split("/"))
        else:
            n, d = int(ans), 1
        assert check_rational_answer(ans, n, d) is True
        assert check_rational_answer("ZZZ", n, d) is False

    def test_integer_round_trip(self):
        p = generate_for_chap2_skill(
            skill_id=SKILL_SSE, problem_type_id="sample_space_count_numeric", seed=10
        )
        ans = p["answer"]
        assert check_integer_answer(str(ans), int(ans)) is True
        assert check_integer_answer(f"{ans}.0", int(ans)) is False
        assert check_integer_answer(f"{ans}%", int(ans)) is False


# ═══ G. Chap1 regression ════════════════════════════════════════════════════

class TestChap1Regression:
    def test_chap1_allowlist_size_unchanged(self):
        from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
            B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
        )
        assert len(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST) == 13

    def test_chap1_router_works(self):
        from core.vocational_math_b4.services.question_router import generate_for_skill
        p = generate_for_skill(skill_id="vh_數學B4_AdditionPrinciple", level=1, seed=1)
        assert p["skill_id"] == "vh_數學B4_AdditionPrinciple"

    def test_chap2_skills_not_in_chap1_allowlist(self):
        from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
            B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
        )
        chap2 = {SKILL_DEF, SKILL_PROP, SKILL_SSE}
        assert not (chap2 & B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST)

    def test_chap1_generate_for_skill_multiple_skills(self):
        from core.vocational_math_b4.services.question_router import generate_for_skill
        for sid in ["vh_數學B4_AdditionPrinciple",
                    "vh_數學B4_CombinationDefinition",
                    "vh_數學B4_BinomialTheorem"]:
            p = generate_for_skill(skill_id=sid, level=1, seed=99)
            assert p["skill_id"] == sid
            assert p["question_text"].strip()


# ═══ H. Chap2 mainline allowlist (6C through 6F) ═════════════════════════════

class TestAllowlistIntegrity:
    def test_mainline_problem_types_count(self):
        # Phase 6K closure: 6C-1 (3) + 6C-2 (2) + 6D (2) + 6E (2) + 6F (2) + 6K (6) = 17.
        assert len(B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES) == 17

    def test_6c1_types_present(self):
        for pid in ["classical_probability_fraction",
                    "complement_probability",
                    "sample_space_count_numeric"]:
            assert pid in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES

    def test_6c2_types_present(self):
        for pid in ["union_intersection_probability", "dice_coin_probability_count"]:
            assert pid in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES

    def test_6d_conditional_types_present(self):
        for pid in [
            "conditional_probability_basic",
            "without_replacement_conditional_probability",
        ]:
            assert pid in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES

    def test_6e_independent_types_present(self):
        for pid in [
            "independent_joint_probability",
            "independent_at_least_one_probability",
        ]:
            assert pid in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES

    def test_6f_expectation_types_present(self):
        for pid in ["expectation_discrete_basic", "expectation_from_distribution"]:
            assert pid in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES
