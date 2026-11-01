"""Per-component inputs for 普高數學2 Unit 7 數學期望值.

Each entry is the textbook stated data (variant 0) and a sampler for further variants of the same shape.
Samplers only choose the numbers a stem prints. The domain computes every answer and refuses degenerate data.
Nothing in this file is an answer.
"""

from __future__ import annotations

import random
from typing import Any

SKILLS = {"expectation": "gh_MathematicalExpectation"}

OP = {name: name for name in (
    "die_payout_expectation", "coin_payout_expectation", "urn_draw_expectation", "two_dice_match_game", "single_die_game",
    "insurance_expectation", "decision_by_expectation", "expectation_claim", "multiple_choice_guess_expectation",
    "lottery_expectation", "prize_ball_expectation",
)}

SKILL_OPERATIONS = {"expectation": sorted(OP)}

# Every formal row 12891-12911 has a generator. Nothing in this unit is held back as a fixed textbook item.
FIXED_ROWS: dict[int, str] = {}

FAMILY = {
    12891: "die_payout", 12903: "die_payout",
    12894: "coin_payout", 12896: "coin_payout",
    12892: "urn_value_sum", 12897: "urn_value_sum",
    12893: "urn_count_expectation", 12898: "urn_count_expectation", 12906: "urn_count_expectation",
    12904: "urn_event_payout", 12905: "urn_event_payout",
    12899: "fair_game", 12907: "fair_game",
    12895: "insurance_expectation", 12908: "insurance_expectation",
    12900: "expectation_decision",
    12901: "expectation_claim", 12902: "expectation_claim",
    12909: "guess_score_expectation",
    12910: "lottery_expectation",
    12911: "prize_draw_comparison",
}


def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def _g(**kw: Any) -> dict[str, Any]:
    return kw


def _die_grouped(rng: random.Random) -> dict[str, Any]:
    cuts = sorted(rng.sample(range(1, 6), 2))
    values = sorted(rng.sample(range(10, 110, 10), 3))
    sizes = [cuts[0], cuts[1] - cuts[0], 6 - cuts[1]]
    payouts = [v for v, size in zip(values, sizes) for _ in range(size)]
    return _g(style="grouped", payouts=payouts)


def _die_linear(rng: random.Random) -> dict[str, Any]:
    c = rng.randint(2, 60)
    return _g(style="linear", coef=c, payouts=[c * k for k in range(1, 7)])


def _coin_rising(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [2, 3, 4])
    step = pick(rng, [5, 10, 15, 20, 25])
    base = pick(rng, [0, 5, 10])
    return _g(n=n, scenarios=[[0] + [base + step * k for k in range(1, n + 1)]])


def _coin_loss_two_rules(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [2, 3, 4])
    step = pick(rng, [5, 10, 20])
    losses = rng.sample(range(20, 220, 20), 2)
    rest = [step * k for k in range(1, n + 1)]
    return _g(n=n, scenarios=[[-losses[0]] + rest, [-losses[1]] + rest])


def _cards(draw_choices: list[int]):
    def sample(rng: random.Random) -> dict[str, Any]:
        values = sorted(rng.sample([50, 100, 200, 300, 500, 1000], 2), reverse=True)
        counts = [rng.randint(1, 5), rng.randint(1, 5)]
        draw = pick(rng, draw_choices)
        if draw >= sum(counts):
            raise ValueError("draw_exceeds")
        return _g(scene="cards", groups=[{"name": "商品卡", "count": counts[0], "value": values[0]},
                                         {"name": "商品卡", "count": counts[1], "value": values[1]}],
                  draw=draw, variable={"kind": "sum_of_values"})

    return sample


def _count_scene(scene: str, names: list[str], index: int, draws: list[int], high: int = 9):
    def sample(rng: random.Random) -> dict[str, Any]:
        counts = [rng.randint(2, high), rng.randint(2, high)]
        draw = pick(rng, draws)
        if draw >= sum(counts):
            raise ValueError("draw_exceeds")
        return _g(scene=scene, groups=[{"name": names[0], "count": counts[0]}, {"name": names[1], "count": counts[1]}],
                  draw=draw, variable={"kind": "count", "index": index})

    return sample


def _color_prize(rng: random.Random) -> dict[str, Any]:
    counts = [rng.randint(2, 8), rng.randint(2, 8)]
    prize = pick(rng, [50, 100, 120, 150, 200, 300, 500])
    return _g(scene="color_prize", groups=[{"name": "紅球", "count": counts[0]}, {"name": "白球", "count": counts[1]}],
              draw=2, variable={"kind": "payout_by_count", "index": 0, "payouts": [[1, prize]], "default": 0})


def _melon(rng: random.Random) -> dict[str, Any]:
    a = pick(rng, [3, 4, 5])
    low = pick(rng, [20000, 21000, 22000, 24000, 25000])
    mid = low + pick(rng, [3000, 5000, 6000, 7000])
    top = mid + pick(rng, [4000, 5000, 7000, 8000])
    return _g(scene="melon", groups=[{"name": "黃肉哈密瓜", "count": a}, {"name": "綠肉哈密瓜", "count": a}], draw=a,
              variable={"kind": "payout_by_count", "index": 0, "payouts": [[a, top], [a - 1, mid]], "default": low})


def _two_dice(rng: random.Random) -> dict[str, Any]:
    m = pick(rng, [2, 3, 4, 5, 6, 8, 10, 12, 15, 20])
    a = pick(rng, [5, 6, 8, 10, 12, 15, 20, 25, 30, 40])
    if 21 * m == 30 * a:
        raise ValueError("already_fair")
    return _g(multiplier=m, amount=a)


def _single_die(rng: random.Random) -> dict[str, Any]:
    return _g(win_set=pick(rng, ["prime", "even", "odd", "high"]), multiplier=rng.randint(2, 5), fee=rng.randint(1, 9))


def _life(rng: random.Random) -> dict[str, Any]:
    survive = pick(rng, ["0.9998", "0.9995", "0.9990", "0.9996", "0.9992", "0.9985"])
    payout = pick(rng, [1000000, 2000000, 3000000, 5000000])
    premium = pick(rng, [1500, 1800, 2400, 3000, 3600, 4000, 5000, 6000, 8000])
    return _g(age=pick(rng, [40, 45, 50, 55, 60]), stated_prob=survive.rstrip("0"), prob_kind="survive", payout=payout,
              ask="profit", premium=premium)


def _fire(rng: random.Random) -> dict[str, Any]:
    prob = pick(rng, ["0.0016", "0.001", "0.0012", "0.002", "0.0025", "0.0008"])
    payout = pick(rng, [500000, 1000000, 2000000, 3000000])
    profit = pick(rng, [200, 300, 400, 500, 600, 800, 1000])
    return _g(stated_prob=prob, prob_kind="event", payout=payout, ask="premium", profit=profit)


_PROB_TRIPLES = [["0.4", "0.5", "0.1"], ["0.3", "0.5", "0.2"], ["0.2", "0.6", "0.2"], ["0.5", "0.3", "0.2"],
                 ["0.25", "0.5", "0.25"], ["0.6", "0.3", "0.1"], ["0.3", "0.4", "0.3"], ["0.1", "0.6", "0.3"]]


def _decision(rng: random.Random) -> dict[str, Any]:
    probs = pick(rng, _PROB_TRIPLES)
    a = [rng.randint(20, 60), rng.randint(5, 25), -rng.randint(5, 20)]
    b = [rng.randint(30, 80), rng.randint(0, 20), -rng.randint(10, 40)]
    return _g(states=["成長", "持平", "衰退"], probs=list(probs), profits=[a, b])


def _claim_coin(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(1, 6)
    stated = pick(rng, [f"{n}/2", f"{n}/2", f"{n}/3", str(n), f"{n + 1}/2", f"{n}/4"])
    return _g(model="coin", n=n, stated=stated)


def _claim_die(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(1, 3)
    stated = pick(rng, [f"{7 * n}/2", f"{7 * n}/2", str(3 * n), str(4 * n), f"{7 * n - 1}/2", f"{7 * n + 1}/2", str(6 * n),
                        str(7 * n), f"{5 * n}/2"])
    return _g(model="die", n=n, stated=stated)


def _guess(rng: random.Random) -> dict[str, Any]:
    m = pick(rng, [4, 5, 6])
    known = rng.randint(max(1, m - 4), m - 1)
    scores = pick(rng, [[5, 3, 1], [6, 4, 2], [4, 2, 1], [8, 5, 2], [5, 4, 2], [6, 3, 1], [10, 6, 2]])
    return _g(options=m, known=known, scores=list(scores))


def _lottery(rng: random.Random) -> dict[str, Any]:
    total = pick(rng, [100000, 200000, 500000, 1000000, 2000000])
    amounts = sorted(rng.sample([1000, 2000, 5000, 10000, 50000, 100000, 500000, 1000000, 5000000, 10000000], rng.randint(3, 5)),
                     reverse=True)
    counts = sorted(rng.sample([1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000], len(amounts)))
    return _g(total=total, prizes=[[a, c] for a, c in zip(amounts, counts)])


def _prize(rng: random.Random) -> dict[str, Any]:
    size = pick(rng, [3, 4, 5])
    values = sorted(rng.sample(range(5, 100, 5), size))
    values = [v * 100 for v in values]
    if sum(values) % size:
        raise ValueError("mean_not_integer")
    offsets = rng.sample([-800, -500, -300, -200, 200, 300, 500, 800], 4)
    offsets.insert(rng.randrange(5), 0)
    return _g(values=values, choice_offsets=offsets)


COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Any]] = {
    12891: ("expectation", "die_payout_expectation", _g(style="grouped", payouts=[10, 10, 10, 20, 20, 50]), _die_grouped),
    12892: ("expectation", "urn_draw_expectation", _g(scene="cards", groups=[
        {"name": "商品卡", "count": 3, "value": 200}, {"name": "商品卡", "count": 2, "value": 100}],
        draw=2, variable={"kind": "sum_of_values"}), _cards([2, 3])),
    12893: ("expectation", "urn_draw_expectation", _g(scene="eggs", groups=[
        {"name": "土雞蛋", "count": 2}, {"name": "普通雞蛋", "count": 8}], draw=3, variable={"kind": "count", "index": 0}),
        _count_scene("eggs", ["土雞蛋", "普通雞蛋"], 0, [2, 3, 4])),
    12894: ("expectation", "coin_payout_expectation", _g(n=3, scenarios=[[-100, 5, 10, 15], [-60, 5, 10, 15]]), _coin_loss_two_rules),
    12895: ("expectation", "insurance_expectation", _g(age=50, stated_prob="0.9998", prob_kind="survive", payout=2000000,
                                                       ask="profit", premium=2400), _life),
    12896: ("expectation", "coin_payout_expectation", _g(n=3, scenarios=[[0, 10, 20, 30]]), _coin_rising),
    12897: ("expectation", "urn_draw_expectation", _g(scene="cards", groups=[
        {"name": "商品卡", "count": 3, "value": 200}, {"name": "商品卡", "count": 2, "value": 100}],
        draw=1, variable={"kind": "sum_of_values"}), _cards([1])),
    12898: ("expectation", "urn_draw_expectation", _g(scene="balls", groups=[
        {"name": "白球", "count": 4}, {"name": "紅球", "count": 3}], draw=3, variable={"kind": "count", "index": 1}),
        _count_scene("balls", ["白球", "紅球"], 1, [2, 3, 4])),
    12899: ("expectation", "two_dice_match_game", _g(multiplier=10, amount=30), _two_dice),
    12900: ("expectation", "decision_by_expectation", _g(states=["成長", "持平", "衰退"], probs=["0.4", "0.5", "0.1"],
                                                         profits=[[40, 15, -10], [55, 10, -30]]), _decision),
    12901: ("expectation", "expectation_claim", _g(model="coin", n=1, stated="1/2"), _claim_coin),
    12902: ("expectation", "expectation_claim", _g(model="die", n=1, stated="3"), _claim_die),
    12903: ("expectation", "die_payout_expectation", _g(style="linear", coef=10, payouts=[10, 20, 30, 40, 50, 60]), _die_linear),
    12904: ("expectation", "urn_draw_expectation", _g(scene="color_prize", groups=[
        {"name": "紅球", "count": 3}, {"name": "白球", "count": 3}], draw=2,
        variable={"kind": "payout_by_count", "index": 0, "payouts": [[1, 100]], "default": 0}), _color_prize),
    12905: ("expectation", "urn_draw_expectation", _g(scene="melon", groups=[
        {"name": "黃肉哈密瓜", "count": 4}, {"name": "綠肉哈密瓜", "count": 4}], draw=4,
        variable={"kind": "payout_by_count", "index": 0, "payouts": [[4, 35000], [3, 28000]], "default": 21000}), _melon),
    12906: ("expectation", "urn_draw_expectation", _g(scene="tangyuan", groups=[
        {"name": "芝麻湯圓", "count": 6}, {"name": "花生湯圓", "count": 4}], draw=4, variable={"kind": "count", "index": 0}),
        _count_scene("tangyuan", ["芝麻湯圓", "花生湯圓"], 0, [3, 4, 5])),
    12907: ("expectation", "single_die_game", _g(win_set="prime", multiplier=3, fee=4), _single_die),
    12908: ("expectation", "insurance_expectation", _g(stated_prob="0.0016", prob_kind="event", payout=1000000,
                                                       ask="premium", profit=400), _fire),
    12909: ("expectation", "multiple_choice_guess_expectation", _g(options=5, known=2, scores=[5, 3, 1]), _guess),
    12910: ("expectation", "lottery_expectation", _g(total=1000000, prizes=[
        [10000000, 1], [5000000, 2], [1000000, 5], [100000, 20], [10000, 100], [1000, 1000]]), _lottery),
    12911: ("expectation", "prize_ball_expectation", _g(values=[1000, 2000, 3000, 7200], choice_offsets=[-500, -300, 0, 200, 500]),
            _prize),
}
