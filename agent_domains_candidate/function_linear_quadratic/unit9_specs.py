"""Per-component *inputs* for 普高數學1 Unit 9 (一次與二次函數).

Each entry gives the source-faithful givens (variant 0) and a sampler for further variants of the same
shape.  Samplers only choose inputs; the domain computes every answer and rejects degenerate inputs
(the sandbox skips a candidate the domain refuses).
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Callable

SKILLS = {
    "lin": "gh_LinearFunctions",
    "quad": "gh_QuadraticFunctions",
}

# 正式作答契約下無法發布的教材題：拋物線描繪沒有正式 grader（drawing_answer_analysis_service 只支援
# line_graph／linear_inequality_region／長條圖等；function_graph 型別不被分析服務支援），不進 wrapper。
_NO_PARABOLA_GRADER = "拋物線作圖題：既有 drawing 契約沒有可用的拋物線 grader（function_graph 不受 drawing_answer_analysis_service 支援）"
DEFERRED: dict[int, str] = {
    12567: _NO_PARABOLA_GRADER,
    12568: _NO_PARABOLA_GRADER,
    12570: _NO_PARABOLA_GRADER + "（描繪 + 頂點／對稱軸）",
    12576: _NO_PARABOLA_GRADER,
    12587: _NO_PARABOLA_GRADER + "（描繪 + 頂點／對稱軸）",
}

OP = {name: name for name in (
    "solve_linear_functions", "evaluate_function_statements", "complete_square_items", "quadratic_vertex_axis", "quadratic_extrema",
    "quadratic_graph_transformations", "quadratic_always_sign", "solve_quadratic_applications", "graph_quadratic_functions",
)}

SKILL_OPERATIONS = {
    "lin": ["solve_linear_functions", "evaluate_function_statements"],
    "quad": ["evaluate_function_statements", "complete_square_items", "quadratic_vertex_axis", "quadratic_extrema",
             "quadratic_graph_transformations", "quadratic_always_sign", "solve_quadratic_applications", "graph_quadratic_functions"],
}

# 觀念題只有兩種真假（概念題，無數值可變）：單一題面
STATIC_COMPONENTS: dict[int, str] = {12602: "concept statement; only the true / swapped (false) wording exists"}


# --- helpers -----------------------------------------------------------------------------------------

def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def nz(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v:
            return v


def j(value: Any) -> Any:
    q = Fraction(value)
    return int(q) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def dec(q: Fraction) -> Any:
    """Decimal string when the fraction terminates (e.g. 3.35), else ``p/q``."""
    d = q.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    if d != 1:
        return j(q)
    text = f"{float(q):.6f}".rstrip("0").rstrip(".")
    return int(text) if "." not in text else text


def quad_from_vertex(a: Any, h: Any, k: Any) -> list:
    a, h, k = Fraction(a), Fraction(h), Fraction(k)
    return [j(a), j(-2 * a * h), j(a * h * h + k)]


# --- 一次函數 ---------------------------------------------------------------------------------------

def _two_points(p1: list, p2: list, dx: Any) -> dict[str, Any]:
    return {"items": [{"kind": "two_points", "p1": p1, "p2": p2, "dx": dx}]}


v12560 = _two_points([2, 1], [4, 5], 3)


def s12560(rng):
    m, b = nz(rng, -4, 4), rng.randint(-5, 5)
    x1 = rng.randint(-3, 3)
    x2 = x1 + nz(rng, -3, 3)
    return _two_points([x1, m * x1 + b], [x2, m * x2 + b], rng.randint(2, 5))


def _value_at(p1: list, p2: list, x: Any) -> dict[str, Any]:
    return {"items": [{"kind": "value_at", "p1": p1, "p2": p2, "x": x}]}


v12561 = _value_at(["1.23", 2], ["9.71", 18], "3.35")


def s12561(rng):
    x1 = Fraction(rng.randint(50, 400), 100)
    g = Fraction(rng.randint(100, 400), 100)
    y1 = rng.randint(-5, 5)
    y2 = y1 + 4 * nz(rng, -6, 6)
    return _value_at([dec(x1), y1], [dec(x1 + 4 * g), y2], dec(x1 + g))


v12565 = _value_at([{"pow": [3, 8]}, 2], [{"pow": [3, 10]}, 7], {"pow": [3, 9]})


def s12565(rng):
    base, e = rng.randint(2, 6), rng.randint(2, 8)
    y1 = rng.randint(-4, 6)
    return _value_at([{"pow": [base, e]}, y1], [{"pow": [base, e + 2]}, y1 + nz(rng, -9, 9)], {"pow": [base, e + 1]})


def _solve_x(a: int, b: int, ya: int, yb: int, y0: int) -> dict[str, Any]:
    return {"items": [{"kind": "solve_x", "p1": [{"sqrt": a}, ya], "p2": [{"sqrt": b}, yb], "y": y0}]}


v12563 = _solve_x(2, 5, 2, 5, 3)


def s12563(rng):
    a, b = pick(rng, [(2, 5), (2, 3), (3, 5), (3, 7), (5, 7), (2, 7), (3, 2)])
    ya = rng.randint(-3, 5)
    yb = ya + nz(rng, -6, 6)
    return _solve_x(a, b, ya, yb, rng.randint(-4, 8))


def _rate(f0: int, dx: int, dy: int) -> dict[str, Any]:
    return {"items": [{"kind": "rate", "p": [0, f0], "dx": dx, "dy": dy}]}


v12564 = _rate(-3, 1, -2)


def s12564(rng): return _rate(nz(rng, -8, 8), pick(rng, [1, 1, 2, 3]), nz(rng, -6, 6))


def _lin_stmt(p1: list, p2: list, statements: list) -> dict[str, Any]:
    return {"subject": {"type": "linear_points", "p1": p1, "p2": p2}, "statements": statements, "mode": "select"}


v12562 = _lin_stmt([1, -2], [2, -5], [
    {"kind": "value_is", "x": 3, "value": 8}, {"kind": "slope_positive", "positive": True}, {"kind": "intercept_is", "value": 1},
    {"kind": "slope_is_quotient", "xa": 9, "xb": 7}, {"kind": "rate_is", "dx": 1, "dy": 3}])


def s12562(rng):
    m, b = nz(rng, -4, 4), rng.randint(-4, 4)
    x3 = pick(rng, [3, 4, 5, -1, 0])
    off = lambda v: v if rng.random() < 0.4 else v + nz(rng, -3, 3)  # noqa: E731
    xa, xb = rng.sample([5, 7, 9, 3, 11, 4], 2)
    return _lin_stmt([1, m + b], [2, 2 * m + b], [
        {"kind": "value_is", "x": x3, "value": off(m * x3 + b)}, {"kind": "slope_positive", "positive": rng.random() < 0.5},
        {"kind": "intercept_is", "value": off(b)}, {"kind": "slope_is_quotient", "xa": xa, "xb": xb},
        {"kind": "rate_is", "dx": pick(rng, [1, 2]), "dy": pick(rng, [m, m + 1, -m, m * 2])}])


def _three(lines: list, statements: list) -> dict[str, Any]:
    return {"subject": {"type": "three_lines", "lines": lines}, "statements": statements, "mode": "select"}


v12566 = _three([["4/5", 1], [3, "-1/2"], ["-3/5", "-1/4"]], [
    {"kind": "slope_sign", "i": 1, "sign": "+"}, {"kind": "slope_greater", "i": 1, "j": 2}, {"kind": "slope_sign", "i": 3, "sign": "-"},
    {"kind": "intercept_sign", "i": 1, "sign": "+"}, {"kind": "intercept_greater", "i": 2, "j": 3}])


def s12566(rng):
    slopes = rng.sample(["1/2", "4/5", 1, 2, 3, "-1/2", "-3/5", -1, -2], 3)
    lines = [[s, pick(rng, ["-1", "-1/2", "-1/4", "1/4", "1/2", 1, "3/2"])] for s in slopes]
    i, j_ = rng.sample([1, 2, 3], 2)
    k, l_ = rng.sample([1, 2, 3], 2)
    return _three(lines, [
        {"kind": "slope_sign", "i": 1, "sign": pick(rng, ["+", "-"])}, {"kind": "slope_greater", "i": i, "j": j_},
        {"kind": "slope_sign", "i": 3, "sign": pick(rng, ["+", "-"])}, {"kind": "intercept_sign", "i": 2, "sign": pick(rng, ["+", "-"])},
        {"kind": "intercept_greater", "i": k, "j": l_}])


def _generic_truth(statement: dict[str, Any]) -> dict[str, Any]:
    return {"subject": {"type": "generic"}, "statements": [statement], "mode": "truth"}


v12598 = _generic_truth({"kind": "linear_slope_claim", "a": 2, "b": 3, "claimed": 3})


def s12598(rng):
    a = nz(rng, -4, 4)
    return _generic_truth({"kind": "linear_slope_claim", "a": a, "b": rng.randint(-5, 5), "claimed": a if rng.random() < 0.35 else a + nz(rng, -2, 2)})


# --- 二次函數：配方、頂點、極值 ------------------------------------------------------------------------

def _rand_quad(rng: random.Random) -> list:
    return [pick(rng, [1, 2, 3, -1, -2, -3, "1/2"]), rng.randint(-8, 8), rng.randint(-6, 6)]


v12569 = {"items": [{"coeffs": [1, 2, 4]}, {"coeffs": [3, -12, 8]}, {"coeffs": [-2, -3, 1]}]}
v12579 = {"items": [{"coeffs": [1, 4, 1]}, {"coeffs": [2, 4, 0]}, {"coeffs": [-1, 3, -1]}]}


def s12569(rng): return {"items": [{"coeffs": _rand_quad(rng)} for _ in range(3)]}


s12579 = s12569

v12580 = {"coeffs": [3, 18, 29]}


def s12580(rng):
    return {"coeffs": quad_from_vertex(pick(rng, [1, 2, 3, -1, -2]), rng.randint(-5, 5), rng.randint(-6, 6))}


def _extrema(style: str, items: list, **extra: Any) -> dict[str, Any]:
    return {"style": style, "items": items, **extra}


v12571 = _extrema("single", [{"f": [-1, 3, 1], "asks": ["max_value", "max_x"]}])
v12582 = _extrema("single", [{"f": [1, 1, 1], "asks": ["min_value", "min_x"]}])
v12583 = _extrema("interval_single", [{"f": [-2, 4, 3], "interval": [2, 4], "asks": ["max_value"]}])


def s12571(rng): return _extrema("single", [{"f": [pick(rng, [-1, -2, -3, "-1/2"]), rng.randint(-6, 6), rng.randint(-5, 5)], "asks": ["max_value", "max_x"]}])


def s12582(rng): return _extrema("single", [{"f": [pick(rng, [1, 2, 3, "1/2"]), rng.randint(-6, 6), rng.randint(-5, 5)], "asks": ["min_value", "min_x"]}])


def s12583(rng):
    lo = rng.randint(-3, 3)
    return _extrema("interval_single", [{"f": _rand_quad(rng), "interval": [lo, lo + rng.randint(1, 4)], "asks": ["max_value"]}])


v12572 = _extrema("intervals", [{"f": [2, -4, -1], "interval": iv, "asks": ["max_value", "min_value"]} for iv in ([-2, -1], [2, 3], [-1, 2])],
                  display="vertex", **{"with": "與"})
v12589 = _extrema("intervals", [{"f": [3, -12, 8], "interval": iv, "asks": ["max_value", "min_value"]} for iv in ([0, 3], [3, 5])])


def s12572(rng):
    a, h, k = pick(rng, [1, 2, 3, -1, -2]), rng.randint(-2, 3), rng.randint(-5, 4)
    f = quad_from_vertex(a, h, k)
    ivs = [[h - 3, h - 2], [h + 1, h + 2], [h - 1, h + 1 + rng.randint(0, 1)]]
    return _extrema("intervals", [{"f": f, "interval": iv, "asks": ["max_value", "min_value"]} for iv in ivs], display="vertex", **{"with": "與"})


def s12589(rng):
    f = _rand_quad(rng)
    h = Fraction(-Fraction(str(f[1])) / (2 * Fraction(str(f[0]))))
    lo = int(h) - rng.randint(0, 2)
    return _extrema("intervals", [{"f": f, "interval": [lo, lo + rng.randint(2, 4)], "asks": ["max_value", "min_value"]},
                                   {"f": f, "interval": [lo + 3, lo + 3 + rng.randint(1, 3)], "asks": ["max_value", "min_value"]}])


# --- 恆正／恆負 -------------------------------------------------------------------------------------

def _always(a: Any, b: Any, c: Any, sign: str, style: str = "plain") -> dict[str, Any]:
    return {"a": a, "b": b, "c": c, "sign": sign, "style": style}


v12575 = _always(1, -6, {"k": 1}, "positive")
v12586 = _always(-2, 8, {"k": 1, "c": -3}, "negative", "named")
v12590 = _always({"k": 1}, 2, -1, "negative")


def s12575(rng): return _always(pick(rng, [1, 1, 2, 3]), nz(rng, -8, 8), {"k": 1}, "positive")


def s12586(rng): return _always(pick(rng, [-1, -2, -3]), nz(rng, -8, 8), {"k": 1, "c": rng.randint(-5, 5)}, "negative", "named")


def s12590(rng): return _always({"k": 1}, nz(rng, -6, 6), pick(rng, [-1, -2, -3, -4]), "negative")


# --- 平移 ------------------------------------------------------------------------------------------

v12577 = {"items": [{"kind": "reflect_x", "f": [-3, 0, 0]}]}


def s12577(rng): return {"items": [{"kind": "reflect_x", "f": [nz(rng, -5, 5), pick(rng, [0, 0, 2, -3, 4]), pick(rng, [0, 0, 1, -2])]}]}


v12578 = {"items": [{"kind": "overlap", "f": [2, 0, 0], "g": [2, 8, 5]}]}


def s12578(rng):
    a = pick(rng, [1, 2, 3, -1, -2, "1/2"])
    return {"items": [{"kind": "overlap", "f": quad_from_vertex(a, 0, 0), "g": quad_from_vertex(a, nz(rng, -4, 4), nz(rng, -5, 5))}]}


v12581 = {"items": [{"kind": "translate", "f": [2, 8, 5], "right": -2, "up": 5}]}


def s12581(rng): return {"items": [{"kind": "translate", "f": _rand_quad(rng), "right": nz(rng, -4, 4), "up": nz(rng, -6, 6)}]}


v12588 = {"items": [{"kind": "find_translation", "f": [4, -8, 0], "g": [4, 8, 9]}]}


def s12588(rng):
    a = pick(rng, [1, 2, 3, 4, -1, -2])
    h1, k1 = rng.randint(-1, 4), rng.randint(-5, 2)
    return {"items": [{"kind": "find_translation", "f": quad_from_vertex(a, h1, k1), "g": quad_from_vertex(a, h1 - rng.randint(1, 5), k1 + rng.randint(1, 8))}]}


# --- 應用問題 --------------------------------------------------------------------------------------

def _app(**item: Any) -> dict[str, Any]:
    return {"items": [item]}


v12573 = _app(kind="tile_cost", side=4, costs=[30, 20, 10])


def s12573(rng): return _app(kind="tile_cost", side=rng.randint(3, 6), costs=[pick(rng, [20, 30, 40, 50]), pick(rng, [10, 20, 30]), pick(rng, [5, 10, 15, 20])])


v12574 = _app(kind="profit", cost=[5, 2], revenue={"mode": "table", "points": [[5, 45], [10, 80]]})


def s12574(rng):
    a = Fraction(-rng.randint(1, 3), pick(rng, [1, 2, 4, 5]))
    b = rng.randint(6, 14)
    x1 = a.denominator * rng.randint(1, 3)
    x2 = x1 + a.denominator * rng.randint(1, 3)
    g = lambda x: j(a * x * x + b * x)  # noqa: E731
    return _app(kind="profit", cost=[rng.randint(3, 9), rng.randint(1, 4)], revenue={"mode": "table", "points": [[x1, g(x1)], [x2, g(x2)]]})


v12585 = _app(kind="profit", cost=[200, 30], revenue={"mode": "given", "a": "-1/5", "b": 50})


def s12585(rng): return _app(kind="profit", cost=[rng.randint(100, 300), rng.randint(10, 40)], revenue={"mode": "given", "a": pick(rng, ["-1/5", "-1/4", "-1/2", "-1/10"]), "b": rng.randint(45, 80)})


v12584 = _app(kind="circle_areas", diameter=6)


def s12584(rng): return _app(kind="circle_areas", diameter=rng.randint(2, 30) * 2)


v12595 = _app(kind="fenced_pens", pens=3, fence=48)


def s12595(rng):
    n = rng.randint(2, 6)
    return _app(kind="fenced_pens", pens=n, fence=rng.randint(10, 30) * 2 * (n + 1) // 2)


v12592 = _app(kind="ball", a=5, b=20, height=15)


def s12592(rng):
    a, big_t = pick(rng, [1, 2, 4, 5, 10]), rng.randint(4, 10)
    t = rng.randint(1, big_t - 1)
    return _app(kind="ball", a=a, b=a * big_t, height=a * t * (big_t - t))


v12596 = _app(kind="basket", apex_x="2.5", apex_y="3.5", start_y="2.25", hoop_x=4)


def s12596(rng):
    return _app(kind="basket", apex_x=dec(Fraction(rng.randint(4, 6), 2)), apex_y=dec(Fraction(rng.randint(30, 40), 10)),
                start_y=dec(Fraction(rng.randint(18, 26), 10)), hoop_x=rng.randint(3, 5))


v12597 = _app(kind="fountain", nozzle=2, land=3, radius=1)


def s12597(rng):
    r = pick(rng, [1, 1, 2])
    return _app(kind="fountain", nozzle=rng.randint(1, 4), land=2 * r + rng.randint(1, 4), radius=r)


v12593 = _app(kind="roots_intercept", root1=-1, root2=-9, y_intercept=9)


def s12593(rng): return _app(kind="roots_intercept", root1=nz(rng, -6, 6), root2=nz(rng, -9, 9), y_intercept=nz(rng, -9, 9))


v12594 = _app(kind="max_condition", apex_x=3, max_value=8)


def s12594(rng):
    a = Fraction(-pick(rng, [1, 2, 3, 4]), pick(rng, [1, 1, 2, 3]))
    p = rng.randint(1, 4)
    return _app(kind="max_condition", apex_x=p, max_value=j((1 - a * a * p * p) / a))


# --- 圖形判讀與概念題 ---------------------------------------------------------------------------------

def _parabola(a: Any, r1: Any, r2: Any) -> dict[str, Any]:
    return {"subject": {"type": "parabola", "a": a, "root1": r1, "root2": r2}, "mode": "select",
            "statements": [{"kind": "negative_quantity", "expr": e} for e in ("a", "b", "c", "D", "a-b+c")]}


v12591 = _parabola(-1, -2, "1/2")


def s12591(rng):
    r1 = pick(rng, [-4, -3, -2, -1, "-1/2", 0, "1/2", 1, 2])
    r2 = pick(rng, [-2, "-1/2", "1/2", 1, 2, 3, 4])
    return _parabola(pick(rng, [-2, -1, 1, 2]), r1, r2)


v12599 = _generic_truth({"kind": "translation_claim", "a": 2, "direction": "left", "amount": 1, "claim_h": -1, "claim_k": 0})


def s12599(rng):
    amount, direction = rng.randint(1, 4), pick(rng, ["left", "right"])
    true_h = -amount if direction == "left" else amount
    return _generic_truth({"kind": "translation_claim", "a": pick(rng, [1, 2, 3, -1, -2, -3]), "direction": direction, "amount": amount,
                           "claim_h": true_h if rng.random() < 0.4 else -true_h if rng.random() < 0.6 else true_h + nz(rng, -2, 2), "claim_k": 0})


v12600 = _generic_truth({"kind": "axis_claim", "p": 2, "q": 1, "r": 3, "p2": 2, "q2": 1})


def s12600(rng):
    p, q = pick(rng, [1, 2, 3]), nz(rng, -4, 4)
    p2, q2 = (p, q) if rng.random() < 0.35 else pick(rng, [(1, q), (p, -q), (p, q + 1), (1, 1), (2, 1)])
    return _generic_truth({"kind": "axis_claim", "p": p, "q": q, "r": nz(rng, -5, 5), "p2": p2, "q2": q2})


v12601 = _generic_truth({"kind": "interval_max_claim", "a": -1, "h": 1, "k": 5, "lo": 2, "hi": 4, "claim_x": 2})


def s12601(rng):
    a, h, k = pick(rng, [-1, -2, 1, 2]), rng.randint(-1, 3), rng.randint(-3, 6)
    lo = rng.randint(h - 2, h + 2)
    hi = lo + rng.randint(1, 3)
    return _generic_truth({"kind": "interval_max_claim", "a": a, "h": h, "k": k, "lo": lo, "hi": hi, "claim_x": pick(rng, [lo, hi, h if lo <= h <= hi else lo])})


v12602 = _generic_truth({"kind": "intercept_claim", "always": "y"})


def s12602(rng): return _generic_truth({"kind": "intercept_claim", "always": pick(rng, ["y", "x"])})


# --- component table ---------------------------------------------------------------------------------

def _c(skill: str, op: str, source: dict, sampler: Callable) -> tuple:
    return (skill, op, source, sampler)


COMPONENTS: dict[int, tuple] = {
    12560: _c("lin", "solve_linear_functions", v12560, s12560),
    12561: _c("lin", "solve_linear_functions", v12561, s12561),
    12562: _c("lin", "evaluate_function_statements", v12562, s12562),
    12563: _c("lin", "solve_linear_functions", v12563, s12563),
    12564: _c("lin", "solve_linear_functions", v12564, s12564),
    12565: _c("lin", "solve_linear_functions", v12565, s12565),
    12566: _c("lin", "evaluate_function_statements", v12566, s12566),
    12598: _c("lin", "evaluate_function_statements", v12598, s12598),
    12569: _c("quad", "complete_square_items", v12569, s12569),
    12571: _c("quad", "quadratic_extrema", v12571, s12571),
    12572: _c("quad", "quadratic_extrema", v12572, s12572),
    12573: _c("quad", "solve_quadratic_applications", v12573, s12573),
    12574: _c("quad", "solve_quadratic_applications", v12574, s12574),
    12575: _c("quad", "quadratic_always_sign", v12575, s12575),
    12577: _c("quad", "quadratic_graph_transformations", v12577, s12577),
    12578: _c("quad", "quadratic_graph_transformations", v12578, s12578),
    12579: _c("quad", "complete_square_items", v12579, s12579),
    12580: _c("quad", "quadratic_vertex_axis", v12580, s12580),
    12581: _c("quad", "quadratic_graph_transformations", v12581, s12581),
    12582: _c("quad", "quadratic_extrema", v12582, s12582),
    12583: _c("quad", "quadratic_extrema", v12583, s12583),
    12584: _c("quad", "solve_quadratic_applications", v12584, s12584),
    12585: _c("quad", "solve_quadratic_applications", v12585, s12585),
    12586: _c("quad", "quadratic_always_sign", v12586, s12586),
    12588: _c("quad", "quadratic_graph_transformations", v12588, s12588),
    12589: _c("quad", "quadratic_extrema", v12589, s12589),
    12590: _c("quad", "quadratic_always_sign", v12590, s12590),
    12591: _c("quad", "evaluate_function_statements", v12591, s12591),
    12592: _c("quad", "solve_quadratic_applications", v12592, s12592),
    12593: _c("quad", "solve_quadratic_applications", v12593, s12593),
    12594: _c("quad", "solve_quadratic_applications", v12594, s12594),
    12595: _c("quad", "solve_quadratic_applications", v12595, s12595),
    12596: _c("quad", "solve_quadratic_applications", v12596, s12596),
    12597: _c("quad", "solve_quadratic_applications", v12597, s12597),
    12599: _c("quad", "evaluate_function_statements", v12599, s12599),
    12600: _c("quad", "evaluate_function_statements", v12600, s12600),
    12601: _c("quad", "evaluate_function_statements", v12601, s12601),
    12602: _c("quad", "evaluate_function_statements", v12602, s12602),
}


# --- 拋物線作圖題（parabola_graph grader；revision 2 候選，隔離驗證用，不在已發布的 38 題 COMPONENTS 內）------------------

def _graph(items: list, layout: str, style: str, ask: bool = False) -> dict[str, Any]:
    return {"items": items, "layout": layout, "style": style, "ask_vertex_axis": ask}


v12567 = _graph([{"coeffs": [1, 0, 0]}], "single", "plain")


def s12567(rng): return _graph([{"coeffs": [pick(rng, [1, 2, 3, 4, 5, -1, -2, -3, -4, -5, "1/2", "-1/2", "1/3", "-1/3", "1/4", "-1/4", "3/2", "-3/2", "2/3", "-2/3"]), 0, 0]}], "single", "plain")


v12568 = _graph([{"coeffs": [3, 0, 0], "name": "f"}, {"coeffs": quad_from_vertex(3, 2, 0), "name": "g", "form": "vertex"},
                 {"coeffs": quad_from_vertex(3, 2, 4), "name": "h", "form": "vertex"}], "same_canvas", "same_plane")


def s12568(rng):
    a, h, k = pick(rng, [1, 2, 3, -1, -2]), nz(rng, -3, 3), nz(rng, -4, 4)
    return _graph([{"coeffs": [a, 0, 0], "name": "f"}, {"coeffs": quad_from_vertex(a, h, 0), "name": "g", "form": "vertex"},
                   {"coeffs": quad_from_vertex(a, h, k), "name": "h", "form": "vertex"}], "same_canvas", "same_plane")


v12570 = _graph([{"coeffs": [-2, 4, 3]}], "single", "plain", True)


def s12570(rng): return _graph([{"coeffs": quad_from_vertex(pick(rng, [1, 2, -1, -2, -3]), rng.randint(-3, 3), rng.randint(-4, 5))}], "single", "plain", True)


v12576 = _graph([{"coeffs": [2, 0, 0]}, {"coeffs": [-1, 0, 0]}], "separate", "planes")


def s12576(rng):
    a, b = rng.sample([1, 2, 3, -1, -2, -3, "1/2", "-1/2"], 2)
    return _graph([{"coeffs": [a, 0, 0]}, {"coeffs": [b, 0, 0]}], "separate", "planes")


v12587 = _graph([{"coeffs": [1, -2, -3]}, {"coeffs": [-2, 1, 3]}], "separate", "list", True)


def s12587(rng):
    return _graph([{"coeffs": [pick(rng, [1, 2, -1, -2]), nz(rng, -6, 6), rng.randint(-5, 5)]} for _ in range(2)], "separate", "list", True)


DRAWING_COMPONENTS: dict[int, tuple] = {
    12567: _c("quad", "graph_quadratic_functions", v12567, s12567),
    12568: _c("quad", "graph_quadratic_functions", v12568, s12568),
    12570: _c("quad", "graph_quadratic_functions", v12570, s12570),
    12576: _c("quad", "graph_quadratic_functions", v12576, s12576),
    12587: _c("quad", "graph_quadratic_functions", v12587, s12587),
}

# 12568 needs the real vision model to separate three curves on one canvas; until that is shown it stays DEFERRED.
HELD_UNTIL_REAL_AI = {12568: "three curves on one canvas: not publishable until the real vision model is shown to read them reliably"}
