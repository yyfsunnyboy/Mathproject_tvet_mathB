"""Canonical choice values with presentation-only LaTeX display fields."""

from __future__ import annotations

import re
from typing import Any

_INTEGER_OR_DECIMAL = re.compile(r"^[+-]?\d+(?:\.\d+)?$")
_COORDINATE_PAIR = re.compile(
    r"^\(\s*[+-]?\d+(?:\.\d+)?(?:/\d+)?\s*,\s*[+-]?\d+(?:\.\d+)?(?:/\d+)?\s*\)$"
)
_FRACTION = re.compile(r"^([+-]?)(\d+)/(\d+)$")
_RADICAL = re.compile(r"^sqrt\(([^()]+)\)$")
_COEFFICIENT_RADICAL = re.compile(r"^([+-]?\d+)\*sqrt\(([^()]+)\)$")
_RADICAL_FRACTION = re.compile(r"^([+-]?\d+)\*sqrt\(([^()]+)\)/(\d+)$")


def format_choice_math_display(value: Any) -> str:
    """Return MathJax-ready display text without changing the canonical value."""
    canonical = str(value or "").strip()
    if not canonical:
        return canonical
    if _INTEGER_OR_DECIMAL.fullmatch(canonical) or _COORDINATE_PAIR.fullmatch(canonical):
        return canonical

    match = _RADICAL_FRACTION.fullmatch(canonical)
    if match:
        coefficient, radicand, denominator = match.groups()
        return rf"\(\frac{{{coefficient}\sqrt{{{radicand}}}}}{{{denominator}}}\)"

    match = _COEFFICIENT_RADICAL.fullmatch(canonical)
    if match:
        coefficient, radicand = match.groups()
        return rf"\({coefficient}\sqrt{{{radicand}}}\)"

    match = _RADICAL.fullmatch(canonical)
    if match:
        return rf"\(\sqrt{{{match.group(1)}}}\)"

    match = _FRACTION.fullmatch(canonical)
    if match:
        sign, numerator, denominator = match.groups()
        return rf"\({sign}\frac{{{numerator}}}{{{denominator}}}\)"

    return canonical


def normalize_choice_displays(choices: Any) -> list[dict[str, str]]:
    """Normalize choices while separating canonical value and display text."""
    if not isinstance(choices, list):
        return []
    normalized: list[dict[str, str]] = []
    for index, item in enumerate(choices):
        if isinstance(item, dict):
            label = str(item.get("label") or item.get("key") or chr(ord("A") + index)).strip()
            canonical = str(item.get("value") or item.get("text") or "").strip()
            text = str(item.get("text") or canonical).strip()
            display = str(item.get("display") or format_choice_math_display(text)).strip()
        else:
            label = chr(ord("A") + index)
            canonical = str(item or "").strip()
            text = canonical
            display = format_choice_math_display(canonical)
        normalized.append(
            {
                "key": label,
                "label": label,
                "text": text,
                "value": canonical,
                "display": display,
            }
        )
    return normalized
