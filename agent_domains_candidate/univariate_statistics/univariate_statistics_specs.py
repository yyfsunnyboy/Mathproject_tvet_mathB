"""Per-component inputs for 普高數學2 Unit 8 一維數據分析.

Samplers only choose the numbers a stem prints. The domain computes every answer.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any

from .univariate_statistics_domain import GSAT109_CN, GSAT109_MATH

SKILLS = {
    "mean": "gh_Mean",
    "median": "gh_MedianAndPercentiles",
    "variance": "gh_VarianceAndStandardDeviation",
    "scaling": "gh_DataScalingAndShifting",
}

OP = {name: name for name in (
    "arithmetic_mean", "weighted_mean", "weighted_mean_unknown", "geometric_growth_mean", "geometric_growth_unknown",
    "median_lists", "median_consecutive", "percentile_frequency", "quartile_frequency", "list_summary_stats",
    "mean_variance_sd", "standard_deviation", "compare_standard_deviation", "unknown_given_sd",
    "linear_mean_sd", "linear_find_scale_sd", "standardize_scores", "monthly_mean_sd",
    "true_false_stat", "statement_selection", "grade_distribution_read",
)}

SKILL_OPERATIONS = {
    "mean": ["arithmetic_mean", "weighted_mean", "weighted_mean_unknown", "geometric_growth_mean", "geometric_growth_unknown", "true_false_stat"],
    "median": ["median_lists", "median_consecutive", "percentile_frequency", "quartile_frequency", "list_summary_stats", "true_false_stat", "statement_selection"],
    "variance": ["mean_variance_sd", "standard_deviation", "compare_standard_deviation", "unknown_given_sd", "true_false_stat", "grade_distribution_read"],
    "scaling": ["linear_mean_sd", "linear_find_scale_sd", "standardize_scores", "monthly_mean_sd", "true_false_stat", "statement_selection"],
}

FIXED_ROWS: dict[int, str] = {}

# Components whose figure the generator cannot draw (例題9／隨堂練習10 now ship generated bar charts).
VISUAL_CAPABILITY_GAP: frozenset[int] = frozenset()
# Components that read a generated chart image.
CHART_COMPONENTS = frozenset({12926, 12930})
# Concept items kept in a single fixed form (not counted as variable coverage).
FIXED_CONCEPT: frozenset[int] = frozenset()

CN109 = list(GSAT109_CN)
MT109 = list(GSAT109_MATH)
GRADE_TEXTBOOK_CLAIMS = [
    {"kind": "mode", "subject": "math", "grade": 15},
    {"kind": "share_below", "grade": 0, "threshold": 5},
    {"kind": "upper_half", "subject": "cn", "grade": 12},
    {"kind": "sd_less", "first": "cn", "second": "math"},
]

FAMILY = {
    12912: "arithmetic_mean", 12915: "arithmetic_mean",
    12913: "weighted_mean_table", 12916: "weighted_mean_insurance", 12936: "weighted_mean_unknown",
    12914: "geometric_growth", 12917: "geometric_growth_unknown", 12937: "geometric_growth",
    12931: "mean_claim",
    12918: "median_lists", 12921: "median_consecutive",
    12919: "percentile_frequency", 12922: "percentile_frequency",
    12920: "quartile_frequency", 12935: "list_summary",
    12923: "quartile_inference", 12934: "median_claim", 12946: "percentile_claims",
    12924: "mean_var_sd", 12927: "mean_var_sd",
    12925: "standard_deviation", 12929: "standard_deviation", 12938: "standard_deviation",
    12928: "compare_sd", 12940: "unknown_given_sd", 12932: "sd_claim",
    12926: "grade_distribution", 12930: "grade_distribution_followup",
    12942: "linear_transform", 12945: "linear_transform", 12939: "linear_find_scale",
    12943: "standardize", 12944: "monthly_mean_sd", 12933: "scaling_claim", 12941: "scaling_multi_select",
}


def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def _g(**kw: Any) -> dict[str, Any]:
    return kw


def _perfect_sd_list(rng: random.Random, n: int = 4) -> list[int]:
    for _ in range(80):
        vals = [rng.randint(1, 20) for _ in range(n)]
        mu = sum(vals) / Fraction(len(vals))
        var = sum((Fraction(v) - mu) ** 2 for v in vals) / len(vals)
        if int(math.isqrt(var.numerator)) ** 2 == var.numerator and int(math.isqrt(var.denominator)) ** 2 == var.denominator:
            return vals
    return [1, 4, 5, 7, 13]


def _list_mean(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [4, 5, 6])
    base = rng.randint(10, 40)
    return _g(values=[base + rng.randint(0, 20) for _ in range(n)])


def _weights_grades(rng: random.Random) -> dict[str, Any]:
    scores = [rng.randint(40, 95) for _ in range(4)]
    patterns = [[0.3, 0.2, 0.2, 0.3], [0.25, 0.25, 0.25, 0.25], [0.4, 0.2, 0.2, 0.2], [0.2, 0.3, 0.3, 0.2]]
    return _g(values=scores, weights=[str(w) for w in pick(rng, patterns)])


def _insurance(rng: random.Random) -> dict[str, Any]:
    premium = pick(rng, [300, 400, 500, 600, 800])
    payout = pick(rng, [50000, 80000, 100000, 120000, 200000])
    p = pick(rng, ["0.001", "0.002", "0.0015", "0.0005"])
    return _g(values=[premium - payout, premium], weights=[p, str(1 - Fraction(p))], scene="insurance", premium=premium, payout=payout)


def _weights_unknown(rng: random.Random) -> dict[str, Any]:
    weights = pick(rng, [[0.3, 0.2, 0.2, 0.3], [0.25, 0.25, 0.25, 0.25]])
    known = [rng.randint(40, 80) for _ in range(3)]
    x = rng.randint(40, 100)
    values = known + [x]
    mean = sum(Fraction(v) * Fraction(str(w)) for v, w in zip(values, weights)) / sum(Fraction(str(w)) for w in weights)
    return _g(values=known + ["x"], weights=[str(w) for w in weights], known_mean=str(mean), unknown_index=3)


def _growth(rng: random.Random) -> dict[str, Any]:
    pool = ["0.02", "0.03", "0.038", "0.05", "-0.02", "0.1", "0.21", "0.035", "0.028", "-0.044", "0.331"]
    n = pick(rng, [3, 4])
    return _g(rates=[pick(rng, pool) for _ in range(n)], decimals=3)


def _terminating(f: Fraction) -> bool:
    d = f.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def _growth_unknown(rng: random.Random) -> dict[str, Any]:
    # the stem asks for a decimal, so the third-year rate must be an exact terminating decimal
    for _ in range(200):
        r1 = pick(rng, ["-0.2", "-0.1", "0.1", "0.2", "0.25", "0.5"])
        r2 = pick(rng, ["-0.2", "-0.1", "0.1", "0.2", "0.25", "0.5"])
        mean = pick(rng, ["0.1", "0.2", "0.5"])
        goal = (1 + Fraction(mean)) ** 3
        x = goal / ((1 + Fraction(r1)) * (1 + Fraction(r2))) - 1
        if _terminating(x) and -Fraction(1, 2) < x < 1 and len(str(float(x))) <= 7:
            return _g(rates=[r1, r2, str(x)], known_mean=mean, unknown_index=2)
    raise ValueError("no_terminating_growth")


def _med_lists(rng: random.Random) -> dict[str, Any]:
    return _g(lists=[[rng.randint(1, 20) for _ in range(5)], [rng.randint(1, 20) for _ in range(6)]])


def _med_consec(rng: random.Random) -> dict[str, Any]:
    n1 = pick(rng, list(range(20, 60, 2)))
    return _g(ends=[n1, n1 + 1])


def _pct_shots(rng: random.Random) -> dict[str, Any]:
    shots = pick(rng, [5, 6, 8])
    counts = [rng.randint(8, 70) for _ in range(shots + 1)]
    return _g(values=list(range(shots + 1)), counts=counts, percentiles=pick(rng, [[35, 60], [20, 70], [25, 75], [15, 80]]),
              scene="shots")


def _pct_breaths(rng: random.Random) -> dict[str, Any]:
    start = rng.randint(12, 16)
    counts = [rng.randint(3, 75) for _ in range(7)]
    return _g(values=list(range(start, start + 7)), counts=counts,
              percentiles=pick(rng, [[15, 80], [20, 70], [35, 60], [25, 75]]), scene="breaths")


def _quart_salary(rng: random.Random) -> dict[str, Any]:
    values = sorted(rng.sample(range(20, 61), 7))
    return _g(values=values, counts=[rng.randint(5, 35) for _ in values], scene="salary")


def _summary(rng: random.Random) -> dict[str, Any]:
    return _g(values=sorted(rng.randint(40, 90) for _ in range(10)), stats=["mean", "median", "q3"])


def _mvs(rng: random.Random) -> dict[str, Any]:
    return _g(values=_perfect_sd_list(rng, pick(rng, [4, 5])))


def _sd_lists(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [1, 2])
    return _g(lists=[_perfect_sd_list(rng, 4) for _ in range(n)])


def _compare(rng: random.Random) -> dict[str, Any]:
    """Three groups of five around one centre: constant, narrow and wide spread, in random order."""
    c = rng.randint(9, 15)
    small, large = sorted(rng.sample([1, 2, 3, 4], 2))
    shapes = [
        lambda s: [c - 2 * s, c - s, c, c + s, c + 2 * s],
        lambda s: [c - s, c - s, c, c + s, c + s],
        lambda s: [c - 2 * s, c, c, c, c + 2 * s],
    ]
    groups = [[c] * 5, pick(rng, shapes)(small), pick(rng, shapes)(large)]
    rng.shuffle(groups)
    return _g(lists=groups)


def _unknown_sd(rng: random.Random) -> dict[str, Any]:
    """Five ascending integers with an integer population sd; the fourth one is hidden."""
    for _ in range(3000):
        vals = sorted(rng.sample(range(1, 41), 5))
        mu = Fraction(sum(vals), 5)
        var = sum((Fraction(v) - mu) ** 2 for v in vals) / 5
        if var.denominator == 1 and math.isqrt(var.numerator) ** 2 == var.numerator:
            return _g(prefix=vals[:3], suffix=vals[4:], sd=math.isqrt(var.numerator))
    raise ValueError("no_integer_sd_list")


def _linear(rng: random.Random) -> dict[str, Any]:
    return _g(mean=rng.randint(20, 40), sd=pick(rng, ["5", "6.5", "8", "10"]), a=pick(rng, ["9/5", "5/4", "2", "1/2"]), b=rng.randint(0, 40))


def _find_scale(rng: random.Random) -> dict[str, Any]:
    old_mean = rng.randint(30, 50)
    old_sd = pick(rng, [8, 10, 12])
    old_max = old_mean + rng.randint(20, 40)
    a = Fraction(pick(rng, ["5/4", "3/2", "4/3"]))
    b = rng.randint(5, 20)
    return _g(old_mean=old_mean, old_sd=old_sd, old_max=old_max, new_mean=str(a * old_mean + b), new_max=str(a * old_max + b))


def _stdz(rng: random.Random) -> dict[str, Any]:
    means = [rng.randint(50, 70), rng.randint(50, 70)]
    sds = [rng.randint(3, 10), rng.randint(3, 10)]
    scores = [means[0] + rng.randint(1, 15), means[1] + rng.randint(1, 15)]
    if scores[0] == means[0] or scores[1] == means[1]:
        raise ValueError("flat")
    if (Fraction(scores[0] - means[0], sds[0]) == Fraction(scores[1] - means[1], sds[1])):
        raise ValueError("tie")
    return _g(means=means, sds=sds, scores=scores, subjects=["數學", "英文"])


def _monthly(rng: random.Random) -> dict[str, Any]:
    vals = [str(rng.randint(0, 20) + rng.choice([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])) for _ in range(12)]
    return _g(values=vals, places=1)


def _tf_mean_shift(rng: random.Random) -> dict[str, Any]:
    """觀念澄清1: without the original mean the claim cannot be decided; with it, the claim may hold or fail."""
    n, delta = pick(rng, [5, 8, 9, 10, 12, 15]), pick(rng, [1, 2, 3])
    if rng.random() < 0.3:
        return _g(claim={"kind": "adding_value_raises_mean_by", "n": n, "delta": delta, "added": pick(rng, [10, 20, 30, 40])})
    mean = rng.randint(10, 60)
    added = mean + delta * (n + 1) + pick(rng, [0, 0, n + 1, -(n + 1), 1])
    return _g(claim={"kind": "adding_value_raises_mean_by", "n": n, "delta": delta, "added": added, "mean": mean})


def _tf_constant_sd(rng: random.Random) -> dict[str, Any]:
    value = rng.randint(2, 30)
    return _g(claim={"kind": "constant_data_sd", "n": pick(rng, [4, 5, 6]), "value": value,
                     "stated": pick(rng, [0, 0, value, 1])})


def _tf_scaled_sd(rng: random.Random) -> dict[str, Any]:
    a = pick(rng, [-5, -4, -3, -2, 2, 3, 4, 5])
    stated = pick(rng, [a, -a])
    return _g(claim={"kind": "scaled_sd_signed", "a": a, "b": rng.randint(-9, 9), "stated_factor": str(stated)})


def _tf_median_mean(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [5, 6, 7])
    base = sorted(rng.randint(1, 20) for _ in range(n))
    if rng.random() < 0.5:
        base[-1] += rng.randint(15, 40)
    else:
        base[0] = max(0, base[0] - rng.randint(0, 3))
        base[1:] = [v + 20 for v in base[1:]]
    rng.shuffle(base)
    return _g(claim={"kind": "median_ge_mean_data", "values": base})


def _to_percent_strings(weights: list[float]) -> list[str]:
    """Two-decimal percentages, each at least 0.01, totalling exactly 100.00 (largest remainder)."""
    free = 10000 - len(weights)
    total = sum(weights)
    raw = [w / total * free for w in weights]
    units = [int(r) for r in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i] - units[i], reverse=True)[: free - sum(units)]:
        units[i] += 1
    return [f"{(u + 1) // 100}.{(u + 1) % 100:02d}" for u in units]


def _concentrated_shape(rng: random.Random) -> list[float]:
    centre = rng.uniform(8.5, 12.8)
    left, right = rng.uniform(1.6, 2.6), rng.uniform(1.2, 2.0)
    return [math.exp(-((g - centre) ** 2) / (2 * (left if g < centre else right) ** 2)) + 0.0004 for g in range(16)]


def _spread_shape(rng: random.Random) -> list[float]:
    style = rng.choice(["plateau_top", "plateau", "bimodal"])
    if style == "plateau_top":
        w = [rng.uniform(0.03, 1.2), rng.uniform(0.4, 3.5)] + [rng.uniform(5.0, 8.0) for _ in range(13)] + [rng.uniform(7.0, 13.0)]
    elif style == "plateau":
        w = [rng.uniform(0.05, 2.5)] + [rng.uniform(4.5, 8.5) for _ in range(15)]
    else:
        lo, hi = rng.uniform(3.0, 6.0), rng.uniform(11.0, 14.0)
        w = [1.2 + 6 * math.exp(-((g - lo) ** 2) / 8) + 7 * math.exp(-((g - hi) ** 2) / 8) for g in range(16)]
        w[0] = rng.uniform(0.05, 2.0)
    return w


def _grade_claims(rng: random.Random, data: dict[str, list[Fraction]]) -> list[dict[str, Any]]:
    subject = rng.choice(["cn", "math"])
    ranked = sorted(range(16), key=lambda g: data[subject][g], reverse=True)
    mode_grade = ranked[0] if rng.random() < 0.5 else ranked[rng.choice([1, 2])]
    half_subject = rng.choice(["cn", "math"])
    tails = [k for k in range(1, 16) if 25 <= sum(data[half_subject][k:]) <= 75]
    first = rng.choice(["cn", "math"])
    return [
        {"kind": "mode", "subject": subject, "grade": mode_grade},
        {"kind": "share_below", "grade": rng.choice([0, 0, 1]), "threshold": rng.choice([1, 2, 3, 4, 5])},
        {"kind": "upper_half", "subject": half_subject, "grade": rng.choice(tails)},
        {"kind": "sd_less", "first": first, "second": "math" if first == "cn" else "cn"},
    ]


def _grade(asks: list[str]):
    """Simulated exam: one concentrated and one spread subject (either way round); the domain grades every claim."""
    def sample(rng: random.Random) -> dict[str, Any]:
        tight, wide = _to_percent_strings(_concentrated_shape(rng)), _to_percent_strings(_spread_shape(rng))
        cn, mt = (tight, wide) if rng.random() < 0.6 else (wide, tight)
        out = _g(cn_pct=cn, math_pct=mt, dataset="simulated", asks=list(asks))
        if "multi_select_basic" in asks:
            out["claims"] = _grade_claims(rng, {"cn": [Fraction(v) for v in cn], "math": [Fraction(v) for v in mt]})
        return out

    return sample


def _quartile_inf(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [32, 36, 40, 44, 48])
    q1 = pick(rng, [5, 6, 7, 8])
    q3 = q1 + pick(rng, [2, 3, 4])
    mean = Fraction(pick(rng, [2 * q1 + 1, 2 * q1 + 2, 2 * q1 + 3, 2 * q3 - 1]), 2)
    total = n * mean
    threshold = int(total) // 10 * 10 + pick(rng, [-20, -10, 10, 20])
    m = n // 4
    return _g(scenario={"n": n, "mean": str(mean), "q1": q1, "q3": q3}, statements=[
        {"kind": pick(rng, ["median_between_quartiles", "median_between_quartiles", "median_is_quartile_midpoint"])},
        {"kind": "count_above_q3", "mode": pick(rng, ["about", "at_most"]), "count": m},
        {"kind": "count_ge_q1", "strict": pick(rng, [False, False, True]), "count": 3 * m},
        {"kind": "total_exceeds", "threshold": threshold},
    ])


def _pct_claims(rng: random.Random) -> dict[str, Any]:
    p = pick(rng, [20, 25, 30, 40, 60, 75])
    second = pick(rng, [{"kind": "pct_shift", "d": pick(rng, [3, 5, -4, -2])}, {"kind": "pct_square"}])
    fourth = pick(rng, [{"kind": "pct_lt_mean"}, {"kind": "pct_within_range"}])
    return _g(scenario={"p": p}, statements=[
        {"kind": "pct_scale", "c": pick(rng, [2, 3, 5, -2, -3])},
        second,
        {"kind": "pct_merge_sum"},
        fourth,
    ])


def _scale_multi(rng: random.Random) -> dict[str, Any]:
    shift = pick(rng, [30, 35, 40, 45, 50])
    cap = 2 * shift
    mu_y = rng.randint(shift + 10, cap - 8)
    mu_x = 2 * (mu_y - shift)
    sd_y = pick(rng, [3, 4, 5, 6, 8])
    if (2 * sd_y) ** 2 > mu_x * (cap - mu_x):
        raise ValueError("sd_infeasible")
    low_y = pick(rng, [v for v in range(shift + 5, mu_y, 5)] or [shift + 5])
    x_low = 2 * (low_y - shift)
    return _g(scenario={"div": 2, "shift": shift, "mu_y": mu_y, "sd_y": sd_y, "k": pick(rng, [3, 4, 5, 6]), "low_y": low_y},
              statements=[
                  {"kind": "orig_mean_below", "stated": mu_x + pick(rng, [-8, -4, 4, 8])},
                  {"kind": "orig_sd_is", "stated": pick(rng, [2 * sd_y, sd_y])},
                  {"kind": "k_orig_below", "stated": pick(rng, [x_low, x_low // 2])},
                  {"kind": "nobody_orig_over", "stated": pick(rng, [cap, cap - 10])},
              ])


COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Any]] = {
    12912: ("mean", "arithmetic_mean", _g(values=[186, 188, 189, 191, 226]), _list_mean),
    12915: ("mean", "arithmetic_mean", _g(values=[21, 13, 23, 21, 22, 20]), _list_mean),
    12913: ("mean", "weighted_mean", _g(values=[83, 68, 87, 74], weights=["0.3", "0.2", "0.2", "0.3"]), _weights_grades),
    12916: ("mean", "weighted_mean", _g(values=[-99500, 500], weights=["0.001", "0.999"], scene="insurance", premium=500, payout=100000), _insurance),
    12936: ("mean", "weighted_mean_unknown", _g(values=[65, 46, 53, "x"], weights=["0.3", "0.2", "0.2", "0.3"], known_mean=60, unknown_index=3), _weights_unknown),
    12914: ("mean", "geometric_growth_mean", _g(rates=["0.038", "0.035", "0.028", "-0.044"], decimals=3), _growth),
    12917: ("mean", "geometric_growth_unknown", _g(rates=["-0.1", "0.2", "0"], known_mean="0.2", unknown_index=2), _growth_unknown),
    12937: ("mean", "geometric_growth_mean", _g(rates=["0.1", "0.21", "0.331"], decimals=3), _growth),
    12931: ("mean", "true_false_stat", _g(claim={"kind": "adding_value_raises_mean_by", "n": 10, "delta": 2, "added": 20}), _tf_mean_shift),
    12918: ("median", "median_lists", _g(lists=[[8, 4, 9, 1, 6], [8, 4, 9, 1, 6, 8]]), _med_lists),
    12921: ("median", "median_consecutive", _g(ends=[49, 50]), _med_consec),
    12919: ("median", "percentile_frequency", _g(values=[0, 1, 2, 3, 4, 5, 6], counts=[13, 29, 42, 66, 38, 35, 27], percentiles=[35, 60], scene="shots"), _pct_shots),
    12922: ("median", "percentile_frequency", _g(values=[15, 16, 17, 18, 19, 20, 21], counts=[16, 31, 48, 71, 67, 34, 3], percentiles=[15, 80], scene="breaths"), _pct_breaths),
    12920: ("median", "quartile_frequency", _g(values=[22, 25, 32, 36, 43, 48, 52], counts=[10, 15, 26, 35, 16, 11, 5], scene="salary"), _quart_salary),
    12935: ("median", "list_summary_stats", _g(values=[55, 56, 59, 59, 59, 60, 60, 63, 68, 71], stats=["mean", "median", "q3"]), _summary),
    12923: ("median", "statement_selection", _g(scenario={"n": 40, "mean": "8.5", "q1": 7, "q3": 10}, statements=[
        {"kind": "median_between_quartiles"}, {"kind": "count_above_q3", "mode": "about", "count": 10},
        {"kind": "count_ge_q1", "strict": False, "count": 30}, {"kind": "total_exceeds", "threshold": 350},
    ]), _quartile_inf),
    12934: ("median", "true_false_stat", _g(claim={"kind": "median_ge_mean_always"}), _tf_median_mean),
    12946: ("median", "statement_selection", _g(scenario={"p": 40}, statements=[
        {"kind": "pct_scale", "c": 3}, {"kind": "pct_shift", "d": 3}, {"kind": "pct_merge_sum"}, {"kind": "pct_lt_mean"},
    ]), _pct_claims),
    12924: ("variance", "mean_variance_sd", _g(values=[1, 4, 5, 7, 13]), _mvs),
    12927: ("variance", "mean_variance_sd", _g(values=[86, 88, 92, 94]), _mvs),
    12925: ("variance", "standard_deviation", _g(lists=[[2, 5, 6, 9]]), _sd_lists),
    12929: ("variance", "standard_deviation", _g(lists=[[5, 8, 9, 12]]), _sd_lists),
    12938: ("variance", "standard_deviation", _g(lists=[[51, 53, 56, 60, 60, 62], [1, 2, 4, 5, 6, 8]]), _sd_lists),
    12928: ("variance", "compare_standard_deviation", _g(lists=[[5, 5, 5, 5, 5], [1, 3, 5, 7, 9], [3, 4, 5, 6, 7]]), _compare),
    12940: ("variance", "unknown_given_sd", _g(prefix=[2, 6, 14], suffix=[18], sd=6), _unknown_sd),
    12932: ("variance", "true_false_stat", _g(claim={"kind": "equal_values_sd_zero"}), _tf_constant_sd),
    12926: ("variance", "grade_distribution_read",
            _g(cn_pct=CN109, math_pct=MT109, dataset="gsat_109", asks=["multi_select_basic", "higher_mark_88"], claims=GRADE_TEXTBOOK_CLAIMS),
            _grade(["multi_select_basic", "higher_mark_88"])),
    12930: ("variance", "grade_distribution_read", _g(cn_pct=CN109, math_pct=MT109, dataset="gsat_109", asks=["higher_mark_75"]),
            _grade(["higher_mark_75"])),
    12942: ("scaling", "linear_mean_sd", _g(mean=30, sd="6.5", a="9/5", b=32), _linear),
    12945: ("scaling", "linear_mean_sd", _g(mean=36, sd=12, a="5/4", b=10), _linear),
    12939: ("scaling", "linear_find_scale_sd", _g(old_mean=42, old_sd=12, old_max=72, new_mean=60, new_max=95), _find_scale),
    12943: ("scaling", "standardize_scores", _g(means=[68, 60], sds=[5, 4], scores=[73, 65], subjects=["數學", "英文"]), _stdz),
    12944: ("scaling", "monthly_mean_sd", _g(values=["3.0", "3.9", "1.8", "5.7", "7.6", "9.6", "9.3", "8.2", "8.0", "4.0", "3.6", "1.3"], places=1), _monthly),
    12933: ("scaling", "true_false_stat", _g(claim={"kind": "scaled_sd_signed", "a": -3, "b": 2, "stated_factor": "-3"}), _tf_scaled_sd),
    12941: ("scaling", "statement_selection", _g(scenario={"div": 2, "shift": 40, "mu_y": 66, "sd_y": 5, "k": 5, "low_y": 60}, statements=[
        {"kind": "orig_mean_below", "stated": 60},
        {"kind": "orig_sd_is", "stated": 10},
        {"kind": "k_orig_below", "stated": 20},
        {"kind": "nobody_orig_over", "stated": 80},
    ]), _scale_multi),
}
