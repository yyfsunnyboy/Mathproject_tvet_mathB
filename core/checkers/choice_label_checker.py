from __future__ import annotations

import re
from typing import Sequence


def _normalize_text(s: object) -> str:
    t = str(s or "")
    t = t.replace("（", "(").replace("）", ")").replace("，", ",")
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def _label_to_index(label: str) -> int | None:
    m = re.match(r"^[\(\[]?([a-d])[\)\]\.]?$", label.lower())
    if m:
        return ord(m.group(1)) - ord("a")
    if label in {"1", "2", "3", "4"}:
        return int(label) - 1
    return None


def choice_value_to_label(value: object, choices: Sequence[str]) -> str | None:
    raw = _normalize_text(value)
    idx = _label_to_index(raw.replace(" ", ""))
    if idx is not None and 0 <= idx < len(choices):
        return chr(ord("A") + idx)
    for i, ch in enumerate(choices):
        if _normalize_text(ch) == raw:
            return chr(ord("A") + i)
    return None


def check_choice_label(user_answer: object, correct_answer: object, choices: Sequence[str]) -> bool:
    u = choice_value_to_label(user_answer, choices)
    c = choice_value_to_label(correct_answer, choices)
    return u is not None and c is not None and u == c

