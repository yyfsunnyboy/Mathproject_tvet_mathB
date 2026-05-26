from __future__ import annotations

import importlib

MODULE_NAME = "skills.vh_數學B1_NumberLine"
SKILL_ID = "vh_數學B1_NumberLine"
ALLOWED_PROBLEM_TYPES = {
    "number_line_point_value_reading",
    "number_line_distance_between_points",
}


def _module():
    return importlib.import_module(MODULE_NAME)


def test_generate_level1_payload_shape() -> None:
    mod = _module()
    payload = mod.generate(level=1, seed=1)

    assert payload["skill_id"] == SKILL_ID
    assert payload["problem_type_id"] in ALLOWED_PROBLEM_TYPES
    assert payload["question_text"]
    assert payload["question"]
    assert payload["answer"]
    assert payload["correct_answer"] == payload["answer"]
    assert payload["answer_type"] == "integer"
    assert payload["answer_contract"]["checker_key"] == "integer_checker"
    assert payload["source_coverage_status"] == "INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES"
    assert payload["bootstrap_mode"] is True
    assert payload["bootstrap_source_skill_id"] == "jh_數學1上_NumberLine"
    assert payload["skill_id"] != "jh_數學1上_NumberLine"


def test_generate_level1_can_hit_both_problem_types() -> None:
    mod = _module()
    seen = set()
    for seed in range(20):
        payload = mod.generate(level=1, seed=seed)
        seen.add(payload["problem_type_id"])
    assert seen == ALLOWED_PROBLEM_TYPES


def test_generate_level2_payload_shape() -> None:
    mod = _module()
    payload = mod.generate(level=2)

    assert payload["skill_id"] == SKILL_ID
    assert payload["problem_type_id"] == "number_line_distance_between_points"
    assert payload["answer_contract"]["checker_key"] == "integer_checker"


def test_check_numeric_exact() -> None:
    mod = _module()
    assert mod.check("5", "5")["correct"] is True
    assert mod.check("5.0", "5")["correct"] is True
    assert mod.check("6", "5")["correct"] is False

