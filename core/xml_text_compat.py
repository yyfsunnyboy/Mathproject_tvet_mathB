# -*- coding: utf-8 -*-
"""XML 1.0 string compatibility helpers for serialization boundaries.

Used when assigning Python strings into XML writers (lxml / OOXML).
Does NOT rewrite textbook semantics; only strips characters illegal in XML 1.0.
Private Use Area code points (e.g. MathType U+EF01) are XML-legal and kept.
"""

from __future__ import annotations

from typing import Any


def is_xml_1_0_char(codepoint: int) -> bool:
    """Return True if codepoint is allowed by XML 1.0 Char production."""
    if codepoint in (0x9, 0xA, 0xD):
        return True
    if 0x20 <= codepoint <= 0xD7FF:
        return True
    if 0xE000 <= codepoint <= 0xFFFD:
        return True
    if 0x10000 <= codepoint <= 0x10FFFF:
        return True
    return False


def find_illegal_xml_characters(text: str) -> list[dict[str, Any]]:
    """Return illegal XML 1.0 characters with escaped diagnostics (safe for logs)."""
    if not isinstance(text, str) or not text:
        return []
    hits: list[dict[str, Any]] = []
    for index, ch in enumerate(text):
        cp = ord(ch)
        if is_xml_1_0_char(cp):
            continue
        hits.append(
            {
                "index": index,
                "repr": repr(ch),
                "codepoint": f"U+{cp:04X}",
            }
        )
    return hits


def sanitize_xml_text(value: Any) -> Any:
    """Strip XML 1.0-illegal characters from strings; leave non-str values unchanged."""
    if not isinstance(value, str):
        return value
    if not value:
        return value
    if not find_illegal_xml_characters(value):
        return value
    return "".join(ch for ch in value if is_xml_1_0_char(ord(ch)))


def describe_illegal_xml_text(
    text: str,
    *,
    field: str = "",
    source: str = "",
    record_index: Any = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Build a log-safe diagnostic payload; None when text is XML-legal."""
    if not isinstance(text, str):
        return None
    illegal = find_illegal_xml_characters(text)
    if not illegal:
        return None
    payload: dict[str, Any] = {
        "field": field,
        "source": source,
        "record_index": record_index,
        "text_repr": repr(text),
        "illegal_chars": illegal,
    }
    if extra:
        payload.update(extra)
    return payload
