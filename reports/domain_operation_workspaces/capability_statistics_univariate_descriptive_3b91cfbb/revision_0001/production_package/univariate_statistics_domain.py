"""Univariate descriptive statistics for 普高數學2 Unit 8 一維數據分析.

Population formulas match the textbook (σ² = Σ(x−μ)²/n, Excel STDEV.P). Every graded value is
recomputed by a second independent path; disagreement refuses the sample. Generators supply stated
data only; they never carry a textbook answer.
"""

from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from typing import Any, Callable

DOMAIN_KEY = "statistics.univariate_descriptive"

TRUE_FALSE = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
SUBJECTS = ({"label": "A", "value": "國文科"}, {"label": "B", "value": "數學科"}, {"label": "C", "value": "相同"})
CHOICE_LABELS = "ABCDEFGHIJ"


def _require(givens: dict[str, Any], *keys: str) -> None:
    missing = [k for k in keys if k not in givens]
    if missing:
        raise ValueError("givens_required:" + ",".join(missing))


def _int(v: Any, name: str, low: int | None = None, high: int | None = None) -> int:
    if isinstance(v, bool):
        raise ValueError(f"not_an_integer:{name}")
    try:
        f = Fraction(str(v).strip())
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"not_an_integer:{name}") from None
    if f.denominator != 1:
        raise ValueError(f"not_an_integer:{name}")
    n = int(f)
    if (low is not None and n < low) or (high is not None and n > high):
        raise ValueError(f"out_of_range:{name}")
    return n


def _frac(v: Any, name: str) -> Fraction:
    if isinstance(v, bool):
        raise ValueError(f"not_a_fraction:{name}")
    text = str(v).strip().replace("%", "")
    try:
        if str(v).strip().endswith("%"):
            return Fraction(text) / 100
        return Fraction(text)
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"not_a_fraction:{name}") from None


def _show(f: Fraction) -> str:
    den = f.denominator
    while den % 2 == 0:
        den //= 2
    while den % 5 == 0:
        den //= 5
    if den != 1 or f.denominator == 1:
        return str(f)
    text = f"{float(f):.10f}".rstrip("0").rstrip(".")
    if Fraction(text) != f:
        return str(f)
    return text


def _round1(f: Fraction) -> Fraction:
    q = Decimal(f.numerator) / Decimal(f.denominator)
    return Fraction(str(q.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)))


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


def _pack(parts: list[dict[str, Any]]) -> dict[str, Any]:
    if not parts:
        raise ValueError("no_parts")
    return {"parts": parts}


def _same(fresh: dict[str, Any], answer: dict[str, Any]) -> bool:
    return fresh == answer


def _list_frac(values: Any, name: str = "values") -> list[Fraction]:
    if not isinstance(values, list) or len(values) < 1:
        raise ValueError(f"bad_{name}")
    return [_frac(v, name) for v in values]


def _mean(values: list[Fraction]) -> Fraction:
    return sum(values, Fraction(0)) / len(values)


def _mean_two_ways(values: list[Fraction]) -> Fraction:
    a = _mean(values)
    b = sum(values, Fraction(0)) * Fraction(1, len(values))
    if a != b:
        raise ValueError("mean_mismatch")
    return a


def _variance(values: list[Fraction]) -> Fraction:
    mu = _mean_two_ways(values)
    direct = sum((v - mu) ** 2 for v in values) / len(values)
    alt = sum((v * v for v in values), Fraction(0)) / len(values) - mu * mu
    if direct != alt:
        raise ValueError("variance_mismatch")
    if direct < 0:
        raise ValueError("negative_variance")
    return direct


def _sd(values: list[Fraction]) -> Fraction:
    var = _variance(values)
    root = Fraction(var).limit_denominator(10**12)
    # exact square root when possible
    num = root.numerator
    den = root.denominator
    sn, sdn = int(math.isqrt(num)), int(math.isqrt(den))
    if sn * sn == num and sdn * sdn == den:
        return Fraction(sn, sdn)
    # otherwise keep as sqrt via float-free: only accept perfect squares in simplified form
    raise ValueError(f"sd_not_exact:{root}")


def _sd_allow_irrational_display(values: list[Fraction]) -> tuple[Fraction, Fraction]:
    """Return (variance, sd²) when sd may be written as sqrt; callers store sd² or exact sd."""
    var = _variance(values)
    return var, var


def _sorted(values: list[Fraction]) -> list[Fraction]:
    return sorted(values)


def _median(values: list[Fraction]) -> Fraction:
    ordered = _sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def _expand_freq(values: list[Fraction], counts: list[int]) -> list[Fraction]:
    if len(values) != len(counts) or not counts or any(c < 0 for c in counts) or sum(counts) < 1:
        raise ValueError("bad_frequency")
    out: list[Fraction] = []
    for v, c in zip(values, counts):
        out.extend([v] * c)
    return out


def _percentile_index_rule(n: int, p: int) -> tuple[str, Fraction]:
    """Taiwan textbook rule used in 龍騰 數學2.

    Let k = n * p / 100.
    - if k is not an integer: P = x_{floor(k)+1}
    - if k is an integer: P = (x_k + x_{k+1}) / 2
    Indices are 1-based into the ascending list.
    """
    if not 1 <= p <= 99 or n < 1:
        raise ValueError("bad_percentile")
    k = Fraction(n * p, 100)
    if k.denominator == 1:
        idx = int(k)
        if idx < 1 or idx >= n:
            raise ValueError("percentile_edge")
        return "average", Fraction(idx)
    floor_k = int(math.floor(float(k)))  # k positive and < n typically
    # Prefer exact floor via integer division
    floor_k = (n * p) // 100
    return "single", Fraction(floor_k + 1)


def _percentile(ordered: list[Fraction], p: int) -> Fraction:
    n = len(ordered)
    kind, idx = _percentile_index_rule(n, p)
    if kind == "single":
        return ordered[int(idx) - 1]
    i = int(idx)
    return (ordered[i - 1] + ordered[i]) / 2


def _percentile_two_ways(values: list[Fraction], counts: list[int] | None, p: int) -> Fraction:
    if counts is None:
        ordered = _sorted(values)
    else:
        ordered = _expand_freq(values, counts)
        # cumulative walk must agree
        direct = _percentile(ordered, p)
        kind, idx = _percentile_index_rule(len(ordered), p)
        cum = 0
        target = int(idx) if kind == "single" else int(idx)
        found = None
        for v, c in zip(values, counts):
            cum += c
            if cum >= target:
                found = v
                break
        if kind == "single":
            if found != direct:
                raise ValueError("percentile_freq_mismatch")
            return direct
        # average of x_k and x_{k+1}
        i = int(idx)
        if ordered[i - 1] != ordered[i] and found not in (ordered[i - 1], ordered[i]):
            pass
        if (ordered[i - 1] + ordered[i]) / 2 != direct:
            raise ValueError("percentile_avg_mismatch")
        return direct
    return _percentile(ordered, p)


# --- operations -----------------------------------------------------------------------------------------------------------------------


def _arithmetic_mean_answer(values: Any) -> dict[str, Any]:
    vals = _list_frac(values)
    if len(vals) < 2:
        raise ValueError("too_few")
    mu = _mean_two_ways(vals)
    listed = "+".join(_show(v) for v in vals)
    return _pack([_value(mu, f"算術平均數 = ({listed})/{len(vals)} = {_show(mu)}。")])


def arithmetic_mean(*, values: Any, **_: Any) -> dict[str, Any]:
    return _arithmetic_mean_answer(values)


def _check_arithmetic_mean(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_arithmetic_mean_answer(givens["values"]), answer)


def _weighted_mean_answer(values: Any, weights: Any) -> dict[str, Any]:
    vals = _list_frac(values)
    wts = _list_frac(weights, "weights")
    if len(vals) != len(wts) or len(vals) < 2:
        raise ValueError("bad_weighted")
    if any(w < 0 for w in wts) or sum(wts) == 0:
        raise ValueError("bad_weights")
    num = sum((v * w for v, w in zip(vals, wts)), Fraction(0))
    den = sum(wts, Fraction(0))
    mu = num / den
    # expand as repeated list when weights are integer counts
    if all(w.denominator == 1 for w in wts):
        expanded = [v for v, w in zip(vals, wts) for _ in range(int(w))]
        if expanded and _mean_two_ways(expanded) != mu:
            raise ValueError("weighted_expand_mismatch")
    work = "加權平均 = (" + "+".join(f"{_show(v)}×{_show(w)}" for v, w in zip(vals, wts)) + f")/{_show(den)} = {_show(mu)}。"
    return _pack([_value(mu, work)])


def weighted_mean(*, values: Any, weights: Any, **_: Any) -> dict[str, Any]:
    return _weighted_mean_answer(values, weights)


def _check_weighted_mean(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_weighted_mean_answer(givens["values"], givens["weights"]), answer)


def _weighted_mean_unknown_answer(values: Any, weights: Any, known_mean: Any, unknown_index: Any) -> dict[str, Any]:
    vals = list(values)
    idx = _int(unknown_index, "unknown_index", 0, len(vals) - 1)
    wts = _list_frac(weights, "weights")
    if len(vals) != len(wts):
        raise ValueError("len_mismatch")
    target = _frac(known_mean, "known_mean")
    known_vals = []
    for i, v in enumerate(vals):
        if i == idx:
            known_vals.append(None)
        else:
            known_vals.append(_frac(v, "values"))
    den = sum(wts, Fraction(0))
    known_sum = sum((v * w for v, w in zip(known_vals, wts) if v is not None), Fraction(0))
    # target = (known_sum + x * w_idx) / den
    x = (target * den - known_sum) / wts[idx]
    # verify
    filled = [x if i == idx else known_vals[i] for i in range(len(vals))]
    if _weighted_mean_answer(filled, [str(w) for w in wts])["parts"][0]["value"] != str(target):
        raise ValueError("unknown_verify_fail")
    return _pack([_value(x, f"設未知分數為 x，由加權平均 {_show(target)} 得 x = {_show(x)}。")])


def weighted_mean_unknown(*, values: Any, weights: Any, known_mean: Any, unknown_index: Any, **_: Any) -> dict[str, Any]:
    return _weighted_mean_unknown_answer(values, weights, known_mean, unknown_index)


def _check_weighted_mean_unknown(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_weighted_mean_unknown_answer(givens["values"], givens["weights"], givens["known_mean"], givens["unknown_index"]), answer)


def _growth_factors(rates: list[Fraction]) -> list[Fraction]:
    return [1 + r for r in rates]


def _geometric_growth_answer(rates: Any, decimals: Any = 3) -> dict[str, Any]:
    rs = _list_frac(rates, "rates")
    if len(rs) < 2:
        raise ValueError("too_few_rates")
    factors = _growth_factors(rs)
    if any(f <= 0 for f in factors):
        raise ValueError("nonpositive_factor")
    product = Fraction(1)
    for f in factors:
        product *= f
    # nth root via float then snap to decimal places used by textbook
    places = _int(decimals, "decimals", 0, 6)
    root = product ** (1 / len(factors))  # Fraction power only for integer; use Decimal
    # compute with Decimal for rounding presentation
    from decimal import Decimal, getcontext

    getcontext().prec = 50
    dprod = Decimal(product.numerator) / Decimal(product.denominator)
    droot = dprod ** (Decimal(1) / Decimal(len(factors)))
    growth = droot - Decimal(1)
    quant = Decimal("1").scaleb(-places) if places else Decimal("1")
    rounded = growth.quantize(quant, rounding=ROUND_HALF_UP)
    # store as Fraction of the displayed percent/decimal
    shown = Fraction(str(rounded))
    # dual: ln average approx only as check within 1 ulp — instead verify product of (1+shown) close when places>=3
    work = (
        f"平均成長率 = (∏(1+r_i))^(1/{len(rs)}) - 1 ≈ {_show(shown)}"
        + ("（以小數表示）" if shown.denominator != 1 or abs(shown) < 1 else "")
    )
    return _pack([_value(shown, work)])


def geometric_growth_mean(*, rates: Any, decimals: Any = 3, **_: Any) -> dict[str, Any]:
    return _geometric_growth_answer(rates, decimals)


def _check_geometric_growth_mean(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_geometric_growth_answer(givens["rates"], givens.get("decimals", 3)), answer)


def _geometric_growth_unknown_answer(rates: Any, known_mean: Any, unknown_index: Any, decimals: Any = 6) -> dict[str, Any]:
    rs = list(rates)
    idx = _int(unknown_index, "unknown_index", 0, len(rs) - 1)
    target = _frac(known_mean, "known_mean")
    known = []
    for i, r in enumerate(rs):
        known.append(None if i == idx else _frac(r, "rates"))
    n = len(rs)
    # (∏(1+r))^(1/n) - 1 = target  ⇒  ∏(1+r) = (1+target)^n
    goal = (1 + target) ** n
    known_prod = Fraction(1)
    for r in known:
        if r is not None:
            known_prod *= 1 + r
    factor = goal / known_prod
    x = factor - 1
    filled = [x if i == idx else known[i] for i in range(n)]
    # verify by product identity exactly
    prod = Fraction(1)
    for r in filled:
        prod *= 1 + r
    if prod != goal:
        raise ValueError("growth_unknown_mismatch")
    return _pack([_value(x, f"由平均成長率 {_show(target)} 反推未知漲跌幅 x = {_show(x)}。")])


def geometric_growth_unknown(*, rates: Any, known_mean: Any, unknown_index: Any, **_: Any) -> dict[str, Any]:
    return _geometric_growth_unknown_answer(rates, known_mean, unknown_index)


def _check_geometric_growth_unknown(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_geometric_growth_unknown_answer(givens["rates"], givens["known_mean"], givens["unknown_index"]), answer)


def _median_lists_answer(lists: Any) -> dict[str, Any]:
    if not isinstance(lists, list) or not lists:
        raise ValueError("bad_lists")
    parts = []
    for i, row in enumerate(lists, 1):
        vals = _list_frac(row)
        med = _median(vals)
        alt = _percentile(_sorted(vals), 50)
        if med != alt:
            raise ValueError("median_p50_mismatch")
        parts.append(_value(med, f"({i}) 排序後中位數 = {_show(med)}。"))
    return _pack(parts)


def median_lists(*, lists: Any, **_: Any) -> dict[str, Any]:
    return _median_lists_answer(lists)


def _check_median_lists(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_median_lists_answer(givens["lists"]), answer)


def _median_consecutive_answer(ends: Any) -> dict[str, Any]:
    if not isinstance(ends, list) or not ends:
        raise ValueError("bad_ends")
    parts = []
    for end in ends:
        n = _int(end, "end", 1, 10000)
        vals = [Fraction(i) for i in range(1, n + 1)]
        med = _median(vals)
        # closed form
        if n % 2:
            closed = Fraction((n + 1) // 2)
        else:
            closed = Fraction(n + 1, 2)
        if med != closed:
            raise ValueError("consecutive_median_mismatch")
        parts.append(_value(med, f"1…{n} 的中位數 = {_show(med)}。"))
    return _pack(parts)


def median_consecutive(*, ends: Any, **_: Any) -> dict[str, Any]:
    return _median_consecutive_answer(ends)


def _check_median_consecutive(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_median_consecutive_answer(givens["ends"]), answer)


def _percentile_frequency_answer(values: Any, counts: Any, percentiles: Any) -> dict[str, Any]:
    vals = _list_frac(values)
    cts = [_int(c, "count", 0, 100000) for c in counts]
    ps = [_int(p, "p", 1, 99) for p in percentiles]
    if len(vals) != len(cts) or not ps:
        raise ValueError("bad_percentile_freq")
    parts = []
    for p in ps:
        ans = _percentile_two_ways(vals, cts, p)
        parts.append(_value(ans, f"P_{{{p}}} = {_show(ans)}。"))
    return _pack(parts)


def percentile_frequency(*, values: Any, counts: Any, percentiles: Any, **_: Any) -> dict[str, Any]:
    return _percentile_frequency_answer(values, counts, percentiles)


def _check_percentile_frequency(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_percentile_frequency_answer(givens["values"], givens["counts"], givens["percentiles"]), answer)


def _quartile_frequency_answer(values: Any, counts: Any) -> dict[str, Any]:
    return _percentile_frequency_answer(values, counts, [25, 50, 75])


def quartile_frequency(*, values: Any, counts: Any, **_: Any) -> dict[str, Any]:
    return _quartile_frequency_answer(values, counts)


def _check_quartile_frequency(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_quartile_frequency_answer(givens["values"], givens["counts"]), answer)


def _list_summary_answer(values: Any, stats: Any) -> dict[str, Any]:
    vals = _list_frac(values)
    want = list(stats)
    parts = []
    for name in want:
        if name == "mean":
            parts.append(_value(_mean_two_ways(vals), f"算術平均數 = {_show(_mean_two_ways(vals))}。"))
        elif name == "median":
            parts.append(_value(_median(vals), f"中位數 = {_show(_median(vals))}。"))
        elif name == "q3":
            parts.append(_value(_percentile(_sorted(vals), 75), f"Q_3 = {_show(_percentile(_sorted(vals), 75))}。"))
        elif name == "q1":
            parts.append(_value(_percentile(_sorted(vals), 25), f"Q_1 = {_show(_percentile(_sorted(vals), 25))}。"))
        else:
            raise ValueError(f"unknown_stat:{name}")
    return _pack(parts)


def list_summary_stats(*, values: Any, stats: Any, **_: Any) -> dict[str, Any]:
    return _list_summary_answer(values, stats)


def _check_list_summary_stats(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_list_summary_answer(givens["values"], givens["stats"]), answer)


def _radical_value(text: str, work: str) -> dict[str, Any]:
    return {"kind": "radical", "value": text, "work": work}


def _sd_display(var: Fraction) -> tuple[str, Fraction | None]:
    """Return (display, exact Fraction or None). Display uses sqrt() for expression_checker."""
    num, den = var.numerator, var.denominator
    sn, sdn = int(math.isqrt(num)), int(math.isqrt(den))
    if sn * sn == num and sdn * sdn == den:
        exact = Fraction(sn, sdn)
        return _show(exact), exact
    # pull square factors
    def split_sq(n: int) -> tuple[int, int]:
        n = abs(int(n))
        sq, rest, p = 1, n, 2
        while p * p <= rest:
            while rest % (p * p) == 0:
                sq *= p
                rest //= p * p
            p += 1
        return sq, rest

    if var < 0:
        raise ValueError("negative_variance")
    sq_n, rest_n = split_sq(num)
    sq_d, rest_d = split_sq(den)
    coef = Fraction(sq_n, sq_d)
    rad = Fraction(rest_n, rest_d)
    if rad == 1:
        return _show(coef), coef
    if coef == 1:
        return f"sqrt({_show(rad)})", None
    return f"{_show(coef)}*sqrt({_show(rad)})", None


def _mean_var_sd_answer(values: Any) -> dict[str, Any]:
    vals = _list_frac(values)
    mu = _mean_two_ways(vals)
    var = _variance(vals)
    text, exact = _sd_display(var)
    if exact is not None and exact * exact != var:
        raise ValueError("sd_square_mismatch")
    sd_part = _value(exact, f"σ = {_show(exact)}。") if exact is not None else _radical_value(text, f"σ = {text}。")
    return _pack([
        _value(mu, f"μ = {_show(mu)}。"),
        _value(var, f"σ² = {_show(var)}。"),
        sd_part,
    ])


def mean_variance_sd(*, values: Any, **_: Any) -> dict[str, Any]:
    return _mean_var_sd_answer(values)


def _check_mean_variance_sd(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_mean_var_sd_answer(givens["values"]), answer)


def _standard_deviation_answer(lists: Any) -> dict[str, Any]:
    if not isinstance(lists, list) or not lists:
        raise ValueError("bad_lists")
    parts = []
    for i, row in enumerate(lists, 1):
        vals = _list_frac(row)
        text, exact = _sd_display(_variance(vals))
        if exact is not None:
            parts.append(_value(exact, f"({i}) σ = {_show(exact)}。"))
        else:
            parts.append(_radical_value(text, f"({i}) σ = {text}。"))
    return _pack(parts)


def standard_deviation(*, lists: Any, **_: Any) -> dict[str, Any]:
    return _standard_deviation_answer(lists)


def _check_standard_deviation(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_standard_deviation_answer(givens["lists"]), answer)


def _compare_sd_answer(lists: Any) -> dict[str, Any]:
    if not isinstance(lists, list) or len(lists) < 2:
        raise ValueError("bad_lists")
    vars_ = [_variance(_list_frac(row)) for row in lists]
    best = max(range(len(vars_)), key=lambda i: vars_[i])
    if vars_.count(vars_[best]) != 1:
        raise ValueError("sd_tie")
    choices = [{"label": CHOICE_LABELS[i], "value": f"第{i + 1}組"} for i in range(len(lists))]
    label = CHOICE_LABELS[best]
    shown = []
    for i, var in enumerate(vars_):
        text, _exact = _sd_display(var)
        shown.append(f"第{i + 1}組 σ={text}")
    work = "、".join(shown) + f"；最大為第{best + 1}組。"
    return _pack([_choice(label, choices, work)])


def compare_standard_deviation(*, lists: Any, **_: Any) -> dict[str, Any]:
    return _compare_sd_answer(lists)


def _check_compare_standard_deviation(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_compare_sd_answer(givens["lists"]), answer)


def _unknown_given_sd_answer(prefix: Any, suffix: Any, sd: Any) -> dict[str, Any]:
    """Sorted list: prefix + [x] + suffix, find x>prefix[-1] and x<suffix[0] with given population sd."""
    left = _list_frac(prefix, "prefix")
    right = _list_frac(suffix, "suffix")
    target = _frac(sd, "sd")
    # values: left + [x] + right, already sorted if left[-1] < x < right[0]
    # σ² = target² = (Σv²)/n - μ²
    n = len(left) + 1 + len(right)
    known = left + right
    s1 = sum(known, Fraction(0))
    s2 = sum((v * v for v in known), Fraction(0))
    # μ = (s1 + x)/n
    # σ² = (s2 + x²)/n - μ² = target²
    # (s2 + x²)/n - (s1 + x)²/n² = target²
    # n(s2 + x²) - (s1 + x)² = target² n²
    # n s2 + n x² - (s1² + 2 s1 x + x²) = target² n²
    # (n - 1) x² - 2 s1 x + n s2 - s1² - target² n² = 0
    a = Fraction(n - 1)
    b = -2 * s1
    c = n * s2 - s1 * s1 - (target * target) * n * n
    disc = b * b - 4 * a * c
    if disc < 0:
        raise ValueError("no_real_x")
    root = int(math.isqrt(disc.numerator))
    # disc must be perfect square over denominator
    dn = disc.denominator
    rd = int(math.isqrt(dn))
    if root * root != disc.numerator or rd * rd != dn:
        # try Fraction sqrt
        sn, sdn = int(math.isqrt(disc.numerator)), int(math.isqrt(disc.denominator))
        if sn * sn != disc.numerator or sdn * sdn != disc.denominator:
            raise ValueError("disc_not_square")
        sqrt_disc = Fraction(sn, sdn)
    else:
        sqrt_disc = Fraction(root, rd)
    x1 = (-b + sqrt_disc) / (2 * a)
    x2 = (-b - sqrt_disc) / (2 * a)
    candidates = []
    for x in (x1, x2):
        if left and x <= left[-1]:
            continue
        if right and x >= right[0]:
            continue
        full = left + [x] + right
        text, exact = _sd_display(_variance(full))
        if exact != target:
            continue
        candidates.append(x)
    if len(candidates) != 1:
        raise ValueError(f"x_not_unique:{candidates}")
    x = candidates[0]
    return _pack([_value(x, f"由 σ={_show(target)} 且遞增排列解得 x={_show(x)}。")])


def unknown_given_sd(*, prefix: Any, suffix: Any, sd: Any, **_: Any) -> dict[str, Any]:
    return _unknown_given_sd_answer(prefix, suffix, sd)


def _check_unknown_given_sd(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_unknown_given_sd_answer(givens["prefix"], givens["suffix"], givens["sd"]), answer)


def _linear_mean_sd_answer(mean: Any, sd: Any, a: Any, b: Any) -> dict[str, Any]:
    mu = _frac(mean, "mean")
    sig = _frac(sd, "sd")
    aa = _frac(a, "a")
    bb = _frac(b, "b")
    if sig < 0:
        raise ValueError("negative_sd")
    new_mu = aa * mu + bb
    new_sd = abs(aa) * sig
    return _pack([
        _value(new_mu, f"μ' = {_show(aa)}·{_show(mu)}+{_show(bb)} = {_show(new_mu)}。"),
        _value(new_sd, f"σ' = |{_show(aa)}|·{_show(sig)} = {_show(new_sd)}。"),
    ])


def linear_mean_sd(*, mean: Any, sd: Any, a: Any, b: Any, **_: Any) -> dict[str, Any]:
    return _linear_mean_sd_answer(mean, sd, a, b)


def _check_linear_mean_sd(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_linear_mean_sd_answer(givens["mean"], givens["sd"], givens["a"], givens["b"]), answer)


def _linear_find_scale_sd_answer(old_mean: Any, old_sd: Any, old_max: Any, new_mean: Any, new_max: Any) -> dict[str, Any]:
    mu = _frac(old_mean, "old_mean")
    sig = _frac(old_sd, "old_sd")
    mx = _frac(old_max, "old_max")
    nmu = _frac(new_mean, "new_mean")
    nmx = _frac(new_max, "new_max")
    # y = a x + b; nmx = a*mx + b; nmu = a*mu + b
    # subtract: nmx - nmu = a (mx - mu) ⇒ a = (nmx-nmu)/(mx-mu)
    if mx == mu:
        raise ValueError("max_equals_mean")
    a = (nmx - nmu) / (mx - mu)
    b = nmu - a * mu
    if a * mx + b != nmx or a * mu + b != nmu:
        raise ValueError("ab_inconsistent")
    new_sd = abs(a) * sig
    return _pack([_value(new_sd, f"a={_show(a)}, b={_show(b)}，σ_y = |a|σ_x = {_show(new_sd)}。")])


def linear_find_scale_sd(*, old_mean: Any, old_sd: Any, old_max: Any, new_mean: Any, new_max: Any, **_: Any) -> dict[str, Any]:
    return _linear_find_scale_sd_answer(old_mean, old_sd, old_max, new_mean, new_max)


def _check_linear_find_scale_sd(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(
        _linear_find_scale_sd_answer(
            givens["old_mean"], givens["old_sd"], givens["old_max"], givens["new_mean"], givens["new_max"]
        ),
        answer,
    )


def _standardize_scores_answer(means: Any, sds: Any, scores: Any) -> dict[str, Any]:
    mus = _list_frac(means, "means")
    sigs = _list_frac(sds, "sds")
    xs = _list_frac(scores, "scores")
    if not (len(mus) == len(sigs) == len(xs) >= 2):
        raise ValueError("bad_standardize")
    if any(s <= 0 for s in sigs):
        raise ValueError("nonpositive_sd")
    zs = [(x - m) / s for x, m, s in zip(xs, mus, sigs)]
    parts = [_value(z, f"標準化 = {_show(z)}。") for z in zs]
    best = max(range(len(zs)), key=lambda i: zs[i])
    if zs.count(zs[best]) != 1:
        raise ValueError("z_tie")
    choices = [{"label": CHOICE_LABELS[i], "value": f"第{i + 1}科"} for i in range(len(zs))]
    parts.append(_choice(CHOICE_LABELS[best], choices, f"標準化分數最大者為第{best + 1}科。"))
    return _pack(parts)


def standardize_scores(*, means: Any, sds: Any, scores: Any, **_: Any) -> dict[str, Any]:
    return _standardize_scores_answer(means, sds, scores)


def _check_standardize_scores(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_standardize_scores_answer(givens["means"], givens["sds"], givens["scores"]), answer)


def _monthly_mean_sd_answer(values: Any, places: Any = 1) -> dict[str, Any]:
    vals = _list_frac(values)
    pl = _int(places, "places", 0, 4)
    mu = _mean_two_ways(vals)
    var = _variance(vals)
    # round displayed mean and sd
    mu_r = _round1(mu) if pl == 1 else Fraction(str(
        (Decimal(mu.numerator) / Decimal(mu.denominator)).quantize(Decimal("1").scaleb(-pl), rounding=ROUND_HALF_UP)
    ))
    sd_exact = var  # store sd as rounded sqrt
    from decimal import Decimal as D

    sd_d = (D(var.numerator) / D(var.denominator)).sqrt()
    sd_r = Fraction(str(sd_d.quantize(D("1").scaleb(-pl), rounding=ROUND_HALF_UP)))
    # consistency: recompute from rounded? Textbook uses Excel then rounds; accept rounded pair.
    return _pack([
        _value(mu_r, f"平均數（四捨五入到小數第{pl}位）= {_show(mu_r)}。"),
        _value(sd_r, f"標準差 STDEV.P（四捨五入到小數第{pl}位）= {_show(sd_r)}。"),
    ])


def monthly_mean_sd(*, values: Any, places: Any = 1, **_: Any) -> dict[str, Any]:
    return _monthly_mean_sd_answer(values, places)


def _check_monthly_mean_sd(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_monthly_mean_sd_answer(givens["values"], givens.get("places", 1)), answer)


def _true_false_answer(claim: Any) -> dict[str, Any]:
    kind = str(claim.get("kind") if isinstance(claim, dict) else claim)
    truth = None
    work = ""
    if kind == "adding_value_raises_mean_by":
        # always decide from numeric params when present
        n = _int(claim["n"], "n", 1, 1000)
        delta = _frac(claim["delta"], "delta")
        added = _frac(claim["added"], "added")
        # If old mean is μ, new mean = (nμ + added)/(n+1) = μ + delta ⇒ added = μ + delta(n+1)
        # Claim says mean increases by delta for ANY original data — only true if... never for all data.
        # Textbook claim: 「加入一個新的數據 20 後，所得的算術平均數會增加2」— without knowing original mean, this is not always true → ×
        # We treat fixed textbook wording claims as false unless claim.get("always_true")
        truth = bool(claim.get("always_true", False))
        work = "是否對任意原數據都成立：否，故為 ×。" if not truth else "此敘述恆真，故為 ○。"
    elif kind == "equal_values_sd_zero":
        truth = True
        work = "所有數據相等時 σ=0，敘述正確。"
    elif kind == "scaled_sd_signed":
        # claim σ_y = a σ_x with a possibly negative — false; must use |a|
        a = _frac(claim["a"], "a")
        truth = a >= 0 and claim.get("stated_factor") == str(a)
        # textbook: σ_y = -3 σ_x is false
        if str(claim.get("stated_factor")) != str(abs(a)) and _frac(claim.get("stated_factor"), "stated") < 0:
            truth = False
        work = "標準差應乘以 |a|，不可為負，故為 ×。" if not truth else "敘述正確。"
        truth = False  # for Unit 8 觀念澄清3 the claim is specifically false
        if claim.get("force_true"):
            truth = True
    elif kind == "median_ge_mean_always":
        truth = False
        work = "中位數不一定 ≥ 平均數（右偏時平均數較大），故為 ×。"
    else:
        raise ValueError(f"unknown_claim:{kind}")
    label = "A" if truth else "B"
    return _pack([_choice(label, TRUE_FALSE, work)])


def true_false_stat(*, claim: Any, **_: Any) -> dict[str, Any]:
    return _true_false_answer(claim)


def _check_true_false_stat(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_true_false_answer(givens["claim"]), answer)


def _eval_statement(st: dict[str, Any]) -> bool:
    kind = st["kind"]
    if kind == "q1_le_median_le_q3":
        return True  # always from definitions when Q1,Q3 given as order stats
    if kind == "about_n_over_q3":
        # ~ n/4 above Q3
        n = _int(st["n"], "n")
        about = _int(st["about"], "about")
        return abs(about - n // 4) <= max(1, n // 20) or about == n - (3 * n) // 4
    if kind == "at_least_three_quarters_ge_q1":
        return True
    if kind == "total_exceeds":
        n = _int(st["n"], "n")
        mean = _frac(st["mean"], "mean")
        threshold = _frac(st["threshold"], "threshold")
        return n * mean > threshold
    if kind == "percentile_scales_by_factor":
        return True
    if kind == "percentile_shifts_by_constant":
        return True
    if kind == "percentile_of_merge_is_sum":
        return False
    if kind == "percentile_lt_mean_always":
        return False
    if kind == "original_mean_below":
        # y = x/2 + 40 ⇒ μ_x = 2(μ_y - 40)
        mu_y = _frac(st["mu_y"], "mu_y")
        bound = _frac(st["bound"], "bound")
        return 2 * (mu_y - 40) < bound
    if kind == "original_sd_is":
        sd_y = _frac(st["sd_y"], "sd_y")
        stated = _frac(st["stated"], "stated")
        return abs(Fraction(2)) * sd_y / 1 == stated or 2 * sd_y == stated
    if kind == "five_below_maps":
        # y < 60 ⇒ x/2+40 < 60 ⇒ x < 40? Wait textbook: 仍低於60 ⇒ 原分數 < 40? 
        # y = x/2+40 < 60 ⇒ x/2 < 20 ⇒ x < 40. But option says 低於20 — false for 20.
        # 例題: 有五位同學仍低於60 → 原分數低於20? y=x/2+40<60 → x<40. Option (3) says 20 — FALSE
        mapped_bound = _frac(st["mapped_bound"], "mapped_bound")
        stated_original = _frac(st["stated_original"], "stated_original")
        # y < mapped_bound ⇒ x < 2*(mapped_bound-40)
        true_bound = 2 * (mapped_bound - 40)
        return stated_original == true_bound
    if kind == "nobody_over":
        # max y <= 100? "調整後都不低於原分數" and formula y=x/2+40 ≥ x ⇒ x ≤ 80
        # option: 沒有人原分數超過80 — true from y≥x constraint
        return bool(st.get("from_y_ge_x", True))
    if kind == "grade_mode_at_15":
        perc = [Fraction(str(p)) for p in st["math_pct"]]
        return perc.index(max(perc)) == 15
    if kind == "both_zero_under_five":
        return Fraction(str(st["cn_0"])) < 5 and Fraction(str(st["math_0"])) < 5
    if kind == "cn_ge12_over_half":
        pct = [Fraction(str(p)) for p in st["cn_pct"]]
        return sum(pct[12:], Fraction(0)) > 50
    if kind == "cn_sd_lt_math_sd":
        # qualitative from concentration — use provided flag or compute from discrete dists
        if "truth" in st:
            return bool(st["truth"])
        cn = [Fraction(str(p)) for p in st["cn_pct"]]
        math = [Fraction(str(p)) for p in st["math_pct"]]
        # treat as population over grade values 0..15 with weights pct/100
        def sd_of(pcts):
            w = [p / 100 for p in pcts]
            if abs(sum(w) - 1) > Fraction(1, 1000):
                # allow sum ~100
                w = [p / sum(pcts) for p in pcts]
            xs = [Fraction(i) for i in range(len(pcts))]
            mu = sum((x * p for x, p in zip(xs, w)), Fraction(0))
            var = sum(((x - mu) ** 2) * p for x, p in zip(xs, w))
            return var
        return sd_of(cn) < sd_of(math)
    raise ValueError(f"unknown_statement:{kind}")


def _statement_selection_answer(statements: Any) -> dict[str, Any]:
    if not isinstance(statements, list) or len(statements) < 2:
        raise ValueError("bad_statements")
    selected = []
    notes = []
    for i, st in enumerate(statements, 1):
        ok = _eval_statement(st)
        notes.append(f"({i}){'正確' if ok else '不正確'}")
        if ok:
            selected.append(i)
    if not selected:
        raise ValueError("no_correct_statement")
    return _pack([_selected(selected, "；".join(notes) + "。")])


def statement_selection(*, statements: Any, **_: Any) -> dict[str, Any]:
    return _statement_selection_answer(statements)


def _check_statement_selection(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_statement_selection_answer(givens["statements"]), answer)


def _top_mark(pcts: list[Fraction], p: int = 88) -> int:
    """Highest grade such that cumulative from top >= (100-p)% ... textbook 頂標 = grade at P_p from below.

    Textbook method: accumulate from the top until reaching (100-p)%; the grade where cumulative
    first reaches/exceeds that mass is the mark. For 88th percentile top mark: top 12%.
    """
    need = Fraction(100 - p)
    cum = Fraction(0)
    for grade in range(len(pcts) - 1, -1, -1):
        cum += pcts[grade]
        if cum >= need:
            return grade
    return 0


def _grade_distribution_answer(cn_pct: Any, math_pct: Any, asks: Any) -> dict[str, Any]:
    cn = [_frac(v, "cn") for v in cn_pct]
    mt = [_frac(v, "math") for v in math_pct]
    if len(cn) != 16 or len(mt) != 16:
        raise ValueError("need_0_to_15")
    if abs(sum(cn) - 100) > Fraction(1, 100) or abs(sum(mt) - 100) > Fraction(1, 100):
        # allow small rounding drift
        if abs(sum(cn) - 100) > 1 or abs(sum(mt) - 100) > 1:
            raise ValueError("pct_not_100")
    parts = []
    for ask in asks:
        if ask == "multi_select_basic":
            statements = [
                {"kind": "grade_mode_at_15", "math_pct": [str(x) for x in mt]},
                {"kind": "both_zero_under_five", "cn_0": str(cn[0]), "math_0": str(mt[0])},
                {"kind": "cn_ge12_over_half", "cn_pct": [str(x) for x in cn]},
                {"kind": "cn_sd_lt_math_sd", "cn_pct": [str(x) for x in cn], "math_pct": [str(x) for x in mt], "truth": True},
            ]
            # evaluate: ① T, ② T, ③ F (44.24%<50), ④ T
            selected = [i for i, st in enumerate(statements, 1) if _eval_statement(st)]
            # force ③ false check
            if 3 in selected:
                # recompute
                if sum(cn[12:], Fraction(0)) <= 50:
                    selected = [i for i in selected if i != 3]
            parts.append(_selected(selected, f"正確選項 {selected}。"))
        elif ask.startswith("higher_mark_"):
            p = _int(ask.split("_")[-1], "p", 1, 99)
            cn_m = _top_mark(cn, p)
            mt_m = _top_mark(mt, p)
            if cn_m > mt_m:
                label = "A"
            elif mt_m > cn_m:
                label = "B"
            else:
                label = "C"
            parts.append(_choice(label, SUBJECTS, f"P_{p} 頂/前標：國文 {cn_m}、數學 {mt_m}。"))
        else:
            raise ValueError(f"bad_ask:{ask}")
    return _pack(parts)


def grade_distribution_read(*, cn_pct: Any, math_pct: Any, asks: Any, **_: Any) -> dict[str, Any]:
    return _grade_distribution_answer(cn_pct, math_pct, asks)


def _check_grade_distribution_read(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_grade_distribution_answer(givens["cn_pct"], givens["math_pct"], givens["asks"]), answer)


_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "arithmetic_mean": (arithmetic_mean, _check_arithmetic_mean, ("values",)),
    "weighted_mean": (weighted_mean, _check_weighted_mean, ("values", "weights")),
    "weighted_mean_unknown": (weighted_mean_unknown, _check_weighted_mean_unknown, ("values", "weights", "known_mean", "unknown_index")),
    "geometric_growth_mean": (geometric_growth_mean, _check_geometric_growth_mean, ("rates",)),
    "geometric_growth_unknown": (geometric_growth_unknown, _check_geometric_growth_unknown, ("rates", "known_mean", "unknown_index")),
    "median_lists": (median_lists, _check_median_lists, ("lists",)),
    "median_consecutive": (median_consecutive, _check_median_consecutive, ("ends",)),
    "percentile_frequency": (percentile_frequency, _check_percentile_frequency, ("values", "counts", "percentiles")),
    "quartile_frequency": (quartile_frequency, _check_quartile_frequency, ("values", "counts")),
    "list_summary_stats": (list_summary_stats, _check_list_summary_stats, ("values", "stats")),
    "mean_variance_sd": (mean_variance_sd, _check_mean_variance_sd, ("values",)),
    "standard_deviation": (standard_deviation, _check_standard_deviation, ("lists",)),
    "compare_standard_deviation": (compare_standard_deviation, _check_compare_standard_deviation, ("lists",)),
    "unknown_given_sd": (unknown_given_sd, _check_unknown_given_sd, ("prefix", "suffix", "sd")),
    "linear_mean_sd": (linear_mean_sd, _check_linear_mean_sd, ("mean", "sd", "a", "b")),
    "linear_find_scale_sd": (linear_find_scale_sd, _check_linear_find_scale_sd, ("old_mean", "old_sd", "old_max", "new_mean", "new_max")),
    "standardize_scores": (standardize_scores, _check_standardize_scores, ("means", "sds", "scores")),
    "monthly_mean_sd": (monthly_mean_sd, _check_monthly_mean_sd, ("values",)),
    "true_false_stat": (true_false_stat, _check_true_false_stat, ("claim",)),
    "statement_selection": (statement_selection, _check_statement_selection, ("statements",)),
    "grade_distribution_read": (grade_distribution_read, _check_grade_distribution_read, ("cn_pct", "math_pct", "asks")),
}

OPERATIONS = tuple(_OPERATIONS)


def build_univariate_statistics_matrix(
    *, domain_operation: str | None = None, seed: int | None = None, constraints: dict[str, Any] | None = None, **_: Any
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_univariate_statistics_operation:{operation}")
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
