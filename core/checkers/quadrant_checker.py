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


def check_quadrant_answer(user_answer: object, correct_answer: object) -> bool | None:
    """
    Compare quadrant answers with equivalence rules.

    Returns None when correct_answer is not a canonical quadrant label,
    so callers can fall back to their default checker.
    """
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
