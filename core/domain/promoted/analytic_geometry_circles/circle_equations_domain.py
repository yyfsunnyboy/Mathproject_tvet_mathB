"""Exact domain operations for general-high Mathematics 1, Unit 6 (圓方程式).

Domain key ``analytic_geometry.circle_equations``.  Every operation is one shared, source-agnostic
implementation: components pass *inputs only* (``constraints``); this module computes the canonical
answer with exact ``Fraction`` arithmetic and a validator re-derives / re-checks it by an independent
method (sympy substitution, polynomial identity and defining-property checks), never by calling the
same construction code again.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable

import sympy as sp

from math import gcd

from .circle_geometry import (
    G, Circle, Radical, circle_from_general, classify_r2, dist2, exact_sqrt_fraction, fr, frac_latex, frac_text, pt,
    radical_of_fraction, relation_to_circle, std_latex, std_text,
)

DOMAIN_KEY = "analytic_geometry.circle_equations"
X, Y = sp.symbols("x y")

GRAPH_KINDS = ("circle", "point", "none")
RELATION_KINDS = ("inside", "outside", "on")
SHAPE_KINDS = ("circle", "upper_semicircle", "lower_semicircle", "line")


# --- shared helpers ----------------------------------------------------------------------------------------

def _require(constraints: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in constraints]
    if missing:
        raise ValueError(f"givens_required:{','.join(missing)}")


def _sr(value: Any) -> sp.Rational:
    value = fr(value)
    return sp.Rational(value.numerator, value.denominator)


def _gen(spec: dict[str, Any]) -> Circle:
    """General-form givens ``{a?, d, e, f}`` -> circle triple (r2 may be <= 0)."""
    return circle_from_general(spec["d"], spec["e"], spec["f"], spec.get("a", 1))


def _std(spec: dict[str, Any]) -> Circle:
    return (fr(spec["center"][0]), fr(spec["center"][1]), fr(spec["r2"]))


def _circle_of(spec: dict[str, Any]) -> Circle:
    return _gen(spec) if "d" in spec else _std(spec)


def _equation_rec(circle: Circle) -> dict[str, Any]:
    h, k, r2 = circle
    return {"kind": "equation", "text": std_text(h, k, r2), "latex": std_latex(h, k, r2),
            "center": [frac_text(h), frac_text(k)], "r2": frac_text(r2)}


def _point_rec(p: Any) -> dict[str, Any]:
    p = pt(p)
    return {"kind": "point", "point": [frac_text(p[0]), frac_text(p[1])], "text": G.point_text(p)}


def _line_rec(line: G.Line) -> dict[str, Any]:
    return {"kind": "line", "line": list(line), "text": G.line_text(line)}


def _rational_rec(value: Fraction) -> dict[str, Any]:
    return {"kind": "rational", "canonical": frac_text(value)}


def _radical_rec(value: Radical) -> dict[str, Any]:
    return {
        "kind": "rational" if value.is_rational() else "radical",
        "canonical": value.canonical(),
        "latex": value.latex(),
        "coef": frac_text(value.coef),
        "radicand": value.radicand,
    }


def _radius_rec(r2: Fraction) -> dict[str, Any]:
    return _radical_rec(radical_of_fraction(r2))


def _choice_rec(value: str) -> dict[str, Any]:
    return {"kind": "choice", "value": value}


def _relation_rec(text: str, latex: str) -> dict[str, Any]:
    return {"kind": "relation", "text": text, "latex": latex}


def _set_rec(values: list[Fraction]) -> dict[str, Any]:
    return {"kind": "set", "values": [frac_text(v) for v in values]}


def _sp_circle_from_text(text: str) -> tuple[sp.Rational, sp.Rational, sp.Rational]:
    """Centre / squared radius of a monic circle equation, derived from its polynomial coefficients."""
    left, right = text.replace("^", "**").split("=")
    poly = sp.Poly(sp.sympify(left) - sp.sympify(right), X, Y)
    if poly.coeff_monomial(X**2) != 1 or poly.coeff_monomial(Y**2) != 1 or poly.coeff_monomial(X * Y) != 0:
        raise ValueError("not_a_monic_circle")
    d, e, f = poly.coeff_monomial(X), poly.coeff_monomial(Y), poly.coeff_monomial(1)
    h, k = -d / 2, -e / 2
    return (sp.Rational(h), sp.Rational(k), sp.Rational(h * h + k * k - f))


def _sp_on(circle: tuple, p: Any) -> bool:
    h, k, r2 = circle
    x0, y0 = _sr(p[0]), _sr(p[1])
    return bool(sp.simplify((x0 - h) ** 2 + (y0 - k) ** 2 - r2) == 0)


def _sp_rat(text: Any) -> sp.Rational:
    return sp.Rational(str(text))


def _sp_dist2(p: Any, q: Any) -> sp.Rational:
    return (_sr(p[0]) - _sr(q[0])) ** 2 + (_sr(p[1]) - _sr(q[1])) ** 2


def _sp_general(spec: dict[str, Any]) -> tuple[sp.Rational, sp.Rational, sp.Rational]:
    a, d, e, f = (_sr(spec.get(key, 1 if key == "a" else 0)) for key in ("a", "d", "e", "f"))
    h, k = -d / (2 * a), -e / (2 * a)
    return (h, k, h * h + k * k - f / a)


def _sp_circle_of(spec: dict[str, Any]) -> tuple[sp.Rational, sp.Rational, sp.Rational]:
    if "d" in spec:
        return _sp_general(spec)
    return (_sr(spec["center"][0]), _sr(spec["center"][1]), _sr(spec["r2"]))


# --- 1. write_circle_equations -----------------------------------------------------------------------------------

_VALUES = {"center_radius": 1, "center_point": 1, "diameter": 1, "concentric_through": 1, "axis_center_through_points": 1,
           "axis_center_through_point_radius": 2, "circumcircle": 1, "perp_bisector": 1, "origin_circle_k": 1,
           "diameter_param_k": 2}


def _origin_r2(item: dict[str, Any]) -> Fraction:
    """|P|^2 of the given point; ``x_sqrt`` n means the abscissa is sqrt(n) (the item then carries only the ordinate)."""
    if "x_sqrt" in item:
        return Fraction(int(item["x_sqrt"])) + fr(item["point"][1]) ** 2
    return dist2((0, 0), item["point"])


def _solve_item(item: dict[str, Any]) -> list[dict[str, Any]]:
    kind = item["kind"]
    if kind == "center_radius":
        return [_equation_rec((fr(item["center"][0]), fr(item["center"][1]), fr(item["r2"])))]
    if kind == "center_point":
        c = pt(item["center"])
        r2 = dist2(c, item["point"])
        if r2 == 0:
            raise ValueError("point_at_centre")
        return [_equation_rec((c[0], c[1], r2))]
    if kind == "diameter":
        a, b = pt(item["a"]), pt(item["b"])
        if a == b:
            raise ValueError("coincident_endpoints")
        m = G.midpoint(a, b)
        return [_equation_rec((m[0], m[1], dist2(a, b) / 4))]
    if kind == "concentric_through":
        h, k, _ = _gen(item["ref"])
        r2 = dist2((h, k), item["point"])
        if r2 == 0:
            raise ValueError("point_at_centre")
        return [_equation_rec((h, k, r2))]
    if kind == "axis_center_through_points":
        p, q = pt(item["points"][0]), pt(item["points"][1])
        if p[0] == q[0]:
            raise ValueError("centre_not_determined")
        h = (q[0] ** 2 + q[1] ** 2 - p[0] ** 2 - p[1] ** 2) / (2 * (q[0] - p[0]))
        return [_equation_rec((h, Fraction(0), dist2((h, 0), p)))]
    if kind == "axis_center_through_point_radius":
        p, r = pt(item["point"]), fr(item["r"])
        under = r * r - p[1] ** 2
        root = exact_sqrt_fraction(under)
        if root is None or root == 0:
            raise ValueError("two_rational_centres_required")
        return [_equation_rec((p[0] - root, Fraction(0), r * r)), _equation_rec((p[0] + root, Fraction(0), r * r))]
    if kind == "circumcircle":
        a, b, c = pt(item["a"]), pt(item["b"]), pt(item["c"])
        centre = G.circumcenter(a, b, c)
        return [_equation_rec((centre[0], centre[1], dist2(centre, a)))]
    if kind == "perp_bisector":
        return [_line_rec(G.perp_bisector(pt(item["p"]), pt(item["q"])))]
    if kind == "origin_circle_k":
        r2 = _origin_r2(item)
        if r2 == 0:
            raise ValueError("point_at_origin")
        return [_rational_rec(r2)]
    if kind == "diameter_param_k":
        c, a = pt(item["center"]), pt(item["a"])
        r2 = dist2(c, a)
        if r2 == 0:
            raise ValueError("endpoint_at_centre")
        return [_rational_rec(r2), _point_rec((2 * c[0] - a[0], 2 * c[1] - a[1]))]
    raise ValueError(f"unknown_circle_item_kind:{kind}")


def write_circle_equations(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    values: list[dict[str, Any]] = []
    for item in items:
        values.extend(_solve_item(item))
    return {"values": values}


def _check_write_circle_equations(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    values, index = answer["values"], 0
    for item in givens["items"]:
        kind = item["kind"]
        recs = values[index:index + _VALUES[kind]]
        index += _VALUES[kind]
        if len(recs) != _VALUES[kind]:
            return False
        if kind == "perp_bisector":
            a, b, c = (sp.Integer(v) for v in recs[0]["line"])
            p, q = item["p"], item["q"]
            mx, my = (_sr(p[0]) + _sr(q[0])) / 2, (_sr(p[1]) + _sr(q[1])) / 2
            dx, dy = _sr(q[0]) - _sr(p[0]), _sr(q[1]) - _sr(p[1])
            # passes through the midpoint and its normal (a, b) is parallel to the segment
            if a * mx + b * my + c != 0 or a * dy - b * dx != 0:
                return False
            continue
        if kind == "origin_circle_k":
            k = _sp_rat(recs[0]["canonical"])
            px = sp.sqrt(int(item["x_sqrt"])) if "x_sqrt" in item else _sr(item["point"][0])
            if sp.simplify(px**2 + _sr(item["point"][1]) ** 2 - k) != 0 or k <= 0:
                return False
            continue
        if kind == "diameter_param_k":
            k = _sp_rat(recs[0]["canonical"])
            bx, by = (_sp_rat(v) for v in recs[1]["point"])
            cx, cy = _sr(item["center"][0]), _sr(item["center"][1])
            ax, ay = _sr(item["a"][0]), _sr(item["a"][1])
            on_circle = lambda x0, y0: sp.simplify((x0 - cx) ** 2 + (y0 - cy) ** 2 - k) == 0  # noqa: E731
            return_ok = on_circle(ax, ay) and on_circle(bx, by) and (ax + bx) / 2 == cx and (ay + by) / 2 == cy and k > 0
            if not return_ok:
                return False
            continue
        circles = [_sp_circle_from_text(r["text"]) for r in recs]
        if any(c[2] <= 0 for c in circles):
            return False
        if kind == "center_radius":
            if circles[0] != (_sr(item["center"][0]), _sr(item["center"][1]), _sr(item["r2"])):
                return False
        elif kind == "center_point":
            c = circles[0]
            if (c[0], c[1]) != (_sr(item["center"][0]), _sr(item["center"][1])) or not _sp_on(c, item["point"]):
                return False
        elif kind == "diameter":
            c = circles[0]
            a, b = item["a"], item["b"]
            if not (_sp_on(c, a) and _sp_on(c, b)):
                return False
            if (c[0], c[1]) != ((_sr(a[0]) + _sr(b[0])) / 2, (_sr(a[1]) + _sr(b[1])) / 2):
                return False
        elif kind == "concentric_through":
            c, ref = circles[0], _sp_general(item["ref"])
            if (c[0], c[1]) != (ref[0], ref[1]) or not _sp_on(c, item["point"]):
                return False
        elif kind == "axis_center_through_points":
            c = circles[0]
            if c[1] != 0 or not all(_sp_on(c, p) for p in item["points"]):
                return False
        elif kind == "axis_center_through_point_radius":
            r = _sr(item["r"])
            if circles[0][0] >= circles[1][0]:
                return False
            for c in circles:
                if c[1] != 0 or c[2] != r * r or not _sp_on(c, item["point"]):
                    return False
        elif kind == "circumcircle":
            if not all(_sp_on(circles[0], item[key]) for key in ("a", "b", "c")):
                return False
        else:
            return False
    return index == len(values)


# --- 2. analyze_general_circle ----------------------------------------------------------------------------------------

_B_VALUES = {"center_radius": 2, "standard_and_classify": 2, "classify": 1, "param_range": 1, "param_from_radius": 1,
             "param_radius_center": 3, "coefficients_from_center": 3}


def _param_f(item: dict[str, Any]) -> tuple[Fraction, Fraction]:
    return fr(item.get("f0", 0)), fr(item["f1"])


def _analyze_item(item: dict[str, Any]) -> list[dict[str, Any]]:
    kind = item["kind"]
    if kind == "center_radius":
        if item.get("form") == "root":  # sqrt((x-h)^2+(y-k)^2)=r  (r > 0)
            h, k, r = fr(item["h"]), fr(item["k"]), fr(item["rhs"])
            if r <= 0:
                raise ValueError("positive_radius_required")
            circle = (h, k, r * r)
        else:
            circle = _gen(item)
        if circle[2] <= 0:
            raise ValueError("not_a_real_circle")
        return [_point_rec((circle[0], circle[1])), _radius_rec(circle[2])]
    if kind == "standard_and_classify":
        circle = _gen(item)
        return [_equation_rec(circle), _choice_rec(classify_r2(circle[2]))]
    if kind == "classify":
        return [_choice_rec(classify_r2(_gen(item)[2]))]
    if kind in ("param_range", "param_from_radius", "param_radius_center"):
        d = fr(item["d"])
        if kind == "param_radius_center":
            e1, e0 = fr(item["e1"]), fr(item.get("e0", 0))
            f1, f0 = fr(item["f1"]), fr(item.get("f0", 0))
            r2 = fr(item["r2"])
            kk = sp.Symbol("k", real=True)
            expr = (_sr(d) ** 2 + (_sr(e1) * kk + _sr(e0)) ** 2) / 4 - (_sr(f1) * kk + _sr(f0)) - _sr(r2)
            roots = sorted(sp.solve(sp.expand(expr), kk))
            if len(roots) != 2 or not all(r.is_Rational for r in roots):
                raise ValueError("two_rational_parameters_required")
            ks = [Fraction(int(r.p), int(r.q)) for r in roots]
            centre = lambda kv: (-d / 2, -(e1 * kv + e0) / 2)  # noqa: E731
            return [_set_rec(ks), _point_rec(centre(ks[1])), _point_rec(centre(ks[0]))]
        e = fr(item["e"])
        f0, f1 = _param_f(item)
        if f1 == 0:
            raise ValueError("parameter_must_appear")
        t = (d * d + e * e) / 4 - f0
        if kind == "param_from_radius":
            return [_rational_rec((t - fr(item["r2"])) / f1)]
        bound = t / f1
        op = "<" if f1 > 0 else ">"
        return [_relation_rec(f"k{op}{frac_text(bound)}", f"k{op}{frac_latex(bound)}")]
    if kind == "coefficients_from_center":
        h, k, f0 = fr(item["h"]), fr(item["k"]), fr(item["f"])
        r2 = h * h + k * k - f0
        if r2 <= 0:
            raise ValueError("not_a_real_circle")
        return [_rational_rec(-2 * h), _rational_rec(-2 * k), _radius_rec(r2)]
    raise ValueError(f"unknown_analyze_kind:{kind}")


def analyze_general_circle(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    values: list[dict[str, Any]] = []
    for item in items:
        values.extend(_analyze_item(item))
    return {"values": values}


def _sp_radical(rec: dict[str, Any]) -> sp.Expr:
    if rec["kind"] == "rational":
        return _sp_rat(rec["canonical"])
    return _sp_rat(rec["coef"]) * sp.sqrt(rec["radicand"])


def _form_kind(a: sp.Rational, d: sp.Rational, e: sp.Rational, f: sp.Rational) -> str:
    """a(x^2+y^2)+dx+ey+f = a((x-h)^2+(y-k)^2) + F(h,k): the sign of a*F(h,k) at the stationary point decides the locus."""
    h, k = -d / (2 * a), -e / (2 * a)
    value = a * (h * h + k * k) + d * h + e * k + f
    return "circle" if a * value < 0 else ("point" if value == 0 else "none")


def _check_analyze_general_circle(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    values, index = answer["values"], 0
    for item in givens["items"]:
        kind = item["kind"]
        recs = values[index:index + _B_VALUES[kind]]
        index += _B_VALUES[kind]
        if len(recs) != _B_VALUES[kind]:
            return False
        if kind == "center_radius":
            cx, cy = (_sp_rat(v) for v in recs[0]["point"])
            radius = _sp_radical(recs[1])
            if item.get("form") == "root":
                # the locus sqrt((x-h)^2+(y-k)^2)=rhs: every point at distance rhs from (h,k), and rhs > 0
                if (cx, cy) != (_sr(item["h"]), _sr(item["k"])) or sp.simplify(radius - _sr(item["rhs"])) != 0 or radius <= 0:
                    return False
            else:
                a, d, e, f = (_sr(item.get(key, 1 if key == "a" else 0)) for key in ("a", "d", "e", "f"))
                # polynomial identity: a(x^2+y^2)+dx+ey+f = a((x-cx)^2+(y-cy)^2-radius^2)
                diff = sp.expand(a * (X**2 + Y**2) + d * X + e * Y + f - a * ((X - cx) ** 2 + (Y - cy) ** 2 - radius**2))
                if sp.simplify(diff) != 0 or radius <= 0:
                    return False
        elif kind == "standard_and_classify":
            c = _sp_circle_from_text(recs[0]["text"])
            a, d, e, f = (_sr(item.get(key, 1 if key == "a" else 0)) for key in ("a", "d", "e", "f"))
            diff = sp.expand(a * (X**2 + Y**2) + d * X + e * Y + f - a * ((X - c[0]) ** 2 + (Y - c[1]) ** 2 - c[2]))
            if sp.simplify(diff) != 0 or recs[1]["value"] != _form_kind(a, d, e, f):
                return False
        elif kind == "classify":
            a, d, e, f = (_sr(item.get(key, 1 if key == "a" else 0)) for key in ("a", "d", "e", "f"))
            if recs[0]["value"] != _form_kind(a, d, e, f):
                return False
        elif kind == "param_range":
            d, e = _sr(item["d"]), _sr(item["e"])
            f0, f1 = _sr(item.get("f0", 0)), _sr(item["f1"])
            kk = sp.Symbol("k", real=True)
            r2 = (d**2 + e**2) / 4 - (f0 + f1 * kk)
            solution = sp.solve_univariate_inequality(r2 > 0, kk, relational=False)
            text = recs[0]["text"]
            op, bound = ("<", text.split("<")[1]) if "<" in text else (">", text.split(">")[1])
            bound = _sp_rat(bound)
            expected = sp.Interval.open(-sp.oo, bound) if op == "<" else sp.Interval.open(bound, sp.oo)
            if solution != expected:
                return False
        elif kind == "param_from_radius":
            d, e = _sr(item["d"]), _sr(item["e"])
            f0, f1 = _sr(item.get("f0", 0)), _sr(item["f1"])
            kv = _sp_rat(recs[0]["canonical"])
            if sp.simplify((d**2 + e**2) / 4 - (f0 + f1 * kv) - _sr(item["r2"])) != 0:
                return False
        elif kind == "param_radius_center":
            d = _sr(item["d"])
            e1, e0 = _sr(item["e1"]), _sr(item.get("e0", 0))
            f1, f0 = _sr(item["f1"]), _sr(item.get("f0", 0))
            ks = sorted(_sp_rat(v) for v in recs[0]["values"])
            if len(ks) != 2 or ks[0] == ks[1]:
                return False
            for kv, centre_rec in zip(reversed(ks), recs[1:]):
                e_val, f_val = e1 * kv + e0, f1 * kv + f0
                if sp.simplify((d**2 + e_val**2) / 4 - f_val - _sr(item["r2"])) != 0:
                    return False
                if tuple(_sp_rat(v) for v in centre_rec["point"]) != (-d / 2, -e_val / 2):
                    return False
        elif kind == "coefficients_from_center":
            a_val, b_val = _sp_rat(recs[0]["canonical"]), _sp_rat(recs[1]["canonical"])
            radius = _sp_radical(recs[2])
            f0 = _sr(item["f"])
            # the form x^2+y^2+a x+b y+f0 is a(x-h)^2+... with centre (h,k): matches the given centre and radius
            diff = sp.expand(X**2 + Y**2 + a_val * X + b_val * Y + f0 - ((X - _sr(item["h"])) ** 2 + (Y - _sr(item["k"])) ** 2 - radius**2))
            if sp.simplify(diff) != 0 or radius <= 0:
                return False
        else:
            return False
    return index == len(values)


# --- 3. solve_distance_ratio_locus -----------------------------------------------------------------------------------

def _ratio_pair(ratio: list[Any] | None, weights: list[Any] | None) -> tuple[int, int]:
    """PA:PB = p:q in lowest integer terms; weights wa, wb mean PA, PB are inversely proportional to them."""
    if weights is not None:
        wa, wb = fr(weights[0]), fr(weights[1])
        p, q = 1 / wa, 1 / wb
    else:
        p, q = fr(ratio[0]), fr(ratio[1])
    scale = p.denominator * q.denominator
    pi_, qi = int(p * scale), int(q * scale)
    g = gcd(pi_, qi)
    return pi_ // g, qi // g


def _apollonius(a: tuple, b: tuple, p: int, q: int) -> Circle:
    """Locus of P with q*PA = p*PB (p != q): (q^2-p^2)|P|^2 - 2(q^2 A - p^2 B)·P + q^2|A|^2 - p^2|B|^2 = 0."""
    if p == q:
        raise ValueError("ratio_one_gives_a_line")
    s = Fraction(q * q - p * p)
    d = -2 * (q * q * a[0] - p * p * b[0]) / s
    e = -2 * (q * q * a[1] - p * p * b[1]) / s
    f = (q * q * (a[0] ** 2 + a[1] ** 2) - p * p * (b[0] ** 2 + b[1] ** 2)) / s
    return circle_from_general(d, e, f)


def solve_distance_ratio_locus(a: list[Any], b: list[Any], asks: list[str], ratio: list[Any] | None = None,
                               weights: list[Any] | None = None, half: str | None = None, **text: Any) -> dict[str, Any]:
    if ratio is None and weights is None:
        raise ValueError("ratio_or_weights_required")
    pa, pb = pt(a), pt(b)
    p, q = _ratio_pair(ratio, weights)
    circle = _apollonius(pa, pb, p, q)
    if circle[2] <= 0:
        raise ValueError("not_a_real_circle")
    if half is not None and (half not in ("upper", "lower") or pa[1] != 0 or pb[1] != 0):
        raise ValueError("half_requires_axis_aligned_points")
    shape = "circle" if half is None else f"{half}_semicircle"
    values = []
    for ask in asks:
        if ask == "ratio_p":
            values.append(_rational_rec(Fraction(p)))
        elif ask == "ratio_q":
            values.append(_rational_rec(Fraction(q)))
        elif ask == "equation":
            values.append(_equation_rec(circle))
        elif ask == "shape":
            values.append(_choice_rec(shape))
        elif ask == "center":
            values.append(_point_rec((circle[0], circle[1])))
        elif ask == "radius":
            values.append(_radius_rec(circle[2]))
        else:
            raise ValueError(f"unknown_locus_ask:{ask}")
    return {"ratio": [p, q], "values": values, "asks": list(asks), "shape": shape}


def _check_solve_distance_ratio_locus(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    ax, ay = _sr(givens["a"][0]), _sr(givens["a"][1])
    bx, by = _sr(givens["b"][0]), _sr(givens["b"][1])
    if givens.get("weights") is not None:
        wa, wb = _sr(givens["weights"][0]), _sr(givens["weights"][1])
        ratio = sp.Rational(1) / wa / (sp.Rational(1) / wb)  # PA:PB = (1/wa):(1/wb)
    else:
        ratio = _sr(givens["ratio"][0]) / _sr(givens["ratio"][1])
    p, q = answer["ratio"]
    if sp.Rational(p, q) != ratio or sp.igcd(p, q) != 1:
        return False
    # q^2 PA^2 - p^2 PB^2 = 0  must be a non-zero constant multiple of the circle polynomial
    locus = sp.expand(q * q * ((X - ax) ** 2 + (Y - ay) ** 2) - p * p * ((X - bx) ** 2 + (Y - by) ** 2))
    for ask, rec in zip(answer["asks"], answer["values"]):
        if ask == "ratio_p" and _sp_rat(rec["canonical"]) != p:
            return False
        if ask == "ratio_q" and _sp_rat(rec["canonical"]) != q:
            return False
        if ask == "equation":
            h, k, r2 = _sp_circle_from_text(rec["text"])
            circle_poly = sp.expand((X - h) ** 2 + (Y - k) ** 2 - r2)
            lead = locus.coeff(X, 2)
            if r2 <= 0 or lead == 0 or sp.simplify(locus - lead * circle_poly) != 0:
                return False
        if ask == "center":
            h, k, r2 = sp.Rational(0), sp.Rational(0), sp.Rational(0)
            lead = locus.coeff(X, 2)
            h = -locus.coeff(X, 1) / (2 * lead)
            k = -locus.coeff(Y, 1) / (2 * lead)
            if tuple(_sp_rat(v) for v in rec["point"]) != (h, k):
                return False
        if ask == "radius":
            lead = locus.coeff(X, 2)
            h, k = -locus.coeff(X, 1) / (2 * lead), -locus.coeff(Y, 1) / (2 * lead)
            r2 = h * h + k * k - locus.subs({X: 0, Y: 0}) / lead
            if sp.simplify(_sp_radical(rec) ** 2 - r2) != 0 or _sp_radical(rec) <= 0:
                return False
        if ask == "shape":
            expected = "circle" if givens.get("half") is None else f"{givens['half']}_semicircle"
            if rec["value"] != expected:
                return False
    return True


# --- 4. classify_points_against_circle ------------------------------------------------------------------------------------

def classify_points_against_circle(circle: dict[str, Any], points: list[list[Any]], **text: Any) -> dict[str, Any]:
    c = _circle_of(circle)
    if c[2] <= 0:
        raise ValueError("not_a_real_circle")
    kinds = [relation_to_circle(c, p) for p in points]
    if len(points) > 1 and len(set(kinds)) < 2:
        raise ValueError("points_should_not_all_be_in_the_same_position")
    return {"values": [_choice_rec(k) for k in kinds]}


def _check_classify_points_against_circle(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    h, k, r2 = _sp_circle_of(givens["circle"])
    if r2 <= 0 or len(answer["values"]) != len(givens["points"]):
        return False
    for p, rec in zip(givens["points"], answer["values"]):
        value = sp.simplify((_sr(p[0]) - h) ** 2 + (_sr(p[1]) - k) ** 2 - r2)  # sign of f(P)=PM^2-r^2
        expected = "inside" if value < 0 else ("outside" if value > 0 else "on")
        if rec["value"] != expected:
            return False
    return True


# --- 5. solve_circle_point_distances -------------------------------------------------------------------------------------------

def solve_circle_point_distances(circle: dict[str, Any], point: list[Any], asks: list[str], **text: Any) -> dict[str, Any]:
    c = _circle_of(circle)
    if c[2] <= 0:
        raise ValueError("not_a_real_circle")
    d2 = dist2((c[0], c[1]), point)
    d, r = exact_sqrt_fraction(d2), exact_sqrt_fraction(c[2])
    if d is None or r is None:
        raise ValueError("rational_distance_and_radius_required")
    values = []
    for ask in asks:
        if ask == "relation":
            values.append(_choice_rec("inside" if d < r else ("outside" if d > r else "on")))
        elif ask == "max":
            values.append(_rational_rec(d + r))
        elif ask == "min":
            values.append(_rational_rec(abs(d - r)))
        else:
            raise ValueError(f"unknown_distance_ask:{ask}")
    return {"values": values, "asks": list(asks), "centre_distance": frac_text(d), "radius": frac_text(r)}


def _check_solve_circle_point_distances(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    h, k, r2 = _sp_circle_of(givens["circle"])
    d2 = (_sr(givens["point"][0]) - h) ** 2 + (_sr(givens["point"][1]) - k) ** 2
    r = sp.sqrt(r2)
    d = sp.sqrt(d2)
    # extreme distances via the exact optimum of |P - Q| over Q on the circle: the line through the centre
    t = sp.Symbol("t", real=True)
    far = sp.sqrt((_sr(givens["point"][0]) - (h + r * sp.cos(t))) ** 2 + (_sr(givens["point"][1]) - (k + r * sp.sin(t))) ** 2)
    for ask, rec in zip(answer["asks"], answer["values"]):
        if ask == "relation":
            expected = "inside" if d2 < r2 else ("outside" if d2 > r2 else "on")
            if rec["value"] != expected:
                return False
        elif ask in ("max", "min"):
            value = _sp_rat(rec["canonical"])
            # attained by the two points of the circle on the line through the point and the centre
            if d == 0:
                return False
            ux, uy = (_sr(givens["point"][0]) - h) / d, (_sr(givens["point"][1]) - k) / d
            near, farthest = (h + r * ux, k + r * uy), (h - r * ux, k - r * uy)
            candidate = sp.sqrt(_sp_dist2(givens["point"], near if ask == "min" else farthest))
            if sp.simplify(candidate - value) != 0:
                return False
            # no point of the circle can beat it: compare with a dense sample
            samples = [float(far.subs(t, sp.Rational(i, 24) * 2 * sp.pi)) for i in range(24)]
            if ask == "max" and max(samples) > float(value) + 1e-9:
                return False
            if ask == "min" and min(samples) < float(value) - 1e-9:
                return False
        else:
            return False
    return True


# --- 6. solve_point_position_parameter_range ---------------------------------------------------------------------------------------

def solve_point_position_parameter_range(inside: list[list[Any]], outside: list[list[Any]], **text: Any) -> dict[str, Any]:
    """Circle ``x^2+y^2=k``: ``k`` must exceed |P|^2 for every inside point and stay below |Q|^2 for every outside point."""
    lower = max((dist2((0, 0), p) for p in inside), default=None)
    upper = min((dist2((0, 0), q) for q in outside), default=None)
    if lower is None and upper is None:
        raise ValueError("a_point_is_required")
    if lower is not None and lower <= 0 and upper is None:
        raise ValueError("origin_is_not_a_proper_inside_bound")
    if lower is not None and upper is not None and lower >= upper:
        raise ValueError("empty_range")
    lo = max(lower, Fraction(0)) if lower is not None else Fraction(0)
    if lower is not None and upper is not None:
        text_ = f"{frac_text(lo)}<k<{frac_text(upper)}"
        latex = f"{frac_latex(lo)}<k<{frac_latex(upper)}"
    elif upper is not None:
        text_, latex = f"0<k<{frac_text(upper)}", f"0<k<{frac_latex(upper)}"
    else:
        text_, latex = f"k>{frac_text(lo)}", f"k>{frac_latex(lo)}"
    return {"values": [_relation_rec(text_, latex)], "lower": frac_text(lo), "upper": None if upper is None else frac_text(upper)}


def _check_solve_point_position_parameter_range(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    kk = sp.Symbol("k", real=True)
    solution = sp.Interval.open(0, sp.oo)
    for p in givens["inside"]:
        solution = solution.intersect(sp.solve_univariate_inequality(_sr(p[0]) ** 2 + _sr(p[1]) ** 2 < kk, kk, relational=False))
    for q in givens["outside"]:
        solution = solution.intersect(sp.solve_univariate_inequality(_sr(q[0]) ** 2 + _sr(q[1]) ** 2 > kk, kk, relational=False))
    text = answer["values"][0]["text"]
    if text.startswith("k>"):
        interval = sp.Interval.open(_sp_rat(text[2:]), sp.oo)
    else:
        parts = text.split("<")
        interval = sp.Interval.open(_sp_rat(parts[0]), _sp_rat(parts[2]))
    return bool(solution != sp.S.EmptySet and solution == interval)


# --- 7. evaluate_circle_statement_truth ----------------------------------------------------------------------------------------------

def _quadrant(h: Fraction, k: Fraction) -> int:
    if h == 0 or k == 0:
        raise ValueError("centre_on_an_axis")
    return 1 if (h > 0 and k > 0) else (2 if (h < 0 and k > 0) else (3 if (h < 0 and k < 0) else 4))


def evaluate_circle_statement_truth(statement: dict[str, Any], **text: Any) -> dict[str, Any]:
    kind = statement["kind"]
    if kind == "center_quadrant":
        h, k, r2 = _std(statement)
        if r2 <= 0:
            raise ValueError("not_a_real_circle")
        return {"truth": _quadrant(h, k) == int(statement["claimed"])}
    if kind == "is_circle":
        return {"truth": _gen(statement)[2] > 0, "graph": classify_r2(_gen(statement)[2])}
    if kind == "may_be_point":
        f0, f1 = fr(statement.get("f0", 0)), fr(statement["f1"])
        d, e = fr(statement["d"]), fr(statement["e"])
        if f1 == 0:
            return {"truth": (d * d + e * e) / 4 - f0 == 0}
        return {"truth": True}  # k = (d^2+e^2)/4 - f0)/f1 makes the radius 0
    if kind == "origin_inside":
        h, k, r2 = _std(statement)
        if r2 <= 0:
            raise ValueError("not_a_real_circle")
        d2 = h * h + k * k
        if d2 == r2:
            raise ValueError("origin_on_the_circle")
        return {"truth": d2 < r2}
    if kind == "area_equals":
        r2 = fr(statement["r2"])
        if r2 <= 0:
            raise ValueError("not_a_real_circle")
        claimed = fr(statement["claimed_coef"])
        with_pi = bool(statement["with_pi"])
        return {"truth": with_pi and claimed == r2}
    raise ValueError(f"unknown_circle_statement_kind:{kind}")


def _check_evaluate_circle_statement_truth(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    statement, truth = givens["statement"], answer["truth"]
    kind = statement["kind"]
    if kind == "center_quadrant":
        h, k, _ = _sp_circle_of(statement)
        quadrant = {(True, True): 1, (False, True): 2, (False, False): 3, (True, False): 4}[(h > 0, k > 0)]
        return (quadrant == int(statement["claimed"])) == truth
    if kind == "is_circle":
        c = _sp_general(statement)
        # exists a real point on the locus other than a single point <=> radius^2 > 0
        return (c[2] > 0) == truth
    if kind == "may_be_point":
        kk = sp.Symbol("k", real=True)
        d, e = _sr(statement["d"]), _sr(statement["e"])
        f = _sr(statement.get("f0", 0)) + _sr(statement["f1"]) * kk
        r2 = (d**2 + e**2) / 4 - f
        solutions = sp.solve(r2, kk) if r2.has(kk) else ([] if r2 != 0 else [0])
        return bool(solutions) == truth
    if kind == "origin_inside":
        h, k, r2 = _sp_circle_of(statement)
        return (h**2 + k**2 < r2) == truth
    if kind == "area_equals":
        r2 = _sr(statement["r2"])
        area = sp.pi * r2
        claimed = _sr(statement["claimed_coef"]) * (sp.pi if statement["with_pi"] else 1)
        return (sp.simplify(area - claimed) == 0) == truth
    return False


# --- 8. solve_mohr_circles ------------------------------------------------------------------------------------------------------------------

def solve_mohr_circles(options: list[dict[str, Any]], diameter: dict[str, Any], nested: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    """Mohr circle = circle whose centre lies on the x-axis."""
    on_axis = [i for i, spec in enumerate(options) if (c := _gen(spec))[2] > 0 and c[1] == 0]
    if len(on_axis) != 1:
        raise ValueError("exactly_one_mohr_option_required")
    a, b = pt(diameter["a"]), pt(diameter["b"])
    m = G.midpoint(a, b)
    if m[1] != 0:
        raise ValueError("diameter_endpoints_not_a_mohr_circle")
    circles = [_gen(spec) for spec in nested]
    if any(c[1] != 0 or c[2] <= 0 for c in circles):
        raise ValueError("nested_circles_must_be_mohr_circles")
    big = max(circles, key=lambda c: c[2])
    smalls = [c for c in circles if c is not big]
    if len(smalls) != 2:
        raise ValueError("one_big_and_two_small_circles_required")
    for c in smalls:
        gap = abs(big[0] - c[0])
        if gap + exact_sqrt_fraction(c[2]) > exact_sqrt_fraction(big[2]):
            raise ValueError("small_circle_not_inside_big_circle")
    s1, s2 = smalls
    if abs(s1[0] - s2[0]) < exact_sqrt_fraction(s1[2]) + exact_sqrt_fraction(s2[2]):
        raise ValueError("small_circles_overlap")
    coef = big[2] - s1[2] - s2[2]
    if coef <= 0:
        raise ValueError("empty_region")
    return {"values": [_choice_rec(str(on_axis[0] + 1)), _equation_rec((m[0], Fraction(0), dist2(a, b) / 4)),
                       {"kind": "pi_multiple", "coef": frac_text(coef), "canonical": f"{frac_text(coef)}*pi", "latex": f"{frac_latex(coef)}\\pi"}]}


def _check_solve_mohr_circles(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    choice, equation, area = answer["values"]
    centres_on_axis = [(_sp_general(spec)[1] == 0 and _sp_general(spec)[2] > 0) for spec in givens["options"]]
    if centres_on_axis.count(True) != 1 or centres_on_axis.index(True) + 1 != int(choice["value"]):
        return False
    c = _sp_circle_from_text(equation["text"])
    a, b = givens["diameter"]["a"], givens["diameter"]["b"]
    if not (c[1] == 0 and _sp_on(c, a) and _sp_on(c, b) and (c[0] == (_sr(a[0]) + _sr(b[0])) / 2)):
        return False
    radii = sorted(_sp_general(spec)[2] for spec in givens["nested"])
    return bool(sp.simplify(sp.pi * (radii[2] - radii[0] - radii[1]) - sp.sympify(area["canonical"])) == 0)


# --- 9. solve_storm_entry_time ------------------------------------------------------------------------------------------------------------------

def solve_storm_entry_time(start_hour: int, distance: Any, radius: Any, speed: Any, options: list[int], **text: Any) -> dict[str, Any]:
    d, r, v = fr(distance), fr(radius), fr(speed)
    if v <= 0 or d <= r or r <= 0:
        raise ValueError("storm_must_approach_from_outside")
    entry = Fraction(int(start_hour)) + (d - r) / v
    gaps = sorted((abs(entry - o), i) for i, o in enumerate(options))
    if len(set(options)) != len(options) or gaps[0][0] > 1 or gaps[1][0] - gaps[0][0] < 2:
        raise ValueError("exactly_one_option_should_match_the_entry_time")
    return {"values": [_choice_rec(str(gaps[0][1] + 1))], "entry_hour": frac_text(entry), "hours_after_start": frac_text((d - r) / v)}


def _check_solve_storm_entry_time(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    t = sp.Symbol("t", real=True)
    # centre-to-point distance after t hours is d - v t (storm moves straight towards the point); entry when it equals the radius
    (root,) = sp.solve(sp.Eq(_sr(givens["distance"]) - _sr(givens["speed"]) * t, _sr(givens["radius"])), t)
    entry = _sr(givens["start_hour"]) + root
    nearest = min(range(len(givens["options"])), key=lambda i: abs(entry - givens["options"][i]))
    close = abs(entry - givens["options"][nearest]) <= 1
    return bool(close and int(answer["values"][0]["value"]) == nearest + 1 and sp.Rational(answer["entry_hour"]) == entry)


# --- 10. solve_circular_arch_height --------------------------------------------------------------------------------------------------------------------

def solve_circular_arch_height(width: Any, height: Any, post_offset: Any, **text: Any) -> dict[str, Any]:
    """Arch through P(w/2,0), Q(-w/2,0) and B(0,H); height of the post standing at horizontal offset ``post_offset``."""
    w, h, off = fr(width), fr(height), fr(post_offset)
    if w <= 0 or h <= 0 or abs(off) > w / 2:
        raise ValueError("invalid_arch")
    c = (h * h - (w / 2) ** 2) / (2 * h)  # centre (0, c)
    r2 = (w / 2) ** 2 + c * c
    under = r2 - off * off
    if under <= 0:
        raise ValueError("post_outside_arch")
    root = exact_sqrt_fraction(under)
    if root is None:
        raise ValueError("rational_post_height_required")
    post = c + root
    if post <= 0:
        raise ValueError("post_height_must_be_positive")
    return {"values": [_rational_rec(post)], "centre": [frac_text(Fraction(0)), frac_text(c)], "r2": frac_text(r2)}


def _check_solve_circular_arch_height(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    w, h, off = _sr(givens["width"]), _sr(givens["height"]), _sr(givens["post_offset"])
    cc = sp.Symbol("c", real=True)
    (centre_y,) = sp.solve(sp.Eq((w / 2) ** 2 + cc**2, (h - cc) ** 2), cc)  # equidistant from P and B
    r2 = (w / 2) ** 2 + centre_y**2
    yy = sp.Symbol("y", real=True)
    heights = sp.solve(sp.Eq(off**2 + (yy - centre_y) ** 2, r2), yy)
    value = _sp_rat(answer["values"][0]["canonical"])
    ok = value in heights and value == max(heights)
    centre = answer["centre"]
    return bool(ok and _sp_rat(centre[1]) == centre_y and _sp_rat(answer["r2"]) == r2)


# --- operation table ---------------------------------------------------------------------------------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "write_circle_equations": (write_circle_equations, _check_write_circle_equations, ("items",)),
    "analyze_general_circle": (analyze_general_circle, _check_analyze_general_circle, ("items",)),
    "solve_distance_ratio_locus": (solve_distance_ratio_locus, _check_solve_distance_ratio_locus, ("a", "b", "asks")),
    "classify_points_against_circle": (classify_points_against_circle, _check_classify_points_against_circle, ("circle", "points")),
    "solve_circle_point_distances": (solve_circle_point_distances, _check_solve_circle_point_distances, ("circle", "point", "asks")),
    "solve_point_position_parameter_range": (solve_point_position_parameter_range, _check_solve_point_position_parameter_range, ("inside", "outside")),
    "evaluate_circle_statement_truth": (evaluate_circle_statement_truth, _check_evaluate_circle_statement_truth, ("statement",)),
    "solve_mohr_circles": (solve_mohr_circles, _check_solve_mohr_circles, ("options", "diameter", "nested")),
    "solve_storm_entry_time": (solve_storm_entry_time, _check_solve_storm_entry_time, ("start_hour", "distance", "radius", "speed", "options")),
    "solve_circular_arch_height": (solve_circular_arch_height, _check_solve_circular_arch_height, ("width", "height", "post_offset")),
}
OPERATIONS = tuple(_OPERATIONS)


def build_circle_equations_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_circle_equations_operation:{operation}")
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


# --- validators (never raise) -----------------------------------------------------------------------------------------------------------------------------

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
