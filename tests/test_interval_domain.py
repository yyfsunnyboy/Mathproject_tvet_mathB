from __future__ import annotations

from fractions import Fraction

from core.domain.interval_domain_function import count_integer_solutions, format_interval, make_interval, make_union


def test_format_closed_interval() -> None:
    iv = make_interval(Fraction(-8), Fraction(8), True, True)
    assert format_interval(iv) == "[-8,8]"


def test_format_open_interval() -> None:
    iv = make_interval(Fraction(-7), Fraction(7), False, False)
    assert format_interval(iv) == "(-7,7)"


def test_format_union_with_infinity() -> None:
    left = make_interval(None, Fraction(-10), False, False)
    right = make_interval(Fraction(10), None, False, False)
    uv = make_union([left, right])
    assert format_interval(uv) == "(-∞,-10) ∪ (10,∞)"


def test_count_integer_solutions_fraction_bounds() -> None:
    iv = make_interval(Fraction(-2), Fraction(10, 3), True, True)
    assert count_integer_solutions(iv) == 6


def test_count_integer_solutions_infinite_returns_none() -> None:
    iv = make_interval(None, Fraction(3), False, True)
    assert count_integer_solutions(iv) is None
