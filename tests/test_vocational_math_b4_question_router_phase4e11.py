"""Phase 4E-11: router entries for mult_principle, mult_digits_no_repeat, repeated_permutation_assignment."""

from __future__ import annotations

import pytest

from core.vocational_math_b4.services import question_router as question_router_module
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

MULT_SKILL = "vh_數學B4_MultiplicationPrinciple"
PERM_REP_SKILL = "vh_數學B4_PermutationWithRepetition"


def test_multiplication_principle_registry_uses_canonical_skill_id_only() -> None:
    """MultiplicationPrinciple must not rely on mojibake keys; canonical key holds the list."""
    reg = question_router_module._REGISTRY
    assert "vh_數學B4_MultiplicationPrinciple" in reg
    assert "vh_?閰券?B4_MultiplicationPrinciple" not in reg


def _assert_new_payload(payload: dict) -> None:
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


def test_multiplication_principle_mult_principle_independent_router() -> None:
    payload = generate_for_skill(
        skill_id=MULT_SKILL,
        level=1,
        seed=11,
        problem_type_id="mult_principle_independent_choices",
    )
    assert payload["problem_type_id"] == "mult_principle_independent_choices"
    assert payload["generator_key"] == "b4.counting.mult_principle_independent_choices"
    assert payload["subskill_id"] == "b4_ch1_mult_principle_independent_01"
    _assert_new_payload(payload)


def test_multiplication_principle_mult_digits_no_repeat_router() -> None:
    payload = generate_for_skill(
        skill_id=MULT_SKILL,
        level=1,
        seed=12,
        problem_type_id="mult_digits_no_repeat",
    )
    assert payload["problem_type_id"] == "mult_digits_no_repeat"
    assert payload["generator_key"] == "b4.counting.mult_digits_no_repeat"
    assert payload["subskill_id"] == "b4_ch1_mult_digits_no_repeat_01"
    _assert_new_payload(payload)


def test_multiplication_principle_default_still_supported() -> None:
    payload = generate_for_skill(skill_id=MULT_SKILL, level=1, seed=99)
    assert payload["problem_type_id"] in {
        "divisor_count_prime_factorization",
        "mult_principle_independent_choices",
        "mult_digits_no_repeat",
    }
    _assert_new_payload(payload)


def test_permutation_with_repetition_repeated_assignment_router() -> None:
    payload = generate_for_skill(
        skill_id=PERM_REP_SKILL,
        level=1,
        seed=13,
        problem_type_id="repeated_permutation_assignment",
    )
    assert payload["problem_type_id"] == "repeated_permutation_assignment"
    assert payload["generator_key"] == "b4.counting.repeated_permutation_assignment"
    assert payload["subskill_id"] == "b4_ch1_rep_perm_assignment_01"
    _assert_new_payload(payload)


def test_permutation_with_repetition_default_still_supported() -> None:
    payload = generate_for_skill(skill_id=PERM_REP_SKILL, level=1, seed=88)
    assert payload["problem_type_id"] in {
        "repeated_choice_basic",
        "repeated_permutation_assignment",
    }
    _assert_new_payload(payload)


@pytest.mark.parametrize(
    "skill_id,bad_problem_type",
    [
        (MULT_SKILL, "repeated_choice_basic"),
        (MULT_SKILL, "repeated_permutation_assignment"),
        (PERM_REP_SKILL, "mult_digits_no_repeat"),
        (PERM_REP_SKILL, "divisor_count_prime_factorization"),
    ],
)
def test_invalid_problem_type_for_skill_raises(skill_id: str, bad_problem_type: str) -> None:
    with pytest.raises(ValueError):
        generate_for_skill(skill_id=skill_id, level=1, seed=1, problem_type_id=bad_problem_type)
