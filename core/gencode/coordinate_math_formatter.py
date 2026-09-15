"""Inline-math formatting helpers for coordinate-geometry question stems."""

from __future__ import annotations


def inline_math(content: object) -> str:
    """Wrap one complete math atom/expression in the project's `$...$` delimiter."""
    text = str(content).strip()
    if not text:
        raise ValueError("inline_math_content_empty")
    if text.startswith("$$") or text.endswith("$$"):
        raise ValueError("display_math_not_allowed")
    if text.startswith("$") and text.endswith("$") and text.count("$") == 2:
        return text
    if "$" in text:
        raise ValueError("nested_or_unbalanced_inline_math")
    return f"${text}$"


def point_with_coordinates(name: str, x: object, y: object) -> str:
    """Format a named coordinate pair as one inline-math expression."""
    return inline_math(f"{name}({x},{y})")


def overline_segment(first: str, second: str) -> str:
    """Format a two-point segment name as one inline-math expression."""
    return inline_math(f"\\overline{{{first}{second}}}")
