"""Per-component *inputs* for 普高數學1 Unit 5 (直線方程式).

Each entry gives the source-faithful givens (variant 0) and a sampler for further variants of the
same shape.  Samplers only choose inputs; the domain computes every answer.  Display strings
(``stem``) are descriptive text only and never carry an answer.
"""

from __future__ import annotations

import random
from fractions import Fraction
from math import gcd
from typing import Any, Callable

SKILLS = {
    "ls": "gh_LineSlope",
    "eq": "gh_EquationOfALine",
    "tr": "gh_TranslationOfALine",
    "pp": "gh_ParallelAndPerpendicularLines",
    "di": "gh_DistanceFromPointToLine",
    "ineq": "gh_LinearInequalityInTwoVariables",
}

# 教材題目中無法落入 Spec §5 五種正式作答契約的題目（記錄原因，不進 wrapper）
DEFERRED: dict[int, str] = {}
_FORMER_DEFERRED = {
    12428: "同一題要求三個獨立的圖示（每小題各一張圖）；drawing 契約只定義單一 canvas 單一圖的 AI 判圖，多圖作答拓撲未定義",
    12447: "同一題同時要求作圖與數值（格子點個數）；multi_part 內的 drawing part 沒有正式契約，drawing 又不得降級為 short_answer",
}

OP = {name: name for name in (
    "rank_line_slopes", "evaluate_slope_sign_statements", "solve_line_equations", "slope_of_line_from_equation",
    "fill_line_property_table", "translate_line_equation", "solve_translation_parameter", "solve_line_constructions",
    "solve_line_parameters", "compute_line_distances", "solve_window_decorative_lines", "solve_triangle_region_system",
    "read_region_signs_from_figure", "solve_region_coefficients_from_figure", "evaluate_line_statement_truth",
    "select_points_same_side", "graph_inequality_system", "solve_rectangle_perpendicular_diagonals",
    "solve_axis_triangle_area_line", "solve_parallel_line_family", "graph_inequality_series",
    "graph_inequality_with_lattice_count",
)}


# --- display helpers -----------------------------------------------------------------------------

def fr(value: Any) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def P(p: Any, name: str = "") -> str:
    def f(v: Any) -> str:
        v = fr(v)
        return str(v.numerator) if v.denominator == 1 else (f"-\\frac{{{abs(v.numerator)}}}{{{v.denominator}}}" if v < 0 else f"\\frac{{{v.numerator}}}{{{v.denominator}}}")
    return f"{name}\\left({f(p[0])},\\ {f(p[1])}\\right)"


def expr(a: Any, b: Any, c: Any = 0) -> str:
    out = ""
    for coef, var in ((fr(a), "x"), (fr(b), "y")):
        if coef == 0:
            continue
        mag = "" if abs(coef) == 1 else str(abs(coef.numerator)) if coef.denominator == 1 else f"\\frac{{{abs(coef.numerator)}}}{{{coef.denominator}}}"
        out += f"{'-' if coef < 0 else ('+' if out else '')}{mag}{var}"
    c = fr(c)
    if c:
        out += f"{'-' if c < 0 else '+'}{abs(c.numerator) if c.denominator == 1 else abs(c)}"
    return out or "0"


def eq_const(a: Any, b: Any, k: Any) -> str:
    """Textbook style ``ax+by=k``."""
    return f"{expr(a, b)}={fr(k)}"


def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def nz(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v:
            return v


def frac_slope(rng: random.Random) -> Fraction:
    return pick(rng, [Fraction(n, d) for n in (-3, -2, -1, 1, 2, 3) for d in (1, 2, 3)])


PYTH = [(3, 4), (4, 3), (5, 12), (12, 5), (6, 8), (8, 6), (8, 15), (15, 8)]


# --- compare / slope signs --------------------------------------------------------------------------

def _slopes_through_pivot(pivot: list[int], targets: list[list[int]]) -> dict[str, Any]:
    return {
        "pivot": {"name": "A", "p": pivot},
        "lines": [{"index": i, "p": pivot, "q": q} for i, q in enumerate(targets, start=1)],
        "ask": "slopes_and_order",
    }


v12403 = _slopes_through_pivot([1, 1], [[2, 2], [3, 2], [3, 1], [3, 0], [2, 0]])


def s12403(rng):
    pivot = [rng.randint(0, 3), rng.randint(0, 3)]
    options = [(dx, dy) for dx in (1, 2, 3) for dy in range(-3, 4)]
    chosen, seen = [], set()
    while len(chosen) < 5:
        dx, dy = pick(rng, options)
        slope = Fraction(dy, dx)
        if slope in seen:
            continue
        seen.add(slope)
        chosen.append((dx, dy))
    chosen.sort(key=lambda t: Fraction(t[1], t[0]), reverse=True)
    return _slopes_through_pivot(pivot, [[pivot[0] + dx, pivot[1] + dy] for dx, dy in chosen])


def _four_lines(slopes_b: list[tuple[Fraction, int]]) -> dict[str, Any]:
    lines = []
    for index, (m, b) in enumerate(slopes_b, start=1):
        den = m.denominator
        lines.append({"index": index, "p": [0, b], "q": [den, b + m.numerator]})
    return {"lines": lines, "ask": "order_only"}


v12436 = _four_lines([(Fraction(1, 3), 1), (Fraction(-2, 3), 3), (Fraction(3, 2), -1), (Fraction(-3), 4)])


def s12436(rng):
    pool = [Fraction(n, d) for n, d in ((1, 3), (1, 2), (1, 1), (2, 1), (3, 1), (-1, 3), (-1, 2), (-1, 1), (-2, 1), (-3, 1), (-2, 3), (2, 3))]
    slopes = rng.sample(pool, 4)
    return _four_lines([(m, rng.randint(-3, 4)) for m in slopes])


def _sign_statements(points: dict[str, list[int]], statements: list[dict[str, Any]]) -> dict[str, Any]:
    return {"points": points, "segments": [["A", "B"], ["B", "C"], ["A", "C"]], "statements": statements}


_STD_STATEMENTS = [
    {"kind": "sign", "index": 1, "op": ">"}, {"kind": "sign", "index": 2, "op": ">"},
    {"kind": "product", "op": ">"}, {"kind": "sum", "op": ">"}, {"kind": "chain", "order": [3, 2, 1]},
]
v12404 = _sign_statements({"A": [1, 2], "B": [4, 0], "C": [5, 3]}, _STD_STATEMENTS)


def s12404(rng):
    while True:
        pts = {n: [rng.randint(0, 6), rng.randint(0, 5)] for n in "ABC"}
        xs = [p[0] for p in pts.values()]
        if len(set(xs)) < 3:
            continue
        cross = (pts["B"][0] - pts["A"][0]) * (pts["C"][1] - pts["A"][1]) - (pts["C"][0] - pts["A"][0]) * (pts["B"][1] - pts["A"][1])
        if cross == 0:
            continue
        statements = [dict(s) for s in _STD_STATEMENTS]
        statements[0]["op"] = pick(rng, [">", "<"])
        statements[1]["op"] = pick(rng, [">", "<"])
        statements[2]["op"] = pick(rng, [">", "<"])
        statements[3]["op"] = pick(rng, [">", "<"])
        statements[4]["order"] = pick(rng, [[3, 2, 1], [1, 2, 3], [2, 1, 3], [3, 1, 2], [1, 3, 2], [2, 3, 1]])
        return _sign_statements(pts, statements)


# --- line equations ----------------------------------------------------------------------------------------

def _ps(p, m):
    return {"kind": "point_slope", "p": p, "m": str(m)}


def _two(p, q, names=None):
    item = {"kind": "two_points", "p": p, "q": q}
    if names:
        item["names"] = names
    return item


def _syi(m, b):
    return {"kind": "slope_y_intercept", "m": str(m), "b": b}


def _xyi(a, b):
    return {"kind": "intercepts", "a": a, "b": b}


def _distinct_points(rng, n=2, span=5):
    while True:
        pts = [[rng.randint(-span, span), rng.randint(-span, span)] for _ in range(n)]
        if pts[0][0] != pts[1][0] and pts[0][1] != pts[1][1]:
            return pts


v12405 = {"stem": "求下列各直線的方程式：", "items": [_ps([-2, 1], -3), _two([1, 2], [4, 1], {"p": "A", "q": "B"})]}


def s12405(rng):
    p, = [[rng.randint(-4, 4), rng.randint(-4, 4)]]
    a, b = _distinct_points(rng)
    return {"stem": "求下列各直線的方程式：", "items": [_ps(p, frac_slope(rng)), _two(a, b, {"p": "A", "q": "B"})]}


v12406 = {"stem": "求下列各直線的方程式：", "items": [_syi(-2, 3), _xyi(4, -3)]}


def s12406(rng):
    return {"stem": "求下列各直線的方程式：", "items": [_syi(frac_slope(rng), nz(rng, -6, 6)), _xyi(nz(rng, -6, 6), nz(rng, -6, 6))]}


v12408 = {"stem": "求下列各直線的方程式：", "items": [_ps([2, -1], Fraction(2, 3)), _two([3, -2], [1, 5], {"p": "A", "q": "B"}),
                                                  {"kind": "vertical_through", "p": [2, 5]}]}


def s12408(rng):
    a, b = _distinct_points(rng)
    return {"stem": "求下列各直線的方程式：", "items": [
        _ps([rng.randint(-4, 4), rng.randint(-4, 4)], frac_slope(rng)), _two(a, b, {"p": "A", "q": "B"}),
        {"kind": "vertical_through", "p": [rng.randint(-5, 5), rng.randint(-5, 5)]}]}


v12409 = {"stem": "求下列各直線的方程式：", "items": [_syi(2, -5), _xyi(-2, -3)]}


def s12409(rng):
    return {"stem": "求下列各直線的方程式：", "items": [_syi(frac_slope(rng), nz(rng, -6, 6)), _xyi(nz(rng, -6, 6), nz(rng, -6, 6))]}


def _named_pair(point, line):
    return {
        "stem": f"給定點 ${P(point, 'A')}$ 及直線 $L:{expr(*line)}=0$。",
        "items": [
            {"kind": "parallel_through", "p": point, "line": line, "names": {"label": "L_{1}", "through": "A", "ref": "L"}},
            {"kind": "perpendicular_through", "p": point, "line": line, "names": {"label": "L_{2}", "through": "A", "ref": "L"}},
        ],
    }


v12413 = _named_pair([3, 1], [1, 2, 4])


def s12413(rng):
    return _named_pair([rng.randint(-4, 5), rng.randint(-4, 5)], [nz(rng, -3, 3), nz(rng, -3, 3), rng.randint(-6, 6)])


def _mixed_five(two, ps, inter, perp, par):
    return {
        "stem": "求下列各直線方程式：",
        "items": [
            _two(two[0], two[1]), _ps(ps[0], ps[1]), _xyi(*inter),
            {"kind": "perpendicular_through", "p": perp[0], "line": perp[1], "line_display": eq_const(perp[1][0], perp[1][1], -perp[1][2])},
            {"kind": "parallel_through_intersection", "l1": par[0], "l2": par[1], "line": par[2],
             "l1_display": eq_const(par[0][0], par[0][1], -par[0][2]), "l2_display": eq_const(par[1][0], par[1][1], -par[1][2]),
             "line_display": eq_const(par[2][0], par[2][1], -par[2][2])},
        ],
    }


v12437 = _mixed_five(([-1, 2], [0, 3]), ([0, 3], -4), (-3, 5), ([2, 3], [5, -2, -1]), ([1, 2, -3], [2, -1, -1], [2, -3, -7]))


def s12437(rng):
    while True:
        a, b = _distinct_points(rng, span=4)
        l1 = [nz(rng, -3, 3), nz(rng, -3, 3), rng.randint(-6, 6)]
        l2 = [nz(rng, -3, 3), nz(rng, -3, 3), rng.randint(-6, 6)]
        if l1[0] * l2[1] - l1[1] * l2[0] == 0:
            continue
        return _mixed_five((a, b), ([rng.randint(-4, 4), rng.randint(-4, 4)], frac_slope(rng)), (nz(rng, -6, 6), nz(rng, -6, 6)),
                           ([rng.randint(-4, 4), rng.randint(-4, 4)], [nz(rng, -5, 5), nz(rng, -5, 5), rng.randint(-5, 5)]),
                           (l1, l2, [nz(rng, -4, 4), nz(rng, -4, 4), rng.randint(-7, 7)]))


def _slope_of(line):
    return {"line": line, "name": "L", "line_display": f"{expr(*line)}=0"}


v12407 = _slope_of([3, -2, -5])


def s12407(rng):
    return _slope_of([nz(rng, -6, 6), nz(rng, -6, 6), nz(rng, -9, 9)])


def _table(rows):
    return {"stem": "在下列的表格中填入適當的答案：", "rows": rows}


v12410 = _table([{"given": "equation", "line": [2, 1, -4]}, {"given": "slope_y_intercept", "m": "3", "b": -2},
                 {"given": "slope_x_intercept", "m": "-2", "a": 3}])


def s12410(rng):
    return _table([
        {"given": "equation", "line": [nz(rng, -4, 4), nz(rng, -4, 4), nz(rng, -8, 8)]},
        {"given": "slope_y_intercept", "m": str(nz(rng, -4, 4)), "b": nz(rng, -6, 6)},
        {"given": "slope_x_intercept", "m": str(nz(rng, -4, 4)), "a": nz(rng, -6, 6)},
    ])


# --- translation --------------------------------------------------------------------------------------------

def _translate(line, dx, dy, direction, first="x"):
    return {"line": line, "dx": dx, "dy": dy, "direction": direction, "first": first}


v12411 = _translate([2, 3, 6], -1, 2, "forward")
v12412 = _translate([3, -4, 0], 3, -2, "inverse")


def _s_translate(direction):
    def sampler(rng):
        return _translate([nz(rng, -4, 4), nz(rng, -4, 4), rng.randint(-8, 8)], nz(rng, -5, 5), nz(rng, -5, 5), direction, pick(rng, ["x", "y"]))
    return sampler


s12411, s12412 = _s_translate("forward"), _s_translate("inverse")
v12438 = {"line": [3, 4, 1], "result_line": [3, 4, -14], "axis": "right"}


def s12438(rng):
    a, b, c, h = nz(rng, -4, 4), nz(rng, -4, 4), rng.randint(-8, 8), nz(rng, -7, 7)
    axis = pick(rng, ["right", "up"])
    c2 = c - (a if axis == "right" else b) * h
    return {"line": [a, b, c], "result_line": [a, b, c2], "axis": axis}


# --- constructions / parameters ----------------------------------------------------------------------------------------

def _three_towns(a, b, c):
    return {
        "stem": f"由A, B, C三個里決議將電信基地台設置在與三個里等距離的位置。今將此區域設定成一個坐標平面，三個里的坐標分別為 ${P(a, 'A')}$、${P(b, 'B')}$、${P(c, 'C')}$。回答下列問題：",
        "items": [
            {"kind": "perp_bisector", "p": a, "q": b, "names": {"p": "A", "q": "B"}},
            {"kind": "perp_bisector", "p": b, "q": c, "names": {"p": "B", "q": "C"}},
            {"kind": "intersect_items", "a": 0, "b": 1, "prompt": "該電信基地台的坐標為何？"},
        ],
    }


v12414 = _three_towns([5, 7], [1, 1], [7, 1])


def s12414(rng):
    while True:
        b = [rng.randint(0, 4), rng.randint(0, 4)]
        c = [b[0] + rng.randint(2, 7), b[1] if rng.random() < 0.5 else rng.randint(0, 6)]
        a = [rng.randint(0, 9), rng.randint(0, 9)]
        cross = (c[0] - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (c[1] - b[1])
        if cross != 0 and len({tuple(a), tuple(b), tuple(c)}) == 3:
            return _three_towns(a, b, c)


def _reflect(p, line, display, name="A"):
    return {"stem": "", "items": [{"kind": "reflect_point", "p": p, "line": line, "line_display": display, "names": {"p": name}}]}


v12415 = _reflect([3, 1], [1, -1, 0], "x-y=0")
v12418 = _reflect([2, 4], [1, 1, 0], "x+y=0")


def _s_reflect(rng):
    k = rng.randint(-4, 4)
    sign = pick(rng, [1, -1])
    line = [1, sign, k]
    display = f"x{'+' if sign > 0 else '-'}y{'+' if k > 0 else '-'}{abs(k)}=0" if k else f"x{'+' if sign > 0 else '-'}y=0"
    return _reflect([rng.randint(-5, 6), rng.randint(-5, 6)], line, display)


s12415 = s12418 = _s_reflect


def _fig_pts(**kw):
    return kw


def _supermarket(s, a, b):
    return {
        "stem": f"如圖，在筆直道路上有學校 $S$ 及小鎮 $A$，而小鎮 $B$ 不在此道路上。為了要在這條道路上蓋一家超級市場，使其與 $A$, $B$ 兩小鎮等距離，"
                f"將此區域設定成一個坐標平面，學校與二個小鎮的坐標分別為 ${P(s, 'S')}$、${P(a, 'A')}$、${P(b, 'B')}$。回答下列問題：",
        "items": [
            {"kind": "line_through", "p": s, "q": a, "names": {"p": "S", "q": "A"}},
            {"kind": "perp_bisector", "p": a, "q": b, "names": {"p": "A", "q": "B"}},
            {"kind": "intersect_items", "a": 0, "b": 1, "prompt": "該超級市場的坐標為何？"},
        ],
        "figure": {"points": [{"name": "S", "p": s, "label": f"S({s[0]},{s[1]})"}, {"name": "A", "p": a, "label": f"A({a[0]},{a[1]})"},
                              {"name": "B", "p": b, "label": f"B({b[0]},{b[1]})"}],
                   "lines": [{"through": ["S", "A"]}], "pad": 2},
    }


v12417 = _supermarket([-1, 1], [9, 3], [3, 7])


def s12417(rng):
    while True:
        s = [rng.randint(-3, 2), rng.randint(0, 3)]
        a = [s[0] + rng.randint(4, 10), s[1] + rng.randint(1, 4)]
        b = [rng.randint(0, 8), rng.randint(4, 9)]
        sa = (a[0] - s[0], a[1] - s[1])
        ab = (b[0] - a[0], b[1] - a[1])
        if sa[0] * ab[0] + sa[1] * ab[1] != 0 and a != b and ab != (0, 0) and (b[1] - s[1]) * sa[0] != (b[0] - s[0]) * sa[1]:
            return _supermarket(s, a, b)


def _centers(a, b, c):
    return {"stem": f"設 ${P(a, 'A')}$、${P(b, 'B')}$、${P(c, 'C')}$。", "items": [
        {"kind": "circumcenter", "pts": [a, b, c], "prompt": "求△ABC的外心坐標。（外心為三中垂線的交點）"},
        {"kind": "orthocenter", "pts": [a, b, c], "prompt": "求△ABC的垂心坐標。（垂心為三高的交點）"}]}


v12440 = _centers([-1, 5], [7, 1], [5, -3])


def s12440(rng):
    while True:
        pts = [[rng.randint(-4, 8), rng.randint(-4, 7)] for _ in range(3)]
        cross = (pts[1][0] - pts[0][0]) * (pts[2][1] - pts[0][1]) - (pts[2][0] - pts[0][0]) * (pts[1][1] - pts[0][1])
        if cross != 0 and len({tuple(p) for p in pts}) == 3:
            return _centers(*pts)


def _path(a, b):
    return {
        "stem": f"將電腦螢幕視為坐標平面，在網路虛擬戰爭遊戲中，彈藥補給車在 $x$ 軸上移動，某士兵從堡壘 ${P(a, 'A')}$ 的位置出發，需先到補給車補充彈藥後，"
                f"再移動至堡壘 ${P(b, 'B')}$ 的位置換防。已知該士兵以最短的距離完成換防任務，回答下列問題：",
        "items": [
            {"kind": "shortest_path_point_on_axis", "a": a, "b": b, "prompt": "求該士兵補充彈藥時，補給車所在位置的坐標。"},
            {"kind": "shortest_path_length", "a": a, "b": b, "prompt": "求該士兵移動的最短距離。"},
        ],
        "figure": {"points": [{"name": "A", "p": a, "label": "A"}, {"name": "B", "p": b, "label": "B"}], "lines": [],
                   "general_lines": [[0, 1, 0]], "pad": 2},  # the x-axis the supply vehicle moves on
    }


v12446 = _path([2, 3], [6, 9])


def s12446(rng):
    a = [rng.randint(0, 6), rng.randint(1, 5)]
    b = [a[0] + rng.randint(2, 7), rng.randint(2, 10)]
    return _path(a, b)


def _perp_at_point(a, b):
    ax, ay = a
    bx, by = b
    return {
        "stem": f"如圖，已知點 ${P(a, 'A')}$ 在直線 $L:ax+y+c=0$ 上，點 ${P(b, 'B')}$ 為 $L$ 外一點，使得 $\\overline{{AB}}\\bot L$，求 $a,\\ c$ 的值。",
        "unknowns": ["a", "c"], "lines": {"L": ["a", "1", "c"]},
        "conditions": [{"kind": "on_line", "point": a, "line": "L"}, {"kind": "perpendicular_to_segment", "p": a, "q": b, "line": "L"}],
        "targets": [{"name": "a", "expr": "a"}, {"name": "c", "expr": "c"}],
        "figure": {"points": [{"name": "A", "p": a, "label": "A"}, {"name": "B", "p": b, "label": "B"},
                              {"name": "Q", "p": [ax + (by - ay), ay - (bx - ax)], "label": ""}],
                   "lines": [{"through": ["A", "Q"], "label": "L"}, {"through": ["A", "B"], "extend": False}], "pad": 2, "hide_unlabeled": True},
    }


v12416 = _perp_at_point([2, 1], [5, 3])


def s12416(rng):
    while True:
        a = [rng.randint(-2, 4), rng.randint(-2, 4)]
        b = [rng.randint(-2, 7), rng.randint(-2, 7)]
        if a[1] != b[1] and a != b:
            return _perp_at_point(a, b)


def _perp_at_intersection(p, q, a, m, k):
    u, b = -k * m, k * a
    k1 = a * p + m * q
    c = u * p + b * q
    return {
        "stem": f"已知兩直線 $L_1:ax+{m}y={k1}$ 與 $L_2:{u}x+by=c$ 互相垂直於點 ${P([p, q])}$，求 $a+b+c$ 的值。".replace("+-", "-"),
        "unknowns": ["a", "b", "c"], "lines": {"L1": ["a", str(m), str(-k1)], "L2": [str(u), "b", "-c"]},
        "conditions": [{"kind": "on_line", "point": [p, q], "line": "L1"}, {"kind": "on_line", "point": [p, q], "line": "L2"},
                       {"kind": "perpendicular", "l1": "L1", "l2": "L2"}],
        "targets": [{"name": "a+b+c", "expr": "a+b+c"}],
    }


v12439 = _perp_at_intersection(3, 2, 2, 3, -2)


def s12439(rng):
    while True:
        p, q = nz(rng, -4, 5), rng.randint(-3, 4)
        a, m, k = nz(rng, -4, 4), nz(rng, 1, 4), nz(rng, -3, 3)
        return _perp_at_intersection(p, q, a, m, k)


def _distance_param(p, a, b, d):
    return {
        "stem": f"已知點 ${P(p, 'P')}$ 到直線 $L:{a}x{'+' if b > 0 else '-'}{abs(b)}y+k=0$ 的距離為 ${d}$，求 $k$ 的值。".replace("L:1x", "L:x"),
        "unknowns": ["k"], "lines": {"L": [str(a), str(b), "k"]},
        "conditions": [{"kind": "point_line_distance", "point": p, "line": "L", "distance": str(d)}],
        "targets": [{"name": "k", "expr": "k"}],
    }


v12422 = _distance_param([-2, 1], 12, -5, 2)


def s12422(rng):
    a, b = pick(rng, PYTH)
    return _distance_param([rng.randint(-4, 4), rng.randint(-4, 4)], a, b * pick(rng, [1, -1]), rng.randint(1, 4))


# --- distances ------------------------------------------------------------------------------------------------------------------

def _one_distance(item):
    return {"stem": "", "items": [item]}


v12419 = _one_distance({"kind": "point_to_line", "p": [3, 1], "name": "P", "line": [3, -4, 5]})


def s12419(rng):
    a, b = pick(rng, PYTH + [(1, 1), (1, 2), (2, 3)])
    return _one_distance({"kind": "point_to_line", "p": [rng.randint(-5, 6), rng.randint(-5, 6)], "name": "P",
                          "line": [a * pick(rng, [1, 1, -1]), b * pick(rng, [1, -1]), rng.randint(-9, 9)]})


v12420 = _one_distance({"kind": "parallel_lines", "l1": [3, 4, 11], "l2": [6, 8, -9]})


def s12420(rng):
    while True:
        a, b = pick(rng, PYTH)
        k = pick(rng, [2, 3, -2, -3])
        c1, c2 = rng.randint(-12, 12), rng.randint(-20, 20)
        if Fraction(c2, k) != c1:
            return _one_distance({"kind": "parallel_lines", "l1": [a, b, c1], "l2": [a * k, b * k, c2]})


v12423 = _one_distance({"kind": "parallel_lines", "l1": [1, -2, 3], "l2": ["1/2", "-1", "-1"], "l1_display": "x-2y+3=0",
                        "l2_display": "\\frac{x}{2}-y=1"})


def s12423(rng):
    while True:
        a, b = pick(rng, [(1, -2), (1, 2), (2, 1), (1, 3), (3, 1), (2, -1), (1, -1), (1, 1)])
        c1 = rng.randint(-6, 6)
        c2 = rng.randint(-6, 6)
        if Fraction(c2, 2) * 1 != c1 and (a, b) != (0, 0):
            return _one_distance({"kind": "parallel_lines", "l1": [a, b, c1], "l2": [str(Fraction(a, 2)), str(Fraction(b, 2)), str(Fraction(c2, 2))]})


def _window(w, h, delta, asks):
    return {"width": w, "height": h, "edge_point": [w, h // 2 - w // 2 + 0], "delta_c": delta, "asks": asks}


v12421 = _window(34, 44, 6, ["l1_equation", "l2_equation"])
v12424 = _window(34, 44, 6, ["distance_origin_l1", "line_count"])


def _s_window(asks, avoid_corner):
    def sampler(rng):
        while True:
            w = rng.randint(8, 18) * 2
            h = w + rng.randint(2, 10) * 2
            delta = pick(rng, [4, 6, 8, 10])
            half = (w + h) // 2
            if avoid_corner and (half % delta == 0):
                continue
            if h // 2 - w // 2 < 2:
                continue
            return _window(w, h, delta, asks)
    return sampler


s12421 = _s_window(["l1_equation", "l2_equation"], False)
s12424 = _s_window(["distance_origin_l1", "line_count"], True)


# --- inequality region -------------------------------------------------------------------------------------------------------------------

def _graph(relations, view=(-6, 6, -6, 6)):
    return {"relations": relations, "view": list(view)}


def _rel(a, b, c, op, text=None):
    rel = {"coefficients": [a, b, c], "op": op}
    if text:
        rel["text"] = text
    return rel


v12425 = _graph([_rel(2, -1, 4, ">")])
v12426 = _graph([_rel(1, -1, -3, "<="), _rel(2, 1, -2, ">")])
v12429 = _graph([_rel(1, 2, -4, "<"), _rel(2, 1, -2, ">")])
v12442 = _graph([_rel(2, 1, -4, "<=", "2x+y\\le 4"), _rel(2, 1, 2, ">", "2x+y>-2")])


def s12425(rng):
    return _graph([_rel(nz(rng, -3, 3), nz(rng, -3, 3), rng.randint(-6, 6), pick(rng, [">", "<", ">=", "<="]))])


def _s_system(parallel):
    def sampler(rng):
        while True:
            r1 = [nz(rng, -3, 3), nz(rng, -3, 3), rng.randint(-6, 6)]
            if parallel:
                k = pick(rng, [1, 1, 2, -1])
                r2 = [r1[0] * k, r1[1] * k, rng.randint(-6, 6)]
                if r2[2] == r1[2] * k:
                    continue
            else:
                r2 = [nz(rng, -3, 3), nz(rng, -3, 3), rng.randint(-6, 6)]
                if r1[0] * r2[1] - r1[1] * r2[0] == 0:
                    continue
                det = r1[0] * r2[1] - r1[1] * r2[0]
                x = Fraction(r1[1] * r2[2] - r2[1] * r1[2], det)
                y = Fraction(r2[0] * r1[2] - r1[0] * r2[2], det)
                if abs(x) > 5 or abs(y) > 5:
                    continue
            ops = ["<", ">", "<=", ">="]
            rels = [_rel(*r1, pick(rng, ops)), _rel(*r2, pick(rng, ops))]
            try:
                from . import line_equations_domain as D
                D.graph_inequality_system(rels, [-6, 6, -6, 6])
            except ValueError:
                continue
            return _graph(rels)
    return sampler


s12426 = s12429 = _s_system(False)
s12442 = _s_system(True)


_CHOICE_NAMES = ("A", "B", "C", "O")


def _triangle_system(a, b, c, extras, c_pos):
    verts = {"A": a, "B": b, "C": c}
    labelled = [{"text": f"A({a[0]},{a[1]})"}, {"text": f"B({b[0]},{b[1]})"}, {"text": "O(0,0)"}] + [{"text": f"({x},{y})"} for x, y in extras]
    points = [{"point": a}, {"point": b}, {"point": [0, 0]}] + [{"point": e} for e in extras]
    choice = [{"point": a, "text": f"A({a[0]},{a[1]})"}, {"point": b, "text": f"B({b[0]},{b[1]})"}, {"point": c, "text": f"C({c[0]},{c[1]})"},
              {"point": [0, 0], "text": "O(0,0)"}] + [{"point": e, "text": f"({e[0]},{e[1]})"} for e in extras]
    _ = (labelled, points, c_pos)
    return {"vertices": verts, "choice_points": choice, "family_point": c}


v12427 = _triangle_system([3, 0], [1, 4], [0, 1], [[1, 1]], 2)


def s12427(rng):
    while True:
        a = [rng.randint(1, 5), rng.randint(-2, 2)]
        b = [rng.randint(1, 5), rng.randint(2, 6)]
        c = [0, 1]
        area2 = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
        if area2 == 0 or (a[0] + b[0]) == 0:
            continue
        extra = [rng.randint(1, 3), rng.randint(1, 3)]
        if extra in (a, b, c, [0, 0]) or extra == [0, 1]:
            continue
        spec = _triangle_system(a, b, c, [extra], 2)
        order = list(range(5))
        rng.shuffle(order)
        spec["choice_points"] = [spec["choice_points"][i] for i in order]
        return spec


def _signs(line1, d):
    return {"lines": [{"line": line1}, {"line": [2, -1, d]}], "view": [-5, 5, -5, 5],
            "statements": [{"coef": "a", "op": ">"}, {"coef": "b", "op": ">"}, {"coef": "c", "op": ">"}, {"coef": "d", "op": ">"}]}


v12430 = _signs([3, 4, -12], 2)


def s12430(rng):
    while True:
        l1 = [nz(rng, -3, 3), nz(rng, -3, 3), rng.randint(-8, 8)]
        d = nz(rng, -4, 4)
        det = l1[0] * -1 - l1[1] * 2
        if det == 0:
            continue
        x = Fraction(l1[1] * d - (-1) * l1[2], det)
        y = Fraction(2 * l1[2] - l1[0] * d, det)
        if abs(x) > 4 or abs(y) > 4:
            continue
        spec = _signs(l1, d)
        try:
            from . import line_equations_domain as D
            D.read_region_signs_from_figure(**spec)
        except ValueError:
            continue
        return spec


v12443 = {"a_point": [2, 6], "b_point": [5, 0], "bound": 5}


def s12443(rng):
    while True:
        p, q, r = rng.randint(1, 4), rng.randint(2, 7), rng.randint(3, 8)
        if p < r:
            return {"a_point": [p, q], "b_point": [r, 0], "bound": 5}


# --- true/false statements ---------------------------------------------------------------------------------------------------------------

def _st(statement):
    return {"statement": statement}


v12431 = _st({"kind": "shape_equal_slopes", "shape": "rectangle"})


def s12431(rng):
    return _st({"kind": "shape_equal_slopes", "shape": pick(rng, ["rectangle", "parallelogram", "rhombus", "trapezoid", "kite"]),
                "negated": pick(rng, [False, False, True])})


v12432 = _st({"kind": "y_intercept_of_line_through_point", "through_y": -2, "claimed": 2})


def s12432(rng):
    k = nz(rng, -6, 6)
    return _st({"kind": "y_intercept_of_line_through_point", "through_y": k, "claimed": pick(rng, [k, -k]), "slope_exists": pick(rng, [False, True])})


v12433 = _st({"kind": "perpendicular_by_coefficients", "l1": [1, 2, 3], "l2": [1, -2, 3]})


def s12433(rng):
    while True:
        l1 = [nz(rng, -4, 4), nz(rng, -4, 4), rng.randint(-6, 6)]
        if rng.random() < 0.5:
            k = nz(rng, -2, 2)
            l2 = [-l1[1] * k, l1[0] * k, rng.randint(-6, 6)]
        else:
            l2 = [nz(rng, -4, 4), nz(rng, -4, 4), rng.randint(-6, 6)]
        if l1 != l2:
            return _st({"kind": "perpendicular_by_coefficients", "l1": l1, "l2": l2})


v12434 = _st({"kind": "parallel_at_distance_count", "line": [1, 2, -5], "distance": 5, "claimed_count": 2})


def s12434(rng):
    return _st({"kind": "parallel_at_distance_count", "line": [nz(rng, -4, 4), nz(rng, -4, 4), rng.randint(-8, 8)],
                "distance": rng.randint(1, 9), "claimed_count": pick(rng, [1, 2, 2, 3, 4])})


v12435 = _st({"kind": "opposite_sides", "line": [1, 1, 1], "a": [1, 2], "b": [2, -1]})


def s12435(rng):
    while True:
        line = [nz(rng, -3, 3), nz(rng, -3, 3), rng.randint(-6, 6)]
        a = [rng.randint(-5, 5), rng.randint(-5, 5)]
        b = [rng.randint(-5, 5), rng.randint(-5, 5)]
        va = line[0] * a[0] + line[1] * a[1] + line[2]
        vb = line[0] * b[0] + line[1] * b[1] + line[2]
        if va and vb and a != b:
            return _st({"kind": "opposite_sides", "line": line, "a": a, "b": b})


# --- same side ---------------------------------------------------------------------------------------------------------------------------

def _same_side(line, points):
    a, b, c = line
    display = f"{expr(a, b)}={-c}"
    return {"line": line, "line_display": display, "reference": [0, 0], "reference_name": "原點", "points": points}


v12441 = _same_side([2, -3, 4], [[1, 2], [2, 3], [3, 4], [4, 3], [3, 2]])


def s12441(rng):
    while True:
        line = [nz(rng, -3, 3), nz(rng, -3, 3), nz(rng, -6, 6)]
        pts = [[rng.randint(-2, 5), rng.randint(-2, 5)] for _ in range(5)]
        sides = [(line[0] * x + line[1] * y + line[2]) for x, y in pts]
        ref = line[2]
        same = [v for v in sides if v and (v > 0) == (ref > 0)]
        other = [v for v in sides if v and (v > 0) != (ref > 0)]
        if len(same) >= 1 and len(other) >= 1 and len({tuple(p) for p in pts}) == 5:
            return _same_side(line, pts)


# --- remaining single-problem shapes -----------------------------------------------------------------------------------------------------

v12444 = {"ab": 2, "bf": 2}


def s12444(rng):
    return {"ab": rng.randint(1, 4), "bf": rng.randint(1, 4)}


v12445 = {"point": [4, 1], "area": 1}


def s12445(rng):
    while True:
        a, b = nz(rng, -6, 6), nz(rng, -6, 6)
        # integer point on x/a + y/b = 1
        x = nz(rng, -8, 8)
        y2 = Fraction(b) * (1 - Fraction(x, a))
        if y2.denominator == 1 and y2 != 0:
            return {"point": [x, int(y2)], "area": str(Fraction(abs(a * b), 2))}


v12448 = {"a_point": [4, 0], "b_point": [0, 3], "p_point": [35, 43], "spacing": 3}


def s12448(rng):
    while True:
        a, b = pick(rng, [(4, 3), (3, 4), (6, 8), (8, 6), (5, 12), (12, 5)])
        spacing = pick(rng, [2, 3, 4, 5])
        p = [rng.randint(10, 40), rng.randint(10, 45)]
        num = abs(b * p[0] + a * p[1] - a * b)
        hyp = (a * a + b * b) ** 0.5
        dist = Fraction(num) / int(hyp)
        if dist % spacing != 0 and dist > spacing:
            return {"a_point": [a, 0], "b_point": [0, b], "p_point": p, "spacing": spacing}


# --- 12428 / 12447: independent canvases and drawing + count -------------------------------------------------------

def _series(items, view=(-6, 6, -6, 6)):
    return {"items": [{"relations": [_rel(*coef, op)]} for coef, op in items], "view": list(view)}


v12428 = _series([((3, -2, 6), ">="), ((1, 2, 0), ">="), ((1, 0, -2), ">=")])


def s12428(rng):
    items = []
    while len(items) < 3:
        coef = (rng.randint(-3, 3), rng.randint(-3, 3), rng.randint(-6, 6))
        if coef[0] == 0 and coef[1] == 0:
            continue
        items.append((coef, pick(rng, [">=", ">=", "<=", ">", "<"])))
    return _series(items)


def _lattice(relations, view=(-3, 8, -3, 8)):
    return {"relations": relations, "view": list(view)}


v12447 = _lattice([_rel(2, 1, -6, "<="), _rel(1, 1, -2, ">="), _rel(1, 0, 0, ">="), _rel(0, 1, 0, ">=")])


def s12447(rng):
    a, b, k, m = rng.randint(1, 3), rng.randint(1, 3), rng.randint(4, 9), rng.randint(1, 3)
    return _lattice([_rel(a, b, -k, "<="), _rel(1, 1, -m, ">="), _rel(1, 0, 0, ">="), _rel(0, 1, 0, ">=")])


COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Callable[[random.Random], dict[str, Any]]]] = {
    12403: ("ls", "rank_line_slopes", v12403, s12403),
    12404: ("ls", "evaluate_slope_sign_statements", v12404, s12404),
    12436: ("ls", "rank_line_slopes", v12436, s12436),
    12405: ("eq", "solve_line_equations", v12405, s12405),
    12406: ("eq", "solve_line_equations", v12406, s12406),
    12407: ("eq", "slope_of_line_from_equation", v12407, s12407),
    12408: ("eq", "solve_line_equations", v12408, s12408),
    12409: ("eq", "solve_line_equations", v12409, s12409),
    12410: ("eq", "fill_line_property_table", v12410, s12410),
    12432: ("eq", "evaluate_line_statement_truth", v12432, s12432),
    12437: ("eq", "solve_line_equations", v12437, s12437),
    12445: ("eq", "solve_axis_triangle_area_line", v12445, s12445),
    12411: ("tr", "translate_line_equation", v12411, s12411),
    12412: ("tr", "translate_line_equation", v12412, s12412),
    12438: ("tr", "solve_translation_parameter", v12438, s12438),
    12413: ("pp", "solve_line_equations", v12413, s12413),
    12414: ("pp", "solve_line_constructions", v12414, s12414),
    12415: ("pp", "solve_line_constructions", v12415, s12415),
    12416: ("pp", "solve_line_parameters", v12416, s12416),
    12417: ("pp", "solve_line_constructions", v12417, s12417),
    12418: ("pp", "solve_line_constructions", v12418, s12418),
    12431: ("pp", "evaluate_line_statement_truth", v12431, s12431),
    12433: ("pp", "evaluate_line_statement_truth", v12433, s12433),
    12439: ("pp", "solve_line_parameters", v12439, s12439),
    12440: ("pp", "solve_line_constructions", v12440, s12440),
    12444: ("pp", "solve_rectangle_perpendicular_diagonals", v12444, s12444),
    12446: ("pp", "solve_line_constructions", v12446, s12446),
    12419: ("di", "compute_line_distances", v12419, s12419),
    12420: ("di", "compute_line_distances", v12420, s12420),
    12421: ("di", "solve_window_decorative_lines", v12421, s12421),
    12422: ("di", "solve_line_parameters", v12422, s12422),
    12423: ("di", "compute_line_distances", v12423, s12423),
    12424: ("di", "solve_window_decorative_lines", v12424, s12424),
    12434: ("di", "evaluate_line_statement_truth", v12434, s12434),
    12448: ("di", "solve_parallel_line_family", v12448, s12448),
    12425: ("ineq", "graph_inequality_system", v12425, s12425),
    12426: ("ineq", "graph_inequality_system", v12426, s12426),
    12427: ("ineq", "solve_triangle_region_system", v12427, s12427),
    12429: ("ineq", "graph_inequality_system", v12429, s12429),
    12430: ("ineq", "read_region_signs_from_figure", v12430, s12430),
    12435: ("ineq", "evaluate_line_statement_truth", v12435, s12435),
    12441: ("ineq", "select_points_same_side", v12441, s12441),
    12442: ("ineq", "graph_inequality_system", v12442, s12442),
    12443: ("ineq", "solve_region_coefficients_from_figure", v12443, s12443),
    12428: ("ineq", "graph_inequality_series", v12428, s12428),
    12447: ("ineq", "graph_inequality_with_lattice_count", v12447, s12447),
}
