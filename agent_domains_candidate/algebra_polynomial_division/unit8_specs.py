"""Per-component *inputs* for 普高數學1 Unit 8 (多項式的除法原理).

Each entry gives the source-faithful givens (variant 0) and a sampler for further variants of the
same shape.  Samplers only choose inputs; the domain computes every answer and rejects degenerate
inputs (the sandbox skips a candidate the domain refuses).
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Callable

from .polynomial_core import deg, ev, fr, norm, padd, pdivmod, pmul, poly, psub, pscale, synthetic

SKILLS = {
    "basic": "gh_BasicConceptsOfPolynomials",
    "arith": "gh_ArithmeticOperationsOfPolynomials",
    "remainder": "gh_RemainderTheorem",
    "factor": "gh_FactorTheorem",
}

# 教材題目中無法落入正式作答契約的題目（記錄原因，不進 wrapper）
DEFERRED: dict[int, str] = {}

OP = {name: name for name in (
    "polynomial_arithmetic_items", "evaluate_polynomial_statements", "solve_polynomial_parameters", "taylor_shift_expansion",
    "evaluate_polynomial_values", "solve_remainder_from_conditions", "solve_polynomial_from_remainder_congruences",
    "solve_remainder_with_linear_part", "interpolate_polynomials", "select_linear_factors", "solve_erased_cubic",
    "solve_masked_synthetic_coefficient", "solve_divisor_from_quotient_remainder",
)}

SKILL_OPERATIONS = {
    "basic": ["evaluate_polynomial_statements"],
    "arith": ["polynomial_arithmetic_items", "evaluate_polynomial_statements", "solve_polynomial_parameters", "taylor_shift_expansion",
              "evaluate_polynomial_values", "solve_divisor_from_quotient_remainder"],
    "remainder": ["evaluate_polynomial_values", "solve_remainder_from_conditions", "evaluate_polynomial_statements",
                  "solve_polynomial_from_remainder_congruences", "solve_remainder_with_linear_part"],
    "factor": ["select_linear_factors", "interpolate_polynomials", "solve_erased_cubic", "solve_masked_synthetic_coefficient",
               "solve_polynomial_parameters", "evaluate_polynomial_statements"],
}

STATIC_COMPONENTS: dict[int, str] = {}


# --- helpers -----------------------------------------------------------------------------------------

def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def nz(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v:
            return v


def j(value: Any) -> Any:
    """JSON-plain coefficient: int when integral, otherwise ``"p/q"``."""
    q = fr(value)
    return int(q) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def jl(coeffs: list) -> list:
    return [j(c) for c in coeffs]


def rpoly(rng: random.Random, n: int, lo: int = -6, hi: int = 6, lead: tuple[int, int] = (1, 4), holes: int = 0,
          signed_lead: bool = False) -> list[int]:
    """Integer coefficients of a degree-``n`` polynomial (descending); ``holes`` interior zero terms."""
    lead_v = rng.randint(*lead) * (pick(rng, [1, -1]) if signed_lead else 1)
    rest = [rng.randint(lo, hi) for _ in range(n)]
    for idx in rng.sample(range(n - 1), min(holes, max(n - 1, 0))) if n > 1 else []:
        rest[idx] = 0
    if rest and rest[-1] == 0 and n >= 1:
        rest[-1] = nz(rng, lo, hi)
    return [lead_v] + rest


def lin(root: Any) -> list:
    """``x - root`` as coefficients."""
    return [1, j(-fr(root))]


def prod(*polys: list) -> list[Fraction]:
    out = poly([1])
    for p in polys:
        out = pmul(out, poly(p))
    return out


def value(p: list, x: Any) -> Fraction:
    return ev(poly(p), x)


# --- A. polynomial_arithmetic_items ------------------------------------------------------------------

def _add_sub(defs_f: list, defs_g: list, style: str = "defs_then_items") -> dict[str, Any]:
    return {"defs": {"f": defs_f, "g": defs_g}, "items": [{"op": "add", "f": "f", "g": "g"}, {"op": "sub", "f": "f", "g": "g"}], "style": style}


def s12520(rng): return _add_sub(rpoly(rng, 3, -5, 5, (1, 4), holes=1), rpoly(rng, 2, -4, 4, (1, 3)))


v12520 = _add_sub([3, 0, 4, -5], [1, 3, 1])


def s12526(rng): return _add_sub(rpoly(rng, 3, -4, 4, (1, 3), holes=1), rpoly(rng, 3, -4, 4, (1, 3), holes=1))


v12526 = _add_sub([2, 1, 0, -1], [2, 0, -3, 4])


def _product(f: list, g: list) -> dict[str, Any]:
    return {"defs": {"f": f, "g": g}, "items": [{"op": "mul", "f": "f", "g": "g"}], "style": "product"}


def s12521(rng): return _product(rpoly(rng, 2, -4, 4, (1, 4)), rpoly(rng, 1, -4, 4, (1, 3)))


v12521 = _product([3, -2, 1], [2, -1])


def s12527(rng): return _product(rpoly(rng, 1, -4, 4, (1, 4)), rpoly(rng, 2, -4, 4, (1, 3)))


v12527 = {"defs": {"f": [3, 2], "g": [1, -2, 1]}, "items": [{"op": "mul", "f": "f", "g": "g"}], "style": "defs_then_items"}


def _syn(f: list, c: int, phrase: str = "into_by") -> dict[str, Any]:
    return {"op": "synthetic", "f": f, "g": [1, -c], "phrase": phrase}


def s12523(rng):
    f = rpoly(rng, 4, -7, 7, (1, 3), holes=1)
    f[rng.randrange(1, 3)] = 0  # keep a missing term, as in the source
    return {"defs": {}, "items": [_syn(f, nz(rng, -4, 4))], "style": "synthetic_single"}


v12523 = {"defs": {}, "items": [_syn([1, 2, 0, 5, -7], -3)], "style": "synthetic_single"}


def s12530(rng):
    return {"defs": {}, "items": [_syn(rpoly(rng, 3, -5, 5, (1, 3), holes=1), nz(rng, -4, 4)), _syn(rpoly(rng, 4, -7, 7, (1, 3)), nz(rng, -4, 4))],
            "style": "synthetic_list", "intro": "使用綜合除法，求下列各式。"}


v12530 = {"defs": {}, "items": [_syn([1, 0, 2, -1], -4), _syn([2, -3, -5, 8, -3], 2)], "style": "synthetic_list", "intro": "使用綜合除法，求下列各式。"}


def s12534(rng):
    return {"defs": {}, "items": [_syn(rpoly(rng, 3, -7, 7, (1, 2)), nz(rng, -4, 4), "by_into"),
                                  _syn(rpoly(rng, 4, -8, 8, (1, 3), holes=1), nz(rng, -4, 4), "by_into")],
            "style": "synthetic_list", "intro": "利用綜合除法求下列各小題的商式及餘式："}


v12534 = {"defs": {}, "items": [_syn([1, -5, 7, -5], 3, "by_into"), _syn([2, 5, 0, 8, -7], -2, "by_into")],
          "style": "synthetic_list", "intro": "利用綜合除法求下列各小題的商式及餘式："}


def _four_ops(f: list, g: list, h: list) -> dict[str, Any]:
    return {"defs": {"f": f, "g": g, "h": h},
            "items": [{"op": "add", "f": "f", "g": "g"}, {"op": "sub", "f": "f", "g": "g"}, {"op": "mul", "f": "f", "g": "g"},
                      {"op": "divide", "f": "h", "g": "g"}], "style": "defs_then_items"}


def s12532(rng):
    return _four_ops(rpoly(rng, 2, -4, 4, (1, 3), signed_lead=True), rpoly(rng, 2, -3, 3, (1, 3), signed_lead=True), rpoly(rng, 4, -6, 6, (1, 3), holes=2))


v12532 = _four_ops([3, 2, -1], [-3, -1, 2], [3, -5, 0, 0, -6])


# --- B. evaluate_polynomial_statements ---------------------------------------------------------------

def _stmt_poly(f: list, statements: list, intro: str = "about_poly") -> dict[str, Any]:
    return {"subject": {"type": "poly", "coeffs": f}, "statements": statements, "mode": "select", "intro_kind": intro}


def _sparse(rng: random.Random, n: int) -> list[int]:
    f = [nz(rng, -3, 3) if abs(rng.randint(0, 3)) else 0 for _ in range(n + 1)]
    f[0] = pick(rng, [1, 2, 3, -2, 4])
    f[-1] = nz(rng, -5, 5)
    return f


def s12517(rng):
    n = rng.randint(4, 6)
    f = _sparse(rng, n)
    p1, p2 = rng.sample(range(1, n), 2)
    c = lambda p: f[n - p]  # noqa: E731
    x0 = pick(rng, [-1, 1, 2, -2])
    claim = lambda v: v if rng.random() < 0.5 else v + nz(rng, -2, 2)  # noqa: E731
    return _stmt_poly(f, [
        {"kind": "is_degree_poly", "n": n if rng.random() < 0.7 else n - 1},
        {"kind": "deg_equals", "n": n if rng.random() < 0.7 else n + 1},
        {"kind": "coeff_is", "power": p1, "value": claim(c(p1))},
        {"kind": "coeff_is", "power": p2, "value": claim(c(p2))},
        {"kind": "value_is", "x": x0, "value": claim(int(value(f, x0)))},
    ])


v12517 = _stmt_poly([3, -2, 0, 1, 0, 5], [
    {"kind": "is_degree_poly", "n": 5}, {"kind": "deg_equals", "n": 5}, {"kind": "coeff_is", "power": 2, "value": 0},
    {"kind": "coeff_is", "power": 3, "value": 0}, {"kind": "value_is", "x": -1, "value": 3}])


def _named_division(f: list, g: list, claim_deg: int, claim_rem: Any) -> dict[str, Any]:
    return {"subject": {"type": "poly", "coeffs": f}, "named_divisor": g, "intro_kind": "division_named", "mode": "select",
            "statements": [{"kind": "quotient_degree", "divisor": g, "n": claim_deg}, {"kind": "quotient_integer_coeffs", "divisor": g},
                           {"kind": "remainder_equals", "divisor": g, "claimed": [claim_rem]},
                           {"kind": "division_identity", "divisor": g}, {"kind": "fraction_identity", "divisor": g}]}


def s12528(rng):
    f = rpoly(rng, 3, -5, 5, (1, 3), signed_lead=True)
    g = [pick(rng, [2, 3, -2]), nz(rng, -3, 3)]
    _q, r = pdivmod(poly(f), poly(g))
    claim = j(r[0] if r else 0) if rng.random() < 0.4 else nz(rng, -5, 5)
    return _named_division(f, g, pick(rng, [2, 2, 3, 1]), claim)


v12528 = _named_division([2, -3, 1, 4], [2, 1], 2, 3)


def _tf_remainder(divisor_root: int, quotient: list, remainder: list, claimed: list) -> dict[str, Any]:
    return {"subject": {"type": "dqr", "divisor": lin(divisor_root), "quotient": quotient, "remainder": remainder}, "mode": "truth",
            "statements": [{"kind": "remainder_equals", "divisor": lin(divisor_root), "claimed": claimed}]}


def s12518(rng):
    c = nz(rng, -3, 3)
    q = rpoly(rng, rng.randint(3, 5), -2, 2, (1, 1))
    r = [nz(rng, -2, 2), nz(rng, -3, 3)]
    const = [j(value(padd(pmul(poly(lin(c)), poly(q)), poly(r)), c))]
    return _tf_remainder(c, q, r, r if rng.random() < 0.6 else const)


v12518 = _tf_remainder(2, [1, 0, 0, 0, 2, -1], [1, 1], [1, 1])


def _tf_factor(f: list, a: int) -> dict[str, Any]:
    return {"subject": {"type": "poly", "coeffs": f}, "mode": "truth",
            "statements": [{"kind": "is_factor", "divisor": lin(a), "phrase": "divisible"}]}


def s12519(rng):
    n = rng.randint(3, 7)
    a = pick(rng, [-3, -2, -1, 1, 2, 3])
    k = -(a ** n) if rng.random() < 0.55 else nz(rng, -9, 9)
    return _tf_factor([1] + [0] * (n - 1) + [k], a)


v12519 = _tf_factor([1, 0, 0, 0, 0, 1], -1)


def _tf_scaled(kind: str, divisor: list, k: int) -> dict[str, Any]:
    return {"subject": {"type": "generic"}, "mode": "truth", "statements": [{"kind": kind, "divisor": divisor, "k": k}]}


def s12543(rng): return _tf_scaled("scaled_remainder_same", [pick(rng, [1, 2]), nz(rng, -4, 4)], pick(rng, [2, 3, 4, 5, -2, -3]))


def s12544(rng): return _tf_scaled("scaled_quotient_same", [pick(rng, [1, 2]), nz(rng, -4, 4)], pick(rng, [2, 3, 4, 5, -2, -3]))


v12543 = _tf_scaled("scaled_remainder_same", [1, 1], 3)
v12544 = _tf_scaled("scaled_quotient_same", [1, 1], 3)


def _statement_expr(d: list, q: list, r: list, statements: list) -> dict[str, Any]:
    return {"subject": {"type": "dqr", "divisor": d, "quotient": q, "remainder": r}, "mode": "select", "intro_kind": "set_expr",
            "statements": statements}


def s12546(rng):
    d = [1] + [nz(rng, -2, 2), pick(rng, [0, 0, 1, -1]), nz(rng, -2, 2)]
    q = [1, nz(rng, -2, 2), nz(rng, -2, 2)]
    r = [nz(rng, -3, 3), 0, nz(rng, -2, 2)]
    f = padd(pmul(poly(d), poly(q)), poly(r))
    c1, c2 = nz(rng, -2, 2), nz(rng, -3, 3)
    quad = [1, nz(rng, -2, 2), nz(rng, -2, 2)]
    true_q = pdivmod(f, poly(quad))[0]
    claim_q = jl(true_q) if rng.random() < 0.5 else jl(padd(true_q, poly([nz(rng, -2, 2)])))
    twice = [2 * x for x in d]
    return _statement_expr(d, q, r, [
        {"kind": "remainder_equals", "divisor": lin(-c1), "claimed": [j(value(f, -c1)) if rng.random() < 0.5 else nz(rng, -4, 4)]},
        {"kind": "is_factor", "divisor": lin(c2)},
        {"kind": "remainder_equals", "divisor": d, "claimed": r},
        {"kind": "remainder_equals", "divisor": twice, "claimed": jl(pscale(poly(r), Fraction(1, 2)))},
        {"kind": "quotient_equals", "divisor": quad, "claimed": claim_q},
    ])


v12546 = _statement_expr([1, 2, 0, 1], [1, 1, -1], [2, 0, 1], [
    {"kind": "remainder_equals", "divisor": [1, 1], "claimed": [3]},
    {"kind": "is_factor", "divisor": [1, -2]},
    {"kind": "remainder_equals", "divisor": [1, 2, 0, 1], "claimed": [2, 0, 1]},
    {"kind": "remainder_equals", "divisor": [2, 4, 0, 2], "claimed": [1, 0, "1/2"]},
    {"kind": "quotient_equals", "divisor": [1, 1, -1], "claimed": [1, 2, 0, 3]},
])


def _tf_zeros(zeros: list, factors: list) -> dict[str, Any]:
    return {"subject": {"type": "generic"}, "mode": "truth",
            "statements": [{"kind": "factor_product_from_zeros", "zeros": zeros, "factors": factors}]}


def _linear_of(root: Fraction) -> list:
    return [root.denominator, -root.numerator]


def s12556(rng):
    z1, z2 = rng.sample([fr(x) for x in (-3, -2, -1, 1, 2, 3, "1/2", "-1/2", "1/3", "3/2")], 2)
    kind = rng.random()
    if kind < 0.5:
        facs = [_linear_of(z1), _linear_of(z2)]
    elif kind < 0.75:
        facs = [_linear_of(z1), _linear_of(z1)]
    else:
        facs = [_linear_of(z1), _linear_of(z2 + 5)]
    return _tf_zeros([j(z1), j(z2)], facs)


v12556 = _tf_zeros([-1, "1/2"], [[1, 1], [2, -1]])


# --- C. solve_polynomial_parameters ------------------------------------------------------------------

def _ident(f: list, d: list, q: list, r: list) -> dict[str, Any]:
    return {"form": "identity", "params": ["a", "b"], "f": f, "d": d, "q": q, "r": r, "stem": "identity"}


def s12522(rng):
    p, q0 = nz(rng, -3, 3), nz(rng, -3, 3)
    b, r1, r0 = nz(rng, -4, 4), nz(rng, -3, 3), nz(rng, -5, 5)
    a = b + p * q0 + r1
    f = [1, p + q0, ["a", 1], b * q0 + r0]
    return _ident(f, [1, p, ["b", 1]], [1, q0], [r1, r0])


v12522 = _ident([1, 1, ["a", 1], 2], [1, 2, ["b", 1]], [1, -1], [1, 5])


def _div(f: list, cond: dict, stem: str, params: list, quotient: bool = False) -> dict[str, Any]:
    return {"form": "division", "params": params, "f": f, "conditions": cond, "ask_quotient": quotient, "stem": stem}


def s12529(rng):
    p, q = nz(rng, -3, 3), nz(rng, -4, 4)
    m, n, r = pick(rng, [1, 2, 3]), nz(rng, -3, 3), nz(rng, -5, 5)
    f = [m, ["a", 1], q * m + p * n, q * n + r]
    return _div(f, [{"divisor": [1, p, q], "remainder": [r]}], "remainder_quotient", ["a"], True)


v12529 = _div([2, ["a", 1], -8, 7], [{"divisor": [1, 2, -3], "remainder": [4]}], "remainder_quotient", ["a"], True)


def s12533(rng):
    p, q = nz(rng, -3, 3), nz(rng, -3, 3)
    m, n = pick(rng, [1, 2, 3]), nz(rng, -3, 3)
    f = [m, n + p * m, ["a", 1], ["b", 1]]
    return _div(f, [{"divisor": [1, p, q], "remainder": []}], "divisible_quotient", ["a", "b"], True)


v12533 = _div([2, -1, ["a", 1], ["b", 1]], [{"divisor": [1, -2, -1], "remainder": []}], "divisible_quotient", ["a", "b"], True)


def s12553(rng):
    m, k = pick(rng, [1, 2, 3]), nz(rng, -3, 3)
    root = Fraction(-k, m)
    lead, c1 = pick(rng, [1, 2, 3, -1]), pick(rng, [0, 0, 1, -1, 2])
    a = nz(rng, -4, 4)
    c0 = -(lead * root ** 3 + a * root ** 2 + c1 * root)
    if c0.denominator != 1 or c0 == 0:
        raise ValueError("non-integral constant")
    return _div([lead, ["a", 1], c1, int(c0)], [{"divisor": [m, k], "remainder": []}], "factor_of", ["a"])


v12553 = _div([2, ["a", 1], 0, 1], [{"divisor": [2, 1], "remainder": []}], "factor_of", ["a"])


def s12557(rng):
    c1, c2 = rng.sample([1, -1, 2, -2, 3], 2)
    a, b = nz(rng, -3, 3), nz(rng, -4, 4)
    c0 = -(c1 ** 3 + 3 * a * c1 ** 2 + b * c1)
    rem = c2 ** 3 + 3 * a * c2 ** 2 + b * c2 + c0
    return _div([1, ["a", 3], ["b", 1], c0],
                [{"divisor": lin(c1), "remainder": []}, {"divisor": lin(c2), "remainder": [rem]}], "two_conditions", ["a", "b"])


v12557 = _div([1, ["a", 3], ["b", 1], -2], [{"divisor": [1, -1], "remainder": []}, {"divisor": [1, -2], "remainder": [2]}],
              "two_conditions", ["a", "b"])


def s12558(rng):
    n, c = rng.randint(3, 7), pick(rng, [-2, -1, 1, 2])
    m = pick(rng, [1, 1, 2])
    return _div([m] + [0] * (n - 1) + [["a", 1]], [{"divisor": lin(c), "remainder": []}], "product_form", ["a"], True)


v12558 = _div([1, 0, 0, 0, 0, ["a", 1]], [{"divisor": [1, 1], "remainder": []}], "product_form", ["a"], True)


# --- D. taylor_shift_expansion -----------------------------------------------------------------------

def _taylor(f: list, center: Any, x0: Any, style: str) -> dict[str, Any]:
    return {"poly_coeffs": f, "center": center, "approx_x": x0, "style": style}


def _taylor_sampler(style: str, centers: list, lead_pool: list):
    def sampler(rng):
        c = pick(rng, centers)
        step = "0.01" if fr(c).denominator == 1 else "0.005"
        x0 = fr(c) + pick(rng, [1, -1]) * fr(step)
        f = [pick(rng, lead_pool), nz(rng, -6, 6), nz(rng, -6, 6), nz(rng, -6, 6)]
        return _taylor(f, c, str(float(x0)), style)
    return sampler


s12524 = _taylor_sampler("numbered", [2, 1, -1, 3, -2], [1, 1, 2, -1])
s12531 = _taylor_sampler("single", [1, 2, -1, 3], [2, 1, -2, 3])
s12537 = _taylor_sampler("synthetic_numbered", ["1/2", "-1/2", "3/2"], [8, 4, 2, -8])
v12524 = _taylor([1, -1, -1, 1], 2, "1.99", "numbered")
v12531 = _taylor([2, -5, 6, 3], 1, "0.99", "single")
v12537 = _taylor([8, 4, -4, 7], "1/2", "0.505", "synthetic_numbered")


# --- E. evaluate_polynomial_values -------------------------------------------------------------------

def _values(items: list, style: str) -> dict[str, Any]:
    return {"items": items, "style": style}


def _val_item(f: list, x: Any, kind: str = "value") -> dict[str, Any]:
    return {"kind": kind, "poly": f, "x": x}


def s12538(rng):
    return _values([_val_item([rng.randint(60, 150), -rng.randint(150, 400), rng.randint(20, 90), -rng.randint(10, 60), -rng.randint(5, 40)],
                              pick(rng, [2, 3, 4, 5, -2, -3]))], "value")


v12538 = _values([_val_item([123, -389, 68, -32, -19], 3)], "value")


def s12541(rng):
    return _values([_val_item([rng.randint(2, 5), -rng.randint(10, 40), -rng.randint(5, 20), -rng.randint(10, 50), rng.randint(5, 30), rng.randint(2, 9)],
                              pick(rng, [5, 6, 7, 8, 9, -5]))], "value")


v12541 = _values([_val_item([3, -22, -12, -33, 10, 5], 8)], "value")


def s12540(rng):
    n = rng.randint(5, 8)
    k = pick(rng, [2, 3])
    f = [pick(rng, [1, 2, 3]) * k ** n] + [0] * (n - 3) + [nz(rng, -5, 5), nz(rng, -5, 5), nz(rng, -5, 5)]
    return _values([{"kind": "remainder_linear", "poly": f, "divisor": [k, 1]}], "remainder_single")


v12540 = _values([{"kind": "remainder_linear", "poly": [128, 0, 0, 0, 0, 4, -2, 3], "divisor": [2, 1]}], "remainder_single")


def s12525(rng):
    n = rng.randint(4, 6)
    k = pick(rng, [2, 3])
    f = [pick(rng, [1, 2]) * k ** n] + [0] * (n - 2) + [k * nz(rng, -3, 3), nz(rng, -5, 5)]
    u = nz(rng, -3, 3)
    return _values([{"kind": "remainder_linear", "poly": f, "divisor": [1, u]}, {"kind": "remainder_linear", "poly": f, "divisor": [k, -1]}],
                   "remainder_pair")


v12525 = _values([{"kind": "remainder_linear", "poly": [64, 0, 0, 0, 0, -4, 5], "divisor": [1, 1]},
                  {"kind": "remainder_linear", "poly": [64, 0, 0, 0, 0, -4, 5], "divisor": [2, -1]}], "remainder_pair")


def s12536(rng):
    x = pick(rng, [10, 11, 12, 13, 15, 20])
    return _values([_val_item([1] + [nz(rng, -60, 60) for _ in range(4)] + [nz(rng, -300, 300)], x, "expression")], "expression")


v12536 = _values([_val_item([1, -7, -58, 16, -465, 100], 12, "expression")], "expression")


# --- F. solve_remainder_from_conditions --------------------------------------------------------------

def _rem_cond(conditions: list, target: list, form: str, joiner: str) -> dict[str, Any]:
    return {"conditions": conditions, "target": target, "target_form": form, "joiner": joiner}


def _two_linear(rng: random.Random, form: str, joiner: str) -> dict[str, Any]:
    c1, c2 = rng.sample([-4, -3, -2, -1, 1, 2, 3, 4], 2)
    v1, v2 = nz(rng, -9, 9), nz(rng, -9, 9)
    return _rem_cond([{"divisor": lin(c1), "remainder": [v1]}, {"divisor": lin(c2), "remainder": [v2]}],
                     jl(prod(lin(c1), lin(c2))), form, joiner)


def s12539(rng): return _two_linear(rng, "factored", "，且")


def s12545(rng): return _two_linear(rng, "factored", "；")


def s12542(rng):
    out = _two_linear(rng, "expanded", "；")
    return out


v12539 = _rem_cond([{"divisor": [1, -1], "remainder": [6]}, {"divisor": [1, -2], "remainder": [4]}], [1, -3, 2], "factored", "，且")
v12545 = _rem_cond([{"divisor": [1, -2], "remainder": [8]}, {"divisor": [1, 1], "remainder": [2]}], [1, -1, -2], "factored", "；")
v12542 = _rem_cond([{"divisor": [1, -3], "remainder": [16]}, {"divisor": [1, 4], "remainder": [-19]}], [1, 1, -12], "expanded", "；")


def s12547(rng):
    a1, a2, c2 = rng.sample([-4, -3, -2, -1, 1, 2, 3, 4, 5], 3)
    r1 = [nz(rng, -3, 3), nz(rng, -5, 5)]
    shared = pick(rng, [a1, a2])
    v = nz(rng, -9, 9)
    return _rem_cond([{"divisor": jl(prod(lin(a1), lin(a2))), "remainder": r1}, {"divisor": lin(c2), "remainder": [v]}],
                     jl(prod(lin(shared), lin(c2))), "expanded", "；")


v12547 = _rem_cond([{"divisor": [1, -4, -5], "remainder": [3, -2]}, {"divisor": [1, -2], "remainder": [4]}], [1, -1, -2], "expanded", "；")


# --- G. remainders with unknown polynomials ----------------------------------------------------------

def _congruences(degree: int, conditions: list) -> dict[str, Any]:
    return {"degree": degree, "conditions": conditions}


def s12548(rng):
    f = rpoly(rng, 3, -4, 4, (1, 2))
    d1 = [1, nz(rng, -2, 2), nz(rng, -3, 3)]
    d2 = [1, nz(rng, -2, 2), nz(rng, -3, 3)]
    if d1 == d2:
        raise ValueError("same divisors")
    return _congruences(3, [{"divisor": d1, "remainder": jl(pdivmod(poly(f), poly(d1))[1])},
                            {"divisor": d2, "remainder": jl(pdivmod(poly(f), poly(d2))[1])}])


v12548 = _congruences(3, [{"divisor": [1, 1, 2], "remainder": [1, 2]}, {"divisor": [1, 1, -2], "remainder": [5, -2]}])


def _linear_part(roots: list, k: int, first: int, last: int) -> dict[str, Any]:
    return {"roots": roots, "k": k, "first_value": first, "last_value": last}


def s12549(rng):
    roots = sorted(rng.sample([-3, -2, -1, 0, 1, 2, 3, 4], 3))
    k = nz(rng, -4, 4)
    g = [nz(rng, -3, 3), nz(rng, -6, 6)]
    r1, r2, r3 = roots
    first = value(g, r1)
    last = k * (r3 - r1) * (r3 - r2) + value(g, r3)
    return _linear_part(roots, k, j(first), j(last))


v12549 = _linear_part([1, 2, 3], 3, -3, 7)


# --- H. interpolate_polynomials ----------------------------------------------------------------------

def _interp(items: list, style: str, last: str) -> dict[str, Any]:
    return {"items": items, "style": style, "last": last}


def _points(f: Any, xs: list) -> list:
    return [[x, j(value(f, x))] for x in xs]


def _two_zero_cubic(rng):
    r1, r2 = rng.sample([-3, -2, -1, 0, 1, 2, 3], 2)
    others = rng.sample([x for x in range(-4, 6) if x not in (r1, r2)], 2)
    f = prod(lin(r1), lin(r2), [pick(rng, [1, 2, 3]), nz(rng, -5, 5)])
    return {"degree": 3, "points": [[r1, 0], [r2, 0]] + _points(f, sorted(others))}


def s12551(rng): return _interp([_two_zero_cubic(rng)], "cubic_full", "與")


v12551 = _interp([{"degree": 3, "points": [[1, 0], [2, 0], [3, 2], [4, 18]]}], "cubic_full", "與")


def s12554(rng):
    start = rng.randint(-2, 1)
    zeros = [start, start + 1, start + 2]
    a = nz(rng, -3, 4)
    f = [a * c for c in prod(lin(zeros[0]), lin(zeros[1]), lin(zeros[2]))]
    x4 = pick(rng, [z for z in range(-4, 7) if z not in zeros])
    return _interp([{"degree": 3, "points": [[z, 0] for z in zeros] + [[x4, j(value(f, x4))]]}], "is_cubic", "且")


v12554 = _interp([{"degree": 3, "points": [[0, 0], [1, 0], [2, 0], [3, 24]]}], "is_cubic", "且")


def _equal_value_cubic(rng):
    xs = sorted(rng.sample([-5, -4, -3, -2, -1, 1, 2], 4))
    v = nz(rng, -6, 6)
    a = nz(rng, -3, 3)
    f = padd(pscale(prod(lin(xs[0]), lin(xs[1]), lin(xs[2])), Fraction(a)), poly([v]))
    return {"degree": 3, "points": [[x, v] for x in xs[:3]] + [[xs[3], j(value(f, xs[3]))]]}


def s12559(rng): return _interp([_two_zero_cubic(rng), _equal_value_cubic(rng)], "items", "與")


v12559 = _interp([{"degree": 3, "points": [[-1, 0], [-2, 0], [1, 6], [2, 48]]}, {"degree": 3, "points": [[-1, 5], [-2, 5], [-3, 5], [-4, -7]]}],
                 "items", "與")


# --- I / J / K / M -----------------------------------------------------------------------------------

def _factors(f: list, cands: list) -> dict[str, Any]:
    return {"poly_coeffs": f, "candidates": cands}


def s12550(rng):
    roots = rng.sample([fr(x) for x in (-2, -1, 1, 2, 3, "1/2", "-1/2")], 3)
    f = prod(*[_linear_of(r) for r in roots])
    f = pscale(f, Fraction(pick(rng, [1, 2, 3])))
    true_root = pick(rng, roots)
    wrong = pick(rng, [fr(x) for x in (-3, 3, "1/3", "2", "-1", "5") if fr(x) not in roots])
    k = pick(rng, [2, 3])
    cands = [_linear_of(true_root), _linear_of(wrong), [k * _linear_of(true_root)[0], k * _linear_of(true_root)[1]], _linear_of(pick(rng, roots))]
    rng.shuffle(cands)
    f_int = [int(c) if c.denominator == 1 else None for c in f]
    if any(c is None for c in f_int):
        raise ValueError("non-integral polynomial")
    return _factors(f_int, cands)


v12550 = _factors([2, -1, 0, -2, 1], [[1, 1], [1, -1], [2, -1], [6, -3]])


def _erased(known: list, root: int) -> dict[str, Any]:
    return {"known": known, "root": root}


def s12552(rng):
    roots = rng.sample([-4, -3, -2, -1, 1, 2, 3, 4, 5], 3)
    c = prod(*[lin(r) for r in roots])
    return _erased([1, int(c[1]), int(c[2])], pick(rng, roots))


v12552 = _erased([1, 3, -4], 2)


def _masked(coeffs: list, idx: int, root: int, rem: Any) -> dict[str, Any]:
    return {"coefficients": coeffs, "mask_index": idx, "root": root, "remainder": rem}


def s12555(rng):
    n = rng.randint(5, 8)
    root = pick(rng, [-3, -2, 2, 3, -1, 1])
    f = [0] * (n + 1)
    for i in rng.sample(range(1, n + 1), 3):
        f[i] = nz(rng, -5, 5)
    f[-1] = f[-1] or nz(rng, -5, 5)
    f[0] = pick(rng, [1, 2, 3, -1, -2])
    rem = value(f, root)
    return _masked([None] + f[1:], 0, root, j(rem))


v12555 = _masked([None, 0, 0, 0, 1, 0, 0, 3, -5], 0, -2, 8)


def _divisor(f: list, q: list, r: list) -> dict[str, Any]:
    return {"dividend": f, "quotient": q, "remainder": r}


def s12535(rng):
    g = [pick(rng, [1, 1, 2]), nz(rng, -3, 3), nz(rng, -4, 4)]
    q = [1, nz(rng, -3, 3)]
    r = [nz(rng, -3, 3), nz(rng, -4, 4)]
    return _divisor(jl(padd(pmul(poly(g), poly(q)), poly(r))), q, r)


v12535 = _divisor([1, 4, 5, -3], [1, 2], [2, -1])


# --- component table ---------------------------------------------------------------------------------

def _c(skill: str, op: str, source: dict, sampler: Callable) -> tuple:
    return (skill, op, source, sampler)


COMPONENTS: dict[int, tuple] = {
    12517: _c("basic", "evaluate_polynomial_statements", v12517, s12517),
    12518: _c("remainder", "evaluate_polynomial_statements", v12518, s12518),
    12519: _c("factor", "evaluate_polynomial_statements", v12519, s12519),
    12520: _c("arith", "polynomial_arithmetic_items", v12520, s12520),
    12521: _c("arith", "polynomial_arithmetic_items", v12521, s12521),
    12522: _c("arith", "solve_polynomial_parameters", v12522, s12522),
    12523: _c("arith", "polynomial_arithmetic_items", v12523, s12523),
    12524: _c("arith", "taylor_shift_expansion", v12524, s12524),
    12525: _c("remainder", "evaluate_polynomial_values", v12525, s12525),
    12526: _c("arith", "polynomial_arithmetic_items", v12526, s12526),
    12527: _c("arith", "polynomial_arithmetic_items", v12527, s12527),
    12528: _c("arith", "evaluate_polynomial_statements", v12528, s12528),
    12529: _c("arith", "solve_polynomial_parameters", v12529, s12529),
    12530: _c("arith", "polynomial_arithmetic_items", v12530, s12530),
    12531: _c("arith", "taylor_shift_expansion", v12531, s12531),
    12532: _c("arith", "polynomial_arithmetic_items", v12532, s12532),
    12533: _c("arith", "solve_polynomial_parameters", v12533, s12533),
    12534: _c("arith", "polynomial_arithmetic_items", v12534, s12534),
    12535: _c("arith", "solve_divisor_from_quotient_remainder", v12535, s12535),
    12536: _c("remainder", "evaluate_polynomial_values", v12536, s12536),
    12537: _c("arith", "taylor_shift_expansion", v12537, s12537),
    12538: _c("remainder", "evaluate_polynomial_values", v12538, s12538),
    12539: _c("remainder", "solve_remainder_from_conditions", v12539, s12539),
    12540: _c("remainder", "evaluate_polynomial_values", v12540, s12540),
    12541: _c("remainder", "evaluate_polynomial_values", v12541, s12541),
    12542: _c("remainder", "solve_remainder_from_conditions", v12542, s12542),
    12543: _c("remainder", "evaluate_polynomial_statements", v12543, s12543),
    12544: _c("remainder", "evaluate_polynomial_statements", v12544, s12544),
    12545: _c("remainder", "solve_remainder_from_conditions", v12545, s12545),
    12546: _c("remainder", "evaluate_polynomial_statements", v12546, s12546),
    12547: _c("remainder", "solve_remainder_from_conditions", v12547, s12547),
    12548: _c("remainder", "solve_polynomial_from_remainder_congruences", v12548, s12548),
    12549: _c("remainder", "solve_remainder_with_linear_part", v12549, s12549),
    12550: _c("factor", "select_linear_factors", v12550, s12550),
    12551: _c("factor", "interpolate_polynomials", v12551, s12551),
    12552: _c("factor", "solve_erased_cubic", v12552, s12552),
    12553: _c("factor", "solve_polynomial_parameters", v12553, s12553),
    12554: _c("factor", "interpolate_polynomials", v12554, s12554),
    12555: _c("factor", "solve_masked_synthetic_coefficient", v12555, s12555),
    12556: _c("factor", "evaluate_polynomial_statements", v12556, s12556),
    12557: _c("factor", "solve_polynomial_parameters", v12557, s12557),
    12558: _c("factor", "solve_polynomial_parameters", v12558, s12558),
    12559: _c("factor", "interpolate_polynomials", v12559, s12559),
}
