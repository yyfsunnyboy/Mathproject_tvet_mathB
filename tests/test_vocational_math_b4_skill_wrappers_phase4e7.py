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


WRAPPERS = [
    (
        "skills.vh_數學B4_AdditionPrinciple",
        "vh_數學B4_AdditionPrinciple",
        "add_principle_mutually_exclusive_choice",
        "b4.counting.add_principle_mutually_exclusive_choice",
    ),
    (
        "skills.vh_數學B4_CombinationProperties",
        "vh_數學B4_CombinationProperties",
        "combination_properties_simplification",
        "b4.combination.combination_properties_simplification",
    ),
    (
        "skills.vh_數學B4_PermutationWithRepetition",
        "vh_數學B4_PermutationWithRepetition",
        "repeated_choice_basic",
        "b4.counting.repeated_choice_basic",
    ),
]


def test_wrapper_import_and_symbols() -> None:
    for module_name, _, _, _ in WRAPPERS:
        module = importlib.import_module(module_name)
        assert hasattr(module, "generate")
        assert hasattr(module, "check")


def test_wrapper_generate_payload_and_check() -> None:
    for module_name, skill_id, problem_type_id, generator_key in WRAPPERS:
        module = importlib.import_module(module_name)
        payload = module.generate(level=1, seed=1)

        assert isinstance(payload, dict)
        assert REQUIRED_KEYS.issubset(payload.keys())
        assert payload["correct_answer"] == payload["answer"]
        assert payload["skill_id"] == skill_id
        assert payload["problem_type_id"] == problem_type_id
        assert payload["generator_key"] == generator_key
        assert len(payload["choices"]) == 4
        assert len(set(payload["choices"])) == 4
        assert payload["answer"] in payload["choices"]

        ok = module.check(str(payload["answer"]), payload["answer"])
        assert ok["correct"] is True
        wrong = module.check("999999", payload["answer"])
        assert wrong["correct"] is False

        assert "[BLANK]" not in payload["question_text"]
        assert "[BLANK]" not in payload["explanation"]
        assert "$" in payload["question_text"] or "$" in payload["explanation"]
