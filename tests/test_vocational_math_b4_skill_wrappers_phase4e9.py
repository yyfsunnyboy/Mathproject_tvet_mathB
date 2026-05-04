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


def test_combination_wrapper_import_and_symbols() -> None:
    module = importlib.import_module("skills.vh_數學B4_Combination")
    assert hasattr(module, "generate")
    assert hasattr(module, "check")


def test_combination_wrapper_generate_payload_and_check() -> None:
    module = importlib.import_module("skills.vh_數學B4_Combination")
    payload = module.generate(level=1, seed=1)

    assert isinstance(payload, dict)
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["correct_answer"] == payload["answer"]
    assert payload["skill_id"] == "vh_數學B4_Combination"
    assert payload["problem_type_id"] == "combination_basic_selection"
    assert payload["generator_key"] == "b4.combination.combination_basic_selection"
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]

    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False

    assert "[BLANK]" not in payload["question_text"]
    assert "[BLANK]" not in payload["explanation"]
    assert "$" in payload["question_text"] or "$" in payload["explanation"]


def test_existing_permutation_wrapper_supports_formula_evaluation() -> None:
    module = importlib.import_module("skills.vh_數學B4_PermutationOfDistinctObjects")
    payload = module.generate(
        level=1,
        seed=1,
        problem_type_id="permutation_formula_evaluation",
    )

    assert payload["problem_type_id"] == "permutation_formula_evaluation"
    assert payload["generator_key"] == "b4.permutation.permutation_formula_evaluation"


def test_existing_factorial_wrapper_supports_factorial_evaluation() -> None:
    module = importlib.import_module("skills.vh_數學B4_FactorialNotation")
    payload = module.generate(
        level=1,
        seed=1,
        problem_type_id="factorial_evaluation",
    )

    assert payload["problem_type_id"] == "factorial_evaluation"
    assert payload["generator_key"] == "b4.counting.factorial_evaluation"
