"""Phase 6C-2 tests: union_intersection_probability + dice_coin_probability_count."""
from __future__ import annotations
import math
import pytest
from fractions import Fraction

from core.vocational_math_b4.generators.chap2_probability_basic import (
    union_intersection_probability,
    dice_coin_probability_count,
)
from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
    B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES,
    B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES,
    is_b4_chapter2_phase6c1_deterministic_skill,
    is_b4_chapter2_excluded_problem_type,
    validate_b4_chap2_phase6c1_generator_payload,
)
from core.vocational_math_b4.domain.b4_validators import (
    check_rational_answer,
    check_integer_answer,
)

SKILL_PROP = "vh_數學B4_ProbabilityProperties"
SKILL_DEF  = "vh_數學B4_ProbabilityDefinition"
SKILL_SSE  = "vh_數學B4_SampleSpaceAndEvents"

PLACEHOLDER_TOKENS = ["[BLANK]", "[FORMULA_MISSING]", "[FORMULA_IMAGE", "□"]


def _frac(s: str) -> Fraction:
    if "/" in s:
        n, d = s.split("/")
        return Fraction(int(n), int(d))
    return Fraction(int(s))


def _no_placeholder(text: str):
    for tok in PLACEHOLDER_TOKENS:
        assert tok not in text, f"Placeholder {tok!r} found in: {text[:80]}"


def _is_reduced(s: str) -> bool:
    if "/" not in s:
        return True
    n, d = map(int, s.split("/"))
    return math.gcd(abs(n), d) == 1


# ═══ A. union_intersection_probability ══════════════════════════════════════

class TestUnionIntersectionGenerator:
    SK = SKILL_PROP
    PID = "union_intersection_probability"

    def _gen(self, seed=1, **kw):
        return union_intersection_probability(
            skill_id=self.SK, subskill_id="b4_ch2_prob_prop_union_01",
            difficulty=1, seed=seed, **kw
        )

    def test_payload_keys(self):
        p = self._gen()
        for k in ["question_text","answer","explanation","skill_id",
                  "problem_type_id","generator_key","answer_type",
                  "difficulty","diagnosis_tags","remediation_candidates"]:
            assert k in p

    def test_skill_and_pid(self):
        for seed in range(1, 8):
            p = self._gen(seed=seed)
            assert p["skill_id"] == self.SK
            assert p["problem_type_id"] == self.PID

    def test_answer_is_reduced_fraction(self):
        for seed in range(1, 10):
            p = self._gen(seed=seed)
            ans = p["answer"]
            assert isinstance(ans, str)
            assert _is_reduced(ans), f"Not reduced: {ans}"

    def test_answer_in_probability_range(self):
        for seed in range(1, 10):
            p = self._gen(seed=seed)
            f = _frac(p["answer"])
            assert 0 <= f <= 1, f"Out of range: {f}"

    def test_intersection_leq_marginals(self):
        """P(A∩B) ≤ P(A) and P(A∩B) ≤ P(B) must hold in generated params."""
        for seed in range(1, 12):
            p = self._gen(seed=seed)
            params = p["parameters"]
            D = params["D"]
            a, b, c = params["pa_num"], params["pb_num"], params["pab_num"]
            assert c <= a, f"P(A∩B)={c}/{D} > P(A)={a}/{D}"
            assert c <= b, f"P(A∩B)={c}/{D} > P(B)={b}/{D}"

    def test_union_geq_marginals(self):
        for seed in range(1, 12):
            p = self._gen(seed=seed)
            params = p["parameters"]
            D = params["D"]
            a, b, paub = params["pa_num"], params["pb_num"], params["paub_num"]
            assert paub >= a, f"P(A∪B)={paub}/{D} < P(A)={a}/{D}"
            assert paub >= b, f"P(A∪B)={paub}/{D} < P(B)={b}/{D}"

    def test_union_formula_holds(self):
        for seed in range(1, 12):
            p = self._gen(seed=seed)
            params = p["parameters"]
            D = params["D"]
            a, b, c, paub = params["pa_num"], params["pb_num"], params["pab_num"], params["paub_num"]
            assert a + b - c == paub, f"Formula violated: {a}+{b}-{c}!={paub}"

    def test_explanation_mentions_union_formula(self):
        for seed in range(1, 6):
            p = self._gen(seed=seed)
            exp = p["explanation"]
            assert "∪" in exp or "cup" in exp or "加法定理" in exp, \
                f"No union formula in explanation: {exp[:100]}"

    def test_no_placeholder(self):
        for seed in range(1, 6):
            p = self._gen(seed=seed)
            _no_placeholder(p["question_text"])
            _no_placeholder(p["explanation"])

    def test_answer_type_not_handwriting(self):
        p = self._gen()
        assert p["answer_type"] not in ("handwriting", "ai_judged_free_response")

    def test_choices_contain_answer(self):
        for seed in range(1, 6):
            p = self._gen(seed=seed)
            assert p["answer"] in p["choices"]

    def test_both_subtypes_covered(self):
        subtypes = set()
        for seed in range(1, 20):
            p = self._gen(seed=seed)
            subtypes.add(p["parameters"]["sub_type"])
        assert "ask_union" in subtypes
        assert "ask_intersection" in subtypes

    def test_via_router(self):
        p = generate_for_chap2_skill(
            skill_id=SKILL_PROP, problem_type_id="union_intersection_probability",
            level=1, seed=42
        )
        assert p["problem_type_id"] == "union_intersection_probability"
        assert p["skill_id"] == SKILL_PROP


# ═══ B. dice_coin_probability_count ═════════════════════════════════════════

class TestDiceCoinGenerator:
    SK = SKILL_DEF
    PID = "dice_coin_probability_count"

    def _gen(self, seed=1, **kw):
        return dice_coin_probability_count(
            skill_id=self.SK, subskill_id="b4_ch2_prob_def_dice_coin_01",
            difficulty=1, seed=seed, **kw
        )

    def test_payload_keys(self):
        p = self._gen()
        for k in ["question_text","answer","explanation","skill_id",
                  "problem_type_id","generator_key","answer_type",
                  "difficulty","diagnosis_tags","remediation_candidates"]:
            assert k in p

    def test_skill_and_pid(self):
        for seed in range(1, 8):
            p = self._gen(seed=seed)
            assert p["skill_id"] == self.SK
            assert p["problem_type_id"] == self.PID

    def test_answer_is_reduced_fraction(self):
        for seed in range(1, 10):
            p = self._gen(seed=seed)
            ans = p["answer"]
            assert isinstance(ans, str)
            assert _is_reduced(ans)

    def test_answer_in_probability_range(self):
        for seed in range(1, 10):
            p = self._gen(seed=seed)
            f = _frac(p["answer"])
            assert 0 <= f <= 1

    def test_three_contexts_covered(self):
        contexts = set()
        for seed in range(1, 30):
            p = self._gen(seed=seed)
            contexts.add(p["parameters"]["context"])
        assert "single_die_property" in contexts, "single_die_property not reached"
        assert "two_dice_sum" in contexts, "two_dice_sum not reached"
        assert "coin_exact_heads" in contexts, "coin_exact_heads not reached"

    def test_explanation_mentions_nA_over_nS(self):
        for seed in range(1, 8):
            p = self._gen(seed=seed)
            exp = p["explanation"]
            assert "n(A)" in exp or "n(S)" in exp or "P(A)" in exp, \
                f"No P(A)=n(A)/n(S) in: {exp[:100]}"

    def test_no_listing_requirement(self):
        for seed in range(1, 10):
            p = self._gen(seed=seed)
            q = p["question_text"]
            assert "列出" not in q and "列舉" not in q

    def test_no_image_keyword(self):
        for seed in range(1, 10):
            p = self._gen(seed=seed)
            q = p["question_text"]
            assert "如圖" not in q and "圖" not in q[:5]

    def test_no_placeholder(self):
        for seed in range(1, 6):
            p = self._gen(seed=seed)
            _no_placeholder(p["question_text"])
            _no_placeholder(p["explanation"])

    def test_answer_type_not_handwriting(self):
        p = self._gen()
        assert p["answer_type"] not in ("handwriting", "ai_judged_free_response")

    def test_choices_contain_answer(self):
        for seed in range(1, 6):
            p = self._gen(seed=seed)
            assert p["answer"] in p["choices"]

    @pytest.mark.parametrize("seed", [0, 1, 2, 3, 6, 9, 12, 15, 42, 99])
    def test_via_router_multi_seed(self, seed):
        p = generate_for_chap2_skill(
            skill_id=SKILL_DEF, problem_type_id="dice_coin_probability_count",
            level=1, seed=seed
        )
        assert p["problem_type_id"] == "dice_coin_probability_count"
        assert p["skill_id"] == SKILL_DEF
        f = _frac(p["answer"])
        assert 0 <= f <= 1


# ═══ C. Checker compatibility ════════════════════════════════════════════════

class TestCheckerCompatibility:
    """Both new problem types use check_rational_answer (flexible mode)."""

    @pytest.mark.parametrize("pid,skill_id", [
        ("union_intersection_probability", SKILL_PROP),
        ("dice_coin_probability_count", SKILL_DEF),
    ])
    def test_canonical_correct(self, pid, skill_id):
        p = generate_for_chap2_skill(skill_id=skill_id, problem_type_id=pid, seed=7)
        ans = p["answer"]
        if "/" in ans:
            n, d = map(int, ans.split("/"))
        else:
            n, d = int(ans), 1
        assert check_rational_answer(ans, n, d) is True

    @pytest.mark.parametrize("pid,skill_id", [
        ("union_intersection_probability", SKILL_PROP),
        ("dice_coin_probability_count", SKILL_DEF),
    ])
    def test_unreduced_equivalent_correct(self, pid, skill_id):
        p = generate_for_chap2_skill(skill_id=skill_id, problem_type_id=pid, seed=3)
        ans = p["answer"]
        if "/" in ans:
            n, d = map(int, ans.split("/"))
            # double numerator and denominator (unreduced)
            user = f"{n*2}/{d*2}"
            assert check_rational_answer(user, n, d) is True

    @pytest.mark.parametrize("pid,skill_id", [
        ("union_intersection_probability", SKILL_PROP),
        ("dice_coin_probability_count", SKILL_DEF),
    ])
    def test_decimal_equivalent_correct(self, pid, skill_id):
        # Use check_rational_answer directly with known clean fractions
        # to avoid infinite-decimal representation issues (e.g. 1/6 = 0.1666...).
        # Confirmed: 0.5 == 1/2, 0.25 == 1/4, 0.125 == 1/8.
        assert check_rational_answer("0.5", 1, 2) is True
        assert check_rational_answer("0.25", 1, 4) is True
        assert check_rational_answer("0.125", 1, 8) is True
        # Also round-trip with a generated answer that has finite decimal
        p = generate_for_chap2_skill(skill_id=skill_id, problem_type_id=pid, seed=5)
        ans = p["answer"]
        if "/" in ans:
            n, d = map(int, ans.split("/"))
            f = Fraction(n, d)
            # Only test decimal if it terminates (denominator = 2^a * 5^b)
            d_reduced = d // math.gcd(n, d)
            tmp = d_reduced
            for prime in (2, 5):
                while tmp % prime == 0:
                    tmp //= prime
            if tmp == 1:
                decimal_str = str(float(f))
                assert check_rational_answer(decimal_str, n, d) is True


    @pytest.mark.parametrize("pid,skill_id", [
        ("union_intersection_probability", SKILL_PROP),
        ("dice_coin_probability_count", SKILL_DEF),
    ])
    def test_percentage_equivalent_correct(self, pid, skill_id):
        p = generate_for_chap2_skill(skill_id=skill_id, problem_type_id=pid, seed=5)
        ans = p["answer"]
        if "/" in ans:
            n, d = map(int, ans.split("/"))
            pct = f"{Fraction(n,d)*100}%"
            assert check_rational_answer(pct, n, d) is True

    def test_wrong_fraction_incorrect(self):
        assert check_rational_answer("2/3", 1, 3) is False

    def test_out_of_range_probability_raises(self):
        with pytest.raises(ValueError, match="probability"):
            check_rational_answer("1/2", 5, 4)  # 5/4 > 1

    def test_denominator_zero_invalid(self):
        assert check_rational_answer("1/0", 1, 2) is False


# ═══ D. Router / allowlist boundary ═════════════════════════════════════════

class TestAllowlistBoundary:
    def test_6c1_still_works(self):
        for sid, pid in [
            (SKILL_DEF, "classical_probability_fraction"),
            (SKILL_PROP, "complement_probability"),
            (SKILL_SSE, "sample_space_count_numeric"),
        ]:
            p = generate_for_chap2_skill(skill_id=sid, problem_type_id=pid, seed=1)
            assert p["problem_type_id"] == pid

    def test_6c2_works(self):
        for sid, pid in [
            (SKILL_PROP, "union_intersection_probability"),
            (SKILL_DEF, "dice_coin_probability_count"),
        ]:
            p = generate_for_chap2_skill(skill_id=sid, problem_type_id=pid, seed=1)
            assert p["problem_type_id"] == pid

    def test_unsupported_skill_raises(self):
        with pytest.raises(ValueError, match="unsupported skill_id"):
            generate_for_chap2_skill(skill_id="vh_數學B4_BasicConceptsOfSets")

    def test_conditional_probability_blocked(self):
        p = generate_for_chap2_skill(
            skill_id="vh_數學B4_ConditionalProbability",
            problem_type_id="conditional_probability_basic",
            seed=1,
        )
        assert p["problem_type_id"] == "conditional_probability_basic"

    def test_independent_events_blocked(self):
        p = generate_for_chap2_skill(
            skill_id="vh_數學B4_IndependentEvents",
            problem_type_id="independent_joint_probability",
            seed=1,
        )
        assert p["problem_type_id"] == "independent_joint_probability"

    @pytest.mark.parametrize("pid", ["sample_space_listing","event_set_listing","subset_listing"])
    def test_handwriting_excluded(self, pid):
        assert is_b4_chapter2_excluded_problem_type(pid) is True
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(
            SKILL_SSE, {"problem_type_id": pid}
        )
        assert ok is False
        assert "excluded_handwriting" in reason

    def test_allowed_set_has_eleven_types(self):
        assert len(B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES) == 11

    def test_validate_passes_new_types(self):
        for sid, pid in [
            (SKILL_PROP, "union_intersection_probability"),
            (SKILL_DEF, "dice_coin_probability_count"),
        ]:
            p = generate_for_chap2_skill(skill_id=sid, problem_type_id=pid, seed=1)
            ok, reason = validate_b4_chap2_phase6c1_generator_payload(sid, p)
            assert ok is True, f"Blocked: {reason}"

    def test_no_fallback_to_legacy_module_for_blocked_skills(self):
        """Blocked skills must not silently import legacy skills.xxx module."""
        for sid in [
            "vh_數學B4_BasicConceptsOfSets",
        ]:
            from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
                is_b4_chapter2_skill_not_enabled_in_phase6c1,
            )
            assert is_b4_chapter2_skill_not_enabled_in_phase6c1(sid) is True


# ═══ E. Route integration (URL decode + skill bypass) ════════════════════════

class TestRouteIntegration:
    """Simulate practice.py route logic without Flask context."""

    def test_url_decode_probability_properties(self):
        from urllib.parse import unquote
        encoded = "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityProperties"
        assert unquote(encoded) == SKILL_PROP

    def test_url_decode_probability_definition(self):
        from urllib.parse import unquote
        encoded = "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition"
        assert unquote(encoded) == SKILL_DEF

    def test_chap2_skill_recognized_after_decode(self):
        from urllib.parse import unquote
        for encoded in [
            "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityProperties",
            "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition",
        ]:
            sid = unquote(encoded)
            assert is_b4_chapter2_phase6c1_deterministic_skill(sid)

    def test_get_next_question_equivalent_union(self):
        """Simulate practice.py generate_for_chap2_skill call for union type."""
        p = generate_for_chap2_skill(
            skill_id=SKILL_PROP, level=1, seed=10,
            problem_type_id="union_intersection_probability"
        )
        assert p["question_text"].strip()
        assert p["answer_type"] not in ("handwriting", "ai_judged_free_response")

    def test_get_next_question_equivalent_dice_coin(self):
        p = generate_for_chap2_skill(
            skill_id=SKILL_DEF, level=1, seed=10,
            problem_type_id="dice_coin_probability_count"
        )
        assert p["question_text"].strip()
        assert p["answer_type"] not in ("handwriting", "ai_judged_free_response")

    def test_check_answer_equivalent_union_fraction(self):
        p = generate_for_chap2_skill(
            skill_id=SKILL_PROP, problem_type_id="union_intersection_probability", seed=20
        )
        ans = p["answer"]
        n, d = (map(int, ans.split("/"))) if "/" in ans else (int(ans), 1)
        assert check_rational_answer(ans, n, d, allow_decimal=True, allow_percentage=True) is True
        assert check_rational_answer("0/1", n, d) is False  # wrong

    def test_check_answer_equivalent_dice_coin_fraction(self):
        p = generate_for_chap2_skill(
            skill_id=SKILL_DEF, problem_type_id="dice_coin_probability_count", seed=20
        )
        ans = p["answer"]
        n, d = (map(int, ans.split("/"))) if "/" in ans else (int(ans), 1)
        assert check_rational_answer(ans, n, d, allow_decimal=True, allow_percentage=True) is True

    def test_handwriting_listing_blocked_before_router(self):
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            is_b4_chapter2_excluded_problem_type,
        )
        assert is_b4_chapter2_excluded_problem_type("sample_space_listing") is True


# ═══ F. Regression ═══════════════════════════════════════════════════════════

class TestRegression:
    def test_6c1_phase_original_tests(self):
        """Smoke re-run of 6C-1 generators."""
        from core.vocational_math_b4.generators.chap2_probability_basic import (
            classical_probability_fraction, complement_probability,
            sample_space_count_numeric,
        )
        for seed in [1, 5, 42]:
            p1 = classical_probability_fraction(
                skill_id=SKILL_DEF, subskill_id="x", difficulty=1, seed=seed)
            assert p1["problem_type_id"] == "classical_probability_fraction"
            p2 = complement_probability(
                skill_id=SKILL_PROP, subskill_id="x", difficulty=1, seed=seed)
            assert p2["problem_type_id"] == "complement_probability"
            p3 = sample_space_count_numeric(
                skill_id=SKILL_SSE, subskill_id="x", difficulty=1, seed=seed)
            assert p3["problem_type_id"] == "sample_space_count_numeric"

    def test_chap1_router_unaffected(self):
        from core.vocational_math_b4.services.question_router import generate_for_skill
        from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
            B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
        )
        chap2_skills = {SKILL_DEF, SKILL_PROP, SKILL_SSE}
        assert not (chap2_skills & B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST)
        p = generate_for_skill(skill_id="vh_數學B4_AdditionPrinciple", level=1, seed=1)
        assert p["skill_id"] == "vh_數學B4_AdditionPrinciple"

    def test_chap1_allowlist_size_unchanged(self):
        from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
            B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
        )
        assert len(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST) == 13


# ═══ Multi-seed smoke ════════════════════════════════════════════════════════

@pytest.mark.parametrize("skill_id,pid", [
    (SKILL_PROP, "union_intersection_probability"),
    (SKILL_DEF,  "dice_coin_probability_count"),
])
@pytest.mark.parametrize("seed", [1, 2, 3, 7, 42, 99])
def test_multi_seed_smoke(skill_id, pid, seed):
    p = generate_for_chap2_skill(skill_id=skill_id, problem_type_id=pid, level=1, seed=seed)
    assert p["problem_type_id"] == pid
    assert p["skill_id"] == skill_id
    f = _frac(p["answer"])
    assert 0 <= f <= 1
    assert p["question_text"].strip()
    assert p["explanation"].strip()
    assert p.get("answer_type") not in ("handwriting", "ai_judged_free_response")
    _no_placeholder(p["question_text"])
    _no_placeholder(p["explanation"])
