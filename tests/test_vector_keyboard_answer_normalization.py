# -*- coding: utf-8 -*-
"""Keyboard-friendly vector answer grading (shared checker path)."""

from __future__ import annotations

import re

import pytest

from core.checkers.expression_equivalence_checker import (
    check_expression_equivalence_answer,
    check_expression_equivalence_debug,
)
from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.checkers.vector_answer_normalization import (
    expected_is_directed_segment,
    is_vector_valued_answer_context,
    try_check_vector_answer,
)
from core.domain.vector_plane_domain import build_vector_plane_matrix
from core.gencode.answer_grading import grade_answer_for_current_question
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload


EXPECTED_BC = r"\overrightarrow{BC}"
EXPECTED_AB = r"a+b"


@pytest.mark.parametrize(
    "user_answer",
    ["BC", "->BC", "BC->", "vec(BC)", r"\vec{BC}", r"\overrightarrow{BC}", "bc"],
)
def test_directed_segment_keyboard_forms_pass(user_answer: str) -> None:
    assert check_expression_equivalence_answer(user_answer, EXPECTED_BC)


def test_directed_segment_reversed_fails() -> None:
    assert not check_expression_equivalence_answer("CB", EXPECTED_BC)
    debug = check_expression_equivalence_debug("CB", EXPECTED_BC)
    assert debug.get("correct") is False
    assert debug.get("error_code") != "ANSWER_PARSE_FAILED"


@pytest.mark.parametrize(
    "user_answer",
    ["a+b", r"\vec{a}+\vec{b}", "b+a", "1*a+1*b"],
)
def test_symbolic_vector_sum_keyboard_forms_pass(user_answer: str) -> None:
    assert check_expression_equivalence_answer(
        user_answer,
        EXPECTED_AB,
        answer_contract={"answer_shape": "vector_expression", "key": "vector"},
    )


def test_symbolic_vector_nonequivalent_fails() -> None:
    assert not check_expression_equivalence_answer(
        "a-b",
        EXPECTED_AB,
        answer_contract={"answer_shape": "vector_expression", "key": "vector"},
    )


def test_scalar_context_does_not_coerce_two_letter_token() -> None:
    assert not is_vector_valued_answer_context("12")
    assert not check_expression_equivalence_answer("AB", "12")
    assert not expected_is_directed_segment("ab")
    assert try_check_vector_answer("AB", "ab") is None


def test_production_grading_path_accepts_bc_for_overrightarrow() -> None:
    current = {
        "skill_id": "vh_數學B2_SubSection_3_1_1",
        "skill": "vh_數學B2_SubSection_3_1_1",
        "problem_type_id": "simplify_vector_path_expression",
        "answer_type": "expression",
        "checker": "expression_checker",
        "correct_answer": EXPECTED_BC,
        "answer": EXPECTED_BC,
        "answer_contract": {
            "answer_type": "expression",
            "checker": "expression_checker",
            "checker_key": "expression_checker",
            "answer_equivalence": "algebraic_equivalent",
            "answer_shape": "directed_segment",
            "expected_answer": EXPECTED_BC,
        },
    }
    result = grade_answer_for_current_question(
        "BC",
        current,
        "vh_數學B2_SubSection_3_1_1",
    )
    assert result.get("correct") is True
    assert result.get("status") == "correct"


def test_production_grading_path_rejects_reversed_without_format_error() -> None:
    current = {
        "skill_id": "vh_數學B2_SubSection_3_1_1",
        "skill": "vh_數學B2_SubSection_3_1_1",
        "problem_type_id": "simplify_vector_path_expression",
        "answer_type": "expression",
        "checker": "expression_checker",
        "correct_answer": EXPECTED_BC,
        "answer": EXPECTED_BC,
        "answer_contract": {
            "answer_type": "expression",
            "checker": "expression_checker",
            "checker_key": "expression_checker",
            "answer_equivalence": "algebraic_equivalent",
            "answer_shape": "directed_segment",
            "expected_answer": EXPECTED_BC,
        },
    }
    result = grade_answer_for_current_question(
        "CB",
        current,
        "vh_數學B2_SubSection_3_1_1",
    )
    assert result.get("correct") is False
    assert result.get("status") != "parse_error"
    assert "答案格式不正確" not in str(result.get("result") or "")


def test_simplify_path_family_runtime_accepts_keyboard_segment() -> None:
    matrix = build_vector_plane_matrix(domain_operation="simplify_vector_path_expression", seed=1)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="expression",
        problem_type_id="simplify_vector_path_expression",
        domain_operation="simplify_vector_path_expression",
    )
    expected = str(payload.get("correct_answer") or payload.get("answer") or "")
    assert expected_is_directed_segment(expected) or "overrightarrow" in expected.lower()
    match = re.search(r"\{([A-Za-z]{2})\}", expected)
    token = match.group(1) if match else expected
    assert check_expression_equivalence_answer(
        token,
        expected,
        answer_contract=payload.get("answer_contract"),
        payload=payload,
    )
    assert not check_expression_equivalence_answer(
        token[::-1],
        expected,
        answer_contract=payload.get("answer_contract"),
        payload=payload,
    )


def test_named_basis_accepts_plain_letter_and_vec_markup() -> None:
    matrix = build_vector_plane_matrix(domain_operation="express_named_vectors_in_given_basis", seed=2)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="multi_part",
        problem_type_id="express_named_vectors_in_given_basis",
        domain_operation="express_named_vectors_in_given_basis",
    )
    parts = (payload.get("answer_contract") or {}).get("parts") or []
    assert parts
    student = {str(p["key"]): str(p["expected_answer"]) for p in parts}
    result = check_multi_part_answer(
        student,
        payload.get("correct_answer"),
        answer_contract=payload.get("answer_contract"),
        payload=payload,
    )
    assert result.get("overall_correct") is True

    first = parts[0]
    key = str(first["key"])
    expected = str(first["expected_answer"]).replace(" ", "")
    if re.fullmatch(r"-?[a-zA-Z]", expected):
        letter = expected.replace("-", "")
        signed = "-" if expected.startswith("-") else ""
        student[key] = f"{signed}\\vec{{{letter}}}"
        result2 = check_multi_part_answer(
            student,
            payload.get("correct_answer"),
            answer_contract=payload.get("answer_contract"),
            payload=payload,
        )
        assert result2.get("overall_correct") is True
