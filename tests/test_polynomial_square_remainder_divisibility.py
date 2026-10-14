# -*- coding: utf-8 -*-
"""4628-style remainder topology must reuse polynomial_remainder_param_solve."""

from __future__ import annotations

from core.domain.polynomial_domain import (
    _solve_quadratic_square_remainder,
    build_polynomial_matrix,
)


def test_square_remainder_closed_form_matches_evaluation():
    for p, q in ((-1, 1), (1, -1), (-2, 1), (1, -2), (-1, 2), (2, -1)):
        b, c = _solve_quadratic_square_remainder(p, q)
        assert (b + 2 * p) * q + (c - p * p) == 0
        assert (b + 2 * q) * p + (c - q * q) == 0
    b, c = _solve_quadratic_square_remainder(-1, 1)
    assert (b, c) == (0, 3)


def test_example_4628_constraints_use_square_remainder_topology():
    matrix = build_polynomial_matrix(
        seed=7,
        domain_operation="polynomial_remainder_param_solve",
        constraints={
            "presentation_mode": "single_choice",
            "textbook_example_id": 4628,
            "source_example_id": 4628,
            "source_question_text": "若f(x)被(x+1)^2除的餘式被x-1整除",
        },
    )
    question = str(matrix.get("question_text") or "")
    givens = matrix.get("givens") or {}
    assert "餘式" in question
    assert "整除" in question
    assert "二次" in question
    p = int(givens["p"])
    q = int(givens["q"])
    expected_c = p * p + q * q - p * q
    assert str(matrix["answer"]["value"]) == str(expected_c)
    assert len(matrix.get("distractors") or []) == 3
    assert str(expected_c) not in {str(x) for x in matrix["distractors"]}


def test_choice_mode_without_4628_keeps_divisible_a_plus_b():
    matrix = build_polynomial_matrix(
        seed=7,
        domain_operation="polynomial_remainder_param_solve",
        constraints={"presentation_mode": "single_choice"},
    )
    question = str(matrix.get("question_text") or "")
    assert "可被" in question
    assert "a+b" in question
    assert "餘式被" not in question
