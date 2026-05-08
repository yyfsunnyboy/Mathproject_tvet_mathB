"""Phase 6F: MathematicalExpectationDefinition (expected value) runtime-ready tests."""

from __future__ import annotations

import importlib
import math
from fractions import Fraction
from urllib.parse import quote as _url_quote, unquote as _url_unquote

import pytest

from core.vocational_math_b4.generators.chap2_expected_value import (
    EXPECTATION_DISCRETE_BASIC_PROBLEM_TYPE_ID,
    EXPECTATION_FROM_DISTRIBUTION_PROBLEM_TYPE_ID,
    expectation_discrete_basic,
    expectation_from_distribution,
)
from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
    B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS,
    B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST,
    B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES,
    is_b4_chapter2_excluded_problem_type,
    is_b4_chapter2_phase6c1_deterministic_skill,
    is_b4_chapter2_skill_not_enabled_in_phase6c1,
    validate_b4_chap2_phase6c1_generator_payload,
)
from core.vocational_math_b4.domain.b4_validators import (
    check_expected_value_answer,
    check_rational_answer,
)

SKILL_EXP = "vh_數學B4_MathematicalExpectationDefinition"
ENCODED_EXP = "vh_%E6%95%B8%E5%AD%B8B4_MathematicalExpectationDefinition"
FORBIDDEN_ABSTRACT_TOKENS = ("W ∈", "隨機權重", "隨機分割")


def _frac(s: str) -> Fraction:
    return Fraction(s) if "/" in s else Fraction(int(s))


def _weights_sum(payload: dict) -> Fraction:
    ws = payload["parameters"]["weights"]
    acc = Fraction(0, 1)
    for pn, pd in ws:
        acc += Fraction(pn, pd)
    return acc


def _expected_matches_answer(payload: dict) -> None:
    xs = payload["parameters"]["xs"]
    ws = payload["parameters"]["weights"]
    expected = Fraction(0, 1)
    for x, (pn, pd) in zip(xs, ws, strict=True):
        expected += Fraction(x, 1) * Fraction(pn, pd)
    assert _frac(payload["answer"]) == expected


def _assert_ev_payload(payload: dict, pid: str) -> None:
    assert payload["skill_id"] == SKILL_EXP
    assert payload["problem_type_id"] == pid
    assert payload["answer_type"] == "expected_value"
    assert payload["question_text"].strip()
    assert payload["explanation"].strip()
    assert "E(X)" in payload["explanation"] or "\\sum_x" in payload["explanation"]
    assert "[FORMULA_MISSING]" not in payload["question_text"]
    assert "[BLANK]" not in payload["question_text"]
    assert "[FORMULA_MISSING]" not in payload["explanation"]
    assert "[BLANK]" not in payload["explanation"]
    assert _weights_sum(payload) == 1
    _expected_matches_answer(payload)
    ans = payload["answer"]
    if "/" in ans:
        n, d = map(int, ans.split("/", 1))
        assert math.gcd(abs(n), d) == 1
    assert payload["answer"] in payload["choices"]
    assert payload["answer_type"] not in ("handwriting", "ai_judged_free_response")
    for tok in FORBIDDEN_ABSTRACT_TOKENS:
        assert tok not in payload["question_text"]


def _assert_textbook_phrase(payload: dict) -> None:
    qt = payload["question_text"]
    assert ("期望值" in qt) or ("E(X)" in qt)
    assert ("P(X" in qt) or ("P(X)" in qt)
    assert ("所得金額" in qt) or ("得分" in qt) or ("期望值" in qt)


def _assert_explanation_substitution(payload: dict) -> None:
    exp = payload["explanation"]
    assert "E(X)=\\sum_x x\\cdot P(X=x)" in exp
    assert ("逐項代入" in exp) or ("代入" in exp)


def _monkeypatch_forbid_legacy_skill_import(monkeypatch: pytest.MonkeyPatch, blocked_skill_id: str) -> None:
    legacy_module = f"skills.{blocked_skill_id}"
    original = importlib.import_module

    def _wrapped(name: str, package=None):
        if name == legacy_module:
            pytest.fail(f"unexpected legacy import: {name}")
        return original(name, package)

    monkeypatch.setattr(importlib, "import_module", _wrapped)


class TestGeneratorExpectationDiscrete:
    @pytest.mark.parametrize("seed", range(1, 31))
    def test_expectation_discrete_basic_multi_seed(self, seed):
        p = expectation_discrete_basic(
            skill_id=SKILL_EXP, subskill_id="b4_ch2_exp_disc_01", seed=seed
        )
        _assert_ev_payload(p, EXPECTATION_DISCRETE_BASIC_PROBLEM_TYPE_ID)
        _assert_textbook_phrase(p)
        _assert_explanation_substitution(p)


class TestGeneratorExpectationDistribution:
    @pytest.mark.parametrize("seed", range(1, 31))
    def test_expectation_from_distribution_multi_seed(self, seed):
        p = expectation_from_distribution(
            skill_id=SKILL_EXP, subskill_id="b4_ch2_exp_table_01", seed=seed
        )
        _assert_ev_payload(p, EXPECTATION_FROM_DISTRIBUTION_PROBLEM_TYPE_ID)
        _assert_textbook_phrase(p)
        _assert_explanation_substitution(p)
        qt = p["question_text"]
        assert "|" in qt
        assert "X" in qt
        assert "P(X)" in qt


class TestCheckerCompatibility:
    @pytest.mark.parametrize("pid", ["expectation_discrete_basic", "expectation_from_distribution"])
    def test_checker_equivalence_and_reject_pct(self, pid):
        p = generate_for_chap2_skill(skill_id=SKILL_EXP, problem_type_id=pid, seed=11)
        ans = p["answer"]
        n, d = (map(int, ans.split("/", 1)) if "/" in ans else (int(ans), 1))
        frac = Fraction(n, d)
        assert check_expected_value_answer(ans, ans) is True
        assert check_expected_value_answer(f"{n * 2}/{d * 2}", ans) is True
        tmp_den = frac.denominator
        td = tmp_den
        while td % 2 == 0:
            td //= 2
        while td % 5 == 0:
            td //= 5
        if td == 1:
            assert check_expected_value_answer(f"{float(frac):g}", ans) is True
        assert check_expected_value_answer(f"{float(frac) * 100:g}%", ans) is False
        assert check_expected_value_answer("999/888", ans) is (Fraction(999, 888) == frac)
        assert check_expected_value_answer("1/0", ans) is False


class TestRouterAllowlistBoundary:
    def test_phase6f_problem_types_generate(self):
        for pid in ("expectation_discrete_basic", "expectation_from_distribution"):
            p = generate_for_chap2_skill(skill_id=SKILL_EXP, problem_type_id=pid, seed=12)
            assert p["problem_type_id"] == pid

    def test_phase6c6d6e_still_generate(self):
        pairs = [
            ("vh_數學B4_ProbabilityDefinition", "classical_probability_fraction"),
            ("vh_數學B4_ProbabilityProperties", "complement_probability"),
            ("vh_數學B4_SampleSpaceAndEvents", "sample_space_count_numeric"),
            ("vh_數學B4_ProbabilityProperties", "union_intersection_probability"),
            ("vh_數學B4_ProbabilityDefinition", "dice_coin_probability_count"),
            ("vh_數學B4_ConditionalProbability", "conditional_probability_basic"),
            ("vh_數學B4_ConditionalProbability", "without_replacement_conditional_probability"),
            ("vh_數學B4_IndependentEvents", "independent_joint_probability"),
            ("vh_數學B4_IndependentEvents", "independent_at_least_one_probability"),
        ]
        for sid, pid in pairs:
            p = generate_for_chap2_skill(skill_id=sid, problem_type_id=pid, seed=13)
            assert p["problem_type_id"] == pid

    def test_unsupported_problem_type_clear_error(self):
        with pytest.raises(ValueError, match="problem_type_id is not supported"):
            generate_for_chap2_skill(
                skill_id=SKILL_EXP,
                problem_type_id="expectation_word_problem_profit_fairness",
                seed=1,
            )

    def test_handwriting_reserved_hard_excluded(self):
        for pid in ("sample_space_listing", "event_set_listing", "subset_listing"):
            assert is_b4_chapter2_excluded_problem_type(pid) is True

    def test_applications_legacy_expectation_still_blocked(self):
        for sid in (
            "vh_數學B4_BasicConceptsOfSets",
            "vh_數學B4_MathematicalExpectation",
            "vh_數學B4_ApplicationsOfExpectation",
            "vh_數學B4_ProbabilityOperations",
        ):
            assert is_b4_chapter2_skill_not_enabled_in_phase6c1(sid) is True

    def test_expectation_definition_enabled(self):
        assert is_b4_chapter2_phase6c1_deterministic_skill(SKILL_EXP) is True
        assert is_b4_chapter2_skill_not_enabled_in_phase6c1(SKILL_EXP) is False
        assert SKILL_EXP in B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST


class TestRouteIntegration:
    def test_url_encoded_decoded_expectation_skill(self):
        assert _url_unquote(ENCODED_EXP) == SKILL_EXP
        assert is_b4_chapter2_phase6c1_deterministic_skill(_url_unquote(ENCODED_EXP))

    def test_frontend_double_encoding_regression_expectation(self):
        raw = ENCODED_EXP
        frontend_decoded = _url_unquote(raw)
        reencoded = _url_quote(frontend_decoded, safe="")
        assert _url_unquote(reencoded) == SKILL_EXP

    @pytest.mark.parametrize("pid", ["expectation_discrete_basic", "expectation_from_distribution"])
    def test_get_next_question_equivalent(self, pid):
        p = generate_for_chap2_skill(skill_id=SKILL_EXP, problem_type_id=pid, seed=14)
        assert p["problem_type_id"] == pid
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(SKILL_EXP, p)
        assert ok is True, reason

    def test_check_answer_equivalent_fraction_decimal(self):
        p = generate_for_chap2_skill(
            skill_id=SKILL_EXP,
            problem_type_id="expectation_discrete_basic",
            seed=3,
        )
        ans = p["answer"]
        assert check_expected_value_answer(ans.strip(), ans)
        assert check_expected_value_answer("  " + ans + "  ", ans)
        frac = _frac(ans)
        un = f"{frac.numerator * 3}/{frac.denominator * 3}"
        assert check_expected_value_answer(un, ans)
        tmp = frac.denominator
        while tmp % 2 == 0:
            tmp //= 2
        while tmp % 5 == 0:
            tmp //= 5
        if tmp == 1:
            assert check_expected_value_answer(f"{float(frac):g}", ans)

    def test_unsupported_skill_no_legacy_import(self, monkeypatch):
        _monkeypatch_forbid_legacy_skill_import(monkeypatch, "vh_數學B4_BasicConceptsOfSets")
        assert "vh_數學B4_BasicConceptsOfSets" in B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS


class TestRegressions:
    def test_chap1_regression_basic(self):
        from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
            B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
        )
        assert len(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST) == 13

    def test_router_trace_exists(self):
        p = generate_for_chap2_skill(skill_id=SKILL_EXP, seed=2)
        assert p["router_trace"]["router"] == "chap2_phase6c1"


class TestRationalCheckerUnchangedForProbability:
    """Sanity: probability path still accepts percentage."""

    def test_pct_still_ok_for_probability_answers(self):
        assert check_rational_answer("50%", 1, 2) is True
