"""Per-component inputs for 普高數學2 Unit 9 二維數據分析.

Samplers only choose the numbers a stem prints. The domain computes (and cross-checks) every answer and refuses
a sample that does not validate, so a sampler may be generous: ``build_sandbox.collect_variants`` skips refusals.
Seed 0 of every component reproduces the textbook data of its source row.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any

SKILLS = {
    "scatter": "gh_ScatterPlot",
    "correlation": "gh_CorrelationCoefficient",
    "regression": "gh_LeastSquaresMethodAndRegressionLine",
}

OP = {name: name for name in (
    "correlation_from_table", "correlation_remove_point", "correlation_change_add_point", "correlation_rescale",
    "regression_from_summary", "regression_from_table", "regression_rounded_from_table", "regression_predict_given_line",
    "correlation_from_regression_point", "regression_line_unknown_intercept", "regression_statement_selection",
    "true_false_bivariate",
)}

# gh_ScatterPlot has no operation bound: its two rows (12947 draw-only, 12948 read-a-figure) are both deferred.
SKILL_OPERATIONS = {
    "correlation": ["correlation_from_table", "correlation_remove_point", "correlation_change_add_point",
                    "correlation_rescale", "true_false_bivariate"],
    # regression_predict_given_line kept in domain/OP for retained 12963 evidence, but not bound for Publish.
    "regression": ["regression_from_summary", "regression_from_table", "regression_rounded_from_table",
                   "correlation_from_regression_point",
                   "regression_line_unknown_intercept", "regression_statement_selection", "true_false_bivariate"],
}
UNBOUND_SKILLS = {"scatter": "all components deferred (VISUAL_CAPABILITY_GAP)"}

FIXED_ROWS: dict[int, str] = {}

# Figure / incomplete-topology rows: keep formal textbook; serve via fixed ungraded original practice.
# 12963 keeps its domain operation and dry-run component as retained evidence, but is excluded from
# COMPONENTS / Publish because the generator only covered prediction, not the scatter-choice part.
DEFERRED_COMPONENTS: dict[int, str] = {
    12947: "draw-only scatter plot (student drawing grader / scatter renderer not part of this unit)",
    12948: "read an existing scatter figure (positive / negative / zero correlation); needs a generated figure",
    12954: "rank the correlation coefficients of four scatter figures; needs generated figures",
    12960: "choose the likely r of figure C from the figures of A and B; needs generated figures",
    12963: "例題6 topology is (1) choose scatter from data + (2) predict from given line; V3 only covered (2)",
}
VISUAL_CAPABILITY_GAP: frozenset[int] = frozenset(DEFERRED_COMPONENTS)
# Retained sandbox evidence for deferred 12963 (not in COMPONENTS → not published).
RETAINED_DEFERRED_COMPONENTS: frozenset[int] = frozenset({12963})
# Concept claims whose pool of distinct statements is intrinsically small (not counted as variable coverage).
FIXED_CONCEPT: frozenset[int] = frozenset({12949, 12955, 12957})

FAMILY = {
    12949: "claim_points_vs_correlation",
    12950: "correlation_from_table", 12951: "correlation_from_table", 12952: "correlation_from_table",
    12953: "correlation_from_table", 12968: "correlation_from_table",
    12959: "correlation_remove_point",
    12967: "correlation_change_add_point",
    12972: "correlation_rescale",
    12957: "claim_r_range", 12958: "claim_points_on_line",
    12955: "claim_slope_sign", 12956: "claim_slope_sigma",
    12961: "regression_from_summary",
    12962: "regression_from_table", 12966: "regression_from_table", 12969: "regression_from_table",
    12964: "regression_rounded_from_table",
    12965: "correlation_from_regression_point",
    12970: "regression_line_unknown_intercept",
    12971: "regression_statement_selection",
}


def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def _g(**kw: Any) -> dict[str, Any]:
    return kw


def _dec(value: Fraction | int | float, places: int = 1) -> str:
    return f"{float(value):.{places}f}"


def _decimal_text(f: Fraction) -> str:
    text = f"{float(f):.2f}".rstrip("0")
    return text[:-1] if text.endswith(".") else text


# --- correlation tables ---------------------------------------------------------------------------------------------


def _scaled_sums(xs: list[int], ys: list[int]) -> tuple[int, int, int]:
    n = len(xs)
    return (n * sum(x * x for x in xs) - sum(xs) ** 2, n * sum(y * y for y in ys) - sum(ys) ** 2,
            n * sum(x * y for x, y in zip(xs, ys)) - sum(xs) * sum(ys))


def _rational_r_table(rng: random.Random, n: int, xr: tuple[int, int], yr: tuple[int, int], *, sort_x: bool, tries: int = 20000) -> dict[str, Any]:
    """Integer data whose r is rational (Sxx·Syy a perfect square) and not 0, ±1."""
    for _ in range(tries):
        xs = rng.sample(range(*xr), n)
        if sort_x:
            xs.sort()
        ys = [rng.randint(*yr) for _ in range(n)]
        nxx, nyy, nxy = _scaled_sums(xs, ys)
        if nxx == 0 or nyy == 0 or nxy == 0 or nxy * nxy == nxx * nyy:
            continue
        if math.isqrt(nxx * nyy) ** 2 != nxx * nyy or abs(nxy) < 0.2 * math.isqrt(nxx * nyy):
            continue
        return {"x": xs, "y": ys}
    raise ValueError("no_rational_r_table")


def _perfect_line_table(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [5, 5, 6])
    x0, step = rng.randint(1, 4), pick(rng, [1, 2, 3])
    xs = [x0 + step * i for i in range(n)]
    sign, ystep = pick(rng, [1, -1]), pick(rng, [1, 1, 2])
    y0 = rng.randint(1, 5) if sign > 0 else rng.randint(2 * n, 2 * n + 6)
    return {"x": xs, "y": [y0 + sign * ystep * i for i in range(n)]}


def _corr_plain(rng: random.Random) -> dict[str, Any]:
    if rng.random() < 0.25:
        return _g(**_perfect_line_table(rng), scene="plain")
    return _g(**_rational_r_table(rng, pick(rng, [5, 5, 6]), (1, 16), (1, 16), sort_x=True), scene="plain")


def _corr_aptitude(rng: random.Random) -> dict[str, Any]:
    return _g(**_rational_r_table(rng, pick(rng, [6, 7, 8]), (2, 15), (1, 11), sort_x=False), scene="aptitude")


def _remove_point(rng: random.Random) -> dict[str, Any]:
    labels = list("ABCDE")
    xs = [rng.randint(1, 12) for _ in range(5)]
    ys = [rng.randint(1, 12) for _ in range(5)]
    return _g(labels=labels, x=xs, y=ys)


def _forearm_x(rng: random.Random) -> str:
    return _dec(24 + rng.randint(0, 8) / 2, 1).rstrip("0").rstrip(".")


def _forearm_table(rng: random.Random, n: int) -> tuple[list[str], list[int]]:
    xs = sorted((_forearm_x(rng) for _ in range(n)), key=float)
    ys = [round(3.8 * float(x) + 66 + rng.randint(-5, 5)) for x in xs]
    return xs, ys


def _change(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [8, 9, 10, 10])
    xs, ys = _forearm_table(rng, n)
    x_new = _forearm_x(rng)
    y_new = round(3.8 * float(x_new) + 66) + pick(rng, [-1, 1]) * rng.randint(0, 12)
    return _g(x=xs, y=ys, new_point=[x_new, y_new])


def _rescale(rng: random.Random) -> dict[str, Any]:
    old, new = pick(rng, [(5, 6), (4, 5), (2, 3), (5, 7), (5, 8), (10, 12)])
    n = pick(rng, [10, 10, 20, 20, 25])
    total = n * old
    top = old * rng.randint(max(1, total // old // 2), total // old - 1)
    r = Fraction(rng.choice([v for v in range(-95, 96) if v and v % 1 == 0]), 100)
    return _g(n_questions=n, old_per=old, new_per=new, top=top, r=_decimal_text(r))


# --- regression -----------------------------------------------------------------------------------------------------


def _reg_summary(rng: random.Random) -> dict[str, Any]:
    r = Fraction(pick(rng, [v for v in range(-9, 10) if v]), 10)
    return _g(mx=rng.randint(1, 12), my=rng.randint(2, 20), sx=pick(rng, [2, 3, 4, 5, 6, 8]), sy=pick(rng, [2, 3, 4, 5, 6, 8, 10]),
              r=_decimal_text(r))


def _nice_line(xs: list[int], ys: list[int]) -> bool:
    n = len(xs)
    nxx, _nyy, nxy = _scaled_sums(xs, ys)
    if nxx == 0 or nxy == 0:
        return False
    m = Fraction(nxy, nxx)
    b = Fraction(sum(ys), n) - m * Fraction(sum(xs), n)
    return m.denominator <= 10 and b.denominator <= 10


def _temp_sales(rng: random.Random) -> dict[str, Any]:
    for _ in range(4000):
        n = pick(rng, [4, 5, 6])
        top, step = rng.randint(30, 36), pick(rng, [1, 2, 2, 3])
        xs = [top - step * i for i in range(n)]
        ys = [rng.randint(6, 20) for _ in range(n)]
        if _nice_line(xs, ys):
            return _g(x=xs, y=ys, x0=rng.randint(min(xs) + 1, max(xs) - 1), scene="temp_sales")
    raise ValueError("no_temp_sales_sample")


def _eq_achievement(rng: random.Random) -> dict[str, Any]:
    for _ in range(4000):
        n = pick(rng, [5, 6, 6, 7])
        xs = sorted(rng.randint(3, 13) for _ in range(n))
        ys = sorted(rng.randint(3, 16) + 0 for _ in range(n))
        ys = [max(2, y + rng.randint(-2, 2)) for y in ys]
        if len(set(xs)) >= 3 and _nice_line(xs, ys):
            return _g(x=xs, y=ys, x0=rng.randint(min(xs) + 1, max(xs) - 1), scene="eq_achievement")
    raise ValueError("no_eq_sample")


def _price_demand(rng: random.Random) -> dict[str, Any]:
    for _ in range(4000):
        n = pick(rng, [5, 5, 6])
        start = rng.randint(10, 30)
        xs = [start + i for i in range(n)]
        ys = [rng.randint(3, 12) for _ in range(n)]
        if _nice_line(xs, ys):
            return _g(x=xs, y=ys, x0=f"{start + rng.randint(0, n - 2)}.5", scene="price_demand")
    raise ValueError("no_price_sample")


def _predict_line(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [8, 9, 10, 10])
    xs, ys = _forearm_table(rng, n)
    fx, fy = [Fraction(x) for x in xs], [Fraction(y) for y in ys]
    mx, my = sum(fx) / n, sum(fy) / n
    m = sum((a - mx) * (b - my) for a, b in zip(fx, fy)) / sum((a - mx) ** 2 for a in fx)
    b = my - m * mx

    def r1(v: Fraction) -> Fraction:
        return Fraction(math.floor(v * 10 + Fraction(1, 2)), 10)

    return _g(x=xs, y=ys, eq_places=1, m_r=_dec(r1(m)), b_r=_dec(r1(b)),
              x0=_dec(24.5 + rng.randint(0, 6) / 2 + rng.randint(1, 4) / 10, 1), places=0)


def _rounded_months(rng: random.Random) -> dict[str, Any]:
    base = [rng.uniform(-1.0, 1.5), rng.uniform(0.0, 2.5)]
    xs = []
    for month in range(12):
        seasonal = 5.0 - 5.5 * math.cos((month - 1.5) / 12 * 2 * math.pi)
        xs.append(max(0.0, round(seasonal + base[0] + rng.uniform(-1.4, 1.4), 1)))
    slope, shift = rng.uniform(0.35, 0.9), rng.uniform(0.5, 3.0)
    ys = [max(0.0, round(slope * x + shift + rng.uniform(-2.4, 2.4), 1)) for x in xs]
    return _g(x=[_dec(v) for v in xs], y=[_dec(v) for v in ys], r_places=1, coef_places=4)


def _from_point(rng: random.Random) -> dict[str, Any]:
    for _ in range(500):
        mx, my = rng.randint(1, 10), rng.randint(1, 15)
        sx, sy = pick(rng, [2, 3, 4, 5, 6, 8]), pick(rng, [3, 4, 5, 6, 8, 9, 10])
        dx, dy = pick(rng, [-3, -2, -1, 1, 2, 3, 4]), pick(rng, [v for v in range(-7, 8) if v])
        r = Fraction(dy, dx) * sx / sy
        if 0 < abs(r) < 1:
            return _g(mx=mx, my=my, sx=sx, sy=sy, point=[mx + dx, my + dy])
    raise ValueError("no_point_sample")


def _unknown_k(rng: random.Random) -> dict[str, Any]:
    for _ in range(500):
        a = Fraction(pick(rng, [1, 2, 3, -1, -2, -3, 1, 2]), pick(rng, [1, 1, 1, 2]))
        mx, my = rng.randint(1, 8), rng.randint(2, 15)
        sx, sy = pick(rng, [2, 3, 4, 5]), pick(rng, [4, 5, 6, 8, 9, 10])
        r = a * sx / sy
        if 0 < abs(r) < 1:
            return _g(mx=mx, my=my, sx=sx, sy=sy, slope=_decimal_text(a) if a.denominator in (1, 2) else str(a))
    raise ValueError("no_k_sample")


def _line_statements(rng: random.Random) -> dict[str, Any]:
    for _ in range(2000):
        mx, my = rng.randint(2, 9), rng.randint(2, 9)
        dx, dy = pick(rng, [-3, -2, 2, 3, 4]), pick(rng, [-3, -2, -1, 1, 2, 3])
        m = Fraction(dy, dx)
        r = Fraction(pick(rng, [v for v in range(1, 10)]), 10) * (1 if m > 0 else -1)
        if abs(r) >= 1:
            continue
        ratio = r / m
        if ratio <= 0 or ratio == 1:
            continue
        step = pick(rng, [d for d in (-4, -3, -2, 2, 3, 4) if (m * d).denominator == 1])
        qx = mx + step
        qy = my + m * step

        def shaken(v: Fraction, truth: bool) -> Fraction:
            return v if truth else v + pick(rng, [-1, 1])

        t1, t2, t3 = rng.random() < 0.6, rng.random() < 0.6, rng.random() < 0.6
        first, second = pick(rng, [("x", "y"), ("y", "x")])
        stated_slope = shaken(m, t2)
        statements = [
            {"kind": "passes_point", "x": mx, "y": int(shaken(Fraction(my), t1))},
            {"kind": "slope_is", "stated": _decimal_text(stated_slope) if stated_slope.denominator in (1, 2, 4, 5) else str(stated_slope)},
            {"kind": "passes_point", "x": int(qx), "y": int(shaken(qy, t3))},
            {"kind": "sigma_less", "first": first, "second": second},
        ]
        return _g(n=pick(rng, [12, 15, 20, 24, 30, 40]), mx=mx, my=my, r=_decimal_text(r), line_point=[mx + dx, my + dy], statements=statements)
    raise ValueError("no_statement_sample")


# --- true / false concepts ------------------------------------------------------------------------------------------


def _tf_points(rng: random.Random) -> dict[str, Any]:
    return _g(claim={"kind": "points_vs_correlation", "stated": pick(rng, ["higher", "higher", "lower", "unrelated"])})


def _tf_slope_sign(rng: random.Random) -> dict[str, Any]:
    return _g(claim={"kind": "slope_sign", "r_rel": pick(rng, [">", "<", "="]), "m_rel": pick(rng, [">", "<", "="])})


def _tf_slope_sigma(rng: random.Random) -> dict[str, Any]:
    pool = ["1", "2", "3", "1/2", "3/2", "4"]
    k = pick(rng, ["1", "1", "2", "3", "1/2", "3/2"])
    c = k if rng.random() < 0.5 else pick(rng, [v for v in pool if v != k])
    return _g(claim={"kind": "slope_sigma", "k": k, "c": c})


def _tf_range(rng: random.Random) -> dict[str, Any]:
    lo, hi = pick(rng, [(-1, 1), (-1, 1), (-1, 1), (0, 1), (-1, 0), (-1, 1)])
    return _g(claim={"kind": "r_range", "lo": lo, "hi": hi, "lo_closed": rng.random() < 0.75, "hi_closed": rng.random() < 0.75})


def _tf_on_line(rng: random.Random) -> dict[str, Any]:
    a = pick(rng, ["2", "3", "1", "-1", "-2", "-3", "1/2", "-1/2", "3/2", "-3/2", "4", "-4"])
    sign = 1 if Fraction(a) > 0 else -1
    stated = sign if rng.random() < 0.55 else -sign
    return _g(claim={"kind": "points_on_line", "a": a, "b": rng.randint(-6, 6), "stated": stated})


# --- components: id -> (skill, operation, textbook givens (seed 0), sampler) ---------------------------------------------

_FOREARM_X = ["24.5", "25", "25", "25.5", "26", "26", "26.5", "27", "27.5", "28"]
_FOREARM_Y = [160, 158, 163, 163, 161, 163, 168, 170, 168, 173]
_UTEMP_X = ["0.4", "1.0", "4.6", "5.4", "6.6", "7.4", "10.1", "9.4", "8.7", "8.5", "6.6", "2.2"]
_UTEMP_Y = ["3.0", "3.9", "1.8", "5.7", "7.6", "9.6", "9.3", "8.2", "8.0", "4.0", "3.6", "1.3"]

COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Any]] = {
    12949: ("correlation", "true_false_bivariate", _g(claim={"kind": "points_vs_correlation", "stated": "higher"}), _tf_points),
    12950: ("correlation", "correlation_from_table", _g(x=[1, 2, 3, 4, 5], y=[4, 5, 3, 1, 2], scene="plain"), _corr_plain),
    12951: ("correlation", "correlation_from_table", _g(x=[2, 4, 6, 8, 10], y=[1, 2, 3, 4, 5], scene="plain"), _corr_plain),
    12952: ("correlation", "correlation_from_table", _g(x=[2, 3, 6, 10, 14], y=[1, 8, 3, 7, 11], scene="plain"), _corr_plain),
    12953: ("correlation", "correlation_from_table", _g(x=[1, 2, 3, 4, 5], y=[10, 9, 8, 7, 6], scene="plain"), _corr_plain),
    12968: ("correlation", "correlation_from_table", _g(x=[5, 3, 7, 4, 8, 12, 10], y=[3, 2, 6, 4, 4, 7, 9], scene="aptitude"), _corr_aptitude),
    12959: ("correlation", "correlation_remove_point", _g(labels=list("ABCDE"), x=[2, 4, 5, 10, 10], y=[3, 4, 6, 1, 11]), _remove_point),
    12967: ("correlation", "correlation_change_add_point", _g(x=_FOREARM_X, y=_FOREARM_Y, new_point=["26", 174]), _change),
    12972: ("correlation", "correlation_rescale", _g(n_questions=20, old_per=5, new_per=6, top=80, r="0.73"), _rescale),
    12957: ("correlation", "true_false_bivariate", _g(claim={"kind": "r_range", "lo": -1, "hi": 1, "lo_closed": True, "hi_closed": True}), _tf_range),
    12958: ("correlation", "true_false_bivariate", _g(claim={"kind": "points_on_line", "a": 2, "b": -1, "stated": 1}), _tf_on_line),
    12955: ("regression", "true_false_bivariate", _g(claim={"kind": "slope_sign", "r_rel": ">", "m_rel": ">"}), _tf_slope_sign),
    12956: ("regression", "true_false_bivariate", _g(claim={"kind": "slope_sigma", "k": 1, "c": 1}), _tf_slope_sigma),
    12961: ("regression", "regression_from_summary", _g(mx=6, my=9, sx=3, sy=5, r="-0.8"), _reg_summary),
    12962: ("regression", "regression_from_table", _g(x=[33, 31, 29, 27], y=[14, 12, 8, 10], x0=30, scene="temp_sales"), _temp_sales),
    12966: ("regression", "regression_from_table", _g(x=[5, 6, 8, 9, 9, 11], y=[5, 8, 8, 12, 13, 14], x0=10, scene="eq_achievement"), _eq_achievement),
    12969: ("regression", "regression_from_table", _g(x=[16, 17, 18, 19, 20], y=[9, 10, 8, 6, 7], x0="17.5", scene="price_demand"), _price_demand),
    12964: ("regression", "regression_rounded_from_table", _g(x=_UTEMP_X, y=_UTEMP_Y, r_places=1, coef_places=4), _rounded_months),
    12965: ("regression", "correlation_from_regression_point", _g(mx=3, my=2, sx=5, sy=8, point=[6, 4]), _from_point),
    12970: ("regression", "regression_line_unknown_intercept", _g(mx=2, my=7, sx=3, sy=8, slope=2), _unknown_k),
    12971: ("regression", "regression_statement_selection", _g(
        n=20, mx=6, my=5, r="-0.9", line_point=[4, 6],
        statements=[{"kind": "passes_point", "x": 6, "y": 5}, {"kind": "slope_is", "stated": "-0.5"},
                    {"kind": "passes_point", "x": 2, "y": 7}, {"kind": "sigma_less", "first": "x", "second": "y"}]), _line_statements),
}

# Seed-0 textbook givens retained for deferred 12963 (publish excluded; operation kept).
RETAINED_DEFERRED_SOURCES: dict[int, tuple[str, str, dict[str, Any]]] = {
    12963: (
        "regression",
        "regression_predict_given_line",
        _g(x=_FOREARM_X, y=_FOREARM_Y, eq_places=1, m_r="3.8", b_r="66.4", x0="26.8", places=0),
    ),
}
