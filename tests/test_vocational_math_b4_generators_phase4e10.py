"""Phase 4E-10 generators: mult_principle_independent_choices, mult_digits_no_repeat, repeated_permutation_assignment."""

from __future__ import annotations

import re

import pytest

from core.vocational_math_b4.domain.b4_validators import validate_problem_payload_contract
from core.vocational_math_b4.domain.counting_domain_functions import (
    multiplication_principle_count,
    permutation,
    repeated_choice_count,
)
from core.vocational_math_b4.generators.counting import (
    mult_digits_no_repeat,
    mult_principle_independent_choices,
    repeated_permutation_assignment,
)


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


def _check_latex_math(text: str) -> None:
    assert "$" in text
    assert "2^2" not in text
    assert "C(n,r)" not in text
    assert "P(n,r)" not in text
    assert "\\times" in text or re.search(r"\^\{[^}]+\}", text) is not None


def _check_mc(payload: dict, multiple_choice: bool) -> None:
    if multiple_choice:
        assert len(payload["choices"]) == 4
        assert len(set(payload["choices"])) == 4
        assert payload["answer"] in payload["choices"]
    else:
        assert payload["choices"] == []


def test_generators_importable() -> None:
    assert callable(mult_principle_independent_choices)
    assert callable(mult_digits_no_repeat)
    assert callable(repeated_permutation_assignment)


@pytest.mark.parametrize(
    "fn",
    [
        mult_principle_independent_choices,
        mult_digits_no_repeat,
        repeated_permutation_assignment,
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


def test_answer_correct_mult_principle() -> None:
    payload = mult_principle_independent_choices(
        skill_id="vh_b4_mp",
        subskill_id="mult_principle_independent_choices",
        seed=8,
    )
    assert payload["answer"] == multiplication_principle_count(payload["parameters"]["counts"])


def test_answer_correct_mult_digits_allow_zero_false() -> None:
    payload = mult_digits_no_repeat(
        skill_id="vh_b4_digits",
        subskill_id="mult_digits_no_repeat",
        seed=1,
        difficulty=1,
    )
    assert payload["parameters"]["allow_zero"] is False
    d, p = payload["parameters"]["digit_pool_size"], payload["parameters"]["positions"]
    assert payload["answer"] == permutation(d, p)


def test_answer_correct_mult_digits_allow_zero_true() -> None:
    payload = mult_digits_no_repeat(
        skill_id="vh_b4_digits",
        subskill_id="mult_digits_no_repeat",
        seed=2,
        difficulty=1,
    )
    assert payload["parameters"]["allow_zero"] is True
    d = payload["parameters"]["digit_pool_size"]
    pos = payload["parameters"]["positions"]
    if pos == 1:
        assert payload["answer"] == d - 1
    else:
        assert payload["answer"] == (d - 1) * permutation(d - 1, pos - 1)


def test_answer_correct_repeated_permutation_assignment() -> None:
    payload = repeated_permutation_assignment(
        skill_id="vh_b4_assign",
        subskill_id="repeated_permutation_assignment",
        seed=9,
    )
    m = payload["parameters"]["choices_per_position"]
    n = payload["parameters"]["positions"]
    assert payload["answer"] == repeated_choice_count(m, n)


@pytest.mark.parametrize(
    "fn",
    [
        mult_principle_independent_choices,
        mult_digits_no_repeat,
        repeated_permutation_assignment,
    ],
)
def test_placeholder_and_latex(fn) -> None:
    payload = fn(skill_id="vh_b4_test", subskill_id="unit_test", seed=7)
    q = payload["question_text"]
    e = payload["explanation"]
    assert "[BLANK]" not in q and "[BLANK]" not in e
    combined = q + "\n" + e
    _check_latex_math(combined)


@pytest.mark.parametrize(
    "fn",
    [
        mult_principle_independent_choices,
        mult_digits_no_repeat,
        repeated_permutation_assignment,
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
        mult_principle_independent_choices,
        mult_digits_no_repeat,
        repeated_permutation_assignment,
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
        mult_principle_independent_choices,
        mult_digits_no_repeat,
        repeated_permutation_assignment,
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
        mult_principle_independent_choices,
        mult_digits_no_repeat,
        repeated_permutation_assignment,
    ],
)
def test_seed_1_to_5_all_distinct(fn) -> None:
    tuples = [
        fn(skill_id="vh", subskill_id="sub", seed=seed, difficulty=1)["parameters"]["parameter_tuple"]
        for seed in range(1, 6)
    ]
    assert len(set(tuples)) == 5


@pytest.mark.parametrize(
    "fn",
    [
        mult_principle_independent_choices,
        mult_digits_no_repeat,
        repeated_permutation_assignment,
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
            mult_principle_independent_choices,
            "core.vocational_math_b4.generators.counting._sample_mult_principle_independent_params",
            lambda _rng, _d: (["階段甲", "階段乙"], [2, 2]),
            ("mult_principle_independent_choices", ("階段甲", "階段乙"), (2, 2)),
        ),
        (
            mult_digits_no_repeat,
            "core.vocational_math_b4.generators.counting._sample_mult_digits_no_repeat_params",
            lambda _rng, _d: (6, 3, False),
            ("mult_digits_no_repeat", 6, 3, False),
        ),
        (
            repeated_permutation_assignment,
            "core.vocational_math_b4.generators.counting._sample_repeated_permutation_assignment_params",
            lambda _rng, _d: (3, 3, "tasks_to_people"),
            ("repeated_permutation_assignment", 3, 3, "tasks_to_people"),
        ),
    ],
)
def test_retry_50_failure_raises(fn, monkeypatch, monkey_target, fixed_fn, seen_tuple) -> None:
    monkeypatch.setattr(monkey_target, fixed_fn)
    seen = {seen_tuple}
    with pytest.raises(ValueError):
        fn(skill_id="vh", subskill_id="sub", seed=42, seen_parameter_tuples=seen)
