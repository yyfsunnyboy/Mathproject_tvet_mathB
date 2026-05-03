from __future__ import annotations

import re

import pytest

from core.vocational_math_b4.domain.binomial_domain_functions import binomial_expansion_coefficients
from core.vocational_math_b4.domain.counting_domain_functions import (
    combination,
    factorial_ratio_solve_n,
)
from core.vocational_math_b4.generators.binomial import generate as binomial_expansion_basic
from core.vocational_math_b4.generators.combination import combination_group_selection
from core.vocational_math_b4.generators.counting import factorial_equation_solve_n

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

PLACEHOLDERS = ["[BLANK]", "[FORMULA_MISSING]", "[FORMULA_IMAGE", "[WORD_EQUATION_UNPARSED]", "□", "＿＿"]


def _assert_contract(payload: dict) -> None:
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert "parameter_tuple" in payload["parameters"]


def _assert_placeholder_free(payload: dict) -> None:
    for token in PLACEHOLDERS:
        assert token not in payload["question_text"]
        assert token not in payload["explanation"]


def _assert_latex_style(payload: dict) -> None:
    q = payload["question_text"]
    e = payload["explanation"]
    assert "$" in q or "$" in e
    assert (
        ("\\binom" in q)
        or ("\\binom" in e)
        or ("^{" in q)
        or ("^{" in e)
        or ("\\frac" in q)
        or ("\\frac" in e)
    )
    assert not re.search(r"\b\d+\^\d+\b", q)
    assert not re.search(r"\b\d+\^\d+\b", e)


def test_import_and_basic_generation() -> None:
    p1 = binomial_expansion_basic(skill_id="s1", subskill_id="ss1", seed=1)
    p2 = combination_group_selection(skill_id="s2", subskill_id="ss2", seed=1)
    p3 = factorial_equation_solve_n(skill_id="s3", subskill_id="ss3", seed=1)
    assert isinstance(p1, dict)
    assert isinstance(p2, dict)
    assert isinstance(p3, dict)


def test_answers_are_correct() -> None:
    p1 = binomial_expansion_basic(skill_id="s1", subskill_id="ss1", difficulty=3, seed=3)
    a = p1["parameters"]["a"]
    b = p1["parameters"]["b"]
    n = p1["parameters"]["n"]
    assert p1["answer"] == binomial_expansion_coefficients(a, b, n)

    p2 = combination_group_selection(skill_id="s2", subskill_id="ss2", difficulty=2, seed=5)
    expected = 1
    for gs, pk in zip(p2["parameters"]["group_sizes"], p2["parameters"]["picks"]):
        expected *= combination(gs, pk)
    assert p2["answer"] == expected

    p3 = factorial_equation_solve_n(skill_id="s3", subskill_id="ss3", difficulty=2, seed=8)
    k = p3["parameters"]["k"]
    assert p3["answer"] == factorial_ratio_solve_n(0, -1, k)


def test_contract_placeholder_and_latex() -> None:
    payloads = [
        binomial_expansion_basic(skill_id="s1", subskill_id="ss1", seed=2),
        combination_group_selection(skill_id="s2", subskill_id="ss2", seed=2),
        factorial_equation_solve_n(skill_id="s3", subskill_id="ss3", seed=2),
    ]
    for payload in payloads:
        _assert_contract(payload)
        _assert_placeholder_free(payload)
        _assert_latex_style(payload)


def test_multiple_choice_behavior() -> None:
    p_binom_true = binomial_expansion_basic(skill_id="s1", subskill_id="ss1", seed=9, multiple_choice=True)
    p_binom_false = binomial_expansion_basic(skill_id="s1", subskill_id="ss1", seed=9, multiple_choice=False)
    assert p_binom_true["choices"] == []
    assert p_binom_false["choices"] == []
    assert isinstance(p_binom_true["answer"], list)
    assert all(isinstance(x, int) for x in p_binom_true["answer"])

    p_group = combination_group_selection(skill_id="s2", subskill_id="ss2", seed=9, multiple_choice=True)
    assert len(p_group["choices"]) == 4
    assert len(set(p_group["choices"])) == 4
    assert p_group["answer"] in p_group["choices"]

    p_fact = factorial_equation_solve_n(skill_id="s3", subskill_id="ss3", seed=9, multiple_choice=True)
    assert len(p_fact["choices"]) == 4
    assert len(set(p_fact["choices"])) == 4
    assert p_fact["answer"] in p_fact["choices"]

    assert combination_group_selection(skill_id="s2", subskill_id="ss2", seed=9, multiple_choice=False)["choices"] == []
    assert factorial_equation_solve_n(skill_id="s3", subskill_id="ss3", seed=9, multiple_choice=False)["choices"] == []


@pytest.mark.parametrize(
    "fn,skill_id,subskill_id",
    [
        (binomial_expansion_basic, "s1", "ss1"),
        (combination_group_selection, "s2", "ss2"),
        (factorial_equation_solve_n, "s3", "ss3"),
    ],
)
def test_same_seed_same_tuple_and_answer(fn, skill_id: str, subskill_id: str) -> None:
    p1 = fn(skill_id=skill_id, subskill_id=subskill_id, seed=11)
    p2 = fn(skill_id=skill_id, subskill_id=subskill_id, seed=11)
    assert p1["parameters"]["parameter_tuple"] == p2["parameters"]["parameter_tuple"]
    assert p1["answer"] == p2["answer"]


@pytest.mark.parametrize(
    "fn,skill_id,subskill_id",
    [
        (binomial_expansion_basic, "s1", "ss1"),
        (combination_group_selection, "s2", "ss2"),
        (factorial_equation_solve_n, "s3", "ss3"),
    ],
)
def test_different_seed_variety(fn, skill_id: str, subskill_id: str) -> None:
    tuples = {fn(skill_id=skill_id, subskill_id=subskill_id, seed=i)["parameters"]["parameter_tuple"] for i in range(1, 11)}
    assert len(tuples) >= 2


@pytest.mark.parametrize(
    "fn,skill_id,subskill_id",
    [
        (binomial_expansion_basic, "s1", "ss1"),
        (combination_group_selection, "s2", "ss2"),
        (factorial_equation_solve_n, "s3", "ss3"),
    ],
)
def test_seed_1_to_5_uniqueness(fn, skill_id: str, subskill_id: str) -> None:
    tuples = {fn(skill_id=skill_id, subskill_id=subskill_id, seed=i)["parameters"]["parameter_tuple"] for i in range(1, 6)}
    assert len(tuples) == 5


def test_seen_parameter_tuples_blocks_duplicates() -> None:
    seen1: set[tuple] = set()
    p1 = binomial_expansion_basic(skill_id="s1", subskill_id="ss1", seed=3, seen_parameter_tuples=seen1)
    p2 = binomial_expansion_basic(skill_id="s1", subskill_id="ss1", seed=3, seen_parameter_tuples=seen1)
    assert p1["parameters"]["parameter_tuple"] != p2["parameters"]["parameter_tuple"]

    seen2: set[tuple] = set()
    c1 = combination_group_selection(skill_id="s2", subskill_id="ss2", seed=3, seen_parameter_tuples=seen2)
    c2 = combination_group_selection(skill_id="s2", subskill_id="ss2", seed=3, seen_parameter_tuples=seen2)
    assert c1["parameters"]["parameter_tuple"] != c2["parameters"]["parameter_tuple"]

    seen3: set[tuple] = set()
    f1 = factorial_equation_solve_n(skill_id="s3", subskill_id="ss3", seed=3, seen_parameter_tuples=seen3)
    f2 = factorial_equation_solve_n(skill_id="s3", subskill_id="ss3", seed=3, seen_parameter_tuples=seen3)
    assert f1["parameters"]["parameter_tuple"] != f2["parameters"]["parameter_tuple"]


def test_raise_when_retries_exhausted() -> None:
    blocked_binom = {
        ("binomial_expansion_basic", 1, b, n)
        for b in range(1, 5)
        for n in range(2, 5)
    }
    with pytest.raises(ValueError):
        binomial_expansion_basic(
            skill_id="s1",
            subskill_id="ss1",
            difficulty=1,
            seed=1,
            seen_parameter_tuples=blocked_binom,
        )

    blocked_group = {
        ("combination_group_selection", (g1, g2), (p1, p2))
        for g1 in range(4, 9)
        for g2 in range(4, 9)
        for p1 in range(1, 4)
        for p2 in range(1, 4)
        if p1 <= g1 and p2 <= g2
    }
    with pytest.raises(ValueError):
        combination_group_selection(
            skill_id="s2",
            subskill_id="ss2",
            difficulty=1,
            seed=1,
            seen_parameter_tuples=blocked_group,
        )

    blocked_fact = {("factorial_equation_solve_n", k) for k in range(3, 10)}
    with pytest.raises(ValueError):
        factorial_equation_solve_n(
            skill_id="s3",
            subskill_id="ss3",
            difficulty=1,
            seed=1,
            seen_parameter_tuples=blocked_fact,
        )
