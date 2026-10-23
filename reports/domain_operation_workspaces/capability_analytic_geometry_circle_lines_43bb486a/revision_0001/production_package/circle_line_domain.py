"""Exact domain operations for general-high Mathematics 1, Unit 7 (圓與直線的關係).

Domain key ``analytic_geometry.circle_line_relations``.  Every operation is one shared, source-agnostic
implementation: components pass *inputs only* (``constraints``); this module computes the canonical
answer with exact ``Fraction`` arithmetic (centre-to-line distance against the radius) and a validator
re-derives it by an independent method (sympy substitution of the line into the circle and the
discriminant / explicit common points), never by calling the same construction code again.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable

import sympy as sp

from .circle_line_geometry import (
    G, Radical, chord_length, circle_of, dist2, exact_sqrt_fraction, fr, frac_latex, frac_text, intersections,
    line_of, normal2, padd, pdeg, peval, pmul, poly, psub, pscale, pt, radical_of_fraction, radical_sum,
    rational_roots, region_latex, region_text, relation, side, solve_region, std_latex, std_text, tangent_at,
    tangents_from, tangents_with_normal,
)

DOMAIN_KEY = "analytic_geometry.circle_line_relations"
X, Y, T = sp.symbols("x y t", real=True)

RELATION_KINDS = ("secant", "tangent", "disjoint")
CONDITIONS = ("tangent", "secant", "disjoint", "intersect", "chord", "quarter_arcs")


# --- shared helpers ----------------------------------------------------------------------------------------

def _require(constraints: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in constraints]
    if missing:
        raise ValueError(f"givens_required:{','.join(missing)}")


def _sr(value: Any) -> sp.Rational:
    value = fr(value)
    return sp.Rational(value.numerator, value.denominator)


def _sp_rat(text: Any) -> sp.Rational:
    return sp.Rational(str(text))


def _point_rec(p: Any) -> dict[str, Any]:
    p = pt(p)
    return {"kind": "point", "point": [frac_text(p[0]), frac_text(p[1])], "text": G.point_text(p)}


def _line_rec(line: G.Line) -> dict[str, Any]:
    return {"kind": "line", "line": list(line), "text": G.line_text(line)}


def _lines_rec(lines: list[G.Line]) -> dict[str, Any]:
    return {"kind": "lines", "lines": [list(ln) for ln in lines], "text": ", ".join(G.line_text(ln) for ln in lines)}


def _rational_rec(value: Fraction) -> dict[str, Any]:
    return {"kind": "rational", "canonical": frac_text(value)}


def _radical_rec(value: Radical) -> dict[str, Any]:
    # Lengths keep one contract whether or not this variant happens to be rational, so the field never hints at it.
    return {"kind": "radical", "canonical": value.canonical(), "latex": value.latex()}


def _sum_rec(text: dict[str, str]) -> dict[str, Any]:
    return {"kind": "radical", "canonical": text["canonical"], "latex": text["latex"]}


def _choice_rec(value: str) -> dict[str, Any]:
    return {"kind": "choice", "value": value}


def _set_rec(values: list[Fraction]) -> dict[str, Any]:
    return {"kind": "set", "values": [frac_text(v) for v in values]}


def _equation_rec(h: Fraction, k: Fraction, r2: Fraction) -> dict[str, Any]:
    return {"kind": "equation", "text": std_text(h, k, r2), "latex": std_latex(h, k, r2)}


def _region_rec(region, var: str) -> dict[str, Any]:
    segments = [[None if lo is None else frac_text(lo), None if hi is None else frac_text(hi), lc, hc] for lo, hi, lc, hc in region]
    return {"kind": "region", "text": region_text(region, var), "latex": region_latex(region, var), "segments": segments}


def _sp_circle(spec: dict[str, Any]) -> tuple[Any, Any, Any]:
    """(h, k, r2) as sympy expressions; general-form coefficients may be ``[c0, c1]`` polynomials in ``T``."""
    def val(v: Any) -> Any:
        if isinstance(v, (list, tuple)):
            return sum((_sr(c) * T**i for i, c in enumerate(v)), sp.Integer(0))
        return _sr(v)

    if "d" in spec:
        a = val(spec.get("a", 1))
        d, e, f = val(spec["d"]) / a, val(spec["e"]) / a, val(spec["f"]) / a
        h, k = -d / 2, -e / 2
        return (sp.expand(h), sp.expand(k), sp.expand(h * h + k * k - f))
    return (val(spec["center"][0]), val(spec["center"][1]), val(spec["r2"]))


def _sp_line(spec: Any) -> tuple[Any, Any, Any]:
    def val(v: Any) -> Any:
        if isinstance(v, (list, tuple)):
            return sum((_sr(c) * T**i for i, c in enumerate(v)), sp.Integer(0))
        return _sr(v)

    if isinstance(spec, dict):
        return (val(spec["a"]), val(spec["b"]), val(spec["c"]))
    return tuple(val(v) for v in spec)  # type: ignore[return-value]


def _sp_common_points(circle: tuple, line: tuple) -> list[tuple[Any, Any]]:
    """Real common points by substituting the line into ``(x-h)^2+(y-k)^2=r2`` (no distance formula)."""
    h, k, r2 = circle
    a, b, c = line
    eq = (X - h) ** 2 + (Y - k) ** 2 - r2
    if b != 0:
        y_expr = -(a * X + c) / b
        xs = sp.solve(sp.expand(eq.subs(Y, y_expr)), X)
        pts = {(sp.nsimplify(x0), sp.simplify(y_expr.subs(X, x0))) for x0 in xs if x0.is_real}
    else:
        x0 = -c / a
        ys = sp.solve(sp.expand(eq.subs(X, x0)), Y)
        pts = {(x0, sp.nsimplify(y0)) for y0 in ys if y0.is_real}
    return sorted(pts, key=lambda p: (float(p[0]), float(p[1])))


def _sp_relation(circle: tuple, line: tuple) -> str:
    """Relation from the discriminant of the substituted quadratic."""
    h, k, r2 = circle
    a, b, c = line
    eq = (X - h) ** 2 + (Y - k) ** 2 - r2
    if b != 0:
        quad = sp.Poly(sp.expand(eq.subs(Y, -(a * X + c) / b) * b * b), X)
    else:
        quad = sp.Poly(sp.expand(eq.subs(X, -c / a)), Y)
    qa, qb, qc = (quad.coeff_monomial(quad.gens[0] ** i) for i in (2, 1, 0))
    disc = sp.simplify(qb**2 - 4 * qa * qc)
    return "secant" if disc > 0 else ("tangent" if disc == 0 else "disjoint")


def _same_line(rec_line: list[Any], line: tuple) -> bool:
    a1, b1, c1 = (_sr(v) for v in rec_line)
    a2, b2, c2 = (sp.nsimplify(v) for v in line)
    return sp.simplify(a1 * b2 - a2 * b1) == 0 and sp.simplify(a1 * c2 - a2 * c1) == 0 and sp.simplify(b1 * c2 - b2 * c1) == 0


def _sp_tangent(circle: tuple, rec_line: list[Any]) -> bool:
    return _sp_relation(circle, tuple(_sr(v) for v in rec_line)) == "tangent"


# --- 1. classify_circle_line_relations ---------------------------------------------------------------------

def classify_circle_line_relations(circle: dict[str, Any], lines: list[Any], ask_points: bool = False, **text: Any) -> dict[str, Any]:
    c = circle_of(circle)
    out = []
    for spec in lines:
        line = line_of(spec)
        rel = relation(c, line)
        item: dict[str, Any] = {"relation": rel, "side": frac_text(abs(side(c, line))), "normal2": normal2(line)}
        if ask_points:
            item["points"] = [_point_rec(p) for p in intersections(c, line)]
        out.append(item)
    if len(lines) > 1 and len({item["relation"] for item in out}) < 2:
        raise ValueError("lines_should_not_all_have_the_same_relation")
    return {"lines": out, "r2": frac_text(c[2])}


def _check_classify_circle_line_relations(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    circle = _sp_circle(givens["circle"])
    if not circle[2] > 0 or len(answer["lines"]) != len(givens["lines"]):
        return False
    for spec, item in zip(givens["lines"], answer["lines"]):
        line = _sp_line(spec)
        common = _sp_common_points(circle, line)
        expected = {2: "secant", 1: "tangent", 0: "disjoint"}[len(common)]
        if item["relation"] != expected:
            return False
        if givens.get("ask_points"):
            got = [(_sp_rat(p["point"][0]), _sp_rat(p["point"][1])) for p in item["points"]]
            if got != [(sp.Rational(x0), sp.Rational(y0)) for x0, y0 in common]:
                return False
    return True


# --- 2. solve_circle_line_parameter ------------------------------------------------------------------------

def _param_circle(spec: dict[str, Any]) -> tuple[list, list, list]:
    """(h, k, r2) as polynomials in the parameter."""
    if "d" in spec:
        a = poly(spec.get("a", 1))
        if pdeg(a) != 0:
            raise ValueError("leading_coefficient_must_be_constant")
        inv = 1 / a[0]
        h = pscale(poly(spec["d"]), -inv / 2)
        k = pscale(poly(spec["e"]), -inv / 2)
        r2 = psub(padd(pmul(h, h), pmul(k, k)), pscale(poly(spec["f"]), inv))
        return h, k, r2
    return poly(spec["center"][0]), poly(spec["center"][1]), poly(spec["r2"])


def _condition_poly(h, k, r2, a, b, c, condition: str, chord: Any) -> list:
    s = padd(padd(pmul(a, h), pmul(b, k)), c)  # signed numerator of the centre-to-line distance
    n = padd(pmul(a, a), pmul(b, b))
    s2, rn = pmul(s, s), pmul(r2, n)
    if condition == "chord":
        length = fr(chord)
        if length <= 0:
            raise ValueError("positive_chord_required")
        # (L/2)^2 = r^2 - d^2  <=>  4 (r2 n - s^2) - L^2 n = 0
        return psub(pscale(psub(rn, s2), 4), pscale(n, length * length))
    if condition == "quarter_arcs":
        return psub(pscale(s2, 2), rn)  # chord subtends a right angle: d^2 = r^2 / 2
    return psub(s2, rn)  # sign: < 0 secant, = 0 tangent, > 0 disjoint


_INEQUALITY = {
    "secant": lambda v: v < 0,
    "disjoint": lambda v: v > 0,
    "intersect": lambda v: v <= 0,
}


def solve_circle_line_parameter(circle: dict[str, Any], line: dict[str, Any], asks: list[dict[str, Any]], param: str = "k", **text: Any) -> dict[str, Any]:
    h, k, r2 = _param_circle(circle)
    a, b, c = poly(line["a"]), poly(line["b"]), poly(line["c"])
    n = padd(pmul(a, a), pmul(b, b))

    def valid(t: Fraction) -> bool:
        return peval(r2, t) > 0 and peval(n, t) > 0

    values: list[dict[str, Any]] = []
    for ask in asks:
        condition, output = ask["condition"], ask["output"]
        if condition not in CONDITIONS:
            raise ValueError(f"unknown_condition:{condition}")
        cond = _condition_poly(h, k, r2, a, b, c, condition, ask.get("chord"))
        if output == "region":
            if condition not in _INEQUALITY:
                raise ValueError("region_needs_an_inequality_condition")
            critical = rational_roots(cond) + (rational_roots(r2) if pdeg(r2) > 0 else []) + (rational_roots(n) if pdeg(n) > 0 else [])
            test = _INEQUALITY[condition]
            region = solve_region(lambda t: valid(t) and test(peval(cond, t)), critical)
            values.append(_region_rec(region, param))
            continue
        if condition in _INEQUALITY:
            raise ValueError("equality_output_needs_an_equality_condition")
        roots = [t for t in rational_roots(cond) if valid(t)]
        if not roots:
            raise ValueError("no_admissible_parameter_value")
        if output == "set":
            values.append(_set_rec(roots))
        elif output == "ordered":  # two values named by ``names`` (largest first)
            if len(roots) != 2:
                raise ValueError("two_parameter_values_required")
            values.append({"kind": "ordered", "values": [frac_text(v) for v in sorted(roots, reverse=True)]})
        elif output == "lines":
            values.append(_lines_rec([G.norm_line(peval(a, t), peval(b, t), peval(c, t)) for t in roots]))
        else:
            raise ValueError(f"unknown_output:{output}")
    return {"values": values, "param": param}


def _sp_admissible(circle: tuple, line: tuple, t0: Any) -> bool:
    h, k, r2 = (sp.sympify(v).subs(T, t0) for v in circle)
    a, b, _c = (sp.sympify(v).subs(T, t0) for v in line)
    return bool(r2 > 0 and (a != 0 or b != 0))


def _sp_holds(circle: tuple, line: tuple, t0: Any, condition: str, chord: Any) -> bool:
    """Condition at a concrete parameter value, from the explicit common points of the substituted system."""
    if not _sp_admissible(circle, line, t0):
        return False
    c0 = tuple(sp.sympify(v).subs(T, t0) for v in circle)
    l0 = tuple(sp.sympify(v).subs(T, t0) for v in line)
    common = _sp_common_points(c0, l0)
    if condition == "tangent":
        return len(common) == 1
    if condition == "secant":
        return len(common) == 2
    if condition == "disjoint":
        return len(common) == 0
    if condition == "intersect":
        return len(common) >= 1
    if len(common) != 2:
        return False
    (x1, y1), (x2, y2) = common
    if condition == "chord":
        return sp.simplify((x1 - x2) ** 2 + (y1 - y2) ** 2 - _sr(chord) ** 2) == 0
    h, k, _ = c0  # quarter arcs: the chord subtends a right angle at the centre
    return sp.simplify((x1 - h) * (x2 - h) + (y1 - k) * (y2 - k)) == 0


def _sp_candidates(circle: tuple, line: tuple, condition: str, chord: Any) -> list:
    """All parameter values where the substituted discriminant / chord / right-angle condition is exact."""
    h, k, r2 = circle
    a, b, c = line
    eq = (X - h) ** 2 + (Y - k) ** 2 - r2
    if not b.has(T) and b != 0:
        quad = sp.Poly(sp.expand(eq.subs(Y, -(a * X + c) / b) * b * b), X)
    elif not a.has(T) and a != 0:
        quad = sp.Poly(sp.expand(eq.subs(X, -(b * Y + c) / a) * a * a), Y)
    else:
        raise ValueError("validator_needs_a_constant_line_coefficient")
    qa, qb, qc = (quad.coeff_monomial(quad.gens[0] ** i) for i in (2, 1, 0))
    disc = sp.expand(qb**2 - 4 * qa * qc)
    if condition == "tangent":
        target = disc
    elif condition == "chord":
        # |x1-x2|^2 = disc/qa^2 and chord^2 = disc (a^2+b^2) / (qa^2 lead^2)
        lead = b if (not b.has(T) and b != 0) else a
        target = sp.expand(disc * (a * a + b * b) - _sr(chord) ** 2 * qa**2 * lead**2)
    else:  # quarter arcs: the chord of a right central angle has length^2 = 2 r^2
        lead = b if (not b.has(T) and b != 0) else a
        target = sp.expand(disc * (a * a + b * b) - 2 * r2 * qa**2 * lead**2)
    sols = sp.solve(target, T)
    return [s for s in sols if s.is_real]


def _region_set(segments: list) -> Any:
    out = sp.EmptySet
    for lo, hi, lc, hc in segments:
        left = -sp.oo if lo is None else _sp_rat(lo)
        right = sp.oo if hi is None else _sp_rat(hi)
        out = sp.Union(out, sp.Interval(left, right, left_open=not lc, right_open=not hc))
    return out


def _sp_region(circle: tuple, line: tuple, condition: str) -> Any:
    h, k, r2 = circle
    a, b, c = line
    eq = (X - h) ** 2 + (Y - k) ** 2 - r2
    if not b.has(T) and b != 0:
        quad = sp.Poly(sp.expand(eq.subs(Y, -(a * X + c) / b) * b * b), X)
    elif not a.has(T) and a != 0:
        quad = sp.Poly(sp.expand(eq.subs(X, -(b * Y + c) / a) * a * a), Y)
    else:
        raise ValueError("validator_needs_a_constant_line_coefficient")
    qa, qb, qc = (quad.coeff_monomial(quad.gens[0] ** i) for i in (2, 1, 0))
    disc = sp.expand(qb**2 - 4 * qa * qc)
    rel = {"secant": disc > 0, "disjoint": disc < 0, "intersect": disc >= 0}[condition]
    found = sp.solveset(rel, T, sp.S.Reals)
    real_circle = sp.solveset(sp.expand(r2) > 0, T, sp.S.Reals)
    return sp.Intersection(found, real_circle)


def _check_solve_circle_line_parameter(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    circle, line = _sp_circle(givens["circle"]), _sp_line(givens["line"])
    if len(answer["values"]) != len(givens["asks"]):
        return False
    for ask, rec in zip(givens["asks"], answer["values"]):
        condition = ask["condition"]
        if ask["output"] == "region":
            if _region_set(rec["segments"]) != _sp_region(circle, line, condition):
                return False
            continue
        expected = sorted({sp.nsimplify(s) for s in _sp_candidates(circle, line, condition, ask.get("chord"))
                           if _sp_holds(circle, line, s, condition, ask.get("chord"))})
        if rec["kind"] == "set":
            if sorted(_sp_rat(v) for v in rec["values"]) != expected:
                return False
        elif rec["kind"] == "ordered":
            if [_sp_rat(v) for v in rec["values"]] != sorted(expected, reverse=True):
                return False
        elif rec["kind"] == "lines":
            if len(rec["lines"]) != len(expected):
                return False
            for t0 in expected:
                target = tuple(sp.sympify(v).subs(T, t0) for v in line)
                if not any(_same_line(got, target) for got in rec["lines"]):
                    return False
        else:
            return False
    return True


# --- 3. write_circle_tangent_lines -------------------------------------------------------------------------

def write_circle_tangent_lines(circle: dict[str, Any], kind: str, point: Any = None, slope: Any = None,
                               parallel_to: Any = None, **text: Any) -> dict[str, Any]:
    c = circle_of(circle)
    if kind == "through_point":
        p = pt(point)
        position = "on" if dist2((c[0], c[1]), p) == c[2] else ("outside" if dist2((c[0], c[1]), p) > c[2] else "inside")
        if position == "inside":
            raise ValueError("no_tangent_through_an_interior_point")
        lines = [tangent_at(c, p)] if position == "on" else tangents_from(c, p)
        return {"values": [_lines_rec(lines)], "position": position, "count": len(lines)}
    if kind == "with_slope":
        m = fr(slope)
        lines = tangents_with_normal(c, m, -1)
        return {"values": [_lines_rec(lines)], "count": 2}
    if kind == "parallel_to":
        ref = line_of(parallel_to)
        if relation(c, ref) == "tangent":
            raise ValueError("reference_line_is_itself_a_tangent")
        lines = tangents_with_normal(c, ref[0], ref[1])
        return {"values": [_lines_rec(lines)], "count": 2}
    raise ValueError(f"unknown_tangent_kind:{kind}")


def _check_write_circle_tangent_lines(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    circle = _sp_circle(givens["circle"])
    h, k, r2 = circle
    got = answer["values"][0]["lines"]
    if not all(_sp_tangent(circle, ln) for ln in got):
        return False
    m = sp.Symbol("m", real=True)
    kind = givens["kind"]
    if kind == "through_point":
        px, py = (_sr(v) for v in givens["point"])
        # every non-vertical line through P: m x - y + (py - m px) = 0; tangent <=> substituted discriminant = 0
        slope_lines = [(s, -1, py - s * px) for s in sp.solve(_sp_disc_expr(circle, m, py - m * px), m) if s.is_real]
        expected = slope_lines + ([(1, 0, -px)] if _sp_relation(circle, (1, 0, -px)) == "tangent" else [])
    elif kind == "with_slope":
        s = _sr(givens["slope"])
        cc = sp.Symbol("c", real=True)
        expected = [(s, -1, c0) for c0 in sp.solve(_sp_disc_expr(circle, s, cc), cc) if c0.is_real]
    else:
        a, b, _c = (_sr(v) for v in givens["parallel_to"])
        cc = sp.Symbol("c", real=True)
        if b != 0:
            expected = [(a, b, c0) for c0 in sp.solve(_sp_disc_expr(circle, -a / b, -cc / b), cc) if c0.is_real]
        else:
            expected = [(1, 0, -x0) for x0 in (h - sp.sqrt(r2), h + sp.sqrt(r2))]
    if len(expected) != len(got):
        return False
    return all(any(_same_line(g, tuple(sp.nsimplify(v) for v in e)) for g in got) for e in expected)


def _sp_disc_expr(circle: tuple, m: Any, q: Any) -> Any:
    """Discriminant of (x-h)^2+(m x+q-k)^2=r2 (the line y = m x + q substituted into the circle)."""
    h, k, r2 = circle
    quad = sp.expand((X - h) ** 2 + (m * X + q - k) ** 2 - r2)
    qa, qb, qc = (quad.coeff(X, i) for i in (2, 1, 0))
    return sp.expand(qb**2 - 4 * qa * qc)


# --- 4. solve_chord_and_distance ---------------------------------------------------------------------------

def solve_chord_and_distance(circle: dict[str, Any], asks: list[str], line: Any = None, point: Any = None, **text: Any) -> dict[str, Any]:
    c = circle_of(circle)
    values: list[dict[str, Any]] = []
    extra: dict[str, Any] = {}
    for ask in asks:
        if ask == "chord":
            values.append(_radical_rec(chord_length(c, line_of(line))))
        elif ask in ("max_distance", "min_distance"):
            ln = line_of(line)
            if relation(c, ln) != "disjoint":
                raise ValueError("line_must_miss_the_circle")
            d = G.radical_of_ratio(abs(side(c, ln)), normal2(ln))
            r = radical_of_fraction(c[2])
            values.append(_sum_rec(radical_sum(d, r, 1 if ask == "max_distance" else -1)))
            extra.update({"distance": d.canonical(), "distance_latex": d.latex(), "radius_latex": r.latex()})
        elif ask in ("shortest_chord", "shortest_chord_line"):
            p = pt(point)
            md2 = dist2((c[0], c[1]), p)
            if md2 == 0 or md2 >= c[2]:
                raise ValueError("point_must_be_interior_and_not_the_centre")
            if ask == "shortest_chord":
                values.append(_radical_rec(radical_of_fraction(4 * (c[2] - md2))))
            else:
                u, v = p[0] - c[0], p[1] - c[1]
                values.append(_line_rec(G.norm_line(u, v, -(u * p[0] + v * p[1]))))
            extra["mp2"] = frac_text(md2)
        else:
            raise ValueError(f"unknown_ask:{ask}")
    return {"values": values, **extra}


def _sp_value(rec: dict[str, Any]) -> Any:
    return sp.sympify(rec["canonical"])


def _sp_equation(text: str) -> Any:
    left, right = text.replace("^", "**").split("=")
    names = {"x": X, "y": Y}
    return sp.sympify(left, locals=names) - sp.sympify(right, locals=names)


def _check_solve_chord_and_distance(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    circle = _sp_circle(givens["circle"])
    h, k, r2 = circle
    for ask, rec in zip(givens["asks"], answer["values"]):
        if ask == "chord":
            (x1, y1), (x2, y2) = _sp_common_points(circle, _sp_line(givens["line"]))
            if sp.simplify(sp.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) - _sp_value(rec)) != 0:
                return False
        elif ask in ("max_distance", "min_distance"):
            a, b, c = _sp_line(givens["line"])
            n = sp.sqrt(a * a + b * b)
            # extreme points of the circle in the normal direction (support points), distance by formula
            ends = [(h + s * sp.sqrt(r2) * a / n, k + s * sp.sqrt(r2) * b / n) for s in (1, -1)]
            dist = [sp.Abs(a * x0 + b * y0 + c) / n for x0, y0 in ends]
            if _sp_relation(circle, (a, b, c)) != "disjoint":
                return False
            target = sp.Max(*dist) if ask == "max_distance" else sp.Min(*dist)
            if sp.simplify(target - _sp_value(rec)) != 0:
                return False
        elif ask == "shortest_chord":
            px, py = (_sr(v) for v in givens["point"])
            # chord through P with direction perpendicular to MP; endpoints from the substituted system
            line = (px - h, py - k, -((px - h) * px + (py - k) * py))
            (x1, y1), (x2, y2) = _sp_common_points(circle, line)
            if sp.simplify(sp.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) - _sp_value(rec)) != 0:
                return False
            # any other chord through P is longer: a chord along MP is a diameter-direction chord
            mp_line = (py - k, h - px, px * k - py * h) if (px, py) != (h, k) else None
            if mp_line is not None:
                (u1, v1), (u2, v2) = _sp_common_points(circle, mp_line)
                if not (u1 - u2) ** 2 + (v1 - v2) ** 2 > (x1 - x2) ** 2 + (y1 - y2) ** 2:
                    return False
        elif ask == "shortest_chord_line":
            px, py = (_sr(v) for v in givens["point"])
            a, b, c = (_sr(v) for v in rec["line"])
            if a * px + b * py + c != 0 or a * (py - k) - b * (px - h) != 0:  # through P, normal parallel to MP
                return False
        else:
            return False
    return True


# --- 5. solve_circle_from_tangent_point --------------------------------------------------------------------

def solve_circle_from_tangent_point(d: Any, point: Any, tangent: Any, **text: Any) -> dict[str, Any]:
    """Circle ``x^2+y^2+d x+E y+F=0`` (``d`` known) tangent to ``tangent`` at ``point``: find E and F."""
    d = fr(d)
    p = pt(point)
    a, b, c = line_of(tangent)
    if a * p[0] + b * p[1] + c != 0:
        raise ValueError("point_must_lie_on_the_tangent")
    if a == 0:
        raise ValueError("tangent_must_not_be_horizontal")
    h = -d / 2
    k = p[1] - (p[0] - h) * Fraction(b, a)  # centre on the normal through the point
    if (h, k) == p:
        raise ValueError("degenerate_circle")
    e = -2 * k
    f = -(p[0] ** 2 + p[1] ** 2 + d * p[0] + e * p[1])
    return {"values": [_rational_rec(e), _rational_rec(f)], "center": [frac_text(h), frac_text(k)],
            "r2": frac_text(dist2((h, k), p))}


def _check_solve_circle_from_tangent_point(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    e, f = sp.symbols("e f", real=True)
    d = _sr(givens["d"])
    px, py = (_sr(v) for v in givens["point"])
    a, b, c = _sp_line(givens["tangent"])
    on_circle = px**2 + py**2 + d * px + e * py + f
    # the gradient of the circle at P is normal to the tangent
    grad_parallel = (2 * px + d) * b - (2 * py + e) * a
    sols = sp.solve([on_circle, grad_parallel], [e, f], dict=True)
    if len(sols) != 1 or a * px + b * py + c != 0:
        return False
    got = [_sp_rat(r["canonical"]) for r in answer["values"]]
    return got == [sols[0][e], sols[0][f]]


# --- 6. evaluate_circle_line_statement_truth ---------------------------------------------------------------

def evaluate_circle_line_statement_truth(statement: dict[str, Any], **text: Any) -> dict[str, Any]:
    kind = statement["kind"]
    if kind == "line_through_point_on_circle_is_tangent":
        return {"truth": False}  # only the line perpendicular to the radius is a tangent
    if kind == "disjoint_distance_bound":
        r2, bound = fr(statement["r2"]), fr(statement["bound"])
        if r2 <= 0 or bound <= 0:
            raise ValueError("invalid_statement")
        return {"truth": bound * bound <= r2}  # disjoint means distance > r; "> bound" is guaranteed iff bound <= r
    if kind == "tangent_to_both_axes":
        h, k, r2 = circle_of(statement)
        return {"truth": h * h == r2 and k * k == r2, "x_axis": k * k == r2, "y_axis": h * h == r2}
    if kind == "tangent_slope_exists":
        fr(statement["slope"])
        return {"truth": True}  # the two lines with the given slope at distance r from the centre are tangents
    if kind == "two_tangents_through_point":
        c = circle_of(statement)
        d2 = dist2((c[0], c[1]), statement["point"])
        position = "outside" if d2 > c[2] else ("on" if d2 == c[2] else "inside")
        return {"truth": position == "outside", "position": position}
    raise ValueError(f"unknown_statement_kind:{kind}")


def _check_evaluate_circle_line_statement_truth(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    s, truth = givens["statement"], answer["truth"]
    kind = s["kind"]
    if kind == "line_through_point_on_circle_is_tangent":
        # counterexample: x^2+y^2=1 and the line through (1,0) and (0,1) cut the circle twice
        return truth is False and _sp_relation((0, 0, 1), (1, 1, -1)) == "secant"
    if kind == "disjoint_distance_bound":
        r = sp.sqrt(_sr(s["r2"]))
        possible = sp.Interval.open(r, sp.oo)  # distances of lines missing the circle
        return possible.is_subset(sp.Interval.open(_sr(s["bound"]), sp.oo)) == truth
    if kind == "tangent_to_both_axes":
        circle = _sp_circle(s)
        both = _sp_relation(circle, (0, 1, 0)) == "tangent" and _sp_relation(circle, (1, 0, 0)) == "tangent"
        return both == truth
    if kind == "tangent_slope_exists":
        h, k = sp.symbols("h k", real=True)
        r = sp.Symbol("r", positive=True)
        q = sp.Symbol("q", real=True)
        roots = sp.solve(_sp_disc_expr((h, k, r**2), _sr(s["slope"]), q), q)
        return (len(roots) == 2 and all(rt.is_real is not False for rt in roots)) == truth
    if kind == "two_tangents_through_point":
        circle = _sp_circle(s)
        px, py = (_sr(v) for v in s["point"])
        m = sp.Symbol("m", real=True)
        count = len([v for v in sp.solve(_sp_disc_expr(circle, m, py - m * px), m) if v.is_real])
        count += 1 if _sp_relation(circle, (1, 0, -px)) == "tangent" else 0
        return (count == 2) == truth
    return False


# --- 7. solve_circle_tangent_scenarios ---------------------------------------------------------------------

def _building(center_y: Any, point: Any) -> dict[str, Any]:
    k = fr(center_y)
    p = pt(point)
    if not (k > 0 and p[0] > 0 and p[1] > k):
        raise ValueError("viewpoint_must_be_on_the_upper_right_arc")
    r2 = p[0] ** 2 + (p[1] - k) ** 2
    if r2 <= k * k:
        raise ValueError("base_chord_must_exist")
    half = exact_sqrt_fraction(r2 - k * k)
    if half is None:
        raise ValueError("rational_base_required")
    tangent = tangent_at((Fraction(0), k, r2), p)
    q = G.intersect(tangent, G.horizontal_line(Fraction(0)))
    if q is None or q[0] <= half:
        raise ValueError("observer_must_stand_beyond_the_base")
    return {"r2": r2, "half": half, "tangent": tangent, "q": q, "slope": G.line_slope(tangent)}


def solve_circle_tangent_scenarios(scenario: str, **givens: Any) -> dict[str, Any]:
    if scenario == "building_view":
        b = _building(givens["center_y"], givens["point"])
        return {"values": [_rational_rec(b["slope"]), _line_rec(b["tangent"]), _point_rec(b["q"])],
                "r2": frac_text(b["r2"]), "half_base": frac_text(b["half"])}
    if scenario == "building_dimensions":
        b = _building(givens["center_y"], givens["point"])
        k = fr(givens["center_y"])
        return {"values": [_radical_rec(radical_of_fraction(b["r2"])), _equation_rec(Fraction(0), k, b["r2"]),
                           _rational_rec(2 * b["half"])], "r2": frac_text(b["r2"]), "q": [frac_text(v) for v in b["q"]]}
    if scenario == "light_shadow":
        c = circle_of(givens["circle"])
        light = pt(givens["light"])
        h, k, r2 = c
        if not (k > 0 and k * k > r2):
            raise ValueError("circle_must_float_above_the_x_axis")
        if not (light[1] > k and (light[1] - k) ** 2 > r2):
            raise ValueError("light_must_be_above_the_circle")
        lines = tangents_from(c, light)
        feet = [G.intersect(ln, G.horizontal_line(Fraction(0))) for ln in lines]
        if any(f is None for f in feet):
            raise ValueError("tangent_parallel_to_the_ground")
        xs = sorted(f[0] for f in feet)
        return {"values": [_rational_rec(xs[1] - xs[0])], "feet": [frac_text(x) for x in xs],
                "tangents": [list(ln) for ln in lines]}
    if scenario == "badge":
        w, r2, cy, od = fr(givens["width"]), fr(givens["r2"]), fr(givens["center_height"]), fr(givens["od"])
        c = (w / 2, cy, r2)
        if not (0 < od < w and r2 < (w / 2) ** 2 and cy > 0 and cy * cy > r2):
            raise ValueError("invalid_badge_layout")
        lines = tangents_from(c, (od, Fraction(0)))
        slopes = [G.line_slope(ln) for ln in lines]
        if None in slopes or not (min(slopes) < 0 < max(slopes)):
            raise ValueError("one_tangent_left_one_right_expected")
        left = lines[slopes.index(min(slopes))]
        right = lines[slopes.index(max(slopes))]
        top = G.intersect(left, G.vertical_line(Fraction(0)))[1]
        e_y = G.intersect(right, G.vertical_line(w))[1]
        if not (0 < e_y < top and cy + _sqrt_upper(r2) < top):
            raise ValueError("tangent_points_must_fit_the_badge")
        return {"values": [_rational_rec(e_y), _rational_rec(top)], "slopes": [frac_text(min(slopes)), frac_text(max(slopes))]}
    raise ValueError(f"unknown_scenario:{scenario}")


def _sqrt_upper(value: Fraction) -> Fraction:
    """sqrt(value) when rational, else a rational upper bound (used only for layout checks)."""
    root = exact_sqrt_fraction(value)
    if root is not None:
        return root
    return Fraction(int(float(value) ** 0.5 * 1000) + 1, 1000)


def _check_solve_circle_tangent_scenarios(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    scenario = givens["scenario"]
    vals = answer["values"]
    if scenario in ("building_view", "building_dimensions"):
        k = _sr(givens["center_y"])
        px, py = (_sr(v) for v in givens["point"])
        r2 = px**2 + (py - k) ** 2
        base = sorted(x0 for x0 in sp.solve(X**2 + (0 - k) ** 2 - r2, X) if x0.is_real)
        if len(base) != 2:
            return False
        # tangent at P is perpendicular to MP (dot product), Q is where it meets the x-axis
        q = sp.Symbol("q", real=True)
        (qx,) = sp.solve((q - px) * (px - 0) + (0 - py) * (py - k), q)
        if scenario == "building_view":
            slope = (0 - py) / (qx - px)
            line_ok = _same_line(vals[1]["line"], (py - 0, qx - px, px * 0 - qx * py))
            return bool(_sp_rat(vals[0]["canonical"]) == slope and line_ok
                        and (_sp_rat(vals[2]["point"][0]), _sp_rat(vals[2]["point"][1])) == (qx, 0))
        radius = _sp_value(vals[0])
        eq_ok = sp.simplify(_sp_equation(vals[1]["text"]) - (X**2 + (Y - k) ** 2 - r2)) == 0
        return bool(sp.simplify(radius**2 - r2) == 0 and radius > 0 and eq_ok
                    and _sp_rat(vals[2]["canonical"]) == base[1] - base[0])
    if scenario == "light_shadow":
        circle = _sp_circle(givens["circle"])
        lx, ly = (_sr(v) for v in givens["light"])
        m = sp.Symbol("m", real=True)
        slopes = [s for s in sp.solve(_sp_disc_expr(circle, m, ly - m * lx), m) if s.is_real]
        feet = [lx - ly / s for s in slopes]  # y = 0 on y - ly = s (x - lx)
        if _sp_relation(circle, (1, 0, -lx)) == "tangent":
            feet.append(lx)
        if len(feet) != 2:
            return False
        feet.sort()
        return _sp_rat(vals[0]["canonical"]) == feet[1] - feet[0]
    if scenario == "badge":
        w, r2, cy, od = (_sr(givens[k]) for k in ("width", "r2", "center_height", "od"))
        m = sp.Symbol("m", real=True)
        slopes = sorted(s for s in sp.solve(_sp_disc_expr((w / 2, cy, r2), m, -m * od), m) if s.is_real)
        if len(slopes) != 2:
            return False
        top = slopes[0] * (0 - od)
        e_y = slopes[1] * (w - od)
        return _sp_rat(vals[0]["canonical"]) == e_y and _sp_rat(vals[1]["canonical"]) == top
    return False


# --- operation table ---------------------------------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "classify_circle_line_relations": (classify_circle_line_relations, _check_classify_circle_line_relations, ("circle", "lines")),
    "solve_circle_line_parameter": (solve_circle_line_parameter, _check_solve_circle_line_parameter, ("circle", "line", "asks")),
    "write_circle_tangent_lines": (write_circle_tangent_lines, _check_write_circle_tangent_lines, ("circle", "kind")),
    "solve_chord_and_distance": (solve_chord_and_distance, _check_solve_chord_and_distance, ("circle", "asks")),
    "solve_circle_from_tangent_point": (solve_circle_from_tangent_point, _check_solve_circle_from_tangent_point, ("d", "point", "tangent")),
    "evaluate_circle_line_statement_truth": (evaluate_circle_line_statement_truth, _check_evaluate_circle_line_statement_truth, ("statement",)),
    "solve_circle_tangent_scenarios": (solve_circle_tangent_scenarios, _check_solve_circle_tangent_scenarios, ("scenario",)),
}
OPERATIONS = tuple(_OPERATIONS)


def build_circle_line_relations_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_circle_line_relations_operation:{operation}")
    solve, _check, required = _OPERATIONS[operation]
    givens = {k: v for k, v in (constraints or {}).items() if k not in ("skill_id",)}
    _require(givens, *required)
    answer = solve(**givens)
    return {
        "domain": DOMAIN_KEY,
        "domain_operation": operation,
        "givens": givens,
        "answer": answer,
        "validation_facts": {"domain_operation": operation, "seed": 0 if seed is None else int(seed)},
    }


# --- validators (never raise) ------------------------------------------------------------------------------

def _make_validator(operation: str) -> Callable[[Any], bool]:
    check = _OPERATIONS[operation][1]

    def validate(matrix: Any) -> bool:
        try:
            facts = matrix.get("validation_facts") or {}
            if (
                matrix.get("domain") != DOMAIN_KEY
                or matrix.get("domain_operation") != operation
                or facts.get("domain_operation") != operation
            ):
                return False
            return bool(check(matrix["givens"], matrix["answer"]))
        except Exception:
            return False

    validate.__name__ = f"validate_{operation}_matrix"
    return validate


for _op in _OPERATIONS:
    globals()[f"validate_{_op}_matrix"] = _make_validator(_op)
