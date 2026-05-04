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


def test_perm_distinct_supports_full_arrangement_override() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_PermutationOfDistinctObjects",
        level=1,
        seed=1,
        problem_type_id="permutation_full_arrangement",
    )
    assert payload["problem_type_id"] == "permutation_full_arrangement"
    assert payload["generator_key"] == "b4.permutation.permutation_full_arrangement"
    _assert_common_payload(payload)


def test_perm_distinct_default_still_supported() -> None:
    payload = generate_for_skill(skill_id="vh_數學B4_PermutationOfDistinctObjects", level=1, seed=3)
    assert payload["problem_type_id"] in {
        "permutation_role_assignment",
        "permutation_formula_evaluation",
        "permutation_full_arrangement",
    }
    _assert_common_payload(payload)


def test_combination_supports_restricted_override() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_Combination",
        level=1,
        seed=1,
        problem_type_id="combination_restricted_selection",
    )
    assert payload["problem_type_id"] == "combination_restricted_selection"
    assert payload["generator_key"] == "b4.combination.combination_restricted_selection"
    _assert_common_payload(payload)


def test_combination_supports_seat_assignment_override() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_Combination",
        level=1,
        seed=1,
        problem_type_id="combination_seat_assignment",
    )
    assert payload["problem_type_id"] == "combination_seat_assignment"
    assert payload["generator_key"] == "b4.combination.combination_seat_assignment"
    _assert_common_payload(payload)


def test_combination_default_still_supported() -> None:
    payload = generate_for_skill(skill_id="vh_數學B4_Combination", level=1, seed=5)
    assert payload["problem_type_id"] in {
        "combination_basic_selection",
        "combination_restricted_selection",
        "combination_seat_assignment",
    }
    _assert_common_payload(payload)


@pytest.mark.parametrize(
    "skill_id,bad_problem_type",
    [
        ("vh_數學B4_PermutationOfDistinctObjects", "combination_seat_assignment"),
        ("vh_數學B4_Combination", "permutation_full_arrangement"),
    ],
)
def test_invalid_problem_type_for_skill_raises(skill_id: str, bad_problem_type: str) -> None:
    with pytest.raises(ValueError):
        generate_for_skill(skill_id=skill_id, level=1, seed=1, problem_type_id=bad_problem_type)
