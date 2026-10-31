"""Per-component inputs for 普高數學2 Unit 6 古典機率.

Each entry is the textbook stated data (variant 0) and a sampler for further variants of the same shape.
Samplers only choose the numbers a stem prints. The domain computes every answer and refuses a degenerate sample space.
Nothing in this file is an answer.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any

SKILLS = {
    "sample": "gh_SampleSpace",
    "event": "gh_Event",
    "classical": "gh_DefinitionOfClassicalProbability",
    "properties": "gh_PropertiesOfProbability",
}

OP = {name: name for name in (
    "coin_outcome_space", "draw_outcome_space", "coded_event_sets", "dice_event_sets", "event_relation",
    "uniform_draw_probability", "coin_count_probability", "dice_count_probability", "urn_draw_probability",
    "replacement_count_probability", "probability_algebra", "password_guess", "solve_urn_count", "classical_claim",
)}

SKILL_OPERATIONS = {
    "sample": ["coin_outcome_space", "draw_outcome_space", "coded_event_sets"],
    "event": ["dice_event_sets", "event_relation"],
    "classical": ["uniform_draw_probability", "coin_count_probability", "dice_count_probability", "urn_draw_probability",
                  "replacement_count_probability", "password_guess", "solve_urn_count", "classical_claim"],
    "properties": ["probability_algebra", "urn_draw_probability", "dice_count_probability", "replacement_count_probability"],
}

# Every formal row 12849-12890 has a generator. Nothing in this unit is held back as a fixed textbook item.
FIXED_ROWS: dict[int, str] = {}

FAMILY = {
    12849: "coin_sequence_space", 12851: "coin_sequence_space",
    12850: "draw_sample_space", 12852: "draw_sample_space",
    12853: "coded_named_events", 12854: "coded_named_events",
    12855: "two_dice_event_sets", 12857: "two_dice_event_sets",
    12856: "event_complement_mutex", 12858: "event_complement_mutex", 12859: "event_complement_mutex",
    12860: "single_draw", 12866: "single_draw", 12879: "single_draw",
    12861: "coin_count", 12862: "coin_count", 12868: "coin_count",
    12863: "numbered_dice", 12865: "numbered_dice", 12869: "numbered_dice", 12871: "numbered_dice",
    12875: "numbered_dice", 12876: "numbered_dice", 12881: "numbered_dice", 12887: "numbered_dice",
    12864: "urn_without_replacement", 12870: "urn_without_replacement", 12877: "urn_without_replacement",
    12878: "urn_without_replacement", 12880: "urn_without_replacement", 12882: "urn_without_replacement",
    12886: "urn_without_replacement", 12889: "urn_without_replacement",
    12867: "with_replacement", 12890: "with_replacement",
    12872: "classical_claim", 12873: "classical_claim", 12874: "classical_claim",
    12883: "password_permutation", 12884: "solve_composition",
    12885: "probability_algebra", 12888: "probability_algebra",
}


def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def _g(**kw: Any) -> dict[str, Any]:
    return kw


def _size(mode: str, n: int, k: int) -> int:
    if mode == "ordered_no_replace":
        return math.perm(n, k)
    if mode == "ordered_replace":
        return n**k
    return math.comb(n, k)


def _coin_obs(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(2, 5)
    kind = pick(rng, ["head_count", "tail_count", "toss"])
    observable: dict[str, Any] = {"kind": kind}
    if kind == "toss":
        observable["index"] = rng.randrange(n)
    return {"n": n, "observable": observable}


def _draw_pair(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [3, 4, 5])
    labels = sorted(rng.sample(range(1, 9), n))
    k_hi = 2 if n >= 5 else pick(rng, [2, 3])
    asks = [{"mode": "ordered_no_replace", "k": k_hi}, {"mode": "unordered", "k": pick(rng, [2, k_hi])}]
    if any(_size(a["mode"], n, a["k"]) > 36 for a in asks):
        raise ValueError("big")
    return {"n": n, "labels": labels, "asks": asks}


def _draw_three(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [3, 4])
    labels = sorted(rng.sample(range(1, 9), n))
    asks = [
        {"mode": "ordered_no_replace", "k": n if n == 3 else 2},
        {"mode": "ordered_replace", "k": 2},
        {"mode": "unordered", "k": 2},
    ]
    if any(_size(a["mode"], n, a["k"]) > 36 for a in asks):
        raise ValueError("big")
    return {"n": n, "labels": labels, "asks": asks}


def _gender(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(2, 5)
    symbol = pick(rng, [0, 1])
    k = rng.randint(1, n - 1)
    return {"n": n, "story": "gender", "asks": [
        {"kind": "space"},
        {"kind": "at_least_symbol", "symbol": 0, "k": 1},
        {"kind": "exactly_symbol", "symbol": symbol, "k": k},
    ]}


def _named_coin(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(3, 5)
    index = rng.randrange(n)
    value = pick(rng, [0, 1])
    k = rng.randint(1, n - 1)
    at_least = {"kind": "at_least_symbol", "symbol": 1, "k": k}
    return {"n": n, "story": "coin", "asks": [
        {"kind": "and", "left": at_least, "right": {"kind": "bit_is", "index": index, "value": value}},
        {"kind": "complement", "event": at_least},
        {"kind": "and", "left": at_least, "right": {"kind": "bit_is", "index": index, "value": 1 - value}},
    ]}


_SET_PAIRS = [
    ({"kind": "sum_gt", "n": 9}, {"kind": "faces_equal"}),
    ({"kind": "sum_gt", "n": 8}, {"kind": "faces_equal"}),
    ({"kind": "sum_gt", "n": 7}, {"kind": "faces_equal"}),
    ({"kind": "sum_gt", "n": 6}, {"kind": "faces_equal"}),
    ({"kind": "sum_gt", "n": 10}, {"kind": "faces_equal"}),
    ({"kind": "sum_eq", "n": 7}, {"kind": "product_eq", "n": 12}),
    ({"kind": "sum_eq", "n": 7}, {"kind": "product_eq", "n": 10}),
    ({"kind": "sum_eq", "n": 7}, {"kind": "product_eq", "n": 6}),
    ({"kind": "sum_eq", "n": 8}, {"kind": "product_eq", "n": 12}),
    ({"kind": "sum_eq", "n": 8}, {"kind": "product_eq", "n": 15}),
    ({"kind": "sum_eq", "n": 9}, {"kind": "product_eq", "n": 18}),
    ({"kind": "sum_eq", "n": 9}, {"kind": "product_eq", "n": 20}),
    ({"kind": "sum_eq", "n": 10}, {"kind": "product_eq", "n": 24}),
    ({"kind": "sum_eq", "n": 10}, {"kind": "faces_equal"}),
    ({"kind": "sum_eq", "n": 6}, {"kind": "product_eq", "n": 8}),
    ({"kind": "sum_eq", "n": 6}, {"kind": "product_eq", "n": 5}),
    ({"kind": "sum_eq", "n": 5}, {"kind": "product_eq", "n": 6}),
    ({"kind": "sum_eq", "n": 4}, {"kind": "product_eq", "n": 4}),
    ({"kind": "first_even"}, {"kind": "faces_equal"}),
    ({"kind": "first_gt_second"}, {"kind": "sum_eq", "n": 9}),
    ({"kind": "both_gt", "n": 3}, {"kind": "faces_equal"}),
    ({"kind": "exactly_one_face", "face": 6}, {"kind": "sum_eq", "n": 9}),
    ({"kind": "diff_eq", "n": 1}, {"kind": "sum_eq", "n": 7}),
    ({"kind": "both_gt", "n": 2}, {"kind": "sum_gt", "n": 9}),
]


def _set_pair(rng: random.Random) -> dict[str, Any]:
    a, b = pick(rng, _SET_PAIRS)
    return {"a": dict(a), "b": dict(b)}


_MUTEX_PAIRS = [
    ({"kind": "first_even"}, {"kind": "sum_odd"}),
    ({"kind": "first_even"}, {"kind": "first_odd"}),
    ({"kind": "faces_equal"}, {"kind": "diff_eq", "n": 1}),
    ({"kind": "faces_equal"}, {"kind": "diff_eq", "n": 2}),
    ({"kind": "sum_eq", "n": 7}, {"kind": "sum_eq", "n": 8}),
    ({"kind": "sum_eq", "n": 7}, {"kind": "sum_gt", "n": 9}),
    ({"kind": "sum_gt", "n": 9}, {"kind": "sum_eq", "n": 12}),
    ({"kind": "first_gt_second"}, {"kind": "first_lt_second"}),
    ({"kind": "first_gt_second"}, {"kind": "faces_equal"}),
    ({"kind": "both_gt", "n": 4}, {"kind": "sum_eq", "n": 6}),
    ({"kind": "exactly_one_face", "face": 6}, {"kind": "faces_equal"}),
    ({"kind": "product_eq", "n": 12}, {"kind": "sum_eq", "n": 2}),
    ({"kind": "first_even"}, {"kind": "second_even"}),
    ({"kind": "sum_odd"}, {"kind": "sum_even"}),
    ({"kind": "diff_eq", "n": 5}, {"kind": "sum_eq", "n": 7}),
    ({"kind": "both_gt", "n": 3}, {"kind": "diff_eq", "n": 1}),
    ({"kind": "first_odd"}, {"kind": "sum_even"}),
    ({"kind": "sum_eq", "n": 3}, {"kind": "product_eq", "n": 2}),
    ({"kind": "sum_gt", "n": 10}, {"kind": "faces_equal"}),
    ({"kind": "exactly_one_face", "face": 1}, {"kind": "both_gt", "n": 3}),
    ({"kind": "sum_eq", "n": 12}, {"kind": "sum_eq", "n": 2}),
    ({"kind": "first_lt_second"}, {"kind": "both_gt", "n": 4}),
]


def _mutex_dice(rng: random.Random) -> dict[str, Any]:
    a, b = pick(rng, _MUTEX_PAIRS)
    return {"model": "dice", "a": dict(a), "b": dict(b)}


def _coin_rel(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(2, 5)

    def one() -> dict[str, Any]:
        if rng.random() < 0.5:
            return {"kind": "exactly_heads", "k": rng.randint(0, n)}
        return {"kind": "at_least_heads", "k": rng.randint(1, n)}

    a, b = one(), one()
    if a == b:
        raise ValueError("same_event")
    return {"model": "coin", "n": n, "a": a, "b": b}


def _die_uniform(rng: random.Random) -> dict[str, Any]:
    face = rng.randint(1, 6)
    values = sorted(rng.sample(range(1, 7), rng.randint(1, 5)))
    return {"model": "die", "faces": 6, "asks": [{"kind": "face", "face": face}, {"kind": "faces", "values": values}]}


def _cards(rng: random.Random) -> dict[str, Any]:
    count = rng.randint(1, 5)
    rank = pick(rng, [1, 6, 7, 10, 13])
    suit = pick(rng, ["黑桃", "紅心", "方塊", "梅花"])
    return {"model": "cards", "deck": 52, "suits": 4, "asks": [
        {"kind": "ranks", "count": count, "rank": rank}, {"kind": "suit", "suit": suit},
    ]}


def _numbers(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(12, 36)
    divisors = list(pick(rng, [(2, 3), (2, 5), (3, 4), (3, 5), (4, 6), (2, 7), (3, 7), (5, 6)]))
    return {"model": "numbers", "n": n, "asks": [{"kind": "divisible_by_any", "divisors": divisors}]}


def _coin_two(rng: random.Random) -> dict[str, Any]:
    asks = []
    for _ in range(2):
        n = rng.randint(2, 6)
        asks.append({"n": n, "k": rng.randint(0, n)})
    if asks[0] == asks[1]:
        raise ValueError("same")
    return {"asks": asks}


def _coin_one(rng: random.Random, *, simultaneous: bool = False) -> dict[str, Any]:
    n = rng.randint(2, 8)
    out = {"asks": [{"n": n, "k": rng.randint(0, n)}]}
    if simultaneous:
        out["simultaneous"] = True
    return out


def _sums(rng: random.Random) -> dict[str, Any]:
    a, b = rng.randint(2, 12), rng.randint(2, 12)
    if a == b:
        raise ValueError("same")
    return {"dice": 2, "faces": 6, "asks": [{"kind": "sum_eq", "n": a}, {"kind": "sum_eq", "n": b}]}


def _three_patterns(rng: random.Random) -> dict[str, Any]:
    second = pick(rng, ["exactly_two_equal", "all_equal", "at_least_two_equal"])
    return {"dice": 3, "faces": rng.randint(4, 12), "asks": [{"kind": "all_different"}, {"kind": second}]}


def _two_face_diff(rng: random.Random) -> dict[str, Any]:
    face = rng.randint(1, 6)
    gap = rng.randint(1, 5)
    return {"dice": 2, "faces": 6, "asks": [
        {"kind": "exactly_face_count", "face": face, "count": 1},
        {"kind": "diff_eq", "n": gap},
    ]}


def _equal_and_order(rng: random.Random) -> dict[str, Any]:
    faces = rng.randint(4, 12)
    second: dict[str, Any] = {"kind": pick(rng, ["first_gt_second", "diff_eq"])}
    if second["kind"] == "diff_eq":
        second["n"] = rng.randint(0, faces - 1)
    return {"dice": 2, "faces": faces, "asks": [{"kind": "faces_equal"}, second]}


def _both_and_diff(rng: random.Random) -> dict[str, Any]:
    return {"dice": 2, "faces": 6, "asks": [
        {"kind": "both_gt", "n": rng.randint(1, 4)},
        {"kind": "diff_eq", "n": rng.randint(0, 5)},
    ]}


def _one_face_three(rng: random.Random) -> dict[str, Any]:
    faces = rng.randint(4, 12)
    return {"dice": 3, "faces": faces, "asks": [{
        "kind": "exactly_face_count", "face": rng.randint(1, faces), "count": rng.randint(0, 2),
    }]}


def _at_least_and_sum(rng: random.Random) -> dict[str, Any]:
    faces = 6
    return {"dice": 3, "faces": faces, "asks": [
        {"kind": "at_least_face", "face": rng.randint(1, faces), "count": 1},
        {"kind": "sum_eq", "n": rng.randint(3, 18)},
    ]}


def _prize(rng: random.Random) -> dict[str, Any]:
    dice = pick(rng, [2, 3])
    kind = "at_least_two_equal" if dice == 3 else pick(rng, ["at_least_two_equal", "faces_equal", "all_different"])
    if dice == 2 and kind == "at_least_two_equal":
        kind = "faces_equal"
    return {"dice": dice, "faces": rng.randint(4, 12), "asks": [{"kind": kind}]}


def _urn_exact_both(rng: random.Random) -> dict[str, Any]:
    red, white = rng.randint(2, 6), rng.randint(1, 5)
    if red + white > 12 or red < 2:
        raise ValueError("size")
    return {"colors": [red, white], "names": ["紅球", "白球"], "draw": 2, "asks": [
        {"kind": "exact", "counts": [2, 0], "ordered": True},
        {"kind": "exact", "counts": [2, 0], "ordered": False},
    ]}


def _urn_mixed_both(rng: random.Random) -> dict[str, Any]:
    red, white = rng.randint(1, 6), rng.randint(1, 6)
    if red + white > 12:
        raise ValueError("size")
    return {"colors": [red, white], "names": ["紅球", "白球"], "draw": 2, "asks": [
        {"kind": "exact", "counts": [1, 1], "ordered": True},
        {"kind": "exact", "counts": [1, 1], "ordered": False},
    ]}


def _urn_seq_three(rng: random.Random) -> dict[str, Any]:
    a, b = rng.randint(3, 7), rng.randint(2, 6)
    counts = [2, 1] if rng.random() < 0.5 else [1, 2]
    if counts[0] > a or counts[1] > b or not 5 <= a + b <= 16:
        raise ValueError("size")
    return {"colors": [a, b], "names": ["紅球", "白球"], "draw": 3, "asks": [
        {"kind": "exact", "counts": counts, "ordered": True},
        {"kind": "not_mono", "ordered": True},
    ]}


def _urn_sim_three(rng: random.Random) -> dict[str, Any]:
    a, b = rng.randint(3, 7), rng.randint(2, 6)
    counts = [2, 1] if rng.random() < 0.5 else [1, 2]
    if counts[0] > a or counts[1] > b or not 5 <= a + b <= 16:
        raise ValueError("size")
    return {"colors": [a, b], "names": ["紅球", "白球"], "draw": 3, "asks": [
        {"kind": "exact", "counts": counts, "ordered": False},
        {"kind": "not_mono", "ordered": False},
    ]}


def _grades(rng: random.Random) -> dict[str, Any]:
    colors = [rng.randint(2, 6) for _ in range(3)]
    if sum(colors) < 4 or sum(colors) > 16:
        raise ValueError("size")
    return {"colors": colors, "names": ["甲等", "乙等", "丙等"], "draw": 2, "asks": [{"kind": "not_mono", "ordered": False}]}


def _signs(rng: random.Random) -> dict[str, Any]:
    pos, neg = rng.randint(2, 6), rng.randint(2, 6)
    if pos + neg > 12:
        raise ValueError("size")
    return {"colors": [pos, neg], "names": ["正數", "負數"], "draw": 2, "asks": [{"kind": "same_color", "ordered": False}]}


def _at_most_one(rng: random.Random) -> dict[str, Any]:
    pork, beef = rng.randint(3, 7), rng.randint(2, 5)
    if pork + beef > 12 or pork < 2:
        raise ValueError("size")
    return {"colors": [pork, beef], "names": ["豬肉", "牛肉"], "draw": 3, "asks": [
        {"kind": "at_most", "index": 1, "count": 1, "ordered": False},
    ]}


def _mixed_people(rng: random.Random) -> dict[str, Any]:
    boys, girls = rng.randint(3, 8), rng.randint(2, 6)
    if boys + girls < 5 or boys + girls > 16:
        raise ValueError("size")
    return {"colors": [boys, girls], "names": ["男生", "女生"], "draw": 3, "asks": [{"kind": "not_mono", "ordered": False}]}


def _replace_balls(rng: random.Random) -> dict[str, Any]:
    sides = rng.randint(2, 6)
    target = rng.randint(1, sides)
    n1, n2 = rng.randint(2, 3), rng.randint(2, 4)
    return {"sides": sides, "labels": list(range(1, sides + 1)), "asks": [
        {"n": n1, "kind": "at_least", "k": rng.randint(1, n1), "target": target},
        {"n": n2, "kind": "exactly", "k": rng.randint(0, n2), "target": target},
    ]}


def _clubs(rng: random.Random) -> dict[str, Any]:
    return {"sides": rng.randint(2, 8), "scene": "club", "asks": [
        {"n": rng.randint(2, 4), "kind": "not_all_different", "scene_line": "club"},
    ]}


_DISJOINT = [
    ["1/2", "1/4", "1/8"], ["1/2", "1/3", "1/7"], ["1/3", "1/3", "1/3"], ["2/5", "1/5", "1/5"],
    ["1/4", "1/4", "1/4"], ["1/2", "1/5", "1/5"], ["1/3", "1/4", "1/5"], ["1/6", "1/6", "1/6"],
    ["1/2", "1/6", "1/6"], ["2/7", "1/7", "1/7"], ["1/3", "1/6", "1/6"], ["3/8", "1/8", "1/8"],
    ["1/4", "1/3", "1/6"], ["1/5", "1/5", "1/5"], ["2/9", "1/9", "1/9"], ["1/2", "1/4", "1/6"],
    ["1/3", "1/5", "1/15"], ["2/5", "3/10", "1/5"], ["1/2", "1/8", "1/8"], ["1/4", "1/5", "1/6"],
    ["1/2", "1/10", "1/10"], ["3/10", "1/5", "1/10"],
]


def _disjoint(rng: random.Random) -> dict[str, Any]:
    return {"probs": list(pick(rng, _DISJOINT)), "pairwise_disjoint": True, "asks": [
        {"kind": "union", "indices": [0, 1]},
        {"kind": "union", "indices": [0, 1, 2]},
    ]}


def _algebra(rng: random.Random) -> dict[str, Any]:
    a = Fraction(rng.randint(1, 3), pick(rng, [3, 4, 5, 6]))
    b = Fraction(rng.randint(1, 3), pick(rng, [3, 4, 5, 6]))
    if a > 1 or b > 1:
        raise ValueError("prob")
    cap = min(a, b)
    inter = Fraction(rng.randint(0, 4), 12)
    if inter > cap:
        raise ValueError("inter")
    union = a + b - inter
    if union > 1:
        raise ValueError("union")
    return {"probs": [str(a), str(b)], "asks": [
        {"kind": "complement", "index": 0},
        {"kind": "union", "indices": [0, 1], "intersection": str(inter)},
        {"kind": "intersection", "indices": [0, 1], "union": str(union)},
    ]}


def _password(rng: random.Random) -> dict[str, Any]:
    symbols = rng.randint(3, 6)
    limit = rng.randint(1, min(4, math.factorial(symbols) - 1))
    out: dict[str, Any] = {"symbols": symbols, "wrong_limit": limit}
    if symbols == 4 and rng.random() < 0.3:
        out["alphabet"] = [1, 3, 5, 7]
    return out


def _solve(rng: random.Random) -> dict[str, Any]:
    white = rng.randint(4, 12)
    black = rng.randint(2, 16)
    goal = Fraction(math.comb(white, 2), math.comb(white + black, 2))
    return {"white": white, "target": f"{goal.numerator}/{goal.denominator}"}


def _claim_urn(rng: random.Random) -> dict[str, Any]:
    if rng.random() < 0.25:
        return {"style": "urn_half", "red": None}
    red, white = rng.randint(1, 8), rng.randint(1, 8)
    return {"style": "urn_half", "red": red, "white": white}


def _claim_sum(rng: random.Random) -> dict[str, Any]:
    total = rng.randint(2, 12)
    stated = pick(rng, ["1/36", "1/18", "1/12", "1/9", "1/6", "5/36", "1/4"])
    return {"style": "dice_sum", "total": total, "stated": stated}


def _claim_six(rng: random.Random) -> dict[str, Any]:
    return {"style": "at_least_one_six", "stated_miss": rng.randint(1, 35)}


_EXACT_RED = [{"kind": "exact", "counts": [2, 0], "ordered": True}, {"kind": "exact", "counts": [2, 0], "ordered": False}]
_EXACT_MIX = [{"kind": "exact", "counts": [1, 1], "ordered": True}, {"kind": "exact", "counts": [1, 1], "ordered": False}]

COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Any]] = {
    12849: ("sample", "coin_outcome_space", _g(n=2, observable={"kind": "head_count"}), _coin_obs),
    12851: ("sample", "coin_outcome_space", _g(n=3, observable={"kind": "head_count"}), _coin_obs),
    12850: ("sample", "draw_outcome_space", _g(n=4, asks=[{"mode": "ordered_no_replace", "k": 2}, {"mode": "unordered", "k": 2}]), _draw_pair),
    12852: ("sample", "draw_outcome_space", _g(n=3, asks=[
        {"mode": "ordered_no_replace", "k": 3}, {"mode": "ordered_replace", "k": 2}, {"mode": "unordered", "k": 2},
    ]), _draw_three),
    12853: ("sample", "coded_event_sets", _g(n=2, story="gender", asks=[
        {"kind": "space"}, {"kind": "at_least_symbol", "symbol": 0, "k": 1}, {"kind": "exactly_symbol", "symbol": 0, "k": 1},
    ]), _gender),
    12854: ("sample", "coded_event_sets", _g(n=3, story="coin", asks=[
        {"kind": "and", "left": {"kind": "at_least_symbol", "symbol": 1, "k": 1}, "right": {"kind": "bit_is", "index": 1, "value": 0}},
        {"kind": "complement", "event": {"kind": "at_least_symbol", "symbol": 1, "k": 1}},
        {"kind": "and", "left": {"kind": "at_least_symbol", "symbol": 1, "k": 1}, "right": {"kind": "bit_is", "index": 1, "value": 1}},
    ]), _named_coin),
    12855: ("event", "dice_event_sets", _g(a={"kind": "sum_gt", "n": 9}, b={"kind": "faces_equal"}), _set_pair),
    12857: ("event", "dice_event_sets", _g(a={"kind": "sum_eq", "n": 7}, b={"kind": "product_eq", "n": 12}), _set_pair),
    12856: ("event", "event_relation", _g(model="coin", n=2, a={"kind": "exactly_heads", "k": 1}, b={"kind": "exactly_heads", "k": 0}), _coin_rel),
    12858: ("event", "event_relation", _g(model="coin", n=3, a={"kind": "at_least_heads", "k": 1}, b={"kind": "exactly_heads", "k": 3}), _coin_rel),
    12859: ("event", "event_relation", _g(model="dice", a={"kind": "first_even"}, b={"kind": "sum_odd"}), _mutex_dice),
    12860: ("classical", "uniform_draw_probability", _g(model="die", faces=6, asks=[
        {"kind": "face", "face": 6}, {"kind": "faces", "values": [2, 3, 5]},
    ]), _die_uniform),
    12866: ("classical", "uniform_draw_probability", _g(model="cards", deck=52, suits=4, asks=[
        {"kind": "ranks", "count": 1, "rank": 6}, {"kind": "suit", "suit": "紅心"},
    ]), _cards),
    12879: ("classical", "uniform_draw_probability", _g(model="numbers", n=24, asks=[
        {"kind": "divisible_by_any", "divisors": [2, 3]},
    ]), _numbers),
    12861: ("classical", "coin_count_probability", _g(asks=[{"n": 2, "k": 1}, {"n": 3, "k": 2}]), _coin_two),
    12862: ("classical", "coin_count_probability", _g(simultaneous=True, asks=[{"n": 2, "k": 1}]), lambda rng: _coin_one(rng, simultaneous=True)),
    12868: ("classical", "coin_count_probability", _g(asks=[{"n": 3, "k": 3}, {"n": 3, "k": 1}]), _coin_two),
    12863: ("classical", "dice_count_probability", _g(dice=2, faces=6, asks=[{"kind": "sum_eq", "n": 9}, {"kind": "sum_eq", "n": 7}]), _sums),
    12869: ("classical", "dice_count_probability", _g(dice=2, faces=6, asks=[
        {"kind": "exactly_face_count", "face": 5, "count": 1}, {"kind": "diff_eq", "n": 1},
    ]), _two_face_diff),
    12875: ("classical", "dice_count_probability", _g(dice=2, faces=6, asks=[
        {"kind": "faces_equal"}, {"kind": "first_gt_second"},
    ]), _equal_and_order),
    12876: ("classical", "dice_count_probability", _g(dice=2, faces=6, asks=[
        {"kind": "both_gt", "n": 3}, {"kind": "diff_eq", "n": 3},
    ]), _both_and_diff),
    12865: ("classical", "dice_count_probability", _g(dice=3, faces=6, asks=[
        {"kind": "all_different"}, {"kind": "exactly_two_equal"},
    ]), _three_patterns),
    12871: ("classical", "dice_count_probability", _g(dice=3, faces=6, asks=[
        {"kind": "exactly_face_count", "face": 6, "count": 1},
    ]), _one_face_three),
    12881: ("classical", "dice_count_probability", _g(dice=3, faces=6, asks=[
        {"kind": "at_least_face", "face": 6, "count": 1}, {"kind": "sum_eq", "n": 9},
    ]), _at_least_and_sum),
    12864: ("classical", "urn_draw_probability", _g(colors=[3, 2], names=["紅球", "白球"], draw=2, asks=list(_EXACT_RED)), _urn_exact_both),
    12870: ("classical", "urn_draw_probability", _g(colors=[3, 2], names=["紅球", "白球"], draw=2, asks=list(_EXACT_MIX)), _urn_mixed_both),
    12877: ("classical", "urn_draw_probability", _g(colors=[3, 3], names=["紅球", "白球"], draw=3, asks=[
        {"kind": "exact", "counts": [2, 1], "ordered": True}, {"kind": "not_mono", "ordered": True},
    ]), _urn_seq_three),
    12878: ("classical", "urn_draw_probability", _g(colors=[4, 2], names=["紅球", "白球"], draw=3, asks=[
        {"kind": "exact", "counts": [2, 1], "ordered": False}, {"kind": "not_mono", "ordered": False},
    ]), _urn_sim_three),
    12880: ("classical", "urn_draw_probability", _g(colors=[5, 11, 4], names=["甲等", "乙等", "丙等"], draw=2, asks=[
        {"kind": "not_mono", "ordered": False},
    ]), _grades),
    12882: ("classical", "urn_draw_probability", _g(colors=[4, 3], names=["正數", "負數"], draw=2, asks=[
        {"kind": "same_color", "ordered": False},
    ]), _signs),
    12867: ("classical", "replacement_count_probability", _g(sides=3, labels=[1, 2, 3], asks=[
        {"n": 2, "kind": "at_least", "k": 1, "target": 3}, {"n": 3, "kind": "exactly", "k": 2, "target": 3},
    ]), _replace_balls),
    12872: ("classical", "classical_claim", _g(style="urn_half", red=None), _claim_urn),
    12873: ("classical", "classical_claim", _g(style="dice_sum", total=11, stated="1/36"), _claim_sum),
    12874: ("classical", "classical_claim", _g(style="at_least_one_six", stated_miss=25), _claim_six),
    12883: ("classical", "password_guess", _g(symbols=4, wrong_limit=3, alphabet=[1, 3, 5, 7]), _password),
    12884: ("classical", "solve_urn_count", _g(white=5, target="2/21"), _solve),
    12885: ("properties", "probability_algebra", _g(probs=["1/3", "1/2"], asks=[
        {"kind": "complement", "index": 0},
        {"kind": "union", "indices": [0, 1], "intersection": "1/6"},
        {"kind": "intersection", "indices": [0, 1], "union": "5/6"},
    ]), _algebra),
    12888: ("properties", "probability_algebra", _g(probs=["1/2", "3/10", "1/30"], pairwise_disjoint=True, asks=[
        {"kind": "union", "indices": [0, 1]},
        {"kind": "union", "indices": [0, 1, 2]},
    ]), _disjoint),
    12886: ("properties", "urn_draw_probability", _g(colors=[6, 4], names=["豬肉", "牛肉"], draw=3, asks=[
        {"kind": "at_most", "index": 1, "count": 1, "ordered": False},
    ]), _at_most_one),
    12889: ("properties", "urn_draw_probability", _g(colors=[4, 2], names=["男生", "女生"], draw=3, asks=[
        {"kind": "not_mono", "ordered": False},
    ]), _mixed_people),
    12887: ("properties", "dice_count_probability", _g(dice=3, faces=6, asks=[{"kind": "at_least_two_equal"}]), _prize),
    12890: ("properties", "replacement_count_probability", _g(sides=6, scene="club", asks=[
        {"n": 4, "kind": "not_all_different", "scene_line": "club"},
    ]), _clubs),
}
