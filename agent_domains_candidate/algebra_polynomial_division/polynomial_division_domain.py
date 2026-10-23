"""Exact domain operations for general-high Mathematics 1, Unit 8 (多項式的除法原理).

Domain key ``algebra.polynomial_division``.  Every operation is one shared, source-agnostic
implementation: components pass *inputs only* (``constraints``); this module computes the canonical
answer with exact ``Fraction`` arithmetic (long / synthetic division, remainder and factor theorem,
interpolation) and a validator re-derives it by an independent method (sympy ``div`` / ``rem`` /
``Poly`` arithmetic and sympy linear solving), never by calling the same construction code again.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any, Callable

import sympy as sp

from .polynomial_core import (
    LinearForm, deg, ev, fr, frac_text, interpolate, lf_divmod_remainder, lf_poly, norm, padd, pdivmod, pmul, poly,
    poly_latex, poly_plain, psub, pscale, root_of, shift_expand, solve_linear, synthetic,
)

DOMAIN_KEY = "algebra.polynomial_division"
X = sp.Symbol("x")


# --- records -----------------------------------------------------------------------------------------

def prec(p: list[Fraction]) -> dict[str, Any]:
    return {"kind": "poly", "coeffs": [frac_text(c) for c in p], "plain": poly_plain(p), "latex": poly_latex(p)}


def rrec(q: Fraction) -> dict[str, Any]:
    return {"kind": "rational", "canonical": frac_text(q)}


def _require(constraints: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in constraints]
    if missing:
        raise ValueError(f"givens_required:{','.join(missing)}")


# --- independent (sympy) helpers ---------------------------------------------------------------------

def _s(p: list[Fraction]) -> sp.Poly:
    return sp.Poly([sp.Rational(c.numerator, c.denominator) for c in p] or [0], X, domain="QQ")


def _sr(q: Any) -> sp.Rational:
    q = fr(q)
    return sp.Rational(q.numerator, q.denominator)


def _same(spoly: sp.Poly, p: list[Fraction]) -> bool:
    return sp.expand(spoly.as_expr() - _s(p).as_expr()) == 0


def _rec_poly(rec: dict[str, Any]) -> list[Fraction]:
    return poly(rec["coeffs"])


def _sdivmod(f: list[Fraction], g: list[Fraction]) -> tuple[sp.Poly, sp.Poly]:
    q, r = sp.div(_s(f), _s(g), X)
    return q, r


def _rational_roots(p: list[Fraction]) -> list[Fraction]:
    """Distinct rational roots via the rational root theorem (exact)."""
    if not p:
        raise ValueError("zero_polynomial")
    scale = math.lcm(*[c.denominator for c in p])
    ints = [int(c * scale) for c in p]
    zero_root = ints[-1] == 0
    while ints and ints[-1] == 0:
        ints.pop()
    roots: set[Fraction] = {Fraction(0)} if zero_root else set()
    if len(ints) > 1:
        lead, const = abs(ints[0]), abs(ints[-1])
        for a in _divisors(lead):
            for b in _divisors(const):
                for sign in (1, -1):
                    cand = Fraction(sign * b, a)
                    if ev(poly(ints), cand) == 0:
                        roots.add(cand)
    return sorted(roots)


def _divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def _factor_completely(p: list[Fraction]) -> tuple[Fraction, list[Fraction]]:
    """``p = lead * prod (x - r_i)`` over the rationals (raises if it does not split)."""
    roots: list[Fraction] = []
    rest = list(p)
    while deg(rest) > 0:
        found = _rational_roots(rest)
        if not found:
            raise ValueError("does_not_split_over_rationals")
        r = found[0]
        rest, rem = pdivmod(rest, poly([1, -r]))
        assert not rem
        roots.append(r)
    return rest[0], roots


def _linear_text(root: Fraction) -> str:
    if root.denominator == 1:
        return "x" if root == 0 else (f"x-{root.numerator}" if root > 0 else f"x+{-root.numerator}")
    a, b = root.denominator, -root.numerator  # a*x + b with b = -numerator
    return f"{a}x{'+' if b > 0 else '-'}{abs(b)}"


# --- A. polynomial_arithmetic_items ------------------------------------------------------------------

def _get(defs: dict[str, list[Fraction]], ref: Any) -> list[Fraction]:
    return defs[ref] if isinstance(ref, str) else poly(ref)


def polynomial_arithmetic_items(defs: dict[str, Any], items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    named = {k: poly(v) for k, v in defs.items()}
    results = []
    for item in items:
        kind = item["op"]
        f, g = _get(named, item["f"]), _get(named, item["g"])
        rec: dict[str, Any] = {"op": kind, "f": prec(f), "g": prec(g)}
        if kind == "add":
            rec["value"] = prec(padd(f, g))
        elif kind == "sub":
            rec["value"] = prec(psub(f, g))
        elif kind == "mul":
            rec["value"] = prec(pmul(f, g))
        elif kind in ("divide", "synthetic"):
            if deg(g) < 1:
                raise ValueError("divisor_must_be_nonconstant")
            if kind == "synthetic":
                if deg(g) != 1 or g[0] != 1:
                    raise ValueError("synthetic_division_needs_x_minus_c")
                q, r, rows = synthetic(f, -g[1])
                rec["table"] = {"root": frac_text(-g[1]), "rows": [[frac_text(c) for c in row] for row in rows]}
                rem = [r] if r else []
            else:
                q, rem = pdivmod(f, g)
            rec["quotient"], rec["remainder"] = prec(q), prec(norm(rem))
        else:
            raise ValueError(f"unknown_arithmetic_item:{kind}")
        results.append(rec)
    return {"items": results}


def _check_polynomial_arithmetic_items(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    named = {k: poly(v) for k, v in givens["defs"].items()}
    if len(answer["items"]) != len(givens["items"]):
        return False
    for item, rec in zip(givens["items"], answer["items"]):
        f, g = _get(named, item["f"]), _get(named, item["g"])
        sf, sg = _s(f), _s(g)
        kind = item["op"]
        if kind == "add":
            ok = _same(sf + sg, _rec_poly(rec["value"]))
        elif kind == "sub":
            ok = _same(sf - sg, _rec_poly(rec["value"]))
        elif kind == "mul":
            ok = _same(sf * sg, _rec_poly(rec["value"]))
        else:
            q, r = sp.div(sf, sg, X)
            q_rec, r_rec = _rec_poly(rec["quotient"]), _rec_poly(rec["remainder"])
            ok = _same(q, q_rec) and _same(r, r_rec) and _same(sg * _s(q_rec) + _s(r_rec), f)
            ok = ok and (r.is_zero or r.degree() < sg.degree())
        if not ok:
            return False
    return True


# --- B. evaluate_polynomial_statements ---------------------------------------------------------------

_TEST_POLYS = ([1, 0, 0, 3, 0, -2], [2, 0, 0, -1, 7], [1, 0, 1, 0])


def _subject(subject: dict[str, Any]) -> list[Fraction] | None:
    kind = subject["type"]
    if kind == "poly":
        return poly(subject["coeffs"])
    if kind == "dqr":
        return padd(pmul(poly(subject["divisor"]), poly(subject["quotient"])), poly(subject["remainder"]))
    if kind == "generic":
        return None
    raise ValueError(f"unknown_subject:{kind}")


def _statement_truth(f: list[Fraction] | None, st: dict[str, Any]) -> bool:
    kind = st["kind"]
    if kind in ("scaled_remainder_same", "scaled_quotient_same"):
        d, k = poly(st["divisor"]), fr(st["k"])
        if k == 0:
            raise ValueError("scale_must_be_nonzero")
        same = True
        for t in _TEST_POLYS:
            tp = poly(t)
            q1, r1 = pdivmod(tp, d)
            q2, r2 = pdivmod(tp, pscale(d, k))
            same = same and (r1 == r2 if kind == "scaled_remainder_same" else q1 == q2)
        return same
    if kind == "factor_product_from_zeros":
        zeros = {fr(z) for z in st["zeros"]}
        roots = [root_of(poly(c)) for c in st["factors"]]
        return len(set(roots)) == len(roots) and all(r in zeros for r in roots)
    if f is None:
        raise ValueError("statement_needs_subject_polynomial")
    if kind == "is_degree_poly" or kind == "deg_equals":
        return deg(f) == int(st["n"])
    if kind == "coeff_is":
        n = deg(f)
        c = f[n - int(st["power"])] if 0 <= int(st["power"]) <= n else Fraction(0)
        return c == fr(st["value"])
    if kind == "value_is":
        return ev(f, st["x"]) == fr(st["value"])
    d = poly(st["divisor"]) if "divisor" in st else None
    q, r = pdivmod(f, d) if d is not None else ([], [])
    if kind == "quotient_degree":
        return deg(q) == int(st["n"])
    if kind == "quotient_integer_coeffs":
        return all(c.denominator == 1 for c in q)
    if kind == "remainder_equals":
        return r == poly(st["claimed"])
    if kind == "quotient_equals":
        return q == poly(st["claimed"])
    if kind == "is_factor":
        return not r
    if kind in ("division_identity", "fraction_identity"):
        return padd(pmul(d, q), r) == f and (not r or deg(r) < deg(d))
    raise ValueError(f"unknown_statement_kind:{kind}")


def evaluate_polynomial_statements(subject: dict[str, Any], statements: list[dict[str, Any]], mode: str = "select", **text: Any) -> dict[str, Any]:
    if mode not in ("select", "truth"):
        raise ValueError("mode_must_be_select_or_truth")
    f = _subject(subject)
    truths = [_statement_truth(f, st) for st in statements]
    if mode == "truth" and len(statements) != 1:
        raise ValueError("truth_mode_needs_exactly_one_statement")
    return {"mode": mode, "truths": truths, "selected": [i for i, t in enumerate(truths, start=1) if t],
            "subject": prec(f) if f is not None else None}


def _sp_statement_truth(f: list[Fraction] | None, st: dict[str, Any]) -> bool:
    """Same truth values derived with sympy (never through the exact-division code above)."""
    kind = st["kind"]
    if kind in ("scaled_remainder_same", "scaled_quotient_same"):
        d, k = _s(poly(st["divisor"])), _sr(st["k"])
        verdicts = []
        for t in _TEST_POLYS:
            tp = _s(poly(t))
            q1, r1 = sp.div(tp, d, X)
            q2, r2 = sp.div(tp, d * k, X)
            verdicts.append(sp.expand(r1.as_expr() - r2.as_expr()) == 0 if kind == "scaled_remainder_same"
                            else sp.expand(q1.as_expr() - q2.as_expr()) == 0)
        return all(verdicts)
    if kind == "factor_product_from_zeros":
        zeros = {sp.nsimplify(_sr(z)) for z in st["zeros"]}
        roots = [sp.solve(_s(poly(c)).as_expr(), X)[0] for c in st["factors"]]
        return len(set(roots)) == len(roots) and all(r in zeros for r in roots)
    sf = _s(f)
    if kind in ("is_degree_poly", "deg_equals"):
        return sf.degree() == int(st["n"])
    if kind == "coeff_is":
        return sf.coeff_monomial(X ** int(st["power"])) == _sr(st["value"])
    if kind == "value_is":
        return sf.eval(_sr(st["x"])) == _sr(st["value"])
    d = _s(poly(st["divisor"]))
    q, r = sp.div(sf, d, X)
    if kind == "quotient_degree":
        return (not q.is_zero and q.degree() == int(st["n"])) or (q.is_zero and int(st["n"]) < 0)
    if kind == "quotient_integer_coeffs":
        return all(c.q == 1 for c in q.all_coeffs())
    if kind == "remainder_equals":
        return sp.expand(r.as_expr() - _s(poly(st["claimed"])).as_expr()) == 0
    if kind == "quotient_equals":
        return sp.expand(q.as_expr() - _s(poly(st["claimed"])).as_expr()) == 0
    if kind == "is_factor":
        return r.is_zero
    return sp.expand((d * q + r).as_expr() - sf.as_expr()) == 0 and (r.is_zero or r.degree() < d.degree())


def _check_evaluate_polynomial_statements(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    f = _subject(givens["subject"])
    sts = givens["statements"]
    truths = [_sp_statement_truth(f, st) for st in sts]
    return truths == answer["truths"] and answer["selected"] == [i for i, t in enumerate(truths, start=1) if t]


# --- C. solve_polynomial_parameters ------------------------------------------------------------------

def _pad_left(p: list[Fraction], n: int) -> list[Fraction]:
    return [Fraction(0)] * (n - len(p)) + list(p)


def solve_polynomial_parameters(form: str, params: list[str], f: Any, conditions: list[dict[str, Any]] | None = None,
                                d: Any = None, q: Any = None, r: Any = None, ask_quotient: bool = False, **text: Any) -> dict[str, Any]:
    names = list(params)
    F = lf_poly(f)
    rows: list[list[Fraction]] = []
    rhs: list[Fraction] = []

    def add_equation(form_: LinearForm, target: Fraction) -> None:
        rows.append([form_.get(n, Fraction(0)) for n in names])
        rhs.append(target - form_.const())

    if form == "division":
        for cond in conditions or []:
            g, want = poly(cond["divisor"]), poly(cond["remainder"])
            _quot, rem = lf_divmod_remainder(F, g)
            for lf, t in zip(rem, _pad_left(want, len(rem))):
                add_equation(lf, t)
    elif form == "identity":
        D, Q, R = lf_poly(d), poly(q), poly(r)
        prod: list[LinearForm] = [LinearForm() for _ in range(len(D) + len(Q) - 1)]
        for i, dc in enumerate(D):
            for j, qc in enumerate(Q):
                prod[i + j] = prod[i + j] + dc.scale(qc)
        n = max(len(F), len(prod), len(R))
        Fp = [LinearForm()] * (n - len(F)) + F
        Pp = [LinearForm()] * (n - len(prod)) + prod
        Rp = _pad_left(R, n)
        for a, b, c in zip(Fp, Pp, Rp):
            add_equation(a.sub(b), c)
    else:
        raise ValueError(f"unknown_parameter_form:{form}")
    sol = dict(zip(names, solve_linear(rows, rhs)))
    f_sub = norm([c.at(sol) for c in F])
    if deg(f_sub) != len(F) - 1:
        raise ValueError("parameter_value_degenerates_polynomial")
    out: dict[str, Any] = {"params": {k: frac_text(v) for k, v in sol.items()}, "f": prec(f_sub), "quotient": None}
    if form == "identity":
        D_sub = norm([c.at(sol) for c in lf_poly(d)])
        if deg(D_sub) != len(lf_poly(d)) - 1:
            raise ValueError("parameter_value_degenerates_divisor")
        out["divisor"] = prec(D_sub)
    elif ask_quotient:
        if not conditions or len(conditions) != 1:
            raise ValueError("quotient_needs_single_division_condition")
        out["quotient"] = prec(pdivmod(f_sub, poly(conditions[0]["divisor"]))[0])
    return out


def _check_solve_polynomial_parameters(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    names = list(givens["params"])
    sol = {n: _sr(answer["params"][n]) for n in names}

    def sub(coeffs: Any) -> sp.Poly:
        vals = [LinearForm.parse(c) for c in coeffs]
        return sp.Poly([sum((_sr(v) * (sol[k] if k else 1) for k, v in lf.items()), sp.Integer(0)) for lf in vals], X, domain="QQ")

    sf = sub(givens["f"])
    if not _same(sf, _rec_poly(answer["f"])):
        return False
    if givens["form"] == "division":
        for cond in givens["conditions"]:
            g = _s(poly(cond["divisor"]))
            q, r = sp.div(sf, g, X)
            if sp.expand(r.as_expr() - _s(poly(cond["remainder"])).as_expr()) != 0:
                return False
            if givens.get("ask_quotient") and len(givens["conditions"]) == 1 and not _same(q, _rec_poly(answer["quotient"])):
                return False
        return True
    sd = sub(givens["d"])
    return sp.expand((sd * _s(poly(givens["q"])) + _s(poly(givens["r"]))).as_expr() - sf.as_expr()) == 0 \
        and _same(sd, _rec_poly(answer["divisor"]))


# --- D. taylor_shift_expansion -----------------------------------------------------------------------

def _round_half_up(q: Fraction, digits: int) -> Fraction:
    scale = 10 ** digits
    return Fraction(math.floor(q * scale + Fraction(1, 2)), scale)


def taylor_shift_expansion(poly_coeffs: Any, center: Any, approx_x: Any, with_approx: bool = True, digits: int = 2, **text: Any) -> dict[str, Any]:
    f = poly(poly_coeffs)
    c = fr(center)
    coeffs = shift_expand(f, c)
    out: dict[str, Any] = {"coefficients": [frac_text(a) for a in coeffs], "center": frac_text(c), "approx": None}
    if with_approx:
        h = fr(approx_x) - c
        exact = ev(f, approx_x)
        truncated = coeffs[-1] + coeffs[-2] * h
        if _round_half_up(exact, digits) != _round_half_up(truncated, digits):
            raise ValueError("first_order_truncation_disagrees_with_exact_rounding")
        out["approx"] = frac_text(_round_half_up(exact, digits))
        out["exact_value"] = frac_text(exact)
    return out


def _check_taylor_shift_expansion(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    f = _s(poly(givens["poly_coeffs"]))
    c = _sr(givens["center"])
    coeffs = [_sr(a) for a in answer["coefficients"]]
    n = len(coeffs) - 1
    rebuilt = sum(a * (X - c) ** (n - i) for i, a in enumerate(coeffs))
    if sp.expand(rebuilt - f.as_expr()) != 0:
        return False
    if givens.get("with_approx", True):
        digits = int(givens.get("digits", 2))
        value = f.eval(_sr(givens["approx_x"]))
        if sp.floor(value * 10 ** digits + sp.Rational(1, 2)) / 10 ** digits != _sr(answer["approx"]):
            return False
    return True


# --- E. evaluate_polynomial_values -------------------------------------------------------------------

def evaluate_polynomial_values(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    values = []
    for it in items:
        f, kind = poly(it["poly"]), it["kind"]
        if kind in ("value", "expression"):
            v = ev(f, it["x"])
        elif kind == "remainder_linear":
            v = ev(f, root_of(poly(it["divisor"])))
        else:
            raise ValueError(f"unknown_value_item:{kind}")
        values.append(rrec(v))
    return {"values": values}


def _check_evaluate_polynomial_values(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for it, rec in zip(givens["items"], answer["values"]):
        sf = _s(poly(it["poly"]))
        if it["kind"] == "remainder_linear":
            want = sp.rem(sf, _s(poly(it["divisor"])), X).as_expr()
        else:
            want = sf.eval(_sr(it["x"]))
        if sp.nsimplify(want) != _sr(rec["canonical"]):
            return False
    return len(answer["values"]) == len(givens["items"])


# --- F. solve_remainder_from_conditions --------------------------------------------------------------

def solve_remainder_from_conditions(conditions: list[dict[str, Any]], target: Any, **text: Any) -> dict[str, Any]:
    t = poly(target)
    if deg(t) != 2:
        raise ValueError("quadratic_target_required")
    roots = _rational_roots(t)
    if len(roots) != 2:
        raise ValueError("target_needs_two_distinct_rational_roots")
    values = []
    for c in roots:
        seen = {ev(poly(cond["remainder"]), c) for cond in conditions if ev(poly(cond["divisor"]), c) == 0}
        if len(seen) != 1:
            raise ValueError("root_value_undetermined")
        values.append(seen.pop())
    r = interpolate(list(zip(roots, values)))
    return {"remainder": prec(r), "roots": [frac_text(c) for c in roots], "values": [frac_text(v) for v in values]}


def _check_solve_remainder_from_conditions(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    conds = givens["conditions"]
    total = sum(deg(poly(c["divisor"])) for c in conds)
    unknown = sp.symbols(f"u0:{total}")
    f = sum(u * X ** i for i, u in enumerate(unknown))
    equations = []
    for cond in conds:
        rem = sp.rem(f, _s(poly(cond["divisor"])).as_expr(), X)
        diff = sp.Poly(sp.expand(rem - _s(poly(cond["remainder"])).as_expr()), X)
        equations += list(diff.all_coeffs())
    sol = sp.solve(equations, unknown, dict=True)
    if len(sol) != 1:
        return False
    f_sol = sp.expand(f.subs(sol[0]))
    rem = sp.rem(f_sol, _s(poly(givens["target"])).as_expr(), X)
    return sp.expand(rem - _s(_rec_poly(answer["remainder"])).as_expr()) == 0


# --- G1. solve_polynomial_from_remainder_congruences ------------------------------------------------

def solve_polynomial_from_remainder_congruences(degree: int, conditions: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    n = int(degree)
    rows: list[list[Fraction]] = []
    rhs: list[Fraction] = []
    for cond in conditions:
        g, want = poly(cond["divisor"]), poly(cond["remainder"])
        m = deg(g)
        basis = [_pad_left(pdivmod(poly([1] + [0] * k), g)[1], m) for k in range(n, -1, -1)]  # x^n .. x^0
        for j, target in enumerate(_pad_left(want, m)):
            rows.append([basis[k][j] for k in range(n + 1)])
            rhs.append(target)
    sol = norm(solve_linear(rows, rhs))
    if deg(sol) != n:
        raise ValueError("solution_degree_mismatch")
    return {"f": prec(sol)}


def _check_solve_polynomial_from_remainder_congruences(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    f = _s(_rec_poly(answer["f"]))
    if f.degree() != int(givens["degree"]):
        return False
    for cond in givens["conditions"]:
        rem = sp.rem(f, _s(poly(cond["divisor"])), X)
        if sp.expand(rem.as_expr() - _s(poly(cond["remainder"])).as_expr()) != 0:
            return False
    return True


# --- G2. solve_remainder_with_linear_part ------------------------------------------------------------

def solve_remainder_with_linear_part(roots: list[Any], k: Any, first_value: Any, last_value: Any, **text: Any) -> dict[str, Any]:
    r1, r2, r3 = (fr(r) for r in roots)
    if len({r1, r2, r3}) != 3:
        raise ValueError("three_distinct_roots_required")
    k = fr(k)
    lead = pmul(poly([1, -r1]), poly([1, -r2]))
    # f(r1) = g(r1);  f(r3) = k(r3-r1)(r3-r2) + g(r3)
    g = interpolate([(r1, fr(first_value)), (r3, fr(last_value) - k * (r3 - r1) * (r3 - r2))])
    if deg(g) != 1:
        raise ValueError("g_must_be_linear")
    full = padd(pscale(lead, k), g)
    return {"g": prec(g), "remainder_mod_quadratic": prec(pdivmod(full, lead)[1]), "full_remainder": prec(full)}


def _check_solve_remainder_with_linear_part(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    r1, r2, r3 = (_sr(r) for r in givens["roots"])
    k = _sr(givens["k"])
    g = _s(_rec_poly(answer["g"]))
    if g.degree() != 1:
        return False
    full = k * (X - r1) * (X - r2) + g.as_expr()
    if sp.expand(sp.Poly(full, X).as_expr() - _s(_rec_poly(answer["full_remainder"])).as_expr()) != 0:
        return False
    cubic = sp.Poly((X - r1) * (X - r2) * (X - r3), X)
    f = cubic * sp.Poly(X ** 2 + 3, X) + sp.Poly(full, X)  # any dividend with that remainder
    ok = f.eval(r1) == _sr(givens["first_value"]) and f.eval(r3) == _sr(givens["last_value"]) + 0 * r3
    rem2 = sp.rem(f, sp.Poly((X - r1) * (X - r2), X), X)
    return ok and sp.expand(rem2.as_expr() - _s(_rec_poly(answer["remainder_mod_quadratic"])).as_expr()) == 0


# --- H. interpolate_polynomials ----------------------------------------------------------------------

def interpolate_polynomials(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    out = []
    for it in items:
        pts = [(fr(x), fr(y)) for x, y in it["points"]]
        if len(pts) != int(it["degree"]) + 1:
            raise ValueError("point_count_must_be_degree_plus_one")
        f = interpolate(pts)
        if deg(f) != int(it["degree"]):
            raise ValueError("interpolant_degree_mismatch")
        out.append(prec(f))
    return {"polys": out}


def _check_interpolate_polynomials(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for it, rec in zip(givens["items"], answer["polys"]):
        f = _s(_rec_poly(rec))
        if f.degree() != int(it["degree"]):
            return False
        for x, y in it["points"]:
            if f.eval(_sr(x)) != _sr(y):
                return False
    return len(answer["polys"]) == len(givens["items"])


# --- I. select_linear_factors ------------------------------------------------------------------------

def select_linear_factors(poly_coeffs: Any, candidates: list[Any], **text: Any) -> dict[str, Any]:
    f = poly(poly_coeffs)
    truths = []
    for cand in candidates:
        d = poly(cand)
        truths.append(ev(f, root_of(d)) == 0)
    return {"truths": truths, "selected": [i for i, t in enumerate(truths, start=1) if t], "poly": prec(f)}


def _check_select_linear_factors(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    sf = _s(poly(givens["poly_coeffs"]))
    truths = [sp.rem(sf, _s(poly(c)), X).is_zero for c in givens["candidates"]]
    return truths == answer["truths"] and answer["selected"] == [i for i, t in enumerate(truths, start=1) if t]


# --- J. solve_erased_cubic ---------------------------------------------------------------------------

def solve_erased_cubic(known: list[Any], root: Any, **text: Any) -> dict[str, Any]:
    lead = poly(list(known) + [0])
    r = fr(root)
    if len(known) != 3:
        raise ValueError("cubic_with_erased_constant_required")
    k = -ev(lead, r)
    cubic = padd(lead, norm([k]))
    constant, roots = _factor_completely(cubic)
    if r not in roots:
        raise ValueError("given_root_not_a_root")
    factors = sorted(roots)
    plain = ("" if constant == 1 else (f"{frac_text(constant)}" if constant.denominator == 1 else f"({frac_text(constant)})"))
    plain += "".join(f"({_linear_text(root_)})" for root_ in factors)
    return {"k": frac_text(k), "poly": prec(cubic), "constant": frac_text(constant), "roots": [frac_text(x) for x in factors],
            "factored_plain": plain}


def _check_solve_erased_cubic(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    lead = _s(poly(list(givens["known"]) + [0]))
    k = _sr(answer["k"])
    cubic = lead.as_expr() + k
    if not sp.rem(sp.Poly(cubic, X), sp.Poly(X - _sr(givens["root"]), X), X).is_zero:
        return False
    if sp.expand(sp.Poly(cubic, X).as_expr() - _s(_rec_poly(answer["poly"])).as_expr()) != 0:
        return False
    const, factors = sp.factor_list(cubic, X)
    roots = sorted(sp.solve(sp.Poly(cubic, X).as_expr(), X))
    return all(sp.Poly(f, X).degree() == 1 for f, _m in factors) and [sp.nsimplify(_sr(r)) for r in answer["roots"]] == roots


# --- K. solve_masked_synthetic_coefficient -----------------------------------------------------------

def solve_masked_synthetic_coefficient(coefficients: list[Any], mask_index: int, root: Any, remainder: Any, **text: Any) -> dict[str, Any]:
    idx = int(mask_index)
    n = len(coefficients) - 1
    if coefficients[idx] is not None:
        raise ValueError("mask_position_must_be_null")
    r = fr(root)
    known = sum((fr(c) * r ** (n - i) for i, c in enumerate(coefficients) if i != idx), Fraction(0))
    weight = r ** (n - idx)
    if weight == 0:
        raise ValueError("mask_cannot_be_recovered_when_root_is_zero")
    value = (fr(remainder) - known) / weight
    full = [value if i == idx else fr(c) for i, c in enumerate(coefficients)]
    _q, rem, rows = synthetic(full, r)
    if rem != fr(remainder):
        raise ValueError("synthetic_remainder_mismatch")
    return {"value": rrec(value), "full": [frac_text(c) for c in full], "rows": [[frac_text(c) for c in row] for row in rows]}


def _check_solve_masked_synthetic_coefficient(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    idx = int(givens["mask_index"])
    a = _sr(answer["value"]["canonical"])
    full = [a if i == idx else _sr(c) for i, c in enumerate(givens["coefficients"])]
    f = sp.Poly(full, X, domain="QQ")
    return sp.rem(f, sp.Poly(X - _sr(givens["root"]), X), X).as_expr() == _sr(givens["remainder"]) \
        and [frac_text(fr(str(c))) for c in full] == answer["full"]


# --- M. solve_divisor_from_quotient_remainder --------------------------------------------------------

def solve_divisor_from_quotient_remainder(dividend: Any, quotient: Any, remainder: Any, **text: Any) -> dict[str, Any]:
    f, q, r = poly(dividend), poly(quotient), poly(remainder)
    g, rem = pdivmod(psub(f, r), q)
    if rem or deg(g) < 1 or (r and deg(r) >= deg(g)):
        raise ValueError("no_valid_divisor")
    return {"divisor": prec(g)}


def _check_solve_divisor_from_quotient_remainder(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    g = _s(_rec_poly(answer["divisor"]))
    q, r = sp.div(_s(poly(givens["dividend"])), g, X)
    return sp.expand(q.as_expr() - _s(poly(givens["quotient"])).as_expr()) == 0 \
        and sp.expand(r.as_expr() - _s(poly(givens["remainder"])).as_expr()) == 0 and (r.is_zero or r.degree() < g.degree())


# --- registry / entrypoint ---------------------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "polynomial_arithmetic_items": (polynomial_arithmetic_items, _check_polynomial_arithmetic_items, ("defs", "items")),
    "evaluate_polynomial_statements": (evaluate_polynomial_statements, _check_evaluate_polynomial_statements, ("subject", "statements")),
    "solve_polynomial_parameters": (solve_polynomial_parameters, _check_solve_polynomial_parameters, ("form", "params", "f")),
    "taylor_shift_expansion": (taylor_shift_expansion, _check_taylor_shift_expansion, ("poly_coeffs", "center", "approx_x")),
    "evaluate_polynomial_values": (evaluate_polynomial_values, _check_evaluate_polynomial_values, ("items",)),
    "solve_remainder_from_conditions": (solve_remainder_from_conditions, _check_solve_remainder_from_conditions, ("conditions", "target")),
    "solve_polynomial_from_remainder_congruences": (solve_polynomial_from_remainder_congruences, _check_solve_polynomial_from_remainder_congruences, ("degree", "conditions")),
    "solve_remainder_with_linear_part": (solve_remainder_with_linear_part, _check_solve_remainder_with_linear_part, ("roots", "k", "first_value", "last_value")),
    "interpolate_polynomials": (interpolate_polynomials, _check_interpolate_polynomials, ("items",)),
    "select_linear_factors": (select_linear_factors, _check_select_linear_factors, ("poly_coeffs", "candidates")),
    "solve_erased_cubic": (solve_erased_cubic, _check_solve_erased_cubic, ("known", "root")),
    "solve_masked_synthetic_coefficient": (solve_masked_synthetic_coefficient, _check_solve_masked_synthetic_coefficient, ("coefficients", "mask_index", "root", "remainder")),
    "solve_divisor_from_quotient_remainder": (solve_divisor_from_quotient_remainder, _check_solve_divisor_from_quotient_remainder, ("dividend", "quotient", "remainder")),
}
OPERATIONS = tuple(_OPERATIONS)


def build_polynomial_division_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_polynomial_division_operation:{operation}")
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


# --- validators (never raise) ------------------------------------------------------------------------

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
