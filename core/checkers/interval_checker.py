from __future__ import annotations

import re
from typing import List, Tuple

Interval = Tuple[float, float, bool, bool]  # low, high, low_closed, high_closed


def _normalize(text: object) -> str:
    s = str(text or "").strip()
    repl = {
        "，": ",",
        "＜": "<",
        "＞": ">",
        "≤": "<=",
        "≥": ">=",
        "∞": "inf",
        "−": "-",
        "（": "(",
        "）": ")",
        "。": "",
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    s = s.replace("或", " or ").replace("∪", " U ")
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("x =", "x=").replace("x< =", "x<=").replace("x> =", "x>=")
    return s


def _parse_num(token: str) -> float:
    t = token.strip().lower()
    if t in {"inf", "+inf", "+infinity", "infinity"}:
        return float("inf")
    if t in {"-inf", "-infinity"}:
        return float("-inf")
    return float(t)


def _split_union(s: str) -> List[str]:
    t = s.replace(" u ", " U ").replace(" or ", " U ")
    return [x.strip() for x in re.split(r"\s+U\s+", t) if x.strip()]


def _parse_bracket_interval(part: str) -> List[Interval]:
    m = re.match(r"^([\[\(])\s*([^,]+)\s*,\s*([^\]\)]+)\s*([\]\)])$", part)
    if not m:
        return []
    lbr, lo, hi, rbr = m.groups()
    low = _parse_num(lo)
    high = _parse_num(hi)
    return [(low, high, lbr == "[", rbr == "]")]


def _parse_inequality(part: str) -> List[Interval]:
    p = part.replace(" ", "")
    m = re.match(r"^([\-]?\w+)(<=|<)x(<=|<)([\-]?\w+)$", p)
    if m:
        lo, op1, op2, hi = m.groups()
        return [(_parse_num(lo), _parse_num(hi), op1 == "<=", op2 == "<=")]
    m = re.match(r"^x(<=|<|>=|>)([\-]?\w+)$", p)
    if m:
        op, val = m.groups()
        v = _parse_num(val)
        if op == "<":
            return [(float("-inf"), v, False, False)]
        if op == "<=":
            return [(float("-inf"), v, False, True)]
        if op == ">":
            return [(v, float("inf"), False, False)]
        if op == ">=":
            return [(v, float("inf"), True, False)]
    m = re.match(r"^([\-]?\w+)(<=|<)x$", p)
    if m:
        lo, op = m.groups()
        return [(_parse_num(lo), float("inf"), op == "<=", False)]
    m = re.match(r"^([\-]?\w+)(>=|>)x$", p)
    if m:
        hi, op = m.groups()
        return [(float("-inf"), _parse_num(hi), False, op == ">=")]
    return []


def parse_interval_answer(text: object) -> List[Interval]:
    s = _normalize(text).lower()
    parts = _split_union(s)
    intervals: List[Interval] = []
    for part in parts:
        got = _parse_bracket_interval(part)
        if not got:
            got = _parse_inequality(part)
        if not got:
            return []
        intervals.extend(got)
    intervals.sort(key=lambda x: (x[0], x[1], not x[2], not x[3]))
    return intervals


def check_interval_answer(user_answer: object, correct_answer: object) -> bool:
    u = parse_interval_answer(user_answer)
    c = parse_interval_answer(correct_answer)
    if not u or not c:
        return False
    if len(u) != len(c):
        return False
    for a, b in zip(u, c):
        if a != b:
            return False
    return True


def check(user_answer: object, correct_answer: object) -> dict:
    ok = check_interval_answer(user_answer, correct_answer)
    if ok:
        return {"correct": True, "result": "答對了"}
    return {"correct": False, "result": f"答錯了，正確答案是 {correct_answer}"}

