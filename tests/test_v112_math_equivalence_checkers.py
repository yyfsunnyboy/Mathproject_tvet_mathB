# -*- coding: utf-8 -*-
"""v1.12 shared-layer mathematical equivalence (not string compare)."""
from __future__ import annotations

from core.checkers.choice_label_checker import check_choice_label
from core.checkers.expression_equivalence_checker import (
    check_equation_equivalence_answer,
    check_equation_equivalence_debug,
    check_expression_equivalence_answer,
    check_expression_equivalence_debug,
)
from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.gencode.answer_grading import grade_answer_for_current_question
from core.gencode.answer_payload import grade_numeric_contract_answer
from core.gencode.runtime_skill_wrapper import check_answer


def test_expression_factor_order_and_spaces_pass() -> None:
    canonical = "(x-1)(x-2)"
    for student in ("(x-1)(x-2)", "(x-2)(x-1)", "(x - 1) (x - 2)"):
        assert check_expression_equivalence_answer(student, canonical) is True
        assert check_answer(
            student,
            canonical,
            answer_contract={
                "answer_type": "expression",
                "checker": "expression_checker",
                "equivalence_type": "algebraic_equivalent",
            },
        )


def test_expression_wrong_factors_fail() -> None:
    canonical = "(x-1)(x-2)"
    for student in ("(x+1)(x-2)", "(x-1)(x+2)"):
        assert check_expression_equivalence_answer(student, canonical) is False


def test_implicit_multiplication_pass() -> None:
    cases = [
        ("2(x+1)", "2*x+2"),
        ("2x", "2*x"),
        ("x(x+3)", "x**2+3*x"),
        ("3x(x-2)", "3*x*(x-2)"),
    ]
    for student, canonical in cases:
        assert check_expression_equivalence_answer(student, canonical) is True, student


def test_fraction_math_equivalence() -> None:
    contract = {
        "answer_type": "rational",
        "checker": "rational_checker",
        "equivalence_type": "rational_equivalent",
    }
    for student in ("1/2", "2/4", "3/6"):
        result = grade_numeric_contract_answer(student, "1/2", contract, checker="rational_checker")
        assert result.get("correct") is True, student
        assert check_answer(student, "1/2", answer_contract=contract)


def test_integer_numeric_equivalence() -> None:
    contract = {
        "answer_type": "integer",
        "checker": "integer_checker",
        "equivalence_type": "numeric_equivalence",
    }
    for student in ("2", "+2", "2.0"):
        result = grade_numeric_contract_answer(student, "2", contract, checker="integer_checker")
        assert result.get("correct") is True, student
    assert grade_numeric_contract_answer("3", "2", contract, checker="integer_checker")["correct"] is False


def test_equation_equivalence_pass_and_fail() -> None:
    canonical = "x=3"
    for student in ("x=3", "3=x", "2x=6", "x-3=0"):
        assert check_equation_equivalence_answer(student, canonical) is True, student
        assert check_answer(
            student,
            canonical,
            answer_contract={
                "answer_type": "equation",
                "checker": "equation_checker",
                "equivalence_type": "equation_equivalent",
            },
        )
    assert check_equation_equivalence_answer("x=4", canonical) is False


def test_factorized_required_form() -> None:
    contract = {
        "answer_type": "expression",
        "checker": "expression_checker",
        "equivalence_type": "algebraic_equivalent",
        "required_form": "factorized",
        "problem_type_id": "polynomial_factoring",
    }
    canonical = "(x-1)(x-2)"
    assert check_expression_equivalence_answer(
        "(x-1)(x-2)", canonical, answer_contract=contract
    )
    assert check_expression_equivalence_answer(
        "(x-2)(x-1)", canonical, answer_contract=contract
    )
    dbg = check_expression_equivalence_debug(
        "x^2-3x+2",
        canonical,
        answer_contract=contract,
    )
    assert dbg["correct"] is False
    assert dbg.get("required_form_failed") is True
    assert check_answer("x^2-3x+2", canonical, answer_contract=contract) is False
    assert check_answer("(x-2)(x-1)", canonical, answer_contract=contract) is True


def test_multi_part_per_part_math_equivalence() -> None:
    ac = {
        "answer_type": "multi_part",
        "checker": "multi_part_answer_checker",
        "equivalence_type": "multi_part_answer",
        "parts": [
            {
                "key": "part_1",
                "checker": "expression_checker",
                "equivalence_type": "algebraic_equivalent",
                "expected_answer": "(x-1)(x+1)",
            },
            {
                "key": "part_2",
                "checker": "rational_checker",
                "equivalence_type": "rational_equivalent",
                "expected_answer": "1/2",
            },
        ],
    }
    result = check_multi_part_answer(
        {"part_1": "(x+1)(x-1)", "part_2": "2/4"},
        {"part_1": "(x-1)(x+1)", "part_2": "1/2"},
        answer_contract=ac,
    )
    assert result["overall_correct"] is True
    assert check_answer(
        {"part_1": "(x+1)(x-1)", "part_2": "2/4"},
        {"part_1": "(x-1)(x+1)", "part_2": "1/2"},
        answer_contract=ac,
    )


def test_parse_failure_is_not_silent_incorrect() -> None:
    dbg = check_expression_equivalence_debug("@@@", "(x-1)(x-2)")
    assert dbg.get("error_code") == "ANSWER_PARSE_FAILED"
    assert dbg.get("correct") is False
    current = {
        "skill_id": "vh_數學B1_PolynomialFactoring",
        "problem_type_id": "polynomial_factoring",
        "answer_type": "expression",
        "checker": "expression_checker",
        "correct_answer": "(x-1)(x-2)",
        "answer": "(x-1)(x-2)",
        "answer_contract": {
            "answer_type": "expression",
            "checker": "expression_checker",
            "equivalence_type": "algebraic_equivalent",
        },
    }
    graded = grade_answer_for_current_question("@@@", current, "vh_數學B1_PolynomialFactoring")
    assert graded is not None
    assert graded.get("error_code") == "ANSWER_PARSE_FAILED"
    assert graded.get("status") == "parse_error"


def test_equation_parse_failure() -> None:
    dbg = check_equation_equivalence_debug("not-an-eq", "x=3")
    assert dbg.get("error_code") == "ANSWER_PARSE_FAILED"


def test_assignment_list_math_equivalence() -> None:
    ac = {
        "answer_type": "expression",
        "checker": "expression_checker",
        "equivalence_type": "algebraic_equivalent",
    }
    assert check_expression_equivalence_answer("a=-1,b=-3", "a=-1,b=-3", answer_contract=ac)
    assert check_expression_equivalence_answer("b=-3,a=-1", "a=-1,b=-3", answer_contract=ac)
    assert check_expression_equivalence_answer("a=0,b=-3", "a=-1,b=-3", answer_contract=ac) is False


def test_single_choice_semantic_mapping() -> None:
    choices = [
        {"label": "A", "text": "(x-1)(x-2)"},
        {"label": "B", "text": "(x+1)(x-2)"},
        {"label": "C", "text": "x^2-3x+2"},
        {"label": "D", "text": "(x-1)(x+2)"},
    ]
    choice_ac = {
        "answer_type": "single_choice",
        "equivalence_type": "choice_label",
        "checker": "choice_label_checker",
        "presentation_mode": "single_choice",
    }
    assert check_choice_label("A", "(x-1)(x-2)", choices)
    assert check_choice_label("A", "A", choices)
    assert check_choice_label("(x-1)(x-2)", "A", choices)
    assert check_choice_label("B", "A", choices) is False
    assert check_answer(
        "A",
        "(x-1)(x-2)",
        payload={"choices": choices},
        answer_contract=choice_ac,
    )


def test_text_short_stays_text() -> None:
    ac = {
        "answer_type": "text_short",
        "checker": "text_short_checker",
        "equivalence_type": "normalized_text_equivalence",
    }
    assert check_answer("第一象限", "第一象限", answer_contract=ac)
    assert check_answer("無解", "無解", answer_contract=ac)
    assert check_answer("第一象限", "第二象限", answer_contract=ac) is False
