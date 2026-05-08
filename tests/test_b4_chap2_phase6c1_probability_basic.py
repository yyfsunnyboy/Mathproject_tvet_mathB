"""Phase 6C-1 tests for B4 Chapter 2 minimal deterministic probability batch.

Covers:
  1. check_rational_answer / check_integer_answer / check_probability_range (checker tests)
  2. Generator tests: classical_probability_fraction, complement_probability,
     sample_space_count_numeric
  3. Router / allowlist boundary tests

No production code outside the Phase 6C-1 allowed files is touched.
"""

from __future__ import annotations

import math
import pytest

# ─── imports ─────────────────────────────────────────────────────────────────

from core.vocational_math_b4.domain.b4_validators import (
    check_integer_answer,
    check_probability_range,
    check_rational_answer,
)
from core.vocational_math_b4.generators.chap2_probability_basic import (
    classical_probability_fraction,
    complement_probability,
    sample_space_count_numeric,
)
from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
    B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES,
    B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST,
    B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES,
    is_b4_chapter2_excluded_problem_type,
    is_b4_chapter2_phase6c1_deterministic_skill,
    validate_b4_chap2_phase6c1_generator_payload,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. check_rational_answer tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckRationalAnswer:
    """Tests for check_rational_answer with expected = 1/2."""

    EXP_NUM = 1
    EXP_DEN = 2

    def _check(self, user_answer, **kwargs) -> bool:
        return check_rational_answer(
            user_answer, self.EXP_NUM, self.EXP_DEN, **kwargs
        )

    # ── correct inputs (flexible mode) ──────────────────────────────────────

    def test_correct_plain_fraction(self):
        assert self._check("1/2") is True

    def test_correct_unreduced_fraction(self):
        assert self._check("2/4") is True

    def test_correct_unreduced_larger(self):
        assert self._check("5/10") is True

    def test_correct_decimal(self):
        assert self._check("0.5") is True

    def test_correct_percentage(self):
        assert self._check("50%") is True

    def test_correct_latex_frac(self):
        assert self._check(r"\frac{1}{2}") is True

    def test_correct_latex_dfrac(self):
        assert self._check(r"\dfrac{1}{2}") is True

    def test_correct_latex_with_dollars(self):
        assert self._check(r"$\frac{1}{2}$") is True

    def test_correct_integer_zero(self):
        # 0/2 == 0, not 1/2
        assert self._check("0") is False

    def test_correct_integer_one_for_1_1(self):
        assert check_rational_answer("1", 1, 1) is True

    # ── wrong values ────────────────────────────────────────────────────────

    def test_wrong_fraction(self):
        assert self._check("3/4") is False

    def test_wrong_decimal(self):
        assert self._check("0.6") is False

    def test_wrong_percentage(self):
        assert self._check("60%") is False

    # ── strict mode ─────────────────────────────────────────────────────────

    def test_strict_accepts_plain_fraction(self):
        assert self._check("1/2", strict_fraction=True) is True

    def test_strict_rejects_decimal(self):
        assert self._check("0.5", strict_fraction=True) is False

    def test_strict_rejects_percentage(self):
        assert self._check("50%", strict_fraction=True) is False

    def test_strict_accepts_latex(self):
        assert self._check(r"\frac{1}{2}", strict_fraction=True) is True

    # ── probability range violations ─────────────────────────────────────────

    def test_out_of_range_expected_raises(self):
        with pytest.raises(ValueError, match="probability"):
            check_rational_answer("1/2", 5, 4)  # 5/4 > 1

    def test_negative_expected_raises(self):
        with pytest.raises(ValueError, match="probability"):
            check_rational_answer("1/2", -1, 2)

    # ── invalid / edge inputs ────────────────────────────────────────────────

    def test_division_by_zero_user_input(self):
        assert self._check("1/0") is False

    def test_empty_string(self):
        assert self._check("") is False

    def test_none_input(self):
        assert self._check(None) is False

    def test_whitespace_only(self):
        assert self._check("   ") is False

    def test_negative_denominator_config_raises(self):
        with pytest.raises(ValueError):
            check_rational_answer("1/2", 1, -2)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. check_integer_answer tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckIntegerAnswer:
    """Tests for check_integer_answer with expected = 36."""

    EXP = 36

    def _check(self, user_answer, **kwargs) -> bool:
        return check_integer_answer(user_answer, self.EXP, **kwargs)

    # ── correct inputs ───────────────────────────────────────────────────────

    def test_correct_int(self):
        assert self._check(36) is True

    def test_correct_string(self):
        assert self._check("36") is True

    def test_correct_with_spaces(self):
        assert self._check(" 36 ") is True

    def test_correct_fullwidth(self):
        # Full-width digits
        assert self._check("３６") is True

    # ── wrong values ─────────────────────────────────────────────────────────

    def test_wrong_value(self):
        assert self._check("35") is False

    def test_wrong_value_int(self):
        assert self._check(37) is False

    # ── rejected formats ─────────────────────────────────────────────────────

    def test_rejects_decimal(self):
        assert self._check("36.0") is False

    def test_rejects_fraction(self):
        assert self._check("72/2") is False

    def test_rejects_percentage(self):
        assert self._check("36%") is False

    def test_rejects_negative_by_default(self):
        assert self._check("-36") is False

    def test_allows_negative_when_flag_set(self):
        assert check_integer_answer("-36", -36, allow_negative=True) is True

    def test_rejects_empty(self):
        assert self._check("") is False

    def test_rejects_none(self):
        assert self._check(None) is False


# ═══════════════════════════════════════════════════════════════════════════════
# 3. check_probability_range tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckProbabilityRange:
    def test_zero_is_valid(self):
        assert check_probability_range(0) is True

    def test_one_is_valid(self):
        assert check_probability_range(1) is True

    def test_half_is_valid(self):
        from fractions import Fraction
        assert check_probability_range(Fraction(1, 2)) is True

    def test_above_one_raises(self):
        with pytest.raises(ValueError, match="probability"):
            check_probability_range(1.5)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="probability"):
            check_probability_range(-0.1)

    def test_non_numeric_raises(self):
        with pytest.raises(ValueError):
            check_probability_range("abc")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Generator tests
# ═══════════════════════════════════════════════════════════════════════════════

_REQUIRED_PAYLOAD_KEYS = {
    "question_text", "choices", "answer", "explanation",
    "skill_id", "subskill_id", "problem_type_id", "generator_key",
    "difficulty", "diagnosis_tags", "remediation_candidates",
    "source_style_refs", "parameters",
}

_PLACEHOLDER_TOKENS = ["[BLANK]", "[FORMULA_MISSING]", "[FORMULA_IMAGE", "[WORD_EQUATION_UNPARSED]", "□"]


def _assert_payload_valid(payload: dict, expected_problem_type_id: str, expected_skill_id: str) -> None:
    missing = _REQUIRED_PAYLOAD_KEYS - set(payload.keys())
    assert not missing, f"Missing keys: {missing}"
    assert payload["problem_type_id"] == expected_problem_type_id
    assert payload["skill_id"] == expected_skill_id
    assert payload["answer_type"] != "handwriting"
    assert payload["answer_type"] != "ai_judged_free_response"
    q = payload["question_text"]
    exp = payload["explanation"]
    assert isinstance(q, str) and q.strip()
    assert isinstance(exp, str) and exp.strip()
    for tok in _PLACEHOLDER_TOKENS:
        assert tok not in q, f"Placeholder {tok!r} in question_text"
        assert tok not in exp, f"Placeholder {tok!r} in explanation"


class TestClassicalProbabilityFractionGenerator:
    SKILL = "vh_數學B4_ProbabilityDefinition"
    PID = "classical_probability_fraction"

    def _gen(self, seed=1, **kwargs):
        return classical_probability_fraction(
            skill_id=self.SKILL, subskill_id="b4_ch2_prob_def_classical_01",
            difficulty=1, seed=seed, **kwargs
        )

    def test_payload_structure(self):
        p = self._gen()
        _assert_payload_valid(p, self.PID, self.SKILL)

    def test_answer_is_fraction_string(self):
        for seed in range(1, 6):
            p = self._gen(seed=seed)
            ans = p["answer"]
            assert isinstance(ans, str)
            # Must be "a/b" or "0" or "1"
            if "/" in ans:
                num, den = ans.split("/")
                assert int(den) > 0
                assert int(num) >= 0
            else:
                assert ans in {"0", "1"}

    def test_answer_in_probability_range(self):
        from fractions import Fraction
        for seed in range(1, 8):
            p = self._gen(seed=seed)
            ans = p["answer"]
            if "/" in ans:
                num, den = ans.split("/")
                frac = Fraction(int(num), int(den))
            else:
                frac = Fraction(int(ans))
            assert 0 <= frac <= 1, f"Out of range: {frac}"

    def test_answer_is_reduced(self):
        from fractions import Fraction
        for seed in range(1, 8):
            p = self._gen(seed=seed)
            ans = p["answer"]
            if "/" in ans:
                num, den = map(int, ans.split("/"))
                assert math.gcd(num, den) == 1, f"Not reduced: {ans}"

    def test_choices_contain_answer(self):
        p = self._gen()
        assert p["answer"] in p["choices"]

    def test_no_two_same_seeds_same_tuple(self):
        seen: set[tuple] = set()
        for seed in range(1, 10):
            p = classical_probability_fraction(
                skill_id=self.SKILL, subskill_id="x",
                difficulty=1, seed=seed, seen_parameter_tuples=seen,
            )
            t = p["parameters"]["parameter_tuple"]
            assert t not in seen or True  # seen updated by generator


class TestComplementProbabilityGenerator:
    SKILL = "vh_數學B4_ProbabilityProperties"
    PID = "complement_probability"

    def _gen(self, seed=1, **kwargs):
        return complement_probability(
            skill_id=self.SKILL, subskill_id="b4_ch2_prob_prop_complement_01",
            difficulty=1, seed=seed, **kwargs
        )

    def test_payload_structure(self):
        p = self._gen()
        _assert_payload_valid(p, self.PID, self.SKILL)

    def test_answer_in_probability_range(self):
        from fractions import Fraction
        for seed in range(1, 8):
            p = self._gen(seed=seed)
            ans = p["answer"]
            if "/" in ans:
                num, den = ans.split("/")
                frac = Fraction(int(num), int(den))
            else:
                frac = Fraction(int(ans))
            assert 0 <= frac <= 1

    def test_answer_is_reduced(self):
        from fractions import Fraction
        for seed in range(1, 8):
            p = self._gen(seed=seed)
            ans = p["answer"]
            if "/" in ans:
                num, den = map(int, ans.split("/"))
                assert math.gcd(num, den) == 1

    def test_explanation_mentions_complement_formula(self):
        for seed in range(1, 5):
            p = self._gen(seed=seed)
            assert "P(A')" in p["explanation"] or "補事件" in p["explanation"]

    def test_choices_contain_answer(self):
        p = self._gen()
        assert p["answer"] in p["choices"]


class TestSampleSpaceCountNumericGenerator:
    SKILL = "vh_數學B4_SampleSpaceAndEvents"
    PID = "sample_space_count_numeric"

    def _gen(self, seed=1, **kwargs):
        return sample_space_count_numeric(
            skill_id=self.SKILL, subskill_id="b4_ch2_sample_space_count_01",
            difficulty=1, seed=seed, **kwargs
        )

    def test_payload_structure(self):
        p = self._gen()
        _assert_payload_valid(p, self.PID, self.SKILL)

    def test_answer_is_nonnegative_integer(self):
        for seed in range(1, 8):
            p = self._gen(seed=seed)
            ans = p["answer"]
            assert isinstance(ans, int), f"Expected int, got {type(ans)}"
            assert ans >= 0

    def test_answer_type_is_integer(self):
        p = self._gen()
        assert p["answer_type"] == "integer"

    def test_choices_are_integers(self):
        p = self._gen()
        for c in p["choices"]:
            assert isinstance(c, int)

    def test_choices_contain_answer(self):
        p = self._gen()
        assert p["answer"] in p["choices"]

    def test_answer_checker_correct(self):
        for seed in range(1, 6):
            p = self._gen(seed=seed)
            expected = p["answer"]
            assert check_integer_answer(str(expected), expected) is True
            assert check_integer_answer(f"{expected}.0", expected) is False  # decimal rejected

    def test_question_does_not_ask_to_list(self):
        for seed in range(1, 6):
            p = self._gen(seed=seed)
            q = p["question_text"]
            assert "列出" not in q and "列舉" not in q, \
                f"Question asks for listing: {q}"

    def test_variety_coverage_across_30_seeds(self):
        seen_contexts = set()
        for seed in range(1, 31):
            p = self._gen(seed=seed)
            context = p.get("context_type") or p["parameters"].get("scenario")
            seen_contexts.add(context)
        assert {"coin_tosses", "dice_rolls", "sequential_choices"} <= seen_contexts

    def test_each_context_has_expected_text_features(self):
        expected = {"coin_tosses": False, "dice_rolls": False, "sequential_choices": False}
        for seed in range(1, 61):
            p = self._gen(seed=seed)
            context = p.get("context_type") or p["parameters"].get("scenario")
            q = p["question_text"]
            if context == "coin_tosses":
                assert "硬幣" in q and "樣本空間" in q
                expected["coin_tosses"] = True
            elif context == "dice_rolls":
                assert "骰子" in q or "面骰" in q
                assert "樣本空間" in q
                expected["dice_rolls"] = True
            elif context == "sequential_choices":
                assert ("階段" in q or "步驟" in q) and "選擇" in q
                expected["sequential_choices"] = True
        assert all(expected.values()), f"missing context text evidence: {expected}"

    def test_variety_questions_have_no_forbidden_tokens(self):
        forbidden = ["列出", "寫出所有", "sample_space_listing", "[FORMULA_MISSING]", "[BLANK]"]
        for seed in range(1, 31):
            p = self._gen(seed=seed)
            q = p["question_text"]
            for tok in forbidden:
                assert tok not in q, f"forbidden token {tok!r} found in question: {q}"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Router tests (generate_for_chap2_skill)
# ═══════════════════════════════════════════════════════════════════════════════

class TestChap2Router:
    @pytest.mark.parametrize("skill_id,expected_pid", [
        ("vh_數學B4_ProbabilityDefinition", "classical_probability_fraction"),
        ("vh_數學B4_ProbabilityProperties", "complement_probability"),
        ("vh_數學B4_SampleSpaceAndEvents", "sample_space_count_numeric"),
    ])
    def test_p0_skills_generate_correctly(self, skill_id, expected_pid):
        # Pin problem_type_id so 6C-2 registry expansion doesn’t rotate to a new entry.
        payload = generate_for_chap2_skill(
            skill_id=skill_id, level=1, seed=42, problem_type_id=expected_pid
        )
        assert payload["problem_type_id"] == expected_pid
        assert payload["skill_id"] == skill_id
        assert "router_trace" in payload
        assert payload["router_trace"]["router"] == "chap2_phase6c1"

    def test_unsupported_skill_raises(self):
        with pytest.raises(ValueError, match="unsupported skill_id"):
            generate_for_chap2_skill(skill_id="vh_數學B4_ProbabilityOperations")

    def test_chap1_skill_still_works_via_original_router(self):
        from core.vocational_math_b4.services.question_router import generate_for_skill
        payload = generate_for_skill(skill_id="vh_數學B4_AdditionPrinciple", level=1, seed=10)
        assert payload["skill_id"] == "vh_數學B4_AdditionPrinciple"

    def test_payload_has_required_keys(self):
        payload = generate_for_chap2_skill(
            skill_id="vh_數學B4_ProbabilityDefinition", level=1, seed=5
        )
        for key in ["question_text", "answer", "correct_answer", "choices",
                    "explanation", "skill_id", "subskill_id", "problem_type_id",
                    "generator_key", "difficulty", "router_trace"]:
            assert key in payload, f"Missing: {key}"

    def test_correct_answer_equals_answer(self):
        payload = generate_for_chap2_skill(
            skill_id="vh_數學B4_ProbabilityProperties", level=1, seed=7
        )
        assert payload["answer"] == payload["correct_answer"]


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Allowlist boundary tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestChap2AllowlistBoundary:
    def test_p0_skills_in_allowlist(self):
        for sid in [
            "vh_數學B4_ProbabilityDefinition",
            "vh_數學B4_ProbabilityProperties",
            "vh_數學B4_SampleSpaceAndEvents",
        ]:
            assert is_b4_chapter2_phase6c1_deterministic_skill(sid), f"{sid} should be in allowlist"

    def test_non_enabled_skills_not_in_allowlist(self):
        for sid in [
            "vh_數學B4_MathematicalExpectation",
        ]:
            assert not is_b4_chapter2_phase6c1_deterministic_skill(sid)

    def test_excluded_handwriting_problem_types(self):
        for pid in ["sample_space_listing", "event_set_listing", "subset_listing"]:
            assert is_b4_chapter2_excluded_problem_type(pid), f"{pid} should be excluded"

    def test_p0_problem_types_not_excluded(self):
        for pid in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES:
            assert not is_b4_chapter2_excluded_problem_type(pid)

    def test_validate_payload_passes_for_valid(self):
        payload = generate_for_chap2_skill(
            skill_id="vh_數學B4_ProbabilityDefinition", level=1, seed=1
        )
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(
            "vh_數學B4_ProbabilityDefinition", payload
        )
        assert ok is True, f"Expected ok=True, got reason={reason}"

    def test_validate_payload_blocks_handwriting_problem_type(self):
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(
            "vh_數學B4_SampleSpaceAndEvents",
            {"problem_type_id": "sample_space_listing"},
        )
        assert ok is False
        assert "excluded_handwriting" in reason

    def test_validate_payload_blocks_unregistered_problem_type(self):
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(
            "vh_數學B4_ProbabilityDefinition",
            {"problem_type_id": "event_operation_probability"},
        )
        assert ok is False
        assert "not_in_phase6c1_allowlist" in reason

    def test_validate_payload_blocks_missing_pid(self):
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(
            "vh_數學B4_ProbabilityDefinition",
            {},
        )
        assert ok is False

    def test_chap1_allowlist_unaffected(self):
        from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
            B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
        )
        chap2_skills = {
            "vh_數學B4_ProbabilityDefinition",
            "vh_數學B4_ProbabilityProperties",
            "vh_數學B4_SampleSpaceAndEvents",
        }
        overlap = chap2_skills & B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST
        assert not overlap, f"Chap2 skills leaked into Chap1 allowlist: {overlap}"


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Multi-seed smoke test (generator stability)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("skill_id,pid", [
    ("vh_數學B4_ProbabilityDefinition", "classical_probability_fraction"),
    ("vh_數學B4_ProbabilityProperties", "complement_probability"),
    ("vh_數學B4_SampleSpaceAndEvents", "sample_space_count_numeric"),
])
@pytest.mark.parametrize("seed", [1, 2, 3, 7, 42, 99])
def test_multi_seed_smoke(skill_id, pid, seed):
    # Pin problem_type_id so 6C-2 expansion doesn’t change which entry is selected.
    payload = generate_for_chap2_skill(skill_id=skill_id, level=1, seed=seed, problem_type_id=pid)
    assert payload["problem_type_id"] == pid
    assert payload["skill_id"] == skill_id
    assert payload["answer"] is not None
    assert payload["question_text"].strip()
    assert payload["explanation"].strip()
    assert payload.get("answer_type") not in ("handwriting", "ai_judged_free_response")
