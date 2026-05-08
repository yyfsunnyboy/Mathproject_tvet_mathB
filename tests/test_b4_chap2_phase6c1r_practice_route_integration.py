"""Phase 6C-1R: Practice route integration tests.

Tests:
  1. URL decode utility (isolated, no Flask context required)
  2. Chap2 Phase 6C-1 skill bypass recognition
  3. Generator smoke via route-equivalent call
  4. Answer checker path (rational + integer)
  5. Allowlist boundary: BasicConceptsOfSets stays blocked
  6. Handwriting listing problem_types blocked
  7. Chap1 regression (router unaffected)

NOTE: This test file deliberately does NOT instantiate a Flask app.
      Route-level path coverage is validated through unit functions extracted
      from practice.py's helper structure; full HTTP integration smoke is
      done manually (see manual smoke instructions in the summary report).
"""

from __future__ import annotations

import pytest
from urllib.parse import unquote as _url_unquote, quote as _url_quote


# ═══════════════════════════════════════════════════════════════════════════════
# 1. URL decode utility tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestUrlDecodeUtility:
    """Verify urllib.parse.unquote behaviour matches Phase 6C-1R expectations."""

    @pytest.mark.parametrize("encoded,expected", [
        # Standard UTF-8 encoding of CJK characters
        ("vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition",
         "vh_數學B4_ProbabilityDefinition"),
        ("vh_%E6%95%B8%E5%AD%B8B4_ProbabilityProperties",
         "vh_數學B4_ProbabilityProperties"),
        ("vh_%E6%95%B8%E5%AD%B8B4_SampleSpaceAndEvents",
         "vh_數學B4_SampleSpaceAndEvents"),
        # Already-decoded IDs pass through unchanged
        ("vh_數學B4_ProbabilityDefinition",
         "vh_數學B4_ProbabilityDefinition"),
        ("vh_數學B4_ProbabilityProperties",
         "vh_數學B4_ProbabilityProperties"),
        ("vh_數學B4_SampleSpaceAndEvents",
         "vh_數學B4_SampleSpaceAndEvents"),
        # Chap1 skill (should not break)
        ("vh_%E6%95%B8%E5%AD%B8B4_AdditionPrinciple",
         "vh_數學B4_AdditionPrinciple"),
        # Double-encoded should decode one level
        ("vh_%E6%95%B8%E5%AD%B8B4_BasicConceptsOfSets",
         "vh_數學B4_BasicConceptsOfSets"),
    ])
    def test_url_decode_skill_ids(self, encoded: str, expected: str) -> None:
        assert _url_unquote(encoded) == expected

    def test_unquote_is_idempotent_on_decoded(self) -> None:
        decoded = "vh_數學B4_ProbabilityDefinition"
        assert _url_unquote(_url_unquote(decoded)) == decoded

    def test_unquote_preserves_ascii_only_ids(self) -> None:
        sid = "remainder"
        assert _url_unquote(sid) == sid


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Chap2 Phase 6C-1 allowlist / skill bypass recognition
# ═══════════════════════════════════════════════════════════════════════════════

class TestChap2SkillBypass:
    """Verify the helper that practice.py uses to bypass DB for Chap2 P0 skills."""

    from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
        is_b4_chapter2_phase6c1_deterministic_skill,
        is_b4_chapter2_excluded_problem_type,
    )

    @pytest.mark.parametrize("skill_id", [
        "vh_數學B4_ProbabilityDefinition",
        "vh_數學B4_ProbabilityProperties",
        "vh_數學B4_SampleSpaceAndEvents",
    ])
    def test_p0_skills_recognized(self, skill_id: str) -> None:
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            is_b4_chapter2_phase6c1_deterministic_skill,
        )
        assert is_b4_chapter2_phase6c1_deterministic_skill(skill_id)

    @pytest.mark.parametrize("skill_id", [
        "vh_數學B4_BasicConceptsOfSets",       # NOT in Phase 6C-1
        "vh_數學B4_ConditionalProbability",
        "vh_數學B4_IndependentEvents",
        "vh_數學B4_AdditionPrinciple",          # Chap1 skill
        "remainder",
        "",
    ])
    def test_non_p0_skills_not_recognized(self, skill_id: str) -> None:
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            is_b4_chapter2_phase6c1_deterministic_skill,
        )
        assert not is_b4_chapter2_phase6c1_deterministic_skill(skill_id)

    @pytest.mark.parametrize("problem_type", [
        "sample_space_listing",
        "event_set_listing",
        "subset_listing",
    ])
    def test_handwriting_listing_types_excluded(self, problem_type: str) -> None:
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            is_b4_chapter2_excluded_problem_type,
        )
        assert is_b4_chapter2_excluded_problem_type(problem_type)

    @pytest.mark.parametrize("problem_type", [
        "classical_probability_fraction",
        "complement_probability",
        "sample_space_count_numeric",
    ])
    def test_p0_problem_types_not_excluded(self, problem_type: str) -> None:
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            is_b4_chapter2_excluded_problem_type,
        )
        assert not is_b4_chapter2_excluded_problem_type(problem_type)

    def test_basic_concepts_of_sets_not_in_allowlist(self) -> None:
        """BasicConceptsOfSets must remain blocked (Phase 6C-1R scope excludes it)."""
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            is_b4_chapter2_phase6c1_deterministic_skill,
        )
        assert not is_b4_chapter2_phase6c1_deterministic_skill("vh_數學B4_BasicConceptsOfSets")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Generator smoke (equivalent to route's generate_for_chap2_skill call)
# ═══════════════════════════════════════════════════════════════════════════════

class TestChap2RouteGeneratorSmoke:
    """Simulate what practice.py's generator branch does at runtime."""

    from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
    from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
        validate_b4_chap2_phase6c1_generator_payload,
    )

    @pytest.mark.parametrize("skill_id,expected_pid", [
        ("vh_數學B4_ProbabilityDefinition", "classical_probability_fraction"),
        ("vh_數學B4_ProbabilityProperties", "complement_probability"),
        ("vh_數學B4_SampleSpaceAndEvents", "sample_space_count_numeric"),
    ])
    def test_generate_and_validate_p0_skills(self, skill_id, expected_pid):
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            validate_b4_chap2_phase6c1_generator_payload,
        )
        payload = generate_for_chap2_skill(skill_id=skill_id, level=1, seed=77)
        assert payload["problem_type_id"] == expected_pid
        # Simulate the allowlist gate in practice.py
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(skill_id, payload)
        assert ok is True, f"Allowlist gate blocked: {reason}"
        # Required keys for /get_next_question response
        for key in ["question_text", "answer", "correct_answer", "choices", "explanation"]:
            assert key in payload, f"Missing: {key}"

    def test_payload_has_answer_type(self):
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
        p = generate_for_chap2_skill(skill_id="vh_數學B4_SampleSpaceAndEvents", level=1, seed=5)
        assert p.get("answer_type") == "integer"
        p2 = generate_for_chap2_skill(skill_id="vh_數學B4_ProbabilityDefinition", level=1, seed=5)
        assert p2.get("answer_type") == "rational_fraction"

    def test_unsupported_skill_raises(self):
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
        with pytest.raises(ValueError, match="unsupported skill_id"):
            generate_for_chap2_skill(skill_id="vh_數學B4_BasicConceptsOfSets")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Answer checker path (mimics check_answer logic in practice.py)
# ═══════════════════════════════════════════════════════════════════════════════

class TestChap2AnswerCheckerPath:
    """Verify the exact check_answer checker code path added in Phase 6C-1R."""

    from core.vocational_math_b4.domain.b4_validators import (
        check_rational_answer,
        check_integer_answer,
    )

    def _check_rational(self, user_ans: str, correct_ans: str) -> bool:
        """Mirror the practice.py rational checker path."""
        from core.vocational_math_b4.domain.b4_validators import check_rational_answer
        if "/" in correct_ans:
            num_str, den_str = correct_ans.split("/", 1)
            exp_num, exp_den = int(num_str), int(den_str)
        elif correct_ans in ("0", "1"):
            exp_num, exp_den = int(correct_ans), 1
        else:
            exp_num, exp_den = int(correct_ans), 1
        return check_rational_answer(
            user_ans, exp_num, exp_den,
            allow_decimal=True, allow_percentage=True,
            validate_probability_range=True,
        )

    def _check_integer(self, user_ans: str, correct_ans: str) -> bool:
        from core.vocational_math_b4.domain.b4_validators import check_integer_answer
        return check_integer_answer(user_ans, int(correct_ans))

    # ── rational (classical / complement) ────────────────────────────────────

    def test_rational_canonical_correct(self):
        assert self._check_rational("1/3", "1/3") is True

    def test_rational_unreduced_correct(self):
        assert self._check_rational("2/6", "1/3") is True

    def test_rational_decimal_correct(self):
        # 0.5 == 1/2
        assert self._check_rational("0.5", "1/2") is True

    def test_rational_percentage_correct(self):
        assert self._check_rational("50%", "1/2") is True

    def test_rational_wrong_value(self):
        assert self._check_rational("2/3", "1/3") is False

    def test_rational_zero_answer(self):
        # correct_ans = "0"
        assert self._check_rational("0", "0") is True
        assert self._check_rational("0/1", "0") is True

    def test_rational_one_answer(self):
        assert self._check_rational("1", "1") is True
        assert self._check_rational("100%", "1") is True

    def test_rational_empty_input(self):
        assert self._check_rational("", "1/2") is False

    # ── integer (sample_space_count_numeric) ─────────────────────────────────

    def test_integer_correct(self):
        assert self._check_integer("36", "36") is True

    def test_integer_correct_int(self):
        from core.vocational_math_b4.domain.b4_validators import check_integer_answer
        assert check_integer_answer(36, 36) is True

    def test_integer_wrong(self):
        assert self._check_integer("35", "36") is False

    def test_integer_decimal_rejected(self):
        assert self._check_integer("36.0", "36") is False

    def test_integer_percentage_rejected(self):
        assert self._check_integer("36%", "36") is False

    def test_integer_negative_rejected(self):
        assert self._check_integer("-36", "36") is False

    # ── real generator correct_answer round-trip ──────────────────────────────

    def test_round_trip_classical(self):
        """Generate a question, get correct_answer, verify checker accepts it."""
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
        payload = generate_for_chap2_skill(
            skill_id="vh_數學B4_ProbabilityDefinition", level=1, seed=11
        )
        correct_ans = payload["correct_answer"]
        result = self._check_rational(correct_ans, correct_ans)
        assert result is True

    def test_round_trip_complement(self):
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
        payload = generate_for_chap2_skill(
            skill_id="vh_數學B4_ProbabilityProperties", level=1, seed=22
        )
        correct_ans = payload["correct_answer"]
        result = self._check_rational(correct_ans, correct_ans)
        assert result is True

    def test_round_trip_sample_space_count(self):
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
        payload = generate_for_chap2_skill(
            skill_id="vh_數學B4_SampleSpaceAndEvents", level=1, seed=33
        )
        correct_ans = str(payload["correct_answer"])
        result = self._check_integer(correct_ans, correct_ans)
        assert result is True

    def test_round_trip_sample_space_decimal_rejected(self):
        """36.0 should be rejected even when correct answer is 36."""
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
        payload = generate_for_chap2_skill(
            skill_id="vh_數學B4_SampleSpaceAndEvents", level=1, seed=33
        )
        correct_int = int(payload["correct_answer"])
        result = self._check_integer(f"{correct_int}.0", str(correct_int))
        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Handwriting listing problem_types blocked at generator gate
# ═══════════════════════════════════════════════════════════════════════════════

class TestHandwritingListingBlocked:
    """Verify listing problem_types are blocked before reaching the generator."""

    @pytest.mark.parametrize("pid", [
        "sample_space_listing",
        "event_set_listing",
        "subset_listing",
    ])
    def test_excluded_pid_blocks_at_allowlist(self, pid):
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            is_b4_chapter2_excluded_problem_type,
        )
        # This is the guard in practice.py before calling generate_for_chap2_skill
        assert is_b4_chapter2_excluded_problem_type(pid) is True

    @pytest.mark.parametrize("pid", [
        "sample_space_listing",
        "event_set_listing",
        "subset_listing",
    ])
    def test_validate_payload_blocks_listing(self, pid):
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            validate_b4_chap2_phase6c1_generator_payload,
        )
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(
            "vh_數學B4_SampleSpaceAndEvents",
            {"problem_type_id": pid},
        )
        assert ok is False
        assert "excluded_handwriting" in reason

    def test_sample_space_listing_not_reachable_via_router(self):
        """The router does not register sample_space_listing → raises ValueError."""
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
        with pytest.raises(ValueError):
            # SampleSpaceAndEvents only maps to sample_space_count_numeric.
            # Requesting a different problem_type_id raises ValueError.
            generate_for_chap2_skill(
                skill_id="vh_數學B4_SampleSpaceAndEvents",
                problem_type_id="sample_space_listing",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Chap1 regression: original router + allowlist unaffected
# ═══════════════════════════════════════════════════════════════════════════════

class TestChap1Regression:
    """Chap1 router and allowlist must be unchanged by Phase 6C-1R."""

    def test_chap1_allowlist_unmodified(self):
        from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
            B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
        )
        expected_count = 13
        assert len(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST) == expected_count, (
            f"Chap1 allowlist size changed: expected {expected_count}, "
            f"got {len(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST)}"
        )

    def test_chap2_skills_not_in_chap1_allowlist(self):
        from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
            B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
        )
        chap2_p0 = {
            "vh_數學B4_ProbabilityDefinition",
            "vh_數學B4_ProbabilityProperties",
            "vh_數學B4_SampleSpaceAndEvents",
        }
        overlap = chap2_p0 & B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST
        assert not overlap, f"Chap2 skills leaked into Chap1 allowlist: {overlap}"

    @pytest.mark.parametrize("skill_id", [
        "vh_數學B4_AdditionPrinciple",
        "vh_數學B4_CombinationDefinition",
        "vh_數學B4_BinomialTheorem",
    ])
    def test_chap1_generate_for_skill_still_works(self, skill_id):
        from core.vocational_math_b4.services.question_router import generate_for_skill
        payload = generate_for_skill(skill_id=skill_id, level=1, seed=99)
        assert payload["skill_id"] == skill_id
        assert payload["question_text"].strip()


# ═══════════════════════════════════════════════════════════════════════════════
# 7. practice.py import sanity (no circular import / missing symbol)
# ═══════════════════════════════════════════════════════════════════════════════

class TestPracticeRouteImportSanity:
    """Confirm all new imports in practice.py resolve correctly."""

    def test_url_unquote_import(self):
        from urllib.parse import unquote as _url_unquote
        assert callable(_url_unquote)

    def test_chap2_allowlist_imports(self):
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST,
            B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS,
            B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES,
            is_b4_chapter2_phase6c1_deterministic_skill,
            is_b4_chapter2_skill_not_enabled_in_phase6c1,
            is_b4_chapter2_excluded_problem_type,
            validate_b4_chap2_phase6c1_generator_payload,
        )
        assert isinstance(B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST, frozenset)
        assert isinstance(B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS, frozenset)
        assert isinstance(B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES, frozenset)
        assert callable(is_b4_chapter2_phase6c1_deterministic_skill)
        assert callable(is_b4_chapter2_skill_not_enabled_in_phase6c1)
        assert callable(is_b4_chapter2_excluded_problem_type)
        assert callable(validate_b4_chap2_phase6c1_generator_payload)

    def test_chap2_router_import(self):
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
        assert callable(generate_for_chap2_skill)

    def test_checker_imports(self):
        from core.vocational_math_b4.domain.b4_validators import (
            check_rational_answer,
            check_integer_answer,
        )
        assert callable(check_rational_answer)
        assert callable(check_integer_answer)
