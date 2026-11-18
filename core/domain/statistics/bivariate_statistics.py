"""Bivariate data: Pearson correlation and its change when a data point is added.

Exact arithmetic (Fraction) decides every comparison; floats are only for display.  Not registered or promoted: a
candidate operation for generators of "continues an example's data set" items (e.g. 普高數學2 單元9 隨堂練習7).
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any, Sequence

Point = tuple[Any, Any]


def _frac(value: Any) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def _sums(points: Sequence[Point]) -> tuple[Fraction, Fraction, Fraction]:
    xs, ys = [_frac(p[0]) for p in points], [_frac(p[1]) for p in points]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy, sxx, syy


def correlation_signed_square(points: Sequence[Point]) -> tuple[int, Fraction]:
    """(sign of r, r squared) exactly; raises when r is undefined (fewer than 2 points or a constant variable)."""
    if len(points) < 2:
        raise ValueError("correlation_needs_two_points")
    sxy, sxx, syy = _sums(points)
    if sxx == 0 or syy == 0:
        raise ValueError("correlation_undefined_constant_variable")
    sign = (sxy > 0) - (sxy < 0)
    return sign, sxy * sxy / (sxx * syy)


def pearson_r(points: Sequence[Point]) -> float:
    sign, square = correlation_signed_square(points)
    return sign * math.sqrt(square)


def compare_correlation(before: Sequence[Point], after: Sequence[Point]) -> int:
    """-1 / 0 / 1 when r(after) is smaller / equal / larger than r(before), decided exactly."""
    (s1, q1), (s2, q2) = correlation_signed_square(before), correlation_signed_square(after)
    v1, v2 = s1 * q1, s2 * q2  # sign(r)*r^2 is strictly increasing in r
    return (v2 > v1) - (v2 < v1)


def correlation_change_after_adding_point(points: Sequence[Point], new_point: Point) -> dict[str, Any]:
    after = list(points) + [new_point]
    cmp = compare_correlation(points, after)
    return {
        "r_before": pearson_r(points),
        "r_after": pearson_r(after),
        "direction": {1: "變大", -1: "變小", 0: "不變"}[cmp],
    }


_SCENARIOS = (
    ("前臂長度", "公分", "身高", "公分", "某人測量{n}位女性的前臂長度x（公分）與身高y（公分）之對照如下表。"),
    ("每日讀書時間", "小時", "數學測驗成績", "分", "某班調查{n}位學生的每日讀書時間x（小時）與數學測驗成績y（分）之對照如下表。"),
    ("當日最高氣溫", "℃", "飲料銷售金額", "千元", "飲料店記錄{n}天的當日最高氣溫x（℃）與銷售金額y（千元）之對照如下表。"),
)


def _fmt(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{float(value):g}"


def build_correlation_change_item(seed: int) -> dict[str, Any]:
    """A self-contained "add one data point: does r get larger or smaller?" item with its data set in the stem."""
    rng = random.Random(seed)
    while True:
        n = rng.randint(6, 10)
        slope = Fraction(rng.choice([1, 2, 3, 4]), rng.choice([1, 2])) * rng.choice([1, -1])
        x0, y0 = rng.randint(10, 30), rng.randint(40, 160)
        xs = sorted(Fraction(x0) + Fraction(rng.randint(0, 16), 2) for _ in range(n))
        points = [(x, y0 + slope * (x - x0) + rng.randint(-3, 3)) for x in xs]
        x_new = xs[0] + Fraction(rng.randint(0, int(2 * (xs[-1] - xs[0]))), 2)
        on_trend = y0 + slope * (x_new - x0)
        new_point = (x_new, on_trend + rng.choice([-1, 1]) * rng.randint(0, 12))
        try:
            change = correlation_change_after_adding_point(points, new_point)
        except ValueError:
            continue
        if change["direction"] != "不變" and abs(change["r_after"] - change["r_before"]) >= 0.01:
            break
    xname, xunit, yname, yunit, intro = rng.choice(_SCENARIOS)
    header_x, header_y = f"\\text{{{xname}x（{xunit}）}}", f"\\text{{{yname}y（{yunit}）}}"
    cols = "|c|" + "c|" * n
    table = (f"\\(\\begin{{array}}{{{cols}}}\\hline {header_x} & " + " & ".join(_fmt(p[0]) for p in points)
             + f" \\\\ \\hline {header_y} & " + " & ".join(_fmt(p[1]) for p in points) + " \\\\ \\hline \\end{array}\\)")
    point_tex = f"\\(\\left({_fmt(new_point[0])},{_fmt(new_point[1])}\\right)\\)"
    question = (f"{intro.format(n=n)}\n{table}\n若今新增一筆資料 {point_tex}，"
                "試問x與y的相關係數會變大還是變小？")
    explanation = (f"原 {n} 筆資料的相關係數 \\(r\\approx {change['r_before']:.4f}\\)；"
                   f"加入 {point_tex} 後共 {n + 1} 筆，\\(r\\approx {change['r_after']:.4f}\\)，"
                   f"故相關係數{change['direction']}。")
    return {
        "question_text": question,
        "answer": change["direction"],
        "correct_answer": change["direction"],
        "answer_type": "single_choice_text",
        "choices": ["變大", "變小"],
        "explanation": explanation,
        "metadata": {
            "givens": {"points": [[_fmt(x), _fmt(y)] for x, y in points], "new_point": [_fmt(v) for v in new_point]},
            "target": "correlation_change_direction",
            "derivation": [f"r_before={change['r_before']:.6f}", f"r_after={change['r_after']:.6f}"],
        },
    }
