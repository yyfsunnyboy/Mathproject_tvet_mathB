from __future__ import annotations

import importlib


WRAPPER_CASES = [
    ("skills.vh_數學B4_CombinationApplications", "vh_數學B4_CombinationApplications"),
    ("skills.vh_數學B4_MultiplicationPrinciple", "vh_數學B4_MultiplicationPrinciple"),
    ("skills.vh_數學B4_PermutationOfDistinctObjects", "vh_數學B4_PermutationOfDistinctObjects"),
    ("skills.vh_數學B4_RepeatedPermutation", "vh_數學B4_RepeatedPermutation"),
]

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


def _assert_payload(payload: dict, expected_skill_id: str):
    assert isinstance(payload, dict)
    assert REQUIRED_KEYS.issubset(set(payload.keys()))
    assert payload["correct_answer"] == payload["answer"]
    assert payload["skill_id"] == expected_skill_id
    assert isinstance(payload["choices"], list)
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]

    trace = payload["router_trace"]
    assert isinstance(trace, dict)
    for k in [
        "input_skill_id",
        "selected_subskill_id",
        "selected_problem_type_id",
        "selected_generator_key",
        "selection_reason",
    ]:
        assert k in trace


def test_import_and_symbols_for_all_wrappers():
    for module_path, _ in WRAPPER_CASES:
        module = importlib.import_module(module_path)
        assert hasattr(module, "generate")
        assert hasattr(module, "check")


def test_generate_payload_for_all_wrappers():
    for module_path, expected_skill_id in WRAPPER_CASES:
        module = importlib.import_module(module_path)
        payload = module.generate(level=1, seed=1)
        _assert_payload(payload, expected_skill_id)


def test_check_for_all_wrappers():
    for module_path, _ in WRAPPER_CASES:
        module = importlib.import_module(module_path)
        payload = module.generate(level=1, seed=1)
        answer = payload["answer"]

        ok = module.check(str(answer), answer)
        assert ok["correct"] is True

        wrong = module.check("999999", answer)
        assert wrong["correct"] is False


def test_combination_applications_problem_type_override_polygon():
    module = importlib.import_module("skills.vh_數學B4_CombinationApplications")
    payload = module.generate(level=1, seed=1, problem_type_id="combination_polygon_count")
    _assert_payload(payload, "vh_數學B4_CombinationApplications")
    assert payload["problem_type_id"] == "combination_polygon_count"


def test_combination_applications_problem_type_override_required_excluded():
    module = importlib.import_module("skills.vh_數學B4_CombinationApplications")
    payload = module.generate(level=1, seed=1, problem_type_id="combination_required_excluded_person")
    _assert_payload(payload, "vh_數學B4_CombinationApplications")
    assert payload["problem_type_id"] == "combination_required_excluded_person"
