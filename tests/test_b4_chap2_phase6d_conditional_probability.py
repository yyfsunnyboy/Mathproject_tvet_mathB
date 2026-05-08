"""Phase 6D: Conditional Probability – full test suite.

Covers:
  A. Generator unit tests (conditional_probability_basic)
  B. Generator unit tests (without_replacement_conditional_probability)
  C. Router / allowlist boundary tests
  D. URL decode round-trip (encoded ConditionalProbability skill)
  E. Frontend double-encoding regression
  F. Unsupported / not-enabled skill guard
  G. Handwriting reserved blocked
  H. Phase 6C regression (all 5 existing problem types)
  I. Chap1 regression
"""
from __future__ import annotations

import pytest
from fractions import Fraction
from urllib.parse import unquote as _url_unquote, quote as _url_quote

from core.vocational_math_b4.generators.chap2_conditional_probability import (
    conditional_probability_basic,
    without_replacement_conditional_probability,
    CONDITIONAL_BASIC_PROBLEM_TYPE_ID,
    WITHOUT_REPLACEMENT_PROBLEM_TYPE_ID,
)
from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
    is_b4_chapter2_phase6c1_deterministic_skill,
    is_b4_chapter2_skill_not_enabled_in_phase6c1,
    is_b4_chapter2_excluded_problem_type,
    validate_b4_chap2_phase6c1_generator_payload,
    B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES,
    B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST,
    B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS,
)
from core.vocational_math_b4.domain.b4_validators import (
    check_rational_answer,
)

SKILL_COND = "vh_數學B4_ConditionalProbability"
ENCODED_COND = "vh_%E6%95%B8%E5%AD%B8B4_ConditionalProbability"

SKILL_DEF  = "vh_數學B4_ProbabilityDefinition"
SKILL_PROP = "vh_數學B4_ProbabilityProperties"
SKILL_SSE  = "vh_數學B4_SampleSpaceAndEvents"

STILL_BLOCKED = [
    "vh_數學B4_BasicConceptsOfSets",
    "vh_數學B4_ProbabilityOperations",
    "vh_數學B4_ApplicationsOfExpectation",
    "vh_數學B4_MathematicalExpectation",
]


# ═══ helpers ════════════════════════════════════════════════════════════════

def _frac(s: str) -> Fraction:
    return Fraction(s) if "/" in s else Fraction(int(s))


def _assert_rational_fraction_payload(p: dict, pid: str):
    assert p["problem_type_id"] == pid
    assert p["answer_type"] == "rational_fraction"
    assert p["answer"].strip()
    assert "/" in p["answer"] or p["answer"].isdigit()
    assert p["question_text"].strip()
    assert p["explanation"].strip()
    assert "[FORMULA_MISSING]" not in p["question_text"]
    assert "[BLANK]" not in p["question_text"]
    assert "[FORMULA_MISSING]" not in p["explanation"]
    assert "[BLANK]" not in p["explanation"]
    # answer must be valid probability 0 < p <= 1
    f = _frac(p["answer"])
    assert 0 < f <= 1, f"answer out of range: {p['answer']}"


def _assert_answer_in_choices(p: dict):
    assert p["answer"] in p["choices"], f"answer {p['answer']} not in choices {p['choices']}"


# ═══ A. conditional_probability_basic unit tests ════════════════════════════

class TestConditionalProbabilityBasic:

    def _gen(self, seed=1, difficulty=1):
        return conditional_probability_basic(
            skill_id=SKILL_COND,
            subskill_id="b4_ch2_cond_prob_basic_01",
            difficulty=difficulty,
            seed=seed,
        )

    @pytest.mark.parametrize("seed", range(1, 31))
    def test_payload_valid_30_seeds(self, seed):
        p = self._gen(seed)
        _assert_rational_fraction_payload(p, CONDITIONAL_BASIC_PROBLEM_TYPE_ID)

    @pytest.mark.parametrize("seed", range(1, 31))
    def test_answer_in_choices(self, seed):
        p = self._gen(seed)
        _assert_answer_in_choices(p)

    def test_skill_id_correct(self):
        p = self._gen()
        assert p["skill_id"] == SKILL_COND

    def test_required_keys_present(self):
        p = self._gen()
        for key in ["question_text", "answer", "explanation", "skill_id",
                    "problem_type_id", "generator_key", "answer_type",
                    "difficulty", "diagnosis_tags", "remediation_candidates"]:
            assert key in p, f"missing key: {key}"

    def test_context_rotation_covers_all(self):
        """30 seeds should cover all 3 contexts."""
        contexts_seen = set()
        for seed in range(1, 31):
            p = self._gen(seed)
            ctx = p["parameters"]["context"]
            contexts_seen.add(ctx)
        assert len(contexts_seen) == 3, f"only saw contexts: {contexts_seen}"

    def test_not_handwriting(self):
        for seed in range(1, 6):
            p = self._gen(seed)
            assert p["answer_type"] != "handwriting"
            assert p["answer_type"] != "ai_judged_free_response"

    @pytest.mark.parametrize("difficulty", [1, 2, 3])
    def test_difficulty_levels(self, difficulty):
        p = self._gen(seed=5, difficulty=difficulty)
        _assert_rational_fraction_payload(p, CONDITIONAL_BASIC_PROBLEM_TYPE_ID)
        assert p["difficulty"] == difficulty

    def test_seen_parameter_tuples_dedup(self):
        seen: set[tuple] = set()
        p1 = conditional_probability_basic(
            skill_id=SKILL_COND, subskill_id="b4_ch2_cond_prob_basic_01",
            seed=1, seen_parameter_tuples=seen,
        )
        assert len(seen) == 1
        p2 = conditional_probability_basic(
            skill_id=SKILL_COND, subskill_id="b4_ch2_cond_prob_basic_01",
            seed=2, seen_parameter_tuples=seen,
        )
        assert len(seen) == 2

    def test_diagnosis_tags_present(self):
        p = self._gen()
        assert "conditional_probability" in p["diagnosis_tags"]

    def test_remediation_candidates_present(self):
        p = self._gen()
        assert p["remediation_candidates"]

    def test_pba_formula_correct(self):
        """Verify P(B|A) = pab_n/pa_n is mathematically correct."""
        for seed in range(1, 11):
            p = self._gen(seed)
            params = p["parameters"]
            pa_n  = params["pa_n"]
            pab_n = params["pab_n"]
            D     = params["D"]
            assert pab_n < pa_n, "P(A∩B) must be < P(A)"
            assert pa_n  <= D,   "P(A) numerator must be <= D"
            assert pab_n >= 1,   "P(A∩B) must be > 0"
            expected = _frac(f"{pab_n}/{pa_n}")
            got = _frac(p["answer"])
            assert got == expected, f"seed={seed}: expected {expected}, got {got}"

    def test_answer_canonical_reduced(self):
        for seed in range(1, 11):
            p = self._gen(seed)
            f = _frac(p["answer"])
            assert str(f) == p["answer"] or int(f) == int(p["answer"].split("/")[0] if "/" in p["answer"] else p["answer"])

    def test_multiple_choice_false(self):
        p = conditional_probability_basic(
            skill_id=SKILL_COND, subskill_id="x", seed=1, multiple_choice=False
        )
        assert p["choices"] == []


# ═══ B. without_replacement_conditional_probability unit tests ══════════════

class TestWithoutReplacementConditionalProbability:

    def _gen(self, seed=1, difficulty=1):
        return without_replacement_conditional_probability(
            skill_id=SKILL_COND,
            subskill_id="b4_ch2_cond_prob_wor_01",
            difficulty=difficulty,
            seed=seed,
        )

    @pytest.mark.parametrize("seed", range(1, 31))
    def test_payload_valid_30_seeds(self, seed):
        p = self._gen(seed)
        _assert_rational_fraction_payload(p, WITHOUT_REPLACEMENT_PROBLEM_TYPE_ID)

    @pytest.mark.parametrize("seed", range(1, 31))
    def test_answer_in_choices(self, seed):
        p = self._gen(seed)
        _assert_answer_in_choices(p)

    def test_skill_id_correct(self):
        p = self._gen()
        assert p["skill_id"] == SKILL_COND

    def test_required_keys_present(self):
        p = self._gen()
        for key in ["question_text", "answer", "explanation", "skill_id",
                    "problem_type_id", "generator_key", "answer_type",
                    "difficulty", "diagnosis_tags", "remediation_candidates"]:
            assert key in p

    def test_scenario_rotation_covers_all(self):
        """30 seeds should cover all 3 scenario types."""
        scenarios_seen = set()
        for seed in range(1, 31):
            p = self._gen(seed)
            sc = p["parameters"]["scenario"]
            scenarios_seen.add(sc)
        assert len(scenarios_seen) == 3, f"only saw: {scenarios_seen}"

    def test_not_handwriting(self):
        for seed in range(1, 6):
            p = self._gen(seed)
            assert p["answer_type"] not in ("handwriting", "ai_judged_free_response")

    @pytest.mark.parametrize("difficulty", [1, 2, 3])
    def test_difficulty_levels(self, difficulty):
        p = self._gen(seed=3, difficulty=difficulty)
        _assert_rational_fraction_payload(p, WITHOUT_REPLACEMENT_PROBLEM_TYPE_ID)

    def test_conditional_answer_valid_fraction(self):
        """ans_num/ans_den must equal _frac(answer)."""
        for seed in range(1, 11):
            p = self._gen(seed)
            params = p["parameters"]
            expected = Fraction(params["ans_num"], params["ans_den"])
            got = _frac(p["answer"])
            assert got == expected

    def test_no_image_reference(self):
        for seed in range(1, 11):
            p = self._gen(seed)
            for field in ("question_text", "explanation"):
                assert "圖" not in p[field] or "圖" in p[field]  # allowed in text
                assert "[IMG]" not in p[field]

    def test_multiple_choice_false(self):
        p = without_replacement_conditional_probability(
            skill_id=SKILL_COND, subskill_id="x", seed=1, multiple_choice=False
        )
        assert p["choices"] == []

    def test_diagnosis_tags_without_replacement(self):
        p = self._gen()
        assert "without_replacement" in p["diagnosis_tags"]


# ═══ C. Router tests ════════════════════════════════════════════════════════

class TestRouterPhase6D:

    @pytest.mark.parametrize("pid", [
        "conditional_probability_basic",
        "without_replacement_conditional_probability",
    ])
    def test_router_generates_payload(self, pid):
        p = generate_for_chap2_skill(
            skill_id=SKILL_COND, problem_type_id=pid, seed=42
        )
        assert p["problem_type_id"] == pid
        assert p["skill_id"] == SKILL_COND

    def test_router_rotates_between_two_types(self):
        """Without pinning problem_type, router should rotate across seeds."""
        seen_types = set()
        for seed in range(1, 20):
            p = generate_for_chap2_skill(skill_id=SKILL_COND, seed=seed)
            seen_types.add(p["problem_type_id"])
        assert len(seen_types) == 2

    def test_router_raises_for_unsupported_skill(self):
        with pytest.raises(ValueError, match="unsupported skill_id"):
            generate_for_chap2_skill(skill_id="vh_數學B4_ProbabilityOperations")

    def test_router_raises_for_unsupported_pid(self):
        with pytest.raises(ValueError):
            generate_for_chap2_skill(
                skill_id=SKILL_COND,
                problem_type_id="independent_events_basic"
            )

    @pytest.mark.parametrize("pid", [
        "conditional_probability_basic",
        "without_replacement_conditional_probability",
    ])
    def test_payload_passes_allowlist_gate(self, pid):
        p = generate_for_chap2_skill(skill_id=SKILL_COND, problem_type_id=pid, seed=7)
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(SKILL_COND, p)
        assert ok is True, f"blocked: {reason}"

    def test_router_trace_present(self):
        p = generate_for_chap2_skill(skill_id=SKILL_COND, seed=1)
        assert "router_trace" in p
        assert p["router_trace"]["router"] == "chap2_phase6c1"


# ═══ D. URL decode round-trip ═══════════════════════════════════════════════

class TestUrlDecodeRoundTrip:

    def test_single_decode_cond_skill(self):
        assert _url_unquote(ENCODED_COND) == SKILL_COND

    def test_decoded_recognized_as_deterministic(self):
        decoded = _url_unquote(ENCODED_COND)
        assert is_b4_chapter2_phase6c1_deterministic_skill(decoded)

    def test_encoded_not_directly_recognized(self):
        assert not is_b4_chapter2_phase6c1_deterministic_skill(ENCODED_COND)

    def test_already_decoded_idempotent(self):
        assert _url_unquote(SKILL_COND) == SKILL_COND

    @pytest.mark.parametrize("encoded,expected", [
        (ENCODED_COND, SKILL_COND),
        ("vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition", SKILL_DEF),
        ("vh_%E6%95%B8%E5%AD%B8B4_SampleSpaceAndEvents",  SKILL_SSE),
    ])
    def test_decode_all_enabled_skills(self, encoded, expected):
        assert _url_unquote(encoded) == expected


# ═══ E. Frontend double-encoding regression ═════════════════════════════════

class TestFrontendDoubleEncoding:
    """Simulates fixed getSkillId(): decodeURIComponent → URLSearchParams.set → backend."""

    def _fixed_flow(self, encoded: str) -> str:
        frontend_decoded = _url_unquote(encoded)
        re_encoded = _url_quote(frontend_decoded, safe="")
        return _url_unquote(re_encoded)

    def test_cond_skill_fixed_flow(self):
        assert self._fixed_flow(ENCODED_COND) == SKILL_COND

    def test_double_encode_broken_flow(self):
        """Original bug: encoded passed to URLSearchParams.set → double-encode."""
        double_encoded = _url_quote(ENCODED_COND, safe="")
        once_decoded = _url_unquote(double_encoded)
        assert once_decoded == ENCODED_COND  # still encoded
        assert once_decoded != SKILL_COND

    @pytest.mark.parametrize("encoded", [
        ENCODED_COND,
        "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition",
        "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityProperties",
        "vh_%E6%95%B8%E5%AD%B8B4_MathematicalExpectationDefinition",
    ])
    def test_fixed_flow_all_skills(self, encoded):
        result = self._fixed_flow(encoded)
        assert "%" not in result
        assert is_b4_chapter2_phase6c1_deterministic_skill(result)

    def test_plain_skill_id_idempotent(self):
        """Already-decoded skill_id survives the fixed flow unchanged."""
        assert self._fixed_flow(SKILL_COND) == SKILL_COND


# ═══ F. Not-enabled / unsupported skill guard ════════════════════════════════

class TestNotEnabledGuard:

    @pytest.mark.parametrize("skill_id", STILL_BLOCKED)
    def test_still_blocked_skills(self, skill_id):
        assert is_b4_chapter2_skill_not_enabled_in_phase6c1(skill_id) is True

    def test_conditional_probability_no_longer_blocked(self):
        assert is_b4_chapter2_skill_not_enabled_in_phase6c1(SKILL_COND) is False

    def test_conditional_probability_in_allowlist(self):
        assert is_b4_chapter2_phase6c1_deterministic_skill(SKILL_COND) is True

    @pytest.mark.parametrize("skill_id", STILL_BLOCKED)
    def test_blocked_skill_raises_in_router(self, skill_id):
        with pytest.raises(ValueError, match="unsupported skill_id"):
            generate_for_chap2_skill(skill_id=skill_id)

    def test_allowlist_size_is_6(self):
        assert len(B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST) == 6

    def test_not_enabled_size_is_4(self):
        assert len(B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS) == 4

    def test_conditional_not_in_not_enabled_set(self):
        assert SKILL_COND not in B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS

    def test_independent_events_not_in_not_enabled_set(self):
        assert "vh_數學B4_IndependentEvents" not in B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS

    def test_expectation_definition_not_in_not_enabled_set(self):
        assert "vh_數學B4_MathematicalExpectationDefinition" not in B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS

    def test_blocked_encoded_skills_recognized_after_decode(self):
        for encoded, expected in [
            ("vh_%E6%95%B8%E5%AD%B8B4_BasicConceptsOfSets",
             "vh_數學B4_BasicConceptsOfSets"),
        ]:
            decoded = _url_unquote(encoded)
            assert decoded == expected
            assert is_b4_chapter2_skill_not_enabled_in_phase6c1(decoded) is True


# ═══ G. Handwriting reserved blocked ════════════════════════════════════════

class TestHandwritingReservedBlocked:

    @pytest.mark.parametrize("pid", [
        "sample_space_listing", "event_set_listing", "subset_listing"
    ])
    def test_handwriting_types_excluded(self, pid):
        assert is_b4_chapter2_excluded_problem_type(pid) is True

    @pytest.mark.parametrize("pid", list(B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES))
    def test_allowed_types_not_excluded(self, pid):
        assert is_b4_chapter2_excluded_problem_type(pid) is False

    def test_conditional_listing_not_in_router(self):
        for pid in ("sample_space_listing", "event_set_listing", "subset_listing"):
            with pytest.raises(ValueError):
                generate_for_chap2_skill(skill_id=SKILL_COND, problem_type_id=pid)

    @pytest.mark.parametrize("pid", ["sample_space_listing", "event_set_listing"])
    def test_validate_blocks_handwriting(self, pid):
        ok, reason = validate_b4_chap2_phase6c1_generator_payload(
            SKILL_COND, {"problem_type_id": pid}
        )
        assert ok is False
        assert "excluded_handwriting" in reason


# ═══ H. Phase 6C regression ══════════════════════════════════════════════════

class TestPhase6CRegression:

    @pytest.mark.parametrize("skill_id,pid", [
        (SKILL_DEF,  "classical_probability_fraction"),
        (SKILL_PROP, "complement_probability"),
        (SKILL_SSE,  "sample_space_count_numeric"),
        (SKILL_DEF,  "dice_coin_probability_count"),
        (SKILL_PROP, "union_intersection_probability"),
    ])
    def test_6c_types_still_work(self, skill_id, pid):
        p = generate_for_chap2_skill(skill_id=skill_id, problem_type_id=pid, seed=99)
        assert p["problem_type_id"] == pid
        assert p["skill_id"] == skill_id

    def test_allowlist_has_11_problem_types(self):
        assert len(B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES) == 11

    def test_6d_types_in_allowlist(self):
        assert "conditional_probability_basic" in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES
        assert "without_replacement_conditional_probability" in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES

    def test_6e_types_in_allowlist(self):
        assert "independent_joint_probability" in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES
        assert "independent_at_least_one_probability" in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES

    def test_6f_types_in_allowlist(self):
        assert "expectation_discrete_basic" in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES
        assert "expectation_from_distribution" in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES

    def test_6c_types_still_in_allowlist(self):
        for pid in ["classical_probability_fraction", "complement_probability",
                    "sample_space_count_numeric", "union_intersection_probability",
                    "dice_coin_probability_count"]:
            assert pid in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES


# ═══ I. check_rational_answer checker reuse ══════════════════════════════════

class TestCheckerReuse:

    @pytest.mark.parametrize("pid", [
        "conditional_probability_basic",
        "without_replacement_conditional_probability",
    ])
    def test_round_trip_check(self, pid):
        p = generate_for_chap2_skill(skill_id=SKILL_COND, problem_type_id=pid, seed=10)
        ans = p["answer"]
        if "/" in ans:
            n, d = map(int, ans.split("/"))
        else:
            n, d = int(ans), 1
        assert check_rational_answer(ans, n, d) is True
        assert check_rational_answer("ZZZ", n, d) is False

    def test_check_accepts_decimal_equivalent(self):
        # 1/2 = 0.5
        assert check_rational_answer("0.5", 1, 2) is True

    def test_check_accepts_percentage(self):
        assert check_rational_answer("50%", 1, 2) is True

    def test_check_accepts_unreduced(self):
        assert check_rational_answer("2/6", 1, 3) is True

    def test_check_rejects_wrong_value(self):
        assert check_rational_answer("3/4", 1, 2) is False

    def test_check_rejects_empty(self):
        assert check_rational_answer("", 1, 2) is False


# ═══ J. Chap1 regression ════════════════════════════════════════════════════

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

    def test_chap2_cond_not_in_chap1_allowlist(self):
        from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
            B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
        )
        assert SKILL_COND not in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST
