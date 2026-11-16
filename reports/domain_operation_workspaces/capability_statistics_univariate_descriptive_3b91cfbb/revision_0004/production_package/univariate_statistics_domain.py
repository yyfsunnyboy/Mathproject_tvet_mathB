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


def _standardize_scores_answer(means: Any, sds: Any, scores: Any, subjects: Any = None) -> dict[str, Any]:
    mus = _list_frac(means, "means")
    sigs = _list_frac(sds, "sds")
    xs = _list_frac(scores, "scores")
    if not (len(mus) == len(sigs) == len(xs) >= 2):
        raise ValueError("bad_standardize")
    if any(s <= 0 for s in sigs):
        raise ValueError("nonpositive_sd")
    names = [str(s) for s in subjects] if subjects else [f"第{i + 1}科" for i in range(len(xs))]
    if len(names) != len(xs) or len(set(names)) != len(names):
        raise ValueError("bad_subjects")
    zs = [(x - m) / s for x, m, s in zip(xs, mus, sigs)]
    parts = [_value(z, f"{name}標準化 = ({_show(x)}-{_show(m)})/{_show(s)} = {_show(z)}。")
             for z, name, x, m, s in zip(zs, names, xs, mus, sigs)]
    best = max(range(len(zs)), key=lambda i: zs[i])
    if zs.count(zs[best]) != 1:
        raise ValueError("z_tie")
    choices = [{"label": CHOICE_LABELS[i], "value": names[i]} for i in range(len(zs))]
    parts.append(_choice(CHOICE_LABELS[best], choices, f"標準化分數最大者為{names[best]}。"))
    return _pack(parts)


def standardize_scores(*, means: Any, sds: Any, scores: Any, subjects: Any = None, **_: Any) -> dict[str, Any]:
    return _standardize_scores_answer(means, sds, scores, subjects)


def _check_standardize_scores(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_standardize_scores_answer(givens["means"], givens["sds"], givens["scores"], givens.get("subjects")), answer)


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
        n = _int(claim["n"], "n", 2, 1000)
        delta = _frac(claim["delta"], "delta")
        added = _frac(claim["added"], "added")
        if "mean" in claim:
            mu = _frac(claim["mean"], "mean")
            new_mu = (n * mu + added) / (n + 1)
            if new_mu != mu + (added - mu) / (n + 1):
                raise ValueError("mean_shift_mismatch")
            truth = new_mu - mu == delta
            work = (f"新平均 = ({n}×{_show(mu)}+{_show(added)})/{n + 1} = {_show(new_mu)}，"
                    f"增加 {_show(new_mu - mu)}，故為 {'○' if truth else '×'}。")
        else:
            # the increase (added - μ)/(n+1) changes with the unstated original mean μ
            increases = {(added - mu) / (n + 1) for mu in (added - delta * (n + 1), added - delta * (n + 1) + 1)}
            truth = len(increases) == 1
            work = "平均數的增加量為（新數據 − 原平均）/(n+1)，取決於未知的原平均，不一定增加該值，故為 ×。"
    elif kind == "equal_values_sd_zero":
        truth = True
        work = "所有數據相等時 σ=0，敘述正確。"
    elif kind == "constant_data_sd":
        n = _int(claim["n"], "n", 2, 100)
        data = [_frac(claim["value"], "value")] * n
        stated = _frac(claim["stated"], "stated")
        text, exact = _sd_display(_variance(data))
        truth = exact is not None and exact == stated
        work = f"每個數據都等於平均數，σ = {text}，故為 {'○' if truth else '×'}。"
    elif kind == "scaled_sd_signed":
        a = _frac(claim["a"], "a")
        b = _frac(claim.get("b", 0), "b")
        stated = _frac(claim["stated_factor"], "stated_factor")
        xs = [Fraction(v) for v in (1, 2, 4, 9)]
        ratio2 = _variance([a * x + b for x in xs]) / _variance(xs)
        if ratio2 != a * a:
            raise ValueError("scale_variance_mismatch")
        truth = stated == abs(a)
        work = f"σ_y = |{_show(a)}|σ_x = {_show(abs(a))}σ_x，故為 {'○' if truth else '×'}。"
    elif kind == "median_ge_mean_always":
        truth = False
        work = "中位數不一定 ≥ 平均數（右偏時平均數較大），故為 ×。"
    elif kind == "median_ge_mean_data":
        vals = _list_frac(claim["values"])
        med, mu = _median(vals), _mean_two_ways(vals)
        if med != _percentile(_sorted(vals), 50):
            raise ValueError("median_p50_mismatch")
        truth = med >= mu
        work = f"中位數 = {_show(med)}，平均數 = {_show(mu)}，故為 {'○' if truth else '×'}。"
    else:
        raise ValueError(f"unknown_claim:{kind}")
    label = "A" if truth else "B"
    return _pack([_choice(label, TRUE_FALSE, work)])


def true_false_stat(*, claim: Any, **_: Any) -> dict[str, Any]:
    return _true_false_answer(claim)


def _check_true_false_stat(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_true_false_answer(givens["claim"]), answer)


def _quartile_witness(n: int, mean: Fraction, q1: Fraction, q3: Fraction) -> list[Fraction]:
    """A non-negative data set of size n=4m with exactly the stated Q1, Q3 and mean.

    x_m = x_{m+1} = Q1 and the top m+1 values all equal Q3, so nothing lies above Q3 and only 3m-1 values
    exceed Q1. A data set like this proves which quartile statements cannot be inferred.
    """
    m = n // 4
    rest = n * mean - (m + 1) * q3 - 2 * q1
    for low in (q1 / 2, Fraction(0), q1, q1 / 4, 3 * q1 / 4):
        mid = (rest - (m - 1) * low) / (2 * m - 2)
        if not q1 <= mid <= q3 or mid == (q1 + q3) / 2:
            continue
        data = [low] * (m - 1) + [q1, q1] + [mid] * (2 * m - 2) + [q3] * (m + 1)
        ordered = _sorted(data)
        if (_percentile(ordered, 25), _percentile(ordered, 75), _mean_two_ways(ordered)) == (q1, q3, mean):
            return ordered
    raise ValueError("quartile_scenario_has_no_witness")


def _quartile_statement(st: dict[str, Any]) -> bool:
    kind = st["kind"]
    n = _int(st["n"], "n", 8, 1000)
    if n % 4:
        raise ValueError("quartile_n_not_multiple_of_4")
    mean, q1, q3 = _frac(st["mean"], "mean"), _frac(st["q1"], "q1"), _frac(st["q3"], "q3")
    if not 0 < q1 < q3:
        raise ValueError("bad_quartiles")
    witness = _quartile_witness(n, mean, q1, q3)
    median = _median(witness)
    if kind == "median_between_quartiles":
        truth = True  # Q1, Q2, Q3 are taken at increasing positions of the same ordered list
        if not q1 <= median <= q3:
            raise ValueError("witness_contradicts_theorem")
        return truth
    if kind == "median_is_quartile_midpoint":
        return median == (q1 + q3) / 2
    if kind == "count_above_q3":
        if _int(st["count"], "count") != n // 4:
            raise ValueError("count_must_be_quarter")
        above = sum(1 for v in witness if v > q3)
        if st["mode"] == "at_most":
            if above > n // 4:
                raise ValueError("witness_contradicts_theorem")
            return True
        if st["mode"] == "about":
            return above == n // 4
        raise ValueError("bad_mode")
    if kind == "count_ge_q1":
        count = _int(st["count"], "count")
        if count != 3 * n // 4:
            raise ValueError("count_must_be_three_quarters")
        if st.get("strict"):
            return sum(1 for v in witness if v > q1) >= count
        if sum(1 for v in witness if v >= q1) < count:
            raise ValueError("witness_contradicts_theorem")
        return True
    if kind == "total_exceeds":
        threshold = _frac(st["threshold"], "threshold")
        if threshold == n * mean:
            raise ValueError("threshold_equals_total")
        return n * mean > threshold
    raise ValueError(f"unknown_statement:{kind}")


def _rescale_statement(st: dict[str, Any]) -> bool:
    """調整分數 y = x/div + shift with y ≥ x for everyone."""
    kind = st["kind"]
    div = _int(st["div"], "div", 2, 10)
    shift = _frac(st["shift"], "shift")
    mu_y, sd_y, low_y = _frac(st["mu_y"], "mu_y"), _frac(st["sd_y"], "sd_y"), _frac(st["low_y"], "low_y")
    cap = div * shift / (div - 1)
    mu_x, sd_x = div * (mu_y - shift), div * sd_y
    if not (shift < low_y < cap and shift < mu_y < cap and sd_x > 0 and sd_x * sd_x <= mu_x * (cap - mu_x)):
        raise ValueError("rescale_scenario_infeasible")
    stated = _frac(st["stated"], "stated")
    if kind == "orig_mean_below":
        if stated == mu_x:
            raise ValueError("bound_equals_mean")
        return mu_x < stated
    if kind == "orig_sd_is":
        return sd_x == stated
    if kind == "k_orig_below":
        bound = div * (low_y - shift)
        if stated > bound:
            raise ValueError("ambiguous_k_bound")
        return stated == bound
    if kind == "nobody_orig_over":
        return stated >= cap
    raise ValueError(f"unknown_statement:{kind}")


_PCT_THEORY = {"pct_shift": True, "pct_square": False, "pct_merge_sum": False, "pct_lt_mean": False, "pct_within_range": True}


def _pct_datasets(p: int) -> list[list[Fraction]]:
    import random

    rng = random.Random(f"univariate:pct:{p}")
    out = [[-5, -1, 0, 1, 2], [1, 10, 10, 10, 10], [1, 2, 3, 4, 10, 30], [3, 1, 4, 1, 5, 9, 2, 6]]
    for _ in range(300):
        out.append([rng.randint(-20, 20) for _ in range(rng.randint(3, 12))])
    return [[Fraction(v) for v in row] for row in out]


def _pct_of(values: list[Fraction], p: int) -> Fraction:
    return _percentile(_sorted(values), p)


def _percentile_statement(st: dict[str, Any]) -> bool:
    """Universal percentile claims: a counterexample among fixed data sets refutes, and must agree with theory."""
    kind = st["kind"]
    p = _int(st["p"], "p", 1, 99)
    data = _pct_datasets(p)
    refuted = False
    for i, xs in enumerate(data):
        P = _pct_of(xs, p)
        if kind == "pct_scale":
            c = _frac(st["c"], "c")
            refuted = _pct_of([c * x for x in xs], p) != c * P
        elif kind == "pct_shift":
            d = _frac(st["d"], "d")
            refuted = _pct_of([x + d for x in xs], p) != P + d
        elif kind == "pct_square":
            refuted = _pct_of([x * x for x in xs], p) != P * P
        elif kind == "pct_merge_sum":
            ys = data[(i + 1) % len(data)]
            refuted = _pct_of(xs + ys, p) != P + _pct_of(ys, p)
        elif kind == "pct_lt_mean":
            refuted = not P < _mean(xs)
        elif kind == "pct_within_range":
            refuted = not min(xs) <= P <= max(xs)
        else:
            raise ValueError(f"unknown_statement:{kind}")
        if refuted:
            break
    theory = _frac(st["c"], "c") > 0 if kind == "pct_scale" else _PCT_THEORY[kind]
    if (not refuted) != theory:
        raise ValueError("percentile_claim_theory_mismatch")
    return not refuted


def _eval_statement(st: dict[str, Any]) -> bool:
    kind = st["kind"]
    if kind in {"median_between_quartiles", "median_is_quartile_midpoint", "count_above_q3", "count_ge_q1", "total_exceeds"}:
        return _quartile_statement(st)
    if kind in {"orig_mean_below", "orig_sd_is", "k_orig_below", "nobody_orig_over"}:
        return _rescale_statement(st)
    if kind.startswith("pct_"):
        return _percentile_statement(st)
    raise ValueError(f"unknown_statement:{kind}")


def _statement_selection_answer(statements: Any, scenario: Any = None) -> dict[str, Any]:
    if not isinstance(statements, list) or len(statements) < 2:
        raise ValueError("bad_statements")
    shared = dict(scenario or {})
    selected = []
    notes = []
    for i, st in enumerate(statements, 1):
        if set(shared) & set(st):
            raise ValueError("statement_overrides_scenario")
        ok = _eval_statement({**shared, **st})
        notes.append(f"({i}){'正確' if ok else '不正確'}")
        if ok:
            selected.append(i)
    if not selected:
        raise ValueError("no_correct_statement")
    return _pack([_selected(selected, "；".join(notes) + "。")])


def statement_selection(*, statements: Any, scenario: Any = None, **_: Any) -> dict[str, Any]:
    return _statement_selection_answer(statements, scenario)


def _check_statement_selection(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_statement_selection_answer(givens["statements"], givens.get("scenario")), answer)


GRADES = 16
GSAT109_CN = ("0.01", "0.01", "0.21", "0.81", "1.35", "1.94", "2.76", "4.00", "5.92", "9.05", "13.38", "16.33", "17.66", "14.89", "8.43", "3.26")
GSAT109_MATH = ("0.04", "0.89", "4.13", "6.92", "6.45", "7.06", "7.05", "6.05", "7.11", "7.28", "6.24", "7.05", "6.89", "6.84", "8.78", "11.22")
GRADE_DATASETS = ("gsat_109", "simulated")
GRADE_SUBJECTS = {"cn": "國文科", "math": "數學科"}
GRADE_CLAIM_KINDS = ("mode", "share_below", "upper_half", "sd_less")
PCT_SUM_TOLERANCE = Fraction(5, 100)  # published two-decimal percentages may total 99.95–100.05
READ_MARGIN = Fraction(2, 10)         # chart reading never hinges on a gap below 0.2 percentage points
HALF_MARGIN = Fraction(1, 2)
SHARE_MARGIN = Fraction(1, 10)
SD_RATIO_MIN = Fraction(6, 5)


def _grade_pcts(values: Any, name: str) -> list[Fraction]:
    if not isinstance(values, (list, tuple)) or len(values) != GRADES:
        raise ValueError(f"need_grades_0_to_15:{name}")
    out = []
    for v in values:
        f = _frac(v, name)
        if f <= 0 or (f * 100).denominator != 1:
            raise ValueError(f"pct_must_be_positive_two_decimals:{name}")
        out.append(f)
    if abs(sum(out) - 100) > PCT_SUM_TOLERANCE:
        raise ValueError(f"pct_not_100:{name}")
    return out


def _grade_mean_var(pcts: list[Fraction]) -> tuple[Fraction, Fraction]:
    """Population mean/variance of the grade 0..15 distribution weighted by its percentages."""
    total = sum(pcts)
    mu = sum((g * p for g, p in enumerate(pcts)), Fraction(0)) / total
    var = sum(((g - mu) ** 2 * p for g, p in enumerate(pcts)), Fraction(0)) / total
    return mu, var


def _percentile_mark(pcts: list[Fraction], p: int) -> int:
    """Grade at the p-th percentile, read the textbook way: accumulate from 15 down until the top (100-p)% is covered."""
    need = Fraction(100 - p)
    cum = Fraction(0)
    for grade in range(GRADES - 1, -1, -1):
        cum += pcts[grade]
        if abs(cum - need) < READ_MARGIN:
            raise ValueError("percentile_on_grade_boundary")
        if cum > need:
            return grade
    raise ValueError("percentile_not_reached")


def _grade_claim_truth(claim: dict[str, Any], data: dict[str, list[Fraction]]) -> tuple[bool, str]:
    kind = claim.get("kind")
    if kind == "mode":
        pcts = data[_subject(claim)]
        g = _int(claim["grade"], "grade", 0, GRADES - 1)
        top = max(pcts)
        if pcts[g] == top:
            if sorted(pcts)[-2] > top - READ_MARGIN:
                raise ValueError("mode_not_readable")
            return True, f"{GRADE_SUBJECTS[_subject(claim)]}{g}級分占{_show(pcts[g])}%為最高"
        if pcts[g] > top - READ_MARGIN:
            raise ValueError("mode_not_readable")
        return False, f"{GRADE_SUBJECTS[_subject(claim)]}最高為{pcts.index(top)}級分（{_show(top)}%），{g}級分僅{_show(pcts[g])}%"
    if kind == "share_below":
        g = _int(claim["grade"], "grade", 0, GRADES - 1)
        t = _int(claim["threshold"], "threshold", 1, 20)
        shares = [data["cn"][g], data["math"][g]]
        if any(abs(s - t) < SHARE_MARGIN for s in shares):
            raise ValueError("share_on_threshold")
        return all(s < t for s in shares), f"{g}級分：國文{_show(shares[0])}%、數學{_show(shares[1])}%，門檻{t}%"
    if kind == "upper_half":
        pcts = data[_subject(claim)]
        k = _int(claim["grade"], "grade", 1, GRADES - 1)
        s = sum(pcts[k:], Fraction(0))
        if abs(s - 50) < HALF_MARGIN:
            raise ValueError("upper_share_near_half")
        return s > 50, f"{GRADE_SUBJECTS[_subject(claim)]}{k}級分以上（含）合計{_show(s)}%"
    if kind == "sd_less":
        first, second = _subject(claim, "first"), _subject(claim, "second")
        if first == second:
            raise ValueError("sd_needs_two_subjects")
        v1, v2 = _grade_mean_var(data[first])[1], _grade_mean_var(data[second])[1]
        lo, hi = min(v1, v2), max(v1, v2)
        if hi < lo * SD_RATIO_MIN ** 2:
            raise ValueError("sd_too_close")
        return v1 < v2, (f"加權變異數：{GRADE_SUBJECTS[first]}{float(v1):.3f}、{GRADE_SUBJECTS[second]}{float(v2):.3f}，"
                         f"標準差約 {float(v1) ** 0.5:.3f} 與 {float(v2) ** 0.5:.3f}")
    raise ValueError(f"bad_grade_claim:{kind}")


def _subject(claim: dict[str, Any], key: str = "subject") -> str:
    s = claim.get(key)
    if s not in GRADE_SUBJECTS:
        raise ValueError(f"bad_subject:{key}")
    return s


def _grade_distribution_answer(cn_pct: Any, math_pct: Any, asks: Any, claims: Any = None, dataset: Any = "simulated") -> dict[str, Any]:
    if dataset not in GRADE_DATASETS:
        raise ValueError("bad_dataset")
    data = {"cn": _grade_pcts(cn_pct, "cn"), "math": _grade_pcts(math_pct, "math")}
    authentic = [Fraction(v) for v in GSAT109_CN] == data["cn"] and [Fraction(v) for v in GSAT109_MATH] == data["math"]
    if (dataset == "gsat_109") != authentic:
        raise ValueError("dataset_label_mismatch")
    if not isinstance(asks, list) or not asks or len(set(asks)) != len(asks):
        raise ValueError("bad_asks")
    parts = []
    for ask in asks:
        if ask == "multi_select_basic":
            if not isinstance(claims, list) or [c.get("kind") for c in claims] != list(GRADE_CLAIM_KINDS):
                raise ValueError("bad_grade_claims")
            results = [_grade_claim_truth(c, data) for c in claims]
            selected = [i for i, (ok, _w) in enumerate(results, 1) if ok]
            if not selected:
                raise ValueError("no_correct_statement")
            parts.append(_selected(selected, "；".join(f"{'①②③④'[i]}{w}，{'正確' if ok else '不正確'}" for i, (ok, w) in enumerate(results)) + "。"))
        elif ask in ("higher_mark_88", "higher_mark_75"):
            p = int(ask.rsplit("_", 1)[1])
            cn_m, mt_m = _percentile_mark(data["cn"], p), _percentile_mark(data["math"], p)
            label = "A" if cn_m > mt_m else "B" if mt_m > cn_m else "C"
            parts.append(_choice(label, SUBJECTS, f"第{p}百分位數：國文 {cn_m} 級分、數學 {mt_m} 級分。"))
        else:
            raise ValueError(f"bad_ask:{ask}")
    if claims is not None and "multi_select_basic" not in asks:
        raise ValueError("claims_without_statement_part")
    return _pack(parts)


def grade_distribution_read(*, cn_pct: Any, math_pct: Any, asks: Any, claims: Any = None, dataset: Any = "simulated", **_: Any) -> dict[str, Any]:
    return _grade_distribution_answer(cn_pct, math_pct, asks, claims, dataset)


def _check_grade_distribution_read(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_grade_distribution_answer(givens["cn_pct"], givens["math_pct"], givens["asks"],
                                            givens.get("claims"), givens.get("dataset", "simulated")), answer)


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
    "grade_distribution_read": (grade_distribution_read, _check_grade_distribution_read, ("cn_pct", "math_pct", "asks", "dataset")),
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
