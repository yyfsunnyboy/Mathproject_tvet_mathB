"""Per-component *inputs* for 普高數學2 Unit 5 組合 — skills ``gh_Combination`` and ``gh_BinomialTheorem`` (textbook ids 12812-12848).

Each entry gives the source-faithful stated data (variant 0) and a sampler for further variants of the same shape.  Samplers only choose the
numbers a stem prints; the domain computes every answer and refuses degenerate inputs, which the sandbox then skips.  Nothing here is an answer.
"""

from __future__ import annotations

import math
import random
from typing import Any

SKILLS = {"combination": "gh_Combination", "binomial": "gh_BinomialTheorem"}

# rows without a dynamic Generator: the textbook question is kept as is (configs/fixed_textbook_practice.json, merged only at the authorized release)
FIXED_ROWS: dict[int, str] = {
    12834: ("進階題12（半圓直徑上 4 點、半圓周上 6 點）：圖形本身決定共線關係（直徑上的點共線、圓周上的點任三點不共線），改數字必須重畫圖形；"
            "以教材原題保留（FIXED_GRADED，含教師核可的教材裁切圖），答案 40 條直線、116 個三角形已逐組枚舉驗證，已於 Stage 1 綁定正式題 12834"),
    12838: ("例題9 證明 C(n,0)+C(n,1)+…+C(n,n)=2^n：證明題沒有可自動判定的單一答案，比照 Unit 2 的證明題以 ungraded 自評保留"
            "（題目、手寫區與逐步參考證明，不產生對錯、連續答對、精熟度或錯題紀錄）"),
    12845: ("隨堂練習10 證明 C(n,0)−C(n,1)+C(n,2)−…+(−1)^n C(n,n)=0：證明題沒有可自動判定的單一答案，比照 Unit 2 的證明題以 ungraded 自評保留"
            "（題目、手寫區與逐步參考證明，不產生對錯、連續答對、精熟度或錯題紀錄）"),
}

OP = {name: name for name in (
    "combination_evaluate", "select_with_members", "mixed_group_ordered", "group_partition", "combination_identity_select", "combination_claim",
    "pair_count", "sequential_selection", "gender_committee", "paired_group_assignment", "surjective_distribution", "parity_sum_selection",
    "multiset_select_arrange", "binomial_expansion", "radical_binomial_power", "general_term_coefficient", "at_least_k_selection",
    "binomial_sum_bound", "coefficient_solve_parameter")}
SKILL_OPERATIONS = {
    "combination": ["combination_evaluate", "select_with_members", "mixed_group_ordered", "group_partition", "combination_identity_select",
                    "combination_claim", "pair_count", "sequential_selection", "gender_committee", "paired_group_assignment",
                    "surjective_distribution", "parity_sum_selection", "multiset_select_arrange"],
    "binomial": ["binomial_expansion", "radical_binomial_power", "general_term_coefficient", "at_least_k_selection", "binomial_sum_bound",
                 "coefficient_solve_parameter", "combination_claim"],
}


def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def _g(**kw: Any) -> dict[str, Any]:
    return kw


# --- combinations --------------------------------------------------------------------------------------------------------------------------

def _evaluate_symmetry(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(6, 15)
    k = rng.randint(2, min(4, n // 2))
    return {"items": [{"kind": "comb", "n": n, "k": k}, {"kind": "comb", "n": n, "k": n - k}, {"kind": "comb", "n": n, "k": pick(rng, [n, 0])}]}


def _evaluate_practice(rng: random.Random) -> dict[str, Any]:
    n1, n2, n3 = rng.randint(7, 15), rng.randint(5, 10), rng.randint(8, 15)
    return {"items": [{"kind": "comb", "n": n1, "k": rng.randint(3, 5)}, {"kind": "comb", "n": n2, "k": rng.randint(2, 4)},
                      {"kind": "perm_over_comb", "n": n3, "k": rng.randint(3, 6)}]}


def _members_handball(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(8, 14)
    return {"style": "handball", "n": n, "k": rng.randint(4, n - 2), "asks": ["total", pick(rng, ["exactly_one", "exactly_one", "at_least_one", "neither"])]}


def _members_basketball(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(6, 12)
    return {"style": "basketball", "n": n, "k": rng.randint(3, n - 2), "asks": ["total", pick(rng, ["both", "both", "neither"])]}


def _debate(rng: random.Random) -> dict[str, Any]:
    return {"style": "debate", "groups": [rng.randint(2, 6), rng.randint(2, 5)], "pick": 3, "require": [0, 1]}


def _ranking(rng: random.Random) -> dict[str, Any]:
    return {"style": "ranking", "groups": [rng.randint(1, 4), rng.randint(1, 5), rng.randint(2, 5)], "pick": 3, "require": [0, 1]}


def _rooms(rng: random.Random) -> dict[str, Any]:
    k = pick(rng, [2, 2, 3])
    sizes = [rng.randint(1, 5) for _ in range(k)]
    if not 4 <= sum(sizes) <= 9:
        raise ValueError("size")
    return {"style": "rooms", "n": sum(sizes), "asks": [{"sizes": sizes, "labeled": True}]}


def _classes(rng: random.Random) -> dict[str, Any]:
    k = rng.randint(2, 4)
    sizes = [rng.randint(1, 4)] * k if rng.random() < 0.6 else [rng.randint(1, 4) for _ in range(k)]
    if not 4 <= sum(sizes) <= 9:
        raise ValueError("size")
    return {"style": "classes", "n": sum(sizes), "asks": [{"sizes": sizes, "labeled": True}]}


def _two_equal_parts(rng: random.Random, n: int) -> list[int]:
    """Three groups, exactly two of the same size (e.g. 4,1,1 or 3,3,2)."""
    options = [sorted([a, b, b], reverse=True) for b in range(1, n) for a in range(1, n) if a != b and a + 2 * b == n]
    if not options:
        raise ValueError("no_pattern")
    return pick(rng, options)


def _books(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [6, 6, 8, 9])
    g = pick(rng, [d for d in (2, 3, 4) if n % d == 0])
    return {"style": "books", "n": n, "asks": [{"sizes": [n // g] * g, "labeled": True}, {"sizes": [n // g] * g, "labeled": False},
                                               {"sizes": _two_equal_parts(rng, n), "labeled": False}]}


def _students(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [6, 8, 8, 9, 10])
    g = pick(rng, [d for d in (2, 3) if n % d == 0])
    return {"style": "students", "n": n, "asks": [{"sizes": [n // g] * g, "labeled": False}, {"sizes": _two_equal_parts(rng, n), "labeled": False}]}


def _identities(rng: random.Random) -> dict[str, Any]:
    def maybe(right: list[int], wrong: list[list[int]]) -> list[int]:
        return pick(rng, wrong) if rng.random() < 0.35 else right

    n1 = rng.randint(20, 99)
    a1 = rng.randint(n1 // 2 + 1, n1 - 2)
    n2 = rng.randint(20, 99)
    a2 = rng.randint(n2 // 3, n2 // 2)
    n3 = rng.randint(20, 99)
    a3 = rng.randint(n3 // 3, n3 // 2)
    n4, a4 = rng.randint(10, 99), rng.randint(1, 4)
    n5, a5 = rng.randint(5, 20), rng.randint(3, 6)
    return {"statements": [
        {"form": "symmetry", "n": n1, "a": a1, "rhs": maybe([n1, n1 - a1], [[n1, n1 - a1 + 1], [n1, n1 - a1 - 1]])},
        {"form": "pascal", "n": n2, "a": a2, "rhs": maybe(pick(rng, [[n2 + 1, a2], [n2 + 1, n2 + 1 - a2]]), [[n2 + 1, a2 - 1], [n2, a2]])},
        {"form": "pascal_diff", "n": n3, "a": a3, "rhs": maybe([n3, a3 - 1], [[n3, a3], [n3 + 1, a3 - 1]])},
        {"form": "pascal_chain", "n": n4, "a": a4, "rhs": maybe([n4 + 2, a4 + 2], [[n4 + 1, a4 + 2], [n4 + 2, a4 + 1]])},
        {"form": "hockey_stick", "n": n5, "a": a5, "rhs": maybe([n5 + a5 + 1, a5], [[n5 + a5, a5], [n5 + a5 + 1, a5 + 1]])},
    ]}


def _claim_choose(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(4, 12)
    k = rng.randint(2, n - 2)
    form, cn, ck = pick(rng, [("comb", n, k), ("comb", n, k), ("perm", n, k), ("comb", n, k + 1)])
    return {"setting": {"kind": "choose", "n": n, "k": k}, "claim": {"form": form, "n": cn, "k": ck}}


def _claim_times_factorial(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(6, 12)
    k = rng.randint(2, n - 2)
    m = pick(rng, [k, k, n - k, k + 1])
    return {"setting": {"kind": "comb_times_factorial", "n": n, "k": k, "m": m}}


def _claim_equal(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(20, 120)
    a = rng.randint(3, n // 2 - 1)
    return {"setting": {"kind": "comb_equal", "n": n, "a": a, "b": pick(rng, [n - a, n - a, n - a + 1, n - a - 1, a + 1])}}


def _claim_binomial(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(5, 15)
    a = rng.randint(1, n - 1)
    c = pick(rng, [n - a, n - a, n - a + 1, n - a - 1])
    return {"setting": {"kind": "binomial_coefficients", "n": n, "a": a, "c": c}}


def _faces(rng: random.Random) -> dict[str, Any]:
    return {"style": "faces", "mode": "count", "n": rng.randint(20, 99)}


def _round_robin(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(5, 30)
    return {"style": "round_robin", "mode": "solve_n", "total": math.comb(n, 2)}


def _chores(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(5, 9)
    tasks = pick(rng, [2, 2, 3])
    ks = [rng.randint(1, 4) for _ in range(tasks)]
    if sum(ks) > n:
        raise ValueError("size")
    return {"n": n, "ks": ks}


def _committee(rng: random.Random) -> dict[str, Any]:
    b, g = rng.randint(4, 8), rng.randint(3, 7)
    p = rng.randint(3, 5)
    i = rng.randint(1, p - 1)
    if i > b or p - i > g:
        raise ValueError("size")
    return {"boys": b, "girls": g, "pick": p, "asks": [{"kind": "exact", "boys": i}, {"kind": "at_least_one_girl"}, {"kind": "both"}]}


def _teachers(rng: random.Random) -> dict[str, Any]:
    t = rng.randint(2, 4)
    return {"teachers": t, "students": t * rng.randint(1, 4)}


def _villages(rng: random.Random) -> dict[str, Any]:
    m = rng.randint(2, 5)
    return {"people": m + pick(rng, [1, 1, 2, 3]), "places": m}


def _parity(rng: random.Random) -> dict[str, Any]:
    top = rng.randint(6, 12)
    return {"top": top, "pick": rng.randint(2, 5), "parity": pick(rng, ["even", "even", "odd"])}


_WORDS = ["snoopy", "coffee", "google", "pepper", "letter", "banana", "cookie", "puppy", "apple", "hello", "teeth", "kitten", "bottle", "yellow"]


def _letters(rng: random.Random) -> dict[str, Any]:
    word = pick(rng, _WORDS)
    return {"word": word, "pick": rng.randint(2, min(4, len(word) - 1))}


# --- binomial theorem ------------------------------------------------------------------------------------------------------------------------

_VAR_PAIRS = [["x", "y"], ["x", "y"], ["a", "b"], ["p", "q"]]


def _plain_binomial(rng: random.Random) -> dict[str, Any]:
    return {"a": 1, "b": pick(rng, [1, 1, -1]), "n": rng.randint(3, 6), "vars": pick(rng, _VAR_PAIRS)}


def _scaled_binomial(rng: random.Random) -> dict[str, Any]:
    a, b = pick(rng, [1, 2, 3]), pick(rng, [-3, -2, -1, 1, 2, 3])
    if abs(a) == abs(b) == 1:
        raise ValueError("plain")
    return {"a": a, "b": b, "n": rng.randint(3, 5), "vars": pick(rng, _VAR_PAIRS)}


def _radical(rng: random.Random) -> dict[str, Any]:
    c = pick(rng, [-2, -1, -1, 1, 2])
    return {"radicand": pick(rng, [2, 2, 3, 5]), "constant": c, "n": rng.randint(3, 6), "order": pick(rng, ["root_first", "root_first", "constant_first"])}


def _coefficient(rng: random.Random) -> dict[str, Any]:
    p1, p2 = pick(rng, [1, 2, 3]), pick(rng, [-1, -1, -2])
    n = rng.randint(4, 8)
    r = rng.randint(1, n - 1)
    target = p1 * (n - r) + p2 * r
    if target <= 0:
        raise ValueError("ask_positive_power")
    return {"c1": 1, "p1": p1, "c2": pick(rng, [-3, -2, -1, 1, 2, 3]), "p2": p2, "n": n, "target": target}


def _constant_term(rng: random.Random) -> dict[str, Any]:
    p1, q = pick(rng, [1, 1, 2, 3]), pick(rng, [1, 2, 2])
    n = rng.randint(3, 9)
    if (p1 * n) % (p1 + q):
        raise ValueError("no_constant_term")
    return {"c1": 1, "p1": p1, "c2": pick(rng, [-3, -2, -1, 1, 2, 3]), "p2": -q, "n": n, "target": 0}


def _half(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(4, 14)
    return {"n": n, "k": n // 2 + 1}


def _at_least_small(rng: random.Random) -> dict[str, Any]:
    return {"n": rng.randint(5, 14), "k": pick(rng, [2, 2, 3])}


def _bound(rng: random.Random) -> dict[str, Any]:
    n, s = rng.randint(5, 14), pick(rng, [1, 1, 0])
    prev, value, nxt = 2 ** (n - 1) - s, 2 ** n - s, 2 ** (n + 1) - s
    unit = 10 if n < 10 else 100
    low = rng.randint(prev, value - 1) // unit * unit
    high = -(-rng.randint(value + 1, nxt) // unit) * unit
    if not (prev <= low < value < high <= nxt):
        raise ValueError("bounds")
    return {"low": low, "high": high, "start": s}


def _parameter(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(3, 7)
    m = rng.randint(2, min(3, n))
    a = pick(rng, [-3, -2, -1, 1, 2, 3])
    return {"n": n, "m": m, "value": math.comb(n, m) + a * math.comb(n, m - 1)}


_SOURCE_IDENTITIES = [
    {"form": "symmetry", "n": 37, "a": 30, "rhs": [37, 7]},
    {"form": "pascal", "n": 99, "a": 50, "rhs": [100, 49]},
    {"form": "pascal_diff", "n": 49, "a": 25, "rhs": [49, 24]},
    {"form": "pascal_chain", "n": 99, "a": 2, "rhs": [101, 4]},
    {"form": "hockey_stick", "n": 10, "a": 5, "rhs": [16, 5]},
]

# component id -> (skill key, operation, source-faithful stated data, sampler)
COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Any]] = {
    12812: ("combination", "combination_evaluate", _g(items=[{"kind": "comb", "n": 10, "k": 2}, {"kind": "comb", "n": 10, "k": 8}, {"kind": "comb", "n": 10, "k": 10}]), _evaluate_symmetry),
    12813: ("combination", "select_with_members", _g(style="handball", n=10, k=7, asks=["total", "exactly_one"]), _members_handball),
    12814: ("combination", "mixed_group_ordered", _g(style="debate", groups=[3, 2], pick=3, require=[0, 1]), _debate),
    12815: ("combination", "group_partition", _g(style="rooms", n=6, asks=[{"sizes": [4, 2], "labeled": True}]), _rooms),
    12816: ("combination", "group_partition", _g(style="books", n=6, asks=[{"sizes": [2, 2, 2], "labeled": True}, {"sizes": [2, 2, 2], "labeled": False},
                                                                        {"sizes": [4, 1, 1], "labeled": False}]), _books),
    12817: ("combination", "combination_evaluate", _g(items=[{"kind": "comb", "n": 10, "k": 4}, {"kind": "comb", "n": 7, "k": 3}, {"kind": "perm_over_comb", "n": 12, "k": 5}]), _evaluate_practice),
    12818: ("combination", "select_with_members", _g(style="basketball", n=7, k=5, asks=["total", "both"]), _members_basketball),
    12819: ("combination", "mixed_group_ordered", _g(style="ranking", groups=[2, 3, 4], pick=3, require=[0, 1]), _ranking),
    12820: ("combination", "group_partition", _g(style="classes", n=6, asks=[{"sizes": [2, 2, 2], "labeled": True}]), _classes),
    12821: ("combination", "group_partition", _g(style="students", n=8, asks=[{"sizes": [4, 4], "labeled": False}, {"sizes": [3, 3, 2], "labeled": False}]), _students),
    12822: ("combination", "combination_identity_select", _g(statements=_SOURCE_IDENTITIES), _identities),
    12823: ("combination", "combination_claim", _g(setting={"kind": "choose", "n": 5, "k": 3}, claim={"form": "comb", "n": 5, "k": 3}), _claim_choose),
    12824: ("combination", "combination_claim", _g(setting={"kind": "comb_times_factorial", "n": 10, "k": 6, "m": 4}), _claim_times_factorial),
    12825: ("combination", "combination_claim", _g(setting={"kind": "comb_equal", "n": 100, "a": 20, "b": 80}), _claim_equal),
    12826: ("combination", "pair_count", _g(style="faces", mode="count", n=60), _faces),
    12827: ("combination", "sequential_selection", _g(n=7, ks=[3, 2]), _chores),
    12828: ("combination", "gender_committee", _g(boys=7, girls=5, pick=4, asks=[{"kind": "exact", "boys": 2}, {"kind": "at_least_one_girl"}, {"kind": "both"}]), _committee),
    12829: ("combination", "paired_group_assignment", _g(teachers=2, students=4), _teachers),
    12830: ("combination", "surjective_distribution", _g(people=4, places=3), _villages),
    12831: ("combination", "pair_count", _g(style="round_robin", mode="solve_n", total=66), _round_robin),
    12832: ("combination", "parity_sum_selection", _g(top=9, pick=4, parity="even"), _parity),
    12833: ("combination", "multiset_select_arrange", _g(word="snoopy", pick=3), _letters),
    12835: ("binomial", "binomial_expansion", _g(a=1, b=1, n=5, vars=["x", "y"]), _plain_binomial),
    12836: ("binomial", "binomial_expansion", _g(a=2, b=-1, n=4, vars=["x", "y"]), _scaled_binomial),
    12837: ("binomial", "general_term_coefficient", _g(c1=1, p1=2, c2=2, p2=-1, n=6, target=3), _coefficient),
    12839: ("binomial", "at_least_k_selection", _g(n=11, k=6), _half),
    12840: ("binomial", "combination_claim", _g(setting={"kind": "binomial_coefficients", "n": 10, "a": 6, "c": 4}), _claim_binomial),
    12841: ("binomial", "binomial_sum_bound", _g(low=1000, high=1200, start=1), _bound),
    12842: ("binomial", "binomial_expansion", _g(a=1, b=1, n=4, vars=["x", "y"]), _plain_binomial),
    12843: ("binomial", "radical_binomial_power", _g(radicand=2, constant=-1, n=5, order="root_first"), _radical),
    12844: ("binomial", "general_term_coefficient", _g(c1=1, p1=1, c2=-2, p2=-2, n=6, target=0), _constant_term),
    12846: ("binomial", "at_least_k_selection", _g(n=11, k=2), _at_least_small),
    12847: ("binomial", "general_term_coefficient", _g(c1=1, p1=3, c2=1, p2=-1, n=7, target=5), _coefficient),
    12848: ("binomial", "coefficient_solve_parameter", _g(n=5, m=2, value=5), _parameter),
}
