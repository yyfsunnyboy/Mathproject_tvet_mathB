"""Classical probability for 普高數學2 Unit 6.

Every graded value is computed here. Enumeration and a closed form are both required, and they must agree.
Generators only supply the stated data (the givens); they never carry a textbook answer.

Outcomes are equiprobable:
- coins and birth order are ordered sequences;
- dice are numbered (a fair die that looks the same is still distinguished, as in the worked solution of 例題10);
- an unordered draw is a combination, and a draw without replacement that keeps order is a permutation;
- with replacement, each draw is independent and the sample space has size ``sides ** n``.
"""

from __future__ import annotations

import itertools
import math
from fractions import Fraction
from typing import Any, Callable

DOMAIN_KEY = "discrete.classical_probability"
MAX_SET = 36

YES_NO = ({"label": "A", "value": "是"}, {"label": "B", "value": "否"})
TRUE_FALSE = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})


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
    try:
        f = Fraction(str(v).strip())
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"not_a_fraction:{name}") from None
    return f


def _prob(f: Fraction, work: str) -> dict[str, Any]:
    if f < 0 or f > 1:
        raise ValueError("probability_out_of_range")
    return {"kind": "rational", "value": str(f), "work": work}


def _count(f: Fraction, work: str) -> dict[str, Any]:
    if f < 0 or f.denominator != 1:
        raise ValueError("not_a_count")
    return {"kind": "rational", "value": str(f), "work": work}


def _set_part(values: list[int], work: str) -> dict[str, Any]:
    vals = sorted({int(v) for v in values})
    if not vals:
        raise ValueError("empty_set")
    if len(vals) > MAX_SET:
        raise ValueError("set_too_large")
    return {"kind": "set", "values": vals, "work": work}


def _choice(yes: bool, choices, work: str) -> dict[str, Any]:
    return {"kind": "choice", "label": "A" if yes else "B", "choices": [dict(c) for c in choices], "work": work}


def _pack(parts: list[dict[str, Any]]) -> dict[str, Any]:
    if not parts:
        raise ValueError("no_parts")
    return {"parts": parts}


def _equiprobable_work(total: int, count: int, prefix: str) -> str:
    """State the sample-space size, the unreduced favorable count, then the probability."""
    if not isinstance(total, int) or not isinstance(count, int) or total < 1 or not 0 <= count <= total:
        raise ValueError("count_out_of_space")
    value = Fraction(count, total)
    reduced = str(value)
    shown = reduced if value.denominator == total else f"{count}/{total} = {reduced}"
    return f"{prefix}{total} 個，有利 {count} 個，機率 {shown}。"


def _same(fresh: dict[str, Any], answer: dict[str, Any]) -> bool:
    return fresh == answer


# --- coins --------------------------------------------------------------------------------------------------------------------------------


def _bit_list(code: int, n: int) -> list[int]:
    return [(code >> (n - 1 - i)) & 1 for i in range(n)]


def _enum_codes(n: int) -> list[int]:
    codes = []
    for bits in itertools.product((0, 1), repeat=n):
        code = 0
        for bit in bits:
            code = code * 2 + bit
        codes.append(code)
    if codes != list(range(2**n)):
        raise ValueError("coin_encoding")
    return codes


def _observable_set(n: int, observable: dict[str, Any]) -> list[int]:
    kind = str(observable.get("kind") or "")
    if kind in {"head_count", "tail_count"}:
        return list(range(n + 1))
    if kind == "toss":
        index = _int(observable.get("index"), "index", 0, n - 1)
        seen = {(_bit_list(code, n)[index]) for code in _enum_codes(n)}
        if seen != {0, 1}:
            raise ValueError("toss_space")
        return [0, 1]
    raise ValueError("bad_observable")


def _coin_answer(n: Any, observable: dict[str, Any]) -> dict[str, Any]:
    n = _int(n, "n", 2, 5)
    if not isinstance(observable, dict):
        raise ValueError("bad_observable")
    codes = _enum_codes(n)
    observed = _observable_set(n, observable)
    return _pack([
        _set_part(codes, f"依序記錄 {n} 次，樣本點對應 0 到 {2**n - 1}，共 {2**n} 個，且彼此等可能。"),
        _count(Fraction(2**n), f"樣本點個數為 2^{n} = {2**n}。"),
        _set_part(observed, "這個觀察所能出現的值組成另一個樣本空間。"),
        _count(Fraction(len(observed)), f"此樣本空間有 {len(observed)} 個樣本點。"),
    ])


def coin_outcome_space(*, n: Any, observable: dict[str, Any], **_: Any) -> dict[str, Any]:
    return _coin_answer(n, observable)


def _check_coin(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_coin_answer(givens["n"], givens["observable"]), answer)


# --- draws --------------------------------------------------------------------------------------------------------------------------------


def _digit_code(seq: tuple[int, ...]) -> int:
    code = 0
    for digit in seq:
        if not 1 <= int(digit) <= 8:
            raise ValueError("bad_digit")
        code = code * 10 + int(digit)
    return code


def _draw_codes(labels: list[int], k: int, mode: str) -> list[int]:
    n = len(labels)
    if mode == "ordered_no_replace":
        seqs = itertools.permutations(labels, k)
        formula = math.perm(n, k)
    elif mode == "ordered_replace":
        seqs = itertools.product(labels, repeat=k)
        formula = n**k
    elif mode == "unordered":
        seqs = itertools.combinations(labels, k)
        formula = math.comb(n, k)
    else:
        raise ValueError("bad_draw_mode")
    codes = sorted(_digit_code(tuple(seq)) for seq in seqs)
    if len(codes) != len(set(codes)) or len(codes) != formula:
        raise ValueError("draw_count_mismatch")
    return codes


def _draw_labels(n: int, labels: Any) -> list[int]:
    if labels is None:
        return list(range(1, n + 1))
    parsed = [_int(v, "label", 1, 8) for v in labels]
    if len(parsed) != n or len(set(parsed)) != n:
        raise ValueError("bad_labels")
    return sorted(parsed)


def _draw_answer(n: Any, asks: list[dict[str, Any]], labels: Any = None) -> dict[str, Any]:
    n = _int(n, "n", 2, 8)
    parsed = _draw_labels(n, labels)
    if not isinstance(asks, list) or not 1 <= len(asks) <= 3:
        raise ValueError("bad_asks")
    parts: list[dict[str, Any]] = []
    for ask in asks:
        mode = str(ask.get("mode") or "")
        limit = min(3, n if mode != "ordered_replace" else 3)
        k = _int(ask.get("k"), "k", 1, limit)
        if mode != "ordered_replace" and k > n:
            raise ValueError("k_exceeds_n")
        codes = _draw_codes(parsed, k, mode)
        how = {
            "ordered_no_replace": f"依序取 {k} 次、每次取出後不放回",
            "ordered_replace": f"取後放回，依序取 {k} 次",
            "unordered": f"同時取 {k} 個，不計順序",
        }[mode]
        parts.append(_set_part(codes, f"{how}的樣本點寫成十進位碼，共 {len(codes)} 個。"))
        parts.append(_count(Fraction(len(codes)), f"個數為 {len(codes)}，與樣本點集合的大小相同。"))
    return _pack(parts)


def draw_outcome_space(*, n: Any, asks: list[dict[str, Any]], labels: Any = None, **_: Any) -> dict[str, Any]:
    return _draw_answer(n, asks, labels)


def _check_draw(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_draw_answer(givens["n"], givens["asks"], givens.get("labels")), answer)


# --- coded events (coins / birth order) ---------------------------------------------------------------------------------------------------


def _holds(code: int, n: int, spec: dict[str, Any]) -> bool:
    kind = str(spec.get("kind") or "")
    bits = _bit_list(code, n)
    if kind == "space":
        return True
    if kind in {"at_least_symbol", "exactly_symbol"}:
        symbol = _int(spec.get("symbol"), "symbol", 0, 1)
        k = _int(spec.get("k"), "k", 0, n)
        count = bits.count(symbol)
        return count >= k if kind == "at_least_symbol" else count == k
    if kind == "bit_is":
        return bits[_int(spec.get("index"), "index", 0, n - 1)] == _int(spec.get("value"), "value", 0, 1)
    if kind == "and":
        return _holds(code, n, spec["left"]) and _holds(code, n, spec["right"])
    if kind == "complement":
        return not _holds(code, n, spec["event"])
    raise ValueError("bad_event")


def _mask(n: int, spec: dict[str, Any]) -> list[int]:
    return [code for code in _enum_codes(n) if _holds(code, n, spec)]


def _coded_answer(n: Any, asks: list[dict[str, Any]]) -> dict[str, Any]:
    n = _int(n, "n", 2, 5)
    if not isinstance(asks, list) or not 1 <= len(asks) <= 3:
        raise ValueError("bad_asks")
    parts = []
    for ask in asks:
        if not isinstance(ask, dict):
            raise ValueError("bad_event")
        found = _mask(n, ask)
        # the same mask built by testing the complement of the complement
        again = [code for code in range(2**n) if _holds(code, n, {"kind": "complement", "event": {"kind": "complement", "event": ask}})]
        if found != again:
            raise ValueError("event_mismatch")
        parts.append(_set_part(found, f"符合條件的樣本點有 {len(found)} 個。"))
    return _pack(parts)


def coded_event_sets(*, n: Any, asks: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    return _coded_answer(n, asks)


def _check_coded(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_coded_answer(givens["n"], givens["asks"]), answer)


# --- two-dice event sets and mutex --------------------------------------------------------------------------------------------------------


def _die_hit(a: int, b: int, spec: dict[str, Any]) -> bool:
    kind = str(spec.get("kind") or "")
    if kind == "sum_gt":
        return a + b > _int(spec.get("n"), "n", 1, 13)
    if kind == "sum_eq":
        return a + b == _int(spec.get("n"), "n", 2, 12)
    if kind == "product_eq":
        return a * b == _int(spec.get("n"), "n", 1, 36)
    if kind == "faces_equal":
        return a == b
    if kind == "first_even":
        return a % 2 == 0
    if kind == "first_odd":
        return a % 2 == 1
    if kind == "second_even":
        return b % 2 == 0
    if kind == "sum_odd":
        return (a + b) % 2 == 1
    if kind == "sum_even":
        return (a + b) % 2 == 0
    if kind == "first_gt_second":
        return a > b
    if kind == "first_lt_second":
        return a < b
    if kind == "diff_eq":
        return abs(a - b) == _int(spec.get("n"), "n", 0, 5)
    if kind == "both_gt":
        t = _int(spec.get("n"), "n", 0, 5)
        return a > t and b > t
    if kind == "exactly_one_face":
        face = _int(spec.get("face"), "face", 1, 6)
        return (a == face) + (b == face) == 1
    raise ValueError("bad_predicate")


def _die_codes(spec: dict[str, Any]) -> list[int]:
    return [10 * a + b for a in range(1, 7) for b in range(1, 7) if _die_hit(a, b, spec)]


def _dice_sets_answer(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    left, right = _die_codes(a), _die_codes(b)
    both = sorted(set(left) & set(right))
    union = sorted(set(left) | set(right))
    return _pack([
        _set_part(left, f"事件 A 有 {len(left)} 個樣本點。"),
        _set_part(right, f"事件 B 有 {len(right)} 個樣本點。"),
        _set_part(both, f"A∩B 有 {len(both)} 個樣本點。"),
        _set_part(union, f"A∪B 有 {len(union)} 個樣本點。"),
    ])


def dice_event_sets(*, a: dict[str, Any], b: dict[str, Any], **_: Any) -> dict[str, Any]:
    return _dice_sets_answer(a, b)


def _check_dice_sets(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_dice_sets_answer(givens["a"], givens["b"]), answer)


def _coin_spec_mask(n: int, spec: dict[str, Any]) -> set[int]:
    kind = str(spec.get("kind") or "")
    if kind == "exactly_heads":
        k = _int(spec.get("k"), "k", 0, n)
        found = {code for code in range(2**n) if _bit_list(code, n).count(1) == k}
        if len(found) != math.comb(n, k):
            raise ValueError("head_count_mismatch")
        return found
    if kind == "at_least_heads":
        k = _int(spec.get("k"), "k", 1, n)
        found = {code for code in range(2**n) if _bit_list(code, n).count(1) >= k}
        formula = sum(math.comb(n, j) for j in range(k, n + 1))
        if len(found) != formula:
            raise ValueError("head_count_mismatch")
        return found
    raise ValueError("bad_relation_event")


def _relation_answer(model: str, **givens: Any) -> dict[str, Any]:
    if model == "coin":
        n = _int(givens.get("n"), "n", 2, 5)
        left = _coin_spec_mask(n, givens["a"])
        right = _coin_spec_mask(n, givens["b"])
        comp = set(range(2**n)) - left
        if not comp or not left or not right:
            raise ValueError("empty_set")
        return _pack([
            _set_part(sorted(comp), f"A' 有 {len(comp)} 個樣本點。"),
            _choice(left.isdisjoint(right), YES_NO, "A 與 B 互斥表示沒有共同樣本點。"),
            _choice(left.isdisjoint(comp), YES_NO, "A 與 A' 沒有共同樣本點。"),
        ])
    if model == "dice":
        left = set(_die_codes(givens["a"]))
        right = set(_die_codes(givens["b"]))
        if not left or not right:
            raise ValueError("empty_set")
        return _pack([_choice(left.isdisjoint(right), YES_NO, "兩事件互斥表示交集是空集合。")])
    raise ValueError("bad_model")


def event_relation(*, model: str, **givens: Any) -> dict[str, Any]:
    return _relation_answer(str(model), **givens)


def _check_relation(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    data = dict(givens)
    model = data.pop("model")
    return _same(_relation_answer(model, **data), answer)


# --- dice / coin probabilities ------------------------------------------------------------------------------------------------------------


def _nonneg(total: int, slots: int) -> int:
    if total < 0 or slots <= 0:
        return 0
    return math.comb(total + slots - 1, slots - 1)


def _sum_ways(dice: int, faces: int, total: int) -> int:
    need = total - dice
    ans = 0
    for i in range(dice + 1):
        rest = need - i * faces
        if rest < 0:
            continue
        sign = 1 if i % 2 == 0 else -1
        ans += sign * math.comb(dice, i) * _nonneg(rest, dice)
    return ans


def _dice_hit_many(outcome: tuple[int, ...], ask: dict[str, Any]) -> bool:
    kind = str(ask.get("kind") or "")
    faces = max(outcome)  # only used when the ask names a face bound; the caller checks the range
    del faces
    if kind == "sum_eq":
        return sum(outcome) == _int(ask.get("n"), "n", 1, 80)
    if kind == "all_different":
        return len(set(outcome)) == len(outcome)
    if kind == "all_equal":
        return len(set(outcome)) == 1
    if kind == "exactly_two_equal":
        return len(outcome) == 3 and len(set(outcome)) == 2
    if kind == "at_least_two_equal":
        return len(set(outcome)) < len(outcome)
    if kind == "faces_equal":
        return len(outcome) == 2 and outcome[0] == outcome[1]
    if kind == "first_gt_second":
        return len(outcome) == 2 and outcome[0] > outcome[1]
    if kind == "diff_eq":
        return len(outcome) == 2 and abs(outcome[0] - outcome[1]) == _int(ask.get("n"), "n", 0, 20)
    if kind == "both_gt":
        t = _int(ask.get("n"), "n", 0, 20)
        return len(outcome) == 2 and outcome[0] > t and outcome[1] > t
    if kind == "exactly_face_count":
        face = _int(ask.get("face"), "face", 1, 20)
        count = _int(ask.get("count"), "count", 0, len(outcome))
        return outcome.count(face) == count
    if kind == "at_least_face":
        face = _int(ask.get("face"), "face", 1, 20)
        count = _int(ask.get("count"), "count", 1, len(outcome))
        return outcome.count(face) >= count
    raise ValueError("bad_dice_ask")


def _dice_closed(dice: int, faces: int, ask: dict[str, Any]) -> Fraction:
    total = faces**dice
    kind = str(ask.get("kind") or "")
    if kind == "sum_eq":
        good = _sum_ways(dice, faces, _int(ask.get("n"), "n", dice, dice * faces))
    elif kind == "all_different":
        good = math.perm(faces, dice) if dice <= faces else 0
    elif kind == "all_equal":
        good = faces
    elif kind == "exactly_two_equal":
        if dice != 3:
            raise ValueError("exactly_two_needs_three_dice")
        good = 3 * faces * (faces - 1)
    elif kind == "at_least_two_equal":
        different = math.perm(faces, dice) if dice <= faces else 0
        good = total - different
    elif kind == "faces_equal":
        if dice != 2:
            raise ValueError("faces_equal_needs_two_dice")
        good = faces
    elif kind == "first_gt_second":
        if dice != 2:
            raise ValueError("order_needs_two_dice")
        good = (total - faces) // 2
    elif kind == "diff_eq":
        if dice != 2:
            raise ValueError("diff_needs_two_dice")
        gap = _int(ask.get("n"), "n", 0, faces - 1)
        good = faces if gap == 0 else 2 * (faces - gap)
    elif kind == "both_gt":
        if dice != 2:
            raise ValueError("both_needs_two_dice")
        t = _int(ask.get("n"), "n", 0, faces - 1)
        width = faces - t
        good = width * width
    elif kind == "exactly_face_count":
        count = _int(ask.get("count"), "count", 0, dice)
        _int(ask.get("face"), "face", 1, faces)
        good = math.comb(dice, count) * (faces - 1) ** (dice - count)
    elif kind == "at_least_face":
        _int(ask.get("face"), "face", 1, faces)
        start = _int(ask.get("count"), "count", 1, dice)
        good = sum(math.comb(dice, j) * (faces - 1) ** (dice - j) for j in range(start, dice + 1))
    else:
        raise ValueError("bad_dice_ask")
    return Fraction(good, total)


def _dice_raw_count(dice: int, faces: int, ask: dict[str, Any]) -> int:
    return sum(1 for outcome in itertools.product(range(1, faces + 1), repeat=dice) if _dice_hit_many(outcome, ask))


def _dice_enum(dice: int, faces: int, ask: dict[str, Any]) -> Fraction:
    return Fraction(_dice_raw_count(dice, faces, ask), faces**dice)


def _dice_prob_answer(dice: Any, faces: Any, asks: list[dict[str, Any]]) -> dict[str, Any]:
    dice = _int(dice, "dice", 2, 3)
    faces = _int(faces, "faces", 4, 12)
    if not isinstance(asks, list) or not 1 <= len(asks) <= 2:
        raise ValueError("bad_asks")
    total = faces**dice
    parts = []
    for ask in asks:
        closed = _dice_closed(dice, faces, ask)
        favorable = _dice_raw_count(dice, faces, ask)
        if closed != Fraction(favorable, total):
            raise ValueError("dice_formula_mismatch")
        parts.append(_prob(closed, _equiprobable_work(total, favorable, "已編號、等可能的樣本點 ")))
    return _pack(parts)


def dice_count_probability(*, dice: Any, faces: Any, asks: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    return _dice_prob_answer(dice, faces, asks)


def _check_dice_prob(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_dice_prob_answer(givens["dice"], givens["faces"], givens["asks"]), answer)


def _coin_prob_one(n: int, k: int) -> Fraction:
    enumerated = sum(1 for code in range(2**n) if _bit_list(code, n).count(1) == k)
    closed = math.comb(n, k)
    if enumerated != closed:
        raise ValueError("coin_formula_mismatch")
    return Fraction(closed, 2**n)


def _coin_prob_answer(asks: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(asks, list) or not 1 <= len(asks) <= 2:
        raise ValueError("bad_asks")
    parts = []
    for ask in asks:
        n = _int(ask.get("n"), "n", 1, 8)
        k = _int(ask.get("k"), "k", 0, n)
        value = _coin_prob_one(n, k)
        parts.append(_prob(value, f"恰有 {k} 個正面的序列有 C({n},{k}) = {math.comb(n, k)} 種，全部 {2**n} 種，機率 {value}。"))
    return _pack(parts)


def coin_count_probability(*, asks: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    return _coin_prob_answer(asks)


def _check_coin_prob(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_coin_prob_answer(givens["asks"]), answer)


# --- one draw -----------------------------------------------------------------------------------------------------------------------------


def _uniform_one(model: str, givens: dict[str, Any], ask: dict[str, Any]) -> Fraction:
    kind = str(ask.get("kind") or "")
    if model == "die":
        faces = _int(givens.get("faces", 6), "faces", 4, 8)
        if kind == "face":
            _int(ask.get("face"), "face", 1, faces)
            return Fraction(1, faces)
        if kind == "faces":
            values = [_int(v, "face", 1, faces) for v in ask.get("values") or []]
            if len(values) != len(set(values)) or not values:
                raise ValueError("bad_faces")
            return Fraction(len(values), faces)
        raise ValueError("bad_uniform_ask")
    if model == "cards":
        deck = _int(givens.get("deck", 52), "deck", 52, 52)
        suits = _int(givens.get("suits", 4), "suits", 4, 4)
        ranks = deck // suits
        if kind == "ranks":
            count = _int(ask.get("count"), "count", 1, 5)
            return Fraction(count * suits, deck)
        if kind == "suit":
            return Fraction(ranks, deck)
        raise ValueError("bad_uniform_ask")
    if model == "numbers":
        n = _int(givens.get("n"), "n", 6, 40)
        if kind != "divisible_by_any":
            raise ValueError("bad_uniform_ask")
        divisors = [_int(v, "divisor", 2, 12) for v in ask.get("divisors") or []]
        if len(divisors) != 2 or divisors[0] == divisors[1]:
            raise ValueError("bad_divisors")
        a, b = divisors
        hit = {i for i in range(1, n + 1) if i % a == 0 or i % b == 0}
        # inclusion-exclusion on the same range
        closed = n // a + n // b - n // math.lcm(a, b)
        if len(hit) != closed:
            raise ValueError("divisibility_mismatch")
        return Fraction(len(hit), n)
    raise ValueError("bad_model")


def _uniform_answer(model: str, givens: dict[str, Any]) -> dict[str, Any]:
    asks = givens.get("asks")
    if not isinstance(asks, list) or not 1 <= len(asks) <= 2:
        raise ValueError("bad_asks")
    parts = []
    for ask in asks:
        value = _uniform_one(model, givens, ask)
        parts.append(_prob(value, f"每一個結果等可能，機率為 {value}。"))
    return _pack(parts)


def uniform_draw_probability(*, model: str, **givens: Any) -> dict[str, Any]:
    return _uniform_answer(str(model), {"model": model, **givens})


def _check_uniform(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    data = dict(givens)
    model = str(data.pop("model"))
    return _same(_uniform_answer(model, data), answer)


# --- urns ---------------------------------------------------------------------------------------------------------------------------------


def _color_tuples(colors: list[int], k: int):
    ranges = [range(min(k, n) + 1) for n in colors]
    for combo in itertools.product(*ranges):
        if sum(combo) == k:
            yield combo


def _hyper(colors: list[int], combo: tuple[int, ...]) -> Fraction:
    ways = 1
    for n, c in zip(colors, combo):
        ways *= math.comb(n, c)
    return Fraction(ways, math.comb(sum(colors), sum(combo)))


def _urn_formula(colors: list[int], k: int, ask: dict[str, Any]) -> Fraction:
    kind = str(ask.get("kind") or "")
    total = sum(_hyper(colors, combo) for combo in _color_tuples(colors, k))
    if total != 1:
        raise ValueError("hypergeometric_not_one")
    if kind == "exact":
        counts = tuple(_int(v, "count", 0, k) for v in ask.get("counts") or [])
        if len(counts) != len(colors) or sum(counts) != k:
            raise ValueError("bad_counts")
        if any(c > n for c, n in zip(counts, colors)):
            return Fraction(0)
        return _hyper(colors, counts)
    if kind == "same_color":
        return sum((_hyper(colors, combo) for combo in _color_tuples(colors, k) if sum(c > 0 for c in combo) == 1), Fraction(0))
    if kind == "not_mono":
        mono = sum((_hyper(colors, combo) for combo in _color_tuples(colors, k) if sum(c > 0 for c in combo) == 1), Fraction(0))
        return 1 - mono
    if kind == "at_most":
        index = _int(ask.get("index"), "index", 0, len(colors) - 1)
        limit = _int(ask.get("count"), "count", 0, k)
        return sum((_hyper(colors, combo) for combo in _color_tuples(colors, k) if combo[index] <= limit), Fraction(0))
    raise ValueError("bad_urn_ask")


def _urn_counts(colors: list[int], k: int, ask: dict[str, Any]) -> tuple[int, int]:
    balls = [color for color, count in enumerate(colors) for _ in range(count)]
    ordered = bool(ask.get("ordered"))
    kind = str(ask.get("kind") or "")

    def ok(cols: list[int]) -> bool:
        tally = [cols.count(i) for i in range(len(colors))]
        if kind == "exact":
            return tally == [_int(v, "count", 0, k) for v in ask["counts"]]
        if kind == "same_color":
            return len(set(cols)) == 1
        if kind == "not_mono":
            return len(set(cols)) > 1
        if kind == "at_most":
            return tally[_int(ask.get("index"), "index", 0, len(colors) - 1)] <= _int(ask.get("count"), "count", 0, k)
        raise ValueError("bad_urn_ask")

    if ordered:
        seqs = list(itertools.permutations(range(len(balls)), k))
    else:
        seqs = list(itertools.combinations(range(len(balls)), k))
    if not seqs:
        raise ValueError("empty_draw")
    good = sum(1 for seq in seqs if ok([balls[i] for i in seq]))
    return good, len(seqs)


def _urn_answer(colors: Any, draw: Any, asks: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(colors, list) or not 2 <= len(colors) <= 4:
        raise ValueError("bad_colors")
    parsed = [_int(v, "color", 0, 20) for v in colors]
    if any(v <= 0 for v in parsed) or not 2 <= sum(parsed) <= 24:
        raise ValueError("bad_colors")
    k = _int(draw, "draw", 2, 3)
    if k > sum(parsed):
        raise ValueError("draw_exceeds")
    if not isinstance(asks, list) or not 1 <= len(asks) <= 2:
        raise ValueError("bad_asks")
    parts = []
    for ask in asks:
        formula = _urn_formula(parsed, k, ask)
        favorable, total = _urn_counts(parsed, k, ask)
        if formula != Fraction(favorable, total):
            raise ValueError("urn_formula_mismatch")
        if formula <= 0:
            raise ValueError("degenerate_event")
        how = "依序取出、不放回" if ask.get("ordered") else "同時取出、不計順序"
        parts.append(_prob(formula, _equiprobable_work(total, favorable, f"{how}的等可能取法 ")))
    return _pack(parts)


def urn_draw_probability(*, colors: Any, draw: Any, asks: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    return _urn_answer(colors, draw, asks)


def _check_urn(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_urn_answer(givens["colors"], givens["draw"], givens["asks"]), answer)


def _repl_formula(sides: int, n: int, ask: dict[str, Any]) -> Fraction:
    kind = str(ask.get("kind") or "")
    if kind == "exactly":
        k = _int(ask.get("k"), "k", 0, n)
        return Fraction(math.comb(n, k) * (sides - 1) ** (n - k), sides**n)
    if kind == "at_least":
        k = _int(ask.get("k"), "k", 1, n)
        good = sum(math.comb(n, j) * (sides - 1) ** (n - j) for j in range(k, n + 1))
        return Fraction(good, sides**n)
    if kind == "not_all_different":
        different = math.perm(sides, n) if n <= sides else 0
        return Fraction(sides**n - different, sides**n)
    raise ValueError("bad_replacement_ask")


def _repl_raw(sides: int, n: int, ask: dict[str, Any]) -> int:
    kind = str(ask.get("kind") or "")
    target = _int(ask.get("target", 1), "target", 1, sides)
    good = 0
    total = 0
    for outcome in itertools.product(range(1, sides + 1), repeat=n):
        total += 1
        if kind == "exactly" and outcome.count(target) == _int(ask.get("k"), "k", 0, n):
            good += 1
        elif kind == "at_least" and outcome.count(target) >= _int(ask.get("k"), "k", 1, n):
            good += 1
        elif kind == "not_all_different" and len(set(outcome)) < n:
            good += 1
    if total != sides**n:
        raise ValueError("replacement_space")
    return good


def _repl_answer(sides: Any, asks: list[dict[str, Any]]) -> dict[str, Any]:
    sides = _int(sides, "sides", 2, 8)
    if not isinstance(asks, list) or not 1 <= len(asks) <= 2:
        raise ValueError("bad_asks")
    parts = []
    for ask in asks:
        n = _int(ask.get("n"), "n", 2, 4)
        if ask.get("kind") != "not_all_different":
            _int(ask.get("target"), "target", 1, sides)
        formula = _repl_formula(sides, n, ask)
        favorable = _repl_raw(sides, n, ask)
        total = sides**n
        if formula != Fraction(favorable, total):
            raise ValueError("replacement_mismatch")
        parts.append(_prob(formula, _equiprobable_work(total, favorable, "放回（或各自選擇）的樣本點有 ")))
    return _pack(parts)


def replacement_count_probability(*, sides: Any, asks: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    return _repl_answer(sides, asks)


def _check_repl(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_repl_answer(givens["sides"], givens["asks"]), answer)


# --- algebra, password, solve, claims -----------------------------------------------------------------------------------------------------


def _algebra_value(probs: list[Fraction], ask: dict[str, Any], disjoint: bool) -> Fraction:
    kind = str(ask.get("kind") or "")
    if kind == "complement":
        return 1 - probs[_int(ask.get("index"), "index", 0, len(probs) - 1)]
    indices = [_int(i, "index", 0, len(probs) - 1) for i in ask.get("indices") or []]
    if len(indices) != len(set(indices)) or len(indices) < 2:
        raise ValueError("bad_indices")
    selected = [probs[i] for i in indices]
    if kind == "union" and disjoint:
        value = sum(selected, Fraction(0))
    elif kind == "union":
        if len(indices) != 2 or "intersection" not in ask:
            raise ValueError("union_needs_intersection")
        inter = _frac(ask.get("intersection"), "intersection")
        if inter < 0 or inter > min(selected):
            raise ValueError("bad_intersection")
        value = selected[0] + selected[1] - inter
    elif kind == "intersection":
        if len(indices) != 2 or "union" not in ask:
            raise ValueError("intersection_needs_union")
        union = _frac(ask.get("union"), "union")
        value = selected[0] + selected[1] - union
        if value < 0 or value > min(selected) or union > 1:
            raise ValueError("bad_union")
    else:
        raise ValueError("bad_algebra_ask")
    if value < 0 or value > 1:
        raise ValueError("probability_out_of_range")
    return value


def _algebra_answer(probs: Any, asks: list[dict[str, Any]], pairwise_disjoint: bool = False) -> dict[str, Any]:
    if not isinstance(probs, list) or not 2 <= len(probs) <= 3:
        raise ValueError("bad_probs")
    parsed = [_frac(v, "prob") for v in probs]
    if any(v <= 0 or v > 1 for v in parsed):
        raise ValueError("bad_probs")
    if pairwise_disjoint and sum(parsed, Fraction(0)) > 1:
        raise ValueError("disjoint_overflow")
    if not isinstance(asks, list) or not 1 <= len(asks) <= 3:
        raise ValueError("bad_asks")
    parts = []
    for ask in asks:
        if pairwise_disjoint and ask.get("kind") == "union" and "intersection" in ask:
            raise ValueError("disjoint_union_has_no_extra_intersection")
        value = _algebra_value(parsed, ask, pairwise_disjoint)
        # recompute complement and inclusion-exclusion from the stored fractions only
        parts.append(_prob(value, f"依機率性質得 {value}。"))
    return _pack(parts)


def probability_algebra(*, probs: Any, asks: list[dict[str, Any]], pairwise_disjoint: bool = False, **_: Any) -> dict[str, Any]:
    return _algebra_answer(probs, asks, bool(pairwise_disjoint))


def _check_algebra(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_algebra_answer(givens["probs"], givens["asks"], bool(givens.get("pairwise_disjoint"))), answer)


def _password_answer(symbols: Any, wrong_limit: Any) -> dict[str, Any]:
    symbols = _int(symbols, "symbols", 3, 6)
    wrong_limit = _int(wrong_limit, "wrong_limit", 1, 5)
    space = math.factorial(symbols)
    if wrong_limit >= space:
        raise ValueError("limit_too_large")
    first = Fraction(1, space)
    confiscated = Fraction(space - wrong_limit, space)
    # failing the first `wrong_limit` distinct guesses telescopes to the same fraction
    running = Fraction(1)
    for used in range(wrong_limit):
        running *= Fraction(space - 1 - used, space - used)
    if running != confiscated:
        raise ValueError("password_mismatch")
    return _pack([
        _prob(first, _equiprobable_work(space, 1, f"{symbols} 個不同符號的排列有 ")),
        _prob(confiscated, _equiprobable_work(space, space - wrong_limit, f"前 {wrong_limit} 次都猜錯才被沒收。等可能排列 ")),
    ])


def password_guess(*, symbols: Any, wrong_limit: Any, alphabet: list[Any] | None = None, **_: Any) -> dict[str, Any]:
    if alphabet is not None:
        if len(alphabet) != _int(symbols, "symbols", 3, 6) or len(set(map(str, alphabet))) != len(alphabet):
            raise ValueError("bad_alphabet")
    return _password_answer(symbols, wrong_limit)


def _check_password(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_password_answer(givens["symbols"], givens["wrong_limit"]), answer)


def _solve_black(white: int, target: Fraction) -> int:
    found = []
    for black in range(1, 80):
        if Fraction(math.comb(white, 2), math.comb(white + black, 2)) == target:
            found.append(black)
    if len(found) != 1:
        raise ValueError("n_not_unique")
    # (w+n)(w+n-1) = w(w-1) / target, so n^2 + (2w-1)n + w(w-1) - product = 0.
    product = Fraction(white * (white - 1), 1) / target
    if product.denominator != 1:
        raise ValueError("n_not_integer")
    disc = (2 * white - 1) ** 2 - 4 * (white * (white - 1) - int(product))
    root = math.isqrt(disc)
    if root * root != disc:
        raise ValueError("n_not_integer")
    n = (-(2 * white - 1) + root) // 2
    if n != found[0]:
        raise ValueError("n_mismatch")
    return n


def _solve_answer(white: Any, target: Any) -> dict[str, Any]:
    white = _int(white, "white", 3, 16)
    goal = _frac(target, "target")
    if goal <= 0 or goal >= 1:
        raise ValueError("bad_target")
    black = _solve_black(white, goal)
    return _pack([_count(Fraction(black), f"由 C({white},2)/C({white}+n,2) = {goal} 解得 n = {black}。")])


def solve_urn_count(*, white: Any, target: Any, **_: Any) -> dict[str, Any]:
    return _solve_answer(white, target)


def _check_solve(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_solve_answer(givens["white"], givens["target"]), answer)


def _claim_truth(givens: dict[str, Any]) -> tuple[bool, str]:
    style = str(givens.get("style") or "")
    if style == "urn_half":
        red = givens.get("red")
        if red is None:
            return False, "只知道兩色都有、不知道顆數，不能推出機率是 1/2。"
        red_n = _int(red, "red", 1, 12)
        white_n = _int(givens.get("white"), "white", 1, 12)
        return red_n == white_n, f"紅球 {red_n} 顆、白球 {white_n} 顆，機率是 {Fraction(red_n, red_n + white_n)}。"
    if style == "dice_sum":
        total = _int(givens.get("total"), "total", 2, 12)
        stated = _frac(givens.get("stated"), "stated")
        actual = _dice_closed(2, 6, {"kind": "sum_eq", "n": total})
        if actual != _dice_enum(2, 6, {"kind": "sum_eq", "n": total}):
            raise ValueError("dice_formula_mismatch")
        return stated == actual, f"點數和為 {total} 的機率是 {actual}，敘述寫的是 {stated}。"
    if style == "at_least_one_six":
        stated_miss = _int(givens.get("stated_miss"), "stated_miss", 1, 35)
        actual_miss = 5 * 5
        claim = 1 - Fraction(stated_miss, 36)
        actual = 1 - Fraction(actual_miss, 36)
        return claim == actual, f"兩次都不是 6 點有 {actual_miss} 種，至少一次 6 點的機率是 {actual}。"
    raise ValueError("bad_claim")


def _claim_answer(givens: dict[str, Any]) -> dict[str, Any]:
    truth, work = _claim_truth(givens)
    return _pack([_choice(truth, TRUE_FALSE, work)])


def classical_claim(**givens: Any) -> dict[str, Any]:
    return _claim_answer(givens)


def _check_claim(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return _same(_claim_answer(givens), answer)


_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "coin_outcome_space": (coin_outcome_space, _check_coin, ("n", "observable")),
    "draw_outcome_space": (draw_outcome_space, _check_draw, ("n", "asks")),
    "coded_event_sets": (coded_event_sets, _check_coded, ("n", "asks")),
    "dice_event_sets": (dice_event_sets, _check_dice_sets, ("a", "b")),
    "event_relation": (event_relation, _check_relation, ("model",)),
    "uniform_draw_probability": (uniform_draw_probability, _check_uniform, ("model", "asks")),
    "coin_count_probability": (coin_count_probability, _check_coin_prob, ("asks",)),
    "dice_count_probability": (dice_count_probability, _check_dice_prob, ("dice", "faces", "asks")),
    "urn_draw_probability": (urn_draw_probability, _check_urn, ("colors", "draw", "asks")),
    "replacement_count_probability": (replacement_count_probability, _check_repl, ("sides", "asks")),
    "probability_algebra": (probability_algebra, _check_algebra, ("probs", "asks")),
    "password_guess": (password_guess, _check_password, ("symbols", "wrong_limit")),
    "solve_urn_count": (solve_urn_count, _check_solve, ("white", "target")),
    "classical_claim": (classical_claim, _check_claim, ("style",)),
}

OPERATIONS = tuple(_OPERATIONS)


def build_classical_probability_matrix(
    *, domain_operation: str | None = None, seed: int | None = None, constraints: dict[str, Any] | None = None, **_: Any
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_classical_probability_operation:{operation}")
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
