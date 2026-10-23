"""Exact univariate polynomial arithmetic shared by the polynomial-division domain and its adapter.

Polynomials are lists of ``Fraction`` coefficients in *descending* order without leading zeros
(``[]`` is the zero polynomial).  Givens reach this module as plain JSON: every coefficient is an
``int`` or a string such as ``"1/2"`` / ``"0.505"``.  Coefficients that carry one unknown parameter
(``["a", 3]`` means ``3a``) are handled by :class:`LinearForm`.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

Poly = list[Fraction]


def fr(value: Any) -> Fraction:
    if isinstance(value, bool):
        raise ValueError("bool_is_not_a_number")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(str(value).strip())


def norm(coeffs: list[Fraction]) -> Poly:
    out = list(coeffs)
    while out and out[0] == 0:
        out.pop(0)
    return out


def poly(coeffs: Any) -> Poly:
    return norm([fr(c) for c in coeffs])


def deg(p: Poly) -> int:
    return len(p) - 1


def coeff(p: Poly, power: int) -> Fraction:
    return p[deg(p) - power] if 0 <= power <= deg(p) else Fraction(0)


def padd(a: Poly, b: Poly) -> Poly:
    n = max(len(a), len(b))
    x, y = [Fraction(0)] * (n - len(a)) + a, [Fraction(0)] * (n - len(b)) + b
    return norm([u + v for u, v in zip(x, y)])


def pscale(a: Poly, k: Fraction) -> Poly:
    return norm([c * k for c in a])


def psub(a: Poly, b: Poly) -> Poly:
    return padd(a, pscale(b, Fraction(-1)))


def pmul(a: Poly, b: Poly) -> Poly:
    if not a or not b:
        return []
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, u in enumerate(a):
        for j, v in enumerate(b):
            out[i + j] += u * v
    return norm(out)


def pdivmod(f: Poly, g: Poly) -> tuple[Poly, Poly]:
    if not g:
        raise ValueError("division_by_zero_polynomial")
    q: dict[int, Fraction] = {}
    r = list(f)
    while r and deg(r) >= deg(g):
        k = deg(r) - deg(g)
        factor = r[0] / g[0]
        q[k] = factor
        sub = [c * factor for c in g] + [Fraction(0)] * k
        r = norm([u - v for u, v in zip(r, sub)])
    top = deg(f) - deg(g)
    quotient = norm([q.get(k, Fraction(0)) for k in range(top, -1, -1)]) if top >= 0 else []
    return quotient, r


def ev(p: Poly, x: Any) -> Fraction:
    x = fr(x)
    acc = Fraction(0)
    for c in p:
        acc = acc * x + c
    return acc


def synthetic(p: Poly, c: Any) -> tuple[Poly, Fraction, list[list[Fraction]]]:
    """Divide by ``x - c``: returns quotient, remainder and the three table rows."""
    c = fr(c)
    top = list(p) if p else [Fraction(0)]
    carry, third, second = Fraction(0), [], []
    for i, a in enumerate(top):
        second.append(carry * c if i else Fraction(0))
        carry = a + (second[-1] if i else 0)
        third.append(carry)
    return norm(third[:-1]), third[-1], [top, second, third]


def shift_expand(p: Poly, c: Any) -> list[Fraction]:
    """Coefficients of ``p`` in powers of ``(x - c)``, highest power first (repeated synthetic division)."""
    out: list[Fraction] = []
    cur = list(p)
    for _ in range(len(p)):
        cur, r, _rows = synthetic(cur, c)
        out.append(r)
    return list(reversed(out))


def interpolate(points: list[tuple[Fraction, Fraction]]) -> Poly:
    """Newton interpolation through distinct x values."""
    xs = [fr(x) for x, _ in points]
    if len(set(xs)) != len(xs):
        raise ValueError("duplicate_interpolation_nodes")
    n = len(points)
    table = [fr(y) for _, y in points]
    divided = [table[0]]
    for level in range(1, n):
        table = [(table[i + 1] - table[i]) / (xs[i + level] - xs[i]) for i in range(n - level)]
        divided.append(table[0])
    result: Poly = []
    for k in range(n - 1, -1, -1):
        result = padd(pmul(result, [Fraction(1), -xs[k]]), [divided[k]]) if result else norm([divided[k]])
    return result


def solve_linear(rows: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    """Unique solution of ``rows @ x = rhs`` over the rationals; otherwise ``ValueError``."""
    m = [list(r) + [b] for r, b in zip(rows, rhs)]
    n = len(rows[0]) if rows else 0
    pivot_row = 0
    pivots = []
    for col in range(n):
        sel = next((i for i in range(pivot_row, len(m)) if m[i][col] != 0), None)
        if sel is None:
            continue
        m[pivot_row], m[sel] = m[sel], m[pivot_row]
        lead = m[pivot_row][col]
        m[pivot_row] = [v / lead for v in m[pivot_row]]
        for i in range(len(m)):
            if i != pivot_row and m[i][col] != 0:
                factor = m[i][col]
                m[i] = [u - factor * v for u, v in zip(m[i], m[pivot_row])]
        pivots.append(col)
        pivot_row += 1
    if len(pivots) != n:
        raise ValueError("underdetermined_system")
    if any(all(v == 0 for v in row[:-1]) and row[-1] != 0 for row in m):
        raise ValueError("inconsistent_system")
    sol = [Fraction(0)] * n
    for r, col in enumerate(pivots):
        sol[col] = m[r][-1]
    return sol


# --- text -------------------------------------------------------------------------------------------

def frac_text(q: Fraction) -> str:
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def frac_latex(q: Fraction) -> str:
    if q.denominator == 1:
        return str(q.numerator)
    body = f"\\frac{{{abs(q.numerator)}}}{{{q.denominator}}}"
    return f"-{body}" if q < 0 else body


def _term_latex(c: Fraction, power: int, var: str) -> str:
    mag = abs(c)
    mono = "" if power == 0 else (var if power == 1 else f"{var}^{{{power}}}")
    if power == 0:
        return frac_latex(mag)
    if mag.denominator != 1:
        top = ("" if mag.numerator == 1 else str(mag.numerator)) + mono
        return f"\\frac{{{top}}}{{{mag.denominator}}}"
    return ("" if mag == 1 else str(mag.numerator)) + mono


def poly_latex(p: Poly, var: str = "x") -> str:
    if not p:
        return "0"
    text = ""
    for i, c in enumerate(p):
        if c == 0:
            continue
        text += ("-" if c < 0 else ("+" if text else "")) + _term_latex(c, deg(p) - i, var)
    return text


def poly_plain(p: Poly, var: str = "x") -> str:
    if not p:
        return "0"
    text = ""
    for i, c in enumerate(p):
        if c == 0:
            continue
        power, mag = deg(p) - i, abs(c)
        mono = "" if power == 0 else (var if power == 1 else f"{var}^{power}")
        if not mono:
            body = frac_text(mag)
        else:
            body = ("" if mag.numerator == 1 else str(mag.numerator)) + mono + (f"/{mag.denominator}" if mag.denominator != 1 else "")
        text += ("-" if c < 0 else ("+" if text else "")) + body
    return text


def linear_text(a: Fraction, b: Fraction) -> str:
    return poly_latex(poly([a, b]))


def root_of(divisor: Poly) -> Fraction:
    if deg(divisor) != 1:
        raise ValueError("linear_divisor_required")
    return -divisor[1] / divisor[0]


# --- coefficients with one unknown parameter ---------------------------------------------------------

class LinearForm(dict):
    """``{param: coefficient, "": constant}`` with exact Fractions."""

    @classmethod
    def parse(cls, value: Any) -> "LinearForm":
        if isinstance(value, (list, tuple)) and len(value) == 2 and isinstance(value[0], str) and value[0].isalpha():
            return cls({value[0]: fr(value[1])})
        return cls({"": fr(value)})

    def const(self) -> Fraction:
        return self.get("", Fraction(0))

    def params(self) -> list[str]:
        return [k for k, v in self.items() if k and v != 0]

    def __add__(self, other: "LinearForm") -> "LinearForm":
        out = LinearForm(self)
        for k, v in other.items():
            out[k] = out.get(k, Fraction(0)) + v
        return out

    def scale(self, k: Fraction) -> "LinearForm":
        return LinearForm({n: v * k for n, v in self.items()})

    def sub(self, other: "LinearForm") -> "LinearForm":
        return self + other.scale(Fraction(-1))

    def at(self, values: dict[str, Fraction]) -> Fraction:
        return sum((v * (values[k] if k else 1) for k, v in self.items()), Fraction(0))


def lf_poly(coeffs: Any) -> list[LinearForm]:
    return [LinearForm.parse(c) for c in coeffs]


def lf_text(form: LinearForm) -> str:
    """Coefficient text such as ``3a`` / ``-a`` / ``5`` (single-parameter, no constant)."""
    params = form.params()
    if not params:
        return frac_text(form.const())
    if len(params) != 1 or form.const() != 0:
        raise ValueError("unsupported_parametric_coefficient")
    k = form[params[0]]
    return ("" if k == 1 else ("-" if k == -1 else frac_text(k))) + params[0]


def lf_poly_latex(coeffs: list[LinearForm], var: str = "x") -> str:
    n = len(coeffs) - 1
    text = ""
    for i, form in enumerate(coeffs):
        power = n - i
        params = form.params()
        if not params and form.const() == 0:
            continue
        if params:
            body = lf_text(form)
            sign = "-" if body.startswith("-") else ("+" if text else "")
            body = body.lstrip("-")
            mono = "" if power == 0 else (var if power == 1 else f"{var}^{{{power}}}")
            text += sign + body + mono
        else:
            c = form.const()
            text += ("-" if c < 0 else ("+" if text else "")) + _term_latex(c, power, var)
    return text or "0"


def lf_divmod_remainder(f: list[LinearForm], g: Poly) -> tuple[list[list[Fraction]], list[LinearForm]]:
    """Remainder (and quotient coefficients as LinearForms) of ``f`` by a constant-coefficient ``g``."""
    r = [LinearForm(c) for c in f]
    quotient: list[LinearForm] = []
    while len(r) >= len(g):
        factor = r[0].scale(1 / g[0])
        quotient.append(factor)
        for i, gc in enumerate(g):
            r[i] = r[i].sub(factor.scale(gc))
        r.pop(0)
    return quotient, r
