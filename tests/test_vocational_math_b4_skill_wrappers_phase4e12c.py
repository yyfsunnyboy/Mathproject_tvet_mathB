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
    assert importlib.import_module("skills.vh_數學B4_Combination")


def test_permutation_wrapper_full_arrangement() -> None:
    module = importlib.import_module("skills.vh_數學B4_PermutationOfDistinctObjects")
    payload = module.generate(level=1, seed=1, problem_type_id="permutation_full_arrangement")
    _assert_payload(
        payload,
        "vh_數學B4_PermutationOfDistinctObjects",
        "permutation_full_arrangement",
        "b4.permutation.permutation_full_arrangement",
    )
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False


def test_combination_wrapper_restricted_selection() -> None:
    module = importlib.import_module("skills.vh_數學B4_Combination")
    payload = module.generate(level=1, seed=1, problem_type_id="combination_restricted_selection")
    _assert_payload(
        payload,
        "vh_數學B4_Combination",
        "combination_restricted_selection",
        "b4.combination.combination_restricted_selection",
    )
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False


def test_combination_wrapper_seat_assignment() -> None:
    module = importlib.import_module("skills.vh_數學B4_Combination")
    payload = module.generate(level=1, seed=1, problem_type_id="combination_seat_assignment")
    _assert_payload(
        payload,
        "vh_數學B4_Combination",
        "combination_seat_assignment",
        "b4.combination.combination_seat_assignment",
    )
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False
