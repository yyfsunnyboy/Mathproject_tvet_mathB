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


def test_addition_principle_router_support() -> None:
    payload = generate_for_skill(skill_id="vh_數學B4_AdditionPrinciple", level=1, seed=1)
    assert payload["problem_type_id"] == "add_principle_mutually_exclusive_choice"
    assert payload["generator_key"] == "b4.counting.add_principle_mutually_exclusive_choice"
    _assert_common_payload(payload)


def test_combination_properties_router_support() -> None:
    payload = generate_for_skill(skill_id="vh_數學B4_CombinationProperties", level=1, seed=2)
    assert payload["problem_type_id"] == "combination_properties_simplification"
    assert payload["generator_key"] == "b4.combination.combination_properties_simplification"
    _assert_common_payload(payload)


def test_repeated_choice_router_support() -> None:
    payload = generate_for_skill(skill_id="vh_數學B4_PermutationWithRepetition", level=1, seed=3)
    assert payload["problem_type_id"] == "repeated_choice_basic"
    assert payload["generator_key"] == "b4.counting.repeated_choice_basic"
    _assert_common_payload(payload)


@pytest.mark.parametrize(
    "skill_id,bad_problem_type",
    [
        ("vh_數學B4_AdditionPrinciple", "combination_properties_simplification"),
        ("vh_數學B4_CombinationProperties", "repeated_choice_basic"),
        ("vh_數學B4_PermutationWithRepetition", "add_principle_mutually_exclusive_choice"),
    ],
)
def test_invalid_problem_type_for_skill_raises(skill_id: str, bad_problem_type: str) -> None:
    with pytest.raises(ValueError):
        generate_for_skill(skill_id=skill_id, level=1, seed=1, problem_type_id=bad_problem_type)
