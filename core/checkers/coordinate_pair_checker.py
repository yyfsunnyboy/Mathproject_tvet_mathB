from __future__ import annotations

import re
from typing import Any

_PAIR_SEP = re.compile(r"[,，]")
_XY_ASSIGN = re.compile(
    r"x\s*=\s*([+-]?\d+(?:\.\d+)?)\s*[,，]?\s*y\s*=\s*([+-]?\d+(?:\.\d+)?)",
    re.I,
)
_PAREN_PAIR = re.compile(
    r"[\(（]\s*([+-]?\d+(?:\.\d+)?)\s*[,，]\s*([+-]?\d+(?:\.\d+)?)\s*[\)）]"
)


def _to_num(token: str) -> float | None:
    try:
        num = float(str(token).strip())
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
    m2 = _PAREN_PAIR.search(raw)
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
