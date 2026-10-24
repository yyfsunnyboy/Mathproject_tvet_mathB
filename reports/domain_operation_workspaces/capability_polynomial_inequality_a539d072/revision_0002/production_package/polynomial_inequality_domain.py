"""Exact domain operations for general-high Mathematics 1, Unit 11 (多項式不等式).

Domain key ``inequality.polynomial``.  Components pass *inputs only*; every answer is computed with exact sympy
arithmetic by a sign chart (factor over Q, exact real roots, sign of the polynomial at a rational point of every
interval) and each validator re-derives it differently (``solve_univariate_inequality``, coefficient matching and
solving, brute checks at sample values, or re-reading the plotted curve), never by calling the same construction twice.

Solution sets are returned in the syntax of the shared ``inequality_solution_checker``
(``1<x<3 or x>=5``, ``x=2``, ``全體實數``, ``無解``) plus LaTeX for display.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable

import sympy as sp

DOMAIN_KEY = "inequality.polynomial"
X = sp.Symbol("x", real=True)
K = sp.Symbol("k", real=True)
RELS = (">", "<", ">=", "<=")


# --- helpers ----------------------------------------------------------------------------------------------

def _q(v: Any) -> sp.Rational:
    if isinstance(v, bool):
        raise ValueError("bool_is_not_a_number")
    if isinstance(v, sp.Basic):
        return sp.nsimplify(v, rational=True)
    text = str(v).strip()
    if "sqrt" in text:  # exact radical coefficient such as -2*sqrt(3)
        return sp.sympify(text)
    f = Fraction(text)
    return sp.Rational(f.numerator, f.denominator)


def _require(constraints: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in constraints]
    if missing:
        raise ValueError(f"givens_required:{','.join(missing)}")


def _poly_expr(coeffs: list[Any], var: sp.Symbol = X) -> sp.Expr:
    n = len(coeffs) - 1
    return sum((_q(c) * var ** (n - i) for i, c in enumerate(coeffs)), sp.Integer(0))


def _factor_expr(factor: dict[str, Any], var: sp.Symbol = X) -> sp.Expr:
    base = _poly_expr(factor["lin"], var) if "lin" in factor else _poly_expr(factor["quad"], var)
    return base ** int(factor.get("mult", 1))


def _side_expr(side: dict[str, Any], var: sp.Symbol = X) -> sp.Expr:
    """A side is ``{"poly": [coeffs]}`` or ``{"coef": c, "factors": [{"lin"|"quad": [...], "mult": m}, ...]}``."""
    if "poly" in side:
        return _poly_expr(side["poly"], var)
    out = _q(side.get("coef", 1))
    for factor in side["factors"]:
        out = out * _factor_expr(factor, var)
    return out


def _rel(expr: sp.Expr, rel: str) -> sp.Expr:
    return {">": sp.StrictGreaterThan, "<": sp.StrictLessThan, ">=": sp.GreaterThan, "<=": sp.LessThan}[rel](expr, 0)


# --- set <-> text -----------------------------------------------------------------------------------------

def _ep_text(v: sp.Expr) -> str:
    v = sp.nsimplify(v) if not v.is_Rational else v
    if v.is_Rational:
        return str(v)
    return "(" + sp.sstr(sp.radsimp(v)).replace(" ", "") + ")"


def _ep_latex(v: sp.Expr) -> str:
    return sp.latex(sp.radsimp(v))


def _pieces(s: sp.Set) -> list[sp.Set]:
    if s == sp.S.EmptySet:
        return []
    if isinstance(s, sp.Union):
        parts: list[sp.Set] = []
        for arg in s.args:
            parts.extend(_pieces(arg))
        return sorted(parts, key=lambda p: float(p.inf if not isinstance(p, sp.FiniteSet) else min(p.args)))
    if isinstance(s, sp.FiniteSet):
        return [sp.FiniteSet(a) for a in sorted(s.args, key=float)]
    return [s]


def _piece_text(p: sp.Set, tex: bool = False) -> str:
    ep = _ep_latex if tex else _ep_text
    le, ge, lt, gt = ("\\le ", "\\ge ", "<", ">") if tex else ("<=", ">=", "<", ">")
    if isinstance(p, sp.FiniteSet):
        return f"x={ep(p.args[0])}"
    lo, hi = p.inf, p.sup
    if lo == -sp.oo:
        return f"x{lt if p.right_open else le}{ep(hi)}"
    if hi == sp.oo:
        return f"x{gt if p.left_open else ge}{ep(lo)}"
    return f"{ep(lo)}{lt if p.left_open else le}x{lt if p.right_open else le}{ep(hi)}"


def set_text(s: sp.Set) -> str:
    if s == sp.S.Reals:
        return "全體實數"
    if s == sp.S.EmptySet:
        return "無解"
    return " or ".join(_piece_text(p) for p in _pieces(s))


def set_latex(s: sp.Set) -> str:
    if s == sp.S.Reals:
        return "\\text{全體實數}"
    if s == sp.S.EmptySet:
        return "\\text{無解}"
    return "\\text{ 或 }".join(_piece_text(p, tex=True) for p in _pieces(s))


def set_record(s: sp.Set) -> dict[str, Any]:
    return {"canonical": set_text(s), "latex": set_latex(s)}


# --- the sign-chart solver (primary derivation) -----------------------------------------------------------

def real_roots(expr: sp.Expr, var: sp.Symbol = X) -> list[sp.Expr]:
    """Distinct real roots in increasing order (every irreducible factor over Q has degree <= 2)."""
    poly = sp.Poly(sp.expand(expr), var)
    roots: set[sp.Expr] = set()
    for factor, _m in sp.factor_list(poly.as_expr())[1]:
        degree = sp.Poly(factor, var).degree()
        if degree == 0:
            continue
        if degree > 2:
            raise ValueError("irreducible_factor_above_degree_two")
        for r in sp.solve(factor, var):
            if r.is_real:
                roots.add(sp.radsimp(r))
    return sorted(roots, key=lambda r: float(r))


def solve_sign_chart(expr: sp.Expr, rel: str, var: sp.Symbol = X) -> sp.Set:
    poly = sp.Poly(sp.expand(expr), var)
    if poly.is_zero:
        return sp.S.Reals if rel in (">=", "<=") else sp.S.EmptySet
    ordered = real_roots(poly.as_expr(), var)
    closed = rel in (">=", "<=")
    want = 1 if rel in (">", ">=") else -1
    if not ordered:
        sign = int(sp.sign(poly.eval(0)))
        return sp.S.Reals if sign == want else sp.S.EmptySet
    probes = [ordered[0] - 1] + [sp.Rational(str(round((float(a) + float(b)) / 2, 9))) for a, b in zip(ordered, ordered[1:])] + [ordered[-1] + 1]
    segments: list[tuple[sp.Set, bool]] = []
    bounds = [-sp.oo] + ordered + [sp.oo]
    for i, probe in enumerate(probes):
        ok = int(sp.sign(poly.eval(probe if probe.is_Rational else sp.nsimplify(probe)))) == want
        segments.append((sp.Interval.open(bounds[i], bounds[i + 1]), ok))
        if i < len(ordered):
            segments.append((sp.FiniteSet(ordered[i]), closed))
    out: sp.Set = sp.S.EmptySet
    for seg, ok in segments:
        if ok:
            out = sp.Union(out, seg)
    return out


# --- 1. solve_polynomial_inequality -----------------------------------------------------------------------

def solve_polynomial_inequality(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    out = []
    for it in items:
        rel = it["rel"]
        if rel not in RELS:
            raise ValueError("unknown_relation")
        left, right = _side_expr(it["left"]), _side_expr(it.get("right", {"poly": [0]}))
        diff = sp.expand(left - right)
        if sp.Poly(diff, X).is_zero:
            raise ValueError("identically_equal_sides")
        domain = it.get("domain")
        solution = solve_sign_chart(diff, rel)
        if domain:
            solution = sp.Intersection(solution, sp.Interval(_q(domain[0]), _q(domain[1]), domain[2], domain[3]))
        out.append({"solution": set_record(solution), "difference": sp.sstr(diff).replace("**", "^"), "degree": int(sp.Poly(diff, X).degree()),
                    "factored": sp.latex(sp.factor(diff)), "difference_latex": sp.latex(diff),
                    "roots": [{"canonical": _ep_text(r), "latex": _ep_latex(r)} for r in real_roots(diff)]})
    return {"items": out}


def _check_solve_polynomial_inequality(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    from core.checkers.inequality_solution_checker import parse_real_solution_set, real_solution_sets_equal

    for it, rec in zip(givens["items"], answer["items"]):
        diff = sp.expand(_side_expr(it["left"]) - _side_expr(it.get("right", {"poly": [0]})))
        ref = sp.solve_univariate_inequality(_rel(diff, it["rel"]), X, relational=False)
        if it.get("domain"):
            d = it["domain"]
            ref = sp.Intersection(ref, sp.Interval(_q(d[0]), _q(d[1]), d[2], d[3]))
        parsed = parse_real_solution_set(rec["solution"]["canonical"])
        if not real_solution_sets_equal(parsed, ref):
            return False
        for probe in (-7, -3, -1, 0, 1, 2, 3, 5, 9, sp.Rational(1, 2)):  # point test against the displayed set
            inside = bool(_rel(diff, it["rel"]).subs(X, probe))
            if it.get("domain"):
                d = it["domain"]
                inside = inside and bool(sp.Interval(_q(d[0]), _q(d[1]), d[2], d[3]).contains(probe))
            if bool(parsed.contains(probe)) != inside:
                return False
    return True


# --- 2. polynomial_inequality_parameters ------------------------------------------------------------------

def _roots_sorted(roots: list[Any]) -> list[sp.Rational]:
    return sorted((_q(r) for r in roots), key=float)


def polynomial_inequality_parameters(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    out = []
    for it in items:
        kind = it["kind"]
        rec: dict[str, Any] = {"kind": kind}
        if kind == "quad_from_solution":
            # a x^2 + p x + b  rel 0, p known, solution strictly between / outside the roots r1 < r2
            p, (r1, r2) = _q(it["p"]), _roots_sorted(it["roots"])
            if r1 + r2 == 0:
                raise ValueError("degenerate_roots")
            a = -p / (r1 + r2)
            b = a * r1 * r2
            positive_rel = it["rel"] in (">", ">=")
            want_positive_lead = (not positive_rel) if it["shape"] == "between" else positive_rel
            if a == 0 or (a > 0) != want_positive_lead:
                raise ValueError("relation_is_inconsistent_with_the_solution")
            rec.update({"a": a, "b": b})
        elif kind == "cubic_from_solution":
            # a x^3 + b x^2 + c x + d  rel 0 with d known and three real roots
            d, (r1, r2, r3) = _q(it["d"]), _roots_sorted(it["roots"])
            prod = r1 * r2 * r3
            if prod == 0:
                raise ValueError("degenerate_roots")
            a = -d / prod
            b, c = -a * (r1 + r2 + r3), a * (r1 * r2 + r1 * r3 + r2 * r3)
            if a == 0 or ((a > 0) == (it["rel"] in ("<", "<="))) != (it["form"] == "low"):
                raise ValueError("relation_is_inconsistent_with_the_solution")
            rec.update({"a": a, "b": b, "c": c})
        elif kind == "always_true":
            # a x^2 + (m1 k + n1) x + (m2 k + n2) >= 0 for every real x  =>  discriminant <= 0
            a = _q(it["a"])
            b1, b0, c1, c0 = (_q(it[key]) for key in ("b1", "b0", "c1", "c0"))
            if a <= 0:
                raise ValueError("leading_coefficient_must_be_positive")
            disc = sp.expand((b1 * K + b0) ** 2 - 4 * a * (c1 * K + c0))
            rec["k"] = solve_sign_chart(disc, "<=", K)
        elif kind == "monic_compare":
            f = sp.expand(sp.Mul(*[(X - _q(r)) ** int(m) for r, m in it["roots"]]))
            g = _poly_expr(it["g"])
            rec["solution"] = solve_sign_chart(sp.expand(f - g), it["rel"])
            rec["f_positive"] = solve_sign_chart(f, ">")
            rec["f"] = f
        elif kind == "quad_factor_param":
            # (p2 x^2 + p1 x + p0)(x^2 + a x + b) rel 0 with a positive definite first factor: only the second factor decides the sign
            p2, p1, p0 = (_q(c) for c in it["pos"])
            if p2 <= 0 or p1 * p1 - 4 * p2 * p0 >= 0:
                raise ValueError("first_factor_must_be_positive_definite")
            r1, r2 = _roots_sorted(it["roots"])
            if r1 == r2:
                raise ValueError("distinct_roots_required")
            if (it["rel"] in ("<", "<=")) != (it["shape"] == "between"):
                raise ValueError("relation_is_inconsistent_with_the_solution")
            rec.update({"a": -(r1 + r2), "b": r1 * r2})
        else:
            raise ValueError(f"unknown_parameter_kind:{kind}")
        out.append(rec)
    # sympy objects are converted to records
    return {"items": [_param_record(r) for r in out]}


def _param_record(rec: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"kind": rec["kind"]}
    for key in ("a", "b", "c"):
        if key in rec:
            out[key] = {"canonical": str(rec[key]), "latex": sp.latex(rec[key])}
    if "k" in rec:
        out["k"] = set_record_k(rec["k"])
    if "solution" in rec:
        out["solution"] = set_record(rec["solution"])
        out["f_positive"] = set_record(rec["f_positive"])
        out["f"] = {"coeffs": [str(c) for c in sp.Poly(rec["f"], X).all_coeffs()], "plain": sp.sstr(rec["f"]).replace("**", "^")}
    return out


def set_record_k(s: sp.Set) -> dict[str, Any]:
    text = set_text(s).replace("x", "k")
    latex = set_latex(s).replace("x", "k")
    return {"canonical": text, "latex": latex}


def _check_polynomial_inequality_parameters(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    from core.checkers.inequality_solution_checker import parse_real_solution_set, real_solution_sets_equal

    for it, rec in zip(givens["items"], answer["items"]):
        kind = it["kind"]
        if kind in ("quad_from_solution", "cubic_from_solution"):
            a = sp.Rational(rec["a"]["canonical"])
            b = sp.Rational(rec["b"]["canonical"])
            if kind == "quad_from_solution":
                f = a * X ** 2 + _q(it["p"]) * X + b
            else:
                c = sp.Rational(rec["c"]["canonical"])
                f = a * X ** 3 + b * X ** 2 + c * X + _q(it["d"])
            got = sp.solve_univariate_inequality(_rel(f, it["rel"]), X, relational=False)  # the found parameters really give the stated solution
            roots = _roots_sorted(it["roots"])
            if kind == "quad_from_solution":
                closed = it["rel"] in (">=", "<=")
                want = sp.Interval(roots[0], roots[1], not closed, not closed) if it["shape"] == "between" else sp.Union(
                    sp.Interval(-sp.oo, roots[0], True, not closed), sp.Interval(roots[1], sp.oo, not closed, True))
            else:
                closed = it["rel"] in (">=", "<=")
                if it["form"] == "low":
                    want = sp.Union(sp.Interval(-sp.oo, roots[0], True, not closed), sp.Interval(roots[1], roots[2], not closed, not closed))
                else:
                    want = sp.Union(sp.Interval(roots[0], roots[1], not closed, not closed), sp.Interval(roots[2], sp.oo, not closed, True))
                want = sp.simplify(want)
            if not real_solution_sets_equal(got, want):
                return False
            if (a == 0):
                return False
        elif kind == "always_true":
            a = _q(it["a"])
            parsed = parse_real_solution_set(rec["k"]["canonical"].replace("k", "x"))
            for kv in (-9, -5, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 9, sp.Rational(7, 2), sp.Rational(1, 3)):
                f = a * X ** 2 + (_q(it["b1"]) * kv + _q(it["b0"])) * X + (_q(it["c1"]) * kv + _q(it["c0"]))
                holds = sp.solve_univariate_inequality(f >= 0, X, relational=False) == sp.S.Reals
                if holds != bool(parsed.contains(kv)):
                    return False
        elif kind == "monic_compare":
            f = sp.expand(sp.Mul(*[(X - _q(r)) ** int(m) for r, m in it["roots"]]))
            ref = sp.solve_univariate_inequality(_rel(f - _poly_expr(it["g"]), it["rel"]), X, relational=False)
            if not real_solution_sets_equal(parse_real_solution_set(rec["solution"]["canonical"]), ref):
                return False
            ref_pos = sp.solve_univariate_inequality(f > 0, X, relational=False)
            if not real_solution_sets_equal(parse_real_solution_set(rec["f_positive"]["canonical"]), ref_pos):
                return False
        elif kind == "quad_factor_param":
            a, b = sp.Rational(rec["a"]["canonical"]), sp.Rational(rec["b"]["canonical"])
            p2, p1, p0 = (_q(c) for c in it["pos"])
            product = sp.expand((p2 * X ** 2 + p1 * X + p0) * (X ** 2 + a * X + b))
            got_set = sp.solve_univariate_inequality(_rel(product, it["rel"]), X, relational=False)  # the found a, b give exactly the stated solution
            r1, r2 = _roots_sorted(it["roots"])
            closed = it["rel"] in (">=", "<=")
            if it["shape"] == "between":
                want = sp.Interval(r1, r2, not closed, not closed)
            else:
                want = sp.Union(sp.Interval(-sp.oo, r1, True, not closed), sp.Interval(r2, sp.oo, not closed, True))
            if not real_solution_sets_equal(got_set, want):
                return False
        else:
            return False
    return True


# --- 3. polynomial_statements -----------------------------------------------------------------------------

def _stmt_set(item: dict[str, Any]) -> sp.Set:
    diff = sp.expand(_side_expr(item["left"]) - _side_expr(item.get("right", {"poly": [0]})))
    return solve_sign_chart(diff, item["rel"])


def _coeff_table(roots: list[Any], lead: Any) -> dict[str, sp.Rational]:
    r = [_q(v) for v in roots]
    a = _q(lead)
    poly = sp.Poly(sp.expand(a * sp.Mul(*[(X - v) for v in r])), X)
    c = poly.all_coeffs()
    return {"a": c[0], "b": c[1], "c": c[2], "d": c[3], "sum": sum(c)}


def polynomial_statements(subject: dict[str, Any], statements: list[dict[str, Any]], mode: str = "select", **text: Any) -> dict[str, Any]:
    if mode not in ("select", "truth"):
        raise ValueError("mode_must_be_select_or_truth")
    if mode == "truth" and len(statements) != 1:
        raise ValueError("truth_mode_needs_exactly_one_statement")
    truths: list[bool] = []
    for st in statements:
        kind = st["kind"]
        if kind == "solution_claim":
            truths.append(bool(_stmt_set(st["ineq"]) == _claim_set(st["claim"])))
        elif kind == "same_solution":
            truths.append(bool(_stmt_set(st["a"]) == _stmt_set(st["b"])))
        elif kind == "coefficient_sign":
            value = _coeff_table(subject["roots"], subject["lead"])[st["name"]]
            truths.append(bool((value > 0) == (st["sign"] == "+") and value != 0))
        elif kind == "sum_positive":
            truths.append(bool(_coeff_table(subject["roots"], subject["lead"])["sum"] > 0))
        else:
            raise ValueError(f"unknown_polynomial_statement:{kind}")
    extra: dict[str, Any] = {}
    if subject and "roots" in subject:
        table = _coeff_table(subject["roots"], subject["lead"])
        extra = {"coefficients": {k: str(v) for k, v in table.items()}}
    return {"mode": mode, "truths": truths, "selected": [i for i, t in enumerate(truths, start=1) if t], **extra}


def _claim_set(claim: str) -> sp.Set:
    from core.checkers.inequality_solution_checker import parse_real_solution_set

    parsed = parse_real_solution_set(claim)
    if parsed is None:
        raise ValueError("claim_not_parsable")
    return parsed


def _check_polynomial_statements(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    subject, sts = givens.get("subject") or {}, givens["statements"]
    if len(answer["truths"]) != len(sts) or answer["selected"] != [i for i, t in enumerate(answer["truths"], start=1) if t]:
        return False
    for st, truth in zip(sts, answer["truths"]):
        kind = st["kind"]
        if kind in ("solution_claim", "same_solution"):
            def ref(item: dict[str, Any]) -> sp.Set:
                diff = sp.expand(_side_expr(item["left"]) - _side_expr(item.get("right", {"poly": [0]})))
                return sp.solve_univariate_inequality(_rel(diff, item["rel"]), X, relational=False)

            if kind == "solution_claim":
                same = ref(st["ineq"]).is_subset(_claim_set(st["claim"])) and _claim_set(st["claim"]).is_subset(ref(st["ineq"]))
            else:
                same = ref(st["a"]).is_subset(ref(st["b"])) and ref(st["b"]).is_subset(ref(st["a"]))
            if bool(same) != bool(truth):
                return False
        else:
            f = a_ = None
            r = [_q(v) for v in subject["roots"]]
            f = sp.expand(_q(subject["lead"]) * sp.Mul(*[(X - v) for v in r]))
            if kind == "sum_positive":
                if bool(f.subs(X, 1) > 0) != bool(truth):
                    return False
            else:
                idx = {"a": 3, "b": 2, "c": 1, "d": 0}[st["name"]]
                value = sp.diff(f, X, idx).subs(X, 0) / sp.factorial(idx)
                if (bool(value > 0) == (st["sign"] == "+") and value != 0) != bool(truth):
                    return False
            # re-read the sign of d from the curve: f(0) is d, f(+large) has the sign of a
            if f.subs(X, 0) != _coeff_table(subject["roots"], subject["lead"])["d"]:
                return False
    return True


# --- 4. polynomial_applications ---------------------------------------------------------------------------

def _within(domain: tuple[Any, Any, bool, bool]) -> sp.Set:
    return sp.Interval(_q(domain[0]), _q(domain[1]), domain[2], domain[3])


def polynomial_applications(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    out = []
    for it in items:
        kind = it["kind"]
        rec: dict[str, Any] = {"kind": kind}
        if kind == "triangle_rectangle":  # base B = height H, rectangle with base x on the base, area >= A
            B, H, A = _q(it["B"]), _q(it["H"]), _q(it["A"])
            area = sp.expand(X * H * (1 - X / B))
            sol = sp.Intersection(solve_sign_chart(sp.expand(area - A), ">="), sp.Interval.open(0, B))
            rec.update({"area": sp.sstr(area).replace("**", "^"), "solution": set_record(sol)})
        elif kind == "square_corner":  # square of side s, AP = BQ = x, area of PQCD >= A
            s, A = _q(it["s"]), _q(it["A"])
            area = sp.expand(s ** 2 - s * X + X ** 2 / 2)
            sol = sp.Intersection(solve_sign_chart(sp.expand(area - A), ">="), sp.Interval.open(0, s))
            rec.update({"area": sp.sstr(area).replace("**", "^"), "solution": set_record(sol)})
        elif kind == "path_around_plot":  # W x L plot, path width w, inner perimeter >= P0 and inner area <= A0
            W, L, P0, A0 = _q(it["W"]), _q(it["L"]), _q(it["P0"]), _q(it["A0"])
            inner_p = sp.expand(2 * ((W - 2 * X) + (L - 2 * X)))
            inner_a = sp.expand((W - 2 * X) * (L - 2 * X))
            dom = sp.Interval.open(0, sp.Min(W, L) / 2)
            sol = sp.Intersection(solve_sign_chart(sp.expand(inner_p - P0), ">="), solve_sign_chart(sp.expand(inner_a - A0), "<="), dom)
            rec.update({"perimeter": sp.sstr(inner_p).replace("**", "^"), "area": sp.sstr(inner_a).replace("**", "^"), "solution": set_record(sol)})
        elif kind == "cube_paint":  # paint cost <= share * plastic cost, edge at most xmax
            c1, c2, share, xmax = _q(it["plastic"]), _q(it["paint"]), _q(it["share"]), _q(it["xmax"])
            diff = sp.expand(share * c1 * X ** 3 - 6 * c2 * X ** 2)
            sol = sp.Intersection(solve_sign_chart(diff, ">="), sp.Interval.Lopen(0, xmax))
            rec.update({"difference": sp.sstr(diff).replace("**", "^"), "solution": set_record(sol)})
        elif kind == "frame_box":  # tube length Ltot cut in 12: 8x + 4y = Ltot, volume x^2 y >= V
            Ltot, V = _q(it["L"]), _q(it["V"])
            y = Ltot / 4 - 2 * X
            f = sp.expand(X ** 2 * y)
            sol = sp.Intersection(solve_sign_chart(sp.expand(f - V), ">="), sp.Interval.open(0, Ltot / 8))
            factors = [r for r in (1, 2, 3, 4, 0) if sp.expand(f - V).subs(X, r) == 0]
            rec.update({"relation": f"8*x+4*y={Ltot}", "c": str(Ltot / 4), "f": sp.sstr(f).replace("**", "^"),
                        "f_coeffs": [str(c) for c in sp.Poly(f, X).all_coeffs()], "factor_roots": [int(r) for r in factors],
                        "solution": set_record(sol)})
        elif kind == "open_box":  # open box with square base x and height y: outside area x^2 + 4xy = S, volume >= V
            S_, V = _q(it["S"]), _q(it["V"])
            y = (S_ - X ** 2) / (4 * X)
            f = sp.expand(sp.cancel(X ** 2 * y))
            sol = sp.Intersection(solve_sign_chart(sp.expand(f - V), ">="), sp.Interval.open(0, sp.sqrt(S_)))
            factors = [r for r in (1, 2, 3, 4, 0) if sp.expand(f - V).subs(X, r) == 0]
            rec.update({"S": str(S_), "relation": f"x^2+4*x*y={S_}", "f": sp.sstr(f).replace("**", "^"), "f_coeffs": [str(c) for c in sp.Poly(f, X).all_coeffs()],
                        "factor_roots": [int(r) for r in factors], "solution": set_record(sol)})
        elif kind == "tent_prism":  # right-triangle prism frame: 2(p+q+r)x + 3y = L, volume (p q / 2) x^2 y >= V
            p, q, r_ = (_q(v) for v in it["triple"])
            if p * p + q * q != r_ * r_:
                raise ValueError("triple_is_not_a_right_triangle")
            Ltot, V = _q(it["L"]), _q(it["V"])
            perimeter = p + q + r_
            f = sp.expand(p * q / 6 * X ** 2 * (Ltot - 2 * perimeter * X))
            sol = sp.Intersection(solve_sign_chart(sp.expand(f - V), ">="), sp.Interval.open(0, Ltot / (2 * perimeter)))
            factors = [r for r in (-1, -2, -3, -4, 0) if sp.expand(f - V).subs(X, r) == 0]
            rec.update({"relation": f"{2 * perimeter}*x+3*y={Ltot}", "f": sp.sstr(f).replace("**", "^"),
                        "f_coeffs": [str(c) for c in sp.Poly(f, X).all_coeffs()], "factor_roots": [int(r) for r in factors], "solution": set_record(sol)})
        elif kind == "projectile_ceiling":  # y = k t (T - t), k > 0: the highest point k T^2 / 4 must stay below the ceiling H
            T, H = _q(it["T"]), _q(it["H"])
            if T <= 0 or H <= 0:
                raise ValueError("positive_T_and_H_required")
            peak = sp.expand(K * T ** 2 / 4)
            rec["solution"] = set_record_k(sp.Intersection(solve_sign_chart(sp.expand(peak - H), "<", K), sp.Interval.open(0, sp.oo)))
            rec["peak"] = sp.sstr(peak).replace("**", "^")
        else:
            raise ValueError(f"unknown_application_kind:{kind}")
        out.append(rec)
    return {"items": out}


def _check_polynomial_applications(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    from core.checkers.inequality_solution_checker import parse_real_solution_set, real_solution_sets_equal

    for it, rec in zip(givens["items"], answer["items"]):
        kind = it["kind"]
        got = parse_real_solution_set(rec["solution"]["canonical"].replace("k", "x") if kind == "projectile_ceiling" else rec["solution"]["canonical"])
        if got is None:
            return False
        if kind == "tent_prism":
            p, q, r_ = (_q(v) for v in it["triple"])
            Ltot, V = _q(it["L"]), _q(it["V"])
            y = sp.Symbol("y", real=True)
            ysol = sp.solve(sp.Eq(2 * (p * X + q * X + r_ * X) + 3 * y, Ltot), y)[0]  # three edges y, two triangles of sides px, qx, rx
            f = sp.expand(sp.Rational(1, 2) * p * X * q * X * ysol)  # right-triangle area times the length y
            ref = sp.solve_univariate_inequality(f >= V, X, relational=False).intersect(sp.Interval.open(0, Ltot / (2 * (p + q + r_))))
            for r in rec["factor_roots"]:
                if sp.rem(sp.Poly(f - V, X), sp.Poly(X - r, X)).as_expr() != 0:
                    return False
            if sorted(rec["factor_roots"]) != sorted(r for r in (-1, -2, -3, -4, 0) if (f - V).subs(X, r) == 0):
                return False
        elif kind == "projectile_ceiling":
            T, H = _q(it["T"]), _q(it["H"])
            t = sp.Symbol("t", real=True)
            for kv in (sp.Rational(1, 10), 1, 2, 3, 4, 5, 6, 8, 10, 16, 40):  # brute check of "the highest point stays below the ceiling"
                top = sp.maximum(kv * t * (T - t), t, sp.Interval(-sp.oo, sp.oo))
                if bool(top < H) != bool(got.contains(kv)):
                    return False
            ref = got
        elif kind == "triangle_rectangle":
            B, H, A = _q(it["B"]), _q(it["H"]), _q(it["A"])
            # similar triangles: the rectangle of base x has height H (B - x) / B
            ref = sp.solve_univariate_inequality(X * H * (B - X) / B >= A, X, relational=False).intersect(sp.Interval.open(0, B))
        elif kind == "square_corner":
            s, A = _q(it["s"]), _q(it["A"])
            # square minus triangle APD (legs s, x) minus triangle PBQ (legs s - x, x)
            ref = sp.solve_univariate_inequality(s ** 2 - s * X / 2 - (s - X) * X / 2 >= A, X, relational=False).intersect(sp.Interval.open(0, s))
        elif kind == "path_around_plot":
            W, L, P0, A0 = (_q(it[k]) for k in ("W", "L", "P0", "A0"))
            c1 = sp.solve_univariate_inequality(2 * (W - 2 * X + L - 2 * X) >= P0, X, relational=False)
            c2 = sp.solve_univariate_inequality((W - 2 * X) * (L - 2 * X) <= A0, X, relational=False)
            ref = c1.intersect(c2).intersect(sp.Interval.open(0, min(W, L) / 2))
        elif kind == "cube_paint":
            c1, c2, share, xmax = (_q(it[k]) for k in ("plastic", "paint", "share", "xmax"))
            ref = sp.solve_univariate_inequality(c2 * 6 * X ** 2 <= share * c1 * X ** 3, X, relational=False).intersect(sp.Interval.Lopen(0, xmax))
        elif kind == "frame_box":
            Ltot, V = _q(it["L"]), _q(it["V"])
            y = sp.Symbol("y", real=True)
            ysol = sp.solve(sp.Eq(8 * X + 4 * y, Ltot), y)[0]
            f = sp.expand(X ** 2 * ysol)
            ref = sp.solve_univariate_inequality(f >= V, X, relational=False).intersect(sp.Interval.open(0, Ltot / 8))
            for r in rec["factor_roots"]:
                if sp.rem(sp.Poly(f - V, X), sp.Poly(X - r, X)).as_expr() != 0:
                    return False
            if sorted(rec["factor_roots"]) != sorted(r for r in (1, 2, 3, 4, 0) if (f - V).subs(X, r) == 0):
                return False
        elif kind == "open_box":
            S_, V = _q(it["S"]), _q(it["V"])
            y = sp.Symbol("y", real=True)
            ysol = sp.solve(sp.Eq(X ** 2 + 4 * X * y, S_), y)[0]
            f = sp.simplify(X ** 2 * ysol)
            ref = sp.solve_univariate_inequality(f >= V, X, relational=False).intersect(sp.Interval.open(0, sp.sqrt(S_)))
            for r in rec["factor_roots"]:
                if sp.simplify((f - V).subs(X, r)) != 0:
                    return False
        else:
            return False
        if not real_solution_sets_equal(got, ref):
            return False
    return True


# --- 5. polynomial_graph_solutions ------------------------------------------------------------------------

def _graph_poly(roots: list[Any], lead: Any) -> sp.Expr:
    return sp.expand(_q(lead) * sp.Mul(*[(X - _q(r)) ** int(m) for r, m in roots]))


def polynomial_graph_solutions(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    out = []
    for it in items:
        roots = sorted(((_q(r), int(m)) for r, m in it["roots"]), key=lambda t: float(t[0]))
        lead = _q(it["lead"])
        if lead == 0 or len({r for r, _m in roots}) != len(roots):
            raise ValueError("distinct_roots_and_nonzero_lead_required")
        f = _graph_poly(roots, lead)
        rec = {"degree": int(sp.Poly(f, X).degree()), "zeros": [str(r) for r, _m in roots],
               "eq": {"canonical": ", ".join(str(r) for r, _m in roots), "members": [str(r) for r, _m in roots]},
               "gt": set_record(solve_sign_chart(f, ">")), "lt": set_record(solve_sign_chart(f, "<")), "le": set_record(solve_sign_chart(f, "<=")),
               "end_up": bool(lead > 0)}
        # the curve for the figure: scaled so the largest wave has height ~4 inside the window
        rec["curve"], rec["window"] = graph_curve(roots, lead)
        out.append(rec)
    return {"items": out}


def graph_curve(roots: list[Any], lead: Any, height: float = 4.0) -> tuple[list[list[float]], dict[str, Any]]:
    """Sampled curve of ``lead * prod (x - r)^m`` for a figure (shape only: y is scaled so the tallest wave is ``height``)."""
    pairs = [(_q(r), int(m)) for r, m in roots]
    f = _graph_poly(pairs, lead)
    lo, hi = float(min(r for r, _m in pairs)) - 1.2, float(max(r for r, _m in pairs)) + 1.2
    xs = [lo + (hi - lo) * i / 160 for i in range(161)]
    ys = [float(f.subs(X, sp.Float(x, 20))) for x in xs]
    scale = height / max(1e-9, max(abs(y) for y in ys))
    return [[round(x, 4), round(y * scale, 4)] for x, y in zip(xs, ys)], {"x": [lo, hi], "y": height + 1.5}


def _check_polynomial_graph_solutions(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    from core.checkers.inequality_solution_checker import parse_real_solution_set, real_solution_sets_equal

    for it, rec in zip(givens["items"], answer["items"]):
        pts = rec["curve"]
        # read the plotted curve alone: sign changes / touches of y at the zeros, and the sign at the far right
        f = _graph_poly(it["roots"], it["lead"])
        for key, rel in (("gt", ">"), ("lt", "<"), ("le", "<=")):
            ref = sp.solve_univariate_inequality(_rel(f, rel), X, relational=False)
            if not real_solution_sets_equal(parse_real_solution_set(rec[key]["canonical"]), ref):
                return False
        # the plotted points must have the same sign pattern as the answer at sample points
        gt = parse_real_solution_set(rec["gt"]["canonical"])
        lt = parse_real_solution_set(rec["lt"]["canonical"])
        for x, y in pts[::8]:
            if abs(y) < 0.05:
                continue
            if (y > 0) != bool(gt.contains(sp.nsimplify(x, rational=True))) or (y < 0) != bool(lt.contains(sp.nsimplify(x, rational=True))):
                return False
        if (pts[-1][1] > 0) != rec["end_up"]:
            return False
        members = sorted(sp.Rational(v) for v in rec["eq"]["members"])
        if members != sorted(sp.Rational(str(sp.nsimplify(r))) for r, _m in it["roots"]):
            return False
    return True


# --- registry / entrypoint --------------------------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "solve_polynomial_inequality": (solve_polynomial_inequality, _check_solve_polynomial_inequality, ("items",)),
    "polynomial_inequality_parameters": (polynomial_inequality_parameters, _check_polynomial_inequality_parameters, ("items",)),
    "polynomial_statements": (polynomial_statements, _check_polynomial_statements, ("statements",)),
    "polynomial_applications": (polynomial_applications, _check_polynomial_applications, ("items",)),
    "polynomial_graph_solutions": (polynomial_graph_solutions, _check_polynomial_graph_solutions, ("items",)),
}
OPERATIONS = tuple(_OPERATIONS)


def build_polynomial_inequality_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_polynomial_inequality_operation:{operation}")
    solve, _check, required = _OPERATIONS[operation]
    givens = {k: v for k, v in (constraints or {}).items() if k not in ("skill_id",)}
    givens.setdefault("subject", {}) if operation == "polynomial_statements" else None
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
