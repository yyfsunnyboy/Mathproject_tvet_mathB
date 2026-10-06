"""Student-facing display text for answers stored on mistake notebook entries."""

from __future__ import annotations

import json
import re

UNANSWERED_LABEL = "未作答"
PART_SEPARATOR = "\u3000"

_PART_KEY = re.compile(r"^part_(\d+)$")
_LATEX_HINT = re.compile(r"\\[A-Za-z]+|[\^_]")
_MATH_DELIMITERS = ("$", "\\(", "\\[")


def _is_blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _part_text(value: object) -> str:
    if _is_blank(value):
        return UNANSWERED_LABEL
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value).strip()
    if _LATEX_HINT.search(text) and not any(mark in text for mark in _MATH_DELIMITERS):
        return f"\\({text}\\)"
    return text


def _ordered_parts(parsed: dict) -> list[object]:
    def sort_key(item: tuple[int, str]) -> tuple[int, int]:
        index, key = item
        match = _PART_KEY.match(str(key))
        return (int(match.group(1)), index) if match else (10**9, index)

    keys = [key for _, key in sorted(enumerate(parsed), key=sort_key)]
    return [parsed[key] for key in keys]


def format_mistake_answer(raw: object) -> str:
    """Render a stored answer for students without exposing the storage format.

    JSON objects/arrays are shown as their values ("(1) a　(2) b" when there
    are several); anything that is not valid JSON is shown unchanged.
    """
    if _is_blank(raw):
        return UNANSWERED_LABEL
    if not isinstance(raw, str):
        parsed: object = raw
    else:
        text = raw.strip()
        if not text.startswith(("{", "[")):
            return _part_text(text)
        try:
            parsed = json.loads(text)
        except (TypeError, ValueError):
            return raw

    if isinstance(parsed, dict):
        values = _ordered_parts(parsed)
    elif isinstance(parsed, list):
        values = list(parsed)
    else:
        return _part_text(parsed)

    if not values or all(_is_blank(value) for value in values):
        return UNANSWERED_LABEL
    if len(values) == 1:
        return _part_text(values[0])
    return PART_SEPARATOR.join(f"({i}) {_part_text(value)}" for i, value in enumerate(values, start=1))
