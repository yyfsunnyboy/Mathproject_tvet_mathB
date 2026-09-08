from __future__ import annotations

import re
from typing import Any, Sequence


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


def _choice_entries(choices: Sequence[Any]) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for i, item in enumerate(choices or []):
        default_label = chr(ord("A") + i)
        if isinstance(item, dict):
            raw_label = str(item.get("label") or item.get("key") or default_label).strip()
            idx = _label_to_index(raw_label.replace(" ", ""))
            label = chr(ord("A") + idx) if idx is not None else (raw_label[:1].upper() or default_label)
            text = str(item.get("text") or item.get("value") or item.get("display") or "").strip()
        else:
            label = default_label
            text = str(item).strip()
        entries.append((label, text))
    return entries


def choice_value_to_label(value: object, choices: Sequence[Any]) -> str | None:
    raw = _normalize_text(value)
    entries = _choice_entries(choices)
    compact = raw.replace(" ", "")
    idx = _label_to_index(compact)
    if idx is not None and 0 <= idx < len(entries):
        return entries[idx][0]
    for label, text in entries:
        if _normalize_text(text) == raw or _normalize_text(label) == raw:
            return label
    return None


def resolve_choice_semantic(value: object, choices: Sequence[Any]) -> str | None:
    """Map a student label or pasted choice text to the choice's semantic text."""
    entries = _choice_entries(choices)
    if not entries:
        return str(value or "").strip() or None
    raw = _normalize_text(value)
    compact = raw.replace(" ", "")
    idx = _label_to_index(compact)
    if idx is not None and 0 <= idx < len(entries):
        return entries[idx][1]
    for _label, text in entries:
        if _normalize_text(text) == raw:
            return text
    label = choice_value_to_label(value, choices)
    if label is None:
        return None
    for item_label, text in entries:
        if item_label == label:
            return text
    return None


def check_choice_label(user_answer: object, correct_answer: object, choices: Sequence[Any]) -> bool:
    """Compare by resolved semantic choice value, not a frozen ABCD position."""
    entries = _choice_entries(choices)
    if not entries:
        u = choice_value_to_label(user_answer, ["A", "B", "C", "D"])
        c = choice_value_to_label(correct_answer, ["A", "B", "C", "D"])
        return u is not None and c is not None and u == c

    user_semantic = resolve_choice_semantic(user_answer, choices)
    correct_semantic = resolve_choice_semantic(correct_answer, choices)
    if user_semantic is None or correct_semantic is None:
        return False
    if _normalize_text(user_semantic) == _normalize_text(correct_semantic):
        return True
    try:
        from core.checkers.expression_equivalence_checker import check_expression_equivalence_answer

        if check_expression_equivalence_answer(user_semantic, correct_semantic):
            return True
    except Exception:
        pass
    user_label = choice_value_to_label(user_answer, entries)
    correct_label = choice_value_to_label(correct_answer, entries)
    return user_label is not None and correct_label is not None and user_label == correct_label
