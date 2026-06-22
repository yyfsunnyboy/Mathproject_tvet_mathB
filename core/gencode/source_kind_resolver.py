"""Resolve canonical SOURCE_KIND and curriculum ordering from textbook metadata."""

from __future__ import annotations

from typing import Any

SOURCE_KIND_ORDER: dict[str, int] = {
    "example": 10,
    "quiz": 20,
    "test": 30,
}

SOURCE_KIND_DIFFICULTY: dict[str, str] = {
    "example": "easy",
    "quiz": "easy",
    "test": "hard",
}


def resolve_source_kind_from_textbook_row(row: dict[str, Any] | None) -> str:
    """Map textbook metadata to canonical SOURCE_KIND (not component_id)."""
    if not isinstance(row, dict):
        return "example"

    explicit = str(row.get("source_kind") or "").strip().lower()
    if explicit in SOURCE_KIND_ORDER:
        return explicit

    problem_type = str(row.get("problem_type") or "").strip().lower()
    if problem_type in {"quiz", "in_class", "class_quiz"}:
        return "quiz"
    if problem_type in {"test", "self_assessment", "exam"}:
        return "test"

    description = str(row.get("source_description") or "").strip().lower()
    if any(token in description for token in ("隨堂", "quiz", "測驗一", "測驗二")):
        return "quiz"
    if any(token in description for token in ("自我評量", "self", "test", "評量")):
        return "test"
    if any(token in description for token in ("例題", "example", "範例")):
        return "example"

    return "example"


def resolve_order_weight(source_kind: str) -> int:
    return SOURCE_KIND_ORDER.get(str(source_kind or "").strip().lower(), 10)


def resolve_difficulty_level(source_kind: str) -> str:
    return SOURCE_KIND_DIFFICULTY.get(str(source_kind or "").strip().lower(), "easy")
