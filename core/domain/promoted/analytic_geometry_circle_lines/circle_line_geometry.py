"""Exact circle-and-line primitives for general-high Mathematics 1, Unit 7 (圓與直線的關係).

A circle is ``(h, k, r2)`` (Fractions, centre and squared radius) and a line is the normalised integer
triple ``(a, b, c)`` of ``a x + b y + c = 0``.  Circle / point / line helpers are imported from the
promoted exact packages of ``analytic_geometry.circle_equations`` and ``analytic_geometry.line_equations``;
everything added here is the circle-and-line relationship itself and is source agnostic.

Parameter conditions use polynomials in one parameter, stored as coefficient lists ``[c0, c1, ...]``.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from core.domain.promoted.analytic_geometry_circles.circle_geometry import (
    G, Radical, circle_from_general, dist2, exact_sqrt_fraction, fr, frac_latex, frac_text, general_latex,
    general_text, pt, radical_of_fraction, std_latex, std_text,
)

Circle = tuple[Fraction, Fraction, Fraction]
Poly = list[Fraction]

__all__ = [
    "G", "Radical", "fr", "frac_latex", "frac_text", "pt", "dist2", "exact_sqrt_fraction", "radical_of_fraction",
    "general_latex", "general_text", "std_latex", "std_text", "Circle", "Poly",
    "circle_of", "line_of", "side", "normal2", "relation", "intersections", "tangent_at", "tangents_from",
    "tangents_with_normal", "chord_length", "radical_text", "radical_sum",
    "poly", "padd", "psub", "pmul", "pscale", "peval", "pdeg", "rational_roots", "solve_region", "region_text", "region_latex",
]


# --- circles and lines -----------------------------------------------------------------------------------

def circle_of(spec: dict[str, Any]) -> Circle:
    """Standard ``{center, r2}`` or general ``{a?, d, e, f}`` givens (numbers only) -> ``(h, k, r2)``."""
    if "d" in spec:
        circle = circle_from_general(spec["d"], spec["e"], spec["f"], spec.get("a", 1))
    else:
        circle = (fr(spec["center"][0]), fr(spec["center"][1]), fr(spec["r2"]))
    if circle[2] <= 0:
        raise ValueError("not_a_real_circle")
    return circle


def line_of(spec: Any) -> G.Line:
    if isinstance(spec, dict):
        return G.norm_line(spec["a"], spec["b"], spec["c"])
    return G.norm_line(*spec)


def side(circle: Circle, line: G.Line) -> Fraction:
    h, k, _ = circle
    a, b, c = line
    return a * h + b * k + c


def normal2(line: G.Line) -> int:
    return line[0] ** 2 + line[1] ** 2


def relation(circle: Circle, line: G.Line) -> str:
    """``secant`` / ``tangent`` / ``disjoint`` by comparing distance^2 with r^2 (exact, no square roots)."""
    lhs, rhs = side(circle, line) ** 2, circle[2] * normal2(line)
    return "secant" if lhs < rhs else ("tangent" if lhs == rhs else "disjoint")


def _foot(circle: Circle, line: G.Line) -> tuple[Fraction, Fraction]:
    h, k, _ = circle
    a, b, _c = line
    t = side(circle, line) / normal2(line)
    return (h - a * t, k - b * t)


def intersections(circle: Circle, line: G.Line) -> list[tuple[Fraction, Fraction]]:
    """Common points sorted by (x, y); raises when they are not rational."""
    rel = relation(circle, line)
    if rel == "disjoint":
        return []
    fx, fy = _foot(circle, line)
    if rel == "tangent":
        return [(fx, fy)]
    a, b, _ = line
    n = normal2(line)
    half2 = circle[2] - side(circle, line) ** 2 / n  # (half chord)^2
    t = exact_sqrt_fraction(half2 / n)
    if t is None:
        raise ValueError("rational_intersections_required")
    return sorted([(fx - b * t, fy + a * t), (fx + b * t, fy - a * t)])


def tangent_at(circle: Circle, p: Any) -> G.Line:
    h, k, r2 = circle
    p = pt(p)
    if dist2((h, k), p) != r2:
        raise ValueError("point_not_on_circle")
    u, v = p[0] - h, p[1] - k
    return G.norm_line(u, v, -(u * p[0] + v * p[1]))


def _line_order(line: G.Line) -> tuple:
    slope = G.line_slope(line)
    return (0, Fraction(0), line) if slope is None else (1, slope, line)


def tangents_from(circle: Circle, p: Any) -> list[G.Line]:
    """Both tangents from an exterior point (vertical first, then by slope); rational slopes required."""
    h, k, r2 = circle
    p = pt(p)
    if dist2((h, k), p) <= r2:
        raise ValueError("point_not_outside_circle")
    dx, dy = h - p[0], k - p[1]
    lines: list[G.Line] = []
    if dx * dx == r2:
        lines.append(G.vertical_line(p[0]))
    # slope m: (dx^2 - r2) m^2 - 2 dx dy m + (dy^2 - r2) = 0
    qa, qb, qc = dx * dx - r2, -2 * dx * dy, dy * dy - r2
    if qa == 0:
        slopes = [-qc / qb]
    else:
        root = exact_sqrt_fraction(qb * qb - 4 * qa * qc)
        if root is None:
            raise ValueError("rational_tangent_slopes_required")
        slopes = [(-qb - root) / (2 * qa), (-qb + root) / (2 * qa)]
    lines += [G.line_from_point_slope(p, m) for m in slopes]
    if len(set(lines)) != 2:
        raise ValueError("two_tangents_expected")
    return sorted(lines, key=_line_order)


def tangents_with_normal(circle: Circle, a: Any, b: Any) -> list[G.Line]:
    """The two tangents ``a x + b y + c = 0`` with a fixed normal direction; rational constants required."""
    h, k, r2 = circle
    a, b = fr(a), fr(b)
    if a == 0 and b == 0:
        raise ValueError("degenerate_direction")
    root = exact_sqrt_fraction(r2 * (a * a + b * b))
    if root is None:
        raise ValueError("rational_tangent_constant_required")
    base = -(a * h + b * k)
    return sorted({G.norm_line(a, b, base + root), G.norm_line(a, b, base - root)}, key=lambda ln: ln[2])


def chord_length(circle: Circle, line: G.Line) -> Radical:
    if relation(circle, line) != "secant":
        raise ValueError("line_must_cut_the_circle")
    return radical_of_fraction(4 * (circle[2] - side(circle, line) ** 2 / normal2(line)))


# --- radicals ---------------------------------------------------------------------------------------------

def radical_text(r: Radical) -> str:
    return r.canonical()


def radical_sum(x: Radical, y: Radical, sign: int) -> dict[str, str]:
    """``x + y`` (sign=1) or ``x - y`` (sign=-1) as checker text and LaTeX; like radicals are combined."""
    if x.radicand == y.radicand:
        z = Radical(x.coef + sign * y.coef, x.radicand)
        return {"canonical": z.canonical(), "latex": z.latex()}
    if y.coef < 0:
        y, sign = Radical(-y.coef, y.radicand), -sign
    op = "+" if sign > 0 else "-"
    return {"canonical": f"{x.canonical()}{op}{y.canonical()}", "latex": f"{x.latex()}{op}{y.latex()}"}


# --- one-parameter polynomials ----------------------------------------------------------------------------

def poly(value: Any) -> Poly:
    """A number -> constant polynomial; ``[c0, c1, ...]`` -> c0 + c1 t + ..."""
    if isinstance(value, (list, tuple)):
        out = [fr(v) for v in value]
    else:
        out = [fr(value)]
    return _trim(out)


def _trim(p: Poly) -> Poly:
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p or [Fraction(0)]


def padd(p: Poly, q: Poly) -> Poly:
    n = max(len(p), len(q))
    return _trim([(p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0) for i in range(n)])


def pscale(p: Poly, c: Any) -> Poly:
    return _trim([fr(c) * v for v in p])


def psub(p: Poly, q: Poly) -> Poly:
    return padd(p, pscale(q, -1))


def pmul(p: Poly, q: Poly) -> Poly:
    out = [Fraction(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return _trim(out)


def peval(p: Poly, t: Fraction) -> Fraction:
    total = Fraction(0)
    for c in reversed(p):
        total = total * t + c
    return total


def pdeg(p: Poly) -> int:
    return -1 if p == [0] else len(p) - 1


def rational_roots(p: Poly) -> list[Fraction]:
    """Real roots of a polynomial of degree <= 2; raises when a real root is irrational."""
    deg = pdeg(p)
    if deg < 0:
        raise ValueError("identically_zero_condition")
    if deg == 0:
        return []
    if deg == 1:
        return [-p[0] / p[1]]
    if deg > 2:
        raise ValueError("condition_degree_above_two")
    c, b, a = p
    disc = b * b - 4 * a * c
    if disc < 0:
        return []
    root = exact_sqrt_fraction(disc)
    if root is None:
        raise ValueError("irrational_parameter_boundary")
    return sorted({(-b - root) / (2 * a), (-b + root) / (2 * a)})


def solve_region(test, critical: list[Fraction]) -> list[tuple[Fraction | None, Fraction | None, bool, bool]]:
    """Exact solution set of ``test(t)`` whose truth can only change at ``critical`` points.

    Returns maximal intervals ``(lo, hi, lo_closed, hi_closed)``; ``None`` is an infinite end.
    """
    cs = sorted(set(critical))
    pieces: list[tuple[str, Fraction | None, Fraction | None, bool]] = []
    if not cs:
        pieces.append(("open", None, None, test(Fraction(0))))
    else:
        pieces.append(("open", None, cs[0], test(cs[0] - 1)))
        for i, c in enumerate(cs):
            pieces.append(("point", c, c, test(c)))
            hi = cs[i + 1] if i + 1 < len(cs) else None
            probe = (c + hi) / 2 if hi is not None else c + 1
            pieces.append(("open", c, hi, test(probe)))
    out: list[list] = []
    for kind, lo, hi, ok in pieces:
        if not ok:
            continue
        if kind == "point":
            if out and out[-1][1] == lo and not out[-1][3]:
                out[-1][3] = True
            else:
                out.append([lo, hi, True, True])
        else:
            if out and out[-1][1] == lo and out[-1][3] and lo is not None:
                out[-1][1] = hi
                out[-1][3] = False
            else:
                out.append([lo, hi, False, False])
    return [tuple(seg) for seg in out]  # type: ignore[misc]


def _interval_text(seg, var: str, latex: bool) -> str:
    lo, hi, lc, hc = seg
    fmt = frac_latex if latex else frac_text
    le, ge = ("\\le ", "\\ge ") if latex else ("<=", ">=")
    if lo is None and hi is None:
        raise ValueError("unbounded_solution_set")
    if lo is not None and hi is not None and lo == hi:
        return f"{var}={fmt(lo)}"
    if lo is None:
        return f"{var}{le if hc else '<'}{fmt(hi)}"
    if hi is None:
        return f"{var}{ge if lc else '>'}{fmt(lo)}"
    return f"{fmt(lo)}{le if lc else '<'}{var}{le if hc else '<'}{fmt(hi)}"


def region_text(region, var: str) -> str:
    if not region:
        raise ValueError("empty_solution_set")
    return " or ".join(_interval_text(seg, var, False) for seg in region)


def region_latex(region, var: str) -> str:
    if not region:
        raise ValueError("empty_solution_set")
    return "\\text{ 或 }".join(_interval_text(seg, var, True) for seg in region)
