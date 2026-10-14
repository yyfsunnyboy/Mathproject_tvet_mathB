"""Exact checker for answers that must be written as one simplest fraction.

Accepted: ``7/25``, ``\\frac{7}{25}``, ``-7/25``, ``-\\frac{7}{25}``, ``\\frac{-7}{25}``;
an integer literal is accepted only when the expected value is an integer.
Rejected: decimals (finite or repeating), reducible fractions, a non-positive
denominator, and any value other than the expected one.  Values are compared as
exact ``Fraction`` objects; no float and no raw string equality.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from typing import Any

_FRACTION = re.compile(r"([+-]?)(\d+)/(\d+)")
_INTEGER = re.compile(r"([+-]?)(\d+)")
_NEGATIVE_DENOMINATOR = re.compile(r"[+-]?\d+/[+-]\d+")
_PAREN_INTEGER = re.compile(r"\(([+-]?\d+)\)")
_OUTER_PARENS = re.compile(r"([+-]?)\(([^()]*)\)")


@dataclass(frozen=True)
class FractionForm:
    numerator: int
    denominator: int
    is_integer_literal: bool

    @property
    def value(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)


def _plain(text: Any) -> str:
    from core.checkers.math_input_normalization import latex_to_plain

    # Whitespace between two digits stays: "1 31/90" is a mixed number, not 131/90.
    s = re.sub(r"(?<!\d)\s+|\s+(?!\d)", "", latex_to_plain(text))
    previous = None
    while previous != s:
        previous = s
        s = _PAREN_INTEGER.sub(r"\1", s)
        outer = _OUTER_PARENS.fullmatch(s)
        if outer:
            s = outer.group(1) + outer.group(2)
    return s


def parse_fraction_form(text: Any) -> FractionForm | None:
    """Parse ``[sign]p/q`` (q > 0) or an integer literal; None for every other notation."""
    if isinstance(text, bool) or not isinstance(text, (str, int)):
        return None
    s = _plain(text)
    match = _FRACTION.fullmatch(s)
    if match:
        sign, numerator, denominator = match.groups()
        if int(denominator) == 0:
            return None
        return FractionForm(-int(numerator) if sign == "-" else int(numerator), int(denominator), False)
    match = _INTEGER.fullmatch(s)
    if match:
        sign, digits = match.groups()
        return FractionForm(-int(digits) if sign == "-" else int(digits), 1, True)
    return None


def _is_other_exact_notation(text: Any) -> bool:
    from core.checkers.math_input_normalization import parse_exact_number
    from core.checkers.repeating_decimal_checker import parse_decimal_expansion

    return parse_exact_number(text) is not None or parse_decimal_expansion(text) is not None


def check_simplest_fraction_answer(
    student_answer: Any,
    expected_answer: Any,
    *,
    answer_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from core.checkers.math_input_normalization import parse_exact_number

    expected = parse_exact_number(expected_answer)
    if expected is None:
        return {"correct": False, "reason": "expected_answer_unparseable", "system_error": True}
    if isinstance(student_answer, str) and _NEGATIVE_DENOMINATOR.fullmatch(_plain(student_answer)):
        return {"correct": False, "reason": "denominator_not_positive"}
    form = parse_fraction_form(student_answer)
    if form is None:
        reason = "fraction_form_required" if _is_other_exact_notation(student_answer) else "unparseable_fraction"
        return {"correct": False, "reason": reason}
    if form.is_integer_literal and expected.denominator != 1:
        return {"correct": False, "reason": "value_mismatch"}
    if form.value != expected:
        return {"correct": False, "reason": "value_mismatch"}
    if gcd(abs(form.numerator), form.denominator) != 1:
        return {"correct": False, "reason": "not_simplest"}
    return {
        "correct": True,
        "reason": "correct",
        "normalized_student_answer": f"{form.numerator}/{form.denominator}",
        "normalized_correct_answer": f"{expected.numerator}/{expected.denominator}",
    }
