from __future__ import annotations

import re
from typing import Any

QUADRANT_CANONICAL_LABELS: tuple[str, ...] = (
    "第一象限",
    "第二象限",
    "第三象限",
    "第四象限",
)

_QUADRANT_FROM_LABEL: dict[str, str] = {
    "第一象限": "Q1",
    "第二象限": "Q2",
    "第三象限": "Q3",
    "第四象限": "Q4",
}

_CN_NUMERAL = {"一": "1", "二": "2", "三": "3", "四": "4"}
_ROMAN_TO_ASCII = {"Ⅰ": "I", "Ⅱ": "II", "Ⅲ": "III", "Ⅳ": "IV"}
_ASCII_ROMAN = {"I": "1", "II": "2", "III": "3", "IV": "4"}


def _preprocess(text: object) -> str:
    s = str(text or "").strip()
    if not s:
        return ""
    s = s.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    for uni, ascii_r in _ROMAN_TO_ASCII.items():
        s = s.replace(uni, ascii_r)
    s = re.sub(r"\s+", "", s)
    return s


def _core_token(text: str) -> str:
    s = _preprocess(text)
    if not s:
        return ""
    if s.startswith("第"):
        s = s[1:]
    if s.endswith("象限"):
        s = s[:-2]
    return s


def _token_to_quadrant(token: str) -> str | None:
    if not token:
        return None
    if token in _QUADRANT_FROM_LABEL:
        return _QUADRANT_FROM_LABEL[token]
    core = _core_token(token)
    if core in _QUADRANT_FROM_LABEL:
        return _QUADRANT_FROM_LABEL[core]
    if core in {"1", "2", "3", "4"}:
        return f"Q{core}"
    if core in _CN_NUMERAL:
        return f"Q{_CN_NUMERAL[core]}"
    upper = core.upper()
    if upper in _ASCII_ROMAN:
        return f"Q{_ASCII_ROMAN[upper]}"
    if core in {"第一", "第二", "第三", "第四"}:
        return _QUADRANT_FROM_LABEL[f"{core}象限"]
    return None


def normalize_quadrant_answer(value: object) -> str | None:
    """Return canonical Q1..Q4 for quadrant answers, else None."""
    raw = str(value or "").strip()
    if not raw:
        return None
    for candidate in (raw, _preprocess(raw), _core_token(raw)):
        q = _token_to_quadrant(candidate)
        if q:
            return q
    return None


def is_quadrant_correct_answer(correct_answer: object) -> bool:
    return str(correct_answer or "").strip() in QUADRANT_CANONICAL_LABELS


AXIS_CANONICAL_LABELS: tuple[str, ...] = ("x軸正向", "y軸正向", "x軸負向", "y軸負向")
_AXIS_FROM_CODE: dict[str, str] = {
    "positive_x": "x軸正向",
    "positive_y": "y軸正向",
    "negative_x": "x軸負向",
    "negative_y": "y軸負向",
}
_AXIS_RE = re.compile(r"^(?P<pre>正|負|\+|-)?(?P<axis>[xy])軸?(?P<post>正|負)?(?:向|方向|半軸|軸)?$")


def normalize_axis_answer(value: object) -> str | None:
    """Return `+x` / `-x` / `+y` / `-y` for a coordinate half-axis answer, else None."""
    s = _preprocess(value).lower().replace("的", "").replace("上", "")
    s = _AXIS_FROM_CODE.get(s, s)
    match = _AXIS_RE.match(s)
    if not match:
        return None
    signs = [token for token in (match.group("pre"), match.group("post")) if token]
    if len(signs) != 1:
        return None
    return ("+" if signs[0] in {"正", "+"} else "-") + match.group("axis")


def angle_location_label(value: object) -> str:
    """Student-facing label for a terminal-side location (quadrant number or axis code)."""
    raw = str(value or "").strip()
    if raw in _AXIS_FROM_CODE:
        return _AXIS_FROM_CODE[raw]
    quadrant = normalize_quadrant_answer(raw)
    if quadrant:
        return QUADRANT_CANONICAL_LABELS[int(quadrant[1]) - 1]
    return raw


def check_quadrant_answer(user_answer: object, correct_answer: object) -> bool | None:
    """
    Compare quadrant / half-axis answers with equivalence rules.

    Returns None when correct_answer is not a canonical quadrant or axis label,
    so callers can fall back to their default checker.
    """
    if str(correct_answer or "").strip() in AXIS_CANONICAL_LABELS:
        actual_axis = normalize_axis_answer(user_answer)
        return actual_axis is not None and actual_axis == normalize_axis_answer(correct_answer)
    if not is_quadrant_correct_answer(correct_answer):
        return None
    expected = normalize_quadrant_answer(correct_answer)
    actual = normalize_quadrant_answer(user_answer)
    if expected is None:
        return None
    if actual is None:
        return False
    return actual == expected


def check(user_answer: Any, correct_answer: Any) -> bool:
    result = check_quadrant_answer(user_answer, correct_answer)
    if result is not None:
        return result
    return str(user_answer or "").strip() == str(correct_answer or "").strip()
