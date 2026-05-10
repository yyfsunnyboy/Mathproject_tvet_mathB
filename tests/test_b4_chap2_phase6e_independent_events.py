"""Phase 6E: Independent Events runtime-ready tests."""
from __future__ import annotations

import importlib
from fractions import Fraction
from urllib.parse import quote as _url_quote, unquote as _url_unquote

import pytest

from core.vocational_math_b4.generators.chap2_independent_events import (
    INDEPENDENT_AT_LEAST_ONE_PROBLEM_TYPE_ID,
    INDEPENDENT_JOINT_PROBLEM_TYPE_ID,
    independent_at_least_one_probability,
    independent_joint_probability,
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
from core.vocational_math_b4.domain.b4_validators import check_rational_answer

SKILL_INDEP = "vh_數學B4_IndependentEvents"
ENCODED_INDEP = "vh_%E6%95%B8%E5%AD%B8B4_IndependentEvents"


def _frac(s: str) -> Fraction:
    return Fraction(s) if "/" in s else Fraction(int(s))


def _assert_common_fraction_payload(payload: dict, pid: str) -> None:
    assert payload["skill_id"] == SKILL_INDEP
    assert payload["problem_type_id"] == pid
    assert payload["answer_type"] == "rational_fraction"
    assert payload["question_text"].strip()
    assert payload["explanation"].strip()
    assert "[FORMULA_MISSING]" not in payload["question_text"]
    assert "[BLANK]" not in payload["question_text"]
    assert "[FORMULA_MISSING]" not in payload["explanation"]
    assert "[BLANK]" not in payload["explanation"]
    f = _frac(payload["answer"])
    assert 0 <= f <= 1
    assert payload["answer"] in payload["choices"]
    assert payload["answer_type"] not in ("handwriting", "ai_judged_free_response")


def _monkeypatch_forbid_legacy_skill_import(monkeypatch: pytest.MonkeyPatch, blocked_skill_id: str) -> None:
    legacy_module = f"skills.{blocked_skill_id}"
    original = importlib.import_module

    def _wrapped(name: str, package=None):
        if name == legacy_module:
            pytest.fail(f"unexpected legacy import: {name}")
        return original(name, package)

    monkeypatch.setattr(importlib, "import_module", _wrapped)


class TestGeneratorIndependentJoint:
    @pytest.mark.parametrize("seed", range(1, 31))
    def test_generator_joint_payload_multi_seed(self, seed):
        p = independent_joint_probability(
            skill_id=SKILL_INDEP, subskill_id="b4_ch2_indep_joint_01", seed=seed
        )
        _assert_common_fraction_payload(p, INDEPENDENT_JOINT_PROBLEM_TYPE_ID)
        assert ("獨立事件" in p["question_text"]) or ("互相獨立" in p["question_text"])
        assert "P(A\\cap B)=P(A)\\times P(B)" in p["explanation"]


class TestGeneratorIndependentAtLeastOne:
    @pytest.mark.parametrize("seed", range(1, 31))
    def test_generator_at_least_one_payload_multi_seed(self, seed):
        p = independent_at_least_one_probability(
            skill_id=SKILL_INDEP, subskill_id="b4_ch2_indep_at_least_one_01", seed=seed
        )
        _assert_common_fraction_payload(p, INDEPENDENT_AT_LEAST_ONE_PROBLEM_TYPE_ID)
        assert ("互相獨立" in p["question_text"]) or ("彼此獨立" in p["question_text"])
        assert "P(\\text{至少一次成功})=1-P(\\text{全部失敗})=1-(1-p)^n" in p["explanation"]
        assert "image" not in p["question_text"].lower()
        assert "chart" not in p["question_text"].lower()


class TestCheckerCompatibility:
    @pytest.mark.parametrize("pid", [
        "independent_joint_probability",
        "independent_at_least_one_probability",
    ])
    def test_checker_equivalence_cases(self, pid):
        p = generate_for_chap2_skill(skill_id=SKILL_INDEP, problem_type_id=pid, seed=9)
        ans = p["answer"]
        n, d = (map(int, ans.split("/", 1)) if "/" in ans else (int(ans), 1))
        assert check_rational_answer(ans, n, d) is True
        assert check_rational_answer(f"{n*2}/{d*2}", n, d) is True
        assert check_rational_answer(str(float(Fraction(n, d))), n, d) is True
        assert check_rational_answer(f"{float(Fraction(n, d))*100:g}%", n, d) is True
        assert check_rational_answer("999/1000", n, d) is (Fraction(999, 1000) == Fraction(n, d))
        assert check_rational_answer("1/0", n, d) is False
        assert check_rational_answer("5/4", n, d) is False


class TestRouterAllowlistBoundary:
    def test_phase6e_problem_types_can_generate(self):
        for pid in ("independent_joint_probability", "independent_at_least_one_probability"):
            p = generate_for_chap2_skill(skill_id=SKILL_INDEP, problem_type_id=pid, seed=10)
            assert p["problem_type_id"] == pid

    def test_phase6c6d_problem_types_still_generate(self):
        for sid, pid in [
            ("vh_數學B4_ProbabilityDefinition", "classical_probability_fraction"),
            ("vh_數學B4_ProbabilityProperties", "complement_probability"),
            ("vh_數學B4_SampleSpaceAndEvents", "sample_space_count_numeric"),
            ("vh_數學B4_ProbabilityProperties", "union_intersection_probability"),
            ("vh_數學B4_ProbabilityDefinition", "dice_coin_probability_count"),
            ("vh_數學B4_ConditionalProbability", "conditional_probability_basic"),
            ("vh_數學B4_ConditionalProbability", "without_replacement_conditional_probability"),
        ]:
            p = generate_for_chap2_skill(skill_id=sid, problem_type_id=pid, seed=11)
            assert p["problem_type_id"] == pid

    def test_unsupported_problem_type_clear_error(self):
        with pytest.raises(ValueError, match="problem_type_id is not supported"):
            generate_for_chap2_skill(
                skill_id=SKILL_INDEP,
                problem_type_id="independent_event_judgement",
                seed=1,
            )

    def test_handwriting_reserved_hard_excluded(self):
        for pid in ("sample_space_listing", "event_set_listing", "subset_listing"):
            assert is_b4_chapter2_excluded_problem_type(pid) is True

    def test_applications_legacy_expectation_and_basicsets_now_enabled(self):
        # Phase 6K closure: the four historically-blocked Chap2 skills are now
        # enabled via deterministic generators; not-enabled set is empty.
        for sid in (
            "vh_數學B4_BasicConceptsOfSets",
            "vh_數學B4_MathematicalExpectation",
            "vh_數學B4_ApplicationsOfExpectation",
            "vh_數學B4_ProbabilityOperations",
        ):
            assert is_b4_chapter2_skill_not_enabled_in_phase6c1(sid) is False
            assert is_b4_chapter2_phase6c1_deterministic_skill(sid) is True

        assert B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS == frozenset()
        assert "vh_數學B4_MathematicalExpectationDefinition" not in B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS

    def test_mathematical_expectation_definition_enabled(self):
        sid = "vh_數學B4_MathematicalExpectationDefinition"
        assert is_b4_chapter2_phase6c1_deterministic_skill(sid) is True
        assert "expectation_discrete_basic" in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES
        assert "expectation_from_distribution" in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES

    def test_independent_events_now_enabled(self):
        assert is_b4_chapter2_phase6c1_deterministic_skill(SKILL_INDEP) is True
        assert is_b4_chapter2_skill_not_enabled_in_phase6c1(SKILL_INDEP) is False
        assert SKILL_INDEP in B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST
        assert "independent_joint_probability" in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES
        assert "independent_at_least_one_probability" in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES


class TestRouteIntegration:
    def test_url_encoded_decoded_independent(self):
        assert _url_unquote(ENCODED_INDEP) == SKILL_INDEP
        assert is_b4_chapter2_phase6c1_deterministic_skill(_url_unquote(ENCODED_INDEP))

    def test_frontend_double_encoding_regression_independent(self):
        raw = ENCODED_INDEP
        frontend_decoded = _url_unquote(raw)
        reencoded = _url_quote(frontend_decoded, safe="")
        assert _url_unquote(reencoded) == SKILL_INDEP

    @pytest.mark.parametrize("pid", [
        "independent_joint_probability",
        "independent_at_least_one_probability",
    ])
    def test_get_next_question_equivalent(self, pid):
        p = generate_for_chap2_skill(skill_id=SKILL_INDEP, problem_type_id=pid, seed=12)
        assert p["question_text"]
        assert p["problem_type_id"] == pid
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(SKILL_INDEP, p)
        assert ok is True, reason

    def test_check_answer_equivalent_fraction_decimal_percentage(self):
        p = generate_for_chap2_skill(
            skill_id=SKILL_INDEP, problem_type_id="independent_joint_probability", seed=7
        )
        ans = p["answer"]
        n, d = (map(int, ans.split("/", 1)) if "/" in ans else (int(ans), 1))
        frac = Fraction(n, d)
        assert check_rational_answer(ans, n, d)
        assert check_rational_answer(f"{n*3}/{d*3}", n, d)
        tmp_den = frac.denominator
        while tmp_den % 2 == 0:
            tmp_den //= 2
        while tmp_den % 5 == 0:
            tmp_den //= 5
        if tmp_den == 1:
            assert check_rational_answer(f"{float(frac):g}", n, d)
            assert check_rational_answer(f"{float(frac)*100:g}%", n, d)

    def test_unsupported_skill_no_legacy_import(self, monkeypatch):
        # Phase 6K: BasicConceptsOfSets is now enabled via deterministic generator;
        # legacy skills.<id> module must still NOT be imported when generating
        # (deterministic path is the only path for Chap2 skills).
        _monkeypatch_forbid_legacy_skill_import(monkeypatch, "vh_數學B4_BasicConceptsOfSets")
        p = generate_for_chap2_skill(
            skill_id="vh_數學B4_BasicConceptsOfSets",
            seed=33,
        )
        assert p["skill_id"] == "vh_數學B4_BasicConceptsOfSets"
        assert "vh_數學B4_BasicConceptsOfSets" not in B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS



class TestRegressions:
    def test_chap1_regression_basic(self):
        from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
            B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
        )
        assert len(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST) == 13

    def test_router_trace_exists(self):
        p = generate_for_chap2_skill(skill_id=SKILL_INDEP, seed=2)
        assert p["router_trace"]["router"] == "chap2_phase6c1"
