"""Exact plane-line primitives for general-high Mathematics 1, Unit 5.

Everything here is source-agnostic and exact (``fractions.Fraction`` / integers).  A line is the
normalised integer triple ``(a, b, c)`` for ``a*x + b*y + c = 0``; a point is a pair of Fractions.
Radical distances are carried as ``Radical(coef, radicand)`` with a square-free radicand.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd, isqrt
from typing import Any

Point = tuple[Fraction, Fraction]
Line = tuple[int, int, int]


def fr(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise ValueError("bool_is_not_a_number")
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(str(value).strip())


def pt(value: Any) -> Point:
    return (fr(value[0]), fr(value[1]))


def frac_text(value: Fraction) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def frac_latex(value: Fraction) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    body = f"\\frac{{{abs(value.numerator)}}}{{{value.denominator}}}"
    return f"-{body}" if value < 0 else body


# --- lines ---------------------------------------------------------------------------

def norm_line(a: Any, b: Any, c: Any) -> Line:
    a, b, c = fr(a), fr(b), fr(c)
    if a == 0 and b == 0:
        raise ValueError("degenerate_line")
    scale = 1
    for value in (a, b, c):
        scale = scale * value.denominator // gcd(scale, value.denominator)
    ia, ib, ic = int(a * scale), int(b * scale), int(c * scale)
    g = gcd(gcd(abs(ia), abs(ib)), abs(ic)) or 1
    ia, ib, ic = ia // g, ib // g, ic // g
    if ia < 0 or (ia == 0 and ib < 0):
        ia, ib, ic = -ia, -ib, -ic
    return ia, ib, ic


def line_through(p: Point, q: Point) -> Line:
    if p == q:
        raise ValueError("coincident_points")
    (x1, y1), (x2, y2) = p, q
    return norm_line(y2 - y1, x1 - x2, x2 * y1 - x1 * y2)


def line_slope(line: Line) -> Fraction | None:
    a, b, _ = line
    return None if b == 0 else Fraction(-a, b)


def line_from_point_slope(p: Point, m: Fraction) -> Line:
    return norm_line(m, -1, p[1] - m * p[0])


def vertical_line(x0: Fraction) -> Line:
    return norm_line(1, 0, -x0)


def horizontal_line(y0: Fraction) -> Line:
    return norm_line(0, 1, -y0)


def line_from_intercepts(x_int: Fraction, y_int: Fraction) -> Line:
    if x_int == 0 or y_int == 0:
        raise ValueError("zero_intercept_form")
    return norm_line(y_int, x_int, -x_int * y_int)


def parallel_through(p: Point, line: Line) -> Line:
    a, b, _ = line
    return norm_line(a, b, -(a * p[0] + b * p[1]))


def perpendicular_through(p: Point, line: Line) -> Line:
    a, b, _ = line
    return norm_line(b, -a, a * p[1] - b * p[0])


def intersect(l1: Line, l2: Line) -> Point | None:
    a1, b1, c1 = l1
    a2, b2, c2 = l2
    det = a1 * b2 - a2 * b1
    if det == 0:
        return None
    return (Fraction(b1 * c2 - b2 * c1, det), Fraction(c1 * a2 - c2 * a1, det))


def midpoint(p: Point, q: Point) -> Point:
    return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)


def perp_bisector(p: Point, q: Point) -> Line:
    if p == q:
        raise ValueError("coincident_points")
    m = midpoint(p, q)
    dx, dy = q[0] - p[0], q[1] - p[1]
    return norm_line(dx, dy, -(dx * m[0] + dy * m[1]))


def reflect_point(p: Point, line: Line) -> Point:
    a, b, c = line
    t = Fraction(a * p[0] + b * p[1] + c, a * a + b * b)
    return (p[0] - 2 * a * t, p[1] - 2 * b * t)


def circumcenter(a: Point, b: Point, c: Point) -> Point:
    center = intersect(perp_bisector(a, b), perp_bisector(b, c))
    if center is None:
        raise ValueError("collinear_points")
    return center


def orthocenter(a: Point, b: Point, c: Point) -> Point:
    def altitude(vertex: Point, p: Point, q: Point) -> Line:
        return perpendicular_through(vertex, line_through(p, q))

    center = intersect(altitude(a, b, c), altitude(b, a, c))
    if center is None:
        raise ValueError("collinear_points")
    return center


def side_value(line: Line, p: Point) -> Fraction:
    return line[0] * p[0] + line[1] * p[1] + line[2]


def on_line(line: Line, p: Point) -> bool:
    return side_value(line, p) == 0


def translate_line(line: Line, dx: Fraction, dy: Fraction) -> Line:
    a, b, c = line
    return norm_line(a, b, c - a * dx - b * dy)


def line_text(line: Line) -> str:
    a, b, c = line
    out = ""
    for coef, var in ((a, "x"), (b, "y")):
        if coef == 0:
            continue
        mag = "" if abs(coef) == 1 else str(abs(coef))
        sign = "-" if coef < 0 else ("+" if out else "")
        out += f"{sign}{mag}{var}"
    if c:
        out += f"{'-' if c < 0 else '+'}{abs(c)}"
    return f"{out}=0"


def line_latex(line: Line) -> str:
    return line_text(line)


def general_expr_latex(a: Fraction, b: Fraction, c: Fraction) -> str:
    """Render ``a x + b y + c`` (fractions allowed) without forcing integers."""
    out = ""
    for coef, var in ((fr(a), "x"), (fr(b), "y")):
        if coef == 0:
            continue
        mag = "" if abs(coef) == 1 else (frac_latex(abs(coef)))
        sign = "-" if coef < 0 else ("+" if out else "")
        out += f"{sign}{mag}{var}"
    c = fr(c)
    if c:
        out += f"{'-' if c < 0 else '+'}{frac_latex(abs(c))}"
    return out or "0"


def point_text(p: Point) -> str:
    return f"({frac_text(p[0])},{frac_text(p[1])})"


def point_latex(p: Point, name: str = "") -> str:
    return f"{name}\\left({frac_latex(p[0])},\\ {frac_latex(p[1])}\\right)"


# --- radicals --------------------------------------------------------------------------

def _split_square(n: int) -> tuple[int, int]:
    """n = s*s*t with t square-free -> (s, t)."""
    if n <= 0:
        raise ValueError("positive_radicand_required")
    s, t, p = 1, n, 2
    while p * p <= t:
        while t % (p * p) == 0:
            t //= p * p
            s *= p
        p += 1
    return s, t


@dataclass(frozen=True)
class Radical:
    coef: Fraction
    radicand: int  # square-free, 1 means rational

    def value(self) -> float:
        return float(self.coef) * (self.radicand ** 0.5)

    def canonical(self) -> str:
        if self.radicand == 1 or self.coef == 0:
            return frac_text(self.coef)
        num, den = self.coef.numerator, self.coef.denominator
        sign = "-" if num < 0 else ""
        mag = "" if abs(num) == 1 else f"{abs(num)}*"
        body = f"{sign}{mag}sqrt({self.radicand})"
        return body if den == 1 else f"{body}/{den}"

    def latex(self) -> str:
        if self.radicand == 1 or self.coef == 0:
            return frac_latex(self.coef)
        num, den = self.coef.numerator, self.coef.denominator
        sign = "-" if num < 0 else ""
        mag = "" if abs(num) == 1 else str(abs(num))
        top = f"{mag}\\sqrt{{{self.radicand}}}"
        return f"{sign}{top}" if den == 1 else f"{sign}\\frac{{{top}}}{{{den}}}"

    def is_rational(self) -> bool:
        return self.radicand == 1


def radical_of_ratio(numerator: Fraction, radicand_total: int) -> Radical:
    """numerator / sqrt(radicand_total) in simplest radical form."""
    s, t = _split_square(radicand_total)
    return Radical(Fraction(numerator) / (s * t), t)


def sqrt_radical(n: int) -> Radical:
    s, t = _split_square(n)
    return Radical(Fraction(s), t)


def distance_point_line(p: Point, line: Line) -> Radical:
    a, b, _ = line
    return radical_of_ratio(abs(side_value(line, p)), a * a + b * b)


def distance_parallel_lines(l1: Line, l2: Line) -> Radical:
    a1, b1, c1 = l1
    a2, b2, c2 = l2
    if a1 * b2 - a2 * b1 != 0:
        raise ValueError("lines_not_parallel")
    k = Fraction(a2, a1) if a1 else Fraction(b2, b1)
    return radical_of_ratio(abs(Fraction(c1) - Fraction(c2) / k), a1 * a1 + b1 * b1)


def exact_int_sqrt(n: int) -> int | None:
    if n < 0:
        return None
    r = isqrt(n)
    return r if r * r == n else None
