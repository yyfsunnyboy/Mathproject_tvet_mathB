"""Per-component *inputs* for 普高數學1 Unit 11 (多項式不等式).

Each entry gives the source-faithful givens (variant 0) and a sampler for further variants of the same shape.
Samplers only choose inputs (plain JSON); the domain computes every answer and refuses degenerate inputs, which the
sandbox then skips.  Figures are never stored: they are rebuilt from the givens of each variant.
"""

from __future__ import annotations

import random
from typing import Any

import sympy as sp

from .polynomial_inequality_domain import K, solve_sign_chart

SKILLS = {"ineq": "gh_PolynomialInequalities", "graph": "gh_PolynomialFunctionGraphs"}

_TRUNCATED = "Stage 1 題幹被截斷（缺少後續小題與條件），須先重新處理教材來源後才能出題"
DEFERRED: dict[int, str] = {
    12650: _TRUNCATED + "（帳棚三角柱支架：只有開頭一句，缺圖中各段長度與全部小題）",
    12662: _TRUNCATED + "（缺『x 的範圍』以外的後續敘述與所求，無法確認所求為何）",
    12664: _TRUNCATED + "（砲彈高度 y=kt(4-t)：缺條件與所有小題）",
}

OP = {name: name for name in ("solve_polynomial_inequality", "polynomial_inequality_parameters", "polynomial_statements",
                              "polynomial_applications", "polynomial_graph_solutions")}
SKILL_OPERATIONS = {
    "ineq": ["solve_polynomial_inequality", "polynomial_inequality_parameters", "polynomial_statements", "polynomial_applications"],
    "graph": ["polynomial_graph_solutions"],
}
RELS = [">", "<", ">=", "<="]
FLIP = {">": "<", "<": ">", ">=": "<=", "<=": ">="}


def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def nz(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v:
            return v


def distinct(rng: random.Random, n: int, lo: int, hi: int, gap: int = 1) -> list[int]:
    for _ in range(200):
        vals = sorted(rng.sample(range(lo, hi + 1), n))
        if all(b - a >= gap for a, b in zip(vals, vals[1:])):
            return vals
    raise RuntimeError("no_distinct_values")


# --- building blocks -------------------------------------------------------------------------------

def L(*coeffs: Any) -> dict[str, Any]:
    return {"poly": list(coeffs)}


def lin(a: Any, b: Any, mult: int = 1) -> dict[str, Any]:
    return {"lin": [a, b], **({"mult": mult} if mult > 1 else {})}


def quad(a: Any, b: Any, c: Any, mult: int = 1) -> dict[str, Any]:
    return {"quad": [a, b, c], **({"mult": mult} if mult > 1 else {})}


def F(*factors: dict[str, Any], coef: Any = 1) -> dict[str, Any]:
    return {"coef": coef, "factors": list(factors)}


def item(left: dict[str, Any], rel: str, right: dict[str, Any] | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {"left": left, "rel": rel}
    if right is not None:
        out["right"] = right
    return out


def items(*its: dict[str, Any]) -> dict[str, Any]:
    return {"items": list(its)}


_POS_QUADS = [(1, 1, 1), (1, 0, 1), (1, 1, 3), (2, 3, 4), (1, -2, 5), (3, -1, 1), (1, -4, 7), (2, 0, 3)]


def _pos_quad(rng: random.Random, mult: int = 1) -> dict[str, Any]:
    return quad(*pick(rng, _POS_QUADS), mult=mult)


def _lin_factor(rng: random.Random, root: int, mult: int = 1, flip_ok: bool = True) -> dict[str, Any]:
    if flip_ok and rng.random() < 0.25:
        return lin(-1, root, mult)
    return lin(1, -root, mult)


def _product(rng: random.Random, mults: list[int], extra_quad: bool = False, lo: int = -5, hi: int = 6) -> dict[str, Any]:
    roots = distinct(rng, len(mults), lo, hi)
    factors = [_lin_factor(rng, r, m) for r, m in zip(roots, mults)]
    if extra_quad:
        factors.append(_pos_quad(rng))
    rng.shuffle(factors)
    return F(*factors)


def _quad_poly(rng: random.Random, kind: str) -> list[int]:
    a = pick(rng, [1, 1, 2, -1, -2, 3])
    if kind == "split":
        r1, r2 = distinct(rng, 2, -6, 6)
        return [a, -a * (r1 + r2), a * r1 * r2]
    if kind == "double":
        r = rng.randint(-5, 5)
        return [a, -2 * a * r, a * r * r]
    b = rng.randint(-6, 6)
    a = abs(a) if rng.random() < 0.7 else -abs(a)
    if a > 0:
        c = -(-b * b // (4 * a)) + rng.randint(1, 4)
    else:
        c = (b * b) // (4 * a) - rng.randint(1, 4)
    return [a, b, c]


def _quad_item(rng: random.Random, kind: str | None = None, rel: str | None = None, two_sided: bool | None = None) -> dict[str, Any]:
    kind = kind or pick(rng, ["split", "split", "double", "none"])
    rel = rel or pick(rng, RELS)
    a, b, c = _quad_poly(rng, kind)
    if two_sided is None:
        two_sided = rng.random() < 0.3
    if two_sided:
        return item(L(a, 0, 0), rel, L(-b, -c))  # a x^2 rel -b x - c  <=>  a x^2 + b x + c rel 0
    return item(L(a, b, c), rel)


def _linear_item(rng: random.Random) -> dict[str, Any]:
    a = nz(rng, -5, 5)
    c = nz(rng, -5, 5)
    while c == a:
        c = nz(rng, -5, 5)
    return item(L(a, rng.randint(-9, 9)), pick(rng, RELS), L(c, rng.randint(-9, 9)))


# --- A. 解多項式不等式 -----------------------------------------------------------------------------

v12631 = items(item(L(1, -3), ">", L(3, 5)))
v12632 = items(item(L(1, -4, 3), "<="), item(L(-1, 1, 3), "<"))
v12633 = items(item(L(1, -4, 4), ">"))
v12634 = items(item(L(1, 1, 1), ">"), item(L(1, 1, 1), "<="))
v12641 = items(item(L(2, 1), "<", L(5, 10)))
v12642 = items(item(L(-1, -5, 6), "<"), item(L(5, 3), ">=", L(1, 0, 0)))
v12643 = items(item(L(9, -6, 1), "<="))
v12644 = items(item(L(2, -8, 11), ">"), item(L(1, "-2*sqrt(3)", 5), "<"))
v12636 = items(item(F(lin(1, -1), lin(1, -2), lin(1, -3)), ">"), item(F(lin(1, -1, 2), lin(1, -3)), "<"))
v12637 = items(item(F(lin(-1, 2), lin(1, -1), lin(1, 1), lin(1, 2)), ">"), item(F(quad(1, -2, 1), quad(1, -4, 3)), ">="))
v12638 = items(item(F(lin(1, -1), lin(1, -3, 2), quad(2, 3, 4)), "<="))
v12646 = items(item(F(lin(1, 2), lin(1, -1), lin(1, -3)), ">="), item(F(lin(1, 1, 2), lin(1, -2)), ">="))
v12647 = items(item(F(quad(-1, 0, 9), quad(1, -1, -6)), ">="))
v12648 = items(item(F(quad(1, 0, 1), lin(1, -2, 2), lin(1, -5, 3)), "<"))
v12656 = items(item(L(1, 0, 0), ">", L(3, 10)), item(L(1, 0, 0), "<", L(1, 1)), item(L(4, -12, 9), "<="), item(L(2, -4, 7), ">"))
v12657 = items(item(F(lin(1, 1), lin(1, 2), lin(1, 3)), "<"),
               item(F(lin(1, -1), lin(1, 2), lin(1, -2, 2), lin(1, -3, 3)), ">="),
               item(F(quad(1, 1, 1), quad(1, -6, 9)), "<="),
               item(F(lin(1, -2, 2), lin(1, -1), lin(1, 2), quad(1, 1, 3)), "<="))
v12660 = items(item(F(lin(1, 0, 2), lin(1, 2), lin(1, 1), lin(1, -5)), "<=", F(lin(2, 3), lin(1, 2), lin(1, 1), lin(1, -5))))


def s12631(rng): return items(_linear_item(rng))
def s12632(rng): return items(_quad_item(rng, "split", pick(rng, RELS), False), _quad_item(rng, None, pick(rng, RELS), rng.random() < 0.5))
def s12633(rng): return items(_quad_item(rng, "double", pick(rng, RELS), False))


def s12634(rng):
    a = pick(rng, [1, 2, 3])
    b = rng.randint(-4, 4)
    c = -(-b * b // (4 * a)) + rng.randint(1, 3)
    pos = rng.random() < 0.7
    r1, r2 = pick(rng, [(">", "<="), (">=", "<"), (">", "<"), (">=", "<=")])
    if pos:
        return items(item(L(a, b, c), r1), item(L(a, b, c), r2))
    return items(item(L(-a, -b, -c), FLIP[r1]), item(L(-a, -b, -c), FLIP[r2]))


def s12641(rng): return items(_linear_item(rng))
def s12642(rng): return items(_quad_item(rng, "split", pick(rng, RELS), False), _quad_item(rng, None, pick(rng, RELS), True))


def s12643(rng):
    m, n = rng.randint(2, 4), rng.randint(1, 5)
    return items(item(L(m * m, -2 * m * n, n * n), pick(rng, RELS)))


def s12644(rng):
    m = pick(rng, [2, 3, 5, 6, 7])
    n = m + rng.randint(1, 4)
    return items(_quad_item(rng, "none", pick(rng, RELS), False), item(L(1, f"-2*sqrt({m})", n), pick(rng, RELS)))


def s12636(rng): return items(item(_product(rng, [1, 1, 1]), pick(rng, RELS)), item(_product(rng, [2, 1]), pick(rng, RELS)))


def s12637(rng):
    r = rng.randint(-3, 3)
    a, b = distinct(rng, 2, -4, 5)
    return items(item(_product(rng, [1, 1, 1, 1]), pick(rng, RELS)),
                 item(F(quad(1, -2 * r, r * r), quad(1, -(a + b), a * b)), pick(rng, RELS)))


def s12638(rng): return items(item(_product(rng, [1, 2], extra_quad=True), pick(rng, RELS)))
def s12646(rng): return items(item(_product(rng, [1, 1, 1]), pick(rng, RELS)), item(_product(rng, [2, 1]), pick(rng, RELS)))


def s12647(rng):
    c = rng.randint(2, 5)
    a, b = distinct(rng, 2, -5, 6)
    return items(item(F(quad(-1, 0, c * c), quad(1, -(a + b), a * b)), pick(rng, RELS)))


def s12648(rng):
    a, b = distinct(rng, 2, -4, 6)
    return items(item(F(_pos_quad(rng), lin(1, -a, 2), lin(1, -b, 3)), pick(rng, RELS)))


def s12656(rng):
    return items(_quad_item(rng, "split", pick(rng, RELS), True), _quad_item(rng, "split", pick(rng, RELS), True),
                 _quad_item(rng, "double", pick(rng, RELS), False), _quad_item(rng, "none", pick(rng, RELS), False))


def s12657(rng):
    rs = distinct(rng, 7, -5, 6)
    f4 = F(lin(1, -rs[0]), lin(1, -rs[1]), lin(1, -rs[2], 2), lin(1, -rs[3], 3))
    r = rng.randint(-3, 4)
    return items(item(_product(rng, [1, 1, 1]), pick(rng, RELS)), item(f4, pick(rng, RELS)),
                 item(F(_pos_quad(rng), quad(1, -2 * r, r * r)), pick(rng, RELS)),
                 item(F(lin(1, -rs[4], 2), lin(1, -rs[5]), lin(1, -rs[6]), _pos_quad(rng)), pick(rng, RELS)))


def s12660(rng):
    g = distinct(rng, 3, -5, 6)
    p, q = rng.randint(-3, 4), rng.randint(-3, 4)
    m, n = p + q, -p * q
    if m == 0 and n == 0:
        raise ValueError("degenerate")
    gfs = [lin(1, -r) for r in g]
    right_first = lin(m, n) if m != 0 else None
    if right_first is None:
        raise ValueError("degenerate")
    return items(item(F(lin(1, 0, 2), *gfs), pick(rng, RELS), F(right_first, *gfs)))


# --- B. 求係數 / 參數 -------------------------------------------------------------------------------

v12639 = items({"kind": "cubic_from_solution", "d": -8, "roots": [-2, 1, 4], "rel": "<=", "form": "high"})
v12658 = items({"kind": "quad_from_solution", "p": -3, "roots": ["-3", "1/2"], "rel": ">", "shape": "between"})
v12659 = items({"kind": "always_true", "a": 1, "b1": 1, "b0": 0, "c1": 1, "c0": 0})
v12649 = items({"kind": "monic_compare", "roots": [[0, 1], [1, 2]], "g": [1, 0], "rel": ">"})


def s12639(rng):
    r = distinct(rng, 3, -5, 6)
    if 0 in r:
        raise ValueError("zero_root")
    a = pick(rng, [1, -1, 2, -2, 3, -3])
    d = -a * r[0] * r[1] * r[2]
    rel = pick(rng, RELS)
    low = (a > 0) == (rel in ("<", "<="))
    return items({"kind": "cubic_from_solution", "d": d, "roots": r, "rel": rel, "form": "low" if low else "high"})


def s12658(rng):
    pool = [-4, -3, -2, -1, 1, 2, 3, 4, "-1/2", "1/2", "3/2", "-3/2"]
    r1, r2 = rng.sample(pool, 2)
    from fractions import Fraction

    f1, f2 = Fraction(str(r1)), Fraction(str(r2))
    if f1 > f2:
        r1, r2, f1, f2 = r2, r1, f2, f1
    a = pick(rng, [1, 2, -1, -2, 3, -3, 4, -4, 6, -6])
    p = -a * (f1 + f2)
    if p == 0 or p.denominator != 1:
        raise ValueError("p_not_integer")
    shape = pick(rng, ["between", "outside"])
    strict = rng.random() < 0.7
    positive = (a < 0) if shape == "between" else (a > 0)
    rel = (">" if positive else "<") if strict else (">=" if positive else "<=")
    return items({"kind": "quad_from_solution", "p": int(p), "roots": [r1, r2], "rel": rel, "shape": shape})


def s12659(rng):
    a = pick(rng, [1, 1, 2])
    b1 = pick(rng, [1, -1, 2, -2, 0])
    c1 = pick(rng, [1, -1, 2, 3, 0]) if b1 else pick(rng, [1, -1, 2, 3])
    b0, c0 = rng.randint(-3, 3), rng.randint(-3, 3)
    disc = sp.expand((b1 * K + b0) ** 2 - 4 * a * (c1 * K + c0))
    if sp.Poly(disc, K).degree() < 1:
        raise ValueError("no_k")
    s = solve_sign_chart(disc, "<=", K)
    if s in (sp.S.Reals, sp.S.EmptySet):
        raise ValueError("degenerate_k_range")
    return items({"kind": "always_true", "a": a, "b1": b1, "b0": b0, "c1": c1, "c0": c0})


def s12649(rng):
    r, s = distinct(rng, 2, -3, 4)
    c = pick(rng, [1, 4, 9])
    return items({"kind": "monic_compare", "roots": [[r, 1], [s, 2]], "g": [c, -c * r], "rel": pick(rng, RELS)})


# --- C. 敘述判斷 ------------------------------------------------------------------------------------

def _truth(statement: dict[str, Any]) -> dict[str, Any]:
    return {"subject": {}, "statements": [statement], "mode": "truth"}


def _claim(item_: dict[str, Any], truth: bool, rng: random.Random | None = None) -> str:
    from .polynomial_inequality_domain import _side_expr, set_text

    diff = sp.expand(_side_expr(item_["left"]) - _side_expr(item_.get("right", {"poly": [0]})))
    rel = item_["rel"] if truth else FLIP[item_["rel"]]
    return set_text(solve_sign_chart(diff, rel))


v12651 = _truth({"kind": "solution_claim", "ineq": item(L(-2, 0), ">", L(3)), "claim": "x>-3/2"})
v12652 = _truth({"kind": "solution_claim", "ineq": item(F(lin(1, -3), lin(1, -5)), ">"), "claim": "3<x<5"})
v12653 = _truth({"kind": "solution_claim", "ineq": item(F(lin(1, 4, 2), coef=5), ">"), "claim": "全體實數"})
v12654 = _truth({"kind": "same_solution", "a": item(F(lin(1, -1), lin(1, -2)), "<="), "b": item(F(lin(-1, 1), lin(1, -2)), ">=")})
v12655 = _truth({"kind": "same_solution", "a": item(F(lin(1, -1), lin(1, -2)), "<="), "b": item(F(quad(1, 1, 1), lin(1, -1), lin(1, -2)), "<=")})


def s12651(rng):
    a = nz(rng, -5, 5)
    ineq = item(L(a, 0), pick(rng, RELS), L(nz(rng, -9, 9)))
    return _truth({"kind": "solution_claim", "ineq": ineq, "claim": _claim(ineq, rng.random() < 0.5)})


def s12652(rng):
    r1, r2 = distinct(rng, 2, -6, 7)
    ineq = item(F(lin(1, -r1), lin(1, -r2)), pick(rng, RELS))
    return _truth({"kind": "solution_claim", "ineq": ineq, "claim": _claim(ineq, rng.random() < 0.5)})


def s12653(rng):
    k = pick(rng, [5, 3, 2, -2, -3, -5])
    r = rng.randint(-6, 6)
    ineq = item(F(lin(1, -r, 2), coef=k), pick(rng, RELS))
    return _truth({"kind": "solution_claim", "ineq": ineq, "claim": pick(rng, ["全體實數", "無解", _claim(ineq, True), _claim(ineq, False)])})


def s12654(rng):
    r1, r2 = distinct(rng, 2, -5, 6)
    rel = pick(rng, RELS)
    rel_b = FLIP[rel] if rng.random() < 0.55 else rel
    return _truth({"kind": "same_solution", "a": item(F(lin(1, -r1), lin(1, -r2)), rel), "b": item(F(lin(-1, r1), lin(1, -r2)), rel_b)})


def s12655(rng):
    r1, r2 = distinct(rng, 2, -5, 6)
    rel = pick(rng, RELS)
    roll = rng.random()
    if roll < 0.55:
        extra, rel_b = _pos_quad(rng), rel
    elif roll < 0.8:
        a, b, c = pick(rng, _POS_QUADS)
        extra, rel_b = quad(-a, -b, -c), rel
    else:
        extra, rel_b = _pos_quad(rng), FLIP[rel]
    return _truth({"kind": "same_solution", "a": item(F(lin(1, -r1), lin(1, -r2)), rel),
                   "b": item(F(extra, lin(1, -r1), lin(1, -r2)), rel_b)})


def _select(roots: list, lead: Any, names: list[tuple[str, str]]) -> dict[str, Any]:
    sts: list[dict[str, Any]] = [{"kind": "coefficient_sign", "name": n, "sign": s} for n, s in names]
    sts.append({"kind": "sum_positive"})
    return {"subject": {"roots": roots, "lead": lead}, "statements": sts, "mode": "select"}


v12661 = _select([0, 1, 2], 1, [("a", "+"), ("b", "+"), ("c", "+"), ("d", "+")])


def s12661(rng):
    roots = distinct(rng, 3, -3, 5)
    lead = pick(rng, [1, 1, -1, 2, -2])
    return _select(roots, lead, [(n, pick(rng, ["+", "+", "-"])) for n in "abcd"])


# --- D. 應用題 --------------------------------------------------------------------------------------

def _app(**kw: Any) -> dict[str, Any]:
    return items(kw)


v12635 = _app(kind="triangle_rectangle", B=40, H=40, A=300)
v12645 = _app(kind="square_corner", s=4, A=10)
v12663 = _app(kind="path_around_plot", W=10, L=12, P0=20, A0=48)
v12665 = _app(kind="cube_paint", plastic=20, paint=10, share="1/2", xmax=8)
v12640 = _app(kind="frame_box", L=40, V=36)
v12666 = _app(kind="open_box", S=32, V=14)


def s12635(rng):
    B = pick(rng, [20, 30, 40, 50, 60])
    H = pick(rng, [B, B, B, B - 10, B + 10, 30, 40, 50])
    x1 = rng.randint(3, B // 2 - 1)
    A = sp.Rational(H * x1 * (B - x1), B)
    if A.q != 1:
        raise ValueError("A_not_integer")
    return _app(kind="triangle_rectangle", B=B, H=H, A=int(A))


def s12645(rng):
    s = pick(rng, [4, 5, 6, 7, 8, 9, 10, 12, 14, 16])
    x1 = pick(rng, [2, 4, 6, 8])
    if x1 >= s:
        raise ValueError("x1_too_large")
    return _app(kind="square_corner", s=s, A=s * s - s * x1 + x1 * x1 // 2)


def s12663(rng):
    W = rng.randint(8, 16)
    L_ = rng.randint(W, 20)
    top = (min(W, L_) - 1) // 2
    xb = rng.randint(1, top - 1)
    xa = rng.randint(xb + 1, top)
    return _app(kind="path_around_plot", W=W, L=L_, P0=2 * (W + L_) - 8 * xa, A0=(W - 2 * xb) * (L_ - 2 * xb))


def s12665(rng):
    c1 = pick(rng, [10, 20, 30, 40])
    c2 = pick(rng, [5, 10, 15, 20])
    share = pick(rng, ["1/2", "1/3", "1/4", "2/3"])
    x0 = sp.Rational(6 * c2) / (sp.Rational(share) * c1)
    if x0.q != 1 or not 2 <= x0 <= 9:
        raise ValueError("x0_not_nice")
    return _app(kind="cube_paint", plastic=c1, paint=c2, share=share, xmax=int(x0) + rng.randint(1, 4))


def s12640(rng):
    m = rng.randint(8, 13)
    r = rng.randint(1, 4)
    if 2 * r >= m:
        raise ValueError("r_too_large")
    return _app(kind="frame_box", L=4 * m, V=r * r * (m - 2 * r))


def s12666(rng):
    S = pick(rng, [12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 72, 80])
    r = rng.randint(1, 4)
    V = sp.Rational(r * (S - r * r), 4)
    if V.q != 1 or V <= 0:
        raise ValueError("V_not_integer")
    return _app(kind="open_box", S=S, V=int(V))


# --- E. 由圖形解多項式不等式 ------------------------------------------------------------------------

v12629 = items({"roots": [[1, 1], [3, 1], [5, 1]], "lead": 1})
v12630 = items({"roots": [[1, 1], [3, 2], [5, 1]], "lead": 1})


def s12629(rng):
    lead = pick(rng, [1, 1, -1])
    if rng.random() < 0.8:
        rs = distinct(rng, 3, -3, 8)
        return items({"roots": [[r, 1] for r in rs], "lead": lead})
    rs = distinct(rng, 2, -3, 8)
    k = rng.randrange(2)
    return items({"roots": [[rs[0], 2 if k == 0 else 1], [rs[1], 1 if k == 0 else 2]], "lead": lead})


def s12630(rng):
    lead = pick(rng, [1, 1, -1])
    shape = pick(rng, ["121", "121", "1111", "22", "112"])
    if shape == "121":
        rs = distinct(rng, 3, -3, 8)
        mults = [1, 2, 1]
    elif shape == "1111":
        rs = distinct(rng, 4, -3, 8)
        mults = [1, 1, 1, 1]
    elif shape == "22":
        rs = distinct(rng, 2, -3, 8, gap=2)
        mults = [2, 2]
    else:
        rs = distinct(rng, 3, -3, 8)
        mults = pick(rng, [[2, 1, 1], [1, 1, 2]])
    return items({"roots": [[r, m] for r, m in zip(rs, mults)], "lead": lead})


def _c(skill: str, op: str, source: dict, sampler) -> tuple:
    return (skill, op, source, sampler)


_S, _P, _T, _A, _G = ("solve_polynomial_inequality", "polynomial_inequality_parameters", "polynomial_statements",
                      "polynomial_applications", "polynomial_graph_solutions")

COMPONENTS: dict[int, tuple] = {
    12629: _c("graph", _G, v12629, s12629), 12630: _c("graph", _G, v12630, s12630),
    12631: _c("ineq", _S, v12631, s12631), 12632: _c("ineq", _S, v12632, s12632), 12633: _c("ineq", _S, v12633, s12633),
    12634: _c("ineq", _S, v12634, s12634), 12635: _c("ineq", _A, v12635, s12635), 12636: _c("ineq", _S, v12636, s12636),
    12637: _c("ineq", _S, v12637, s12637), 12638: _c("ineq", _S, v12638, s12638), 12639: _c("ineq", _P, v12639, s12639),
    12640: _c("ineq", _A, v12640, s12640), 12641: _c("ineq", _S, v12641, s12641), 12642: _c("ineq", _S, v12642, s12642),
    12643: _c("ineq", _S, v12643, s12643), 12644: _c("ineq", _S, v12644, s12644), 12645: _c("ineq", _A, v12645, s12645),
    12646: _c("ineq", _S, v12646, s12646), 12647: _c("ineq", _S, v12647, s12647), 12648: _c("ineq", _S, v12648, s12648),
    12649: _c("ineq", _P, v12649, s12649), 12651: _c("ineq", _T, v12651, s12651), 12652: _c("ineq", _T, v12652, s12652),
    12653: _c("ineq", _T, v12653, s12653), 12654: _c("ineq", _T, v12654, s12654), 12655: _c("ineq", _T, v12655, s12655),
    12656: _c("ineq", _S, v12656, s12656), 12657: _c("ineq", _S, v12657, s12657), 12658: _c("ineq", _P, v12658, s12658),
    12659: _c("ineq", _P, v12659, s12659), 12660: _c("ineq", _S, v12660, s12660), 12661: _c("ineq", _T, v12661, s12661),
    12663: _c("ineq", _A, v12663, s12663), 12665: _c("ineq", _A, v12665, s12665), 12666: _c("ineq", _A, v12666, s12666),
}


# --- revision 2: the three items whose Stage 1 stems were repaired (12650, 12662, 12664) -------------------------

v12650 = _app(kind="tent_prism", triple=[3, 4, 5], L=168, V=1728)
v12662 = items({"kind": "quad_factor_param", "pos": [3, -1, 1], "roots": [-1, 3], "rel": "<=", "shape": "between"})
v12664 = _app(kind="projectile_ceiling", T=4, H=16)


def s12650(rng):
    from .polynomial_inequality_domain import polynomial_applications

    p, q, r = pick(rng, [(3, 4, 5), (3, 4, 5), (6, 8, 10), (5, 12, 13)])
    c = rng.randint(1, 4)
    L_ = rng.randrange(30, 400, 3)
    P = p + q + r
    V = sp.Rational(p * q, 6) * c * c * (L_ + 2 * P * c)
    if V.q != 1:
        raise ValueError("V_not_integer")
    givens = {"kind": "tent_prism", "triple": [p, q, r], "L": L_, "V": int(V)}
    rec = polynomial_applications([givens])["items"][0]
    if rec["solution"]["canonical"] == "無解" or len(rec["factor_roots"]) != 1:
        raise ValueError("no_clean_solution")
    return _app(**givens)


def s12662(rng):
    pos = pick(rng, _POS_QUADS)
    r1, r2 = distinct(rng, 2, -5, 6)
    shape = pick(rng, ["between", "outside"])
    strict = rng.random() < 0.4
    rel = ("<" if strict else "<=") if shape == "between" else (">" if strict else ">=")
    return items({"kind": "quad_factor_param", "pos": list(pos), "roots": [r1, r2], "rel": rel, "shape": shape})


def s12664(rng):
    T = pick(rng, [2, 4, 6, 8, 10, 12])
    k0 = rng.randint(1, 9)
    return _app(kind="projectile_ceiling", T=T, H=k0 * T * T // 4)


REV2_COMPONENTS: dict[int, tuple] = {
    12650: _c("ineq", _A, v12650, s12650), 12662: _c("ineq", _P, v12662, s12662), 12664: _c("ineq", _A, v12664, s12664),
}
