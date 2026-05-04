"""Phase 4E-8 generators: combination_basic_selection, permutation_formula_evaluation, factorial_evaluation."""

from __future__ import annotations

import re

import pytest

from core.vocational_math_b4.domain.b4_validators import validate_problem_payload_contract
from core.vocational_math_b4.domain.counting_domain_functions import combination, factorial, permutation
from core.vocational_math_b4.generators.combination import combination_basic_selection
from core.vocational_math_b4.generators.counting import factorial_evaluation
from core.vocational_math_b4.generators.permutation import permutation_formula_evaluation


def _check_contract(payload: dict) -> None:
    validate_problem_payload_contract(payload)
    required = {
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
    assert required.issubset(payload.keys())
    assert "parameter_tuple" in payload["parameters"]


def _check_latex_no_plain_math_notation(text: str) -> None:
    assert "$" in text
    assert "2^2" not in text
    assert "C(n,r)" not in text
    assert "P(n,r)" not in text


def _check_mc(payload: dict, multiple_choice: bool) -> None:
    if multiple_choice:
        assert len(payload["choices"]) == 4
        assert len(set(payload["choices"])) == 4
        assert payload["answer"] in payload["choices"]
    else:
        assert payload["choices"] == []


def test_generators_importable() -> None:
    assert callable(combination_basic_selection)
    assert callable(permutation_formula_evaluation)
    assert callable(factorial_evaluation)


@pytest.mark.parametrize(
    "fn",
    [
        combination_basic_selection,
        permutation_formula_evaluation,
        factorial_evaluation,
    ],
)
def test_payload_contract_and_answer_type(fn) -> None:
    payload = fn(
        skill_id="vh_b4_test",
        subskill_id="unit_test",
        difficulty=2,
        seed=11,
        multiple_choice=True,
    )
    _check_contract(payload)
    assert isinstance(payload["answer"], int)


def test_answer_correct_combination_basic_selection() -> None:
    payload = combination_basic_selection(
        skill_id="vh_b4_combination",
        subskill_id="combination_basic_selection",
        seed=3,
    )
    assert payload["answer"] == combination(payload["parameters"]["n"], payload["parameters"]["r"])


def test_answer_correct_permutation_formula_evaluation() -> None:
    payload = permutation_formula_evaluation(
        skill_id="vh_b4_permutation",
        subskill_id="permutation_formula_evaluation",
        seed=4,
    )
    assert payload["answer"] == permutation(payload["parameters"]["n"], payload["parameters"]["r"])


def test_answer_correct_factorial_evaluation() -> None:
    payload = factorial_evaluation(
        skill_id="vh_b4_factorial",
        subskill_id="factorial_evaluation",
        seed=5,
    )
    n = payload["parameters"]["n"]
    k = payload["parameters"]["k"]
    variant = payload["parameters"]["variant"]
    if variant == "direct":
        assert payload["answer"] == factorial(n)
    else:
        assert payload["answer"] == factorial(n) // factorial(n - k)


@pytest.mark.parametrize(
    "fn,expect_comb,expect_perm,expect_fact",
    [
        (combination_basic_selection, True, False, False),
        (permutation_formula_evaluation, False, True, False),
        (factorial_evaluation, False, False, True),
    ],
)
def test_placeholder_and_latex_format(
    fn, expect_comb: bool, expect_perm: bool, expect_fact: bool
) -> None:
    payload = fn(
        skill_id="vh_b4_test",
        subskill_id="unit_test",
        seed=7,
    )
    q = payload["question_text"]
    e = payload["explanation"]
    assert "[BLANK]" not in q and "[BLANK]" not in e
    combined = q + "\n" + e
    _check_latex_no_plain_math_notation(combined)
    if expect_comb:
        assert re.search(r"C\^\{", combined) is not None or "\\binom" in combined
    if expect_perm:
        assert re.search(r"P\^\{", combined) is not None
    if expect_fact:
        assert "!" in combined


@pytest.mark.parametrize(
    "fn",
    [
        combination_basic_selection,
        permutation_formula_evaluation,
        factorial_evaluation,
    ],
)
def test_multiple_choice_and_free_response(fn) -> None:
    payload_mc = fn(skill_id="vh", subskill_id="sub", seed=12, multiple_choice=True)
    _check_mc(payload_mc, True)

    payload_fr = fn(skill_id="vh", subskill_id="sub", seed=12, multiple_choice=False)
    _check_mc(payload_fr, False)


@pytest.mark.parametrize(
    "fn",
    [
        combination_basic_selection,
        permutation_formula_evaluation,
        factorial_evaluation,
    ],
)
def test_same_seed_stable_parameter_tuple_and_answer(fn) -> None:
    p1 = fn(skill_id="vh", subskill_id="sub", seed=101)
    p2 = fn(skill_id="vh", subskill_id="sub", seed=101)
    assert p1["parameters"]["parameter_tuple"] == p2["parameters"]["parameter_tuple"]
    assert p1["answer"] == p2["answer"]


@pytest.mark.parametrize(
    "fn",
    [
        combination_basic_selection,
        permutation_formula_evaluation,
        factorial_evaluation,
    ],
)
def test_different_seed_generates_variety(fn) -> None:
    tuples = {
        fn(skill_id="vh", subskill_id="sub", seed=seed)["parameters"]["parameter_tuple"]
        for seed in range(1, 11)
    }
    assert len(tuples) >= 2


@pytest.mark.parametrize(
    "fn",
    [
        combination_basic_selection,
        permutation_formula_evaluation,
        factorial_evaluation,
    ],
)
def test_seed_1_to_5_all_distinct(fn) -> None:
    tuples = [
        fn(skill_id="vh", subskill_id="sub", seed=seed)["parameters"]["parameter_tuple"]
        for seed in range(1, 6)
    ]
    assert len(set(tuples)) == 5


@pytest.mark.parametrize(
    "fn",
    [
        combination_basic_selection,
        permutation_formula_evaluation,
        factorial_evaluation,
    ],
)
def test_seen_parameter_tuples_blocks_duplicates(fn) -> None:
    seen: set[tuple] = set()
    p1 = fn(skill_id="vh", subskill_id="sub", seed=31, seen_parameter_tuples=seen)
    p2 = fn(skill_id="vh", subskill_id="sub", seed=31, seen_parameter_tuples=seen)
    assert p1["parameters"]["parameter_tuple"] != p2["parameters"]["parameter_tuple"]


@pytest.mark.parametrize(
    "fn,monkey_target,fixed_fn,seen_tuple",
    [
        (
            combination_basic_selection,
            "core.vocational_math_b4.generators.combination._sample_combination_basic_selection_params",
            lambda _rng, _d: (8, 3, "books"),
            ("combination_basic_selection", 8, 3, "books"),
        ),
        (
            permutation_formula_evaluation,
            "core.vocational_math_b4.generators.permutation._sample_permutation_formula_params",
            lambda _rng, _d: (8, 3, "symbolic"),
            ("permutation_formula_evaluation", 8, 3, "symbolic"),
        ),
        (
            factorial_evaluation,
            "core.vocational_math_b4.generators.counting._sample_factorial_evaluation_params",
            lambda _rng, _d: (5, 0, "direct"),
            ("factorial_evaluation", 5, 0, "direct"),
        ),
    ],
)
def test_retry_50_failure_raises(fn, monkeypatch, monkey_target, fixed_fn, seen_tuple) -> None:
    monkeypatch.setattr(monkey_target, fixed_fn)
    seen = {seen_tuple}
    with pytest.raises(ValueError):
        fn(skill_id="vh", subskill_id="sub", seed=42, seen_parameter_tuples=seen)
