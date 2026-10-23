from __future__ import annotations

import pytest

from core.checkers.linear_relation_set_checker import check_linear_relation_set_answer, parse_relation
from core.gencode.runtime_skill_wrapper import check_answer

SYSTEM = "2x+y-6≤0, 3x-y+1≥0, x+3y-3≥0"
LINES = "x-8y+4=0, x-2y-2=0"


def _ok(student, expected):
    return check_linear_relation_set_answer(student, expected)["correct"]


@pytest.mark.parametrize(
    "student",
    [
        SYSTEM,
        "x+3y-3>=0; 3x-y+1>=0; 2x+y<=6",
        "6-2x-y≥0，y≤3x+1，x+3y≥3",
        "\\left\\{2x+y-6\\le 0, 3x-y+1\\ge 0, x+3y-3\\ge 0\\right.",
        "4x+2y-12≤0, 6x-2y+2≥0, 2x+6y-6≥0",
    ],
)
def test_equivalent_inequality_systems_accepted(student):
    assert _ok(student, SYSTEM)


@pytest.mark.parametrize(
    "student",
    [
        "2x+y-6<0, 3x-y+1≥0, x+3y-3≥0",   # strictness differs
        "2x+y-6≥0, 3x-y+1≥0, x+3y-3≥0",   # wrong side
        "2x+y-6≤0, 3x-y+1≥0",             # missing one
        "2x+y-6≤0, 3x-y+1≥0, x+3y-3≥0, y>0",  # extra one
        "2x+y-7≤0, 3x-y+1≥0, x+3y-3≥0",   # wrong constant
    ],
)
def test_wrong_inequality_systems_rejected(student):
    result = check_linear_relation_set_answer(student, SYSTEM)
    assert result["correct"] is False and not result.get("invalid_input")


@pytest.mark.parametrize("student", ["x-2y-2=0 或 x-8y+4=0", "x-2y=2, 8y=x+4", "2x-4y-4=0;x-8y=-4"])
def test_equation_sets_any_order_and_form(student):
    assert _ok(student, LINES)


@pytest.mark.parametrize("student", ["x-2y-2=0", "x-2y-2=0, x-8y+4=0, x=1", "x-2y-2=0, x-8y+5=0"])
def test_equation_sets_missing_extra_or_wrong_rejected(student):
    assert not _ok(student, LINES)


@pytest.mark.parametrize("student", ["", "abc", "x^2+y=1", "1<x<3", "x+y"])
def test_unreadable_is_invalid_input_not_wrong(student):
    result = check_linear_relation_set_answer(student, SYSTEM)
    assert result["correct"] is False and result["invalid_input"] is True


def test_equation_is_not_the_same_relation_as_an_inequality():
    assert parse_relation("x-y=0") != parse_relation("x-y>=0")


def test_unreadable_expected_is_a_system_error():
    assert check_linear_relation_set_answer("x+y=1", "???")["system_error"] is True


def _contract():
    return {"answer_type": "short_answer", "checker": "linear_relation_set_checker", "checker_key": "linear_relation_set_checker",
            "equivalence_type": "linear_relation_set", "answer_equivalence": "linear_relation_set"}


def test_runtime_check_answer_dispatch():
    ac = _contract()
    payload = {"answer_contract": ac, "correct_answer": LINES}
    assert check_answer("x-2y-2=0, x-8y+4=0", LINES, payload=payload, answer_contract=ac, skill_id="x") is True
    assert check_answer("x-2y-2=0", LINES, payload=payload, answer_contract=ac, skill_id="x") is False


def test_multi_part_part_level_dispatch():
    part = {"key": "part_1", "label": "(1)", **_contract(), "expected_answer": SYSTEM}
    ac = {"answer_type": "multi_part", "checker": "multi_part_answer_checker", "checker_key": "multi_part_answer_checker",
          "equivalence_type": "multi_part_answer", "answer_equivalence": "multi_part_answer", "parts": [part]}
    payload = {"answer_contract": ac, "correct_answer": {"part_1": SYSTEM}}
    assert check_answer({"part_1": "x+3y>=3; 3x-y>=-1; 2x+y<=6"}, {"part_1": SYSTEM}, payload=payload, answer_contract=ac, skill_id="x")
    assert not check_answer({"part_1": "2x+y>=6"}, {"part_1": SYSTEM}, payload=payload, answer_contract=ac, skill_id="x")


def test_registered_in_checker_registry():
    from core.gencode.checker_registry import CHECKER_CAPABILITIES, validate_answer_contract_capability

    assert CHECKER_CAPABILITIES["linear_relation_set_checker"]["runtime_available"] is True
    assert validate_answer_contract_capability(_contract())["checker_capability_status"] == "ok"
