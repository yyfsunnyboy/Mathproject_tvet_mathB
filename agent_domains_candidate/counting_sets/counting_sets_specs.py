"""Per-component *inputs* for 普高數學2 Unit 3 計數原理 — skills ``gh_LogicAndSets`` and ``gh_CountingPrinciples`` (textbook ids 12744-12773).

Each entry gives the source-faithful stated data (variant 0) and a sampler for further variants of the same shape.  Samplers only choose
the numbers a stem prints; the domain computes every answer and refuses degenerate inputs, which the sandbox then skips.  Nothing here is an answer.
"""

from __future__ import annotations

import math
import random
from typing import Any

SKILLS = {"logic": "gh_LogicAndSets", "counting": "gh_CountingPrinciples"}

_NEGATION = ("寫出兩個命題的否定命題（自由文字）：沒有已授權的自由文字／命題文字等價判分契約，不以字串比對或 AI 判斷替代；"
             "題型沒有可驗證的作答形式，改為教材原題自評（FIXED_UNGRADED），解答以真值表逐一驗證（德摩根律）")
DEFERRED: dict[int, str] = {
    12746: _NEGATION + "：隨堂練習2「2是偶數且2是質數」「π=3或π是正數」的否定命題",
}

OP = {name: name for name in (
    "interval_set_operations", "finite_set_operations", "equation_root_sets", "proposition_truth", "implication_truth", "condition_relation",
    "choice_product", "grade_selection", "divisor_counting", "at_least_one_pairing", "ordered_at_least_one", "two_set_counting",
    "three_set_counting", "multiples_counting", "coin_payment", "dice_sum_multiples", "race_outcomes", "graph_paths",
    "coin_toss_sequences", "tiling_count", "region_pairs_claim")}
SKILL_OPERATIONS = {
    "logic": ["interval_set_operations", "finite_set_operations", "equation_root_sets", "proposition_truth", "implication_truth", "condition_relation"],
    "counting": ["choice_product", "grade_selection", "divisor_counting", "at_least_one_pairing", "ordered_at_least_one", "two_set_counting",
                 "three_set_counting", "multiples_counting", "coin_payment", "dice_sum_multiples", "race_outcomes", "graph_paths",
                 "coin_toss_sequences", "tiling_count", "region_pairs_claim"],
}


def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def _g(**kw: Any) -> dict[str, Any]:
    return kw


# --- sets ------------------------------------------------------------------------------------------------------------------------------

def _intervals(rng: random.Random) -> dict[str, Any]:
    a = rng.randint(-5, 5)
    b = a + rng.randint(3, 7)
    c = rng.randint(a + 1, b - 1)
    d = b + rng.randint(1, 5)
    closed = [True, True, True, False]
    items = pick(rng, [["intersection", "union", "a_minus_b", "a_complement"], ["intersection", "union", "b_minus_a", "b_complement"]])
    return {"A": {"lo": a, "hi": b, "lc": pick(rng, closed), "hc": pick(rng, closed)}, "B": {"lo": c, "hi": d, "lc": pick(rng, closed), "hc": pick(rng, closed)},
            "items": items}


def _universe_sets(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(5, 9)
    universe = list(range(1, n + 1))
    a = sorted(rng.sample(universe, rng.randint(3, min(5, n - 1))))
    b = sorted(rng.sample(universe, rng.randint(3, min(5, n - 1))))
    return {"universe": universe, "A": a, "B": b, "items": ["intersection", "union", "a_minus_b", "a_complement"]}


def _plain_sets(rng: random.Random) -> dict[str, Any]:
    a = sorted(rng.sample(range(1, 10), rng.randint(3, 5)))
    b = sorted(rng.sample(range(1, 10), rng.randint(3, 5)))
    return {"A": a, "B": b, "items": ["intersection", "union", "a_minus_b", "b_minus_a"]}


def _equation_sets(rng: random.Random) -> dict[str, Any]:
    r = rng.randint(1, 4)
    p, q = rng.sample(range(-4, 6), 2)
    if r not in (abs(p), abs(q)):
        raise ValueError("no_common_member")
    return {"A": {"kind": "square", "rhs": r * r}, "B": {"kind": "quad", "b": -(p + q), "c": p * q}, "items": ["intersection", "union"]}


# --- propositions ---------------------------------------------------------------------------------------------------------------------

_FACT_IDS = ["rect_square", "eq_tri_isos", "square_rect", "rhombus_square", "para_rect", "square_rhombus", "prime_odd", "even_div2", "isos_equi", "rect_diag", "tri_angles"]
_OPTIONS_POOL = [["atom", 0], ["atom", 1], ["atom", 2], ["and", 0, 1], ["and", 0, 2], ["and", 1, 2], ["or", 0, 1], ["or", 0, 2], ["or", 1, 2]]


def _compare_atom(rng: random.Random) -> dict[str, Any]:
    a, b = rng.sample(range(1, 12), 2)
    return {"kind": "compare", "a": a, "op": pick(rng, [">", "<"]), "b": b}


def _prop_atom(rng: random.Random) -> dict[str, Any]:
    if rng.random() < 0.5:
        return {"kind": "prop", "n": rng.randint(4, 40), "prop": pick(rng, ["prime", "even", "odd"])}
    k = pick(rng, [3, 4, 5, 6, 7])
    return {"kind": "prop", "n": rng.randint(8, 60), "prop": "multiple_of", "k": k}


def _select_true(rng: random.Random) -> dict[str, Any]:
    ids = rng.sample(_FACT_IDS, 2)
    atoms = [{"kind": "fact", "id": ids[0]}, {"kind": "fact", "id": ids[1]}, pick(rng, [_compare_atom, _prop_atom])(rng)]
    options = rng.sample(_OPTIONS_POOL, 5)
    return {"atoms": atoms, "options": options, "mode": "select_true"}


def _compound_truth(rng: random.Random) -> dict[str, Any]:
    atoms = [pick(rng, [_compare_atom, _prop_atom])(rng), pick(rng, [_compare_atom, _prop_atom])(rng)]
    return {"atoms": atoms, "options": [[pick(rng, ["and", "or"]), 0, 1]], "mode": "truth"}


def _claim(rng: random.Random) -> dict[str, Any]:
    from agent_domains_candidate.counting_sets.counting_sets_domain import CLAIMS

    return {"claim": pick(rng, sorted(CLAIMS))}


def _condition(rng: random.Random) -> dict[str, Any]:
    def one() -> dict[str, Any]:
        kind = pick(rng, ["eq", "abs_eq", "sq_eq", "gt", "ge", "lt", "eq"])
        c = rng.randint(1, 4) ** 2 if kind == "sq_eq" else rng.randint(1, 6)
        return {"kind": kind, "c": c}

    return {"cond": one(), "target": one()}


# --- counting -------------------------------------------------------------------------------------------------------------------------

def _menu(rng: random.Random) -> dict[str, Any]:
    return {"style": "menu", "groups": [{"label": "主菜", "count": rng.randint(2, 6)}, {"label": "湯", "count": rng.randint(2, 5)}, {"label": "飲料", "count": rng.randint(2, 4)}]}


def _staff(rng: random.Random) -> dict[str, Any]:
    return {"style": "staff", "groups": [{"label": "內科醫師", "count": rng.randint(4, 12)}, {"label": "外科醫師", "count": rng.randint(3, 10)}]}


def _grades(rng: random.Random) -> dict[str, Any]:
    return {"grades": [rng.randint(2, 8), rng.randint(2, 8), rng.randint(2, 8)]}


_RICH = [120, 180, 240, 252, 300, 360, 420, 450, 480, 504, 540, 600, 630, 720, 756, 840, 900, 1008]


def _divisors(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, _RICH)
    m = pick(rng, [d for d in range(4, n) if n % d == 0 and d <= 60])
    return {"n": n, "multiple_of": m, "exclude_multiple_of": None}


def _divisors_exclude(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, _RICH)
    m = pick(rng, [d for d in range(2, 25) if n % d == 0])
    k = pick(rng, [p for p in (2, 3, 5, 7) if n % p == 0 and m % p != 0])
    return {"n": n, "multiple_of": m, "exclude_multiple_of": k}


def _pairing(rng: random.Random) -> dict[str, Any]:
    t1, t2 = rng.randint(4, 8), rng.randint(3, 6)
    return {"head": {"total": t1, "vet": rng.randint(1, t1 - 1)}, "tail": {"total": t2, "vet": rng.randint(1, t2 - 1)}}


def _ordered(rng: random.Random) -> dict[str, Any]:
    return {"others": rng.randint(3, 8), "special": rng.randint(2, 6), "picks": pick(rng, [2, 2, 3])}


def _two_union_none(rng: random.Random) -> dict[str, Any]:
    ab = rng.randint(4, 16)
    a, b = ab + rng.randint(2, 25), ab + rng.randint(1, 18)
    return {"kind": "union_and_none", "U": a + b - ab + rng.randint(1, 8), "A": a, "B": b, "AB": ab}


def _two_union(rng: random.Random) -> dict[str, Any]:
    ab = rng.randint(5, 18)
    a, b = ab + rng.randint(2, 12), ab + rng.randint(4, 18)
    return {"kind": "union", "U": a + b - ab + rng.randint(1, 8), "A": a, "B": b, "AB": ab}


def _two_missing(rng: random.Random) -> dict[str, Any]:
    ab = rng.randint(2, 8)
    a, b = ab + rng.randint(2, 12), ab + rng.randint(2, 12)
    return {"kind": "missing_set", "union": a + b - ab, "A": a, "AB": ab}


def _two_range(rng: random.Random) -> dict[str, Any]:
    u = rng.randint(30, 70)
    return {"kind": "intersection_range", "U": u, "A": rng.randint(u // 2 + 3, u - 2), "B": rng.randint(u // 2 + 1, u - 4)}


def _regions(rng: random.Random) -> dict[str, int]:
    r = {k: rng.randint(0, 9) for k in ("abc", "ab", "bc", "ca", "a", "b", "c")}
    r["abc"] = rng.randint(1, 6)
    return r


def _three(kind: str):
    def sampler(rng: random.Random) -> dict[str, Any]:
        r = _regions(rng)
        out = {"kind": kind, "A": r["a"] + r["ab"] + r["ca"] + r["abc"], "B": r["b"] + r["ab"] + r["bc"] + r["abc"], "C": r["c"] + r["bc"] + r["ca"] + r["abc"],
               "AB": r["ab"] + r["abc"], "BC": r["bc"] + r["abc"], "CA": r["ca"] + r["abc"], "ABC": r["abc"]}
        if kind == "union_and_none":
            out["U"] = sum(r.values()) + rng.randint(1, 12)
        return out
    return sampler


_DIVISOR_SETS = [[2, 3, 5], [2, 3, 7], [3, 5, 7], [2, 5, 7], [2, 3, 4], [3, 4, 5], [2, 7, 11]]


def _multiples(rng: random.Random) -> dict[str, Any]:
    return {"limit": pick(rng, [100, 120, 150, 180, 200, 240, 300, 360, 400, 500]), "divisors": pick(rng, _DIVISOR_SETS)}


def _coins(rng: random.Random) -> dict[str, Any]:
    c1, c2 = pick(rng, [(10, 50), (5, 10), (5, 50), (1, 5), (10, 50)])
    step = c2 // c1  # the larger coin is a whole number of the smaller ones
    return {"coins": [c1, c2], "total": c1 * rng.randint(2 * step, 6 * step)}


def _dice(rng: random.Random) -> dict[str, Any]:
    return {"modulus": rng.randint(3, 11)}


def _race(rng: random.Random) -> dict[str, Any]:
    return {"wins_needed": pick(rng, [2, 3]), "winner": pick(rng, ["甲", "乙"]), "sport": pick(rng, ["桌球", "羽球", "網球"])}


def _path(rng: random.Random) -> dict[str, Any]:
    start, end = rng.sample("ABCD", 2)
    return {"vertices": list("ABCD"), "edges": [list(e) for e in ("AB", "AD", "BC", "BD", "CD")], "start": start, "end": end}


def _toss(rng: random.Random) -> dict[str, Any]:
    run = pick(rng, [2, 2, 3])
    return {"max_tosses": rng.randint(max(run, 3), 7 if run == 2 else 6), "run": run}


_L_CELLS = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [0, 1]]
_TILE_ASKS = [{"kind": "total"}] + [{"kind": "exactly", "k": k} for k in range(1, 4)] + [{"kind": "at_least", "k": k} for k in range(1, 3)]


def _tiling(rng: random.Random) -> dict[str, Any]:
    return {"cells": _L_CELLS, "ask": dict(pick(rng, _TILE_ASKS))}


def _claim_pairs(rng: random.Random) -> dict[str, Any]:
    s, n = rng.randint(2, 4), rng.randint(2, 5)
    relation = pick(rng, ["same_region", "same_region", "different_regions"])
    actual = math.comb(s, 2) + math.comb(n, 2) if relation == "same_region" else s * n
    wrong = {s * n, math.comb(s + n, 2), math.comb(s, 2) * math.comb(n, 2), s + n, math.comb(s, 2) + math.comb(n, 2) + 1} - {actual}
    claimed = actual if rng.random() < 0.5 else pick(rng, sorted(w for w in wrong if w >= 1))
    return {"south": s, "north": n, "claimed": claimed, "relation": relation}


# component id -> (skill key, operation, source-faithful stated data, sampler)
COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Any]] = {
    12744: ("logic", "interval_set_operations", _g(A={"lo": 1, "hi": 3}, B={"lo": 2, "hi": 4}, items=["intersection", "union", "a_minus_b", "a_complement"]), _intervals),
    12745: ("logic", "proposition_truth", _g(atoms=[{"kind": "fact", "id": "rect_square"}, {"kind": "fact", "id": "eq_tri_isos"}, {"kind": "compare", "a": 3, "op": ">", "b": 5}],
                                          options=[["atom", 0], ["atom", 1], ["and", 0, 1], ["or", 1, 2], ["or", 0, 2]], mode="select_true"), _select_true),
    12747: ("logic", "condition_relation", _g(cond={"kind": "abs_eq", "c": 3}, target={"kind": "eq", "c": 3}), _condition),
    12748: ("logic", "finite_set_operations", _g(universe=[1, 2, 3, 4, 5], A=[1, 2, 3], B=[2, 3, 4], items=["intersection", "union", "a_minus_b", "a_complement"]), _universe_sets),
    12763: ("logic", "proposition_truth", _g(atoms=[{"kind": "compare", "a": 5, "op": ">", "b": 8}, {"kind": "compare", "a": 5, "op": "<", "b": 7}], options=[["or", 0, 1]], mode="truth"), _compound_truth),
    12764: ("logic", "implication_truth", _g(claim="ab0_and"), _claim),
    12766: ("logic", "finite_set_operations", _g(A=[1, 2, 4, 5], B=[1, 3, 6], items=["intersection", "union", "a_minus_b", "b_minus_a"]), _plain_sets),
    12767: ("logic", "equation_root_sets", _g(A={"kind": "square", "rhs": 1}, B={"kind": "quad", "b": -2, "c": -3}, items=["intersection", "union"]), _equation_sets),
    12749: ("counting", "race_outcomes", _g(wins_needed=2, winner="甲", sport="桌球"), _race),
    12750: ("counting", "choice_product", _g(style="menu", groups=[{"label": "主菜", "count": 4}, {"label": "湯", "count": 3}, {"label": "飲料", "count": 2}]), _menu),
    12751: ("counting", "divisor_counting", _g(n=360, multiple_of=18, exclude_multiple_of=None), _divisors),
    12752: ("counting", "at_least_one_pairing", _g(head={"total": 6, "vet": 4}, tail={"total": 4, "vet": 3}), _pairing),
    12753: ("counting", "two_set_counting", _g(kind="union_and_none", U=40, A=35, B=15, AB=12), _two_union_none),
    12754: ("counting", "three_set_counting", _g(kind="union_and_none", U=40, A=15, B=19, C=20, AB=10, BC=12, CA=8, ABC=3), _three("union_and_none")),
    12755: ("counting", "coin_payment", _g(coins=[10, 50], total=160), _coins),
    12756: ("counting", "graph_paths", _g(vertices=list("ABCD"), edges=[list(e) for e in ("AB", "AD", "BC", "BD", "CD")], start="A", end="C"), _path),
    12757: ("counting", "dice_sum_multiples", _g(modulus=5), _dice),
    12758: ("counting", "choice_product", _g(style="staff", groups=[{"label": "內科醫師", "count": 8}, {"label": "外科醫師", "count": 6}]), _staff),
    12759: ("counting", "divisor_counting", _g(n=240, multiple_of=4, exclude_multiple_of=5), _divisors_exclude),
    12760: ("counting", "ordered_at_least_one", _g(others=5, special=4, picks=2), _ordered),
    12761: ("counting", "two_set_counting", _g(kind="missing_set", union=20, A=12, AB=5), _two_missing),
    12762: ("counting", "multiples_counting", _g(limit=300, divisors=[2, 3, 5]), _multiples),
    12765: ("counting", "region_pairs_claim", _g(south=2, north=3, claimed=4, relation="same_region"), _claim_pairs),
    12768: ("counting", "coin_toss_sequences", _g(max_tosses=4, run=2), _toss),
    12769: ("counting", "grade_selection", _g(grades=[3, 4, 6]), _grades),
    12770: ("counting", "two_set_counting", _g(kind="union", U=40, A=20, B=30, AB=15), _two_union),
    12771: ("counting", "three_set_counting", _g(kind="union", A=20, B=10, C=5, AB=6, BC=3, CA=3, ABC=1), _three("union")),
    12772: ("counting", "two_set_counting", _g(kind="intersection_range", U=40, A=30, B=25), _two_range),
    12773: ("counting", "tiling_count", _g(cells=_L_CELLS, ask={"kind": "total"}), _tiling),
}
