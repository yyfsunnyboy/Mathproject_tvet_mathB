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


def _assert_payload(payload: dict, skill_id: str, problem_type_id: str, generator_key: str) -> None:
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["correct_answer"] == payload["answer"]
    assert isinstance(payload["answer"], int)
    assert payload["skill_id"] == skill_id
    assert payload["problem_type_id"] == problem_type_id
    assert payload["generator_key"] == generator_key
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    assert "[BLANK]" not in payload["question_text"]
    assert "[BLANK]" not in payload["explanation"]
    assert "$" in payload["question_text"] or "$" in payload["explanation"]


def test_wrapper_imports() -> None:
    assert importlib.import_module("skills.vh_數學B4_PermutationOfDistinctObjects")


def test_permutation_wrapper_adjacent_block() -> None:
    module = importlib.import_module("skills.vh_數學B4_PermutationOfDistinctObjects")
    payload = module.generate(level=1, seed=1, problem_type_id="permutation_adjacent_block")
    _assert_payload(
        payload,
        "vh_數學B4_PermutationOfDistinctObjects",
        "permutation_adjacent_block",
        "b4.permutation.permutation_adjacent_block",
    )
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False


def test_permutation_wrapper_digit_parity() -> None:
    module = importlib.import_module("skills.vh_數學B4_PermutationOfDistinctObjects")
    payload = module.generate(level=1, seed=1, problem_type_id="permutation_digit_parity")
    _assert_payload(
        payload,
        "vh_數學B4_PermutationOfDistinctObjects",
        "permutation_digit_parity",
        "b4.permutation.permutation_digit_parity",
    )
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False


def test_permutation_wrapper_default_supported_set() -> None:
    module = importlib.import_module("skills.vh_數學B4_PermutationOfDistinctObjects")
    payload = module.generate(level=1, seed=1)
    assert payload["problem_type_id"] in {
        "permutation_role_assignment",
        "permutation_formula_evaluation",
        "permutation_full_arrangement",
        "permutation_adjacent_block",
        "permutation_digit_parity",
    }
    assert payload["skill_id"] == "vh_數學B4_PermutationOfDistinctObjects"
    assert payload["correct_answer"] == payload["answer"]
