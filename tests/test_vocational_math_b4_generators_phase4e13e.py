from __future__ import annotations

import re

import pytest

from core.vocational_math_b4.domain.binomial_domain_functions import binomial_expansion_coefficients
from core.vocational_math_b4.generators import binomial as binomial_generators


REQUIRED_KEYS = {
    "question_text",
    "choices",
    "answer",
    "explanation",
    "skill_id",
    "subskill_id",
    "problem_type_id",
    "generator_key",
    "difficulty",
    "diagnosis_tags",
    "remediation_candidates",
    "source_style_refs",
    "parameters",
}


def _assert_latex_format(payload: dict) -> None:
    text = f"{payload['question_text']} {payload['explanation']}"
    assert "$" in text
    assert re.search(r"\^\{[^}]+\}", text)
    assert "$(" in text and ")^{" in text
    assert "C(n,r)" not in text
    assert "P(n,r)" not in text
    assert re.search(r"\b\d+\^\d+\b", text) is None


def _assert_contract(payload: dict) -> None:
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert isinstance(payload["answer"], int)
    assert "[BLANK]" not in payload["question_text"]
    assert "[BLANK]" not in payload["explanation"]
    assert "parameter_tuple" in payload["parameters"]
    _assert_latex_format(payload)


@pytest.mark.parametrize(
    "fn_name,problem_type_id,generator_key",
    [
        (
            "binomial_middle_term_coefficient",
            "binomial_middle_term_coefficient",
            "b4.binomial.binomial_middle_term_coefficient",
        ),
        (
            "binomial_odd_even_coefficient_sum",
            "binomial_odd_even_coefficient_sum",
            "b4.binomial.binomial_odd_even_coefficient_sum",
        ),
        (
            "binomial_specific_coefficient_with_negative_term",
            "binomial_specific_coefficient_with_negative_term",
            "b4.binomial.binomial_specific_coefficient_with_negative_term",
        ),
    ],
)
def test_generators_import_and_contract(fn_name: str, problem_type_id: str, generator_key: str) -> None:
    fn = getattr(binomial_generators, fn_name)
    payload = fn(skill_id="vh_數學B4_Test", subskill_id="test", difficulty=1, seed=1)
    _assert_contract(payload)
    assert payload["problem_type_id"] == problem_type_id
    assert payload["generator_key"] == generator_key
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]


def test_middle_term_answer_correct() -> None:
    payload = binomial_generators.binomial_middle_term_coefficient(
        skill_id="vh_數學B4_Test",
        subskill_id="test",
        difficulty=2,
        seed=7,
        multiple_choice=False,
    )
    _assert_contract(payload)
    assert payload["choices"] == []
    p = payload["parameters"]
    coeffs = binomial_expansion_coefficients(p["a"], p["b"], p["n"])
    middle_power = p["n"] // 2
    assert payload["answer"] == coeffs[p["n"] - middle_power]


def test_odd_even_sum_answer_correct() -> None:
    payload = binomial_generators.binomial_odd_even_coefficient_sum(
        skill_id="vh_數學B4_Test",
        subskill_id="test",
        difficulty=2,
        seed=8,
        multiple_choice=False,
    )
    _assert_contract(payload)
    assert payload["choices"] == []
    p = payload["parameters"]
    coeffs = binomial_expansion_coefficients(p["a"], p["b"], p["n"])
    target_mod = 1 if p["target_parity"] == "odd" else 0
    expected = sum(coeffs[p["n"] - k] for k in range(p["n"] + 1) if k % 2 == target_mod)
    assert payload["answer"] == expected


def test_specific_negative_term_answer_correct_and_b_negative() -> None:
    payload = binomial_generators.binomial_specific_coefficient_with_negative_term(
        skill_id="vh_數學B4_Test",
        subskill_id="test",
        difficulty=2,
        seed=9,
        multiple_choice=False,
    )
    _assert_contract(payload)
    assert payload["choices"] == []
    p = payload["parameters"]
    assert p["b"] < 0
    coeffs = binomial_expansion_coefficients(p["a"], p["b"], p["n"])
    assert payload["answer"] == coeffs[p["n"] - p["k"]]


def test_negative_term_generator_can_produce_negative_answer() -> None:
    found_negative = False
    for seed in range(1, 201):
        payload = binomial_generators.binomial_specific_coefficient_with_negative_term(
            skill_id="vh_數學B4_Test",
            subskill_id="test",
            difficulty=3,
            seed=seed,
            multiple_choice=False,
        )
        if payload["answer"] < 0:
            found_negative = True
            break
    assert found_negative


@pytest.mark.parametrize(
    "fn",
    [
        binomial_generators.binomial_middle_term_coefficient,
        binomial_generators.binomial_odd_even_coefficient_sum,
        binomial_generators.binomial_specific_coefficient_with_negative_term,
    ],
)
def test_same_seed_same_output(fn) -> None:
    p1 = fn(skill_id="vh_數學B4_Test", subskill_id="test", difficulty=1, seed=3)
    p2 = fn(skill_id="vh_數學B4_Test", subskill_id="test", difficulty=1, seed=3)
    assert p1["parameters"]["parameter_tuple"] == p2["parameters"]["parameter_tuple"]
    assert p1["answer"] == p2["answer"]


@pytest.mark.parametrize(
    "fn",
    [
        binomial_generators.binomial_middle_term_coefficient,
        binomial_generators.binomial_odd_even_coefficient_sum,
        binomial_generators.binomial_specific_coefficient_with_negative_term,
    ],
)
def test_different_seed_has_diversity(fn) -> None:
    tuples = {
        fn(skill_id="vh_數學B4_Test", subskill_id="test", difficulty=1, seed=seed)["parameters"]["parameter_tuple"]
        for seed in range(1, 11)
    }
    assert len(tuples) >= 2


@pytest.mark.parametrize(
    "fn",
    [
        binomial_generators.binomial_middle_term_coefficient,
        binomial_generators.binomial_odd_even_coefficient_sum,
        binomial_generators.binomial_specific_coefficient_with_negative_term,
    ],
)
def test_seed_1_to_5_are_all_distinct(fn) -> None:
    tuples = {
        fn(skill_id="vh_數學B4_Test", subskill_id="test", difficulty=1, seed=seed)["parameters"]["parameter_tuple"]
        for seed in range(1, 6)
    }
    assert len(tuples) == 5


def test_seen_parameter_tuples_blocks_duplicates() -> None:
    seen: set[tuple] = set()
    first = binomial_generators.binomial_middle_term_coefficient(
        skill_id="vh_數學B4_Test",
        subskill_id="test",
        difficulty=1,
        seed=1,
        seen_parameter_tuples=seen,
    )
    second = binomial_generators.binomial_middle_term_coefficient(
        skill_id="vh_數學B4_Test",
        subskill_id="test",
        difficulty=1,
        seed=1,
        seen_parameter_tuples=seen,
    )
    assert first["parameters"]["parameter_tuple"] != second["parameters"]["parameter_tuple"]


def test_middle_term_raises_after_50_retries_when_space_exhausted() -> None:
    seen = {
        ("binomial_middle_term_coefficient", 1, b, n)
        for b in range(1, 5)
        for n in [2, 4, 6]
    }
    with pytest.raises(ValueError):
        binomial_generators.binomial_middle_term_coefficient(
            skill_id="vh_數學B4_Test",
            subskill_id="test",
            difficulty=1,
            seed=11,
            seen_parameter_tuples=seen,
        )


def test_odd_even_raises_after_50_retries_when_space_exhausted() -> None:
    seen = {
        ("binomial_odd_even_coefficient_sum", 1, b, n, parity)
        for b in range(1, 5)
        for n in range(2, 6)
        for parity in ["odd", "even"]
    }
    with pytest.raises(ValueError):
        binomial_generators.binomial_odd_even_coefficient_sum(
            skill_id="vh_數學B4_Test",
            subskill_id="test",
            difficulty=1,
            seed=12,
            seen_parameter_tuples=seen,
        )


def test_specific_negative_raises_after_50_retries_when_space_exhausted() -> None:
    seen = {
        ("binomial_specific_coefficient_with_negative_term", 1, b, n, k)
        for b in range(-4, 0)
        for n in range(2, 6)
        for k in range(0, n + 1)
    }
    with pytest.raises(ValueError):
        binomial_generators.binomial_specific_coefficient_with_negative_term(
            skill_id="vh_數學B4_Test",
            subskill_id="test",
            difficulty=1,
            seed=13,
            seen_parameter_tuples=seen,
        )


def test_binomial_expansion_basic_not_modified_to_runtime_ready_int_answer() -> None:
    payload = binomial_generators.binomial_expansion_basic(
        skill_id="vh_數學B4_Test",
        subskill_id="test",
        difficulty=1,
        seed=1,
    )
    assert isinstance(payload["answer"], list)
    assert payload["choices"] == []
