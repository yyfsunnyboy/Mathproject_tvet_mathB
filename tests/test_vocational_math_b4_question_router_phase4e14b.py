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
    assert isinstance(payload["answer"], int)
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


def test_perm_distinct_supports_adjacent_block_override() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_PermutationOfDistinctObjects",
        level=1,
        seed=1,
        problem_type_id="permutation_adjacent_block",
    )
    assert payload["problem_type_id"] == "permutation_adjacent_block"
    assert payload["generator_key"] == "b4.permutation.permutation_adjacent_block"
    _assert_common_payload(payload)


def test_perm_distinct_supports_digit_parity_override() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_PermutationOfDistinctObjects",
        level=1,
        seed=1,
        problem_type_id="permutation_digit_parity",
    )
    assert payload["problem_type_id"] == "permutation_digit_parity"
    assert payload["generator_key"] == "b4.permutation.permutation_digit_parity"
    _assert_common_payload(payload)


def test_perm_distinct_default_still_supported() -> None:
    payload = generate_for_skill(skill_id="vh_數學B4_PermutationOfDistinctObjects", level=1, seed=3)
    assert payload["problem_type_id"] in {
        "permutation_role_assignment",
        "permutation_formula_evaluation",
        "permutation_full_arrangement",
        "permutation_adjacent_block",
        "permutation_digit_parity",
    }
    _assert_common_payload(payload)


def test_invalid_problem_type_for_perm_distinct_raises() -> None:
    with pytest.raises(ValueError):
        generate_for_skill(
            skill_id="vh_數學B4_PermutationOfDistinctObjects",
            level=1,
            seed=1,
            problem_type_id="binomial_coefficient_sum",
        )
