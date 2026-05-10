"""Phase 6K: Chap2 remaining deterministic skill coverage runtime-ready batch tests.

Skills opened in this phase:
  - vh_數學B4_ProbabilityOperations
      * event_operation_probability   (rational_fraction)
      * probability_algebra_mixed     (rational_fraction)
  - vh_數學B4_BasicConceptsOfSets
      * set_operation_count           (integer)
      * inclusion_exclusion_count     (integer)
  - vh_數學B4_ApplicationsOfExpectation
      * expectation_word_problem_profit_fairness  (expected_value)
  - vh_數學B4_MathematicalExpectation
      * expectation_assessment_numeric            (expected_value)

Hard restrictions (Phase 6K guardrail):
  - No handwriting / ai_judged_free_response payloads
  - sample_space_listing / event_set_listing / subset_listing /
    tree_diagram_listing remain hard-excluded
  - No mastery / APR / fail_streak / remediation modification
  - No new skills beyond the four listed above
"""

from __future__ import annotations

import importlib
import uuid
from fractions import Fraction
from urllib.parse import quote as _url_quote, unquote as _url_unquote

import pytest

from app import create_app
from models import User, db
from core.routes.practice import (
    B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR,
)
from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
    B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS,
    B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST,
    B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES,
    B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES,
    is_b4_chapter2_excluded_problem_type,
    is_b4_chapter2_phase6c1_deterministic_skill,
    is_b4_chapter2_skill_not_enabled_in_phase6c1,
    validate_b4_chap2_phase6c1_generator_payload,
)
from core.vocational_math_b4.domain.b4_validators import (
    check_expected_value_answer,
    check_integer_answer,
    check_rational_answer,
)
from core.vocational_math_b4.generators.chap2_basic_sets import (
    INCLUSION_EXCLUSION_COUNT_PROBLEM_TYPE_ID,
    SET_OPERATION_COUNT_PROBLEM_TYPE_ID,
    inclusion_exclusion_count,
    set_operation_count,
)
from core.vocational_math_b4.generators.chap2_expectation_extensions import (
    EXPECTATION_ASSESSMENT_NUMERIC_PROBLEM_TYPE_ID,
    EXPECTATION_WORD_PROBLEM_PROFIT_FAIRNESS_PROBLEM_TYPE_ID,
    expectation_assessment_numeric,
    expectation_word_problem_profit_fairness,
)
from core.vocational_math_b4.generators.chap2_probability_operations import (
    EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID,
    PROBABILITY_ALGEBRA_MIXED_PROBLEM_TYPE_ID,
    event_operation_probability,
    probability_algebra_mixed,
)
from core.vocational_math_b4.services.question_router import generate_for_chap2_skill


# ─── constants ────────────────────────────────────────────────────────────────

SKILL_PROB_OPS = "vh_數學B4_ProbabilityOperations"
SKILL_BASIC_SETS = "vh_數學B4_BasicConceptsOfSets"
SKILL_APP_EXP = "vh_數學B4_ApplicationsOfExpectation"
SKILL_MATH_EXP = "vh_數學B4_MathematicalExpectation"

ENCODED_PROB_OPS = "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityOperations"
ENCODED_BASIC_SETS = "vh_%E6%95%B8%E5%AD%B8B4_BasicConceptsOfSets"
ENCODED_APP_EXP = "vh_%E6%95%B8%E5%AD%B8B4_ApplicationsOfExpectation"
ENCODED_MATH_EXP = "vh_%E6%95%B8%E5%AD%B8B4_MathematicalExpectation"

PHASE6K_SKILL_PIDS: list[tuple[str, str]] = [
    (SKILL_PROB_OPS, EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID),
    (SKILL_PROB_OPS, PROBABILITY_ALGEBRA_MIXED_PROBLEM_TYPE_ID),
    (SKILL_BASIC_SETS, SET_OPERATION_COUNT_PROBLEM_TYPE_ID),
    (SKILL_BASIC_SETS, INCLUSION_EXCLUSION_COUNT_PROBLEM_TYPE_ID),
    (SKILL_APP_EXP, EXPECTATION_WORD_PROBLEM_PROFIT_FAIRNESS_PROBLEM_TYPE_ID),
    (SKILL_MATH_EXP, EXPECTATION_ASSESSMENT_NUMERIC_PROBLEM_TYPE_ID),
]

# Eleven previously-runtime problem types that must remain working.
PRIOR_11_PIDS = [
    "classical_probability_fraction",
    "complement_probability",
    "sample_space_count_numeric",
    "union_intersection_probability",
    "dice_coin_probability_count",
    "conditional_probability_basic",
    "without_replacement_conditional_probability",
    "independent_joint_probability",
    "independent_at_least_one_probability",
    "expectation_discrete_basic",
    "expectation_from_distribution",
]

PRIOR_SKILL_PID_PAIRS = [
    ("vh_數學B4_ProbabilityDefinition", "classical_probability_fraction"),
    ("vh_數學B4_ProbabilityProperties", "complement_probability"),
    ("vh_數學B4_SampleSpaceAndEvents", "sample_space_count_numeric"),
    ("vh_數學B4_ProbabilityProperties", "union_intersection_probability"),
    ("vh_數學B4_ProbabilityDefinition", "dice_coin_probability_count"),
    ("vh_數學B4_ConditionalProbability", "conditional_probability_basic"),
    ("vh_數學B4_ConditionalProbability", "without_replacement_conditional_probability"),
    ("vh_數學B4_IndependentEvents", "independent_joint_probability"),
    ("vh_數學B4_IndependentEvents", "independent_at_least_one_probability"),
    ("vh_數學B4_MathematicalExpectationDefinition", "expectation_discrete_basic"),
    ("vh_數學B4_MathematicalExpectationDefinition", "expectation_from_distribution"),
]

RESERVED_LISTING_PIDS = (
    "sample_space_listing",
    "event_set_listing",
    "subset_listing",
    "tree_diagram_listing",
)


# ─── helpers ──────────────────────────────────────────────────────────────────

def _frac(s: str) -> Fraction:
    if "/" in s:
        return Fraction(s)
    return Fraction(int(s))


def _assert_payload_basics(payload: dict, *, skill_id: str, pid: str) -> None:
    assert payload["skill_id"] == skill_id
    assert payload["problem_type_id"] == pid
    assert payload["question_text"].strip()
    assert payload["explanation"].strip()
    assert payload["answer_type"] not in ("handwriting", "ai_judged_free_response")
    for token in ("[FORMULA_MISSING]", "[BLANK]", "[未填]"):
        assert token not in payload["question_text"]
        assert token not in payload["explanation"]
    assert isinstance(payload["diagnosis_tags"], list) and payload["diagnosis_tags"]
    assert isinstance(payload["remediation_candidates"], list)
    # Allowlist gate at payload-validate time:
    ok, reason = validate_b4_chap2_phase6c1_generator_payload(skill_id, payload)
    assert ok is True, f"validate failed: {reason}"


def _monkeypatch_forbid_legacy_skill_import(
    monkeypatch: pytest.MonkeyPatch, blocked_skill_id: str
) -> None:
    legacy_module = f"skills.{blocked_skill_id}"
    original = importlib.import_module

    def _wrapped(name: str, package=None):
        if name == legacy_module:
            pytest.fail(f"unexpected legacy import: {name}")
        return original(name, package)

    monkeypatch.setattr(importlib, "import_module", _wrapped)


# ═══ A. Generator tests ══════════════════════════════════════════════════════

class TestGeneratorEventOperationProbability:
    @pytest.mark.parametrize("seed", [1, 2, 3, 7, 13, 21, 42, 99, 100, 137])
    def test_basic_payload(self, seed: int) -> None:
        p = event_operation_probability(
            skill_id=SKILL_PROB_OPS,
            subskill_id="b4_ch2_prob_ops_event_op_01",
            seed=seed,
        )
        _assert_payload_basics(
            p, skill_id=SKILL_PROB_OPS, pid=EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID
        )
        assert p["answer_type"] == "rational_fraction"
        # Answer must be a reduced fraction or integer string in [0, 1].
        if "/" in p["answer"]:
            n, d = map(int, p["answer"].split("/", 1))
            assert d > 0
            assert 0 <= n <= d
            from math import gcd
            assert gcd(abs(n), d) == 1
        else:
            assert p["answer"] in ("0", "1")

    @pytest.mark.parametrize("seed", [1, 5, 11, 17, 25, 30, 41])
    def test_checker_accepts_canonical(self, seed: int) -> None:
        p = event_operation_probability(
            skill_id=SKILL_PROB_OPS,
            subskill_id="b4_ch2_prob_ops_event_op_01",
            seed=seed,
        )
        ans = p["answer"]
        f = _frac(ans)
        assert check_rational_answer(ans, f.numerator, f.denominator) is True
        # Probability rational: unreduced equivalent should also pass.
        assert check_rational_answer(
            f"{f.numerator * 2}/{f.denominator * 2}", f.numerator, f.denominator
        ) is True


class TestGeneratorProbabilityAlgebraMixed:
    @pytest.mark.parametrize("seed", [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 19, 50])
    def test_basic_payload(self, seed: int) -> None:
        p = probability_algebra_mixed(
            skill_id=SKILL_PROB_OPS,
            subskill_id="b4_ch2_prob_ops_algebra_mixed_01",
            seed=seed,
        )
        _assert_payload_basics(
            p, skill_id=SKILL_PROB_OPS, pid=PROBABILITY_ALGEBRA_MIXED_PROBLEM_TYPE_ID
        )
        assert p["answer_type"] == "rational_fraction"

    @pytest.mark.parametrize("seed", [0, 3, 7, 11, 23, 41])
    def test_checker_accepts_decimal_and_percent(self, seed: int) -> None:
        p = probability_algebra_mixed(
            skill_id=SKILL_PROB_OPS,
            subskill_id="b4_ch2_prob_ops_algebra_mixed_01",
            seed=seed,
        )
        ans = p["answer"]
        f = _frac(ans)
        assert check_rational_answer(ans, f.numerator, f.denominator) is True
        # decimal equivalence: only assert when terminating.
        tmp = f.denominator
        while tmp % 2 == 0:
            tmp //= 2
        while tmp % 5 == 0:
            tmp //= 5
        if tmp == 1:
            decimal_str = f"{float(f):g}"
            assert check_rational_answer(decimal_str, f.numerator, f.denominator) is True


class TestGeneratorSetOperationCount:
    @pytest.mark.parametrize("seed", [0, 1, 2, 3, 4, 5, 7, 11, 23, 50])
    def test_basic_payload(self, seed: int) -> None:
        p = set_operation_count(
            skill_id=SKILL_BASIC_SETS,
            subskill_id="b4_ch2_basic_sets_op_count_01",
            seed=seed,
        )
        _assert_payload_basics(
            p, skill_id=SKILL_BASIC_SETS, pid=SET_OPERATION_COUNT_PROBLEM_TYPE_ID
        )
        assert p["answer_type"] == "integer"
        assert isinstance(p["answer"], int)
        assert p["answer"] >= 0

    @pytest.mark.parametrize("seed", [1, 7, 13, 25, 50])
    def test_checker_strict_integer(self, seed: int) -> None:
        p = set_operation_count(
            skill_id=SKILL_BASIC_SETS,
            subskill_id="b4_ch2_basic_sets_op_count_01",
            seed=seed,
        )
        ans = p["answer"]
        assert check_integer_answer(str(ans), int(ans)) is True
        assert check_integer_answer(int(ans), int(ans)) is True
        # Decimal / percent / fraction-form must be rejected.
        assert check_integer_answer(f"{ans}.0", int(ans)) is False
        assert check_integer_answer(f"{ans}%", int(ans)) is False
        assert check_integer_answer(f"{ans}/1", int(ans)) is False

    def test_does_not_request_subset_listing(self) -> None:
        # Phase 6K explicitly forbids subset_listing in the deterministic path.
        for s in range(1, 30):
            p = set_operation_count(
                skill_id=SKILL_BASIC_SETS,
                subskill_id="b4_ch2_basic_sets_op_count_01",
                seed=s,
            )
            qt = p["question_text"]
            assert "請列出" not in qt
            assert "請寫出所有" not in qt


class TestGeneratorInclusionExclusionCount:
    @pytest.mark.parametrize("seed", [0, 1, 2, 3, 5, 9, 13, 27, 99])
    def test_basic_payload(self, seed: int) -> None:
        p = inclusion_exclusion_count(
            skill_id=SKILL_BASIC_SETS,
            subskill_id="b4_ch2_basic_sets_inex_count_01",
            seed=seed,
        )
        _assert_payload_basics(
            p, skill_id=SKILL_BASIC_SETS, pid=INCLUSION_EXCLUSION_COUNT_PROBLEM_TYPE_ID
        )
        assert p["answer_type"] == "integer"
        assert isinstance(p["answer"], int)
        assert p["answer"] >= 0

    @pytest.mark.parametrize("seed", [1, 4, 8, 17, 32])
    def test_checker_rejects_non_integer_forms(self, seed: int) -> None:
        p = inclusion_exclusion_count(
            skill_id=SKILL_BASIC_SETS,
            subskill_id="b4_ch2_basic_sets_inex_count_01",
            seed=seed,
        )
        ans = p["answer"]
        assert check_integer_answer(str(ans), int(ans)) is True
        assert check_integer_answer(f"{ans}.0", int(ans)) is False
        assert check_integer_answer(f"{ans}%", int(ans)) is False


class TestGeneratorExpectationWordProblemProfitFairness:
    """Phase 6K-D: textbook alignment + 4-scenario variety repair."""

    EXPECTED_SCENARIOS = {"lottery", "game_fee", "fair_fee", "ball_draw"}

    @pytest.mark.parametrize("seed", [0, 1, 2, 3, 5, 8, 13, 21, 34])
    def test_basic_payload(self, seed: int) -> None:
        p = expectation_word_problem_profit_fairness(
            skill_id=SKILL_APP_EXP,
            subskill_id="b4_ch2_app_exp_lottery_01",
            seed=seed,
        )
        _assert_payload_basics(
            p,
            skill_id=SKILL_APP_EXP,
            pid=EXPECTATION_WORD_PROBLEM_PROFIT_FAIRNESS_PROBLEM_TYPE_ID,
        )
        assert p["answer_type"] == "expected_value"
        # Textbook scope guard: must avoid 保險精算 / 投資報酬 / 大學機率論 / 抽象語句.
        qt = p["question_text"]
        for forbidden in (
            "保險", "保費", "投資報酬", "股票", "債券",
            "隨機權重", "隨機分割", "W ∈",
        ):
            assert forbidden not in qt, f"forbidden token {forbidden!r} in: {qt}"
        # Scenario id must be one of the 4 textbook templates.
        assert p["parameters"]["scenario_id"] in self.EXPECTED_SCENARIOS
        # Answer must be a reduced fraction string or integer-form.
        f = _frac(p["answer"])
        from math import gcd
        assert gcd(abs(f.numerator), f.denominator) == 1

    @pytest.mark.parametrize("seed", [0, 4, 11, 25])
    def test_checker_accepts_fraction_and_decimal_rejects_percent(self, seed: int) -> None:
        p = expectation_word_problem_profit_fairness(
            skill_id=SKILL_APP_EXP,
            subskill_id="b4_ch2_app_exp_lottery_01",
            seed=seed,
        )
        ans = p["answer"]
        assert check_expected_value_answer(ans, ans) is True
        f = _frac(ans)
        un = f"{f.numerator * 2}/{f.denominator * 2}"
        assert check_expected_value_answer(un, ans) is True
        tmp = f.denominator
        while tmp % 2 == 0:
            tmp //= 2
        while tmp % 5 == 0:
            tmp //= 5
        if tmp == 1:
            assert check_expected_value_answer(f"{float(f):g}", ans) is True
        assert check_expected_value_answer(f"{ans}%", ans) is False

    def test_scenario_diversity_across_seeds(self) -> None:
        """Phase 6K-D: must observe ≥3 distinct scenarios within 24 seeds.

        Lottery alone must NOT dominate (≤ ~1/2 share) — manual smoke fix.
        """
        from collections import Counter

        ctr: Counter = Counter()
        for s in range(0, 24):
            p = expectation_word_problem_profit_fairness(
                skill_id=SKILL_APP_EXP,
                subskill_id="b4_ch2_app_exp_var_div",
                seed=s,
            )
            ctr[p["parameters"]["scenario_id"]] += 1
        distinct = set(ctr.keys())
        assert len(distinct) >= 3, f"scenario diversity too low: {dict(ctr)}"
        # All seen scenarios must be in textbook-aligned 4 set.
        assert distinct.issubset(self.EXPECTED_SCENARIOS), f"unexpected scenarios: {distinct}"
        # Lottery share must not dominate (was 100% before 6K-D).
        lottery_share = ctr.get("lottery", 0) / max(1, sum(ctr.values()))
        assert lottery_share <= 0.5, f"lottery still dominates: {dict(ctr)}"

    def test_explanation_contains_formula_and_substitution(self) -> None:
        """Phase 6K-D Section 4: explanation must show E(X) formula + substitution."""
        for s in (0, 1, 2, 3, 5, 7):
            p = expectation_word_problem_profit_fairness(
                skill_id=SKILL_APP_EXP,
                subskill_id="b4_ch2_app_exp_explain",
                seed=s,
            )
            ex = p["explanation"]
            assert "E(X)" in ex or "E(\\text{獎金})" in ex
            # Substitution lines: dot or times symbol.
            assert ("\\cdot" in ex) or ("\\times" in ex)


class TestGeneratorExpectationAssessmentNumeric:
    """Phase 6K-D: textbook-style coin/dice/two-coin/distribution-table coverage."""

    EXPECTED_SCENARIOS = {"coin_single", "dice_single", "coin_two", "distribution_table"}

    @pytest.mark.parametrize("seed", [0, 1, 2, 3, 5, 8, 13, 21])
    def test_basic_payload(self, seed: int) -> None:
        p = expectation_assessment_numeric(
            skill_id=SKILL_MATH_EXP,
            subskill_id="b4_ch2_math_exp_assess_numeric_01",
            seed=seed,
        )
        _assert_payload_basics(
            p,
            skill_id=SKILL_MATH_EXP,
            pid=EXPECTATION_ASSESSMENT_NUMERIC_PROBLEM_TYPE_ID,
        )
        assert p["answer_type"] == "expected_value"
        weights = p["parameters"]["weights"]
        s = sum(Fraction(pn, pd) for pn, pd in weights)
        assert s == 1
        # Forbidden complex / abstract contexts (Phase 6K-D §3 禁止清單).
        qt = p["question_text"]
        for forbidden in (
            "保險", "投資", "股票", "債券", "求 x", "求未知數",
            "隨機權重", "隨機分割", "W ∈", "W \\in",
        ):
            assert forbidden not in qt, f"forbidden token {forbidden!r} in: {qt}"
        # Scenario must be one of the 4 textbook templates.
        assert p["parameters"]["scenario_id"] in self.EXPECTED_SCENARIOS

    @pytest.mark.parametrize("seed", [0, 7, 14, 28])
    def test_checker_round_trip(self, seed: int) -> None:
        p = expectation_assessment_numeric(
            skill_id=SKILL_MATH_EXP,
            subskill_id="b4_ch2_math_exp_assess_numeric_01",
            seed=seed,
        )
        ans = p["answer"]
        assert check_expected_value_answer(ans, ans) is True
        assert check_expected_value_answer(f"{ans}%", ans) is False

    def test_scenario_diversity_across_seeds(self) -> None:
        """Phase 6K-D: must observe ≥3 of {coin_single, dice_single, coin_two,
        distribution_table} within 24 seeds, and not dominated by 抽卡 / 圓盤."""
        from collections import Counter

        ctr: Counter = Counter()
        for s in range(0, 24):
            p = expectation_assessment_numeric(
                skill_id=SKILL_MATH_EXP,
                subskill_id="b4_ch2_math_exp_assess_div",
                seed=s,
            )
            ctr[p["parameters"]["scenario_id"]] += 1
        distinct = set(ctr.keys())
        assert len(distinct) >= 3, f"scenario diversity too low: {dict(ctr)}"
        assert distinct.issubset(self.EXPECTED_SCENARIOS), f"unexpected scenarios: {distinct}"

    def test_no_card_or_wheel_dominance(self) -> None:
        """Phase 6K-D §3 禁止：不得大量使用「抽卡 / 圓盤 / 轉動圓盤」."""
        from collections import Counter

        ctr: Counter = Counter()
        for s in range(0, 32):
            p = expectation_assessment_numeric(
                skill_id=SKILL_MATH_EXP,
                subskill_id="b4_ch2_math_exp_no_card_wheel",
                seed=s,
            )
            qt = p["question_text"]
            if "抽卡" in qt or "卡片" in qt or "轉動圓盤" in qt or "圓盤" in qt:
                ctr["card_or_wheel"] += 1
            else:
                ctr["other"] += 1
        # Card/wheel must be a small minority (≤1/4) or absent altogether.
        cw = ctr.get("card_or_wheel", 0)
        total = sum(ctr.values())
        assert cw / max(1, total) <= 0.25, f"card/wheel still dominates: {dict(ctr)}"

    def test_explanation_contains_formula_and_substitution(self) -> None:
        """Phase 6K-D Section 4: explanation must show E(X) formula + substitution."""
        for s in (0, 1, 2, 3, 5, 7):
            p = expectation_assessment_numeric(
                skill_id=SKILL_MATH_EXP,
                subskill_id="b4_ch2_math_exp_explain",
                seed=s,
            )
            ex = p["explanation"]
            assert "E(X)" in ex
            assert ("\\cdot" in ex) or ("\\times" in ex)

    def test_distribution_table_uses_money_or_score_context(self) -> None:
        """Distribution table scenario must use 金額 / 得分 / 元 context, not abstract X."""
        from core.vocational_math_b4.generators.chap2_expectation_extensions import (
            expectation_assessment_numeric as gen,
        )

        seen_dt = False
        for s in range(0, 64):
            p = gen(
                skill_id=SKILL_MATH_EXP,
                subskill_id="b4_ch2_math_exp_dt_context",
                seed=s,
            )
            if p["parameters"]["scenario_id"] != "distribution_table":
                continue
            seen_dt = True
            qt = p["question_text"]
            # Must reference money/score context, not bare abstract X.
            assert ("金額" in qt) or ("分數" in qt) or ("元" in qt) or ("得分" in qt), qt
            # Must not write college-style 「設離散隨機變數 X」 lead-in.
            assert "設離散隨機變數" not in qt
        assert seen_dt, "distribution_table scenario never reached in diversity range"


# ═══ B. Checker boundary tests ═══════════════════════════════════════════════

class TestCheckerBoundaries:
    """Verify the checker contract for each Phase 6K answer type."""

    # -- integer (set_operation_count, inclusion_exclusion_count) --

    def test_integer_canonical_passes(self) -> None:
        assert check_integer_answer("36", 36) is True
        assert check_integer_answer(36, 36) is True

    def test_integer_decimal_form_rejected(self) -> None:
        assert check_integer_answer("36.0", 36) is False

    def test_integer_percent_form_rejected(self) -> None:
        assert check_integer_answer("36%", 36) is False

    def test_integer_fraction_form_rejected(self) -> None:
        assert check_integer_answer("36/1", 36) is False

    def test_integer_wrong_value(self) -> None:
        assert check_integer_answer("35", 36) is False

    # -- rational_fraction (event_operation_probability, probability_algebra_mixed) --

    def test_rational_canonical_passes(self) -> None:
        assert check_rational_answer("1/2", 1, 2) is True

    def test_rational_unreduced_passes(self) -> None:
        assert check_rational_answer("2/4", 1, 2) is True

    def test_rational_decimal_passes(self) -> None:
        assert check_rational_answer("0.5", 1, 2) is True

    def test_rational_percent_passes(self) -> None:
        # check_rational_answer flexible mode allows percent for probability.
        assert check_rational_answer("50%", 1, 2) is True

    def test_rational_wrong_value(self) -> None:
        assert check_rational_answer("3/4", 1, 2) is False

    # -- expected_value (expectation_word_problem_profit_fairness, _assessment_numeric) --

    def test_ev_fraction_passes(self) -> None:
        assert check_expected_value_answer("3/2", "3/2") is True
        assert check_expected_value_answer("6/4", "3/2") is True

    def test_ev_decimal_passes(self) -> None:
        assert check_expected_value_answer("1.5", "3/2") is True

    def test_ev_percent_rejected(self) -> None:
        assert check_expected_value_answer("150%", "3/2") is False
        assert check_expected_value_answer("50%", "1/2") is False

    def test_ev_negative_pass(self) -> None:
        # Expected values can be negative; no probability-range guard.
        assert check_expected_value_answer("-1/2", "-1/2") is True

    def test_ev_wrong_value(self) -> None:
        assert check_expected_value_answer("1/2", "3/2") is False


# ═══ C. Router / allowlist boundary tests ════════════════════════════════════

class TestRouterAllowlist:
    @pytest.mark.parametrize("skill_id, pid", PHASE6K_SKILL_PIDS)
    def test_phase6k_skill_in_allowlist_and_router(self, skill_id: str, pid: str) -> None:
        assert is_b4_chapter2_phase6c1_deterministic_skill(skill_id) is True
        assert is_b4_chapter2_skill_not_enabled_in_phase6c1(skill_id) is False
        assert pid in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES
        p = generate_for_chap2_skill(skill_id=skill_id, problem_type_id=pid, seed=7)
        assert p["skill_id"] == skill_id
        assert p["problem_type_id"] == pid

    @pytest.mark.parametrize("skill_id, pid", PRIOR_SKILL_PID_PAIRS)
    def test_prior_11_problem_types_still_generate(
        self, skill_id: str, pid: str
    ) -> None:
        p = generate_for_chap2_skill(skill_id=skill_id, problem_type_id=pid, seed=11)
        assert p["skill_id"] == skill_id
        assert p["problem_type_id"] == pid
        assert p["question_text"].strip()

    def test_chap2_not_enabled_set_is_empty(self) -> None:
        assert B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS == frozenset()

    def test_allowlist_and_problem_type_count_after_phase6k(self) -> None:
        # 6 prior skills + 4 newly opened in 6K = 10
        assert len(B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST) == 10
        # 11 prior problem types + 6 added in 6K = 17
        assert len(B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES) == 17

    @pytest.mark.parametrize("pid", RESERVED_LISTING_PIDS)
    def test_reserved_listing_remains_excluded(self, pid: str) -> None:
        assert is_b4_chapter2_excluded_problem_type(pid) is True
        assert pid not in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES

    @pytest.mark.parametrize("pid", RESERVED_LISTING_PIDS)
    def test_reserved_listing_payload_validate_blocks(self, pid: str) -> None:
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(
            SKILL_BASIC_SETS, {"problem_type_id": pid}
        )
        assert ok is False
        assert "excluded_handwriting" in reason

    def test_reserved_listing_not_routable(self) -> None:
        # Reserved listing types are not registered to the router for any skill.
        for pid in RESERVED_LISTING_PIDS:
            with pytest.raises(ValueError):
                generate_for_chap2_skill(skill_id=SKILL_BASIC_SETS, problem_type_id=pid)

    def test_unsupported_skill_raises(self) -> None:
        # Truly unsupported (not in any registry) must still raise.
        with pytest.raises(ValueError, match="unsupported skill_id"):
            generate_for_chap2_skill(skill_id="vh_數學B4_NoSuchPhase6KSkill")

    def test_no_legacy_fallback_for_phase6k_skills(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for sid in (SKILL_PROB_OPS, SKILL_BASIC_SETS, SKILL_APP_EXP, SKILL_MATH_EXP):
            _monkeypatch_forbid_legacy_skill_import(monkeypatch, sid)
        # All four must generate without ever importing skills.<id>
        for sid, pid in PHASE6K_SKILL_PIDS:
            p = generate_for_chap2_skill(skill_id=sid, problem_type_id=pid, seed=3)
            assert p["skill_id"] == sid
            assert p["problem_type_id"] == pid


# ═══ D. URL encoding regressions ═════════════════════════════════════════════

class TestUrlEncoding:
    @pytest.mark.parametrize(
        "encoded, expected",
        [
            (ENCODED_PROB_OPS, SKILL_PROB_OPS),
            (ENCODED_BASIC_SETS, SKILL_BASIC_SETS),
            (ENCODED_APP_EXP, SKILL_APP_EXP),
            (ENCODED_MATH_EXP, SKILL_MATH_EXP),
        ],
    )
    def test_decoded_recognized_as_chap2_deterministic(
        self, encoded: str, expected: str
    ) -> None:
        decoded = _url_unquote(encoded)
        assert decoded == expected
        assert is_b4_chapter2_phase6c1_deterministic_skill(decoded) is True

    @pytest.mark.parametrize(
        "encoded",
        [ENCODED_PROB_OPS, ENCODED_BASIC_SETS, ENCODED_APP_EXP, ENCODED_MATH_EXP],
    )
    def test_frontend_double_encoding_round_trip(self, encoded: str) -> None:
        decoded_once = _url_unquote(encoded)
        re_encoded = _url_quote(decoded_once, safe="")
        assert _url_unquote(re_encoded) == decoded_once


# ═══ E. /practice and /get_next_question route integration ═══════════════════

def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"b4_6k_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


class TestPracticeRouteIntegration:
    """Phase 6K skills must serve via /practice and /get_next_question."""

    @pytest.mark.parametrize(
        "skill",
        [SKILL_PROB_OPS, SKILL_BASIC_SETS, SKILL_APP_EXP, SKILL_MATH_EXP],
    )
    def test_practice_decoded_skill_id_returns_200(
        self, logged_client, skill: str
    ) -> None:
        r = logged_client.get(f"/practice?skill={skill}")
        assert r.status_code == 200, r.get_data(as_text=True)

    @pytest.mark.parametrize(
        "encoded",
        [ENCODED_PROB_OPS, ENCODED_BASIC_SETS, ENCODED_APP_EXP, ENCODED_MATH_EXP],
    )
    def test_practice_encoded_skill_id_returns_200(
        self, logged_client, encoded: str
    ) -> None:
        r = logged_client.get(f"/practice?skill={encoded}")
        assert r.status_code == 200, r.get_data(as_text=True)

    @pytest.mark.parametrize(
        "skill, gen_seed",
        [
            (SKILL_PROB_OPS, 41),
            (SKILL_BASIC_SETS, 42),
            (SKILL_APP_EXP, 43),
            (SKILL_MATH_EXP, 44),
        ],
    )
    def test_get_next_question_returns_200_with_payload(
        self, logged_client, skill: str, gen_seed: int
    ) -> None:
        r = logged_client.get(
            f"/get_next_question?skill={skill}&gen_seed={gen_seed}&level=1"
        )
        assert r.status_code == 200, r.get_data(as_text=True)
        body = r.get_json() or {}
        assert body.get("new_question_text")
        assert body.get("problem_type_id")

    @pytest.mark.parametrize(
        "encoded, gen_seed",
        [
            (ENCODED_PROB_OPS, 51),
            (ENCODED_BASIC_SETS, 52),
            (ENCODED_APP_EXP, 53),
            (ENCODED_MATH_EXP, 54),
        ],
    )
    def test_get_next_question_encoded_returns_200(
        self, logged_client, encoded: str, gen_seed: int
    ) -> None:
        r = logged_client.get(
            f"/get_next_question?skill={encoded}&gen_seed={gen_seed}&level=1"
        )
        assert r.status_code == 200, r.get_data(as_text=True)
        body = r.get_json() or {}
        assert body.get("new_question_text")
        assert body.get("problem_type_id")

    @pytest.mark.parametrize(
        "pid",
        ["sample_space_listing", "event_set_listing", "subset_listing"],
    )
    def test_reserved_chap2_listing_problem_types_return_422(
        self, logged_client, pid: str
    ) -> None:
        # Reserved Chap2 listing types must still return the public
        # reserved error message when requested against a Chap2 skill
        # (Phase 6K does NOT open these).
        r = logged_client.get(
            f"/get_next_question?skill=vh_數學B4_SampleSpaceAndEvents&problem_type={pid}"
        )
        assert r.status_code == 422
        body = r.get_json() or {}
        assert body.get("error") == B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR

    def test_tree_diagram_listing_excluded_from_deterministic_allowlist(self) -> None:
        # tree_diagram_listing has its own free-response (handwriting) path
        # under vh_數學B4_TreeDiagramCounting; it must NOT be reachable through
        # the Chap2 deterministic allowlist or generator.
        assert is_b4_chapter2_excluded_problem_type("tree_diagram_listing") is True
        assert "tree_diagram_listing" not in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES
        with pytest.raises(ValueError):
            generate_for_chap2_skill(
                skill_id=SKILL_BASIC_SETS,
                problem_type_id="tree_diagram_listing",
            )


# ═══ F. /check_answer route integration ══════════════════════════════════════

class TestCheckAnswerRouteIntegration:
    """Verify /check_answer integrates the right checker for Phase 6K answer types.

    The /check_answer route reads the current question from server session,
    so the request body only needs the user's ``answer``. The seed used by
    the test must match the seed used to populate the session via
    /get_next_question, so we can recompute the canonical answer
    deterministically and submit it.
    """

    @pytest.mark.parametrize(
        "skill, pid, gen_seed",
        [
            (SKILL_PROB_OPS, EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID, 61),
            (SKILL_PROB_OPS, PROBABILITY_ALGEBRA_MIXED_PROBLEM_TYPE_ID, 62),
            (SKILL_BASIC_SETS, SET_OPERATION_COUNT_PROBLEM_TYPE_ID, 63),
            (SKILL_BASIC_SETS, INCLUSION_EXCLUSION_COUNT_PROBLEM_TYPE_ID, 64),
            (SKILL_APP_EXP, EXPECTATION_WORD_PROBLEM_PROFIT_FAIRNESS_PROBLEM_TYPE_ID, 65),
            (SKILL_MATH_EXP, EXPECTATION_ASSESSMENT_NUMERIC_PROBLEM_TYPE_ID, 66),
        ],
    )
    def test_round_trip_correct_answer_marked_correct(
        self, logged_client, skill: str, pid: str, gen_seed: int
    ) -> None:
        # Recompute canonical answer from the same generator + seed.
        canonical = generate_for_chap2_skill(
            skill_id=skill, problem_type_id=pid, seed=gen_seed, level=1
        )
        correct = str(canonical["answer"]).strip()

        # Drive the practice route with the same seed so the session question
        # matches our recomputed canonical payload.
        r = logged_client.get(
            f"/get_next_question?skill={skill}"
            f"&gen_seed={gen_seed}&level=1&problem_type={pid}"
        )
        assert r.status_code == 200, r.get_data(as_text=True)

        ck = logged_client.post("/check_answer", json={"answer": correct})
        assert ck.status_code == 200, ck.get_data(as_text=True)
        ck_body = ck.get_json() or {}
        assert ck_body.get("correct") is True, (
            f"expected correct=True for canonical answer {correct!r}, got: {ck_body}"
        )

    @pytest.mark.parametrize(
        "skill, pid, gen_seed, wrong_answer",
        [
            (SKILL_BASIC_SETS, SET_OPERATION_COUNT_PROBLEM_TYPE_ID, 63, "999999"),
            (SKILL_PROB_OPS, EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID, 61, "0"),
            (SKILL_APP_EXP, EXPECTATION_WORD_PROBLEM_PROFIT_FAIRNESS_PROBLEM_TYPE_ID, 65, "0"),
        ],
    )
    def test_round_trip_wrong_answer_marked_incorrect(
        self,
        logged_client,
        skill: str,
        pid: str,
        gen_seed: int,
        wrong_answer: str,
    ) -> None:
        canonical = generate_for_chap2_skill(
            skill_id=skill, problem_type_id=pid, seed=gen_seed, level=1
        )
        # Make sure the chosen wrong_answer is genuinely wrong.
        if str(canonical["answer"]).strip() == wrong_answer:
            wrong_answer = "-987654"

        r = logged_client.get(
            f"/get_next_question?skill={skill}"
            f"&gen_seed={gen_seed}&level=1&problem_type={pid}"
        )
        assert r.status_code == 200, r.get_data(as_text=True)

        ck = logged_client.post("/check_answer", json={"answer": wrong_answer})
        assert ck.status_code == 200, ck.get_data(as_text=True)
        ck_body = ck.get_json() or {}
        assert ck_body.get("correct") is False, (
            f"expected correct=False for wrong answer {wrong_answer!r}, got: {ck_body}"
        )


# ═══ G. Audit visibility regression ══════════════════════════════════════════

class TestAuditVisibilityRegression:
    """Phase 6K must not break the existing visibility audit logging path."""

    def test_audit_helper_module_imports_cleanly(self) -> None:
        from core.vocational_math_b4.services import b4_chap2_visibility_audit  # noqa: F401
        from models import B4Chap2VisibilityAuditLog  # noqa: F401

    def test_phase6k_deterministic_answer_writes_audit_log(
        self, logged_client
    ) -> None:
        from models import B4Chap2VisibilityAuditLog

        r = logged_client.get(
            f"/get_next_question?skill={SKILL_PROB_OPS}&gen_seed=71&level=1"
            f"&problem_type={EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID}"
        )
        assert r.status_code == 200, r.get_data(as_text=True)
        body = r.get_json() or {}
        qid = body.get("question_id")
        correct = body.get("correct_answer") or body.get("answer")

        app = logged_client.application
        with app.app_context():
            before = (
                db.session.query(B4Chap2VisibilityAuditLog)
                .filter_by(
                    skill_id=SKILL_PROB_OPS,
                    record_kind="deterministic_answer",
                )
                .count()
            )

        ck = logged_client.post(
            "/check_answer",
            json={
                "question_id": qid,
                "user_answer": str(correct),
                "skill_id": SKILL_PROB_OPS,
                "problem_type_id": EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID,
            },
        )
        assert ck.status_code == 200

        with app.app_context():
            after = (
                db.session.query(B4Chap2VisibilityAuditLog)
                .filter_by(
                    skill_id=SKILL_PROB_OPS,
                    record_kind="deterministic_answer",
                )
                .count()
            )
        assert after >= before + 1, (
            f"deterministic_answer audit row not written: before={before} after={after}"
        )

    def test_phase6k_skills_not_logged_as_gated_not_enabled(
        self, logged_client
    ) -> None:
        from models import B4Chap2VisibilityAuditLog

        app = logged_client.application
        with app.app_context():
            before_gated = (
                db.session.query(B4Chap2VisibilityAuditLog)
                .filter_by(
                    skill_id=SKILL_BASIC_SETS,
                    record_kind="gated",
                    gated_event_type="not_enabled_skill",
                )
                .count()
            )
        r = logged_client.get(
            f"/get_next_question?skill={SKILL_BASIC_SETS}&gen_seed=72&level=1"
        )
        assert r.status_code == 200
        with app.app_context():
            after_gated = (
                db.session.query(B4Chap2VisibilityAuditLog)
                .filter_by(
                    skill_id=SKILL_BASIC_SETS,
                    record_kind="gated",
                    gated_event_type="not_enabled_skill",
                )
                .count()
            )
        assert after_gated == before_gated, (
            "Phase 6K skill must not trigger not_enabled_skill gated audit"
        )

    def test_reserved_listing_still_writes_gated_audit(
        self, logged_client
    ) -> None:
        from models import B4Chap2VisibilityAuditLog

        app = logged_client.application
        with app.app_context():
            before_gated = (
                db.session.query(B4Chap2VisibilityAuditLog)
                .filter_by(
                    record_kind="gated",
                    gated_event_type="reserved_problem_type",
                )
                .count()
            )
        r = logged_client.get(
            "/get_next_question?skill=vh_數學B4_SampleSpaceAndEvents"
            "&problem_type=sample_space_listing"
        )
        assert r.status_code == 422
        with app.app_context():
            after_gated = (
                db.session.query(B4Chap2VisibilityAuditLog)
                .filter_by(
                    record_kind="gated",
                    gated_event_type="reserved_problem_type",
                )
                .count()
            )
        assert after_gated >= before_gated + 1, (
            "reserved listing must still write gated audit row"
        )
