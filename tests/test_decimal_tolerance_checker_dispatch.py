"""Minimal tests for decimal_tolerance_checker contract dispatch."""

from __future__ import annotations

import pytest

from core.gencode.answer_grading import grade_answer_for_current_question
from core.gencode.answer_payload import (
    check_decimal_tolerance_answer,
    grade_numeric_contract_answer,
    parse_single_numeric,
)
from core.gencode.runtime_skill_wrapper import check_answer


DECIMAL_TOLERANCE_CONTRACT = {
    "answer_type": "decimal",
    "checker_key": "decimal_tolerance_checker",
    "checker": "decimal_tolerance_checker",
    "answer_equivalence": "decimal_tolerance",
    "equivalence_type": "decimal_tolerance",
    "canonical_answer": "10.7",
    "tolerance": 0.05,
}


@pytest.fixture()
def decimal_contract() -> dict:
    return dict(DECIMAL_TOLERANCE_CONTRACT)


@pytest.mark.parametrize(
    ("student", "expected_correct"),
    [
        ("10.7", True),
        ("10.71", True),
        ("10.714", True),
        ("75/7", True),
        ("10.6", False),
        ("11", False),
    ],
)
def test_decimal_tolerance_checker_cases(
    decimal_contract: dict,
    student: str,
    expected_correct: bool,
) -> None:
    result = check_decimal_tolerance_answer(
        student,
        decimal_contract["canonical_answer"],
        decimal_contract["tolerance"],
    )
    assert result.get("invalid_input") is not True
    assert result.get("system_error") is not True
    assert result["correct"] is expected_correct


def test_decimal_tolerance_empty_string_is_invalid_input(decimal_contract: dict) -> None:
    result = check_decimal_tolerance_answer(
        "",
        decimal_contract["canonical_answer"],
        decimal_contract["tolerance"],
    )
    assert result["correct"] is False
    assert result.get("invalid_input") is True
    assert result.get("result") == "invalid input"


def test_parse_single_numeric_supports_integer_decimal_fraction() -> None:
    assert parse_single_numeric("11") == (11.0, None)
    assert parse_single_numeric("10.7") == (10.7, None)
    assert parse_single_numeric("75/7")[0] == pytest.approx(75 / 7)
    val, err = parse_single_numeric("10.7", require_integer=True)
    assert val is None
    assert err == "invalid"


def test_grade_numeric_contract_dispatches_by_checker_key(decimal_contract: dict) -> None:
    ok = grade_numeric_contract_answer("10.714", "10.7", decimal_contract)
    assert ok["correct"] is True
    bad = grade_numeric_contract_answer("11", "10.7", decimal_contract)
    assert bad["correct"] is False


def test_grade_answer_for_current_question_uses_contract_checker(decimal_contract: dict) -> None:
    current = {
        "skill_id": "test_skill",
        "problem_type_id": "test_problem",
        "correct_answer": "10.7",
        "answer": "10.7",
        "answer_contract": decimal_contract,
        "checker": "decimal_tolerance_checker",
        "answer_type": "decimal",
    }
    ok = grade_answer_for_current_question("75/7", current, "test_skill")
    assert ok is not None
    assert ok["correct"] is True

    empty = grade_answer_for_current_question("", current, "test_skill")
    assert empty is not None
    assert empty.get("invalid_input") is True
    assert empty.get("result") == "invalid input"


def test_runtime_check_answer_does_not_int_cast_decimal(decimal_contract: dict) -> None:
    payload = {
        "answer_contract": decimal_contract,
        "checker": "decimal_tolerance_checker",
        "answer_type": "decimal",
    }
    assert check_answer("10.71", "10.7", payload=payload, answer_contract=decimal_contract) is True
    assert check_answer("11", "10.7", payload=payload, answer_contract=decimal_contract) is False


def test_decimal_tolerance_missing_tolerance_is_system_error() -> None:
    contract = {
        "checker_key": "decimal_tolerance_checker",
        "canonical_answer": "10.7",
    }
    result = grade_numeric_contract_answer("10.7", "10.7", contract)
    assert result.get("system_error") is True
    assert "容許誤差" in str(result.get("result", ""))
