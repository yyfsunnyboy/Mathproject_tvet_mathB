"""Per-component *inputs* for 普高數學1 Unit 3 (指數).

Each entry gives the source-faithful givens (variant 0) and a sampler for further variants of
the same shape.  Samplers only choose inputs; the domain computes every answer.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Callable

SKILLS = {
    "pos": "gh_PositiveIntegerExponentsAndLaws",
    "int": "gh_IntegerExponentsAndLaws",
    "rat": "gh_RationalExponentsAndLaws",
    "real": "gh_RealExponentsAndLaws",
    "sn": "gh_ScientificNotationAndItsOperations",
    "cl": "gh_CommonLogarithms",
}


# --- tree helpers ----------------------------------------------------------------

def _t(x: Any) -> list:
    if isinstance(x, list):
        return x
    if isinstance(x, Fraction):
        return ["n", f"{x.numerator}" if x.denominator == 1 else f"{x.numerator}/{x.denominator}"]
    return ["n", str(x)]


def P(b: Any, e: Any) -> list: return ["pow", _t(b), _t(e)]
def M(*a: Any) -> list: return ["mul", *[_t(x) for x in a]]
def J(*a: Any) -> list: return ["jux", *[_t(x) for x in a]]
def D(a: Any, b: Any) -> list: return ["div", _t(a), _t(b)]
def A(*a: Any) -> list: return ["add", *[_t(x) for x in a]]
def Sb(a: Any, b: Any) -> list: return ["sub", _t(a), _t(b)]
def Ng(a: Any) -> list: return ["neg", _t(a)]
def Sq(x: Any) -> list: return ["sqrt", _t(x)]
def Rt(k: int, x: Any) -> list: return ["root", k, _t(x)]
def V(name: str) -> list: return ["sym", name]
PI = ["pi"]


def fr(num: int, den: int = 1) -> Fraction:
    return Fraction(num, den)


def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


# --- O1 simplify_exponent_expressions ----------------------------------------------

def _o1(stem: str, items: list) -> dict[str, Any]:
    return {"stem": stem, "items": items}


def s12339(rng):
    b = pick(rng, [2, 3, 5, 7, 4]); m, n = rng.randint(2, 6), rng.randint(2, 6)
    c = pick(rng, [-1, -2, 2, -3, 3]); k, l = rng.randint(2, 4), rng.randint(2, 3)
    x, y = pick(rng, [-2, -3, -4, -5, 3, 4]), pick(rng, [2, 3, 5]); e = rng.randint(2, 4)
    return _o1("利用指數律求下列各式的值：", [M(P(b, m), P(b, n)), P(P(c, k), l), M(P(x, e), P(y, e))])


v12339 = _o1("利用指數律求下列各式的值：", [M(P(2, 3), P(2, 5)), P(P(-1, 2), 3), M(P(-5, 3), P(2, 3))])


def s12343(rng):
    k = pick(rng, [64, 49, 81, 100, 36, 25]); m, n = rng.randint(10, 99), rng.randint(2, 12)
    b = pick(rng, [2, 3, 5, 7]); p, q = rng.randint(2, 6), rng.randint(2, 9)
    return _o1("求下列各式的值：", [P(A(P(PI, m), P(k, n)), 0), D(P(b, p), P(b, q))])


v12343 = _o1("求下列各式的值：", [P(A(P(PI, 25), P(64, 10)), 0), D(P(3, 5), P(3, 7))])


def s12344(rng):
    b = pick(rng, [-5, -3, -2, 5, 3, 7]); m, n = rng.randint(2, 4), rng.randint(2, 5)
    c = pick(rng, [4, 2, 3, 5]); i, j = pick(rng, [-1, -2]), pick(rng, [-2, -3])
    d, e = pick(rng, [3, 7, 11]), pick(rng, [2, 3, 5]); k = pick(rng, [-2, -3])
    return _o1("利用指數律求下列各式的值：",
               [M(P(b, m), P(b, -n)), P(P(c, i), j), M(P(d * e, k), P(fr(1, d), k))])


v12344 = _o1("利用指數律求下列各式的值：", [M(P(-5, 3), P(-5, -4)), P(P(4, -1), -2), M(P(21, -2), P(fr(1, 7), -2))])


def s12347(rng):
    k, m, n = pick(rng, [3, 2, 5, 7]), rng.randint(2, 200), rng.randint(2, 9)
    b = pick(rng, [2, 3, 5]); p, q = rng.randint(1, 4), rng.randint(2, 6)
    return _o1("求下列各式的值：", [D(1, P(A(P(k, m), P(PI, n)), 0)), D(P(b, -p), P(b, -q))])


v12347 = _o1("求下列各式的值：", [D(1, P(A(P(3, 107), P(PI, 2)), 0)), D(P(2, -1), P(2, -3))])


def _root_power_item(rng):
    b = pick(rng, [2, 3, 5, 7]); k = pick(rng, [2, 3, 5]); m = pick(rng, [3, 5, 2, 4, 7]); j = rng.randint(1, 4)
    return P(Rt(k, P(b, m)), fr(k * j, m))


def _prod_item(rng):
    a = pick(rng, [7, 5, 3, 2]); c = pick(rng, [4, 9, 16, 25, 36]); s = pick(rng, [fr(3, 2), fr(1, 2), fr(5, 2)])
    if a == c:
        c *= 4
    return M(P(a, s), P(fr(c, a), s))


def s12352(rng): return _o1("利用指數律，求下列各式的值：", [_root_power_item(rng), _prod_item(rng)])


v12352 = _o1("利用指數律，求下列各式的值：", [P(Rt(3, P(2, 5)), fr(12, 5)), M(P(7, fr(3, 2)), P(fr(4, 7), fr(3, 2)))])


def s12356(rng):
    b = pick(rng, [7, 3, 5, 2]); k = pick(rng, [5, 4, 3]); m = pick(rng, [3, 2, 5]); j = rng.randint(1, 3)
    a = pick(rng, [5, 3, 7, 2]); c = pick(rng, [16, 81, 256, 625]); s = pick(rng, [fr(1, 4), fr(3, 4), fr(1, 2)])
    return _o1("利用指數律，求下列各式的值：", [P(Rt(k, P(b, m)), fr(k * j, m)), M(P(a, s), P(fr(c, a), s))])


v12356 = _o1("利用指數律，求下列各式的值：", [P(Rt(5, P(7, 3)), fr(10, 3)), M(P(5, fr(1, 4)), P(fr(16, 5), fr(1, 4)))])


def s12362(rng):
    p, q = pick(rng, [(5, 2), (7, 3), (6, 2), (10, 3), (5, 3), (7, 2)]); e = rng.randint(2, 4)
    r = pick(rng, [5, 3, 7, 2]); s, t = rng.randint(2, 4), pick(rng, [-2, -1, -3])
    w, x = pick(rng, [(64, fr(2, 3)), (27, fr(2, 3)), (8, fr(4, 3)), (125, fr(2, 3)), (16, fr(3, 4)), (32, fr(3, 5)), (64, fr(5, 6))])
    (u1, v1) = pick(rng, [(16, 25), (4, 9), (9, 25), (49, 16)])
    (u2, v2, e2) = pick(rng, [(27, 8, fr(2, 3)), (8, 27, fr(2, 3)), (64, 125, fr(2, 3)), (125, 8, fr(1, 3))])
    d, e3 = pick(rng, ["0.25", "0.04", "0.09", "0.16", "0.01", "0.49"]), pick(rng, ["-0.5", "-1.5", "-2.5"])
    return _o1("求下列各式的值：", [
        M(P(Sb(Sq(p), Sq(q)), e), P(A(Sq(p), Sq(q)), e)),
        P(P(Sq(r), s), t), P(w, x),
        M(P(fr(u1, v1), "-0.5"), P(fr(u2, v2), e2), P(d, e3)),
    ])


v12362 = _o1("求下列各式的值：", [
    M(P(Sb(Sq(5), Sq(2)), 3), P(A(Sq(5), Sq(2)), 3)), P(P(Sq(5), 3), -2), P(64, fr(2, 3)),
    M(P(fr(16, 25), "-0.5"), P(fr(27, 8), fr(2, 3)), P("0.25", "-2.5")),
])


def s12367(rng):
    b, r1 = pick(rng, [10, 2, 3, 5]), pick(rng, [2, 3, 5, 6, 7])
    c, r2, k = pick(rng, [2, 3, 5, 7]), pick(rng, [2, 3, 5]), pick(rng, [1, 2, 3])
    (p, q), r3, k3 = pick(rng, [(3, 2), (2, 3), (5, 3), (4, 3)]), pick(rng, [2, 3, 5]), pick(rng, [2, 3])
    return _o1("利用指數律，求下列各式的值：", [
        M(P(b, Sq(r1)), P(b * b, D(Sb(1, Sq(r1)), 2))),
        P(P(c, Sq(r2)), J(k, Sq(r2))),
        M(P(fr(p, q), J(k3, Sq(r3))), P(fr(q, p), Sq(k3 * k3 * r3))),
    ])


v12367 = _o1("利用指數律，求下列各式的值：", [
    M(P(10, Sq(2)), P(100, D(Sb(1, Sq(2)), 2))), P(P(3, Sq(2)), J(2, Sq(2))),
    M(P(fr(3, 2), J(2, Sq(3))), P(fr(2, 3), Sq(12))),
])


def s12370(rng):
    b, r1 = pick(rng, [fr(1, 2), fr(1, 3), fr(2, 3), fr(3, 2)]), pick(rng, [3, 2, 5, 7])
    c, r2 = pick(rng, [9, 16, 25, 4, 36]), pick(rng, [2, 3, 5])
    base, k, r3 = pick(rng, [2, 3, 5]), pick(rng, [2, 3, 4]), pick(rng, [2, 3, 5])
    return _o1("利用指數律，求下列各式的值：", [
        M(P(b, A(1, Sq(r1))), P(b, Sb(1, Sq(r1)))),
        P(P(c, Sq(r2)), D(1, J(2, Sq(r2)))),
        D(P(base, Sq(k * k * r3)), P(P(base ** k, 1), Sq(r3))),
    ])


v12370 = _o1("利用指數律，求下列各式的值：", [
    M(P(fr(1, 2), A(1, Sq(3))), P(fr(1, 2), Sb(1, Sq(3)))), P(P(9, Sq(2)), D(1, J(2, Sq(2)))),
    D(P(3, Sq(18)), P(27, Sq(2))),
])


def s12363(rng):
    m, n, k = rng.randint(2, 4), -rng.randint(1, 3), pick(rng, [-3, -2, 2, 3])
    if m + n == 0:
        m += 1
    c, d, i = pick(rng, [2, 4, 8, 1]), pick(rng, [2, 4, 1, 8]), pick(rng, [1, 2, 3])
    u = pick(rng, [fr(1, 2), fr(1, 3), fr(1, 4), fr(2, 3)])
    return _o1("設 $a>0$，化簡下列各式：", [
        P(J(P(V("a"), m), P(V("a"), n)), k),
        D(P(J(c, P(V("a"), -1)), fr(1, 3)), P(J(d, V("a")), fr(-4, 3))),
        J(A(P(V("a"), u), P(V("a"), -u)), Sb(P(V("a"), u), P(V("a"), -u))),
    ])


v12363 = _o1("設 $a>0$，化簡下列各式：", [
    P(J(P(V("a"), 3), P(V("a"), -2)), -3),
    D(P(J(2, P(V("a"), -1)), fr(1, 3)), P(J(4, V("a")), fr(-4, 3))),
    J(A(P(V("a"), fr(1, 2)), P(V("a"), fr(-1, 2))), Sb(P(V("a"), fr(1, 2)), P(V("a"), fr(-1, 2)))),
])


# --- O2 solve_exponent_blank_equations ---------------------------------------------

def _blank(stem, items): return {"stem": stem, "items": items}


def s12341(rng):
    b, m, n = pick(rng, [-3, 2, -2, 5, -5, 3]), rng.randint(2, 7), rng.randint(2, 7)
    base, i, o = pick(rng, [2, 3, 5]), pick(rng, [2, 3, 4]), rng.randint(3, 9)
    n3, j = pick(rng, [3, 4, 5]), rng.randint(1, 3)
    b1, b2 = pick(rng, [2, 3, 5]), pick(rng, [-2, -3, 3, 5, -5])
    if b1 == abs(b2):
        b2 = -7
    return _blank("利用指數律完成下列填空：", [
        {"kind": "product_to_base", "factors": [[str(b), m], [str(b), n]], "result_base": str(b)},
        {"kind": "power_power", "base": str(base), "inner": i, "outer": None, "result_base": str(base), "result_exp": i * o},
        {"kind": "merge_bases", "factors": [[str(b1), n3 * j], [str(b2), n3]], "common_exponent": n3},
    ])


v12341 = _blank("利用指數律完成下列填空：", [
    {"kind": "product_to_base", "factors": [["-3", 4], ["-3", 5]], "result_base": "-3"},
    {"kind": "power_power", "base": "2", "inner": 4, "outer": None, "result_base": "2", "result_exp": 20},
    {"kind": "merge_bases", "factors": [["2", 10], ["-3", 5]], "common_exponent": 5},
])


def s12348(rng):
    b, m, n = pick(rng, [3, 2, 5]), rng.randint(2, 7), rng.randint(3, 9)
    base, o, re_ = pick(rng, [2, 3, 5]), pick(rng, [3, 4, 5]), 0
    re_ = o * rng.randint(2, 4)
    inv = rng.random() < 0.5
    n3, j = pick(rng, [3, 4, 5]), rng.randint(1, 3)
    b1, b2 = pick(rng, [2, 3, 5]), pick(rng, [3, 5, 7])
    if b1 == b2:
        b2 = 7
    return _blank("利用指數律完成下列填空：", [
        {"kind": "product_to_base", "factors": [[f"1/{b}", m], [str(b), -n]], "result_base": str(b)},
        {"kind": "power_power", "base": str(base), "inner": None, "outer": o,
         "result_base": f"1/{base}" if inv else str(base), "result_exp": re_},
        {"kind": "merge_bases", "factors": [[str(b1), -n3 * j], [str(b2), -n3]], "common_exponent": -n3},
    ])


v12348 = _blank("利用指數律完成下列填空：", [
    {"kind": "product_to_base", "factors": [["1/3", 5], ["3", -8]], "result_base": "3"},
    {"kind": "power_power", "base": "2", "inner": None, "outer": 5, "result_base": "1/2", "result_exp": 15},
    {"kind": "merge_bases", "factors": [["2", -10], ["3", -5]], "common_exponent": -5},
])


# --- O3 evaluate_conditional_exponent_values --------------------------------------

def _roots_sym(c: int, sign_set=(1, -1), half=False) -> list[str]:
    out = []
    for sgn in sign_set:
        root = f"(({c} + ({sgn})*sqrt({c * c - 4}))/2)"
        out.append(f"{root}**2" if half else root)
    return out


def _cond(prefix, lhs, rhs, roots, targets, var="a"):
    return {"stem_prefix": prefix, "var": var, "condition": {"lhs": lhs, "rhs": _t(rhs)}, "roots": roots, "targets": targets,
            "assume_positive": "a>0" in prefix}


a_ = V("a")


def _nonsq(c: int, delta: int) -> bool:
    from math import isqrt
    v = c * c + delta
    return v > 0 and isqrt(v) ** 2 != v


def s12345(rng):
    c = rng.randint(3, 22)
    while not _nonsq(c, -4):
        c = rng.randint(3, 22)
    return _cond("已知 $a>0$ 且 ", A(a_, P(a_, -1)), c, _roots_sym(c), [A(P(a_, 2), P(a_, -2)), A(P(a_, 3), P(a_, -3))])


v12345 = s12345(random.Random(0)); v12345 = _cond("已知 $a>0$ 且 ", A(a_, P(a_, -1)), 3, _roots_sym(3), [A(P(a_, 2), P(a_, -2)), A(P(a_, 3), P(a_, -3))])


def s12349(rng):
    d = rng.randint(1, 40)
    return _cond("已知 $a>0$ 且 ", Sb(a_, P(a_, -1)), d, [f"({d} + sqrt({d * d + 4}))/2"], [A(P(a_, 2), P(a_, -2)), A(P(a_, 4), P(a_, -4))])


v12349 = _cond("已知 $a>0$ 且 ", Sb(a_, P(a_, -1)), 2, ["(2 + sqrt(8))/2"], [A(P(a_, 2), P(a_, -2)), A(P(a_, 4), P(a_, -4))])


def s12353(rng):
    c = rng.randint(3, 22)
    while not _nonsq(c, -4):
        c = rng.randint(3, 22)
    return _cond("已知 $a>0$ 且 ", A(a_, P(a_, -1)), c, _roots_sym(c), [A(P(a_, fr(1, 2)), P(a_, fr(-1, 2)))])


v12353 = _cond("已知 $a>0$ 且 ", A(a_, P(a_, -1)), 4, _roots_sym(4), [A(P(a_, fr(1, 2)), P(a_, fr(-1, 2)))])


def s12357(rng):
    c = rng.randint(3, 22)
    while not _nonsq(c, -4):
        c = rng.randint(3, 22)
    return _cond("已知 $a>0$ 且 ", A(P(a_, fr(1, 2)), P(a_, fr(-1, 2))), c, _roots_sym(c, half=True),
                 [A(P(a_, fr(1, 4)), P(a_, fr(-1, 4)))])


v12357 = _cond("已知 $a>0$ 且 ", A(P(a_, fr(1, 2)), P(a_, fr(-1, 2))), 3, _roots_sym(3, half=True), [A(P(a_, fr(1, 4)), P(a_, fr(-1, 4)))])


def s12368(rng):
    m, j, k = pick(rng, [3, 5, 6, 7, 10, 11]), pick(rng, [1, 2]), pick(rng, [9, 18, 6, 12, 16])
    return _cond("已知 ", P(2, a_), m, [f"log({m})/log(2)"], [P(4, Sb(a_, j)), M(k, P(8, A(Ng(a_), j)))])


v12368 = _cond("已知 ", P(2, a_), 3, ["log(3)/log(2)"], [P(4, Sb(a_, 1)), M(9, P(8, A(Ng(a_), 1)))])


def s12371(rng):
    m, k = pick(rng, [2, 4, 5, 6, 7, 10]), pick(rng, [36, 12, 18, 24, 72])
    return _cond("已知 ", P(3, a_), m, [f"log({m})/log(3)"], [P(9, A(a_, 1)), M(k, P(27, Sb(Ng(a_), 1)))])


v12371 = _cond("已知 ", P(3, a_), 2, ["log(2)/log(3)"], [P(9, A(a_, 1)), M(36, P(27, Sb(Ng(a_), 1)))])


def s12365(rng):
    n = pick(rng, [2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21, 22])
    cond_val = A(Sq(n), 1)
    return _cond("已知 ", P(9, a_), cond_val, [f"log(sqrt({n}) + 1)/log(9)"],
                 [D(A(P(27, a_), P(27, Ng(a_))), A(P(3, a_), P(3, Ng(a_))))])


v12365 = s12365(random.Random(0)); v12365 = _cond("已知 ", P(9, a_), A(Sq(2), 1), ["log(sqrt(2) + 1)/log(9)"], [D(A(P(27, a_), P(27, Ng(a_))), A(P(3, a_), P(3, Ng(a_))))])


def s12375(rng):
    c = rng.randint(3, 22)
    while not _nonsq(c, -4):
        c = rng.randint(3, 22)
    roots = [f"log(({c} + ({s})*sqrt({c * c - 4}))/2)/log(2)" for s in (1, -1)]
    return _cond("已知 ", A(P(2, a_), P(2, Ng(a_))), c, roots,
                 [A(P(4, a_), P(4, Ng(a_))), A(P(8, a_), P(8, Ng(a_))), A(P(Sq(2), a_), P(Sq(2), Ng(a_)))])


v12375 = _cond("已知 ", A(P(2, a_), P(2, Ng(a_))), 3,
               [f"log(({3} + ({s})*sqrt(5))/2)/log(2)" for s in (1, -1)],
               [A(P(4, a_), P(4, Ng(a_))), A(P(8, a_), P(8, Ng(a_))), A(P(Sq(2), a_), P(Sq(2), Ng(a_)))])


def s12376(rng):
    m = pick(rng, [5, 3, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21, 22, 23])
    return _cond("已知 ", P(4, a_), m, [f"log({m})/log(4)"], [Sb(P(8, a_), P(2, A(a_, 2)))])


v12376 = _cond("已知 ", P(4, a_), 5, ["log(5)/log(4)"], [Sb(P(8, a_), P(2, A(a_, 2)))])


# --- O4 evaluate_exponent_statement_truth ------------------------------------------

def _truth(statements, definitions=None):
    out = {"statements": statements}
    if definitions:
        out["definitions"] = definitions
    return out


def s12359(rng):
    b, (p, q) = pick(rng, [2, 3, 5, 7]), pick(rng, [(1, 3), (2, 3), (3, 4), (1, 2), (2, 5)])
    form = rng.randrange(3)
    lhs = P(b, fr(p, q))
    rhs = [D(1, P(b, q)), D(1, P(b, fr(p, q))), D(1, P(b, fr(-p, q)))][form]
    if rng.random() < 0.4:
        lhs, rhs = P(b, fr(-p, q)), D(1, P(b, fr(p, q)))
    return _truth([{"lhs": lhs, "rhs": rhs}])


v12359 = _truth([{"lhs": P(2, fr(1, 3)), "rhs": D(1, P(2, 3))}])


def s12360(rng):
    b, (p, q) = pick(rng, [2, 3, 5, 7]), pick(rng, [(2, 3), (1, 2), (3, 4), (1, 3), (2, 5)])
    lhs = P(b, fr(-p, q))
    rhs = pick(rng, [D(1, Rt(q, P(b, p))), D(1, Rt(p, P(b, q))), Ng(Rt(q, P(b, p))), Rt(q, P(b, -p))]) if q > 1 else None
    return _truth([{"lhs": lhs, "rhs": rhs}])


v12360 = _truth([{"lhs": P(5, fr(-2, 3)), "rhs": D(1, Rt(3, 25))}])


def s12361(rng):
    b, (p, q) = pick(rng, [2, 3, 5, 7]), pick(rng, [(3, 5), (2, 3), (3, 4), (5, 3), (2, 5)])
    lhs = Rt(q, P(b, p))
    rhs = pick(rng, [P(Rt(q, b), p), P(Rt(p, b), q), Rt(p, P(b, q)), P(Rt(q, b), q)])
    return _truth([{"lhs": lhs, "rhs": rhs}])


v12361 = _truth([{"lhs": Rt(5, P(2, 3)), "rhs": P(Rt(5, 2), 3)}])


def s12364(rng):
    p, q = rng.randint(2, 9), pick(rng, [1, 2, 4, 5]); a, b = V("a"), V("b")
    k = pick(rng, [5, 10, 20, 4]); m = 10 * p // q if (10 * p) % q == 0 else 10; j, c = pick(rng, [1, 2, 3]), pick(rng, [2, 1])
    fx = lambda x: f"{Fraction(x).numerator}" if Fraction(x).denominator == 1 else str(float(x)).rstrip("0").rstrip(".")
    e1 = Fraction(k * p, 10)
    e3 = Fraction(1) * (1 if c == 2 else 0) + Fraction(p, 10) + j * Fraction(q, 100)
    e4 = Fraction(p, 10) - (1 if c == 2 else 0) - Fraction(q, 100)
    wrong = rng.random() < 0.5
    s1 = {"lhs": P(a, k), "rhs": P(2, fx(e1 + (Fraction(1, 2) if wrong else 0)))}
    s2 = {"lhs": P(b, m), "rhs": a}
    s3 = {"lhs": J(c, a, P(b, j)) if c != 1 else J(a, P(b, j)), "rhs": P(2, fx(e3 + (Fraction(1, 100) if wrong else 0)))}
    s4 = {"lhs": D(a, J(c, b) if c != 1 else b), "rhs": P(2, fx(e4))}
    return _truth([s1, s2, s3, s4], {"a": P(2, fx(Fraction(p, 10))), "b": P(2, fx(Fraction(q, 100)))})


v12364 = _truth(
    [{"lhs": P(V("a"), 10), "rhs": _t(8)}, {"lhs": P(V("b"), 30), "rhs": V("a")},
     {"lhs": J(2, V("a"), P(V("b"), 2)), "rhs": P(2, "1.32")}, {"lhs": D(V("a"), J(2, V("b"))), "rhs": P(2, "0.28")}],
    {"a": P(2, "0.3"), "b": P(2, "0.01")})


# --- O5/O6 folding and tsunami -----------------------------------------------------

LANDMARKS = [
    {"name": "臺北 101", "value": 509, "text": "臺北 101 高度約 509 公尺"},
    {"name": "七星山", "value": 1120, "text": "七星山高度約 1120 公尺"},
    {"name": "玉山", "value": 3952, "text": "玉山高度約 3952 公尺"},
    {"name": "聖母峰", "value": 8844, "text": "聖母峰高度約 8844 公尺"},
]
SPEEDS = [
    {"name": "獵豹", "value": 36, "text": "獵豹約 36 公尺／秒"},
    {"name": "高鐵", "value": 80, "text": "高鐵約 80 公尺／秒"},
    {"name": "飛機", "value": 200, "text": "飛機約 200 公尺／秒"},
    {"name": "聲音", "value": 340, "text": "聲音約 340 公尺／秒"},
]


def s12340(rng):
    t, n = pick(rng, ["0.01", "0.02", "0.1", "0.05"]), rng.randint(6, 14)
    dist = pick(rng, [(384400, "地球到月球"), (149600000, "地球到太陽"), (40075, "地球赤道一圈"), (6371, "地球表面到地心")])
    return {"thickness_cm": t, "fold_count": n, "distance_km": str(dist[0]), "distance_name": dist[1]}


v12340 = {"thickness_cm": "0.01", "fold_count": 10, "distance_km": "384400", "distance_name": "地球到月球"}


def s12342(rng):
    return {"model": "folding", "thickness_cm": pick(rng, ["0.01", "0.02", "0.005", "0.1"]), "fold_count": rng.randint(18, 28),
            "options": LANDMARKS}


v12342 = {"model": "folding", "thickness_cm": "0.01", "fold_count": 25, "options": LANDMARKS}


def s12374(rng):
    return {"model": "tsunami", "depth_m": rng.randrange(100, 12000, 10), "options": SPEEDS}


v12374 = {"model": "tsunami", "depth_m": 3890, "options": SPEEDS}


# --- O7 power law ------------------------------------------------------------------

def s12346(rng):
    return {"mode": "value", "k": str(pick(rng, [100, 200, 300, 400, 500, 600])), "exponent": pick(rng, [-2, -3]),
            "distance_m": pick(rng, ["0.4", "0.5", "0.2", "0.8", "1.5", "0.25", "0.6"])}


v12346 = {"mode": "value", "k": "300", "exponent": -2, "distance_m": "0.4"}


def s12350(rng):
    d1, f = pick(rng, ["0.4", "0.5", "0.6", "0.2", "0.3"]), pick(rng, [2, 3])
    d2 = str(Fraction(d1) * f)
    return {"mode": "ratio", "k": str(pick(rng, [100, 200, 300, 400, 500])), "exponent": pick(rng, [-2, -3]),
            "from_distance_m": d1, "to_distance_m": d2.rstrip("0").rstrip(".") if "." in d2 else d2}


v12350 = {"mode": "ratio", "k": "300", "exponent": -2, "from_distance_m": "0.4", "to_distance_m": "0.8"}


# --- O8..O11 ------------------------------------------------------------------------

def s12354(rng):
    e, q = pick(rng, [("3/4", [8, 27, 64, 125, 1000]), ("2/3", [100, 400, 900, 10000])])
    return {"exponent": e, "weight_ratio": pick(rng, [16, 100, 50, 81, 30, 20, 10]), "options": [10, 20, 30, 40, 50],
            "metabolic_ratio": pick(rng, q)}


v12354 = {"exponent": "3/4", "weight_ratio": 100, "options": [10, 20, 30, 40, 50], "metabolic_ratio": 1000}


def s12358(rng):
    return {"half_life_hours": pick(rng, [2, 3, 4, 6, 8, 12]), "threshold_exponent": rng.randint(3, 8), "days": pick(rng, [1, 2, 3])}


v12358 = {"half_life_hours": 4, "threshold_exponent": 6, "days": 3}


def s12366(rng):
    return {"factor_exponent": pick(rng, [5, 4, 6]), "high": pick(rng, [7, 8, 6, 9]), "low": pick(rng, [3, 4, 2]),
            "partial_scale": pick(rng, ["5.1", "4.6", "5.4", "4.2", "5.7", "6.2"]), "reference": 3}


v12366 = {"factor_exponent": 5, "high": 7, "low": 3, "partial_scale": "5.1", "reference": 3}


def s12369(rng):
    ta, h0 = pick(rng, [(30, 180), (25, 175), (20, 170), (30, 230)]), 0
    ta, h0 = ta
    ratio = pick(rng, [2, 4, 8, 16, 32, 5, 10])
    measured = Fraction(ta) + Fraction(h0 - ta, ratio)
    return {"ambient": str(ta), "initial": str(h0), "measured": str(float(measured)).rstrip("0").rstrip("."),
            "minutes": pick(rng, [2, 3, 4, 5, 6]), "decimals": 1}


v12369 = {"ambient": "30", "initial": "180", "measured": "48.75", "minutes": 6, "decimals": 1}


# --- O12..O14 (final four) ---------------------------------------------------------

def _conv(b, e): return {"base": b, "exponent": e}


def s12351(rng):
    out = []
    for _ in range(3):
        b = pick(rng, [2, 3, 5, 7, 6, 10])
        e = pick(rng, ["1/2", "1/3", "2/3", "3/4", "1.5", "0.5", "-1/2", "-2/3", "-1/3", "2.5", "-0.5", "1/4", "3/2"])
        out.append(_conv(b, e))
    return {"conversions": out}


v12351 = {"conversions": [_conv(3, "1/2"), _conv(2, "1.5"), _conv(5, "-2/3")]}


def _rhs_tree(b: int, p: int, q: int) -> list:
    core = Sq(b) if (p, q) in ((1, 2), (-1, 2)) else (Rt(q, b) if abs(p) == 1 else Rt(q, P(b, abs(p))))
    return D(1, core) if p < 0 else core


def s12355(rng):
    b = pick(rng, [7, 5, 3, 2, 6, 11])
    e1, e2 = pick(rng, ["2/3", "3/4", "1/3", "3/5", "2/5"]), pick(rng, ["0.2", "0.5", "0.25", "0.4", "0.75", "1.5"])
    sb = pick(rng, [3, 2, 5, 7])
    p, q = pick(rng, [(-1, 2), (1, 2), (-1, 3), (1, 3), (-2, 3), (2, 3), (-1, 4)])
    return {"conversions": [_conv(b, e1), _conv(b, e2)], "solve": {"base": sb, "rhs": _rhs_tree(sb, p, q)}}


v12355 = {"conversions": [_conv(7, "2/3"), _conv(7, "0.2")], "solve": {"base": 3, "rhs": D(1, Sq(3))}}


def s12372(rng):
    ta, base, t = pick(rng, [30, 25, 20, 35]), pick(rng, ["1.25", "1.5", "1.2", "2"]), rng.randint(2, 5)
    h = rng.randint(ta + 30, ta + 160)
    measured = round(float(Fraction(ta) + Fraction(h - ta) / Fraction(base) ** t), 1)
    return {"ambient": str(ta), "measured": f"{measured:g}", "minutes": t, "decay_base": base}


v12372 = {"ambient": "30", "measured": "55.6", "minutes": 3, "decay_base": "1.25"}

PLANETS = [{"label": "金星", "n": 0}, {"label": "地球", "n": 1}, {"label": "火星", "n": 2}]


def s12373(rng):
    a, b = pick(rng, ["0.4", "0.2", "0.6", "0.5", "0.3", "0.1"]), pick(rng, ["0.3", "0.2", "0.1", "0.5", "0.4", "0.6"])
    labels = rng.sample([r["label"] for r in PLANETS], 2)
    n_of = {r["label"]: r["n"] for r in PLANETS}
    known = [{"label": lb, "distance": f"{float(Fraction(a) + Fraction(b) * 2 ** n_of[lb]):g}"} for lb in labels]
    return {"table": PLANETS, "base": "2", "known": known}


v12373 = {"table": PLANETS, "base": "2",
          "known": [{"label": "金星", "distance": "0.7"}, {"label": "火星", "distance": "1.6"}]}


# --- Unit 4 (科學記號與常用對數) ---------------------------------------------------------

def L(x: Any) -> list: return ["log", _t(x)]
def Pa(x: Any) -> list: return ["paren", _t(x)]
def sci(m: str, e: int) -> list: return Pa(M(m, P(10, e)))


def _num_text(x: Any) -> str:
    return str(x)


def _sci_item(value: str, sig: int, prompt: str) -> dict:
    return {"kind": "value", "value": value, "sig": sig, "prompt": prompt}


def _sig_prompt(what: str, sig: int) -> str:
    return f"將{what}取 ${sig}$ 位有效數字並以科學記號表示。"


def s12377(rng):
    n = rng.randint(10 ** rng.randint(6, 9), 10 ** rng.randint(9, 10) - 1)
    year = rng.randint(2010, 2023)
    sig1, sig2 = pick(rng, [(2, 3), (2, 4), (3, 4), (1, 2)])
    return {"stem": f"已知 ${year}$ 年美國的人口數為 ${n}$ 人。",
            "items": [_sci_item(str(n), sig1, _sig_prompt("人口數", sig1)), _sci_item(str(n), sig2, _sig_prompt("人口數", sig2))]}


v12377 = {"stem": "已知 $2018$ 年美國的人口數為 $329976959$ 人。",
          "items": [_sci_item("329976959", 2, _sig_prompt("人口數", 2)), _sci_item("329976959", 3, _sig_prompt("人口數", 3))]}

_SCI_STEM = "計算下列各式的值，將答案取 $2$ 位有效數字並以科學記號表示："


def _m(rng, lo=1.0, hi=9.9) -> str:
    return f"{rng.uniform(lo, hi):.1f}"


def s12378(rng):
    a, b, c, d = _m(rng), _m(rng), _m(rng), _m(rng)
    m1, n1 = rng.randint(2, 9), -rng.randint(3, 9)
    p, q = rng.randint(10, 18), 0
    q = p - 2
    return {"stem": _SCI_STEM, "items": [
        {"kind": "expr", "tree": M(sci(a, m1), sci(b, n1)), "sig": 2},
        {"kind": "expr", "tree": Sb(sci(c, p), sci(d, q)), "sig": 2}]}


v12378 = {"stem": _SCI_STEM, "items": [
    {"kind": "expr", "tree": M(sci("3.0", 3), sci("4.5", -7)), "sig": 2},
    {"kind": "expr", "tree": Sb(sci("3.2", 15), sci("7.1", 13)), "sig": 2}]}


def s12379(rng):
    a, b = _m(rng, 1.0, 9.9), _m(rng, 1.0, 9.9)
    e1, e2 = rng.randint(14, 20), rng.randint(8, 13)
    return {"stem": f"已知太陽的體積約為 ${a}\\times 10^{{{e1}}}$ 立方公里，且地球的體積約為 ${b}\\times 10^{{{e2}}}$ 立方公里，"
                    "試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）",
            "items": [{"kind": "expr", "tree": D(M(a, P(10, e1)), M(b, P(10, e2))), "sig": 2, "show_expr": False}]}


v12379 = {"stem": "已知太陽的體積約為 $1.41\\times 10^{18}$ 立方公里，且地球的體積約為 $1.08\\times 10^{12}$ 立方公里，"
                  "試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）",
          "items": [{"kind": "expr", "tree": D(M("1.41", P(10, 18)), M("1.08", P(10, 12))), "sig": 2, "show_expr": False}]}


def s12380(rng):
    d = rng.randint(50, 990)
    k = pick(rng, [-7, -6, -9, -8])
    return {"stem": f"流感病毒的直徑約為 ${d}$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{{{k}}}$ 公分，問：將其以科學記號表示時為多少公分？",
            "items": [{"kind": "expr", "tree": M(d, P(10, k)), "sig": 3, "show_expr": False}]}


v12380 = {"stem": "流感病毒的直徑約為 $100$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-7}$ 公分，問：將其以科學記號表示時為多少公分？",
          "items": [{"kind": "expr", "tree": M(100, P(10, -7)), "sig": 3, "show_expr": False}]}


def s12381(rng):
    a, b, c, d = _m(rng), _m(rng, 2.0, 9.9), _m(rng), _m(rng)
    n1, n2 = -rng.randint(3, 9), rng.randint(2, 6)
    p = rng.randint(10, 14)
    return {"stem": _SCI_STEM, "items": [
        {"kind": "expr", "tree": D(sci(a, n1), sci(b, n2)), "sig": 2},
        {"kind": "expr", "tree": A(sci(c, p), sci(d, p - 1)), "sig": 2}]}


v12381 = {"stem": _SCI_STEM, "items": [
    {"kind": "expr", "tree": D(sci("3.4", -6), sci("8.0", 4)), "sig": 2},
    {"kind": "expr", "tree": A(sci("6.4", 12), sci("2.8", 11)), "sig": 2}]}


def s12382(rng):
    a, b = f"{rng.uniform(3.0, 9.9):.2f}", f"{rng.uniform(1.0, 9.9):.2f}"
    e = rng.randint(6, 9)
    return {"stem": f"亞洲是世界上最大的洲，其面積約為 ${a}\\times 10^{{{e}}}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 "
                    f"${b}\\times 10^{{{e - 1}}}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）",
            "items": [{"kind": "expr", "tree": Sb(M(a, P(10, e)), M(b, P(10, e - 1))), "sig": 2, "show_expr": False}]}


v12382 = {"stem": "亞洲是世界上最大的洲，其面積約為 $4.46\\times 10^{7}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 "
                  "$8.54\\times 10^{6}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）",
          "items": [{"kind": "expr", "tree": Sb(M("4.46", P(10, 7)), M("8.54", P(10, 6))), "sig": 2, "show_expr": False}]}


def s12383(rng):
    v = f"{rng.randint(10 ** 7, 10 ** 9)}.{rng.randint(0, 9)}"
    sig1, sig2 = pick(rng, [(2, 3), (3, 4), (2, 4)])
    return {"stem": f"已知太陽到地球的平均距離為{v}公里。",
            "items": [_sci_item(v, sig1, _sig_prompt("此平均距離", sig1)), _sci_item(v, sig2, _sig_prompt("此平均距離", sig2))]}


v12383 = {"stem": "已知太陽到地球的平均距離為149597870.7公里。",
          "items": [_sci_item("149597870.7", 2, _sig_prompt("此平均距離", 2)), _sci_item("149597870.7", 3, _sig_prompt("此平均距離", 3))]}


def _digits_of(m: str, e: int) -> str:
    return str(int(Fraction(m) * Fraction(10) ** e))


def s12384(rng):
    e = rng.randint(6, 10)
    digits = rng.randint(2, 4)
    m = "0." + "".join(str(rng.randint(1, 9)) for _ in range(digits - 1)) + str(rng.randint(1, 9)) + "0"
    if len(m) - 2 > e:
        m = "0." + "".join(str(rng.randint(1, 9)) for _ in range(e - 1)) + "0"
    actual = _digits_of(m, e)
    pick_claim = lambda true, delta: true if rng.random() < 0.6 else true + delta
    return {"number": {"mantissa": m, "exponent": e}, "statements": [
        {"kind": "is_scientific_notation", "claim": True},
        {"kind": "digit_count", "claim": pick_claim(len(actual), pick(rng, [-1, 1]))},
        {"kind": "zero_count", "claim": pick_claim(actual.count("0"), pick(rng, [-1, 1, 2]))},
        {"kind": "greater_than_power", "claim": pick(rng, [e - 1, e, e - 2])}]}


v12384 = {"number": {"mantissa": "0.3210", "exponent": 9}, "statements": [
    {"kind": "is_scientific_notation", "claim": True}, {"kind": "digit_count", "claim": 9},
    {"kind": "zero_count", "claim": 6}, {"kind": "greater_than_power", "claim": 8}]}


def _decimal_str(rng) -> str:
    return f"{rng.randint(1, 9)}.{rng.randint(1, 9)}{rng.randint(0, 9)}{rng.choice(['0', '0', '5'])}"


def s12385(rng):
    return {"stem": "", "items": [{"kind": "as_power_of_ten", "value": f"{rng.randint(11, 99) / 10:g}"},
                                  {"kind": "expr", "tree": P(10, L(f"{rng.randint(101, 999) / 100:g}"))}]}


v12385 = {"stem": "", "items": [{"kind": "as_power_of_ten", "value": "2.7"}, {"kind": "expr", "tree": P(10, L("3.14"))}]}


def _pow10_num(k: int) -> Any:
    return str(10 ** k) if k >= 0 else f"0.{'0' * (-k - 1)}1"


def s12386(rng):
    ks = rng.sample([-4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6], 3)
    return {"stem": "求下列各數的值：", "items": [{"kind": "expr", "tree": L(_pow10_num(k))} for k in ks]}


v12386 = {"stem": "求下列各數的值：", "items": [{"kind": "expr", "tree": L(1)}, {"kind": "expr", "tree": L(100)}, {"kind": "expr", "tree": L("0.001")}]}


def _cond_log(x: int, targets: list) -> dict:
    return _cond("已知 ", V("t"), L(x), [f"log({x})/log(10)"], targets, var="t")


def s12387(rng):
    x = pick(rng, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47])
    return _cond_log(x, [P(100, V("t")), A(P(10, V("t")), P(10, Ng(V("t"))))])


v12387 = _cond_log(13, [P(100, V("t")), A(P(10, V("t")), P(10, Ng(V("t"))))])


def s12392(rng):
    return s12387(rng)


v12392 = _cond_log(5, [P(100, V("t")), A(P(10, V("t")), P(10, Ng(V("t"))))])


def s12399(rng):
    x = pick(rng, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61])
    return _cond_log(x, [P(10, V("t")), A(P(100, V("t")), P(10, Ng(V("t"))))])


v12399 = _cond_log(7, [P(10, V("t")), A(P(100, V("t")), P(10, Ng(V("t"))))])


def s12388(rng):
    return {"value": f"{rng.randint(101, 999) / 100:g}", "decimals": 4}


v12388 = {"value": "1.34", "decimals": 4}


def s12389(rng):
    return {"base": 2, "exponent": pick(rng, [13, 17, 19, 31, 61, 89, 107, 127, 521]), "offset": -1, "style": pick(rng, ["lucas", "known"])}


v12389 = {"base": 2, "exponent": 127, "offset": -1, "style": "lucas"}


def s12393(rng):
    return s12389(rng)


v12393 = {"base": 2, "exponent": 31, "offset": -1, "style": "known"}


def s12390(rng):
    return {"stem": "", "items": [{"kind": "as_power_of_ten", "value": f"{rng.randint(1, 99) / 100:g}"},
                                  {"kind": "expr", "tree": P(10, L(rng.randint(101, 999)))}]}


v12390 = {"stem": "", "items": [{"kind": "as_power_of_ten", "value": "0.02"}, {"kind": "expr", "tree": P(10, L(120))}]}


def s12391(rng):
    k1, k2 = rng.randint(2, 8), rng.randint(1, 6)
    return {"stem": "", "items": [{"kind": "expr", "tree": L(10 ** k1)}, {"kind": "expr", "tree": L(D(1, 10 ** k2))}]}


v12391 = {"stem": "", "items": [{"kind": "expr", "tree": L(10000)}, {"kind": "expr", "tree": L(D(1, 10))}]}


def s12398(rng):
    k1, k2 = rng.randint(2, 8), rng.randint(2, 8)
    return {"stem": "求下列各數的值：", "items": [{"kind": "expr", "tree": L(10 ** k1)}, {"kind": "expr", "tree": L(D(1, 10 ** k2))}]}


v12398 = {"stem": "求下列各數的值：", "items": [{"kind": "expr", "tree": L(100000)}, {"kind": "expr", "tree": L(D(1, 10000))}]}


def s12394(rng):
    lit = pick(rng, ["3.2100", "0.0450", "12.30", "4.0100", "0.00720", "8.500", "2.0030"])
    digits = len(lit.replace(".", "").lstrip("0"))
    claim = digits if rng.random() < 0.5 else digits + pick(rng, [-1, 1])
    return {"number": {"decimal": lit}, "statements": [{"kind": "significant_digits", "claim": claim}]}


v12394 = {"number": {"decimal": "3.2100"}, "statements": [{"kind": "significant_digits", "claim": 5}]}


def s12395(rng):
    a = rng.randint(2, 99)
    form = rng.randrange(3)
    if form == 0:
        return _truth([{"lhs": _t(a), "rhs": P(10, L(a))}])
    if form == 1:
        return _truth([{"lhs": _t(a), "rhs": P(10, L(a + rng.randint(1, 5)))}])
    return _truth([{"lhs": L(P(10, a)), "rhs": _t(a + pick(rng, [0, 0, 1]))}])


v12395 = _truth([{"lhs": _t(7), "rhs": P(10, L(7))}])


def s12396(rng):
    k = rng.randint(1, 6)
    claim = k if rng.random() < 0.4 else k + pick(rng, [-1, 1, 2])
    return _truth([{"lhs": L(10 ** k), "rhs": _t(claim)}])


v12396 = _truth([{"lhs": L(10), "rhs": _t(2)}])


def s12397(rng):
    x = f"{rng.randint(5, 40)}.{rng.randint(1, 9)}"
    actual = int(float(x)) + 1
    claim = actual if rng.random() < 0.4 else actual - 1
    return {"number": {"ten_power": x}, "statements": [{"kind": "integer_part_digits", "claim": claim}]}


v12397 = {"number": {"ten_power": "19.1"}, "statements": [{"kind": "integer_part_digits", "claim": 19}]}


def s12400(rng):
    return {"base": pick(rng, [2, 3, 5, 6, 7, 11]), "exponent": rng.randint(50, 300), "decimals": 1}


v12400 = {"base": 6, "exponent": 100, "decimals": 1}


def s12401(rng):
    return {"base": 2, "tower_n": rng.randint(4, 20), "decimals": 0}


v12401 = {"base": 2, "tower_n": 10, "decimals": 0}

BENFORD = [{"name": f"{p}%", "value": p, "text": f"{p}%"} for p in (10, 20, 30, 40, 50)]


def s12402(rng):
    return {"model": "benford", "leading_digit": rng.randint(1, 9), "options": BENFORD}


v12402 = {"model": "benford", "leading_digit": 1, "options": BENFORD}


# --- registry of components -------------------------------------------------------

OP = {
    "o1": "simplify_exponent_expressions", "o2": "solve_exponent_blank_equations",
    "o3": "evaluate_conditional_exponent_values", "o4": "evaluate_exponent_statement_truth",
    "o5": "evaluate_repeated_folding", "o6": "select_nearest_model_value", "o7": "evaluate_power_law_model",
    "o8": "solve_metabolic_scaling", "o9": "solve_half_life_model", "o10": "evaluate_scale_energy_ratio",
    "o11": "solve_cooling_coefficient", "o12": "express_rational_powers_as_radicals",
    "o13": "solve_cooling_initial_temperature", "o14": "solve_linear_unknowns_from_exponential_table",
    "o15": "evaluate_scientific_notation_expression", "o16": "evaluate_number_property_statements",
    "o17": "evaluate_common_logarithm_items", "o18": "approximate_common_logarithm",
    "o19": "count_digits_of_integer_power", "o20": "solve_power_of_ten_exponent",
}

# id -> (skill key, op key, source variant, sampler)
COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Callable]] = {
    12339: ("pos", "o1", v12339, s12339), 12340: ("pos", "o5", v12340, s12340),
    12341: ("pos", "o2", v12341, s12341), 12342: ("pos", "o6", v12342, s12342),
    12343: ("int", "o1", v12343, s12343), 12344: ("int", "o1", v12344, s12344),
    12345: ("int", "o3", v12345, s12345), 12346: ("int", "o7", v12346, s12346),
    12347: ("int", "o1", v12347, s12347), 12348: ("int", "o2", v12348, s12348),
    12349: ("int", "o3", v12349, s12349), 12350: ("int", "o7", v12350, s12350),
    12352: ("rat", "o1", v12352, s12352), 12353: ("rat", "o3", v12353, s12353),
    12354: ("rat", "o8", v12354, s12354), 12356: ("rat", "o1", v12356, s12356),
    12357: ("rat", "o3", v12357, s12357), 12358: ("rat", "o9", v12358, s12358),
    12359: ("rat", "o4", v12359, s12359), 12360: ("rat", "o4", v12360, s12360),
    12361: ("rat", "o4", v12361, s12361), 12362: ("rat", "o1", v12362, s12362),
    12363: ("rat", "o1", v12363, s12363), 12364: ("rat", "o4", v12364, s12364),
    12365: ("rat", "o3", v12365, s12365), 12366: ("rat", "o10", v12366, s12366),
    12367: ("real", "o1", v12367, s12367), 12368: ("real", "o3", v12368, s12368),
    12369: ("real", "o11", v12369, s12369), 12370: ("real", "o1", v12370, s12370),
    12371: ("real", "o3", v12371, s12371), 12374: ("real", "o8" if False else "o6", v12374, s12374),
    12375: ("real", "o3", v12375, s12375), 12376: ("real", "o3", v12376, s12376),
    12351: ("rat", "o12", v12351, s12351), 12355: ("rat", "o12", v12355, s12355),
    12372: ("real", "o13", v12372, s12372), 12373: ("real", "o14", v12373, s12373),
    12377: ("sn", "o15", v12377, s12377), 12378: ("sn", "o15", v12378, s12378),
    12379: ("sn", "o15", v12379, s12379), 12380: ("sn", "o15", v12380, s12380),
    12381: ("sn", "o15", v12381, s12381), 12382: ("sn", "o15", v12382, s12382),
    12383: ("sn", "o15", v12383, s12383), 12384: ("sn", "o16", v12384, s12384),
    12385: ("cl", "o17", v12385, s12385), 12386: ("cl", "o17", v12386, s12386),
    12387: ("cl", "o3", v12387, s12387), 12388: ("cl", "o18", v12388, s12388),
    12389: ("cl", "o19", v12389, s12389), 12390: ("cl", "o17", v12390, s12390),
    12391: ("cl", "o17", v12391, s12391), 12392: ("cl", "o3", v12392, s12392),
    12393: ("cl", "o19", v12393, s12393), 12394: ("cl", "o16", v12394, s12394),
    12395: ("cl", "o4", v12395, s12395), 12396: ("cl", "o4", v12396, s12396),
    12397: ("cl", "o16", v12397, s12397), 12398: ("cl", "o17", v12398, s12398),
    12399: ("cl", "o3", v12399, s12399), 12400: ("cl", "o20", v12400, s12400),
    12401: ("cl", "o20", v12401, s12401), 12402: ("cl", "o6", v12402, s12402),
}
UNIT4_IDS = tuple(range(12377, 12403))

DEFERRED: dict[int, str] = {}
FINAL_FOUR = (12351, 12355, 12372, 12373)
