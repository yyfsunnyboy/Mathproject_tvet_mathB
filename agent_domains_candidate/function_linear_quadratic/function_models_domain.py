"""Exact domain operations for general-high Mathematics 1, Unit 9 (一次與二次函數).

Domain key ``function.linear_quadratic``.  Every operation is one shared, source-agnostic implementation:
components pass *inputs only* (``constraints``); this module computes the canonical answer with exact
``Fraction`` / sympy arithmetic and each validator re-derives it by a different method (sympy solving,
``function_range`` / ``solve_univariate_inequality``, or high-precision numerics), never by calling the
same construction code again.  Polynomial text helpers are reused from the promoted
``algebra.polynomial_division`` package.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable

import sympy as sp

from core.domain.promoted.algebra_polynomial_division.polynomial_core import (
    fr, frac_latex, frac_text, poly, poly_latex, poly_plain,
)

DOMAIN_KEY = "function.linear_quadratic"
X = sp.Symbol("x", real=True)
K = sp.Symbol("k", real=True)


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


def _quad(c: Any) -> tuple[Fraction, Fraction, Fraction]:
    a, b, cc = (fr(v) for v in c)
    if a == 0:
        raise ValueError("leading_coefficient_must_be_nonzero")
    return a, b, cc


def _vertex(a: Fraction, b: Fraction, c: Fraction) -> tuple[Fraction, Fraction]:
    h = -b / (2 * a)
    return h, c - b * b / (4 * a)


def _qeval(q: tuple[Fraction, Fraction, Fraction], x: Fraction) -> Fraction:
    return q[0] * x * x + q[1] * x + q[2]


def _sq(q: tuple[Fraction, Fraction, Fraction]) -> sp.Expr:
    return _sx(q[0]) * X ** 2 + _sx(q[1]) * X + _sx(q[2])


def _num(spec: Any) -> sp.Expr:
    """A given number: int / "p/q" / "3.35" / {"sqrt": n} / {"pow": [b, e]}."""
    if isinstance(spec, dict):
        if "sqrt" in spec:
            return sp.sqrt(sp.Integer(int(spec["sqrt"])))
        if "pow" in spec:
            b, e = spec["pow"]
            return sp.Integer(int(b)) ** int(e)
        raise ValueError("unknown_number_spec")
    return _sx(spec)


def _expr_rec(e: sp.Expr) -> dict[str, Any]:
    e = sp.expand(sp.radsimp(sp.expand(e)))
    if e.is_Rational:
        return {**rrec(Fraction(int(e.p), int(e.q))), "radical": False}
    return {"kind": "radical", "canonical": str(e).replace("**", "^"), "latex": sp.latex(e), "radical": True, "canonical_text": str(e)}


# --- 1. solve_linear_functions ----------------------------------------------------------------------------

def _line_through(p1: Any, p2: Any) -> tuple[sp.Expr, sp.Expr]:
    (x1, y1), (x2, y2) = ((_num(v) for v in p1), (_num(v) for v in p2))
    if sp.simplify(x1 - x2) == 0:
        raise ValueError("vertical_line_not_a_function")
    m = sp.simplify((y2 - y1) / (x2 - x1))
    if m == 0:
        raise ValueError("constant_function_is_not_linear")
    return m, sp.simplify(y1 - m * x1)


def solve_linear_functions(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    out = []
    for it in items:
        kind = it["kind"]
        rec: dict[str, Any] = {"kind": kind}
        if kind == "two_points":
            m, b = _line_through(it["p1"], it["p2"])
            rec["f"] = prec([fr(str(m)), fr(str(b))])
            rec["slope"], rec["y_intercept"] = _expr_rec(m), _expr_rec(b)
            if "dx" in it:
                rec["delta"] = _expr_rec(m * _num(it["dx"]))
        elif kind == "value_at":
            m, b = _line_through(it["p1"], it["p2"])
            rec["value"] = _expr_rec(m * _num(it["x"]) + b)
            rec["ratio_check"] = None
        elif kind == "rate":
            x0, y0 = (_num(v) for v in it["p"])
            m = _num(it["dy"]) / _num(it["dx"])
            if m == 0:
                raise ValueError("constant_function_is_not_linear")
            rec["f"] = prec([fr(str(m)), fr(str(sp.simplify(y0 - m * x0)))])
            rec["slope"], rec["y_intercept"] = _expr_rec(m), _expr_rec(y0 - m * x0)
        elif kind == "solve_x":
            m, b = _line_through(it["p1"], it["p2"])
            rec["x"] = _expr_rec((_num(it["y"]) - b) / m)
        else:
            raise ValueError(f"unknown_linear_item:{kind}")
        out.append(rec)
    return {"items": out}


def _mp_line(p1: Any, p2: Any):
    import mpmath as mp

    mp.mp.dps = 50
    f = lambda s: mp.mpmathify(sp.N(_num(s), 50))  # noqa: E731
    (x1, y1), (x2, y2) = (f(p1[0]), f(p1[1])), (f(p2[0]), f(p2[1]))
    m = (y2 - y1) / (x2 - x1)
    return m, y1 - m * x1, f


def _check_solve_linear_functions(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    import mpmath as mp

    close = lambda a, b: abs(mp.mpf(a) - mp.mpf(b)) < mp.mpf(10) ** -30  # noqa: E731

    def val(rec):
        return mp.mpmathify(sp.N(sp.sympify(rec["canonical_text"] if rec.get("radical") else rec["canonical"], rational=True), 50))

    for it, rec in zip(givens["items"], answer["items"]):
        kind = it["kind"]
        if kind in ("two_points", "value_at", "solve_x"):
            m, b, f = _mp_line(it["p1"], it["p2"])
        if kind == "two_points":
            if not (close(val(rec["slope"]), m) and close(val(rec["y_intercept"]), b)):
                return False
            if "dx" in it and not close(val(rec["delta"]), m * f(it["dx"])):
                return False
        elif kind == "value_at":
            if not close(val(rec["value"]), m * f(it["x"]) + b):
                return False
        elif kind == "rate":
            x0, y0 = (mp.mpmathify(sp.N(_num(v), 50)) for v in it["p"])
            mm = mp.mpmathify(sp.N(_num(it["dy"]), 50)) / mp.mpmathify(sp.N(_num(it["dx"]), 50))
            if not (close(val(rec["slope"]), mm) and close(val(rec["y_intercept"]), y0 - mm * x0)):
                return False
        else:
            if not close(val(rec["x"]), (f(it["y"]) - b) / m):
                return False
    return len(answer["items"]) == len(givens["items"])


# --- 2. evaluate_function_statements ----------------------------------------------------------------------

def _line_ab(subject: dict[str, Any]) -> list[tuple[Fraction, Fraction]]:
    return [(fr(a), fr(b)) for a, b in subject["lines"]]


def _parabola(subject: dict[str, Any]) -> tuple[Fraction, Fraction, Fraction]:
    a, r1, r2 = fr(subject["a"]), fr(subject["root1"]), fr(subject["root2"])
    if a == 0 or r1 == r2:
        raise ValueError("parabola_needs_two_distinct_roots")
    return a, -a * (r1 + r2), a * r1 * r2


def _statement_truth(subject: dict[str, Any], st: dict[str, Any]) -> bool:
    kind, stype = st["kind"], subject["type"]
    if stype == "linear_points":
        m, b = _line_through(subject["p1"], subject["p2"])
        if kind == "value_is":
            return sp.simplify(m * _num(st["x"]) + b - _num(st["value"])) == 0
        if kind == "slope_positive":
            return bool(m > 0) == bool(st["positive"])
        if kind == "intercept_is":
            return sp.simplify(b - _num(st["value"])) == 0
        if kind == "slope_is_quotient":
            return sp.simplify(((m * _num(st["xa"]) + b) - (m * _num(st["xb"]) + b)) / (_num(st["xa"]) - _num(st["xb"])) - m) == 0
        if kind == "rate_is":
            return sp.simplify(m * _num(st["dx"]) - _num(st["dy"])) == 0
    if stype == "three_lines":
        ab = _line_ab(subject)
        i = int(st.get("i", 1)) - 1
        j = int(st.get("j", 1)) - 1
        if kind == "slope_sign":
            return (ab[i][0] > 0) == (st["sign"] == "+")
        if kind == "slope_greater":
            return ab[i][0] > ab[j][0]
        if kind == "intercept_sign":
            return (ab[i][1] > 0) == (st["sign"] == "+")
        if kind == "intercept_greater":
            return ab[i][1] > ab[j][1]
    if stype == "parabola" and kind == "negative_quantity":
        a, b, c = _parabola(subject)
        table = {"a": a, "b": b, "c": c, "D": b * b - 4 * a * c, "a-b+c": a - b + c, "a+b+c": a + b + c}
        return table[st["expr"]] < 0
    if stype == "generic":
        if kind == "linear_slope_claim":
            return fr(st["a"]) == fr(st["claimed"])
        if kind == "translation_claim":
            right = fr(st["amount"]) * (1 if st["direction"] == "right" else -1)
            return fr(st["claim_h"]) == right and fr(st["claim_k"]) == fr(st.get("up", 0))
        if kind == "axis_claim":
            p, q, p2, q2 = (fr(st[k]) for k in ("p", "q", "p2", "q2"))
            return -q / p == -q2 / p2
        if kind == "interval_max_claim":
            a, h, k = fr(st["a"]), fr(st["h"]), fr(st["k"])
            lo, hi = fr(st["lo"]), fr(st["hi"])
            cand = {lo: a * (lo - h) ** 2 + k, hi: a * (hi - h) ** 2 + k}
            if lo <= h <= hi:
                cand[h] = k
            best = max(cand, key=lambda t: cand[t])
            return cand[fr(st["claim_x"])] == cand[best] if fr(st["claim_x"]) in cand else False
        if kind == "intercept_claim":
            # every function has exactly one value at x=0 (a y-intercept); an x-intercept needs D >= 0 (may fail)
            return st["always"] == "y"
    raise ValueError(f"unknown_statement:{stype}:{kind}")


def evaluate_function_statements(subject: dict[str, Any], statements: list[dict[str, Any]], mode: str = "select", **text: Any) -> dict[str, Any]:
    if mode not in ("select", "truth"):
        raise ValueError("mode_must_be_select_or_truth")
    if mode == "truth" and len(statements) != 1:
        raise ValueError("truth_mode_needs_exactly_one_statement")
    truths = [bool(_statement_truth(subject, st)) for st in statements]
    extra: dict[str, Any] = {}
    if subject["type"] == "linear_points":
        m, b = _line_through(subject["p1"], subject["p2"])
        extra = {"slope": _expr_rec(m), "y_intercept": _expr_rec(b)}
    elif subject["type"] == "parabola":
        a, b, c = _parabola(subject)
        extra = {"abc": [frac_text(a), frac_text(b), frac_text(c)], "discriminant": frac_text(b * b - 4 * a * c)}
    return {"mode": mode, "truths": truths, "selected": [i for i, t in enumerate(truths, start=1) if t], **extra}


def _sp_truth(subject: dict[str, Any], st: dict[str, Any]) -> bool:
    kind, stype = st["kind"], subject["type"]
    if stype == "linear_points":
        (x1, y1), (x2, y2) = ((_num(v) for v in subject["p1"]), (_num(v) for v in subject["p2"]))
        f = sp.Function("f")
        sol = sp.solve([sp.Symbol("m") * x1 + sp.Symbol("b") - y1, sp.Symbol("m") * x2 + sp.Symbol("b") - y2], [sp.Symbol("m"), sp.Symbol("b")], dict=True)[0]
        m, b = sol[sp.Symbol("m")], sol[sp.Symbol("b")]
        g = lambda t: sp.nsimplify(m * t + b)  # noqa: E731
        if kind == "value_is":
            return g(_num(st["x"])) == sp.nsimplify(_num(st["value"]))
        if kind == "slope_positive":
            return (sp.N(m) > 0) == bool(st["positive"])
        if kind == "intercept_is":
            return sp.nsimplify(b) == sp.nsimplify(_num(st["value"]))
        if kind == "slope_is_quotient":
            return sp.simplify((g(_num(st["xa"])) - g(_num(st["xb"]))) / (_num(st["xa"]) - _num(st["xb"])) - m) == 0
        if kind == "rate_is":
            x0 = _num(st.get("x0", 0))
            return sp.simplify(g(x0 + _num(st["dx"])) - g(x0) - _num(st["dy"])) == 0
    if stype == "three_lines":
        ab = [(_sx(a), _sx(b)) for a, b in subject["lines"]]
        i, j = int(st.get("i", 1)) - 1, int(st.get("j", 1)) - 1
        return {
            "slope_sign": lambda: (ab[i][0] > 0) == (st["sign"] == "+"),
            "slope_greater": lambda: ab[i][0] - ab[j][0] > 0,
            "intercept_sign": lambda: (ab[i][1] > 0) == (st["sign"] == "+"),
            "intercept_greater": lambda: ab[i][1] - ab[j][1] > 0,
        }[kind]()
    if stype == "parabola":
        a, r1, r2 = _sx(subject["a"]), _sx(subject["root1"]), _sx(subject["root2"])
        expr = sp.expand(a * (X - r1) * (X - r2))
        pa, pb, pc = (expr.coeff(X, n) for n in (2, 1, 0))
        table = {"a": pa, "b": pb, "c": pc, "D": pb ** 2 - 4 * pa * pc, "a-b+c": expr.subs(X, -1), "a+b+c": expr.subs(X, 1)}
        return bool(table[st["expr"]] < 0)
    if kind == "linear_slope_claim":
        return sp.Eq(_sx(st["a"]), _sx(st["claimed"])) == sp.true
    if kind == "translation_claim":
        base = _sx(st["a"]) * X ** 2
        sign = 1 if st["direction"] == "right" else -1
        moved = sp.expand(base.subs(X, X - sign * _sx(st["amount"])) + _sx(st.get("up", 0)))
        claimed = sp.expand(_sx(st["a"]) * (X - _sx(st["claim_h"])) ** 2 + _sx(st["claim_k"]))
        return sp.expand(moved - claimed) == 0
    if kind == "axis_claim":
        p, q, p2, q2 = (_sx(st[k]) for k in ("p", "q", "p2", "q2"))
        h = sp.solve(sp.diff((p * X + q) ** 2 + _sx(st.get("r", 0)), X), X)[0]
        return sp.simplify(h + q2 / p2) == 0
    if kind == "interval_max_claim":
        f = _sx(st["a"]) * (X - _sx(st["h"])) ** 2 + _sx(st["k"])
        top = sp.calculus.util.maximum(f, X, sp.Interval(_sx(st["lo"]), _sx(st["hi"])))
        return sp.simplify(f.subs(X, _sx(st["claim_x"])) - top) == 0 and _sx(st["lo"]) <= _sx(st["claim_x"]) <= _sx(st["hi"])
    if kind == "intercept_claim":
        has_no_root = sp.solve(X ** 2 + 1, X, domain=sp.S.Reals) == []  # x^2+1 never meets the x-axis, f(0) always exists
        return bool(has_no_root) and st["always"] == "y"
    raise ValueError("unknown_statement")


def _check_evaluate_function_statements(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    truths = [bool(_sp_truth(givens["subject"], st)) for st in givens["statements"]]
    return truths == answer["truths"] and answer["selected"] == [i for i, t in enumerate(truths, start=1) if t]


# --- 3. complete_square_items -----------------------------------------------------------------------------

def complete_square_items(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    out = []
    for it in items:
        a, b, c = _quad(it["coeffs"])
        h, k = _vertex(a, b, c)
        out.append({"coeffs": [frac_text(a), frac_text(b), frac_text(c)], "a": rrec(a), "h": rrec(h), "k": rrec(k)})
    return {"items": out}


def _check_complete_square_items(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for it, rec in zip(givens["items"], answer["items"]):
        a, h, k = (sp.Rational(rec[n]["canonical"]) for n in ("a", "h", "k"))
        a0, b0, c0 = (_sx(v) for v in it["coeffs"])
        if sp.expand(a * (X - h) ** 2 + k - (a0 * X ** 2 + b0 * X + c0)) != 0:
            return False
    return len(answer["items"]) == len(givens["items"])


# --- 4. quadratic_vertex_axis -----------------------------------------------------------------------------

def quadratic_vertex_axis(coeffs: Any, **text: Any) -> dict[str, Any]:
    a, b, c = _quad(coeffs)
    h, k = _vertex(a, b, c)
    return {"vertex": pointrec(h, k), "axis": {"kind": "line", "text": f"x={frac_text(h)}"}, "opens": "up" if a > 0 else "down"}


def _check_quadratic_vertex_axis(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    f = _sq(_quad(givens["coeffs"]))
    crit = sp.solve(sp.diff(f, X), X)[0]
    return sp.Rational(answer["vertex"]["x"]) == crit and sp.Rational(answer["vertex"]["y"]) == f.subs(X, crit) \
        and answer["axis"]["text"] == f"x={frac_text(Fraction(int(crit.p), int(crit.q)))}"


# --- 5. quadratic_extrema ---------------------------------------------------------------------------------

def _extrema(q: tuple[Fraction, Fraction, Fraction], interval: Any) -> dict[str, tuple[Fraction, Fraction]]:
    a, b, c = q
    h, k = _vertex(a, b, c)
    if interval is None:
        return {"max": (h, k)} if a < 0 else {"min": (h, k)}
    lo, hi = fr(interval[0]), fr(interval[1])
    if lo >= hi:
        raise ValueError("empty_interval")
    cand = {lo: _qeval(q, lo), hi: _qeval(q, hi)}
    if lo <= h <= hi:
        cand[h] = k
    top = max(cand, key=lambda t: (cand[t], -t))
    low = min(cand, key=lambda t: (cand[t], t))
    return {"max": (top, cand[top]), "min": (low, cand[low])}


def quadratic_extrema(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    out = []
    for it in items:
        q = _quad(it["f"])
        ex = _extrema(q, it.get("interval"))
        values = []
        for ask in it["asks"]:
            which, what = ask.split("_") if "_" in ask else (ask, "value")
            if which not in ex:
                raise ValueError("extremum_does_not_exist")
            x, y = ex[which]
            values.append(rrec(y if what == "value" else x))
        out.append({"asks": list(it["asks"]), "values": values, "f": prec(list(q))})
    return {"items": out}


def _check_quadratic_extrema(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for it, rec in zip(givens["items"], answer["items"]):
        f = _sq(_quad(it["f"]))
        iv = it.get("interval")
        domain = sp.S.Reals if iv is None else sp.Interval(_sx(iv[0]), _sx(iv[1]))
        for ask, val in zip(it["asks"], rec["values"]):
            which, what = ask.split("_") if "_" in ask else (ask, "value")
            best = sp.calculus.util.maximum(f, X, domain) if which == "max" else sp.calculus.util.minimum(f, X, domain)
            got = sp.Rational(val["canonical"])
            if what == "value":
                if got != best:
                    return False
            else:
                if not (got in domain and sp.simplify(f.subs(X, got) - best) == 0):
                    return False
    return len(answer["items"]) == len(givens["items"])


# --- 6. quadratic_graph_transformations -------------------------------------------------------------------

def quadratic_graph_transformations(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    out = []
    for it in items:
        kind = it["kind"]
        if kind == "translate":
            a, b, c = _quad(it["f"])
            dx, dy = fr(it["right"]), fr(it["up"])
            # g(x) = a(x-dx)^2 + b(x-dx) + c + dy
            g = [a, b - 2 * a * dx, a * dx * dx - b * dx + c + dy]
            out.append({"kind": kind, "g": prec(g)})
        elif kind == "reflect_x":
            a, b, c = _quad(it["f"])
            out.append({"kind": kind, "g": prec([-a, -b, -c])})
        elif kind == "find_translation":
            fa, fb, fc = _quad(it["f"])
            ga, gb, gc = _quad(it["g"])
            if fa != ga:
                raise ValueError("graphs_are_not_congruent_by_translation")
            fh, fk = _vertex(fa, fb, fc)
            gh, gk = _vertex(ga, gb, gc)
            out.append({"kind": kind, "left": rrec(fh - gh), "up": rrec(gk - fk)})
        elif kind == "overlap":
            fa, fb, fc = _quad(it["f"])
            ga, gb, gc = _quad(it["g"])
            same = fa == ga
            if not same:
                raise ValueError("overlap_variant_must_be_congruent")
            fh, fk = _vertex(fa, fb, fc)
            gh, gk = _vertex(ga, gb, gc)
            out.append({"kind": kind, "possible": True, "right": rrec(gh - fh), "up": rrec(gk - fk)})
        else:
            raise ValueError(f"unknown_transformation:{kind}")
    return {"items": out}


def _check_quadratic_graph_transformations(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for it, rec in zip(givens["items"], answer["items"]):
        kind = it["kind"]
        if kind == "translate":
            f = _sq(_quad(it["f"]))
            moved = sp.expand(f.subs(X, X - _sx(it["right"])) + _sx(it["up"]))
            got = sp.Poly([sp.Rational(c) for c in rec["g"]["coeffs"]], X).as_expr()
            if sp.expand(moved - got) != 0:
                return False
        elif kind == "reflect_x":
            got = sp.Poly([sp.Rational(c) for c in rec["g"]["coeffs"]], X).as_expr()
            if sp.expand(-_sq(_quad(it["f"])) - got) != 0:
                return False
        else:
            f, g = _sq(_quad(it["f"])), _sq(_quad(it["g"]))
            right = sp.Rational(rec["right"]["canonical"]) if kind == "overlap" else -sp.Rational(rec["left"]["canonical"])
            up = sp.Rational(rec["up"]["canonical"])
            if sp.expand(f.subs(X, X - right) + up - g) != 0:
                return False
    return len(answer["items"]) == len(givens["items"])


# --- 7. quadratic_always_sign -----------------------------------------------------------------------------

def _coef(spec: Any) -> tuple[Fraction, Fraction]:
    """``c0 + c1*k`` as (c0, c1)."""
    if isinstance(spec, dict):
        return fr(spec.get("c", 0)), fr(spec.get("k", 0))
    return fr(spec), Fraction(0)


def _bound(lo: Fraction | None, hi: Fraction | None, lo_open: bool, hi_open: bool) -> dict[str, Any]:
    return {"lo": None if lo is None else frac_text(lo), "hi": None if hi is None else frac_text(hi)}


def quadratic_always_sign(a: Any, b: Any, c: Any, sign: str, **text: Any) -> dict[str, Any]:
    (a0, a1), (b0, b1), (c0, c1) = _coef(a), _coef(b), _coef(c)
    if b1 != 0 or (a1 != 0 and c1 != 0):
        raise ValueError("parameter_must_sit_in_a_or_c_only")
    if sign not in ("positive", "negative"):
        raise ValueError("sign_must_be_positive_or_negative")
    lo: Fraction | None = None
    hi: Fraction | None = None

    def apply(coeff0: Fraction, coeff1: Fraction, want_positive: bool) -> None:
        nonlocal lo, hi
        # coeff0 + coeff1*k  (> 0 if want_positive else < 0)
        if coeff1 == 0:
            if (coeff0 > 0) != want_positive or coeff0 == 0:
                raise ValueError("no_solution")
            return
        bound = -coeff0 / coeff1
        upper = (coeff1 > 0) != want_positive  # k < bound
        if upper:
            hi = bound if hi is None else min(hi, bound)
        else:
            lo = bound if lo is None else max(lo, bound)

    want = sign == "positive"
    apply(a0, a1, want)  # a > 0 (positive) / a < 0 (negative); constant a is checked as a sign condition
    # D = b^2 - 4ac < 0, linear in k
    d0, d1 = b0 * b0 - 4 * a0 * c0, -4 * (a0 * c1 + a1 * c0)
    if a1 != 0 and c1 != 0:
        raise ValueError("nonlinear_discriminant")
    apply(d0, d1, False)
    if lo is not None and hi is not None and lo >= hi:
        raise ValueError("no_solution")
    if lo is None and hi is None:
        raise ValueError("unbounded")
    if hi is not None and lo is None:
        text = f"k<{frac_text(hi)}"
    elif lo is not None and hi is None:
        text = f"k>{frac_text(lo)}"
    else:
        text = f"{frac_text(lo)}<k<{frac_text(hi)}"
    return {"region": {"kind": "region", "text": text, "lo": None if lo is None else frac_text(lo), "hi": None if hi is None else frac_text(hi)},
            "discriminant": {"d0": frac_text(d0), "d1": frac_text(d1)}}


def _check_quadratic_always_sign(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    def expr(spec):
        c0, c1 = _coef(spec)
        return _sx(c0) + _sx(c1) * K

    a, b, c = expr(givens["a"]), expr(givens["b"]), expr(givens["c"])
    disc = sp.expand(b ** 2 - 4 * a * c)

    def region(e, positive):
        if not e.free_symbols:
            return sp.S.Reals if ((e > 0) == positive and e != 0) else sp.S.EmptySet
        return sp.solve_univariate_inequality(e > 0 if positive else e < 0, K, relational=False, domain=sp.S.Reals)

    solved = sp.Intersection(region(disc, False), region(a, givens["sign"] == "positive"))
    rec = answer["region"]
    lo = sp.Rational(rec["lo"]) if rec["lo"] is not None else -sp.oo
    hi = sp.Rational(rec["hi"]) if rec["hi"] is not None else sp.oo
    return solved == sp.Interval.open(lo, hi)


# --- 8. solve_quadratic_applications ----------------------------------------------------------------------

def _poly_div(coeffs: list[Fraction], d: Fraction) -> list[Fraction]:
    return [c / d for c in coeffs]


def _app_tile(it: dict[str, Any]) -> dict[str, Any]:
    s = fr(it["side"])
    c1, c2, c3 = (fr(v) for v in it["costs"])
    # areas: ECF = x^2/2, ABE = s(s-x)/2, AEFD = s^2 - x^2/2 - s(s-x)/2
    a = c1 / 2 - c3 / 2
    b = -c2 * s / 2 + c3 * s / 2
    c = c2 * s * s / 2 + c3 * (s * s - s * s / 2)
    h, k = _vertex(a, b, c)
    if not 0 < h < s or a <= 0:
        raise ValueError("minimum_outside_the_valid_range")
    return {"cost": prec([a, b, c]), "x": rrec(h), "min": rrec(k)}


def _app_profit(it: dict[str, Any]) -> dict[str, Any]:
    f0, f1 = (fr(v) for v in it["cost"])
    rev = it["revenue"]
    if rev["mode"] == "table":
        (x1, y1), (x2, y2) = ((fr(v) for v in p) for p in rev["points"])
        # g(x) = a x^2 + b x:  a x_i + b = y_i / x_i
        d = x2 - x1
        a = (y2 / x2 - y1 / x1) / d
        b = y1 / x1 - a * x1
    else:
        a, b = fr(rev["a"]), fr(rev["b"])
    h = [a, b - f1, -f0]
    if a >= 0:
        raise ValueError("profit_must_have_a_maximum")
    x, m = _vertex(*h)
    return {"a": rrec(a), "b": rrec(b), "revenue": prec([a, b, 0]), "profit": prec(h), "x": rrec(x), "max": rrec(m)}


def _app_circles(it: dict[str, Any]) -> dict[str, Any]:
    d = fr(it["diameter"])
    # three circles with diameters x, d-2x, x: area / pi = (x^2 + (d-2x)^2 + x^2) / 4
    a, b, c = Fraction(6, 4), Fraction(-4, 4) * d, d * d / 4
    h, k = _vertex(a, b, c)
    if not 0 < h < d / 2:
        raise ValueError("minimum_outside_the_valid_range")
    return {"area_over_pi": prec([a, b, c]), "x": rrec(h), "min_over_pi": rrec(k)}


def _app_pens(it: dict[str, Any]) -> dict[str, Any]:
    n, total = int(it["pens"]), fr(it["fence"])
    # (n+1) cross fences of width w plus one wall-parallel side l:  (n+1) w + l = total;  area = w * l
    a, b = Fraction(-(n + 1)), total
    w, area = _vertex(a, b, Fraction(0))
    return {"width": rrec(w), "length": rrec(total - (n + 1) * w), "max_area": rrec(area)}


def _app_ball(it: dict[str, Any]) -> dict[str, Any]:
    a, b = fr(it["a"]), fr(it["b"])  # y = -a x^2 + b x
    h = fr(it["height"])
    disc = b * b - 4 * a * h
    if a <= 0 or disc < 0:
        raise ValueError("ball_never_reaches_that_height")
    r = sp.sqrt(sp.Rational(disc.numerator, disc.denominator))
    if not r.is_Rational:
        raise ValueError("height_times_must_be_rational")
    r = fr(str(r))
    times = sorted({(b - r) / (2 * a), (b + r) / (2 * a)})
    t_top, y_top = _vertex(-a, b, Fraction(0))
    return {"times": [rrec(t) for t in times], "flight": rrec(b / a), "top_time": rrec(t_top), "top_height": rrec(y_top)}


def _app_basket(it: dict[str, Any]) -> dict[str, Any]:
    xa, ya, y0, xh = (fr(it[k]) for k in ("apex_x", "apex_y", "start_y", "hoop_x"))
    a = (y0 - ya) / (xa * xa)
    if a >= 0:
        raise ValueError("parabola_must_open_down")
    return {"a": rrec(a), "hoop_height": rrec(a * (xh - xa) ** 2 + ya)}


def _app_fountain(it: dict[str, Any]) -> dict[str, Any]:
    n, land, r = (fr(it[k]) for k in ("nozzle", "land", "radius"))
    if land <= 2 * r:
        raise ValueError("disc_beyond_the_landing_point")
    a = -n / (land * land - 2 * land * r)
    k = n - a * r * r  # vertex height: f(0) = a r^2 + k = n
    return {"a": rrec(a), "peak": rrec(k), "above_nozzle": rrec(k - n)}


def _app_roots_intercept(it: dict[str, Any]) -> dict[str, Any]:
    p, q, r = (fr(it[k]) for k in ("root1", "root2", "y_intercept"))
    a = r / (p * q)
    f = [a, -a * (p + q), a * p * q]
    h, k = _vertex(*f)
    return {"f": prec(f), "vertex": pointrec(h, k)}


def _app_max_condition(it: dict[str, Any]) -> dict[str, Any]:
    p, m = fr(it["apex_x"]), fr(it["max_value"])
    a = sp.Symbol("a", real=True)
    sols = sp.solve(sp.Eq(sp.Integer(0), (_sx(p) ** 2) * a ** 2 + _sx(m) * a - 1), a)
    neg = [s for s in sols if s.is_Rational and s < 0]
    if len(neg) != 1:
        raise ValueError("need_exactly_one_rational_negative_root")
    av = fr(str(neg[0]))
    return {"a": rrec(av), "b": rrec(-2 * av * p), "c": rrec(1 / av)}


_APPS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "tile_cost": _app_tile, "profit": _app_profit, "circle_areas": _app_circles, "fenced_pens": _app_pens, "ball": _app_ball,
    "basket": _app_basket, "fountain": _app_fountain, "roots_intercept": _app_roots_intercept, "max_condition": _app_max_condition,
}


def solve_quadratic_applications(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    out = []
    for it in items:
        if it["kind"] not in _APPS:
            raise ValueError(f"unknown_application:{it['kind']}")
        out.append({"kind": it["kind"], **_APPS[it["kind"]](it)})
    return {"items": out}


def _sp_min_max(f: sp.Expr, lo: Any, hi: Any, want: str) -> tuple[sp.Expr, sp.Expr]:
    dom = sp.Interval(lo, hi)
    best = sp.calculus.util.minimum(f, X, dom) if want == "min" else sp.calculus.util.maximum(f, X, dom)
    arg = sp.solve(sp.Eq(f, best), X)
    return best, arg[0]


def _check_solve_quadratic_applications(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    R = lambda rec: sp.Rational(rec["canonical"])  # noqa: E731
    for it, rec in zip(givens["items"], answer["items"]):
        kind = it["kind"]
        if kind == "tile_cost":
            s = _sx(it["side"])
            c1, c2, c3 = (_sx(v) for v in it["costs"])
            ecf, abe = X ** 2 / 2, s * (s - X) / 2
            total = sp.expand(c1 * ecf + c2 * abe + c3 * (s ** 2 - ecf - abe))
            if sp.expand(total - sp.Poly([sp.Rational(c) for c in rec["cost"]["coeffs"]], X).as_expr()) != 0:
                return False
            best, arg = _sp_min_max(total, 0, s, "min")
            if (R(rec["x"]), R(rec["min"])) != (arg, best):
                return False
        elif kind == "profit":
            f = _sx(it["cost"][0]) + _sx(it["cost"][1]) * X
            rev = it["revenue"]
            if rev["mode"] == "table":
                a_, b_ = sp.symbols("a_ b_")
                (x1, y1), (x2, y2) = rev["points"]
                sol = sp.solve([a_ * _sx(x1) ** 2 + b_ * _sx(x1) - _sx(y1), a_ * _sx(x2) ** 2 + b_ * _sx(x2) - _sx(y2)], [a_, b_], dict=True)[0]
                g = sol[a_] * X ** 2 + sol[b_] * X
            else:
                g = _sx(rev["a"]) * X ** 2 + _sx(rev["b"]) * X
            if (R(rec["a"]), R(rec["b"])) != (g.coeff(X, 2), g.coeff(X, 1)):
                return False
            best = sp.calculus.util.maximum(g - f, X, sp.S.Reals)
            if R(rec["max"]) != best or sp.simplify((g - f).subs(X, R(rec["x"])) - best) != 0:
                return False
        elif kind == "circle_areas":
            d = _sx(it["diameter"])
            area = (X ** 2 + (d - 2 * X) ** 2 + X ** 2) / 4
            best, arg = _sp_min_max(area, 0, d / 2, "min")
            if (R(rec["x"]), R(rec["min_over_pi"])) != (arg, best):
                return False
        elif kind == "fenced_pens":
            n, total = int(it["pens"]), _sx(it["fence"])
            w = sp.Symbol("w", positive=True)
            area = w * (total - (n + 1) * w)
            best, arg = _sp_min_max(area.subs(w, X), 0, total / (n + 1), "max")
            if (R(rec["width"]), R(rec["max_area"])) != (arg, best):
                return False
        elif kind == "ball":
            a, b, h = _sx(it["a"]), _sx(it["b"]), _sx(it["height"])
            y = -a * X ** 2 + b * X
            if sorted(sp.solve(sp.Eq(y, h), X)) != sorted(R(t) for t in rec["times"]):
                return False
            if sorted(sp.solve(sp.Eq(y, 0), X))[-1] != R(rec["flight"]):
                return False
            if (R(rec["top_time"]), R(rec["top_height"])) != (sp.solve(sp.diff(y, X), X)[0], sp.calculus.util.maximum(y, X, sp.S.Reals)):
                return False
        elif kind == "basket":
            xa, ya, y0, xh = (_sx(it[k]) for k in ("apex_x", "apex_y", "start_y", "hoop_x"))
            a = sp.Symbol("a")
            sol = sp.solve(a * (0 - xa) ** 2 + ya - y0, a)[0]
            if R(rec["hoop_height"]) != sol * (xh - xa) ** 2 + ya:
                return False
        elif kind == "fountain":
            n, land, r = (_sx(it[k]) for k in ("nozzle", "land", "radius"))
            a, k_ = sp.symbols("a k_")
            sol = sp.solve([a * r ** 2 + k_ - n, a * (land - r) ** 2 + k_], [a, k_], dict=True)[0]
            if R(rec["peak"]) != sol[k_] or R(rec["above_nozzle"]) != sol[k_] - n:
                return False
        elif kind == "roots_intercept":
            p, q, r = (_sx(it[k]) for k in ("root1", "root2", "y_intercept"))
            a = sp.Symbol("a")
            f = sp.expand(sp.solve(a * p * q - r, a)[0] * (X - p) * (X - q))
            got = sp.Poly([sp.Rational(c) for c in rec["f"]["coeffs"]], X).as_expr()
            if sp.expand(f - got) != 0 or sp.Rational(rec["vertex"]["x"]) != sp.solve(sp.diff(f, X), X)[0]:
                return False
        elif kind == "max_condition":
            p, m = _sx(it["apex_x"]), _sx(it["max_value"])
            a, b, c = R(rec["a"]), R(rec["b"]), R(rec["c"])
            f = a * X ** 2 + b * X + c
            if not (a < 0 and sp.simplify(c - 1 / a) == 0 and sp.solve(sp.diff(f, X), X)[0] == p and f.subs(X, p) == m):
                return False
        else:
            return False
    return len(answer["items"]) == len(givens["items"])


# --- 9. graph_quadratic_functions (parabola drawing) ------------------------------------------------------

def _graph_range(items: list[tuple[Fraction, Fraction, Fraction]]) -> dict[str, int]:
    """Canvas range that shows every vertex and the curves up to |y| <= 10 (steep parabolas get a narrower x window)."""
    import math

    hs = [h for _a, h, _k in items]
    ks = [k for _a, _h, k in items]
    widths = []
    for a, _h, k in items:
        top = max(Fraction(10) - k, Fraction(4)) if a > 0 else max(k + 10, Fraction(4))
        widths.append(min(4, max(2, math.ceil(math.sqrt(float(top / abs(a)))))))
    w = max(widths)
    x0, x1 = math.floor(min(hs)) - w, math.ceil(max(hs)) + w
    ys = [float(a * (x - h) ** 2 + k) for a, h, k in items for x in (h - w, h + w)] + [float(k) for k in ks] + [0.0]
    y0, y1 = max(-10, math.floor(min(ys)) - 1), min(12, math.ceil(max(ys)) + 1)
    if y1 - y0 < 6:
        y1 = y0 + 6
    return {"x_min": x0, "x_max": x1, "y_min": y0, "y_max": y1}


def graph_quadratic_functions(items: list[dict[str, Any]], layout: str = "single", ask_vertex_axis: bool = False, **text: Any) -> dict[str, Any]:
    if layout not in ("single", "same_canvas", "separate"):
        raise ValueError("layout_must_be_single_same_canvas_or_separate")
    if layout == "single" and len(items) != 1:
        raise ValueError("single_layout_needs_exactly_one_function")
    if layout == "same_canvas" and len(items) < 2:
        raise ValueError("same_canvas_needs_several_functions")
    quads = []
    out_items = []
    for it in items:
        a, b, c = _quad(it["coeffs"])
        h, k = _vertex(a, b, c)
        quads.append((a, h, k))
        samples = [[frac_text(h + d), frac_text(a * d * d + k)] for d in (Fraction(-2), Fraction(-1), Fraction(0), Fraction(1), Fraction(2))]
        out_items.append({"coeffs": [frac_text(a), frac_text(b), frac_text(c)], "a": frac_text(a), "vertex": pointrec(h, k), "axis": {"kind": "line", "text": f"x={frac_text(h)}"},
                          "opens": "up" if a > 0 else "down", "points": samples})
    groups = [list(range(len(items)))] if layout in ("single", "same_canvas") else [[i] for i in range(len(items))]
    canvases = [{"members": g, "axis_range": _graph_range([quads[i] for i in g])} for g in groups]
    return {"items": out_items, "canvases": canvases, "layout": layout, "ask_vertex_axis": bool(ask_vertex_axis)}


def _check_graph_quadratic_functions(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    members = sorted(i for c in answer["canvases"] for i in c["members"])
    if members != list(range(len(givens["items"]))) or len(answer["items"]) != len(givens["items"]):
        return False
    if givens.get("layout", "single") == "same_canvas" and len(answer["canvases"]) != 1:
        return False
    if givens.get("layout", "single") == "separate" and len(answer["canvases"]) != len(givens["items"]):
        return False
    for it, rec in zip(givens["items"], answer["items"]):
        f = _sq(_quad(it["coeffs"]))
        crit = sp.solve(sp.diff(f, X), X)[0]
        if sp.Rational(rec["vertex"]["x"]) != crit or sp.Rational(rec["vertex"]["y"]) != f.subs(X, crit):
            return False
        if rec["axis"]["text"] != f"x={frac_text(Fraction(int(crit.p), int(crit.q)))}" or (rec["opens"] == "up") != bool(sp.Poly(f, X).LC() > 0):
            return False
        if any(f.subs(X, sp.Rational(x)) != sp.Rational(y) for x, y in rec["points"]):
            return False
    for canvas in answer["canvases"]:
        r = canvas["axis_range"]
        if r["x_min"] >= r["x_max"] or r["y_min"] >= r["y_max"]:
            return False
        for i in canvas["members"]:  # every vertex of the canvas is visible on it
            v = answer["items"][i]["vertex"]
            if not (r["x_min"] <= sp.Rational(v["x"]) <= r["x_max"] and r["y_min"] <= sp.Rational(v["y"]) <= r["y_max"]):
                return False
    return True


# --- registry / entrypoint --------------------------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "solve_linear_functions": (solve_linear_functions, _check_solve_linear_functions, ("items",)),
    "evaluate_function_statements": (evaluate_function_statements, _check_evaluate_function_statements, ("subject", "statements")),
    "complete_square_items": (complete_square_items, _check_complete_square_items, ("items",)),
    "quadratic_vertex_axis": (quadratic_vertex_axis, _check_quadratic_vertex_axis, ("coeffs",)),
    "quadratic_extrema": (quadratic_extrema, _check_quadratic_extrema, ("items",)),
    "quadratic_graph_transformations": (quadratic_graph_transformations, _check_quadratic_graph_transformations, ("items",)),
    "quadratic_always_sign": (quadratic_always_sign, _check_quadratic_always_sign, ("a", "b", "c", "sign")),
    "solve_quadratic_applications": (solve_quadratic_applications, _check_solve_quadratic_applications, ("items",)),
    "graph_quadratic_functions": (graph_quadratic_functions, _check_graph_quadratic_functions, ("items",)),
}
OPERATIONS = tuple(_OPERATIONS)


def build_function_models_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_function_models_operation:{operation}")
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
