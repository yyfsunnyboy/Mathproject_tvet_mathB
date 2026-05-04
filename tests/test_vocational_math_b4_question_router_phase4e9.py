from __future__ import annotations

import pytest

from core.vocational_math_b4.services.question_router import generate_for_skill


REQUIRED_KEYS = {
    "question_text",
    "answer",
    "correct_answer",
    "choices",
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
    "router_trace",
}


def _assert_common_payload(payload: dict) -> None:
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["correct_answer"] == payload["answer"]
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    assert "[BLANK]" not in payload["question_text"]
    assert "[BLANK]" not in payload["explanation"]
    assert "$" in payload["question_text"] or "$" in payload["explanation"]

    trace = payload["router_trace"]
    assert isinstance(trace, dict)
    for key in [
        "input_skill_id",
        "selected_subskill_id",
        "selected_problem_type_id",
        "selected_generator_key",
        "selection_reason",
    ]:
        assert key in trace
    assert trace["selected_subskill_id"] == payload["subskill_id"]
    assert trace["selected_problem_type_id"] == payload["problem_type_id"]
    assert trace["selected_generator_key"] == payload["generator_key"]


def test_combination_router_support() -> None:
    payload = generate_for_skill(skill_id="vh_數學B4_Combination", level=1, seed=1)

    assert payload["problem_type_id"] == "combination_basic_selection"
    assert payload["generator_key"] == "b4.combination.combination_basic_selection"
    _assert_common_payload(payload)


def test_permutation_formula_evaluation_router_support() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_PermutationOfDistinctObjects",
        level=1,
        seed=1,
        problem_type_id="permutation_formula_evaluation",
    )

    assert payload["problem_type_id"] == "permutation_formula_evaluation"
    assert payload["generator_key"] == "b4.permutation.permutation_formula_evaluation"
    _assert_common_payload(payload)


def test_permutation_default_still_generates_supported_problem_type() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_PermutationOfDistinctObjects",
        level=1,
        seed=1,
    )

    assert payload["problem_type_id"] in {
        "permutation_role_assignment",
        "permutation_formula_evaluation",
    }
    _assert_common_payload(payload)
    exp = payload["explanation"]
    assert "$" in exp
    assert "P^{" in exp
    assert "P(n," not in exp
    assert "P(" not in exp


def test_factorial_evaluation_router_support() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_FactorialNotation",
        level=1,
        seed=1,
        problem_type_id="factorial_evaluation",
    )

    assert payload["problem_type_id"] == "factorial_evaluation"
    assert payload["generator_key"] == "b4.counting.factorial_evaluation"
    _assert_common_payload(payload)


def test_factorial_default_still_generates_supported_problem_type() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_FactorialNotation",
        level=1,
        seed=1,
    )

    assert payload["problem_type_id"] in {
        "factorial_equation_solve_n",
        "factorial_evaluation",
    }
    _assert_common_payload(payload)


@pytest.mark.parametrize(
    "skill_id,bad_problem_type",
    [
        ("vh_數學B4_Combination", "permutation_formula_evaluation"),
        ("vh_數學B4_PermutationOfDistinctObjects", "factorial_evaluation"),
        ("vh_數學B4_FactorialNotation", "combination_basic_selection"),
    ],
)
def test_invalid_problem_type_for_skill_raises(skill_id: str, bad_problem_type: str) -> None:
    with pytest.raises(ValueError):
        generate_for_skill(skill_id=skill_id, level=1, seed=1, problem_type_id=bad_problem_type)
