from __future__ import annotations

import math
import re
from fractions import Fraction
from typing import Any

DEFAULT_NUMERIC_ABS_TOLERANCE = 1e-5
DEFAULT_NUMERIC_REL_TOLERANCE = 1e-9

_NUM_TOKEN = r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:/\d+(?:\.\d+)?)?"
_ASSIGNMENT_RE = re.compile(r"^(?:x|y)\s*=\s*(.+)$", re.I)
_POINT_LABEL_RE = re.compile(r"^[A-Za-z]\s*\((.*)\)$")


def _normalize_text(value: Any) -> str:
    text = str(value or "").strip()
    replacements = {
        "（": "(",
        "）": ")",
        "，": ",",
        "、": ",",
        "；": ";",
        "﹐": ",",
        "：": ":",
        "－": "-",
        "−": "-",
        "＋": "+",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text.strip()


def _parse_scalar(value: Any) -> Fraction | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return Fraction(str(value))

    text = _normalize_text(value)
    if not text:
        return None
    text = text.replace(" ", "")
    if not re.fullmatch(_NUM_TOKEN, text):
        return None
    try:
        return Fraction(text)
    except (ValueError, ZeroDivisionError):
        return None


def _strip_wrapping_pair(text: str) -> str:
    text = text.strip()
    label_match = _POINT_LABEL_RE.fullmatch(text)
    if label_match:
        return label_match.group(1).strip()
    if text.startswith("(") and text.endswith(")"):
        return text[1:-1].strip()
    return text


def _strip_assignment(text: str) -> str:
    match = _ASSIGNMENT_RE.fullmatch(text.strip())
    return match.group(1).strip() if match else text.strip()


def _split_pair_components(text: str) -> list[str]:
    parts = [part.strip() for part in text.split(",")]
    if len(parts) != 2:
        return []
    return [_strip_assignment(part) for part in parts]


def parse_coordinate_pair_answer(text: object) -> tuple[Fraction, Fraction] | None:
    if isinstance(text, (list, tuple)) and len(text) == 2:
        x_value = _parse_scalar(text[0])
        y_value = _parse_scalar(text[1])
        if x_value is not None and y_value is not None:
            return (x_value, y_value)
        return None

    raw = _normalize_text(text)
    if not raw:
        return None
    if ";" in raw:
        return None

    body = _strip_wrapping_pair(raw)
    components = _split_pair_components(body)
    if not components:
        return None
    x_value = _parse_scalar(components[0])
    y_value = _parse_scalar(components[1])
    if x_value is None or y_value is None:
        return None
    return (x_value, y_value)


def _scalar_equivalent(actual: Fraction, expected: Fraction) -> bool:
    if actual == expected:
        return True
    return math.isclose(
        float(actual),
        float(expected),
        rel_tol=DEFAULT_NUMERIC_REL_TOLERANCE,
        abs_tol=DEFAULT_NUMERIC_ABS_TOLERANCE,
    )


def check_coordinate_pair_answer(user_answer: object, correct_answer: object) -> bool:
    user = parse_coordinate_pair_answer(user_answer)
    correct = parse_coordinate_pair_answer(correct_answer)
    if user is None or correct is None:
        return False
    return all(_scalar_equivalent(actual, expected) for actual, expected in zip(user, correct))
