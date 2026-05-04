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
    assert not isinstance(payload["answer"], list)
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


def test_binomial_theorem_supports_middle_term_override() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_BinomialTheorem",
        level=1,
        seed=1,
        problem_type_id="binomial_middle_term_coefficient",
    )
    assert payload["problem_type_id"] == "binomial_middle_term_coefficient"
    assert payload["generator_key"] == "b4.binomial.binomial_middle_term_coefficient"
    _assert_common_payload(payload)


def test_binomial_theorem_supports_specific_negative_override() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_BinomialTheorem",
        level=1,
        seed=1,
        problem_type_id="binomial_specific_coefficient_with_negative_term",
    )
    assert payload["problem_type_id"] == "binomial_specific_coefficient_with_negative_term"
    assert payload["generator_key"] == "b4.binomial.binomial_specific_coefficient_with_negative_term"
    _assert_common_payload(payload)


def test_binomial_theorem_default_supported_set_only() -> None:
    payload = generate_for_skill(skill_id="vh_數學B4_BinomialTheorem", level=1, seed=2)
    assert payload["problem_type_id"] in {
        "binomial_specific_term_coefficient",
        "binomial_middle_term_coefficient",
        "binomial_specific_coefficient_with_negative_term",
    }
    assert payload["problem_type_id"] != "binomial_expansion_basic"
    _assert_common_payload(payload)


def test_binomial_theorem_rejects_expansion_basic_override() -> None:
    with pytest.raises(ValueError):
        generate_for_skill(
            skill_id="vh_數學B4_BinomialTheorem",
            level=1,
            seed=1,
            problem_type_id="binomial_expansion_basic",
        )


def test_binomial_coefficient_identities_supports_odd_even_override() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_BinomialCoefficientIdentities",
        level=1,
        seed=1,
        problem_type_id="binomial_odd_even_coefficient_sum",
    )
    assert payload["problem_type_id"] == "binomial_odd_even_coefficient_sum"
    assert payload["generator_key"] == "b4.binomial.binomial_odd_even_coefficient_sum"
    _assert_common_payload(payload)


def test_binomial_coefficient_identities_default_supported_set_only() -> None:
    payload = generate_for_skill(skill_id="vh_數學B4_BinomialCoefficientIdentities", level=1, seed=3)
    assert payload["problem_type_id"] in {
        "binomial_coefficient_sum",
        "binomial_equation_solve_n",
        "binomial_odd_even_coefficient_sum",
    }
    _assert_common_payload(payload)
