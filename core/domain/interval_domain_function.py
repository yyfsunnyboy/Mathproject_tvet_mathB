from __future__ import annotations

from fractions import Fraction
from math import ceil, floor
from typing import Any


def make_interval(left: Fraction | int | str | None, right: Fraction | int | str | None, left_closed: bool, right_closed: bool) -> dict[str, Any]:
    l = Fraction(left) if left is not None else None
    r = Fraction(right) if right is not None else None
    if l is not None and r is not None and l > r:
        raise ValueError("left endpoint cannot be greater than right endpoint")
    return {"type": "interval", "left": l, "right": r, "left_closed": bool(left_closed), "right_closed": bool(right_closed)}


def make_union(intervals: list[dict[str, Any]]) -> dict[str, Any]:
    return {"type": "union", "intervals": normalize_interval_union(intervals)}


def normalize_interval_union(intervals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    parts = [x for x in intervals if isinstance(x, dict) and x.get("type") == "interval"]
    if not parts:
        return []
    sorted_parts = sorted(parts, key=lambda x: (float("-inf") if x["left"] is None else float(x["left"]), not bool(x["left_closed"])))
    merged: list[dict[str, Any]] = []
    for cur in sorted_parts:
        if not merged:
            merged.append(dict(cur))
            continue
        last = merged[-1]
        if _can_merge(last, cur):
            merged[-1] = _merge_interval(last, cur)
        else:
            merged.append(dict(cur))
    return merged


def _can_merge(a: dict[str, Any], b: dict[str, Any]) -> bool:
    if a["right"] is None or b["left"] is None:
        return True
    if a["right"] > b["left"]:
        return True
    if a["right"] < b["left"]:
        return False
    return bool(a["right_closed"] or b["left_closed"])


def _merge_interval(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    left = a["left"]
    left_closed = a["left_closed"]
    if a["right"] is None or b["right"] is None:
        right = None
        right_closed = False
    elif a["right"] > b["right"]:
        right = a["right"]
        right_closed = a["right_closed"]
    elif a["right"] < b["right"]:
        right = b["right"]
        right_closed = b["right_closed"]
    else:
        right = a["right"]
        right_closed = bool(a["right_closed"] or b["right_closed"])
    return {"type": "interval", "left": left, "right": right, "left_closed": left_closed, "right_closed": right_closed}


def _format_num(v: Fraction | None) -> str:
    if v is None:
        return "∞"
    if v.denominator == 1:
        return str(v.numerator)
    s = f"{float(v):.10f}".rstrip("0").rstrip(".")
    return "0" if s in {"-0", ""} else s


def format_interval(interval_or_union: dict[str, Any]) -> str:
    if interval_or_union.get("type") == "union":
        return " ∪ ".join(format_interval(x) for x in interval_or_union.get("intervals", []))
    left = interval_or_union.get("left")
    right = interval_or_union.get("right")
    lbr = "[" if interval_or_union.get("left_closed") else "("
    rbr = "]" if interval_or_union.get("right_closed") else ")"
    left_s = "-∞" if left is None else _format_num(left)
    right_s = "∞" if right is None else _format_num(right)
    return f"{lbr}{left_s},{right_s}{rbr}"


def count_integer_solutions(interval_or_union: dict[str, Any]) -> int | None:
    if interval_or_union.get("type") == "union":
        total = 0
        for part in normalize_interval_union(interval_or_union.get("intervals", [])):
            c = _count_interval_integers(part)
            if c is None:
                return None
            total += c
        return total
    return _count_interval_integers(interval_or_union)


def _count_interval_integers(interval: dict[str, Any]) -> int | None:
    left = interval.get("left")
    right = interval.get("right")
    if left is None or right is None:
        return None
    lo = ceil(left) if interval.get("left_closed") else floor(left) + 1
    hi = floor(right) if interval.get("right_closed") else ceil(right) - 1
    if hi < lo:
        return 0
    return hi - lo + 1
