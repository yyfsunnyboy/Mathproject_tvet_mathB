from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

_PAIR_SEP = re.compile(r"[,，]")
_NUM_TOKEN = r"[+-]?(?:\d+/\d+|\d+(?:\.\d+)?)"
_XY_ASSIGN = re.compile(
    rf"x\s*=\s*({_NUM_TOKEN})\s*[,，]?\s*y\s*=\s*({_NUM_TOKEN})",
    re.I,
)
_PAREN_PAIR = re.compile(
    rf"[\(（]\s*({_NUM_TOKEN})\s*[,，]\s*({_NUM_TOKEN})\s*[\)）]"
)
_POINT_PAIR = re.compile(
    rf"[Pp]\s*\(\s*({_NUM_TOKEN})\s*[,，]\s*({_NUM_TOKEN})\s*\)"
)


def _to_num(token: str) -> float | None:
    text = str(token).strip()
    if not text:
        return None
    try:
        if "/" in text:
            frac = Fraction(text)
            num = float(frac.numerator) / float(frac.denominator)
        else:
            num = float(text)
        return int(num) if num.is_integer() else num
    except Exception:
        return None


def parse_coordinate_pair_answer(text: object) -> tuple[float, float] | None:
    raw = str(text or "").strip()
    if not raw:
        return None
    raw = raw.replace("（", "(").replace("）", ")").replace("，", ",")
    m = _XY_ASSIGN.search(raw)
    if m:
        x, y = _to_num(m.group(1)), _to_num(m.group(2))
        if x is not None and y is not None:
            return (x, y)
    for pattern in (_POINT_PAIR, _PAREN_PAIR):
        m2 = pattern.search(raw)
        if m2:
            x, y = _to_num(m2.group(1)), _to_num(m2.group(2))
            if x is not None and y is not None:
                return (x, y)
    if isinstance(text, (list, tuple)) and len(text) >= 2:
        x, y = _to_num(text[0]), _to_num(text[1])
        if x is not None and y is not None:
            return (x, y)
    parts = [p.strip() for p in _PAIR_SEP.split(raw.strip("()（） ")) if p.strip()]
    if len(parts) >= 2:
        x, y = _to_num(parts[0]), _to_num(parts[1])
        if x is not None and y is not None:
            return (x, y)
    return None


def check_coordinate_pair_answer(user_answer: object, correct_answer: object) -> bool:
    user = parse_coordinate_pair_answer(user_answer)
    correct = parse_coordinate_pair_answer(correct_answer)
    if user is None or correct is None:
        return False
    return user == correct
