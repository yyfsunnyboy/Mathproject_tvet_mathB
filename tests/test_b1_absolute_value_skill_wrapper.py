from __future__ import annotations

import importlib

SKILL_MODULE = "skills.vh_數學B1_AbsoluteValue"
SKILL_ID = "vh_數學B1_AbsoluteValue"
COMPONENT_IDS = ("src_4398", "src_4399", "src_4408", "src_4412")
PROBLEM_TYPES = {
    "solve_basic_absolute_value_equation",
    "number_line_distance_between_two_points",
}


def _module():
    return importlib.import_module(SKILL_MODULE)


def test_v3_thin_facade_exports() -> None:
    module = _module()
    assert hasattr(module, "generate")
    assert hasattr(module, "check")
    assert hasattr(module, "get_hint")
    assert not hasattr(module, "generate_question")


def test_v3_generate_payload_shape() -> None:
    module = _module()
    payload = module.generate(seed=1, component_id="src_4398")

    assert isinstance(payload, dict)
    assert payload["component_id"] == "src_4398"
    assert payload["problem_type_id"] in PROBLEM_TYPES
    assert payload["question_text"]
    assert "question" not in payload
    assert payload["answer"]
    assert payload["correct_answer"] == payload["answer"]
    assert isinstance(payload.get("answer_contract"), dict)
    assert payload["answer_contract"].get("checker_key")


def test_v3_generate_hits_all_production_components() -> None:
    module = _module()
    for component_id in COMPONENT_IDS:
        payload = module.generate(seed=42, component_id=component_id)
        assert payload["component_id"] == component_id
        assert payload["problem_type_id"] in PROBLEM_TYPES
        assert payload["question_text"]
        assert payload["answer_contract"]["checker_key"]


def test_solution_set_check_requires_payload_and_returns_bool() -> None:
    module = _module()
    payload = module.generate(seed=99, component_id="src_4398")
    correct_answer = payload["answer"]

    assert module.check("13,-13", correct_answer) is False
    assert module.check("13,-13", correct_answer, payload) is True
    assert module.check("-13，13", correct_answer, payload) is True
    assert module.check("x=-13 或 x=13", correct_answer, payload) is True
    assert module.check("{-13,13}", correct_answer, payload) is True
    assert module.check("±13", correct_answer, payload) is True
    assert module.check("+-13", correct_answer, payload) is True
    assert module.check("13", correct_answer, payload) is False
    assert module.check("13,-12", correct_answer, payload) is False


def test_integer_distance_check_with_payload_returns_bool() -> None:
    module = _module()
    payload = module.generate(seed=42, component_id="src_4399")
    correct_answer = payload["answer"]

    assert module.check(correct_answer, correct_answer, payload) is True
    assert module.check("__wrong__", correct_answer, payload) is False
