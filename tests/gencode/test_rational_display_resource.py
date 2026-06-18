# -*- coding: utf-8 -*-
"""Regression tests for shared V3 rational/display formatting resources."""

from __future__ import annotations

from fractions import Fraction

from core.gencode.resources.rational_display import (
    canonicalize_multi_part_display,
    canonicalize_part_display_answer,
    canonicalize_display_answer,
    fraction_to_latex,
    fraction_to_plain,
    normalize_fraction_value,
    normalize_linear_expression_display,
)


def test_fraction_to_plain_and_latex_negative_fraction():
    value = Fraction(-3, 2)

    assert fraction_to_plain(value) == "-3/2"
    assert fraction_to_latex(value) == r"-\frac{3}{2}"


def test_fraction_to_plain_and_latex_integer_fraction():
    value = Fraction(4, 1)

    assert fraction_to_plain(value) == "4"
    assert fraction_to_latex(value) == "4"


def test_normalize_fraction_value_moves_negative_sign_to_numerator():
    normalized = normalize_fraction_value(Fraction(3, -2))

    assert normalized == Fraction(-3, 2)
    assert normalized.numerator == -3
    assert normalized.denominator == 2


def test_normalize_fraction_value_accepts_latex_fraction():
    normalized = normalize_fraction_value(r"-\frac{3}{2}")

    assert normalized == Fraction(-3, 2)


def test_normalize_linear_expression_display_removes_unit_and_zero_terms():
    assert normalize_linear_expression_display("1x + -3") == "x - 3"
    assert normalize_linear_expression_display("-1x + 0") == "-x"
    assert normalize_linear_expression_display("0x + 5") == "5"


def test_normalize_linear_expression_display_preserves_equation_lhs():
    assert normalize_linear_expression_display("y = 1x + 0") == "y = x"
    assert normalize_linear_expression_display("y = -1x + 2") == "y = -x + 2"
    assert normalize_linear_expression_display("y = 2x + -3") == "y = 2x - 3"


def test_canonicalize_display_answer_normalizes_rational_and_linear_answer():
    assert canonicalize_display_answer(Fraction(-3, 2)) == r"-\frac{3}{2}"
    assert canonicalize_display_answer("y = 1x + -3") == "y = x - 3"
    assert canonicalize_display_answer("-3/2", answer_type="rational") == r"-\frac{3}{2}"


def test_canonicalize_multi_part_display_normalizes_parts_without_changing_expected_answers():
    part = {
        "key": "area",
        "checker": "rational_checker",
        "expected_answer": "5/2",
    }
    assert canonicalize_part_display_answer(part) == r"\frac{5}{2}"
    assert part["expected_answer"] == "5/2"

    display = canonicalize_multi_part_display(
        {
            "equation": "5x - y + 5 = 0",
            "area": "5/2",
            "negative": "-3/2",
        }
    )
    assert display == {
        "equation": "5x - y + 5 = 0",
        "area": r"\frac{5}{2}",
        "negative": r"-\frac{3}{2}",
    }
