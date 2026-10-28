"""Per-component *inputs* for 普高數學2 Unit 4 排列 — skills ``gh_LinearPermutation``, ``gh_PermutationWithIdenticalItems`` and
``gh_RepeatedPermutation`` (textbook ids 12774-12811).

Each entry gives the source-faithful stated data (variant 0) and a sampler for further variants of the same shape.  Samplers only choose the
numbers a stem prints; the domain computes every answer and refuses degenerate inputs, which the sandbox then skips.  Nothing here is an answer.
"""

from __future__ import annotations

import math
import random
from typing import Any

from agent_domains_candidate.permutations.permutations_domain import _claimed

SKILLS = {"linear": "gh_LinearPermutation", "identical": "gh_PermutationWithIdenticalItems", "repeated": "gh_RepeatedPermutation"}

# rows without a dynamic Generator: the textbook question is kept as is (FIXED_GRADED, trusted figure-derived answer)
FIXED_ROWS: dict[int, str] = {
    12801: ("下圖為一街道圖，從 A 取捷徑走到 B：街道圖是不規則的方格（有些街道線不存在），圖形本身就是題目，無法改數字而不重畫；"
            "以教材原題保留（FIXED_GRADED），答案由圖檔像素讀出的街道圖獨立推導並經動態規劃與逐路徑枚舉交叉驗證"),
}

OP = {name: name for name in (
    "selected_arrangement", "distinct_digit_numbers", "adjacent_separated", "restricted_assignment", "two_group_line", "counting_claim",
    "ends_from_group", "ends_and_block", "fixed_order_insertion", "relative_order_three", "identical_arrangement", "grid_paths",
    "multiset_digit_numbers", "colored_distinct_items", "column_shooting_order", "line_walk", "distribute_distinct")}
SKILL_OPERATIONS = {
    "linear": ["selected_arrangement", "distinct_digit_numbers", "adjacent_separated", "restricted_assignment", "two_group_line", "counting_claim",
               "ends_from_group", "ends_and_block", "fixed_order_insertion", "relative_order_three"],
    "identical": ["identical_arrangement", "grid_paths", "multiset_digit_numbers", "counting_claim", "colored_distinct_items", "column_shooting_order", "line_walk"],
    "repeated": ["distribute_distinct", "counting_claim", "identical_arrangement"],
}


def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def _g(**kw: Any) -> dict[str, Any]:
    return kw


# --- linear permutations -----------------------------------------------------------------------------------------------------------------------

def _lottery(style: str):
    def sampler(rng: random.Random) -> dict[str, Any]:
        n = rng.randint(3, 10)
        return {"style": style, "n": n, "k": n}
    return sampler


def _partial(style: str, low: int, high: int):
    def sampler(rng: random.Random) -> dict[str, Any]:
        n = rng.randint(low, high)
        return {"style": style, "n": n, "k": rng.randint(2, min(5, n - 1))}
    return sampler


_WORDS = {2: ["AI", "TV", "PC", "DJ"], 3: ["IMO", "SUN", "CAT", "DNA", "USB"], 4: ["MATH", "CODE", "STAR", "WIFI"]}


def _colors(rng: random.Random) -> dict[str, Any]:
    k = pick(rng, [2, 3, 3, 4, 4])
    return {"style": "colors", "word": pick(rng, _WORDS[k]), "n": rng.randint(k + 1, 8), "k": k}


def _digits_pick(rng: random.Random) -> dict[str, Any]:
    m = rng.randint(4, 7)
    digits = sorted([0] + rng.sample(range(1, 10), m - 1))
    return {"style": "pick", "digits": digits, "length": rng.randint(2, min(4, m)), "asks": ["total"]}


def _digits_compose(rng: random.Random) -> dict[str, Any]:
    m = rng.randint(5, 7)
    digits = sorted([0, 5] + rng.sample([1, 2, 3, 4, 6, 7, 8, 9], m - 2))
    return {"style": "compose", "digits": digits, "length": rng.choice([3, 4]), "asks": ["total", "not_multiple_of_5"]}


def _adjacent(rng: random.Random) -> dict[str, Any]:
    return {"men": rng.randint(3, 6), "women": rng.randint(2, 4)}


def _universities(rng: random.Random) -> dict[str, Any]:
    k = rng.choice([3, 4])
    p, q = rng.sample(range(k), 2)
    return {"style": "universities", "n": rng.randint(k + 1, 9), "k": k, "forbidden": [[0, p], [1, q]], "names": ["甲", "乙"]}


def _relay(rng: random.Random) -> dict[str, Any]:
    return {"style": "relay", "n": rng.randint(5, 8), "k": rng.choice([3, 4]), "forbidden": [[rng.randint(0, 3), 0]], "names": []}


_ROLES = [("爸爸", "么兒"), ("媽媽", "么兒"), ("爸爸", "姐姐"), ("媽媽", "大哥")]


def _family(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(4, 7)
    first, second = pick(rng, [(0, n - 1), (n - 1, 0)])
    return {"style": "family", "n": n, "k": n, "forbidden": [[0, first], [1, second]], "names": list(pick(rng, _ROLES))}


def _projects(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(4, 7)
    p, q = rng.sample(range(n), 2)
    return {"style": "projects", "n": n, "k": n, "forbidden": [[0, p], [1, q]], "names": ["甲", "乙"]}


def _two_groups(rng: random.Random) -> dict[str, Any]:
    if rng.random() < 0.25:
        a = pick(rng, [4, 5])
        return {"style": "baseball", "a": a, "b": 9 - a}
    a = rng.randint(3, 6)
    return {"style": "club", "a": a, "b": a + pick(rng, [-1, 0, 1])}


_CHARS = ["讀", "書", "好", "學", "習", "樂", "數", "理"]


def _claim_arrangement(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(3, 5)
    actual = math.factorial(n)
    wrong = sorted(w for w in {n * n, n * (n - 1), n**n, 2 * n, actual + n, actual * 2} - {actual} if w >= 1)
    value = actual if rng.random() < 0.5 else pick(rng, wrong)
    return {"setting": {"kind": "arrangement", "n": n, "chars": rng.sample(_CHARS, n)}, "claim": {"form": "number", "value": value}}


def _claim_selection(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(4, 8)
    k = rng.randint(2, min(4, n - 1))
    actual = math.perm(n, k)
    options = [{"form": "perm", "n": n, "k": k}, {"form": "perm", "n": n, "k": k - 1}, {"form": "perm", "n": n, "k": k + 1},
               {"form": "perm", "n": n - 1, "k": k}, {"form": "power", "base": n, "exp": k}, {"form": "factorial", "n": n}]
    wrong = [o for o in options[1:] if _claimed(o) != actual]
    claim = options[0] if rng.random() < 0.5 else pick(rng, wrong)
    return {"setting": {"kind": "selection", "n": n, "k": k}, "claim": claim}


_LETTERS = "ABCDEHKLMNPRSTW"


def _round_robin(letters: list[str], counts: list[int]) -> str:
    left, word = list(counts), ""
    while any(left):
        for i, letter in enumerate(letters):
            if left[i]:
                word += letter
                left[i] -= 1
    return word


def _claim_identical(rng: random.Random) -> dict[str, Any]:
    m = rng.choice([2, 3])
    counts = [rng.randint(1, 4) for _ in range(m)]
    total = sum(counts)
    if not 4 <= total <= 8:
        raise ValueError("size")
    actual = math.factorial(total) // math.prod(math.factorial(c) for c in counts)
    parts = rng.randint(2, 4)
    other = [1] * parts
    for _ in range(total - parts):
        other[rng.randrange(parts)] += 1
    wrong = [{"form": "factorial", "n": total}]
    if sorted(other) != sorted(counts):
        wrong.append({"form": "multinomial", "counts": other})
    wrong = [w for w in wrong if _claimed(w) != actual]
    claim = {"form": "multinomial", "counts": counts} if rng.random() < 0.5 or not wrong else pick(rng, wrong)
    return {"setting": {"kind": "identical", "counts": counts, "word": _round_robin(rng.sample(list(_LETTERS), m), counts)}, "claim": claim}


def _claim_repeated(rng: random.Random) -> dict[str, Any]:
    boxes, items = rng.randint(2, 4), rng.randint(3, 6)
    if boxes == items:
        raise ValueError("same")
    actual = boxes**items
    options = [{"form": "power", "base": boxes, "exp": items}, {"form": "power", "base": items, "exp": boxes}, {"form": "power", "base": boxes, "exp": items - 1},
               {"form": "power", "base": boxes, "exp": items + 1}, {"form": "power", "base": items, "exp": items}]
    wrong = [o for o in options[1:] if _claimed(o) != actual]
    claim = options[0] if rng.random() < 0.5 else pick(rng, wrong)
    return {"setting": {"kind": "repeated", "boxes": boxes, "items": items}, "claim": claim}


def _ends(rng: random.Random) -> dict[str, Any]:
    return {"special": rng.randint(2, 4), "others": rng.randint(2, 5)}


def _ends_block(rng: random.Random) -> dict[str, Any]:
    return {"end_group": rng.randint(2, 3), "singles": rng.randint(1, 3), "block": rng.randint(2, 3)}


def _insertion(rng: random.Random) -> dict[str, Any]:
    return {"base": rng.randint(3, 6), "added": rng.randint(1, 3)}


def _order_three(rng: random.Random) -> dict[str, Any]:
    n = rng.randint(5, 8)
    a, b, c = rng.sample(range(n), 3)
    return {"n": n, "pair": sorted([a, b]), "ref": c, "mode": pick(rng, ["same_side", "same_side", "between"])}


# --- identical objects -----------------------------------------------------------------------------------------------------------------------------

_DUTY_NAMES = [["甲", "乙"], ["丙", "丁"], ["戊", "己"]]
_ANIMALS = [["無尾熊", "貓熊"], ["獅子", "老虎"], ["企鵝", "海豹"], ["長頸鹿", "斑馬"]]


def _duty(rng: random.Random) -> dict[str, Any]:
    return {"style": "duty", "counts": [rng.randint(2, 6), rng.randint(2, 5)], "names": pick(rng, _DUTY_NAMES)}


def _train(rng: random.Random) -> dict[str, Any]:
    return {"style": "train", "counts": [rng.randint(2, 5), rng.randint(2, 5)], "animals": pick(rng, _ANIMALS)}


def _volunteers(rng: random.Random) -> dict[str, Any]:
    counts = [rng.randint(1, 4) for _ in range(3)]
    if sum(counts) > 9:
        raise ValueError("too_long")
    return {"style": "volunteers", "counts": counts}


def _grid(own_figure: str):
    def sampler(rng: random.Random) -> dict[str, Any]:
        w, h = rng.randint(4, 8), rng.randint(2, 4)
        c = [rng.randint(1, w - 1), rng.randint(1, h - 1)]
        d = [rng.randint(1, w - 1), rng.randint(1, h - 1)]
        if c == d:
            raise ValueError("same_point")
        for fig in ("example7", "practice7"):  # a variant must never equal a textbook figure's structure
            from agent_domains_candidate.permutations.permutations_adapter import FIGURE_GRIDS

            f = FIGURE_GRIDS[fig]
            if (w, h, tuple(c), tuple(d)) == (f["width"], f["height"], f["C"], f["D"]):
                raise ValueError("equals_a_figure")
        return {"width": w, "height": h, "points": {"C": c, "D": d}, "asks": ["any", "via_C", "via_C_or_D", "avoid_both"]}
    return sampler


def _digits_number(rng: random.Random) -> dict[str, Any]:
    others = rng.sample(range(1, 10), 2)
    counts = [rng.randint(1, 2), rng.randint(1, 3), rng.randint(1, 3)]
    if not 5 <= sum(counts) <= 7:
        raise ValueError("size")
    digits = sorted([0] * counts[0] + [others[0]] * counts[1] + [others[1]] * counts[2])
    return {"digits": digits, "ask": "number"}


def _digits_parity(rng: random.Random) -> dict[str, Any]:
    kinds = rng.sample(range(1, 10), rng.randint(2, 3))
    counts = [rng.randint(1, 3) for _ in kinds]
    if not 5 <= sum(counts) <= 8:
        raise ValueError("size")
    return {"digits": sorted(d for d, c in zip(kinds, counts) for _ in range(c)), "ask": pick(rng, ["even", "even", "odd"])}


_CAT_COLORS = ["黃", "白", "黑", "灰", "橘", "棕"]


def _cats(rng: random.Random) -> dict[str, Any]:
    counts = [rng.randint(2, 4), rng.randint(2, 4), rng.randint(2, 5)]
    return {"counts": counts, "colors": rng.sample(_CAT_COLORS, 3), "asks": ["each_color_together", "last_color_apart"]}


def _walk(rng: random.Random) -> dict[str, Any]:
    steps = rng.randint(4, 11)
    target = rng.choice([t for t in range(-(steps - 2), steps - 1) if t != 0 and (steps + t) % 2 == 0])
    return {"steps": steps, "target": target}


_BALLOON_COLORS = ["紅", "黃", "藍"]


def _balloons(rng: random.Random) -> dict[str, Any]:
    k = rng.choice([2, 3])
    counts = [rng.randint(1, 5) for _ in range(k)]
    if sum(counts) > 12 or (k == 3 and counts == [2, 3, 3]):
        raise ValueError("size_or_figure")
    return {"counts": counts, "colors": _BALLOON_COLORS[:k]}


# --- repeated permutations ------------------------------------------------------------------------------------------------------------------------

def _rabbit(rng: random.Random) -> dict[str, Any]:
    boxes = rng.randint(2, 4)
    n = rng.randint(boxes + 1, 7)
    return {"style": "rabbit", "boxes": boxes, "asks": [{"kind": "any", "items": n}, {"kind": "onto", "items": n}]}


def _books(rng: random.Random) -> dict[str, Any]:
    n, k = rng.randint(3, 6), rng.randint(1, 2)
    return {"style": "books", "boxes": rng.randint(3, 4), "asks": [{"kind": "any", "items": n}, {"kind": "first_at_least", "items": n, "k": k},
                                                                  {"kind": "first_exactly", "items": n, "k": k}]}


def _vending(rng: random.Random) -> dict[str, Any]:
    boxes = rng.randint(4, 8)
    p = rng.randint(2, min(4, boxes))
    return {"style": "vending", "boxes": boxes, "asks": [{"kind": "any", "items": p}, {"kind": "all_different", "items": p}]}


def _rooms(rng: random.Random) -> dict[str, Any]:
    boxes, cap = rng.randint(3, 4), rng.randint(2, 4)
    n1, n2 = rng.choice([cap - 1, cap]), rng.choice([cap + 1, cap + 2])
    if n1 < 2 or n2 > boxes * cap:
        raise ValueError("size")
    return {"style": "rooms", "boxes": boxes, "asks": [{"kind": "each_at_most", "items": n1, "cap": cap}, {"kind": "each_at_most", "items": n2, "cap": cap}]}


def _lunch(rng: random.Random) -> dict[str, Any]:
    boxes, n = rng.randint(3, 4), rng.randint(4, 7)
    cap = rng.randint(max(2, n - 2), n - 1)
    return {"style": "lunch", "boxes": boxes, "asks": [{"kind": "each_at_most", "items": n, "cap": cap}]}


def _digit_sets(rng: random.Random) -> dict[str, Any]:
    m = rng.randint(2, 3)
    return {"style": "digits", "digits": sorted(rng.sample(range(1, 10), m)), "boxes": m, "asks": [{"kind": "onto", "items": rng.randint(m + 1, 6)}]}


_GRID_ASKS = ["any", "via_C", "via_C_or_D", "avoid_both"]

# component id -> (skill key, operation, source-faithful stated data, sampler)
COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Any]] = {
    12774: ("linear", "selected_arrangement", _g(style="lottery_singing", n=6, k=6), _lottery("lottery_singing")),
    12775: ("linear", "selected_arrangement", _g(style="songs", n=7, k=4), _partial("songs", 4, 10)),
    12776: ("linear", "distinct_digit_numbers", _g(style="pick", digits=[0, 1, 2, 3, 4], length=3, asks=["total"]), _digits_pick),
    12777: ("linear", "adjacent_separated", _g(men=4, women=3), _adjacent),
    12778: ("linear", "restricted_assignment", _g(style="universities", n=7, k=4, forbidden=[[0, 0], [1, 3]], names=["甲", "乙"]), _universities),
    12779: ("linear", "selected_arrangement", _g(style="lottery_election", n=5, k=5), _lottery("lottery_election")),
    12780: ("linear", "selected_arrangement", _g(style="sites", n=6, k=3), _partial("sites", 4, 10)),
    12781: ("linear", "restricted_assignment", _g(style="relay", n=6, k=4, forbidden=[[0, 0]], names=[]), _relay),
    12782: ("linear", "two_group_line", _g(style="baseball", a=4, b=5), _two_groups),
    12783: ("linear", "restricted_assignment", _g(style="family", n=5, k=5, forbidden=[[0, 0], [1, 4]], names=["爸爸", "么兒"]), _family),
    12784: ("linear", "counting_claim", _g(setting={"kind": "arrangement", "n": 3, "chars": ["讀", "書", "好"]}, claim={"form": "number", "value": 6}), _claim_arrangement),
    12785: ("linear", "counting_claim", _g(setting={"kind": "selection", "n": 5, "k": 3}, claim={"form": "perm", "n": 5, "k": 3}), _claim_selection),
    12786: ("linear", "selected_arrangement", _g(style="colors", word="IMO", n=5, k=3), _colors),
    12787: ("linear", "distinct_digit_numbers", _g(style="compose", digits=[0, 1, 2, 3, 4, 5], length=3, asks=["total", "not_multiple_of_5"]), _digits_compose),
    12788: ("linear", "restricted_assignment", _g(style="projects", n=5, k=5, forbidden=[[0, 0], [1, 1]], names=["甲", "乙"]), _projects),
    12789: ("linear", "ends_from_group", _g(special=2, others=4), _ends),
    12790: ("linear", "ends_and_block", _g(end_group=2, singles=2, block=2), _ends_block),
    12791: ("linear", "fixed_order_insertion", _g(base=5, added=2), _insertion),
    12792: ("linear", "relative_order_three", _g(n=6, pair=[0, 1], ref=2, mode="same_side"), _order_three),
    12793: ("identical", "identical_arrangement", _g(style="duty", counts=[4, 3], names=["甲", "乙"]), _duty),
    12794: ("identical", "grid_paths", _g(width=7, height=3, points={"C": [2, 1], "D": [4, 2]}, asks=_GRID_ASKS, figure="example7"), _grid("example7")),
    12795: ("identical", "multiset_digit_numbers", _g(digits=[0, 0, 1, 1, 2, 2], ask="number"), _digits_number),
    12796: ("identical", "identical_arrangement", _g(style="train", counts=[3, 4], animals=["無尾熊", "貓熊"]), _train),
    12797: ("identical", "grid_paths", _g(width=6, height=4, points={"C": [3, 1], "D": [4, 2]}, asks=_GRID_ASKS, figure="practice7"), _grid("practice7")),
    12798: ("identical", "multiset_digit_numbers", _g(digits=[4, 5, 5, 5, 8, 8, 8], ask="even"), _digits_parity),
    12799: ("identical", "counting_claim", _g(setting={"kind": "identical", "counts": [3, 3], "word": "PAPAPA"}, claim={"form": "multinomial", "counts": [2, 2, 2]}), _claim_identical),
    12800: ("identical", "colored_distinct_items", _g(counts=[2, 3, 4], colors=["黃", "白", "黑"], asks=["each_color_together", "last_color_apart"]), _cats),
    12802: ("identical", "line_walk", _g(steps=6, target=4), _walk),
    12803: ("identical", "column_shooting_order", _g(counts=[2, 3, 3], colors=["紅", "黃", "藍"], figure="balloons"), _balloons),
    12804: ("repeated", "distribute_distinct", _g(style="rabbit", boxes=3, asks=[{"kind": "any", "items": 4}, {"kind": "onto", "items": 4}]), _rabbit),
    12805: ("repeated", "distribute_distinct", _g(style="books", boxes=3, asks=[{"kind": "any", "items": 4}, {"kind": "first_at_least", "items": 4, "k": 1},
                                                                          {"kind": "first_exactly", "items": 4, "k": 1}]), _books),
    12806: ("repeated", "distribute_distinct", _g(style="vending", boxes=6, asks=[{"kind": "any", "items": 3}, {"kind": "all_different", "items": 3}]), _vending),
    12807: ("repeated", "distribute_distinct", _g(style="rooms", boxes=3, asks=[{"kind": "each_at_most", "items": 4, "cap": 4}, {"kind": "each_at_most", "items": 5, "cap": 4}]), _rooms),
    12808: ("repeated", "counting_claim", _g(setting={"kind": "repeated", "boxes": 3, "items": 4}, claim={"form": "power", "base": 4, "exp": 3}), _claim_repeated),
    12809: ("repeated", "identical_arrangement", _g(style="volunteers", counts=[2, 2, 2]), _volunteers),
    12810: ("repeated", "distribute_distinct", _g(style="lunch", boxes=3, asks=[{"kind": "each_at_most", "items": 5, "cap": 4}]), _lunch),
    12811: ("repeated", "distribute_distinct", _g(style="digits", digits=[2, 3], boxes=2, asks=[{"kind": "onto", "items": 4}]), _digit_sets),
}
