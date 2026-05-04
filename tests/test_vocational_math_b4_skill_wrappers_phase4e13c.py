from __future__ import annotations

import importlib

import pytest


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
    assert importlib.import_module("skills.vh_數學B4_BinomialCoefficientIdentities")
    assert importlib.import_module("skills.vh_數學B4_BinomialTheorem")


def test_binomial_coefficient_identities_wrapper_sum() -> None:
    module = importlib.import_module("skills.vh_數學B4_BinomialCoefficientIdentities")
    payload = module.generate(level=1, seed=1, problem_type_id="binomial_coefficient_sum")
    _assert_payload(
        payload,
        "vh_數學B4_BinomialCoefficientIdentities",
        "binomial_coefficient_sum",
        "b4.binomial.binomial_coefficient_sum",
    )
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False


def test_binomial_coefficient_identities_wrapper_equation() -> None:
    module = importlib.import_module("skills.vh_數學B4_BinomialCoefficientIdentities")
    payload = module.generate(level=1, seed=1, problem_type_id="binomial_equation_solve_n")
    _assert_payload(
        payload,
        "vh_數學B4_BinomialCoefficientIdentities",
        "binomial_equation_solve_n",
        "b4.binomial.binomial_equation_solve_n",
    )
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False


def test_binomial_theorem_wrapper_specific_term() -> None:
    module = importlib.import_module("skills.vh_數學B4_BinomialTheorem")
    payload = module.generate(level=1, seed=1, problem_type_id="binomial_specific_term_coefficient")
    _assert_payload(
        payload,
        "vh_數學B4_BinomialTheorem",
        "binomial_specific_term_coefficient",
        "b4.binomial.binomial_specific_term_coefficient",
    )
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False


def test_binomial_theorem_wrapper_default_only_specific_term() -> None:
    module = importlib.import_module("skills.vh_數學B4_BinomialTheorem")
    payload = module.generate(level=1, seed=1)
    assert payload["problem_type_id"] == "binomial_specific_term_coefficient"
    _assert_payload(
        payload,
        "vh_數學B4_BinomialTheorem",
        "binomial_specific_term_coefficient",
        "b4.binomial.binomial_specific_term_coefficient",
    )


def test_binomial_theorem_wrapper_rejects_expansion_basic() -> None:
    module = importlib.import_module("skills.vh_數學B4_BinomialTheorem")
    with pytest.raises(ValueError):
        module.generate(level=1, seed=1, problem_type_id="binomial_expansion_basic")
