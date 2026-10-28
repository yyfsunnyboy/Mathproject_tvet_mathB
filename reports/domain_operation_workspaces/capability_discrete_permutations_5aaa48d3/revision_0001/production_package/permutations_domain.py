"""Exact domain operations for general-high Mathematics 2, Unit 4 排列 (linear permutations, arrangements of identical objects, repeated permutations).

Domain key ``discrete.permutations``.  Components pass the *stated data of the problem*; every answer is derived here with exact integer
arithmetic (factorials, falling factorials, multinomials, inclusion-exclusion).  Each operation owns a validator that re-derives the answer
a different way and never calls the construction a second time: enumeration of the labelled objects (``itertools.permutations`` /
``product``), enumeration of colour / L-R patterns, depth-first listing of every lattice path, a memoised shooting-order recursion, or a
sequential-binomial rebuild.  Numbers cross the JSON boundary as ints.
"""

from __future__ import annotations

import itertools
import math
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from typing import Any, Callable

DOMAIN_KEY = "discrete.permutations"
_BRUTE = 200_000  # largest enumeration a validator runs


def _require(givens: dict[str, Any], *keys: str) -> None:
    missing = [k for k in keys if k not in givens]
    if missing:
        raise ValueError(f"givens_required:{','.join(missing)}")


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


def _int_list(values: Any, name: str, min_len: int, max_len: int, low: int, high: int, distinct: bool = False) -> list[int]:
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"not_a_list:{name}")
    out = [_int(v, name, low, high) for v in values]
    if not (min_len <= len(out) <= max_len) or (distinct and len(set(out)) != len(out)):
        raise ValueError(f"bad_list:{name}")
    return out


def _multinomial(counts: list[int]) -> int:
    out = math.factorial(sum(counts))
    for c in counts:
        out //= math.factorial(c)
    return out


def _sequential_binomials(counts: list[int]) -> int:
    """Choose the positions of each kind in turn (a different route to the multinomial)."""
    left, out = sum(counts), 1
    for c in counts:
        out *= math.comb(left, c)
        left -= c
    return out


def _falling(n: int, k: int) -> int:
    return math.prod(range(n - k + 1, n + 1))


def _multiset_patterns(counts: list[int]):
    """Every distinct word with ``counts[i]`` copies of letter ``i`` (no duplicates are generated)."""
    left = list(counts)
    word: list[int] = []

    def rec():
        if not any(left):
            yield tuple(word)
            return
        for i, c in enumerate(left):
            if c:
                left[i] -= 1
                word.append(i)
                yield from rec()
                word.pop()
                left[i] += 1

    yield from rec()


def _positive(count: int) -> int:
    if count <= 0:
        raise ValueError("empty_result")
    return count


# --- 1. choose k of n and line them up (n = k is the full arrangement n!) ----------------------------------------------------------------

def selected_arrangement(n: int, k: int, **_: Any) -> dict[str, Any]:
    n_ = _int(n, "n", 2, 10)
    k_ = _int(k, "k", 1, n_)
    return {"n": n_, "k": k_, "count": math.perm(n_, k_)}


def _check_selected_arrangement(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n, k = int(givens["n"]), int(givens["k"])
    brute = sum(1 for _ in itertools.permutations(range(n), k)) if math.perm(n, k) <= _BRUTE else _falling(n, k)
    return brute == answer["count"] and (answer["n"], answer["k"]) == (n, k)


# --- 2. numbers written with distinct digits ------------------------------------------------------------------------------------------------

DIGIT_ASKS = ("total", "multiple_of_5", "not_multiple_of_5", "even", "odd")
_LAST_OK: dict[str, Callable[[int], bool]] = {
    "multiple_of_5": lambda d: d % 5 == 0, "not_multiple_of_5": lambda d: d % 5 != 0, "even": lambda d: d % 2 == 0, "odd": lambda d: d % 2 == 1,
}


def distinct_digit_numbers(digits: list[int], length: int, asks: list[str], **_: Any) -> dict[str, Any]:
    ds = _int_list(digits, "digits", 3, 8, 0, 9, distinct=True)
    m = len(ds)
    size = _int(length, "length", 2, min(m, 5))
    if not isinstance(asks, (list, tuple)) or not 1 <= len(asks) <= 3 or len(set(asks)) != len(asks) or any(a not in DIGIT_ASKS for a in asks):
        raise ValueError("bad_asks")
    nonzero = [d for d in ds if d != 0]
    items = []
    for ask in asks:
        if ask == "total":
            count = len(nonzero) * math.perm(m - 1, size - 1)
        else:
            count = sum(len([x for x in nonzero if x != d]) * math.perm(m - 2, size - 2) for d in ds if _LAST_OK[ask](d))
        items.append({"ask": ask, "count": _positive(count)})
    return {"digits": ds, "length": size, "items": items, "leading_zero_excluded": 0 in ds}


def _check_distinct_digit_numbers(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    ds, size = [int(d) for d in givens["digits"]], int(givens["length"])
    numbers = [p for p in itertools.permutations(ds, size) if p[0] != 0]
    for item in answer["items"]:
        ask = item["ask"]
        want = len(numbers) if ask == "total" else sum(1 for p in numbers if _LAST_OK[ask](p[-1]))
        if want != item["count"]:
            return False
    return [it["ask"] for it in answer["items"]] == list(givens["asks"])


# --- 3. two kinds in a row: one kind together / apart --------------------------------------------------------------------------------------

def adjacent_separated(men: int, women: int, **_: Any) -> dict[str, Any]:
    m, w = _int(men, "men", 2, 8), _int(women, "women", 2, 5)
    if w > m + 1 or m + w > 10:
        raise ValueError("women_cannot_be_separated_or_too_large")
    return {"men": m, "women": w, "adjacent": math.factorial(m + 1) * math.factorial(w), "separated": math.factorial(m) * math.perm(m + 1, w)}


def _check_adjacent_separated(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    m, w = int(givens["men"]), int(givens["women"])
    together = apart = 0
    for spots in itertools.combinations(range(m + w), w):  # the seats the women take
        if spots[-1] - spots[0] == w - 1:
            together += 1
        if all(b - a >= 2 for a, b in zip(spots, spots[1:])):
            apart += 1
    scale = math.factorial(m) * math.factorial(w)
    return together * scale == answer["adjacent"] and apart * scale == answer["separated"]


# --- 4. a few people may not take certain places ------------------------------------------------------------------------------------------------

def restricted_assignment(n: int, k: int, forbidden: list[list[int]], **_: Any) -> dict[str, Any]:
    n_ = _int(n, "n", 2, 9)
    k_ = _int(k, "k", 2, n_)
    if not isinstance(forbidden, (list, tuple)) or not 1 <= len(forbidden) <= 2:
        raise ValueError("one_or_two_forbidden_pairs")
    pairs = [(_int(p, "person", 0, n_ - 1), _int(q, "position", 0, k_ - 1)) for p, q in forbidden]
    if len({p for p, _q in pairs}) != len(pairs) or len({q for _p, q in pairs}) != len(pairs):
        raise ValueError("pairs_must_use_different_people_and_places")
    total = math.perm(n_, k_)
    if total > _BRUTE:
        raise ValueError("too_large")
    each = [math.perm(n_ - 1, k_ - 1) for _ in pairs]
    both = math.perm(n_ - 2, k_ - 2) if len(pairs) == 2 else None
    return {"n": n_, "k": k_, "total": total, "each": each, "both": both, "count": total - sum(each) + (both or 0)}


def _check_restricted_assignment(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n, k = int(givens["n"]), int(givens["k"])
    pairs = [(int(p), int(q)) for p, q in givens["forbidden"]]
    good = sum(1 for seats in itertools.permutations(range(n), k) if all(seats[q] != p for p, q in pairs))
    return good == answer["count"]


# --- 5. two groups in a row: each together / alternating -------------------------------------------------------------------------------------

def two_group_line(a: int, b: int, **_: Any) -> dict[str, Any]:
    a_, b_ = _int(a, "a", 2, 7), _int(b, "b", 2, 7)
    if abs(a_ - b_) > 1 or a_ + b_ > 12:
        raise ValueError("cannot_alternate")
    return {"a": a_, "b": b_, "contiguous": 2 * math.factorial(a_) * math.factorial(b_),
            "alternating": (2 if a_ == b_ else 1) * math.factorial(a_) * math.factorial(b_)}


def _check_two_group_line(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    a, b = int(givens["a"]), int(givens["b"])
    together = alternate = 0
    for spots in itertools.combinations(range(a + b), a):  # seats of group A
        mark = [i in spots for i in range(a + b)]
        runs = 1 + sum(1 for x, y in zip(mark, mark[1:]) if x != y)
        together += runs == 2
        alternate += runs == a + b
    scale = math.factorial(a) * math.factorial(b)
    return together * scale == answer["contiguous"] and alternate * scale == answer["alternating"]


# --- 6. a counting claim to mark true or false ---------------------------------------------------------------------------------------------------

CLAIM_SETTINGS = ("arrangement", "selection", "identical", "repeated")
CLAIM_FORMS = ("number", "perm", "power", "factorial", "multinomial")


def _actual(setting: dict[str, Any]) -> int:
    kind = setting.get("kind")
    if kind == "arrangement":
        return math.factorial(_int(setting["n"], "n", 2, 8))
    if kind == "selection":
        n = _int(setting["n"], "n", 2, 10)
        return math.perm(n, _int(setting["k"], "k", 1, n))
    if kind == "identical":
        counts = _int_list(setting["counts"], "counts", 2, 4, 1, 8)
        if sum(counts) > 8:
            raise ValueError("too_large")
        return _multinomial(counts)
    if kind == "repeated":
        return _int(setting["boxes"], "boxes", 2, 6) ** _int(setting["items"], "items", 2, 8)
    raise ValueError(f"unsupported_setting:{kind}")


def _claimed(claim: dict[str, Any]) -> int:
    form = claim.get("form")
    if form == "number":
        return _int(claim["value"], "value", 1)
    if form == "perm":
        n = _int(claim["n"], "n", 1, 12)
        return math.perm(n, _int(claim["k"], "k", 0, n))
    if form == "power":
        return _int(claim["base"], "base", 1, 12) ** _int(claim["exp"], "exp", 0, 10)
    if form == "factorial":
        return math.factorial(_int(claim["n"], "n", 0, 10))
    if form == "multinomial":
        return _multinomial(_int_list(claim["counts"], "counts", 2, 5, 1, 10))
    raise ValueError(f"unsupported_claim_form:{form}")


def counting_claim(setting: dict[str, Any], claim: dict[str, Any], **_: Any) -> dict[str, Any]:
    actual, claimed = _actual(setting), _claimed(claim)
    return {"actual": actual, "claimed": claimed, "truth": actual == claimed}


def _brute_actual(setting: dict[str, Any]) -> int:
    kind = setting["kind"]
    if kind == "arrangement":
        return sum(1 for _ in itertools.permutations(range(int(setting["n"]))))
    if kind == "selection":
        return sum(1 for _ in itertools.permutations(range(int(setting["n"])), int(setting["k"])))
    if kind == "identical":
        letters = [i for i, c in enumerate(setting["counts"]) for _ in range(int(c))]
        return len(set(itertools.permutations(letters)))
    return sum(1 for _ in itertools.product(range(int(setting["boxes"])), repeat=int(setting["items"])))


def _rebuilt_claim(claim: dict[str, Any]) -> int:
    form = claim["form"]
    if form == "number":
        return int(claim["value"])
    if form == "perm":
        return _falling(int(claim["n"]), int(claim["k"]))
    if form == "power":
        out = 1
        for _ in range(int(claim["exp"])):
            out *= int(claim["base"])
        return out
    if form == "factorial":
        return _falling(int(claim["n"]), int(claim["n"]))
    return _sequential_binomials([int(c) for c in claim["counts"]])


def _check_counting_claim(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    setting = givens["setting"]
    size = {"arrangement": lambda s: math.factorial(int(s["n"])), "selection": lambda s: math.perm(int(s["n"]), int(s["k"])),
            "identical": lambda s: _multinomial([int(c) for c in s["counts"]]), "repeated": lambda s: int(s["boxes"]) ** int(s["items"])}[setting["kind"]](setting)
    if size > _BRUTE:
        raise ValueError("too_large")
    actual, claimed = _brute_actual(setting), _rebuilt_claim(givens["claim"])
    return actual == answer["actual"] and claimed == answer["claimed"] and (actual == claimed) == answer["truth"]


# --- 7. both ends reserved for a special group ------------------------------------------------------------------------------------------------

def ends_from_group(special: int, others: int, **_: Any) -> dict[str, Any]:
    s, t = _int(special, "special", 2, 6), _int(others, "others", 1, 6)
    if s + t > 8:
        raise ValueError("too_large")
    return {"special": s, "others": t, "ends": math.perm(s, 2), "middle": math.factorial(s + t - 2), "count": math.perm(s, 2) * math.factorial(s + t - 2)}


def _check_ends_from_group(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    s, t = int(givens["special"]), int(givens["others"])
    good = sum(1 for p in itertools.permutations(range(s + t)) if p[0] < s and p[-1] < s)
    return good == answer["count"]


# --- 8. both ends reserved for a group and a block kept together -------------------------------------------------------------------------------

def ends_and_block(end_group: int, singles: int, block: int, **_: Any) -> dict[str, Any]:
    a, s, b = _int(end_group, "end_group", 2, 4), _int(singles, "singles", 0, 4), _int(block, "block", 2, 4)
    if a + s + b > 8:
        raise ValueError("too_large")
    units = (a - 2) + s + 1
    return {"end_group": a, "singles": s, "block": b, "ends": math.perm(a, 2), "units": units,
            "count": math.perm(a, 2) * math.factorial(units) * math.factorial(b)}


def _check_ends_and_block(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    a, s, b = int(givens["end_group"]), int(givens["singles"]), int(givens["block"])
    total, block = a + s + b, set(range(a + s, a + s + b))
    good = 0
    for p in itertools.permutations(range(total)):
        if p[0] < a and p[-1] < a:
            places = [i for i, v in enumerate(p) if v in block]
            good += places[-1] - places[0] == b - 1
    return good == answer["count"]


# --- 9. new items inserted without disturbing the order of the old ones --------------------------------------------------------------------------

def fixed_order_insertion(base: int, added: int, **_: Any) -> dict[str, Any]:
    old, new = _int(base, "base", 2, 7), _int(added, "added", 1, 4)
    if old + new > 8:
        raise ValueError("too_large")
    return {"base": old, "added": new, "count": math.factorial(old + new) // math.factorial(old)}


def _check_fixed_order_insertion(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    old, new = int(givens["base"]), int(givens["added"])
    good = sum(1 for p in itertools.permutations(range(old + new)) if [v for v in p if v < old] == list(range(old)))
    return good == answer["count"]


# --- 10. position of one letter relative to two others ---------------------------------------------------------------------------------------------

ORDER_MODES = ("same_side", "between")


def relative_order_three(n: int, pair: list[int], ref: int, mode: str, **_: Any) -> dict[str, Any]:
    n_ = _int(n, "n", 4, 8)
    two = _int_list(pair, "pair", 2, 2, 0, n_ - 1, distinct=True)
    r = _int(ref, "ref", 0, n_ - 1)
    if r in two or mode not in ORDER_MODES:
        raise ValueError("bad_letters_or_mode")
    count = math.factorial(n_) * 2 // 3 if mode == "same_side" else math.factorial(n_) // 3
    return {"n": n_, "pair": two, "ref": r, "mode": mode, "count": count}


def _check_relative_order_three(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n, (a, b), c, mode = int(givens["n"]), [int(x) for x in givens["pair"]], int(givens["ref"]), givens["mode"]
    good = 0
    for p in itertools.permutations(range(n)):
        pa, pb, pc = p.index(a), p.index(b), p.index(c)
        good += ((pa < pc) == (pb < pc)) if mode == "same_side" else (min(pa, pb) < pc < max(pa, pb))
    return good == answer["count"]


# --- 11. arrangements of identical objects (the multinomial) -----------------------------------------------------------------------------------

def identical_arrangement(counts: list[int], **_: Any) -> dict[str, Any]:
    cs = _int_list(counts, "counts", 2, 4, 1, 8)
    if sum(cs) > 10:
        raise ValueError("too_large")
    return {"counts": cs, "total": sum(cs), "count": _multinomial(cs)}


def _check_identical_arrangement(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    cs = [int(c) for c in givens["counts"]]
    if sum(cs) <= 8:
        letters = [i for i, c in enumerate(cs) for _ in range(c)]
        return len(set(itertools.permutations(letters))) == answer["count"]
    return _sequential_binomials(cs) == answer["count"]


# --- 12. shortest lattice paths with checkpoints --------------------------------------------------------------------------------------------------

GRID_ASKS = ("any", "via_C", "via_C_or_D", "avoid_both")


def _lattice(p: tuple[int, int], q: tuple[int, int]) -> int:
    dx, dy = q[0] - p[0], q[1] - p[1]
    return math.comb(dx + dy, dx) if dx >= 0 and dy >= 0 else 0


def grid_paths(width: int, height: int, points: dict[str, list[int]], asks: list[str], **_: Any) -> dict[str, Any]:
    w, h = _int(width, "width", 2, 8), _int(height, "height", 2, 5)
    c = tuple(_int(v, "C", 0, w if i == 0 else h) for i, v in enumerate(points["C"]))
    d = tuple(_int(v, "D", 0, w if i == 0 else h) for i, v in enumerate(points["D"]))
    start, end = (0, 0), (w, h)
    if len(c) != 2 or len(d) != 2 or c == d or {c, d} & {start, end}:
        raise ValueError("bad_points")
    if not isinstance(asks, (list, tuple)) or not asks or len(set(asks)) != len(asks) or any(a not in GRID_ASKS for a in asks):
        raise ValueError("bad_asks")
    total = _lattice(start, end)
    via_c, via_d = _lattice(start, c) * _lattice(c, end), _lattice(start, d) * _lattice(d, end)
    both = _lattice(start, c) * _lattice(c, d) * _lattice(d, end) + _lattice(start, d) * _lattice(d, c) * _lattice(c, end)
    union = via_c + via_d - both
    table = {"any": total, "via_C": via_c, "via_C_or_D": union, "avoid_both": total - union}
    return {"width": w, "height": h, "total": total, "via_C": via_c, "via_D": via_d, "via_both": both, "union": union, "avoid": total - union,
            "items": [{"ask": a, "count": _positive(table[a])} for a in asks]}


def _check_grid_paths(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    w, h = int(givens["width"]), int(givens["height"])
    c, d = tuple(int(v) for v in givens["points"]["C"]), tuple(int(v) for v in givens["points"]["D"])
    paths: list[list[tuple[int, int]]] = []

    def walk(x: int, y: int, trail: list[tuple[int, int]]) -> None:
        trail = trail + [(x, y)]
        if (x, y) == (w, h):
            paths.append(trail)
            return
        if x < w:
            walk(x + 1, y, trail)
        if y < h:
            walk(x, y + 1, trail)

    walk(0, 0, [])
    table = {"any": len(paths), "via_C": sum(1 for p in paths if c in p), "via_C_or_D": sum(1 for p in paths if c in p or d in p),
             "avoid_both": sum(1 for p in paths if c not in p and d not in p)}
    return all(table[it["ask"]] == it["count"] for it in answer["items"]) and [it["ask"] for it in answer["items"]] == list(givens["asks"])


# --- 13. numbers written with repeated digits ---------------------------------------------------------------------------------------------------------

MULTISET_ASKS = ("number", "even", "odd")


def _arrangements(counter: Counter) -> int:
    return _multinomial([c for c in counter.values() if c > 0])


def _without(counter: Counter, digit: int) -> Counter:
    out = Counter(counter)
    out[digit] -= 1
    if out[digit] == 0:
        del out[digit]
    return out


def _nonleading_zero(counter: Counter) -> int:
    """Arrangements of the digits of ``counter`` whose first digit is not 0."""
    total = _arrangements(counter)
    return total - (_arrangements(_without(counter, 0)) if counter.get(0) else 0)


def multiset_digit_numbers(digits: list[int], ask: str, **_: Any) -> dict[str, Any]:
    ds = _int_list(digits, "digits", 4, 8, 0, 9)
    if ask not in MULTISET_ASKS or len(set(ds)) < 2:
        raise ValueError("bad_ask_or_digits")
    counter = Counter(ds)
    if ask == "number":
        count = _nonleading_zero(counter)
    else:
        wanted = (lambda d: d % 2 == 0) if ask == "even" else (lambda d: d % 2 == 1)
        count = sum(_nonleading_zero(_without(counter, d)) for d in counter if wanted(d))
    return {"digits": sorted(ds), "ask": ask, "all_arrangements": _arrangements(counter), "count": _positive(count)}


def _check_multiset_digit_numbers(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    ds, ask = [int(d) for d in givens["digits"]], givens["ask"]
    numbers = {p for p in itertools.permutations(ds) if p[0] != 0}
    want = len(numbers) if ask == "number" else sum(1 for p in numbers if p[-1] % 2 == (0 if ask == "even" else 1))
    return want == answer["count"]


# --- 14. distinct objects of several colours ---------------------------------------------------------------------------------------------------------

COLOR_ASKS = ("each_color_together", "last_color_apart")


def colored_distinct_items(counts: list[int], asks: list[str], **_: Any) -> dict[str, Any]:
    cs = _int_list(counts, "counts", 3, 3, 1, 6)
    total = sum(cs)
    if total > 10 or not isinstance(asks, (list, tuple)) or not asks or len(set(asks)) != len(asks) or any(a not in COLOR_ASKS for a in asks):
        raise ValueError("bad_counts_or_asks")
    rest = total - cs[-1]
    if cs[-1] > rest + 1:
        raise ValueError("last_color_cannot_be_apart")
    table = {"each_color_together": math.factorial(len(cs)) * math.prod(math.factorial(c) for c in cs),
             "last_color_apart": math.factorial(rest) * math.perm(rest + 1, cs[-1])}
    return {"counts": cs, "total": total, "rest": rest, "items": [{"ask": a, "count": _positive(table[a])} for a in asks]}


def _check_colored_distinct_items(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    cs = [int(c) for c in givens["counts"]]
    scale = math.prod(math.factorial(c) for c in cs)  # the objects of one colour are distinct: every colour pattern carries c! orders per colour
    last = len(cs) - 1
    together = apart = 0
    for word in _multiset_patterns(cs):
        runs = 1 + sum(1 for x, y in zip(word, word[1:]) if x != y)
        together += runs == len(cs)
        apart += not any(x == y == last for x, y in zip(word, word[1:]))
    table = {"each_color_together": together * scale, "last_color_apart": apart * scale}
    return all(table[it["ask"]] == it["count"] for it in answer["items"]) and [it["ask"] for it in answer["items"]] == list(givens["asks"])


# --- 15. shooting order of hanging columns -----------------------------------------------------------------------------------------------------------------

def column_shooting_order(counts: list[int], **_: Any) -> dict[str, Any]:
    cs = _int_list(counts, "counts", 2, 3, 1, 5)
    if sum(cs) > 12:
        raise ValueError("too_large")
    return {"counts": cs, "total": sum(cs), "count": _multinomial(cs)}


def _check_column_shooting_order(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    @lru_cache(maxsize=None)
    def orders(state: tuple[int, ...]) -> int:
        if not any(state):
            return 1
        return sum(orders(state[:i] + (state[i] - 1,) + state[i + 1:]) for i in range(len(state)) if state[i] > 0)  # the lowest balloon of a column goes first

    return orders(tuple(int(c) for c in givens["counts"])) == answer["count"]


# --- 16. jumps on the number line ---------------------------------------------------------------------------------------------------------------------------------

def line_walk(steps: int, target: int, **_: Any) -> dict[str, Any]:
    s = _int(steps, "steps", 3, 12)
    t = _int(target, "target", -s, s)
    if (s + t) % 2 or t == 0 or abs(t) > s - 2:
        raise ValueError("target_not_reachable_or_trivial")
    right = (s + t) // 2
    return {"steps": s, "target": t, "right": right, "left": s - right, "count": math.comb(s, right)}


def _check_line_walk(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    s, t = int(givens["steps"]), int(givens["target"])
    return sum(1 for jumps in itertools.product((-1, 1), repeat=s) if sum(jumps) == t) == answer["count"]


# --- 17. distinct objects dealt into boxes (repeated permutations) -----------------------------------------------------------------------------------

BOX_KINDS = ("any", "onto", "first_at_least", "first_exactly", "all_different", "each_at_most")


def _at_most_each(items: int, boxes: int, cap: int) -> int:
    """Items! times the coefficient of x^items in (sum_{j<=cap} x^j / j!)^boxes."""
    base = [Fraction(1, math.factorial(j)) for j in range(cap + 1)]
    poly = [Fraction(1)]
    for _ in range(boxes):
        nxt = [Fraction(0)] * (len(poly) + cap)
        for i, a in enumerate(poly):
            for j, b in enumerate(base):
                nxt[i + j] += a * b
        poly = nxt
    value = poly[items] * math.factorial(items) if items < len(poly) else Fraction(0)
    if value.denominator != 1:
        raise ValueError("not_integral")
    return int(value)


def _box_count(boxes: int, ask: dict[str, Any]) -> int:
    kind, n = ask["kind"], _int(ask["items"], "items", 2, 8)
    if boxes**n > 300_000:
        raise ValueError("too_large")
    if kind == "any":
        return boxes**n
    if kind == "onto":
        if n < boxes:
            raise ValueError("too_few_items")
        return sum((-1) ** j * math.comb(boxes, j) * (boxes - j) ** n for j in range(boxes + 1))
    if kind in ("first_at_least", "first_exactly"):
        k = _int(ask["k"], "k", 1, n)
        exact = math.comb(n, k) * (boxes - 1) ** (n - k)
        return exact if kind == "first_exactly" else boxes**n - sum(math.comb(n, i) * (boxes - 1) ** (n - i) for i in range(k))
    if kind == "all_different":
        if n > boxes:
            raise ValueError("too_many_items")
        return math.perm(boxes, n)
    if kind == "each_at_most":
        cap = _int(ask["cap"], "cap", 1, n)
        return _at_most_each(n, boxes, cap)
    raise ValueError(f"unsupported_kind:{kind}")


def distribute_distinct(boxes: int, asks: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    b = _int(boxes, "boxes", 2, 8)
    if not isinstance(asks, (list, tuple)) or not 1 <= len(asks) <= 3 or any(not isinstance(a, dict) or a.get("kind") not in BOX_KINDS for a in asks):
        raise ValueError("bad_asks")
    items = []
    for ask in asks:
        count = _positive(_box_count(b, ask))
        items.append({**{k: v for k, v in ask.items() if k in ("kind", "items", "k", "cap")}, "count": count, "all": b ** int(ask["items"])})
    return {"boxes": b, "items": items}


def _check_distribute_distinct(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    b = int(givens["boxes"])
    tests: dict[str, Callable[[tuple[int, ...], dict[str, Any]], bool]] = {
        "any": lambda t, a: True,
        "onto": lambda t, a: len(set(t)) == b,
        "first_at_least": lambda t, a: t.count(0) >= int(a["k"]),
        "first_exactly": lambda t, a: t.count(0) == int(a["k"]),
        "all_different": lambda t, a: len(set(t)) == len(t),
        "each_at_most": lambda t, a: max(Counter(t).values()) <= int(a["cap"]),
    }
    if len(givens["asks"]) != len(answer["items"]):
        return False
    for ask, item in zip(givens["asks"], answer["items"]):
        n = int(ask["items"])
        if b**n > 300_000 or ask["kind"] != item["kind"]:
            return False
        if sum(1 for t in itertools.product(range(b), repeat=n) if tests[ask["kind"]](t, ask)) != item["count"]:
            return False
    return True


# --- registry / entrypoint --------------------------------------------------------------------------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "selected_arrangement": (selected_arrangement, _check_selected_arrangement, ("n", "k")),
    "distinct_digit_numbers": (distinct_digit_numbers, _check_distinct_digit_numbers, ("digits", "length", "asks")),
    "adjacent_separated": (adjacent_separated, _check_adjacent_separated, ("men", "women")),
    "restricted_assignment": (restricted_assignment, _check_restricted_assignment, ("n", "k", "forbidden")),
    "two_group_line": (two_group_line, _check_two_group_line, ("a", "b")),
    "counting_claim": (counting_claim, _check_counting_claim, ("setting", "claim")),
    "ends_from_group": (ends_from_group, _check_ends_from_group, ("special", "others")),
    "ends_and_block": (ends_and_block, _check_ends_and_block, ("end_group", "singles", "block")),
    "fixed_order_insertion": (fixed_order_insertion, _check_fixed_order_insertion, ("base", "added")),
    "relative_order_three": (relative_order_three, _check_relative_order_three, ("n", "pair", "ref", "mode")),
    "identical_arrangement": (identical_arrangement, _check_identical_arrangement, ("counts",)),
    "grid_paths": (grid_paths, _check_grid_paths, ("width", "height", "points", "asks")),
    "multiset_digit_numbers": (multiset_digit_numbers, _check_multiset_digit_numbers, ("digits", "ask")),
    "colored_distinct_items": (colored_distinct_items, _check_colored_distinct_items, ("counts", "asks")),
    "column_shooting_order": (column_shooting_order, _check_column_shooting_order, ("counts",)),
    "line_walk": (line_walk, _check_line_walk, ("steps", "target")),
    "distribute_distinct": (distribute_distinct, _check_distribute_distinct, ("boxes", "asks")),
}
OPERATIONS = tuple(_OPERATIONS)


def build_permutations_matrix(
    *, domain_operation: str | None = None, seed: int | None = None, constraints: dict[str, Any] | None = None, **_: Any
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_permutations_operation:{operation}")
    solve, _check, required = _OPERATIONS[operation]
    givens = {k: v for k, v in (constraints or {}).items() if k not in ("skill_id",)}
    _require(givens, *required)
    answer = solve(**givens)
    return {
        "domain": DOMAIN_KEY,
        "domain_operation": operation,
        "givens": givens,
        "answer": answer,
        "validation_facts": {"domain_operation": operation, "seed": 0 if seed is None else int(seed)},
    }


def _make_validator(operation: str) -> Callable[[Any], bool]:
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
