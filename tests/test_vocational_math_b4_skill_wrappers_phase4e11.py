"""Phase 4E-11: existing wrappers route new problem types via question_router."""

from __future__ import annotations

import importlib


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


def test_multiplication_principle_wrapper_import() -> None:
    module = importlib.import_module("skills.vh_數學B4_MultiplicationPrinciple")
    assert hasattr(module, "generate")
    assert hasattr(module, "check")


def test_permutation_with_repetition_wrapper_import() -> None:
    module = importlib.import_module("skills.vh_數學B4_PermutationWithRepetition")
    assert hasattr(module, "generate")
    assert hasattr(module, "check")


def test_multiplication_wrapper_mult_principle_independent() -> None:
    module = importlib.import_module("skills.vh_數學B4_MultiplicationPrinciple")
    payload = module.generate(
        level=1,
        seed=1,
        problem_type_id="mult_principle_independent_choices",
    )
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["correct_answer"] == payload["answer"]
    assert payload["skill_id"] == "vh_數學B4_MultiplicationPrinciple"
    assert payload["problem_type_id"] == "mult_principle_independent_choices"
    assert payload["generator_key"] == "b4.counting.mult_principle_independent_choices"
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False
    assert "[BLANK]" not in payload["question_text"]
    assert "[BLANK]" not in payload["explanation"]
    assert "$" in payload["question_text"] or "$" in payload["explanation"]


def test_multiplication_wrapper_mult_digits_no_repeat() -> None:
    module = importlib.import_module("skills.vh_數學B4_MultiplicationPrinciple")
    payload = module.generate(
        level=1,
        seed=1,
        problem_type_id="mult_digits_no_repeat",
    )
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["correct_answer"] == payload["answer"]
    assert payload["skill_id"] == "vh_數學B4_MultiplicationPrinciple"
    assert payload["problem_type_id"] == "mult_digits_no_repeat"
    assert payload["generator_key"] == "b4.counting.mult_digits_no_repeat"
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False
    assert "[BLANK]" not in payload["question_text"]
    assert "[BLANK]" not in payload["explanation"]
    assert "$" in payload["question_text"] or "$" in payload["explanation"]


def test_permutation_with_repetition_wrapper_repeated_assignment() -> None:
    module = importlib.import_module("skills.vh_數學B4_PermutationWithRepetition")
    payload = module.generate(
        level=1,
        seed=1,
        problem_type_id="repeated_permutation_assignment",
    )
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["correct_answer"] == payload["answer"]
    assert payload["skill_id"] == "vh_數學B4_PermutationWithRepetition"
    assert payload["problem_type_id"] == "repeated_permutation_assignment"
    assert payload["generator_key"] == "b4.counting.repeated_permutation_assignment"
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False
    assert "[BLANK]" not in payload["question_text"]
    assert "[BLANK]" not in payload["explanation"]
    assert "$" in payload["question_text"] or "$" in payload["explanation"]
