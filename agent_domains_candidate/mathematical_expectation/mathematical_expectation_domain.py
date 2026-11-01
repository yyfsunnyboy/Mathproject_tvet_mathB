"""Discrete expectation for 普高數學2 Unit 7 數學期望值.

Every graded value is computed here twice: once by enumerating the equiprobable outcomes (or the stated distribution)
and once by a closed form (binomial / hypergeometric counts, linearity of expectation). They must agree.
Generators only supply the stated data (the givens); they never carry a textbook answer.
"""

from __future__ import annotations

import itertools
import math
from fractions import Fraction
from typing import Any, Callable

DOMAIN_KEY = "discrete.mathematical_expectation"

TRUE_FALSE = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
YES_NO = ({"label": "A", "value": "是"}, {"label": "B", "value": "否"})
FAIR = ({"label": "A", "value": "公平"}, {"label": "B", "value": "不公平"})
PARTY = ({"label": "A", "value": "甲"}, {"label": "B", "value": "乙"}, {"label": "C", "value": "雙方公平"})
SITES = ({"label": "A", "value": "甲地"}, {"label": "B", "value": "乙地"})
CHOICE_LABELS = "ABCDE"

WIN_SETS = {
    "prime": (2, 3, 5),
    "even": (2, 4, 6),
    "odd": (1, 3, 5),
    "high": (4, 5, 6),
}


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
    try:
        return Fraction(str(v).strip())
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"not_a_fraction:{name}") from None


def _show(f: Fraction) -> str:
    """Terminating decimals stay decimals in the worked solution; others are fractions."""
    den = f.denominator
    while den % 2 == 0:
        den //= 2
    while den % 5 == 0:
        den //= 5
    if den != 1 or f.denominator == 1:
        return str(f)
    text = f"{float(f):.6f}".rstrip("0").rstrip(".")
    if Fraction(text) != f:
        return str(f)
    return text


def _value(f: Fraction, work: str) -> dict[str, Any]:
    return {"kind": "rational", "value": str(f), "work": work}


def _choice(label: str, choices, work: str) -> dict[str, Any]:
    if label not in {c["label"] for c in choices}:
        raise ValueError("bad_choice_label")
    return {"kind": "choice", "label": label, "choices": [dict(c) for c in choices], "work": work}


def _pack(parts: list[dict[str, Any]]) -> dict[str, Any]:
    if not parts:
        raise ValueError("no_parts")
    return {"parts": parts}


def _same(fresh: dict[str, Any], answer: dict[str, Any]) -> bool:
    return fresh == answer


def _collapse(pairs: list[tuple[Fraction, Fraction]]) -> list[tuple[Fraction, Fraction]]:
    """Merge equal values of a distribution and check the probabilities sum to 1."""
    merged: dict[Fraction, Fraction] = {}
    for value, prob in pairs:
        if prob < 0:
            raise ValueError("negative_probability")
        merged[value] = merged.get(value, Fraction(0)) + prob
    if sum(merged.values()) != 1:
        raise ValueError("distribution_not_one")
    return sorted((v, p) for v, p in merged.items() if p)


def _mean(dist: list[tuple[Fraction, Fraction]]) -> Fraction:
    return sum((v * p for v, p in dist), Fraction(0))


def _dist_work(dist: list[tuple[Fraction, Fraction]], what: str) -> str:
    listed = "、".join(f"{_show(v)}（機率 {p}）" for v, p in dist)
    terms = " + ".join(f"({_show(v)})×{p}" for v, p in dist)
    return f"{what}的可能值與機率：{listed}；期望值 E = {terms} = {_show(_mean(dist))}。"


def _uniform(values: list[Fraction]) -> list[tuple[Fraction, Fraction]]:
    if not values:
        raise ValueError("empty_sample_space")
    weight = Fraction(1, len(values))
    return _collapse([(Fraction(v), weight) for v in values])


# --- one die payouts ------------------------------------------------------------------------------------------------------------------


def _die_payout_answer(payouts: Any, style: Any, coef: Any = None) -> dict[str, Any]:
    if not isinstance(payouts, list) or len(payouts) != 6:
        raise ValueError("bad_payouts")
    pays = [_int(v, "payout", -100000, 1000000) for v in payouts]
    style = str(style)
    if style == "linear":
        c = _int(coef, "coef", 1, 10000)
        if pays != [c * k for k in range(1, 7)]:
            raise ValueError("linear_payouts_mismatch")
        closed = c * Fraction(7, 2)
    elif style == "grouped":
        if len(set(pays)) < 2:
            raise ValueError("degenerate_payouts")
        closed = sum((Fraction(v * pays.count(v), 6) for v in set(pays)), Fraction(0))
    else:
        raise ValueError("bad_style")
    dist = _uniform([Fraction(v) for v in pays])
    if _mean(dist) != closed:
        raise ValueError("die_payout_mismatch")
    return _pack([_value(closed, "每個點數出現的機率都是 1/6。" + _dist_work(dist, "所得金額"))])


def die_payout_expectation(*, payouts: Any, style: Any, coef: Any = None, **_: Any) -> dict[str, Any]:
    return _die_payout_answer(payouts, style, coef)


def _check_die_payout(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_die_payout_answer(givens["payouts"], givens["style"], givens.get("coef")), answer)


# --- coin payouts ---------------------------------------------------------------------------------------------------------------------


def _coin_payout_answer(n: Any, scenarios: Any) -> dict[str, Any]:
    n = _int(n, "n", 1, 5)
    if not isinstance(scenarios, list) or not 1 <= len(scenarios) <= 2:
        raise ValueError("bad_scenarios")
    parsed = []
    for row in scenarios:
        if not isinstance(row, list) or len(row) != n + 1:
            raise ValueError("bad_scenario")
        pays = [_int(v, "payout", -100000, 100000) for v in row]
        if len(set(pays)) < 2:
            raise ValueError("degenerate_payouts")
        parsed.append(pays)
    if len(parsed) == 2 and parsed[0] == parsed[1]:
        raise ValueError("scenarios_identical")
    parts = []
    for pays in parsed:
        seqs = list(itertools.product((0, 1), repeat=n))
        dist = _uniform([Fraction(pays[sum(seq)]) for seq in seqs])
        closed = sum((Fraction(math.comb(n, k) * pays[k], 2**n) for k in range(n + 1)), Fraction(0))
        if _mean(dist) != closed:
            raise ValueError("coin_payout_mismatch")
        heads = "、".join(f"{k} 個正面的機率 {Fraction(math.comb(n, k), 2**n)}" for k in range(n + 1))
        parts.append(_value(closed, f"丟 {n} 枚硬幣共有 {2**n} 種等可能結果，{heads}。" + _dist_work(dist, "所得金額")))
    return _pack(parts)


def coin_payout_expectation(*, n: Any, scenarios: Any, **_: Any) -> dict[str, Any]:
    return _coin_payout_answer(n, scenarios)


def _check_coin_payout(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_coin_payout_answer(givens["n"], givens["scenarios"]), answer)


# --- urn draws without replacement ----------------------------------------------------------------------------------------------------


def _urn_variable(variable: Any, groups: list[dict[str, Any]], draw: int) -> Callable[[tuple[int, ...]], Fraction]:
    if not isinstance(variable, dict):
        raise ValueError("bad_variable")
    kind = str(variable.get("kind") or "")
    if kind == "sum_of_values":
        values = [g.get("value") for g in groups]
        if any(v is None for v in values):
            raise ValueError("values_required")
        vals = [_int(v, "value", 1, 100000) for v in values]
        if len(set(vals)) != len(vals):
            raise ValueError("values_not_distinct")
        return lambda tally: Fraction(sum(c * v for c, v in zip(tally, vals)))
    index = _int(variable.get("index"), "index", 0, len(groups) - 1)
    if kind == "count":
        return lambda tally: Fraction(tally[index])
    if kind == "payout_by_count":
        table = variable.get("payouts")
        if not isinstance(table, list) or not table:
            raise ValueError("bad_payout_table")
        pays = {}
        for item in table:
            if not isinstance(item, list) or len(item) != 2:
                raise ValueError("bad_payout_table")
            pays[_int(item[0], "count", 0, draw)] = _int(item[1], "payout", -1000000, 1000000)
        default = _int(variable.get("default"), "default", -1000000, 1000000)
        if len(pays) != len(table) or len(set(pays.values()) | {default}) < 2:
            raise ValueError("degenerate_payouts")
        return lambda tally: Fraction(pays.get(tally[index], default))
    raise ValueError("bad_variable_kind")


def _urn_closed(variable: dict[str, Any], counts: list[int], draw: int, measure) -> Fraction:
    total = sum(counts)
    expected = Fraction(0)
    weight = Fraction(0)
    for tally in itertools.product(*[range(min(c, draw) + 1) for c in counts]):
        if sum(tally) != draw:
            continue
        ways = math.prod(math.comb(c, t) for c, t in zip(counts, tally))
        prob = Fraction(ways, math.comb(total, draw))
        weight += prob
        expected += measure(tally) * prob
    if weight != 1:
        raise ValueError("hypergeometric_not_one")
    kind = variable["kind"]
    if kind == "count":
        linear = Fraction(draw * counts[int(variable["index"])], total)
        if linear != expected:
            raise ValueError("count_linearity_mismatch")
    if kind == "sum_of_values":
        linear = Fraction(draw, total) * measure(tuple(counts))
        if linear != expected:
            raise ValueError("sum_linearity_mismatch")
    return expected


def _urn_answer(groups: Any, draw: Any, variable: Any) -> dict[str, Any]:
    if not isinstance(groups, list) or not 2 <= len(groups) <= 3 or not all(isinstance(g, dict) for g in groups):
        raise ValueError("bad_groups")
    counts = [_int(g.get("count"), "count", 1, 12) for g in groups]
    total = sum(counts)
    if not 3 <= total <= 20:
        raise ValueError("bad_total")
    k = _int(draw, "draw", 1, 5)
    if k >= total:
        raise ValueError("draw_exceeds")
    measure = _urn_variable(variable, groups, k)
    items = [i for i, c in enumerate(counts) for _ in range(c)]
    combos = list(itertools.combinations(range(total), k))
    values = []
    for combo in combos:
        tally = tuple(sum(1 for j in combo if items[j] == i) for i in range(len(counts)))
        values.append(measure(tally))
    dist = _uniform(values)
    if len(dist) < 2:
        raise ValueError("degenerate_variable")
    closed = _urn_closed(variable, counts, k, measure)
    if _mean(dist) != closed:
        raise ValueError("urn_mismatch")
    work = f"從 {total} 個中任取 {k} 個，共 C({total},{k}) = {len(combos)} 種等可能取法。" + _dist_work(dist, "隨機變數")
    return _pack([_value(closed, work)])


def urn_draw_expectation(*, groups: Any, draw: Any, variable: Any, **_: Any) -> dict[str, Any]:
    return _urn_answer(groups, draw, variable)


def _check_urn(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_urn_answer(givens["groups"], givens["draw"], givens["variable"]), answer)


# --- dice games -----------------------------------------------------------------------------------------------------------------------


def _two_dice_gain(m: int, amount: int) -> list[Fraction]:
    return [Fraction(m * a) if a == b else Fraction(-amount) for a in range(1, 7) for b in range(1, 7)]


def _two_dice_answer(multiplier: Any, amount: Any) -> dict[str, Any]:
    m = _int(multiplier, "multiplier", 1, 50)
    a = _int(amount, "amount", 1, 500)
    dist = _uniform(_two_dice_gain(m, a))
    closed = Fraction(21 * m - 30 * a, 36)
    if _mean(dist) != closed:
        raise ValueError("two_dice_mismatch")
    fair = Fraction(21 * m, 30)
    if _mean(_collapse([(v, Fraction(1, 36)) for v in
                        [Fraction(m * x) if x == y else -fair for x in range(1, 7) for y in range(1, 7)]])) != 0:
        raise ValueError("fair_amount_mismatch")
    label = "B" if closed > 0 else ("A" if closed < 0 else "C")
    verdict = {"A": "期望值為負，對甲有利", "B": "期望值為正，對乙有利", "C": "期望值為 0，雙方公平"}[label]
    return _pack([
        _value(closed, "兩人點數相同有 6 種、不同有 30 種，共 36 種等可能結果。" + _dist_work(dist, "乙的所得金額")),
        _choice(label, PARTY, f"乙所得金額的期望值為 {_show(closed)}，{verdict}。"),
        _value(fair, f"設改為 x 元，令 {m}×(1+2+3+4+5+6)/36 - 30x/36 = 0，得 x = {_show(fair)}。"),
    ])


def two_dice_match_game(*, multiplier: Any, amount: Any, **_: Any) -> dict[str, Any]:
    return _two_dice_answer(multiplier, amount)


def _check_two_dice(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_two_dice_answer(givens["multiplier"], givens["amount"]), answer)


def _single_die_answer(win_set: Any, multiplier: Any, fee: Any) -> dict[str, Any]:
    wins = WIN_SETS.get(str(win_set))
    if wins is None:
        raise ValueError("bad_win_set")
    m = _int(multiplier, "multiplier", 1, 20)
    f = _int(fee, "fee", 1, 100)
    gains = [Fraction(m * face) if face in wins else Fraction(-face) for face in range(1, 7)]
    dist = _uniform(gains)
    closed = Fraction(m * sum(wins) - sum(x for x in range(1, 7) if x not in wins), 6)
    if _mean(dist) != closed:
        raise ValueError("single_die_mismatch")
    after = _mean(_uniform([g - f for g in gains]))
    if after != closed - f:
        raise ValueError("fee_linearity_mismatch")
    fair = after == 0
    return _pack([
        _value(closed, "每個點數出現的機率都是 1/6。" + _dist_work(dist, "乙的所得金額")),
        _choice("A" if fair else "B", FAIR,
                f"先付 {f} 元後，乙的所得期望值為 {_show(closed)} - {f} = {_show(after)}，"
                + ("等於 0，遊戲公平。" if fair else "不等於 0，遊戲不公平。")),
    ])


def single_die_game(*, win_set: Any, multiplier: Any, fee: Any, **_: Any) -> dict[str, Any]:
    return _single_die_answer(win_set, multiplier, fee)


def _check_single_die(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_single_die_answer(givens["win_set"], givens["multiplier"], givens["fee"]), answer)


# --- insurance ------------------------------------------------------------------------------------------------------------------------


def _insurance_answer(givens: dict[str, Any]) -> dict[str, Any]:
    stated = _frac(givens.get("stated_prob"), "stated_prob")
    kind = str(givens.get("prob_kind") or "")
    if kind == "survive":
        p = 1 - stated
    elif kind == "event":
        p = stated
    else:
        raise ValueError("bad_prob_kind")
    if not 0 < p < 1:
        raise ValueError("probability_out_of_range")
    payout = _int(givens.get("payout"), "payout", 1000, 100000000)
    ask = str(givens.get("ask") or "")
    if ask == "profit":
        premium = Fraction(_int(givens.get("premium"), "premium", 1, 1000000))
        dist = _collapse([(premium, 1 - p), (premium - payout, p)])
        closed = premium - payout * p
        if _mean(dist) != closed:
            raise ValueError("insurance_mismatch")
        work = (f"事故發生的機率為 {_show(p)}。" + _dist_work(dist, "公司每份保單的利潤")
                + f"也可寫成 {_show(premium)} - {payout}×{_show(p)} = {_show(closed)}。")
        return _pack([_value(closed, work)])
    if ask == "premium":
        profit = Fraction(_int(givens.get("profit"), "profit", -1000000, 1000000))
        premium = profit + payout * p
        if premium <= 0:
            raise ValueError("premium_not_positive")
        dist = _collapse([(premium, 1 - p), (premium - payout, p)])
        if _mean(dist) != profit:
            raise ValueError("insurance_mismatch")
        work = (f"設保費為 x 元，事故發生的機率為 {_show(p)}，利潤期望值 x×{_show(1 - p)} + (x - {payout})×{_show(p)}"
                f" = x - {_show(payout * p)} = {_show(profit)}，得 x = {_show(premium)}。")
        return _pack([_value(premium, work)])
    raise ValueError("bad_ask")


def insurance_expectation(**givens: Any) -> dict[str, Any]:
    return _insurance_answer(givens)


def _check_insurance(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_insurance_answer(givens), answer)


# --- decision by expectation ----------------------------------------------------------------------------------------------------------


def _decision_answer(probs: Any, profits: Any, states: Any) -> dict[str, Any]:
    if not isinstance(probs, list) or not 2 <= len(probs) <= 4:
        raise ValueError("bad_probs")
    ps = [_frac(v, "prob") for v in probs]
    if any(p <= 0 for p in ps) or sum(ps) != 1:
        raise ValueError("bad_probs")
    if not isinstance(states, list) or len(states) != len(ps) or not all(str(s).strip() for s in states):
        raise ValueError("bad_states")
    if not isinstance(profits, list) or len(profits) != 2:
        raise ValueError("bad_profits")
    rows = []
    for row in profits:
        if not isinstance(row, list) or len(row) != len(ps):
            raise ValueError("bad_profits")
        rows.append([Fraction(_int(v, "profit", -1000, 1000)) for v in row])
    means = [_mean(_collapse(list(zip(row, ps)))) for row in rows]
    diff = sum(((a - b) * p for a, b, p in zip(rows[0], rows[1], ps)), Fraction(0))
    if diff != means[0] - means[1]:
        raise ValueError("decision_mismatch")
    if diff == 0:
        raise ValueError("tie")
    label = "A" if diff > 0 else "B"
    work = "；".join(
        f"{name}地的利潤期望值 = " + " + ".join(f"({_show(v)})×{_show(p)}" for v, p in zip(row, ps)) + f" = {_show(mean)}"
        for name, row, mean in zip(("甲", "乙"), rows, means)
    )
    best = "甲" if label == "A" else "乙"
    return _pack([_choice(label, SITES, f"{work}；期望值較大的是{best}地。")])


def decision_by_expectation(*, probs: Any, profits: Any, states: Any, **_: Any) -> dict[str, Any]:
    return _decision_answer(probs, profits, states)


def _check_decision(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_decision_answer(givens["probs"], givens["profits"], givens["states"]), answer)


# --- true / false claims --------------------------------------------------------------------------------------------------------------


def _claim_answer(model: Any, n: Any, stated: Any) -> dict[str, Any]:
    model = str(model)
    claim = _frac(stated, "stated")
    if model == "coin":
        k = _int(n, "n", 1, 6)
        enum = _mean(_uniform([Fraction(sum(seq)) for seq in itertools.product((0, 1), repeat=k)]))
        closed = Fraction(k, 2)
        what = "正面次數"
    elif model == "die":
        k = _int(n, "n", 1, 3)
        enum = _mean(_uniform([Fraction(sum(seq)) for seq in itertools.product(range(1, 7), repeat=k)]))
        closed = Fraction(7 * k, 2)
        what = "點數和" if k > 1 else "點數"
    else:
        raise ValueError("bad_model")
    if enum != closed:
        raise ValueError("claim_mismatch")
    right = claim == closed
    work = f"{what}的期望值為 {_show(closed)}，敘述中的值為 {_show(claim)}，所以敘述" + ("正確。" if right else "錯誤。")
    return _pack([_choice("A" if right else "B", TRUE_FALSE, work)])


def expectation_claim(*, model: Any, n: Any, stated: Any, **_: Any) -> dict[str, Any]:
    return _claim_answer(model, n, stated)


def _check_claim(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_claim_answer(givens["model"], givens["n"], givens["stated"]), answer)


# --- multiple-choice guessing ---------------------------------------------------------------------------------------------------------


def _guess_answer(options: Any, known: Any, scores: Any) -> dict[str, Any]:
    m = _int(options, "options", 4, 6)
    k = _int(known, "known", 1, m - 1)
    r = m - k
    if r > 4:
        raise ValueError("too_many_guesses")
    if not isinstance(scores, list) or len(scores) != 3:
        raise ValueError("bad_scores")
    pts = [_int(v, "score", 1, 20) for v in scores]
    if not pts[0] > pts[1] > pts[2] > 0:
        raise ValueError("scores_not_decreasing")

    def score(wrong: int) -> Fraction:
        return Fraction(pts[wrong]) if wrong < 3 else Fraction(0)

    dist = _uniform([score(sum(1 for hit in seq if not hit)) for seq in itertools.product((True, False), repeat=r)])
    closed = sum((Fraction(math.comb(r, w), 2**r) * score(w) for w in range(r + 1)), Fraction(0))
    if _mean(dist) != closed:
        raise ValueError("guess_mismatch")
    wrongs = "、".join(f"錯 {w} 個的機率 {Fraction(math.comb(r, w), 2**r)}" for w in range(r + 1))
    work = f"其餘 {r} 個選項各自猜對或猜錯的機會均等，共 {2**r} 種等可能情形，{wrongs}。" + _dist_work(dist, "得分")
    return _pack([_value(closed, work)])


def multiple_choice_guess_expectation(*, options: Any, known: Any, scores: Any, **_: Any) -> dict[str, Any]:
    return _guess_answer(options, known, scores)


def _check_guess(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_guess_answer(givens["options"], givens["known"], givens["scores"]), answer)


# --- lottery --------------------------------------------------------------------------------------------------------------------------


def _lottery_answer(total: Any, prizes: Any) -> dict[str, Any]:
    n = _int(total, "total", 100, 100000000)
    if not isinstance(prizes, list) or not 2 <= len(prizes) <= 7:
        raise ValueError("bad_prizes")
    rows = []
    for item in prizes:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("bad_prizes")
        rows.append((_int(item[0], "amount", 1, 100000000), _int(item[1], "count", 1, n)))
    if len({a for a, _c in rows}) != len(rows) or sum(c for _a, c in rows) >= n:
        raise ValueError("bad_prizes")
    blanks = n - sum(c for _a, c in rows)
    dist = _collapse([(Fraction(a), Fraction(c, n)) for a, c in rows] + [(Fraction(0), Fraction(blanks, n))])
    closed = Fraction(sum(a * c for a, c in rows), n)
    if _mean(dist) != closed:
        raise ValueError("lottery_mismatch")
    terms = " + ".join(f"{a}×{c}" for a, c in rows)
    work = f"所有獎金總和為 {terms} = {sum(a * c for a, c in rows)} 元，平均分配到 {n} 張彩券，期望值為 {_show(closed)} 元。"
    return _pack([_value(closed, work)])


def lottery_expectation(*, total: Any, prizes: Any, **_: Any) -> dict[str, Any]:
    return _lottery_answer(total, prizes)


def _check_lottery(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_lottery_answer(givens["total"], givens["prizes"]), answer)


# --- prize balls: single draw vs. max of two ------------------------------------------------------------------------------------------


def prize_ball_choices(values: list[int], offsets: list[int]) -> list[dict[str, str]]:
    mean = Fraction(sum(values), len(values))
    return [{"label": CHOICE_LABELS[i], "value": f"{_show(mean + off)}元"} for i, off in enumerate(offsets)]


def _prize_answer(values: Any, choice_offsets: Any) -> dict[str, Any]:
    if not isinstance(values, list) or not 3 <= len(values) <= 5:
        raise ValueError("bad_values")
    vals = [_int(v, "value", 100, 100000) for v in values]
    if len(set(vals)) != len(vals):
        raise ValueError("values_not_distinct")
    if not isinstance(choice_offsets, list) or len(choice_offsets) != 5:
        raise ValueError("bad_offsets")
    offsets = [_int(v, "offset", -5000, 5000) for v in choice_offsets]
    if len(set(offsets)) != 5 or offsets.count(0) != 1:
        raise ValueError("bad_offsets")
    single = _mean(_uniform([Fraction(v) for v in vals]))
    if single != Fraction(sum(vals), len(vals)) or single.denominator != 1:
        raise ValueError("single_mean_not_integer")
    if any(single + off <= 0 for off in offsets):
        raise ValueError("choice_not_positive")
    choices = prize_ball_choices(vals, offsets)
    label = CHOICE_LABELS[offsets.index(0)]

    balls = [v for v in vals for _ in range(2)]
    pairs = list(itertools.combinations(range(len(balls)), 2))
    double = _uniform([Fraction(max(balls[i], balls[j])) for i, j in pairs])
    ordered = sorted(vals)
    total = math.comb(len(balls), 2)
    closed = Fraction(0)
    for j, v in enumerate(ordered, 1):
        below = Fraction(math.comb(2 * j, 2) - math.comb(2 * (j - 1), 2), total)
        closed += v * below
    if _mean(double) != closed:
        raise ValueError("max_draw_mismatch")
    gain = closed - single
    correct = gain > 0
    shown = "、".join(str(v) for v in vals)
    return _pack([
        _choice(label, choices, f"{len(vals)} 種獎額等可能，期望值 = ({shown}) 的平均 = {_show(single)} 元。"),
        _choice("A" if correct else "B", YES_NO,
                f"箱中共 {len(balls)} 顆球，取二球有 C({len(balls)},2) = {total} 種取法。" + _dist_work(double, "最大獎額")
                + f"{_show(closed)} " + ("大於" if correct else "不大於") + f" {_show(single)}，宣稱" + ("正確。" if correct else "不正確。")),
        _value(gain, f"增加 {_show(closed)} - {_show(single)} = {_show(gain)} 元。"),
    ])


def prize_ball_expectation(*, values: Any, choice_offsets: Any, **_: Any) -> dict[str, Any]:
    return _prize_answer(values, choice_offsets)


def _check_prize(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_prize_answer(givens["values"], givens["choice_offsets"]), answer)


_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "die_payout_expectation": (die_payout_expectation, _check_die_payout, ("payouts", "style")),
    "coin_payout_expectation": (coin_payout_expectation, _check_coin_payout, ("n", "scenarios")),
    "urn_draw_expectation": (urn_draw_expectation, _check_urn, ("groups", "draw", "variable")),
    "two_dice_match_game": (two_dice_match_game, _check_two_dice, ("multiplier", "amount")),
    "single_die_game": (single_die_game, _check_single_die, ("win_set", "multiplier", "fee")),
    "insurance_expectation": (insurance_expectation, _check_insurance, ("stated_prob", "prob_kind", "payout", "ask")),
    "decision_by_expectation": (decision_by_expectation, _check_decision, ("probs", "profits", "states")),
    "expectation_claim": (expectation_claim, _check_claim, ("model", "n", "stated")),
    "multiple_choice_guess_expectation": (multiple_choice_guess_expectation, _check_guess, ("options", "known", "scores")),
    "lottery_expectation": (lottery_expectation, _check_lottery, ("total", "prizes")),
    "prize_ball_expectation": (prize_ball_expectation, _check_prize, ("values", "choice_offsets")),
}

OPERATIONS = tuple(_OPERATIONS)


def build_mathematical_expectation_matrix(
    *, domain_operation: str | None = None, seed: int | None = None, constraints: dict[str, Any] | None = None, **_: Any
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_mathematical_expectation_operation:{operation}")
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
