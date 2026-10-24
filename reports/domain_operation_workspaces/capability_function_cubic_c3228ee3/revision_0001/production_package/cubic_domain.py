"""Exact domain operations for general-high Mathematics 1, Unit 10 (三次函數的圖形特徵).

Domain key ``function.cubic_graph``.  Every operation is one shared, source-agnostic implementation:
components pass *inputs only* (``constraints``); this module computes the canonical answer with exact
``Fraction`` arithmetic and each validator re-derives it by a different method (sympy expansion / linear
solving with a different unknown set, symbolic differentiation, or re-reading the sampled curves), never by
calling the same construction code again.

A cubic is handled in the textbook's *symmetry-centre form* ``y = a(x-h)^3 + p(x-h) + k`` (centre ``(h, k)``)
and in coefficient form ``[c3, c2, c1, c0]`` (highest degree first).
"""

from __future__ import annotations

import itertools
from fractions import Fraction
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Callable

import sympy as sp

from core.domain.promoted.algebra_polynomial_division.polynomial_core import (
    coeff, fr, frac_latex, frac_text, poly, poly_latex, poly_plain,
)

DOMAIN_KEY = "function.cubic_graph"
X = sp.Symbol("x", real=True)
PARAM_C = sp.Symbol("c", real=True)
PARAM_D = sp.Symbol("d", real=True)


# --- records ----------------------------------------------------------------------------------------------

def rrec(q: Any) -> dict[str, Any]:
    q = fr(q)
    return {"kind": "rational", "canonical": frac_text(q), "latex": frac_latex(q)}


def prec(coeffs: list[Fraction]) -> dict[str, Any]:
    p = poly(coeffs)
    return {"kind": "poly", "coeffs": [frac_text(c) for c in p], "plain": poly_plain(p), "latex": poly_latex(p)}


def pointrec(x: Fraction, y: Fraction) -> dict[str, Any]:
    return {"kind": "point", "x": frac_text(x), "y": frac_text(y), "text": f"({frac_text(x)},{frac_text(y)})"}


def _require(constraints: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in constraints]
    if missing:
        raise ValueError(f"givens_required:{','.join(missing)}")


def _sx(v: Any) -> sp.Rational:
    q = fr(v)
    return sp.Rational(q.numerator, q.denominator)


# --- exact cubic arithmetic ------------------------------------------------------------------------------

def _coeffs(c: Any) -> list[Fraction]:
    values = [fr(v) for v in c]
    if len(values) != 4 or values[0] == 0:
        raise ValueError("cubic_needs_four_coefficients_with_nonzero_leading")
    return values


def _eval(c: list[Fraction], x: Fraction) -> Fraction:
    return ((c[0] * x + c[1]) * x + c[2]) * x + c[3]


def _to_form(c: list[Fraction]) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Coefficients -> (a, p, h, k) with y=a(x-h)^3+p(x-h)+k."""
    c3, c2, c1, c0 = c
    h = -c2 / (3 * c3)
    p = c1 - 3 * c3 * h * h
    k = c0 - 2 * c3 * h ** 3 + c1 * h
    return c3, p, h, k


def _from_form(a: Fraction, p: Fraction, h: Fraction, k: Fraction) -> list[Fraction]:
    """(a, p, h, k) -> coefficients, by expanding the powers of (x-h) directly."""
    return [a, -3 * a * h, 3 * a * h * h + p, -a * h ** 3 - p * h + k]


def _form(spec: Any) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    a, p, h, k = (fr(spec[key]) for key in ("a", "p", "h", "k"))
    if a == 0:
        raise ValueError("cubic_leading_coefficient_must_be_nonzero")
    return a, p, h, k


def _sp_cubic(c: list[Fraction]) -> sp.Expr:
    return sum((_sx(v) * X ** (3 - i) for i, v in enumerate(c)), sp.Integer(0))


def _sp_form(a: Any, p: Any, h: Any, k: Any) -> sp.Expr:
    return _sx(a) * (X - _sx(h)) ** 3 + _sx(p) * (X - _sx(h)) + _sx(k)


def _sp_is_symmetric_about(f: sp.Expr, h: sp.Rational, k: sp.Rational) -> bool:
    t = sp.Symbol("t", real=True)
    return sp.expand(f.subs(X, h + t) + f.subs(X, h - t) - 2 * k) == 0


# --- 1. cubic_center_form ---------------------------------------------------------------------------------

def _record_form(c: list[Fraction]) -> dict[str, Any]:
    a, p, h, k = _to_form(c)
    return {"coeffs": prec(c), "a": rrec(a), "p": rrec(p), "h": rrec(h), "k": rrec(k), "center": pointrec(h, k)}


def cubic_center_form(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    out = []
    for it in items:
        kind = it["kind"]
        rec: dict[str, Any] = {"kind": kind}
        if kind in ("to_form", "center"):
            rec.update(_record_form(_coeffs(it["coeffs"])))
        elif kind == "from_center":
            a, p = fr(it["a"]), fr(it["p"])
            cx, cy = fr(it["center"][0]), fr(it["center"][1])
            if a == 0:
                raise ValueError("cubic_leading_coefficient_must_be_nonzero")
            rec.update({"a": rrec(a), "p": rrec(p), "h": rrec(cx), "k": rrec(cy), "center": pointrec(cx, cy),
                        "coeffs": prec(_from_form(a, p, cx, cy))})
        elif kind == "shift":
            a, p, h, k = _form(it["form"])
            dx, dy = fr(it["dx"]), fr(it["dy"])
            power = int(it["power"])
            if not 0 <= power <= 3:
                raise ValueError("power_out_of_range")
            g = _from_form(a, p, h + dx, k + dy)  # g(x) = f(x - dx) + dy
            rec.update({"g_coeffs": prec(g), "g_form": {"a": rrec(a), "p": rrec(p), "h": rrec(h + dx), "k": rrec(k + dy)},
                        "asked_power": power, "asked_coeff": rrec(coeff(poly(g), power))})
        elif kind == "translation_overlap":
            fa, fp, fh, fk = _form(it["f"])
            ga, gp, gh, gk = _form(it["g"])
            overlap = fa == ga and fp == gp
            rec.update({"overlap": overlap, "dx": rrec(gh - fh), "dy": rrec(gk - fk)})
        else:
            raise ValueError(f"unknown_cubic_center_form_kind:{kind}")
        out.append(rec)
    return {"items": out}


def _check_cubic_center_form(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    if len(givens["items"]) != len(answer["items"]):
        return False
    for it, rec in zip(givens["items"], answer["items"]):
        kind = it["kind"]
        if rec["kind"] != kind:
            return False
        if kind in ("to_form", "center"):
            f = _sp_cubic(_coeffs(it["coeffs"]))
            a, p, h, k = (sp.Rational(rec[key]["canonical"]) for key in ("a", "p", "h", "k"))
            if sp.expand(f - _sp_form(a, p, h, k)) != 0 or not _sp_is_symmetric_about(f, h, k):
                return False
            # the centre is unique: the second derivative vanishes only at x = h
            if sp.solve(sp.diff(f, X, 2), X) != [h]:
                return False
        elif kind == "from_center":
            a, p = _sx(it["a"]), _sx(it["p"])
            cx, cy = _sx(it["center"][0]), _sx(it["center"][1])
            f = sp.expand(a * (X - sp.Rational(rec["h"]["canonical"])) ** 3 + p * (X - sp.Rational(rec["h"]["canonical"])) + sp.Rational(rec["k"]["canonical"]))
            if not _sp_is_symmetric_about(f, cx, cy) or sp.Rational(rec["h"]["canonical"]) != cx or sp.Rational(rec["k"]["canonical"]) != cy:
                return False
        elif kind == "shift":
            a, p, h, k = (_sx(v) for v in (it["form"]["a"], it["form"]["p"], it["form"]["h"], it["form"]["k"]))
            f = _sp_form(a, p, h, k)
            g = sp.expand(f.subs(X, X - _sx(it["dx"])) + _sx(it["dy"]))
            power = rec["asked_power"]
            if sp.Poly(g, X).coeff_monomial(X ** power) != sp.Rational(rec["asked_coeff"]["canonical"]):
                return False
            if sp.expand(g - _sp_cubic([fr(v) for v in rec["g_coeffs"]["coeffs"]])) != 0:
                return False
        elif kind == "translation_overlap":
            f = _sp_form(*(_sx(it["f"][key]) for key in ("a", "p", "h", "k")))
            g = _sp_form(*(_sx(it["g"][key]) for key in ("a", "p", "h", "k")))
            dx, dy = sp.Rational(rec["dx"]["canonical"]), sp.Rational(rec["dy"]["canonical"])
            same_shape = sp.expand(f.subs(X, X - dx) + dy - g) == 0
            if same_shape != bool(rec["overlap"]):
                return False
        else:
            return False
    return True


# --- 2. cubic_from_conditions ----------------------------------------------------------------------------

def cubic_from_conditions(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    out = []
    for it in items:
        kind = it["kind"]
        rec: dict[str, Any] = {"kind": kind}
        if kind == "symmetric_pair_origin":
            # origin O and A are on the graph; A and B are symmetric about the centre; ask the centre, f and f(c_x)
            ax, ay = fr(it["A"][0]), fr(it["A"][1])
            bx, by = fr(it["B"][0]), fr(it["B"][1])
            cx = fr(it["C_x"])
            h, k = (ax + bx) / 2, (ay + by) / 2
            # y = a(x-h)^3 + p(x-h) + k through O and A
            u0, u1 = -h, ax - h
            r0, r1 = -k, ay - k
            det = u0 ** 3 * u1 - u1 ** 3 * u0
            if det == 0:
                raise ValueError("conditions_are_degenerate")
            a = (r0 * u1 - r1 * u0) / det
            p = (u0 ** 3 * r1 - u1 ** 3 * r0) / det
            if a == 0:
                raise ValueError("not_a_cubic")
            c = _from_form(a, p, h, k)
            rec.update({"center": pointrec(h, k), "f": prec(c), "a": rrec(a), "p": rrec(p),
                        "s": rrec(_eval(c, cx)), "value_at_B": rrec(_eval(c, bx))})
        elif kind == "center_zero_linear":
            cx, cy = fr(it["center"][0]), fr(it["center"][1])
            if cx == 0:
                raise ValueError("centre_must_not_be_on_the_y_axis")
            a = -cy / (2 * cx ** 3)
            b = -3 * a * cx
            c = [a, b, Fraction(0), Fraction(0)]
            rec.update({"landing": pointrec(2 * cx, 2 * cy), "f": prec(c)})
        elif kind == "global_local":
            lead, m, n, h = fr(it["lead"]), fr(it["slope"]), fr(it["intercept"]), fr(it["h"])
            if lead == 0:
                raise ValueError("not_a_cubic")
            rec.update({"a": rrec(lead), "b": rrec(m), "c": rrec(m * h + n), "h": rrec(h)})
        else:
            raise ValueError(f"unknown_cubic_from_conditions_kind:{kind}")
        out.append(rec)
    return {"items": out}


def _check_cubic_from_conditions(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for it, rec in zip(givens["items"], answer["items"]):
        kind = it["kind"]
        if rec["kind"] != kind:
            return False
        if kind == "symmetric_pair_origin":
            c3, c2, c1, c0 = sp.symbols("c3 c2 c1 c0")
            f = c3 * X ** 3 + c2 * X ** 2 + c1 * X + c0
            ax, ay, bx, by = (_sx(v) for v in (it["A"][0], it["A"][1], it["B"][0], it["B"][1]))
            # a different unknown set: general coefficients from O, A, B and "second derivative vanishes at the midpoint of A and B"
            sol = sp.solve([f.subs(X, 0), f.subs(X, ax) - ay, f.subs(X, bx) - by, sp.diff(f, X, 2).subs(X, (ax + bx) / 2)], [c3, c2, c1, c0], dict=True)
            if len(sol) != 1:
                return False
            g = f.subs(sol[0])
            if sp.expand(g - _sp_cubic([fr(v) for v in rec["f"]["coeffs"]])) != 0:
                return False
            if g.subs(X, _sx(it["C_x"])) != sp.Rational(rec["s"]["canonical"]):
                return False
            if sp.Rational(rec["center"]["x"]) != (ax + bx) / 2 or sp.Rational(rec["center"]["y"]) != (ay + by) / 2:
                return False
        elif kind == "center_zero_linear":
            cx, cy = _sx(it["center"][0]), _sx(it["center"][1])
            c3, c2, c1, c0 = sp.symbols("c3 c2 c1 c0")
            f = c3 * X ** 3 + c2 * X ** 2 + c1 * X + c0
            sol = sp.solve([f.subs(X, 0), c1, sp.diff(f, X, 2).subs(X, cx), f.subs(X, cx) - cy], [c3, c2, c1, c0], dict=True)
            if len(sol) != 1:
                return False
            g = f.subs(sol[0])
            if sp.expand(g - _sp_cubic([fr(v) for v in rec["f"]["coeffs"]])) != 0:
                return False
            if (sp.Rational(rec["landing"]["x"]), sp.Rational(rec["landing"]["y"])) != (2 * cx, g.subs(X, 2 * cx)):
                return False
        elif kind == "global_local":
            lead, m, n, h = (_sx(it[key]) for key in ("lead", "slope", "intercept", "h"))
            a, b, c = (sp.Rational(rec[key]["canonical"]) for key in ("a", "b", "c"))
            f = a * (X - h) ** 3 + b * (X - h) + c
            far = sp.limit(f / X ** 3, X, sp.oo)
            if far != lead or sp.diff(f, X).subs(X, h) != m or f.subs(X, h) != m * h + n:
                return False
        else:
            return False
    return True


# --- 3. cubic_statements ---------------------------------------------------------------------------------

def _subject_coeffs(subject: dict[str, Any]) -> tuple[list[Fraction] | None, str]:
    """(coefficients, type).  ``free_cd`` leaves c1, c0 unknown: the truth of every statement must not depend on them."""
    stype = subject["type"]
    if stype == "form":
        return _from_form(*_form(subject)), stype
    if stype == "cubic":
        return _coeffs(subject["coeffs"]), stype
    if stype == "cubic_with_center":
        c3, c2, c1 = (fr(v) for v in subject["coeffs"])
        cx, cy = fr(subject["center"][0]), fr(subject["center"][1])
        if c3 == 0 or -c2 / (3 * c3) != cx:
            raise ValueError("centre_is_inconsistent_with_the_leading_coefficients")
        c0 = cy - _eval([c3, c2, c1, Fraction(0)], cx)
        return [c3, c2, c1, c0], stype
    if stype == "free_cd":
        c3, c2 = fr(subject["coeffs"][0]), fr(subject["coeffs"][1])
        if c3 == 0:
            raise ValueError("cubic_leading_coefficient_must_be_nonzero")
        return None, stype
    raise ValueError(f"unknown_cubic_subject:{stype}")


_FREE_SAMPLES = [(Fraction(0), Fraction(0)), (Fraction(3), Fraction(-7)), (Fraction(-5, 2), Fraction(11, 3))]
# statements whose truth is the same for every real c and d (the others need c, d and are refused for a ``free_cd`` subject)
_FREE_OK = {"value_attained", "x_axis_meets", "axis_of_symmetry", "center_on_curve_at", "symmetric_mean", "global_extremum", "point_shift_on_graph"}


def _check_free_allowed(st: dict[str, Any]) -> None:
    if st["kind"] not in _FREE_OK:
        raise ValueError(f"statement_depends_on_the_free_parameters:{st['kind']}")
    if st["kind"] == "x_axis_meets" and st["claim"] != "at_least_one":
        raise ValueError("free_parameters_only_decide_at_least_one_root")
    if st["kind"] == "symmetric_mean" and fr(st["x1"]) + fr(st["x2"]) != 2 * fr(st["xm"]):
        raise ValueError("symmetric_mean_needs_xm_to_be_the_midpoint_for_free_parameters")


def _round_half_up(q: Fraction, places: int) -> Fraction:
    d = Decimal(q.numerator) / Decimal(q.denominator)
    return fr(str(d.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)))


def _truth_for(c: list[Fraction], st: dict[str, Any]) -> bool:
    kind = st["kind"]
    a, p, h, k = _to_form(c)
    f = lambda x: _eval(c, fr(x))  # noqa: E731
    if kind == "value_attained":
        return st["claim"] == "exists"  # a cubic takes every real value (its range is R)
    if kind == "x_axis_meets":
        roots = len(set(sp.real_roots(sp.Poly(_sp_cubic(c), X))))
        return roots >= 1 if st["claim"] == "at_least_one" else roots <= 2
    if kind == "axis_of_symmetry":
        return False  # a cubic graph is point-symmetric, never mirror-symmetric
    if kind == "center_is":
        return (fr(st["x"]), fr(st["y"])) == (h, k)
    if kind == "center_on_curve_at":
        return fr(st["x"]) == h  # the centre (h, f(h)) lies on the curve by definition; only its abscissa can be wrong
    if kind == "symmetric_mean":
        xm, x1, x2 = fr(st["xm"]), fr(st["x1"]), fr(st["x2"])
        return f(xm) == (f(x1) + f(x2)) / 2
    if kind == "odd_function":
        return all(f(-x) == -f(x) for x in (Fraction(1), Fraction(2), Fraction(3, 2), Fraction(5)))
    if kind == "global_extremum":
        return st["claim"] == "none"  # a cubic has neither a global maximum nor a global minimum
    if kind == "local_line":
        x0, m, n = fr(st["x0"]), fr(st["m"]), fr(st["n"])
        slope = 3 * c[0] * x0 * x0 + 2 * c[1] * x0 + c[2]
        return slope == m and f(x0) == m * x0 + n
    if kind == "value_approx":
        return _round_half_up(f(fr(st["x"])), int(st["decimals"])) == fr(st["approx"])
    if kind == "translate_overlap":
        return (a, p) == (fr(st["a"]), fr(st["p"]))
    if kind == "point_shift_on_graph":
        return fr(st["dx"]) == 0 and fr(st["dy"]) == 0  # a cubic graph is not invariant under any nonzero translation
    if kind == "constant_claim":
        return fr(st["claimed"]) == fr(st["value"])
    raise ValueError(f"unknown_cubic_statement:{kind}")


def _statement_truth(subject: dict[str, Any], st: dict[str, Any]) -> bool:
    c, stype = _subject_coeffs(subject)
    if stype == "free_cd":
        _check_free_allowed(st)
        c3, c2 = fr(subject["coeffs"][0]), fr(subject["coeffs"][1])
        truths = {_truth_for([c3, c2, c1, c0], st) for c1, c0 in _FREE_SAMPLES}
        if len(truths) != 1:
            raise ValueError("statement_depends_on_the_free_parameters")
        return truths.pop()
    if st["kind"] == "constant_claim" and stype == "cubic_with_center":
        c3, c2, c1 = (fr(v) for v in subject["coeffs"])
        value = fr(subject["center"][1]) - _eval([c3, c2, c1, Fraction(0)], fr(subject["center"][0]))
        return fr(st["claimed"]) == value
    return _truth_for(c, st)


def cubic_statements(subject: dict[str, Any], statements: list[dict[str, Any]], mode: str = "select", **text: Any) -> dict[str, Any]:
    if mode not in ("select", "truth"):
        raise ValueError("mode_must_be_select_or_truth")
    if mode == "truth" and len(statements) != 1:
        raise ValueError("truth_mode_needs_exactly_one_statement")
    truths = [bool(_statement_truth(subject, st)) for st in statements]
    extra: dict[str, Any] = {}
    c, stype = _subject_coeffs(subject)
    if c is not None:
        extra = _record_form(c)
        if stype == "cubic_with_center":
            extra["c0"] = rrec(c[3])
    return {"mode": mode, "truths": truths, "selected": [i for i, t in enumerate(truths, start=1) if t], **extra}


def _sp_truth(subject: dict[str, Any], st: dict[str, Any]) -> bool:
    """Symbolic re-derivation (free parameters stay symbols)."""
    stype, kind = subject["type"], st["kind"]
    if stype == "free_cd":
        _check_free_allowed(st)
    if stype == "form":
        f = _sp_form(*(_sx(subject[key]) for key in ("a", "p", "h", "k")))
    elif stype == "cubic":
        f = _sp_cubic(_coeffs(subject["coeffs"]))
    elif stype == "cubic_with_center":
        c3, c2, c1 = (_sx(v) for v in subject["coeffs"])
        cx, cy = _sx(subject["center"][0]), _sx(subject["center"][1])
        c0 = sp.Symbol("c0")
        g = c3 * X ** 3 + c2 * X ** 2 + c1 * X + c0
        f = g.subs(c0, sp.solve(g.subs(X, cx) - cy, c0)[0])
    else:  # free_cd
        c3, c2 = (_sx(v) for v in subject["coeffs"])
        f = c3 * X ** 3 + c2 * X ** 2 + PARAM_C * X + PARAM_D
    is_free = stype == "free_cd"
    center_x = sp.solve(sp.diff(f, X, 2), X)[0]
    if kind == "value_attained":
        return (st["claim"] == "exists") == (sp.degree(f - _sx(st["value"]), X) % 2 == 1)  # an odd-degree equation always has a real root
    if kind == "x_axis_meets":
        if is_free:
            if st["claim"] != "at_least_one":
                raise ValueError("free_parameters_only_decide_at_least_one_root")
            return sp.degree(f, X) % 2 == 1
        n = len(set(sp.real_roots(sp.Poly(f, X))))
        return n >= 1 if st["claim"] == "at_least_one" else n <= 2
    if kind == "axis_of_symmetry":
        t = sp.Symbol("t", real=True)
        x0 = _sx(st["claimed_x"])
        return sp.expand(f.subs(X, x0 + t) - f.subs(X, x0 - t)) == 0
    if kind == "center_is":
        cy = f.subs(X, center_x)
        return sp.simplify(center_x - _sx(st["x"])) == 0 and sp.simplify(cy - _sx(st["y"])) == 0
    if kind == "center_on_curve_at":
        return sp.simplify(center_x - _sx(st["x"])) == 0
    if kind == "symmetric_mean":
        return sp.simplify(f.subs(X, _sx(st["xm"])) - (f.subs(X, _sx(st["x1"])) + f.subs(X, _sx(st["x2"]))) / 2) == 0
    if kind == "odd_function":
        return sp.expand(f.subs(X, -X) + f) == 0
    if kind == "global_extremum":
        up, down = sp.limit(f, X, sp.oo), sp.limit(f, X, -sp.oo)
        has_max = up != sp.oo and down != sp.oo  # a continuous function has a global maximum iff it is not unbounded above
        has_min = up != -sp.oo and down != -sp.oo
        return {"max": has_max, "min": has_min, "none": not has_max and not has_min}[st["claim"]]
    if kind == "local_line":
        x0 = _sx(st["x0"])
        return sp.simplify(sp.diff(f, X).subs(X, x0) - _sx(st["m"])) == 0 and sp.simplify(f.subs(X, x0) - (_sx(st["m"]) * x0 + _sx(st["n"]))) == 0
    if kind == "value_approx":
        value = f.subs(X, _sx(st["x"]))
        return sp.Rational(round_half_up_sympy(value, int(st["decimals"]))) == _sx(st["approx"])
    if kind == "translate_overlap":
        a, p = _sx(st["a"]), _sx(st["p"])
        g = a * (X - center_x) ** 3 + p * (X - center_x) + f.subs(X, center_x)
        return sp.expand(f - g) == 0 and sp.expand(sp.diff(f, X, 3) / 6 - a) == 0 and sp.simplify(sp.diff(f, X).subs(X, center_x) - p) == 0
    if kind == "point_shift_on_graph":
        dx, dy = _sx(st["dx"]), _sx(st["dy"])
        return sp.expand(f.subs(X, X - dx) + dy - f) == 0
    if kind == "constant_claim":
        if stype != "cubic_with_center":
            raise ValueError("constant_claim_needs_a_centre_subject")
        return _constant_claim_symbolic(subject, st)
    raise ValueError(kind)


def _constant_claim_symbolic(subject: dict[str, Any], st: dict[str, Any]) -> bool:
    c3, c2, c1 = (_sx(v) for v in subject["coeffs"])
    cx, cy = _sx(subject["center"][0]), _sx(subject["center"][1])
    return sp.simplify(c3 * cx ** 3 + c2 * cx ** 2 + c1 * cx + _sx(st["claimed"]) - cy) == 0


def round_half_up_sympy(value: sp.Expr, places: int) -> sp.Rational:
    scale = sp.Integer(10) ** places
    return sp.Rational(sp.floor(value * scale + sp.Rational(1, 2)), scale)


def _check_cubic_statements(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    subject, sts = givens["subject"], givens["statements"]
    if len(answer["truths"]) != len(sts):
        return False
    for st, truth in zip(sts, answer["truths"]):
        if st["kind"] == "x_axis_meets" and subject["type"] == "free_cd" and st["claim"] != "at_least_one":
            return False
        if bool(_sp_truth(subject, st)) != bool(truth):
            return False
    if answer["selected"] != [i for i, t in enumerate(answer["truths"], start=1) if t]:
        return False
    if answer["mode"] == "truth" and len(sts) != 1:
        return False
    return True


# --- 4. cubic_curve_matching -----------------------------------------------------------------------------

_SAMPLES = 61


def _curve_points(c: list[Fraction], x_range: tuple[float, float], y_limit: float) -> list[list[float]]:
    lo, hi = x_range
    pts = []
    for i in range(_SAMPLES):
        x = lo + (hi - lo) * i / (_SAMPLES - 1)
        y = float(_eval(c, Fraction(x).limit_denominator(10 ** 6)))
        if abs(y) <= y_limit:
            pts.append([round(x, 4), round(y, 4)])
    return pts


def cubic_curve_matching(kind: str, functions: list[dict[str, Any]], order: list[int], window: dict[str, Any],
                         reference: list[dict[str, Any]] | None = None, **text: Any) -> dict[str, Any]:
    """``functions[i]`` is drawn as curve Γ_(g+1) where ``order[g] == i``.  ``kind`` is ``match`` (name the Γ of each
    function) or ``compare`` (order the leading coefficients of y=a_i x^3 drawn as Γ_i)."""
    n = len(functions)
    if kind not in ("match", "compare"):
        raise ValueError("kind_must_be_match_or_compare")
    if sorted(order) != list(range(n)):
        raise ValueError("order_must_be_a_permutation")
    coeff_sets = [_coeffs(f["coeffs"]) for f in functions]
    if len({tuple(c) for c in coeff_sets}) != n:
        raise ValueError("functions_must_be_distinct")
    xr, yl = float(window["x"]), float(window["y"])
    gammas = []
    for g, fi in enumerate(order):
        pts = _curve_points(coeff_sets[fi], (-xr, xr), yl)
        if len(pts) < 14:
            raise ValueError("curve_is_mostly_outside_the_window")
        gammas.append({"gamma": g + 1, "function": fi, "points": pts})
    for g1, g2 in itertools.combinations(gammas, 2):  # every pair must be visibly different
        ys2 = {round(p[0], 4): p[1] for p in g2["points"]}
        if max((abs(p[1] - ys2[round(p[0], 4)]) for p in g1["points"] if round(p[0], 4) in ys2), default=0.0) < 0.6:
            raise ValueError("two_curves_are_visually_indistinguishable")
    rec: dict[str, Any] = {"kind": kind, "gammas": gammas, "window": {"x": xr, "y": yl}}
    if reference:  # extra curves drawn for orientation only (e.g. the black y = x^3 of the textbook figure)
        rec["reference"] = [{"coeffs": [frac_text(v) for v in _coeffs(r["coeffs"])], "points": _curve_points(_coeffs(r["coeffs"]), (-xr, xr), yl)} for r in reference]
    if kind == "match":
        rec["assignment"] = [order.index(i) + 1 for i in range(n)]  # function i -> gamma number
    else:
        a = [c[0] for c in coeff_sets]
        if len(set(a)) != n:
            raise ValueError("leading_coefficients_must_differ")
        ranking = sorted(range(n), key=lambda i: -a[i])  # indices in decreasing a
        gamma_of = [order.index(i) + 1 for i in range(n)]
        rec["ranking"] = [gamma_of[i] for i in ranking]
        rec["ranking_text"] = ">".join(f"a_{g}" for g in rec["ranking"])
        rec["assignment"] = gamma_of
    return rec


def _check_cubic_curve_matching(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    funcs = [_coeffs(f["coeffs"]) for f in givens["functions"]]
    gammas = answer["gammas"]
    if len(gammas) != len(funcs):
        return False
    # re-read the plotted curves: each Γ must coincide with exactly one function at its own sample points
    read: dict[int, int] = {}
    for g in gammas:
        fits = [i for i, c in enumerate(funcs)
                if all(abs(p[1] - float(_eval(c, Fraction(p[0]).limit_denominator(10 ** 6)))) < 2e-3 for p in g["points"])]
        if len(fits) != 1:
            return False
        read[g["gamma"]] = fits[0]
    if sorted(read.values()) != list(range(len(funcs))):
        return False
    assignment = [next(gn for gn, fi in read.items() if fi == i) for i in range(len(funcs))]
    if assignment != answer["assignment"]:
        return False
    for ref, given in zip(answer.get("reference") or [], givens.get("reference") or []):
        c = _coeffs(given["coeffs"])
        if any(abs(p[1] - float(_eval(c, Fraction(p[0]).limit_denominator(10 ** 6)))) > 2e-3 for p in ref["points"]):
            return False
    if answer["kind"] == "compare":
        values = [(float(funcs[read[g]][0]), g) for g in sorted(read)]  # a_g of curve Γ_g
        # a_g is also visible as the curve height at x = 1
        for a_g, g in values:
            if abs(float(_eval(funcs[read[g]], Fraction(1))) - a_g) > 1e-9:
                return False
        if [g for _a, g in sorted(values, key=lambda t: -t[0])] != answer["ranking"]:
            return False
    return True


# --- registry / entrypoint --------------------------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "cubic_center_form": (cubic_center_form, _check_cubic_center_form, ("items",)),
    "cubic_from_conditions": (cubic_from_conditions, _check_cubic_from_conditions, ("items",)),
    "cubic_statements": (cubic_statements, _check_cubic_statements, ("subject", "statements")),
    "cubic_curve_matching": (cubic_curve_matching, _check_cubic_curve_matching, ("kind", "functions", "order", "window")),
}
OPERATIONS = tuple(_OPERATIONS)


def build_cubic_graph_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_cubic_graph_operation:{operation}")
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
