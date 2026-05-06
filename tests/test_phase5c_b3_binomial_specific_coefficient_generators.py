"""Phase 5C-B3-A: binomial two-variable and Laurent specific-coefficient generators."""

from __future__ import annotations

import pytest

from core.vocational_math_b4.adaptive import b4_chapter1_deterministic_allowlist as allow
from core.vocational_math_b4.domain.counting_domain_functions import combination
from core.vocational_math_b4.generators import binomial as binomial_generators
from core.vocational_math_b4.services.question_router import generate_for_skill

BINOMIAL_SKILL = "vh_數學B4_BinomialTheorem"
TWO_VAR_PT = "binomial_two_variable_specific_coefficient"
LAURENT_PT = "binomial_laurent_specific_power_coefficient"
EXCLUDED = frozenset(
    {
        "binomial_expansion_basic",
        "tree_diagram_listing",
        "pascal_triangle_derivation",
    }
)


@pytest.mark.parametrize("seed", range(1, 51))
def test_two_variable_sampling_int_answer_and_contract(seed: int) -> None:
    payload = binomial_generators.binomial_two_variable_specific_coefficient(
        skill_id=BINOMIAL_SKILL,
        subskill_id="b4_ch1_binomial_two_variable_specific_01",
        difficulty=1,
        seed=seed,
        multiple_choice=True,
    )
    assert payload["problem_type_id"] == TWO_VAR_PT
    assert isinstance(payload["answer"], int)
    assert payload["problem_type_id"] not in EXCLUDED
    assert "完整展開" not in payload["question_text"] or "不必" in payload["question_text"]
    assert "\\binom" in payload["explanation"] or "binom" in payload["explanation"]
    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(BINOMIAL_SKILL, payload)
    assert ok, reason


def test_two_variable_formula_matches_parameters() -> None:
    for seed in range(1, 120):
        payload = binomial_generators.binomial_two_variable_specific_coefficient(
            skill_id=BINOMIAL_SKILL,
            subskill_id="b4_ch1_binomial_two_variable_specific_01",
            difficulty=2,
            seed=seed,
            multiple_choice=False,
        )
        par = payload["parameters"]
        a, b, n, p, q = par["a"], par["b"], par["n"], par["p"], par["q"]
        y_plus: bool = par["y_plus"]
        assert p + q == n
        signed_b = b if y_plus else -b
        expected = combination(n, q) * (a**p) * (signed_b**q)
        assert payload["answer"] == expected


@pytest.mark.parametrize("seed", range(1, 51))
def test_laurent_sampling_int_answer_and_contract(seed: int) -> None:
    payload = binomial_generators.binomial_laurent_specific_power_coefficient(
        skill_id=BINOMIAL_SKILL,
        subskill_id="b4_ch1_binomial_laurent_specific_power_01",
        difficulty=1,
        seed=seed,
        multiple_choice=True,
    )
    assert payload["problem_type_id"] == LAURENT_PT
    assert isinstance(payload["answer"], int)
    assert payload["problem_type_id"] not in EXCLUDED
    assert "n-2r" in payload["explanation"].replace(" ", "")
    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(BINOMIAL_SKILL, payload)
    assert ok, reason


def test_laurent_formula_matches_parameters() -> None:
    for seed in range(1, 120):
        payload = binomial_generators.binomial_laurent_specific_power_coefficient(
            skill_id=BINOMIAL_SKILL,
            subskill_id="b4_ch1_binomial_laurent_specific_power_01",
            difficulty=2,
            seed=seed,
            multiple_choice=False,
        )
        par = payload["parameters"]
        a, b, n, r, k = par["a"], par["b"], par["n"], par["r"], par["k"]
        term_plus: bool = par["term_plus"]
        assert k == n - 2 * r
        assert (n - k) % 2 == 0
        assert 0 <= r <= n
        signed_b = b if term_plus else -b
        expected = combination(n, r) * (a ** (n - r)) * (signed_b**r)
        assert payload["answer"] == expected


def test_router_emits_new_problem_types_via_explicit_selection() -> None:
    p1 = generate_for_skill(
        skill_id=BINOMIAL_SKILL,
        level=1,
        seed=7,
        problem_type_id=TWO_VAR_PT,
    )
    assert p1["problem_type_id"] == TWO_VAR_PT
    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(BINOMIAL_SKILL, p1)
    assert ok, reason

    p2 = generate_for_skill(
        skill_id=BINOMIAL_SKILL,
        level=1,
        seed=7,
        problem_type_id=LAURENT_PT,
    )
    assert p2["problem_type_id"] == LAURENT_PT
    ok2, reason2 = allow.validate_b4_deterministic_adaptive_generator_payload(BINOMIAL_SKILL, p2)
    assert ok2, reason2


def test_router_seed_sampling_covers_both_new_types() -> None:
    seen: set[str] = set()
    for seed in range(1, 800):
        payload = generate_for_skill(skill_id=BINOMIAL_SKILL, level=1, seed=seed)
        seen.add(payload["problem_type_id"])
        assert payload["problem_type_id"] not in EXCLUDED
    assert TWO_VAR_PT in seen
    assert LAURENT_PT in seen
