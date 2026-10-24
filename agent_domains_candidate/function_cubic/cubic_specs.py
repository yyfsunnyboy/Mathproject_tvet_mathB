"""Per-component *inputs* for 普高數學1 Unit 10 (三次函數的圖形特徵).

Each entry gives the source-faithful givens (variant 0) and a sampler for further variants of the same shape.
Samplers only choose inputs; the domain computes every answer and rejects degenerate inputs (the sandbox skips a
candidate the domain refuses).  Figures are never stored: they are rebuilt from the givens of each variant.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

SKILLS = {"cubic": "gh_GraphsOfCubicFunctions"}

_NEEDS_CUBIC_GRADER = "三次函數描繪題：既有 drawing 契約沒有可用的三次函數 grader（需新增共用作圖類型，須另經核准）"
DEFERRED: dict[int, str] = {
    12603: _NEEDS_CUBIC_GRADER,
    12604: _NEEDS_CUBIC_GRADER,
    12605: _NEEDS_CUBIC_GRADER,
    12606: _NEEDS_CUBIC_GRADER + "（描繪 + 對稱中心）",
    12607: _NEEDS_CUBIC_GRADER + "（a, p, h, k + 描繪 + 對稱中心）",
    12613: _NEEDS_CUBIC_GRADER + "（a, p, h, k + 描繪 + 對稱中心）",
    12626: "選項為五張函數圖形（需多圖選項的圖形呈現），現有單一坐標平面圖形無法忠實呈現 (1)~(5) 選項圖",
}

OP = {name: name for name in ("cubic_center_form", "cubic_from_conditions", "cubic_statements", "cubic_curve_matching")}
SKILL_OPERATIONS = {"cubic": list(OP)}


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


def _c(skill: str, op: str, source: dict, sampler) -> tuple:
    return (skill, op, source, sampler)


def _cubic_coeffs(rng: random.Random, *, centered: bool = True) -> list:
    """Coefficients c3, c2, c1, c0 with a simple centre abscissa (an integer, or ±1/3 like the textbook's x^3+x^2-x+1)."""
    c3 = pick(rng, [1, 1, 2, -1, -2, 3])
    if rng.random() < 0.15:
        return [1, pick(rng, [1, -1, 2, -2]), rng.randint(-4, 4), rng.randint(-4, 4)]
    h = rng.randint(-3, 3)
    return [c3, j(-3 * c3 * h), rng.randint(-9, 9), rng.randint(-9, 9)]


# --- 對稱中心形式 -----------------------------------------------------------------------------------

def _to_form(*coeffs: list) -> dict[str, Any]:
    return {"items": [{"kind": "to_form", "coeffs": c} for c in coeffs]}


v12622 = _to_form([-1, -6, 2, -3], [1, 1, -1, 1])


def s12622(rng): return _to_form(_cubic_coeffs(rng), _cubic_coeffs(rng))


v12625 = {"items": [{"kind": "center", "coeffs": [1, 3, 5, 6]}]}


def s12625(rng): return {"items": [{"kind": "center", "coeffs": _cubic_coeffs(rng)}]}


v12624 = {"items": [{"kind": "from_center", "a": 3, "p": 8, "center": [-2, 5]}]}


def s12624(rng): return {"items": [{"kind": "from_center", "a": nz(rng, -4, 4), "p": nz(rng, -9, 9), "center": [rng.randint(-5, 5), rng.randint(-6, 6)]}]}


def _form(a: Any, p: Any, h: Any, k: Any) -> dict[str, Any]:
    return {"a": a, "p": p, "h": h, "k": k}


v12623 = {"items": [{"kind": "shift", "form": _form(1, -2, -1, 5), "dx": 3, "dy": -4, "power": 1}]}


def s12623(rng):
    return {"items": [{"kind": "shift", "form": _form(pick(rng, [1, 2, -1, -2, 3]), nz(rng, -6, 6), rng.randint(-4, 4), rng.randint(-6, 6)),
                       "dx": nz(rng, -5, 5), "dy": nz(rng, -6, 6), "power": 1}]}


v12612 = {"items": [{"kind": "translation_overlap", "f": _form(1, -4, 0, 0), "g": _form(1, -4, -2, -3)}]}


def s12612(rng):
    a, p = pick(rng, [1, 2, -1, -2]), nz(rng, -6, 6)
    h, k = nz(rng, -4, 4), nz(rng, -5, 5)
    p2 = p if rng.random() < 0.75 else p + nz(rng, -3, 3)
    return {"items": [{"kind": "translation_overlap", "f": _form(a, p, 0, 0), "g": _form(a, p2, h, k)}]}


# --- 由條件求三次函數 -------------------------------------------------------------------------------

v12614 = {"items": [{"kind": "symmetric_pair_origin", "A": [1, 25], "B": [7, 7], "C_x": 9}]}


def s12614(rng):
    h = rng.randint(2, 5)
    d = rng.randint(1, h - 1) if h > 1 else 1
    a, p = pick(rng, [1, -1, 2]), nz(rng, -15, 15)
    k = a * h ** 3 + p * h  # the graph passes through the origin
    f = lambda x: a * (x - h) ** 3 + p * (x - h) + k  # noqa: E731
    return {"items": [{"kind": "symmetric_pair_origin", "A": [h - d, f(h - d)], "B": [h + d, f(h + d)], "C_x": rng.randint(h + 2, 2 * h + 3)}]}


v12608 = {"items": [{"kind": "center_zero_linear", "center": [2, 1]}]}


def s12608(rng): return {"items": [{"kind": "center_zero_linear", "center": [pick(rng, [2, 3, 4, 5, -2, -3]), nz(rng, -4, 4)]}]}


v12616 = {"items": [{"kind": "global_local", "lead": -2, "slope": 5, "intercept": 3, "h": -1}]}


def s12616(rng): return {"items": [{"kind": "global_local", "lead": nz(rng, -4, 4), "slope": nz(rng, -8, 8), "intercept": rng.randint(-6, 6), "h": nz(rng, -3, 3)}]}


# --- 敘述判斷 ---------------------------------------------------------------------------------------

def _truth(subject: dict, statement: dict) -> dict[str, Any]:
    return {"subject": subject, "statements": [statement], "mode": "truth"}


def _sel(subject: dict, statements: list) -> dict[str, Any]:
    return {"subject": subject, "statements": statements, "mode": "select"}


def _form_subject(a: Any, p: Any, h: Any, k: Any) -> dict[str, Any]:
    return {"type": "form", **_form(a, p, h, k)}


_SUBJ_SRC = _form_subject(2, 3, 4, 5)


def _rand_form_subject(rng: random.Random) -> tuple[dict, Fraction, Fraction, Fraction, Fraction]:
    a, p = pick(rng, [1, 2, 3, -1, -2, -3]), nz(rng, -6, 6)
    h, k = rng.randint(-5, 5), rng.randint(-6, 6)
    return _form_subject(a, p, h, k), Fraction(a), Fraction(p), Fraction(h), Fraction(k)


v12617 = _truth(_SUBJ_SRC, {"kind": "odd_function"})


def s12617(rng):
    if rng.random() < 0.3:  # centre at the origin: a genuinely odd function
        return _truth(_form_subject(pick(rng, [1, 2, -1, -2, 3]), nz(rng, -6, 6), 0, 0), {"kind": "odd_function"})
    return _truth(_rand_form_subject(rng)[0], {"kind": "odd_function"})


v12618 = _truth(_SUBJ_SRC, {"kind": "center_is", "x": 4, "y": 5})


def s12618(rng):
    subject, _a, _p, h, k = _rand_form_subject(rng)
    if rng.random() < 0.4:
        return _truth(subject, {"kind": "center_is", "x": j(h), "y": j(k)})
    return _truth(subject, {"kind": "center_is", "x": j(h + rng.randint(-2, 2)), "y": j(k + rng.randint(-2, 2))})


v12619 = _truth(_SUBJ_SRC, {"kind": "global_extremum", "claim": "max", "value": 5})


def s12619(rng):
    subject, _a, _p, _h, k = _rand_form_subject(rng)
    claim = pick(rng, ["max", "min", "max", "none"])
    return _truth(subject, {"kind": "global_extremum", "claim": claim, **({"value": j(k)} if claim != "none" else {})})


v12620 = _truth(_SUBJ_SRC, {"kind": "local_line", "x0": 4, "m": 3, "n": -7})


def s12620(rng):
    subject, _a, p, h, k = _rand_form_subject(rng)
    m, n = p, k - p * h
    if rng.random() > 0.4:
        m, n = (m + nz(rng, -2, 2), n) if rng.random() < 0.5 else (m, n + nz(rng, -3, 3))
    return _truth(subject, {"kind": "local_line", "x0": j(h), "m": j(m), "n": j(n)})


v12615 = _sel({"type": "free_cd", "coeffs": [3, -5]}, [
    {"kind": "value_attained", "value": 1000, "claim": "exists"}, {"kind": "x_axis_meets", "claim": "at_least_one"},
    {"kind": "axis_of_symmetry", "claimed_x": "5/6"}, {"kind": "center_on_curve_at", "x": "5/9"},
    {"kind": "symmetric_mean", "xm": "5/9", "x1": "2/9", "x2": "8/9"}])


def s12615(rng):
    c3 = pick(rng, [3, 6, 2, -3, -2, 1])
    c2 = nz(rng, -9, 9)
    h = Fraction(-c2, 3 * c3)
    d = Fraction(rng.randint(1, 5), pick(rng, [3, 9, 2]))
    xm = h if rng.random() < 0.5 else h + Fraction(nz(rng, -2, 2), 3)
    return _sel({"type": "free_cd", "coeffs": [c3, c2]}, [
        {"kind": "value_attained", "value": nz(rng, -2000, 2000), "claim": pick(rng, ["exists", "exists", "none"])},
        {"kind": "x_axis_meets", "claim": "at_least_one"},
        {"kind": "axis_of_symmetry", "claimed_x": j(h + Fraction(rng.randint(-1, 1), 6))},
        {"kind": "center_on_curve_at", "x": j(h if rng.random() < 0.5 else h + Fraction(nz(rng, -2, 2), 9))},
        {"kind": "symmetric_mean", "xm": j(xm), "x1": j(xm - d), "x2": j(xm + d)}])


def _sub_center(c3: int, h: int, c1: int, k: int) -> dict[str, Any]:
    return {"type": "cubic_with_center", "coeffs": [c3, -3 * c3 * h, c1], "center": [h, k]}


v12627 = _sel({"type": "cubic_with_center", "coeffs": [2, -6, 9], "center": [1, 3]}, [
    {"kind": "constant_claim", "claimed": 2}, {"kind": "point_shift_on_graph", "dx": 2, "dy": 6},
    {"kind": "local_line", "x0": 1, "m": 2, "n": 3, "style": "slope_intercept"}, {"kind": "value_approx", "x": "0.99", "approx": "2.97", "decimals": 2},
    {"kind": "translate_overlap", "a": 2, "p": 3, "k": 4}])


def s12627(rng):
    c3 = pick(rng, [1, 2, 3, -1, -2])
    h, c1, k = rng.randint(-3, 3), rng.randint(-9, 9), rng.randint(-6, 6)
    subject = _sub_center(c3, h, c1, k)
    value = k - (-2 * c3 * h ** 3 + c1 * h)  # the constant term c0 (the textbook's unknown k)
    p = c1 - 3 * c3 * h * h  # p of the centre form
    a = c3
    delta = Fraction(pick(rng, [1, -1]), 100)
    x = Fraction(h) + delta
    exact = a * delta ** 3 + p * delta + k
    places = 2
    scale = 10 ** places
    rounded = Fraction(int((exact * scale + Fraction(1, 2)) // 1), scale)
    approx = rounded if rng.random() < 0.55 else rounded + Fraction(nz(rng, -2, 2), scale)
    return _sel(subject, [
        {"kind": "constant_claim", "claimed": j(Fraction(value) if rng.random() < 0.4 else Fraction(value) + nz(rng, -3, 3))},
        {"kind": "point_shift_on_graph", "dx": nz(rng, -3, 3), "dy": nz(rng, -8, 8)},
        {"kind": "local_line", "x0": h, "m": j(p if rng.random() < 0.4 else p + nz(rng, -2, 2)), "n": j(k - p * h), "style": "slope_intercept"},
        {"kind": "value_approx", "x": _dec(x), "approx": _dec(approx), "decimals": places},
        {"kind": "translate_overlap", "a": a, "p": j(p if rng.random() < 0.5 else p + nz(rng, -3, 3)), "k": rng.randint(-5, 5)}])


def _dec(q: Fraction) -> Any:
    text = f"{float(q):.6f}".rstrip("0").rstrip(".")
    return int(text) if "." not in text else text


# --- 圖形配對 / 比較 ---------------------------------------------------------------------------------

_GAMMA_COLORS3 = ["紅色", "藍色", "綠色"]


def _perm(rng: random.Random, n: int) -> list[int]:
    order = list(range(n))
    rng.shuffle(order)
    return order


def _match(functions: list, order: list, window: dict, colors: list, **extra: Any) -> dict[str, Any]:
    return {"kind": "match", "functions": functions, "order": order, "window": window, "colors": colors, **extra}


_REF = [{"coeffs": [1, 0, 0, 0], "label": "y=x³"}]
# order[g] = index of the function drawn as Γ_(g+1).  Textbook figure: Γ1 (red) = 2x^3, Γ2 (blue) = -2x^3, Γ3 (green) = -x^3.
v12609 = _match([{"coeffs": [-1, 0, 0, 0]}, {"coeffs": [2, 0, 0, 0]}, {"coeffs": [-2, 0, 0, 0]}], [1, 2, 0], {"x": 3, "y": 6}, _GAMMA_COLORS3, reference=_REF)


def s12609(rng):
    values = rng.sample([-3, -2, -1, 2, 3, "1/2", "-1/2"], 3)
    return _match([{"coeffs": [v, 0, 0, 0]} for v in values], _perm(rng, 3), {"x": 3, "y": 6}, _GAMMA_COLORS3, reference=_REF)


v12610 = _match([{"coeffs": [2, 0, 1, 0]}, {"coeffs": ["-1/2", 0, -1, 0]}], [1, 0], {"x": 3, "y": 6}, ["紅色", "黑色"])


def s12610(rng):
    a1, p1 = pick(rng, [1, 2, 3]), pick(rng, [1, 2, 3])
    a2, p2 = pick(rng, ["1/2", 1, 2]), pick(rng, [1, 2, 3])
    s = pick(rng, [1, -1])  # both functions have a and p of the same sign; the two functions open opposite ways
    f1 = [j(s * Fraction(a1)), 0, j(s * p1), 0]
    f2 = [j(-s * Fraction(a2)), 0, j(-s * p2), 0]
    return _match([{"coeffs": f1}, {"coeffs": f2}], _perm(rng, 2), {"x": 3, "y": 6}, ["紅色", "黑色"])


v12611 = _match([{"coeffs": [1, 0, -4, 0]}, {"coeffs": ["-1/2", 0, 2, 0]}], [1, 0], {"x": 3, "y": 6}, ["紅色", "黑色"])


def s12611(rng):
    a1, p1 = pick(rng, [1, 2]), pick(rng, [2, 3, 4, 5])
    a2, p2 = pick(rng, ["1/2", 1, 2]), pick(rng, [1, 2, 3])
    s = pick(rng, [1, -1])  # both functions have a and p of opposite signs
    f1 = [j(s * a1), 0, j(-s * p1), 0]
    f2 = [j(-s * Fraction(a2)), 0, j(s * p2), 0]
    return _match([{"coeffs": f1}, {"coeffs": f2}], _perm(rng, 2), {"x": 3, "y": 6}, ["紅色", "黑色"])


def _shifted(m: int, dx: int, dy: int) -> list:
    # base f(x) = x^3 - m x ; f(x-dx) expanded
    def expand(shift_x: int, shift_y: int) -> list:
        return [1, -3 * shift_x, 3 * shift_x * shift_x - m, -(shift_x ** 3) + m * shift_x + shift_y]
    return [
        {"coeffs": expand(0, 0), "tex": "y=f\\left(x\\right)"},
        {"coeffs": expand(0, dy), "tex": "y=f\\left(x\\right)" + ("+" if dy > 0 else "-") + str(abs(dy))},
        {"coeffs": expand(dx, 0), "tex": "y=f\\left(x" + ("-" if dx > 0 else "+") + str(abs(dx)) + "\\right)"},
        {"coeffs": expand(dx, -dy), "tex": "y=f\\left(x" + ("-" if dx > 0 else "+") + str(abs(dx)) + "\\right)" + ("-" if dy > 0 else "+") + str(abs(dy))},
    ]


_COLORS4 = ["藍色", "黑色", "紅色", "綠色"]
v12628 = _match(_shifted(1, 1, 3), [1, 0, 2, 3], {"x": 3, "y": 6}, _COLORS4, preface="已知 $f\\left(x\\right)=x^{3}-x$，")


def s12628(rng):
    m, dx, dy = pick(rng, [1, 1, 2, 3]), nz(rng, -2, 2), pick(rng, [2, 3, 4, -2, -3])
    return _match(_shifted(m, dx, dy), _perm(rng, 4), {"x": 3, "y": 7}, _COLORS4, preface=f"已知 $f\\left(x\\right)=x^{{3}}{'-' if m > 0 else '+'}{'' if abs(m) == 1 else abs(m)}x$，")


def _compare(values: list, order: list, window: dict) -> dict[str, Any]:
    return {"kind": "compare", "functions": [{"coeffs": [v, 0, 0, 0]} for v in values], "order": order, "window": window, "colors": ["藍色", "紅色", "黑色"]}


v12621 = _compare([-3, -1, 2], [0, 1, 2], {"x": 3, "y": 6})


def s12621(rng):
    values = rng.sample([-3, -2, -1, "-1/2", "1/2", 1, 2, 3], 3)
    return _compare(values, [0, 1, 2], {"x": 3, "y": 6})


COMPONENTS: dict[int, tuple] = {
    12608: _c("cubic", "cubic_from_conditions", v12608, s12608),
    12609: _c("cubic", "cubic_curve_matching", v12609, s12609),
    12610: _c("cubic", "cubic_curve_matching", v12610, s12610),
    12611: _c("cubic", "cubic_curve_matching", v12611, s12611),
    12612: _c("cubic", "cubic_center_form", v12612, s12612),
    12614: _c("cubic", "cubic_from_conditions", v12614, s12614),
    12615: _c("cubic", "cubic_statements", v12615, s12615),
    12616: _c("cubic", "cubic_from_conditions", v12616, s12616),
    12617: _c("cubic", "cubic_statements", v12617, s12617),
    12618: _c("cubic", "cubic_statements", v12618, s12618),
    12619: _c("cubic", "cubic_statements", v12619, s12619),
    12620: _c("cubic", "cubic_statements", v12620, s12620),
    12621: _c("cubic", "cubic_curve_matching", v12621, s12621),
    12622: _c("cubic", "cubic_center_form", v12622, s12622),
    12623: _c("cubic", "cubic_center_form", v12623, s12623),
    12624: _c("cubic", "cubic_center_form", v12624, s12624),
    12625: _c("cubic", "cubic_center_form", v12625, s12625),
    12627: _c("cubic", "cubic_statements", v12627, s12627),
    12628: _c("cubic", "cubic_curve_matching", v12628, s12628),
}


# --- revision 2: cubic drawing items and the five-option graph choice (shared cubic_graph drawing grader) --------------

OP.update({name: name for name in ("graph_cubic_functions", "cubic_option_graph")})
SKILL_OPERATIONS["cubic"] = list(OP)


def _graph(item: dict, ask: list) -> dict[str, Any]:
    return {"items": [item], "ask": ask}


def _expand_form(a: Any, p: Any, h: Any, k: Any) -> list:
    a, p, h, k = (Fraction(v) for v in (a, p, h, k))
    return [j(a), j(-3 * a * h), j(3 * a * h * h + p), j(-a * h ** 3 - p * h + k)]


v12603 = _graph({"coeffs": [1, 0, 0, 0]}, [])


def s12603(rng):
    return _graph({"form": {"a": pick(rng, [1, 1, 2, -1, -2, "1/2"]), "p": 0, "h": rng.randint(-2, 2), "k": rng.randint(-3, 3)}}, [])


v12604 = _graph({"coeffs": [1, 0, 2, 0]}, [])


def s12604(rng):
    a = pick(rng, [1, 2, -1, -2, "1/2"])
    sign = 1 if Fraction(a) > 0 else -1
    return _graph({"form": {"a": a, "p": sign * pick(rng, [1, 2, 3]), "h": rng.randint(-2, 2), "k": rng.randint(-2, 2)}}, [])


v12605 = _graph({"coeffs": [1, 0, -1, 0]}, [])


def s12605(rng):
    a = pick(rng, [1, 2, -1, -2])
    sign = -1 if a > 0 else 1
    return _graph({"form": {"a": a, "p": sign * pick(rng, [1, 2, 3]), "h": rng.randint(-2, 2), "k": rng.randint(-2, 2)}}, [])


v12606 = _graph({"form": {"a": 1, "p": 2, "h": 3, "k": 1}}, ["center"])


def s12606(rng):
    return _graph({"form": {"a": pick(rng, [1, -1, 2]), "p": nz(rng, -3, 3), "h": nz(rng, -3, 3), "k": rng.randint(-3, 3)}}, ["center"])


v12607 = _graph({"coeffs": [1, -6, 11, -3]}, ["form", "center"])


def _coeff_sampler(rng, signs=(1, -1)):
    a = pick(rng, [s * m for s in signs for m in (1, 1, 2)])
    return _graph({"coeffs": _expand_form(a, rng.randint(-3, 3), nz(rng, -3, 3), rng.randint(-4, 4))}, ["form", "center"])


def s12607(rng): return _coeff_sampler(rng)


v12613 = _graph({"coeffs": [-1, 3, -2, -2]}, ["form", "center"])


def s12613(rng): return _coeff_sampler(rng, signs=(-1, 1))


_OPTION_SHAPES = ["S_up", "S_down", "M_up", "M_down"]


def _options(slope: Any, intercept: Any, options: list) -> dict[str, Any]:
    return {"slope": slope, "intercept": intercept, "options": options}


v12626 = _options(-1, 2, ["parabola_up", "S_up", "S_down", "M_up", "M_down"])


def s12626(rng):
    options = _OPTION_SHAPES + [pick(rng, ["parabola_up", "parabola_down"])]
    rng.shuffle(options)
    return _options(pick(rng, [1, 2, -1, -2, "1/2", "-1/2"]), pick(rng, [1, 2, 3, -1, -2, -3]), options)


REV2_COMPONENTS: dict[int, tuple] = {
    12603: _c("cubic", "graph_cubic_functions", v12603, s12603),
    12604: _c("cubic", "graph_cubic_functions", v12604, s12604),
    12605: _c("cubic", "graph_cubic_functions", v12605, s12605),
    12606: _c("cubic", "graph_cubic_functions", v12606, s12606),
    12607: _c("cubic", "graph_cubic_functions", v12607, s12607),
    12613: _c("cubic", "graph_cubic_functions", v12613, s12613),
    12626: _c("cubic", "cubic_option_graph", v12626, s12626),
}
