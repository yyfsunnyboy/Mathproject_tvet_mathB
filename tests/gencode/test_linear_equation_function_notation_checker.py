from __future__ import annotations

from core.checkers.linear_equation_equivalent_checker import (
    check_linear_equation_equivalent_answer,
)
from core.checkers.multi_part_answer_checker import check_multi_part_answer


def test_function_notation_and_y_are_equivalent() -> None:
    assert check_linear_equation_equivalent_answer(
        "f(x)=-2/3x-2",
        "y=-2/3x-2",
    )


def test_function_notation_accepts_equivalent_general_form() -> None:
    assert check_linear_equation_equivalent_answer(
        "f(x)=-2/3x-2",
        "2x+3y+6=0",
    )


def test_function_notation_rejects_wrong_slope_or_intercept() -> None:
    expected = "f(x)=-2/3x-2"
    assert not check_linear_equation_equivalent_answer("y=-1/3x-2", expected)
    assert not check_linear_equation_equivalent_answer("y=-2/3x-1", expected)


def test_multi_part_checker_accepts_function_notation() -> None:
    contract = {
        "answer_type": "multi_part",
        "checker": "multi_part_answer_checker",
        "parts": [
            {
                "key": "function_equation",
                "checker": "linear_equation_equivalent_checker",
                "equivalence_type": "linear_equation_equivalent",
                "expected_answer": "f(x)=-2/3x-2",
            }
        ],
    }
    result = check_multi_part_answer(
        {"function_equation": "y=-2/3x-2"},
        {"function_equation": "f(x)=-2/3x-2"},
        answer_contract=contract,
    )
    assert result["overall_correct"] is True
