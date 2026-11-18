"""Bivariate descriptive statistics for 普高數學2 Unit 9 二維數據分析.

Textbook (population) style: S_xx=Σ(x-μx)², S_yy=Σ(y-μy)², S_xy=Σ(x-μx)(y-μy), r=S_xy/(√S_xx·√S_yy);
regression of y on x: m=r·σy/σx=S_xy/S_xx, b=μy-m·μx, σ=√(S/n).

Every graded value is computed with exact ``Fraction`` arithmetic and recomputed by a second independent path
(deviation sums vs raw sums, Cramer's rule, Decimal square roots, witness data sets). Disagreement refuses the
sample. Generators only supply stated givens; they never carry a textbook answer.

Display rule for r: r is always an exact rational for "compute r from a table" items (samplers keep
S_xx·S_yy a perfect square); it is shown as a terminating decimal when it terminates (e.g. -0.8), otherwise as a
reduced fraction (e.g. 5/6). Only items whose stem states a rounding rule (Excel-style data, 12964) round
r to the stated decimals (ROUND_HALF_UP of the exact value, decided without floats).
"""

from __future__ import annotations

import math
from decimal import ROUND_HALF_UP, Decimal, localcontext
from fractions import Fraction
from typing import Any, Callable

DOMAIN_KEY = "statistics.bivariate_descriptive"

TRUE_FALSE = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
UP_DOWN = ({"label": "A", "value": "變大"}, {"label": "B", "value": "變小"})
PREC = 60
TIE_MARGIN = Decimal("1e-9")


# --- small helpers ---------------------------------------------------------------------------------------------------


def _require(givens: dict[str, Any], *keys: str) -> None:
    missing = [k for k in keys if k not in givens]
    if missing:
        raise ValueError("givens_required:" + ",".join(missing))


def _frac(v: Any, name: str = "value") -> Fraction:
    if isinstance(v, bool):
        raise ValueError(f"not_a_fraction:{name}")
    try:
        return v if isinstance(v, Fraction) else Fraction(str(v).strip())
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"not_a_fraction:{name}") from None


def _int(v: Any, name: str, low: int | None = None, high: int | None = None) -> int:
    f = _frac(v, name)
    if f.denominator != 1:
        raise ValueError(f"not_an_integer:{name}")
    n = int(f)
    if (low is not None and n < low) or (high is not None and n > high):
        raise ValueError(f"out_of_range:{name}")
    return n


def _list(values: Any, name: str, minimum: int = 2) -> list[Fraction]:
    if not isinstance(values, (list, tuple)) or len(values) < minimum:
        raise ValueError(f"bad_{name}")
    return [_frac(v, name) for v in values]


def _terminating(f: Fraction) -> bool:
    den = f.denominator
    for p in (2, 5):
        while den % p == 0:
            den //= p
    return den == 1


def _show(f: Fraction) -> str:
    """Integer, terminating decimal, otherwise reduced fraction."""
    if f.denominator == 1:
        return str(f.numerator)
    if _terminating(f):
        return format(Decimal(f.numerator) / Decimal(f.denominator), "f").rstrip("0").rstrip(".")
    return str(f)


def _dec(f: Fraction) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PREC
        return Decimal(f.numerator) / Decimal(f.denominator)


def _sqrt_frac(f: Fraction) -> Fraction | None:
    """Exact square root of a non-negative rational, or None when it is irrational."""
    if f < 0:
        return None
    sn, sd = math.isqrt(f.numerator), math.isqrt(f.denominator)
    return Fraction(sn, sd) if sn * sn == f.numerator and sd * sd == f.denominator else None


def _sign(f: Fraction) -> int:
    return (f > 0) - (f < 0)


def round_half_up(f: Fraction, places: int) -> Fraction:
    """ROUND_HALF_UP to ``places`` decimals, computed two ways (Decimal and integer arithmetic)."""
    if not 0 <= places <= 8:
        raise ValueError("bad_places")
    with localcontext() as ctx:
        ctx.prec = PREC
        via_decimal = Fraction(str(_dec(f).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)))
    scale = 10 ** places
    n = (2 * abs(f.numerator) * scale + f.denominator) // (2 * f.denominator)  # floor(|f|·scale + 1/2)
    via_int = Fraction(_sign(f) * n, scale)
    if via_decimal != via_int:
        raise ValueError("rounding_mismatch")
    return via_int


def _is_rounding_tie(f: Fraction, places: int) -> bool:
    return (f * 10 ** places * 2).denominator == 1 and (f * 10 ** places).denominator != 1


def _fixed(f: Fraction, places: int) -> str:
    """Exact decimal text of an already rounded value with exactly ``places`` decimals."""
    return format(_dec(f), f".{places}f")


def _value(f: Fraction, work: str) -> dict[str, Any]:
    return {"kind": "rational", "value": str(f), "work": work}


def _choice(label: str, choices, work: str) -> dict[str, Any]:
    if label not in {c["label"] for c in choices}:
        raise ValueError("bad_choice_label")
    return {"kind": "choice", "label": label, "choices": [dict(c) for c in choices], "work": work}


def _selected(indices: list[int], work: str) -> dict[str, Any]:
    if not indices or sorted(indices) != indices or len(set(indices)) != len(indices):
        raise ValueError("bad_selected")
    return {"kind": "selected", "selected": list(indices), "work": work}


def fraction_line_text(m: Fraction, b: Fraction) -> str:
    """``y=p/qx+c`` with fractions only (the line checker's integer route does not read decimals)."""
    return f"y={m}x{'+' if b >= 0 else '-'}{abs(b)}"


def _equation(value: str, display: str, work: str, line: tuple[Fraction, Fraction] | None = None) -> dict[str, Any]:
    from core.checkers.linear_equation_equivalent_checker import check_linear_equation_equivalent_answer

    # second route to the same line: the fraction text of (m, b) must be proportional to the graded form
    if line is not None and not check_linear_equation_equivalent_answer(fraction_line_text(*line), value):
        raise ValueError("line_text_mismatch")
    return {"kind": "equation", "value": value, "display": display, "work": work}


def _pack(parts: list[dict[str, Any]]) -> dict[str, Any]:
    if not parts:
        raise ValueError("no_parts")
    return {"parts": parts}


# --- lines ------------------------------------------------------------------------------------------------------------


def _coef(a: int) -> str:
    return {1: "", -1: "-"}.get(a, str(a))


def general_form(m: Fraction, b: Fraction) -> str:
    """``y=mx+b`` as a primitive integer ``Ax+By+C=0`` with B>0 (the checker accepts any proportional form)."""
    d = math.lcm(m.denominator, b.denominator)
    a_, b_, c_ = -int(m * d), d, -int(b * d)
    g = math.gcd(math.gcd(abs(a_), abs(b_)), abs(c_)) or 1
    a_, b_, c_ = a_ // g, b_ // g, c_ // g
    text = ""
    if a_:
        text += f"{_coef(a_)}x"
    text += ("+" if text and b_ > 0 else "") + f"{_coef(b_)}y"
    if c_:
        text += ("+" if c_ > 0 else "") + str(c_)
    return text + "=0"


def y_form(m: Fraction, b: Fraction) -> str:
    """Display form with fractions (never bare decimals mixed with fractions)."""
    text = "y=" + (f"{m}x" if m not in (1, -1) else ("x" if m == 1 else "-x"))
    if b:
        text += ("+" if b > 0 else "-") + str(abs(b))
    return text


# --- two-variable statistics ------------------------------------------------------------------------------------------


def _stats(xs: list[Fraction], ys: list[Fraction]) -> dict[str, Fraction]:
    """μ, S_xx, S_yy, S_xy by deviations (textbook) and again by raw sums; the two must agree."""
    n = len(xs)
    if n != len(ys) or n < 2:
        raise ValueError("bad_data_lengths")
    mx, my = sum(xs, Fraction(0)) / n, sum(ys, Fraction(0)) / n
    sxx = sum(((x - mx) ** 2 for x in xs), Fraction(0))
    syy = sum(((y - my) ** 2 for y in ys), Fraction(0))
    sxy = sum(((x - mx) * (y - my) for x, y in zip(xs, ys)), Fraction(0))
    tx, ty = sum(xs, Fraction(0)), sum(ys, Fraction(0))
    raw = (
        sum((x * x for x in xs), Fraction(0)) - tx * tx / n,
        sum((y * y for y in ys), Fraction(0)) - ty * ty / n,
        sum((x * y for x, y in zip(xs, ys)), Fraction(0)) - tx * ty / n,
    )
    if raw != (sxx, syy, sxy):
        raise ValueError("stats_mismatch")
    if sxx == 0 or syy == 0:
        raise ValueError("constant_variable")
    return {"n": Fraction(n), "mx": mx, "my": my, "sxx": sxx, "syy": syy, "sxy": sxy}


def _signed_square(s: dict[str, Fraction]) -> Fraction:
    """sign(r)·r² — strictly increasing in r, so it orders correlation coefficients exactly."""
    return _sign(s["sxy"]) * s["sxy"] ** 2 / (s["sxx"] * s["syy"])


def _r_decimal(s: dict[str, Fraction]) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PREC
        return _dec(s["sxy"]) / (_dec(s["sxx"]).sqrt() * _dec(s["syy"]).sqrt())


def _r_checked_decimal(s: dict[str, Fraction]) -> Decimal:
    """r as a Decimal, cross-checked against the exact signed square."""
    r = _r_decimal(s)
    with localcontext() as ctx:
        ctx.prec = PREC
        if abs(r * r * _sign(s["sxy"]) - _dec(_signed_square(s))) > Decimal("1e-40") or abs(r) > 1 + Decimal("1e-40"):
            raise ValueError("r_decimal_mismatch")
    return r


def _r_exact(s: dict[str, Fraction]) -> Fraction:
    if s["sxy"] == 0:
        return Fraction(0)
    root = _sqrt_frac(s["sxx"] * s["syy"])
    if root is None:
        raise ValueError("r_not_rational")
    r = s["sxy"] / root
    if r * r != s["sxy"] ** 2 / (s["sxx"] * s["syy"]) or abs(r) > 1:
        raise ValueError("r_mismatch")
    if abs(_dec(r) - _r_checked_decimal(s)) > Decimal("1e-40"):
        raise ValueError("r_decimal_mismatch")
    return r


def _r_rounded(s: dict[str, Fraction], places: int) -> Fraction:
    """round(r, places) for irrational r too: compare r² with ((k±½)/10^p)² exactly, then cross-check with Decimal."""
    sq, sign = s["sxy"] ** 2 / (s["sxx"] * s["syy"]), _sign(s["sxy"])
    scale = 10 ** places
    k = 0
    while Fraction(2 * k + 1, 2 * scale) ** 2 <= sq:  # smallest k with |r| < (k+½)/scale  (half-up)
        k += 1
    exact = Fraction(sign * k, scale)
    via_decimal = Fraction(str(_r_checked_decimal(s).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)))
    if exact != via_decimal:
        raise ValueError("r_rounding_mismatch")
    edge = Fraction(2 * k + 1, 2 * scale) ** 2
    if abs(_dec(edge) - _dec(sq)) < TIE_MARGIN and k:
        raise ValueError("r_on_rounding_boundary")
    return exact


def _regression(xs: list[Fraction], ys: list[Fraction], s: dict[str, Fraction]) -> tuple[Fraction, Fraction]:
    """y on x: m=S_xy/S_xx, b=μy-mμx; Cramer's rule on the normal equations and m²=r²S_yy/S_xx must agree."""
    m = s["sxy"] / s["sxx"]
    b = s["my"] - m * s["mx"]
    n = len(xs)
    tx, ty = sum(xs, Fraction(0)), sum(ys, Fraction(0))
    txx = sum((x * x for x in xs), Fraction(0))
    txy = sum((x * y for x, y in zip(xs, ys)), Fraction(0))
    det = n * txx - tx * tx
    if (n * txy - tx * ty) / det != m or (ty * txx - tx * txy) / det != b:
        raise ValueError("regression_mismatch")
    if m * m != s["sxy"] ** 2 / (s["sxx"] * s["syy"]) * s["syy"] / s["sxx"] or _sign(m) != _sign(s["sxy"]):
        raise ValueError("regression_r_relation_mismatch")
    return m, b


def _data(givens: dict[str, Any], minimum: int = 3) -> tuple[list[Fraction], list[Fraction]]:
    xs, ys = _list(givens["x"], "x", minimum), _list(givens["y"], "y", minimum)
    if len(xs) != len(ys):
        raise ValueError("data_length_mismatch")
    return xs, ys


def _pairs_text(xs: list[Fraction], ys: list[Fraction]) -> str:
    return "、".join(f"({_show(x)}, {_show(y)})" for x, y in zip(xs, ys))


# --- correlation ------------------------------------------------------------------------------------------------------


def _correlation_from_table_answer(x: Any, y: Any, **_: Any) -> dict[str, Any]:
    xs, ys = _data({"x": x, "y": y})
    s = _stats(xs, ys)
    r = _r_exact(s)
    work = (f"μx={_show(s['mx'])}，μy={_show(s['my'])}，Sxx={_show(s['sxx'])}，Syy={_show(s['syy'])}，Sxy={_show(s['sxy'])}，"
            f"r=Sxy/(√Sxx·√Syy)={_show(r)}。")
    return _pack([_value(r, work)])


def correlation_from_table(*, x: Any, y: Any, **_: Any) -> dict[str, Any]:
    return _correlation_from_table_answer(x, y)


def _check_correlation_from_table(g: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _correlation_from_table_answer(g["x"], g["y"]) == answer


def _remove_point_answer(labels: Any, x: Any, y: Any) -> dict[str, Any]:
    xs, ys = _data({"x": x, "y": y}, 5)
    if not isinstance(labels, (list, tuple)) or len(labels) != len(xs) or len(set(map(str, labels))) != len(xs):
        raise ValueError("bad_labels")
    codes = [str(c) for c in labels]
    exact, decimals = [], []
    for i in range(len(xs)):
        rest_x, rest_y = xs[:i] + xs[i + 1:], ys[:i] + ys[i + 1:]
        s = _stats(rest_x, rest_y)
        exact.append(_signed_square(s))
        decimals.append(_r_checked_decimal(s))
    best = max(range(len(xs)), key=lambda i: exact[i])
    if sorted(exact)[-1] == sorted(exact)[-2]:
        raise ValueError("remove_point_tie")
    if max(range(len(xs)), key=lambda i: decimals[i]) != best:
        raise ValueError("remove_point_decimal_mismatch")
    if sorted(decimals)[-1] - sorted(decimals)[-2] < Decimal("1e-6"):
        raise ValueError("remove_point_too_close")
    shown = "，".join(f"去掉{c}：r≈{float(d):.4f}" for c, d in zip(codes, decimals))
    choices = [{"label": c, "value": f"去掉{c}"} for c in codes]
    return _pack([_choice(codes[best], choices, f"逐一去掉一筆資料後的相關係數：{shown}。去掉 {codes[best]} 後相關係數最大。")])


def correlation_remove_point(*, labels: Any, x: Any, y: Any, **_: Any) -> dict[str, Any]:
    return _remove_point_answer(labels, x, y)


def _check_correlation_remove_point(g: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _remove_point_answer(g["labels"], g["x"], g["y"]) == answer


def _change_answer(x: Any, y: Any, new_point: Any) -> dict[str, Any]:
    xs, ys = _data({"x": x, "y": y}, 4)
    if not isinstance(new_point, (list, tuple)) or len(new_point) != 2:
        raise ValueError("bad_new_point")
    nx, ny = _frac(new_point[0], "new_x"), _frac(new_point[1], "new_y")
    before, after = _stats(xs, ys), _stats(xs + [nx], ys + [ny])
    cmp = (_signed_square(after) > _signed_square(before)) - (_signed_square(after) < _signed_square(before))
    if cmp == 0:
        raise ValueError("correlation_unchanged")
    rb, ra = _r_checked_decimal(before), _r_checked_decimal(after)
    if ((ra > rb) - (ra < rb)) != cmp or abs(ra - rb) < Decimal("0.01"):
        raise ValueError("correlation_change_mismatch_or_tiny")
    label = "A" if cmp > 0 else "B"
    word = "變大" if cmp > 0 else "變小"
    return _pack([_choice(label, UP_DOWN, f"原 {len(xs)} 筆資料 r≈{float(rb):.4f}；新增({_show(nx)}, {_show(ny)})後 r≈{float(ra):.4f}，相關係數{word}。")])


def correlation_change_add_point(*, x: Any, y: Any, new_point: Any, **_: Any) -> dict[str, Any]:
    return _change_answer(x, y, new_point)


def _check_correlation_change_add_point(g: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _change_answer(g["x"], g["y"], g["new_point"]) == answer


def _rescale_answer(n_questions: Any, old_per: Any, new_per: Any, top: Any, r: Any) -> dict[str, Any]:
    n, old, new = _int(n_questions, "n_questions", 2, 100), _int(old_per, "old_per", 1, 100), _int(new_per, "new_per", 1, 100)
    if new <= old:
        raise ValueError("new_per_must_be_larger")
    top_old, rr = _int(top, "top", 1), _frac(r, "r")
    if top_old > n * old or top_old * Fraction(new, old) > n * new or abs(rr) > 1 or rr == 0:
        raise ValueError("bad_scores_or_r")
    # witness: every possible old math score against a fixed English score pattern
    old_scores = [Fraction(i * old) for i in range(n + 1)]
    english = [Fraction((7 * i + 3) % 11) for i in range(n + 1)]
    new_scores = [v * Fraction(new, old) for v in old_scores]
    base, scaled, vs_old = _stats(old_scores, english), _stats(new_scores, english), _stats(new_scores, old_scores)
    if _signed_square(base) != _signed_square(scaled) or _signed_square(vs_old) != 1:
        raise ValueError("rescale_invariance_failed")
    new_top = top_old * Fraction(new, old)
    work1 = f"每題配分由 {old} 分改為 {new} 分是乘以正數 {_show(Fraction(new, old))}，相關係數不變，仍為 {_show(rr)}。"
    work2 = (f"新成績是原成績的 {_show(Fraction(new, old))} 倍（正比例關係，點都在斜率為正的直線上），相關係數為 1；"
             f"（調整後全校最高分為 {_show(new_top)} 分。）")
    return _pack([_value(rr, work1), _value(Fraction(1), work2)])


def correlation_rescale(*, n_questions: Any, old_per: Any, new_per: Any, top: Any, r: Any, **_: Any) -> dict[str, Any]:
    return _rescale_answer(n_questions, old_per, new_per, top, r)


def _check_correlation_rescale(g: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _rescale_answer(g["n_questions"], g["old_per"], g["new_per"], g["top"], g["r"]) == answer


# --- regression -------------------------------------------------------------------------------------------------------


def _line_from_summary(mx: Any, my: Any, sx: Any, sy: Any, r: Any) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]:
    mx_, my_, sx_, sy_, r_ = (_frac(v, n) for v, n in ((mx, "mx"), (my, "my"), (sx, "sx"), (sy, "sy"), (r, "r")))
    if sx_ <= 0 or sy_ <= 0 or abs(r_) > 1:
        raise ValueError("bad_summary")
    return mx_, my_, sx_, sy_, r_, r_ * sy_ / sx_, my_ - (r_ * sy_ / sx_) * mx_


def _regression_from_summary_answer(mx: Any, my: Any, sx: Any, sy: Any, r: Any) -> dict[str, Any]:
    mx_, my_, sx_, sy_, r_, m, b = _line_from_summary(mx, my, sx, sy, r)
    if r_ == 0:
        raise ValueError("zero_correlation")
    # second route: point-slope through (μx, μy) expanded, and slope·σx = r·σy
    if m * sx_ != r_ * sy_ or m * mx_ + b != my_:
        raise ValueError("line_mismatch")
    work = (f"斜率 m=r·σy/σx={_show(r_)}×{_show(sy_)}/{_show(sx_)}={_show(m)}；通過({_show(mx_)}, {_show(my_)})，"
            f"點斜式得 {y_form(m, b)}。")
    return _pack([_equation(general_form(m, b), y_form(m, b), work, (m, b))])


def regression_from_summary(*, mx: Any, my: Any, sx: Any, sy: Any, r: Any, **_: Any) -> dict[str, Any]:
    return _regression_from_summary_answer(mx, my, sx, sy, r)


def _check_regression_from_summary(g: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _regression_from_summary_answer(g["mx"], g["my"], g["sx"], g["sy"], g["r"]) == answer


def _predict_exact(m: Fraction, b: Fraction, x0: Fraction) -> Fraction:
    y0 = m * x0 + b
    if y0 != (b + m * (x0 - 1)) + m:  # intercept form vs. a one-step-back point-slope form
        raise ValueError("prediction_mismatch")
    return y0


def _regression_from_table_answer(x: Any, y: Any, x0: Any) -> dict[str, Any]:
    xs, ys = _data({"x": x, "y": y})
    s = _stats(xs, ys)
    m, b = _regression(xs, ys, s)
    if m == 0:
        raise ValueError("zero_slope")
    x_0 = _frac(x0, "x0")
    y_0 = _predict_exact(m, b, x_0)
    if not _terminating(y_0):
        raise ValueError("prediction_not_terminating")
    work1 = (f"μx={_show(s['mx'])}，μy={_show(s['my'])}，Sxx={_show(s['sxx'])}，Sxy={_show(s['sxy'])}，"
             f"m=Sxy/Sxx={_show(m)}，b=μy−mμx={_show(b)}，迴歸直線 {y_form(m, b)}。")
    work2 = f"x={_show(x_0)} 代入 {y_form(m, b)}，得 y={_show(y_0)}。"
    return _pack([_equation(general_form(m, b), y_form(m, b), work1, (m, b)), _value(y_0, work2)])


def regression_from_table(*, x: Any, y: Any, x0: Any, **_: Any) -> dict[str, Any]:
    return _regression_from_table_answer(x, y, x0)


def _check_regression_from_table(g: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _regression_from_table_answer(g["x"], g["y"], g["x0"]) == answer


def _regression_rounded_answer(x: Any, y: Any, r_places: Any, coef_places: Any) -> dict[str, Any]:
    xs, ys = _data({"x": x, "y": y}, 5)
    rp, cp = _int(r_places, "r_places", 0, 6), _int(coef_places, "coef_places", 1, 8)
    s = _stats(xs, ys)
    r_r = _r_rounded(s, rp)
    m, b = _regression(xs, ys, s)
    m_r, b_r = round_half_up(m, cp), round_half_up(b, cp)
    for exact, rounded in ((m, m_r), (b, b_r)):
        if _is_rounding_tie(exact, cp):
            raise ValueError("coefficient_rounding_tie")
    if m_r == 0:
        raise ValueError("rounded_slope_zero")
    work1 = f"r=Sxy/(√Sxx·√Syy)≈{float(_r_checked_decimal(s)):.6f}，四捨五入到小數點後第 {rp} 位為 {_fixed(r_r, rp)}。"
    line = f"迴歸直線 y={_fixed(m_r, cp)}x{'+' if b_r >= 0 else '-'}{_fixed(abs(b_r), cp)}"
    # The shared equation checkers do not reliably accept equivalent forms of 4-decimal equations, so the line is
    # graded as its two coefficients (slope m and y-intercept b), each an exact rounded rational.
    work2 = f"m=Sxy/Sxx={_show(m)}≈{_fixed(m_r, cp)}（{line}）。"
    work3 = f"b=μy−m·μx={_show(b)}≈{_fixed(b_r, cp)}（{line}）。"
    return _pack([_value(r_r, work1), _value(m_r, work2), _value(b_r, work3)])


def regression_rounded_from_table(*, x: Any, y: Any, r_places: Any, coef_places: Any, **_: Any) -> dict[str, Any]:
    return _regression_rounded_answer(x, y, r_places, coef_places)


def _check_regression_rounded_from_table(g: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _regression_rounded_answer(g["x"], g["y"], g["r_places"], g["coef_places"]) == answer


def _predict_given_line_answer(x: Any, y: Any, eq_places: Any, m_r: Any, b_r: Any, x0: Any, places: Any) -> dict[str, Any]:
    xs, ys = _data({"x": x, "y": y}, 5)
    ep, pl = _int(eq_places, "eq_places", 1, 6), _int(places, "places", 0, 4)
    s = _stats(xs, ys)
    m, b = _regression(xs, ys, s)
    given_m, given_b, x_0 = _frac(m_r, "m_r"), _frac(b_r, "b_r"), _frac(x0, "x0")
    if round_half_up(m, ep) != given_m or round_half_up(b, ep) != given_b or _is_rounding_tie(m, ep) or _is_rounding_tie(b, ep):
        raise ValueError("stated_line_does_not_match_data")
    y_0 = given_m * x_0 + given_b
    if _is_rounding_tie(y_0, pl):
        raise ValueError("prediction_rounding_tie")
    out = round_half_up(y_0, pl)
    work = (f"x={_show(x_0)} 代入 y={_show(given_m)}x{'+' if given_b >= 0 else '-'}{_show(abs(given_b))}，"
            f"得 y={_show(y_0)}，四捨五入到小數點後第 {pl} 位為 {_show(out)}。")
    return _pack([_value(out, work)])


def regression_predict_given_line(*, x: Any, y: Any, eq_places: Any, m_r: Any, b_r: Any, x0: Any, places: Any, **_: Any) -> dict[str, Any]:
    return _predict_given_line_answer(x, y, eq_places, m_r, b_r, x0, places)


def _check_regression_predict_given_line(g: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _predict_given_line_answer(g["x"], g["y"], g["eq_places"], g["m_r"], g["b_r"], g["x0"], g["places"]) == answer


def _r_from_point_answer(mx: Any, my: Any, sx: Any, sy: Any, point: Any) -> dict[str, Any]:
    mx_, my_, sx_, sy_ = (_frac(v, n) for v, n in ((mx, "mx"), (my, "my"), (sx, "sx"), (sy, "sy")))
    if not isinstance(point, (list, tuple)) or len(point) != 2:
        raise ValueError("bad_point")
    px, py = _frac(point[0], "px"), _frac(point[1], "py")
    if sx_ <= 0 or sy_ <= 0 or px == mx_:
        raise ValueError("bad_summary")
    m = (py - my_) / (px - mx_)           # the line passes through (μx, μy) and the given point
    r = m * sx_ / sy_                      # m = r·σy/σx
    if r == 0 or abs(r) > 1:
        raise ValueError("r_out_of_range")
    if r * sy_ / sx_ != m or my_ + r * sy_ / sx_ * (px - mx_) != py:
        raise ValueError("r_line_mismatch")
    work = f"斜率 m=({_show(py)}−{_show(my_)})/({_show(px)}−{_show(mx_)})={_show(m)}；m=r·σy/σx，r=m·σx/σy={_show(r)}。"
    return _pack([_value(r, work)])


def correlation_from_regression_point(*, mx: Any, my: Any, sx: Any, sy: Any, point: Any, **_: Any) -> dict[str, Any]:
    return _r_from_point_answer(mx, my, sx, sy, point)


def _check_correlation_from_regression_point(g: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _r_from_point_answer(g["mx"], g["my"], g["sx"], g["sy"], g["point"]) == answer


def _unknown_intercept_answer(mx: Any, my: Any, sx: Any, sy: Any, slope: Any) -> dict[str, Any]:
    mx_, my_, sx_, sy_, a = (_frac(v, n) for v, n in ((mx, "mx"), (my, "my"), (sx, "sx"), (sy, "sy"), (slope, "slope")))
    if sx_ <= 0 or sy_ <= 0 or a == 0:
        raise ValueError("bad_summary")
    k = my_ - a * mx_                      # the line passes through (μx, μy)
    r = a * sx_ / sy_
    if r == 0 or abs(r) > 1:
        raise ValueError("r_out_of_range")
    if a * mx_ + k != my_ or r * sy_ / sx_ != a:
        raise ValueError("unknown_intercept_mismatch")
    work_k = f"迴歸直線通過({_show(mx_)}, {_show(my_)})：{_show(my_)}={_show(a)}×{_show(mx_)}+k，k={_show(k)}。"
    work_r = f"斜率 {_show(a)}=r·σy/σx，r={_show(a)}×{_show(sx_)}/{_show(sy_)}={_show(r)}。"
    return _pack([_value(k, work_k), _value(r, work_r)])


def regression_line_unknown_intercept(*, mx: Any, my: Any, sx: Any, sy: Any, slope: Any, **_: Any) -> dict[str, Any]:
    return _unknown_intercept_answer(mx, my, sx, sy, slope)


def _check_regression_line_unknown_intercept(g: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _unknown_intercept_answer(g["mx"], g["my"], g["sx"], g["sy"], g["slope"]) == answer


STATEMENT_KINDS = ("passes_point", "slope_is", "sigma_less")


def _line_statement(st: dict[str, Any], mx: Fraction, my: Fraction, r: Fraction, point: tuple[Fraction, Fraction]) -> tuple[bool, str]:
    px, py = point
    m = (py - my) / (px - mx)
    kind = st.get("kind")
    if kind == "passes_point":
        qx, qy = _frac(st["x"], "x"), _frac(st["y"], "y")
        path_a = qy == my + m * (qx - mx)
        path_b = (qy - my) * (px - mx) == (py - my) * (qx - mx)   # collinear with (μx, μy) and the given point
        if path_a != path_b:
            raise ValueError("passes_point_mismatch")
        return path_a, f"點({_show(qx)}, {_show(qy)}){'在' if path_a else '不在'}迴歸直線上"
    if kind == "slope_is":
        stated = _frac(st["stated"], "stated")
        return stated == m, f"斜率為 {_show(m)}"
    if kind == "sigma_less":
        first, second = st.get("first"), st.get("second")
        if {first, second} != {"x", "y"}:
            raise ValueError("bad_sigma_statement")
        ratio = r / m                       # σx/σy, because m = r·σy/σx
        if ratio <= 0:
            raise ValueError("sigma_ratio_not_positive")
        if ratio == 1:
            raise ValueError("sigma_equal")
        sx_less = ratio < 1
        # second route: m = r·σy/σx  ⇒  σx/σy = r/m, compare squares to stay exact
        if (r * r < m * m) != sx_less:
            raise ValueError("sigma_compare_mismatch")
        truth = sx_less if first == "x" else not sx_less
        return truth, f"σx/σy=r/m={_show(ratio)}，故σx{'<' if sx_less else '>'}σy"
    raise ValueError(f"unknown_statement:{kind}")


def _statement_selection_answer(n: Any, mx: Any, my: Any, r: Any, line_point: Any, statements: Any) -> dict[str, Any]:
    _int(n, "n", 3, 10000)
    mx_, my_, r_ = _frac(mx, "mx"), _frac(my, "my"), _frac(r, "r")
    if not isinstance(line_point, (list, tuple)) or len(line_point) != 2:
        raise ValueError("bad_line_point")
    point = (_frac(line_point[0], "px"), _frac(line_point[1], "py"))
    if point[0] == mx_ or r_ == 0 or abs(r_) >= 1 or _sign((point[1] - my_) / (point[0] - mx_)) != _sign(r_):
        raise ValueError("inconsistent_line_and_r")
    if not isinstance(statements, list) or len(statements) < 3:
        raise ValueError("bad_statements")
    results = [_line_statement(st, mx_, my_, r_, point) for st in statements]
    picked = [i for i, (ok, _w) in enumerate(results, 1) if ok]
    if not picked or len(picked) == len(results):
        raise ValueError("selection_not_informative")
    return _pack([_selected(picked, "；".join(f"({i}){w}，{'正確' if ok else '不正確'}" for i, (ok, w) in enumerate(results, 1)) + "。")])


def regression_statement_selection(*, n: Any, mx: Any, my: Any, r: Any, line_point: Any, statements: Any, **_: Any) -> dict[str, Any]:
    return _statement_selection_answer(n, mx, my, r, line_point, statements)


def _check_regression_statement_selection(g: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _statement_selection_answer(g["n"], g["mx"], g["my"], g["r"], g["line_point"], g["statements"]) == answer


# --- true/false concept claims ---------------------------------------------------------------------------------------

_BASE_DOWN = ([Fraction(v) for v in (1, 2, 3, 4)], [Fraction(v) for v in (1, 2, 3, 4)], (Fraction(5), Fraction(1)))
_BASE_UP = ([Fraction(v) for v in (1, 2, 3, 4)], [Fraction(v) for v in (2, 1, 4, 3)], (Fraction(5), Fraction(5)))
_RELS = {">": 1, "<": -1, "=": 0}
RELATION_WORDS = tuple(_RELS)


def _strength_change(base: tuple[list[Fraction], list[Fraction], tuple[Fraction, Fraction]]) -> int:
    xs, ys, extra = base
    before, after = _stats(xs, ys), _stats(xs + [extra[0]], ys + [extra[1]])
    exact = (after["sxy"] ** 2 / (after["sxx"] * after["syy"])) - (before["sxy"] ** 2 / (before["sxx"] * before["syy"]))
    dec = _r_checked_decimal(after).copy_abs() - _r_checked_decimal(before).copy_abs()
    if _sign(exact) != (dec > 0) - (dec < 0) or exact == 0:
        raise ValueError("strength_change_mismatch")
    return _sign(exact)


def _claim_points_vs_correlation(claim: dict[str, Any]) -> tuple[bool, str]:
    stated = claim.get("stated")
    if stated not in ("higher", "lower", "unrelated"):
        raise ValueError("bad_stated")
    seen = {_strength_change(_BASE_DOWN), _strength_change(_BASE_UP)}
    if seen != {1, -1}:
        raise ValueError("witness_not_two_sided")
    truth = {"higher": seen == {1}, "lower": seen == {-1}, "unrelated": seen == {1, -1}}[stated]
    return truth, "新增資料點後，相關程度可能變高也可能變低（取決於新點的位置），與點數多寡無關。"


def _claim_slope_sign(claim: dict[str, Any]) -> tuple[bool, str]:
    r_rel, m_rel = claim.get("r_rel"), claim.get("m_rel")
    if r_rel not in _RELS or m_rel not in _RELS:
        raise ValueError("bad_relation")
    witnesses = {
        1: ([Fraction(v) for v in (1, 2, 3, 4)], [Fraction(v) for v in (1, 3, 2, 4)]),
        -1: ([Fraction(v) for v in (1, 2, 3, 4)], [Fraction(v) for v in (4, 2, 3, 1)]),
        0: ([Fraction(v) for v in (1, 2, 3)], [Fraction(v) for v in (1, 3, 1)]),
    }
    xs, ys = witnesses[_RELS[r_rel]]
    sxx = sum(((v - sum(xs) / len(xs)) ** 2 for v in xs), Fraction(0))
    sxy = sum(((a - sum(xs) / len(xs)) * (b - sum(ys) / len(ys)) for a, b in zip(xs, ys)), Fraction(0))
    if _sign(sxy) != _RELS[r_rel]:
        raise ValueError("witness_sign_mismatch")
    path_b = _sign(sxy / sxx)               # slope of the witness regression line
    path_a = _RELS[r_rel]                   # m = r·σy/σx with σx, σy > 0 has the sign of r
    if path_a != path_b:
        raise ValueError("slope_sign_mismatch")
    truth = _RELS[m_rel] == path_a
    return truth, "m=r·σy/σx，σx、σy 為正，故 m 與 r 同號（r=0 時 m=0）。"


def _claim_slope_sigma(claim: dict[str, Any]) -> tuple[bool, str]:
    k, c = _frac(claim.get("k"), "k"), _frac(claim.get("c"), "c")
    if k <= 0 or c <= 0:
        raise ValueError("bad_multiples")
    xs = [Fraction(v) for v in (1, 2, 3, 4, 5)]
    base_y = [Fraction(v) for v in (2, 1, 4, 3, 5)]            # S_yy = S_xx = 10, so σy/σx = 1; scaling by k gives σy/σx = k
    ys = [k * v for v in base_y]
    s = _stats(xs, ys)
    if s["syy"] != k * k * s["sxx"]:
        raise ValueError("sigma_ratio_witness_failed")
    m, _b = _regression(xs, ys, s)
    r = s["sxy"] / _sqrt_frac(s["sxx"] * s["syy"])
    path_b = m == c * r                     # does the witness satisfy m = c·r ?
    path_a = c == k                         # m = r·σy/σx = k·r
    if path_a != path_b:
        raise ValueError("slope_sigma_mismatch")
    return path_a, f"m=r·σy/σx，σy/σx={_show(k)}，故 m 是 r 的 {_show(k)} 倍。"


def _claim_r_range(claim: dict[str, Any]) -> tuple[bool, str]:
    lo, hi = _frac(claim.get("lo"), "lo"), _frac(claim.get("hi"), "hi")
    lo_closed, hi_closed = bool(claim.get("lo_closed")), bool(claim.get("hi_closed"))
    if lo >= hi:
        raise ValueError("bad_range")

    def inside(v: Fraction) -> bool:
        return (lo < v or (lo_closed and lo == v)) and (v < hi or (hi_closed and hi == v))

    # attainable values: exactly -1 and 1 (perfect lines) and everything between (r = 0 witnessed too)
    path_a = all(inside(v) for v in (Fraction(-1), Fraction(0), Fraction(1)))
    xs = [Fraction(v) for v in (1, 2, 3, 4)]
    witnesses = [
        [3 * v + 2 for v in xs],
        [-2 * v + 9 for v in xs],
        [Fraction(v) for v in (1, 3, 3, 1)],
    ]
    values = [_r_exact(_stats(xs, ys)) for ys in witnesses]
    if values != [Fraction(1), Fraction(-1), Fraction(0)]:
        raise ValueError("r_witness_failed")
    path_b = all(inside(v) for v in values)
    if path_a != path_b:
        raise ValueError("r_range_mismatch")
    return path_a, "相關係數 r 可以等於 −1（完全負相關）與 1（完全正相關），且 −1≤r≤1。"


def _claim_points_on_line(claim: dict[str, Any]) -> tuple[bool, str]:
    a, b = _frac(claim.get("a"), "a"), _frac(claim.get("b"), "b")
    stated = _frac(claim.get("stated"), "stated")
    if a == 0:
        raise ValueError("horizontal_line_r_undefined")
    xs = [Fraction(v) for v in (1, 2, 3, 4, 5)]
    r = _r_exact(_stats(xs, [a * v + b for v in xs]))
    if r != _sign(a):
        raise ValueError("on_line_r_mismatch")
    return stated == r, f"所有點在斜率 {_show(a)} 的直線上，完全{'正' if a > 0 else '負'}相關，r={_sign(a)}。"


_CLAIMS: dict[str, Callable[[dict[str, Any]], tuple[bool, str]]] = {
    "points_vs_correlation": _claim_points_vs_correlation,
    "slope_sign": _claim_slope_sign,
    "slope_sigma": _claim_slope_sigma,
    "r_range": _claim_r_range,
    "points_on_line": _claim_points_on_line,
}


def _true_false_answer(claim: Any) -> dict[str, Any]:
    if not isinstance(claim, dict) or claim.get("kind") not in _CLAIMS:
        raise ValueError(f"unknown_claim:{claim.get('kind') if isinstance(claim, dict) else claim}")
    truth, why = _CLAIMS[claim["kind"]](claim)
    return _pack([_choice("A" if truth else "B", TRUE_FALSE, f"{why}故為 {'○' if truth else '×'}。")])


def true_false_bivariate(*, claim: Any, **_: Any) -> dict[str, Any]:
    return _true_false_answer(claim)


def _check_true_false_bivariate(g: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _true_false_answer(g["claim"]) == answer


# --- registry ---------------------------------------------------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "correlation_from_table": (correlation_from_table, _check_correlation_from_table, ("x", "y")),
    "correlation_remove_point": (correlation_remove_point, _check_correlation_remove_point, ("labels", "x", "y")),
    "correlation_change_add_point": (correlation_change_add_point, _check_correlation_change_add_point, ("x", "y", "new_point")),
    "correlation_rescale": (correlation_rescale, _check_correlation_rescale, ("n_questions", "old_per", "new_per", "top", "r")),
    "regression_from_summary": (regression_from_summary, _check_regression_from_summary, ("mx", "my", "sx", "sy", "r")),
    "regression_from_table": (regression_from_table, _check_regression_from_table, ("x", "y", "x0")),
    "regression_rounded_from_table": (regression_rounded_from_table, _check_regression_rounded_from_table, ("x", "y", "r_places", "coef_places")),
    "regression_predict_given_line": (regression_predict_given_line, _check_regression_predict_given_line,
                                      ("x", "y", "eq_places", "m_r", "b_r", "x0", "places")),
    "correlation_from_regression_point": (correlation_from_regression_point, _check_correlation_from_regression_point, ("mx", "my", "sx", "sy", "point")),
    "regression_line_unknown_intercept": (regression_line_unknown_intercept, _check_regression_line_unknown_intercept, ("mx", "my", "sx", "sy", "slope")),
    "regression_statement_selection": (regression_statement_selection, _check_regression_statement_selection,
                                       ("n", "mx", "my", "r", "line_point", "statements")),
    "true_false_bivariate": (true_false_bivariate, _check_true_false_bivariate, ("claim",)),
}

OPERATIONS = tuple(_OPERATIONS)


def build_bivariate_statistics_matrix(
    *, domain_operation: str | None = None, seed: int | None = None, constraints: dict[str, Any] | None = None, **_: Any
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_bivariate_statistics_operation:{operation}")
    solve, _check, required = _OPERATIONS[operation]
    givens = {k: v for k, v in (constraints or {}).items() if k != "skill_id"}
    _require(givens, *required)
    answer = solve(**givens)
    return {
        "domain": DOMAIN_KEY,
        "domain_operation": operation,
        "givens": givens,
        "answer": answer,
        "validation_facts": {"domain_operation": operation, "seed": 0 if seed is None else int(seed)},
    }


def _make_validator(operation: str):
    check = _OPERATIONS[operation][1]

    def validate(matrix: Any) -> bool:
        try:
            facts = matrix.get("validation_facts") or {}
            if matrix.get("domain") != DOMAIN_KEY or matrix.get("domain_operation") != operation or facts.get("domain_operation") != operation:
                return False
            return bool(check(matrix["givens"], matrix["answer"]))
        except Exception:
            return False

    validate.__name__ = f"validate_{operation}_matrix"
    return validate


for _op in _OPERATIONS:
    globals()[f"validate_{_op}_matrix"] = _make_validator(_op)
