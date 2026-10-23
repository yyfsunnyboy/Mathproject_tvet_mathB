"""Exact circle primitives for general-high Mathematics 1, Unit 6 (圓方程式).

A circle is the triple ``(h, k, r2)`` of Fractions: centre ``(h, k)`` and squared radius ``r2``.  The
general form is ``a(x^2+y^2)+d x+e y+f=0``.  Point / line primitives come from the shared exact helpers
of ``analytic_geometry.line_equations`` (``line_geometry``); nothing here is source specific.
"""

from __future__ import annotations

from fractions import Fraction
from math import isqrt
from typing import Any

from core.domain.promoted.analytic_geometry_lines import line_geometry as G
from core.domain.promoted.analytic_geometry_lines.line_geometry import Radical, fr, frac_latex, frac_text, pt

Circle = tuple[Fraction, Fraction, Fraction]

__all__ = [
    "G", "Radical", "fr", "frac_latex", "frac_text", "pt", "Circle",
    "radical_of_fraction", "exact_sqrt_fraction", "circle_from_general", "classify_r2", "dist2",
    "std_text", "std_latex", "general_latex", "general_text", "point_on_circle", "relation_to_circle",
]


def exact_sqrt_fraction(value: Fraction) -> Fraction | None:
    value = Fraction(value)
    if value < 0:
        return None
    num, den = isqrt(value.numerator), isqrt(value.denominator)
    if num * num == value.numerator and den * den == value.denominator:
        return Fraction(num, den)
    return None


def radical_of_fraction(value: Fraction) -> Radical:
    """``sqrt(value)`` for a positive rational in simplest radical form (coef * sqrt(square-free))."""
    value = Fraction(value)
    if value <= 0:
        raise ValueError("positive_value_required")
    s, t = G._split_square(value.numerator * value.denominator)  # sqrt(p/q) = sqrt(p*q)/q
    return Radical(Fraction(s, value.denominator), t)


def dist2(p: Any, q: Any) -> Fraction:
    (x1, y1), (x2, y2) = pt(p), pt(q)
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


def circle_from_general(d: Any, e: Any, f: Any, a: Any = 1) -> Circle:
    """``a(x^2+y^2)+d x+e y+f=0`` -> (h, k, r2); r2 may be <= 0 (point / empty)."""
    a, d, e, f = fr(a), fr(d), fr(e), fr(f)
    if a == 0:
        raise ValueError("not_a_circle_form")
    d, e, f = d / a, e / a, f / a
    h, k = -d / 2, -e / 2
    return (h, k, h * h + k * k - f)


def classify_r2(r2: Fraction) -> str:
    r2 = Fraction(r2)
    return "circle" if r2 > 0 else ("point" if r2 == 0 else "none")


def relation_to_circle(circle: Circle, p: Any) -> str:
    h, k, r2 = circle
    d2 = dist2((h, k), p)
    return "inside" if d2 < r2 else ("outside" if d2 > r2 else "on")


def point_on_circle(circle: Circle, p: Any) -> bool:
    return relation_to_circle(circle, p) == "on"


# --- text -----------------------------------------------------------------------------------------

def _shift_text(var: str, centre: Fraction) -> str:
    if centre == 0:
        return f"{var}^2"
    sign = "-" if centre > 0 else "+"
    return f"({var}{sign}{frac_text(abs(centre))})^2"


def std_text(h: Any, k: Any, r2: Any) -> str:
    """Classroom standard form, e.g. ``(x-2)^2+(y+3)^2=16`` (plain text the equation checker parses)."""
    h, k, r2 = fr(h), fr(k), fr(r2)
    return f"{_shift_text('x', h)}+{_shift_text('y', k)}={frac_text(r2)}"


def _shift_latex(var: str, centre: Fraction) -> str:
    if centre == 0:
        return f"{var}^{{2}}"
    sign = "-" if centre > 0 else "+"
    return f"\\left({var}{sign}{frac_latex(abs(centre))}\\right)^{{2}}"


def std_latex(h: Any, k: Any, r2: Any) -> str:
    h, k, r2 = fr(h), fr(k), fr(r2)
    return f"{_shift_latex('x', h)}+{_shift_latex('y', k)}={frac_latex(r2)}"


def _terms_latex(terms: list[tuple[Fraction, str]]) -> str:
    out = ""
    for coef, symbol in terms:
        if coef == 0:
            continue
        mag = frac_latex(abs(coef)) if (abs(coef) != 1 or not symbol) else ""
        sign = "-" if coef < 0 else ("+" if out else "")
        out += f"{sign}{mag}{symbol}"
    return out or "0"


def general_latex(d: Any, e: Any, f: Any, a: Any = 1) -> str:
    a, d, e, f = fr(a), fr(d), fr(e), fr(f)
    return _terms_latex([(a, "x^{2}"), (a, "y^{2}"), (d, "x"), (e, "y"), (f, "")]) + "=0"


def general_text(d: Any, e: Any, f: Any, a: Any = 1) -> str:
    a, d, e, f = fr(a), fr(d), fr(e), fr(f)
    out = ""
    for coef, symbol in ((a, "x^2"), (a, "y^2"), (d, "x"), (e, "y"), (f, "")):
        if coef == 0:
            continue
        mag = frac_text(abs(coef)) if (abs(coef) != 1 or not symbol) else ""
        if coef.denominator != 1 and symbol:
            mag = f"({mag})*"
        sign = "-" if coef < 0 else ("+" if out else "")
        out += f"{sign}{mag}{symbol}"
    return f"{out}=0"
