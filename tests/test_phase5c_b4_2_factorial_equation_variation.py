"""Phase 5C-B4.2: factorial equation variants (multiply / sum / product forms)."""

from __future__ import annotations

import pytest

from core.vocational_math_b4.adaptive import b4_chapter1_deterministic_allowlist as allow
from core.vocational_math_b4.domain.counting_domain_functions import factorial, factorial_ratio_solve_n
from core.vocational_math_b4.generators.counting import factorial_equation_solve_n
from core.vocational_math_b4.services.question_router import generate_for_skill

FACT_SKILL = "vh_數學B4_FactorialNotation"
FACT_PT = "factorial_equation_solve_n"
EXCLUDED = frozenset(
    {
        "binomial_expansion_basic",
        "tree_diagram_listing",
        "pascal_triangle_derivation",
    }
)


def test_multiply_variant_answer_formula() -> None:
    payload = factorial_equation_solve_n(
        skill_id=FACT_SKILL,
        subskill_id="b4_ch1_factorial_solve_n_02",
        difficulty=1,
        seed=1,
        multiple_choice=False,
    )
    assert payload["parameters"]["variant"] == "multiply_factorial_equation"
    a, b = payload["parameters"]["a"], payload["parameters"]["b"]
    assert a is not None and b is not None
    ratio = factorial(b) // factorial(a)
    assert payload["answer"] == ratio


def test_sum_variant_answer_formula() -> None:
    payload = factorial_equation_solve_n(
        skill_id=FACT_SKILL,
        subskill_id="b4_ch1_factorial_solve_n_02",
        difficulty=1,
        seed=2,
        multiple_choice=False,
    )
    assert payload["parameters"]["variant"] == "factorial_sum_linear_equation"
    a, b = payload["parameters"]["a"], payload["parameters"]["b"]
    ratio = factorial(b) // factorial(a)
    assert payload["answer"] == ratio + 1


def test_product_variant_answer_formula() -> None:
    payload = factorial_equation_solve_n(
        skill_id=FACT_SKILL,
        subskill_id="b4_ch1_factorial_solve_n_02",
        difficulty=1,
        seed=3,
        multiple_choice=False,
    )
    assert payload["parameters"]["variant"] == "factorial_product_ratio"
    a, b = payload["parameters"]["a"], payload["parameters"]["b"]
    assert payload["answer"] == factorial(b) // factorial(a)


def test_ratio_basic_unchanged_for_seed_8() -> None:
    payload = factorial_equation_solve_n(
        skill_id=FACT_SKILL,
        subskill_id="b4_ch1_factorial_solve_n_02",
        difficulty=2,
        seed=8,
        multiple_choice=False,
    )
    assert payload["parameters"]["variant"] == "ratio_basic"
    k = payload["parameters"]["k"]
    assert k is not None
    assert payload["answer"] == factorial_ratio_solve_n(0, -1, k)
    assert payload["parameters"]["parameter_tuple"] == (FACT_PT, k)


@pytest.mark.parametrize("seed", range(1, 101))
def test_seed_sampling_contract(seed: int) -> None:
    payload = factorial_equation_solve_n(
        skill_id=FACT_SKILL,
        subskill_id="b4_ch1_factorial_solve_n_02",
        difficulty=2,
        seed=seed,
        multiple_choice=True,
    )
    assert payload["problem_type_id"] == FACT_PT
    assert isinstance(payload["answer"], int)
    assert payload["answer"] > 0
    assert "!" in payload["question_text"]
    assert "\\frac" in payload["explanation"] or "^{" in payload["explanation"]
    assert "$" in payload["explanation"]

    v = payload["parameters"]["variant"]
    if v == "ratio_basic":
        k = payload["parameters"]["k"]
        assert payload["answer"] == k
    elif v == "multiply_factorial_equation":
        a, b = payload["parameters"]["a"], payload["parameters"]["b"]
        assert payload["answer"] == factorial(b) // factorial(a)
    elif v == "factorial_sum_linear_equation":
        a, b = payload["parameters"]["a"], payload["parameters"]["b"]
        assert payload["answer"] == factorial(b) // factorial(a) + 1
    else:
        a, b = payload["parameters"]["a"], payload["parameters"]["b"]
        assert v == "factorial_product_ratio"
        assert payload["answer"] == factorial(b) // factorial(a)

    if payload["parameters"].get("gap") is not None:
        gap = payload["parameters"]["gap"]
        assert gap >= 1
        assert payload["parameters"]["b"] == payload["parameters"]["a"] + gap

    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]

    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(FACT_SKILL, payload)
    assert ok, reason


def test_variants_include_multiply_and_sum_in_range() -> None:
    found = set()
    for seed in range(1, 101):
        payload = factorial_equation_solve_n(
            skill_id=FACT_SKILL,
            subskill_id="b4_ch1_factorial_solve_n_02",
            difficulty=2,
            seed=seed,
            multiple_choice=False,
        )
        found.add(payload["parameters"]["variant"])
    assert "multiply_factorial_equation" in found
    assert "factorial_sum_linear_equation" in found


def test_router_explicit_factorial_equation() -> None:
    payload = generate_for_skill(
        skill_id=FACT_SKILL,
        level=1,
        seed=20,
        problem_type_id=FACT_PT,
    )
    assert payload["problem_type_id"] == FACT_PT
    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(FACT_SKILL, payload)
    assert ok, reason


def test_router_sampling_includes_factorial_equation() -> None:
    seen: set[str] = set()
    for seed in range(1, 800):
        payload = generate_for_skill(skill_id=FACT_SKILL, level=1, seed=seed)
        seen.add(payload["problem_type_id"])
        assert payload["problem_type_id"] not in EXCLUDED
    assert FACT_PT in seen


def test_excluded_still_blocked() -> None:
    for pid in EXCLUDED:
        ok, _ = allow.validate_b4_deterministic_adaptive_generator_payload(
            FACT_SKILL,
            {"problem_type_id": pid, "generator_key": "x"},
        )
        assert ok is False
