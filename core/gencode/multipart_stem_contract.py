# -*- coding: utf-8 -*-
"""Shared multipart stem structure contract (generation → student render).

Subquestion boundaries are semantic data. They must not rely on whitespace
inside a flattened ``question_text`` string.
"""

from __future__ import annotations

import re
from typing import Any


def normalize_group_label(label: Any, *, index: int | None = None) -> str:
    """Canonical student-facing group marker: ``(1)``, ``(2)``, …"""
    text = str(label or "").strip()
    if text:
        m = re.fullmatch(r"[\(（]?\s*(\d+)\s*[\)）]?", text)
        if m:
            return f"({m.group(1)})"
        m = re.search(r"(\d+)", text)
        if m and not re.search(r"[\u4e00-\u9fffA-Za-z]", text):
            return f"({m.group(1)})"
    if index is not None and int(index) > 0:
        return f"({int(index)})"
    return text


def build_stem_structure(
    prompt: str,
    items: list[dict[str, Any]] | list[str],
) -> dict[str, Any]:
    """Build canonical multipart stem structure.

    ``items`` entries may be plain strings or dicts with optional
    ``group_label`` / ``text`` / ``math`` / ``body``.
    """
    prompt_text = str(prompt or "").strip()
    normalized_items: list[dict[str, str]] = []
    for idx, raw in enumerate(items or [], 1):
        if isinstance(raw, dict):
            group = normalize_group_label(
                raw.get("group_label") or raw.get("label") or raw.get("marker"),
                index=idx,
            )
            body = str(
                raw.get("text")
                or raw.get("math")
                or raw.get("body")
                or raw.get("content")
                or ""
            ).strip()
            # If body still starts with a duplicate marker, strip it.
            body = re.sub(r"^[\(（]\s*\d+\s*[\)）]\s*", "", body).strip()
        else:
            group = normalize_group_label(None, index=idx)
            body = str(raw or "").strip()
            body = re.sub(r"^[\(（]\s*\d+\s*[\)）]\s*", "", body).strip()
        if not body:
            continue
        normalized_items.append({"group_label": group, "text": body})
    return {
        "prompt": prompt_text,
        "items": normalized_items,
    }


def stem_structure_to_question_text(stem: dict[str, Any] | None) -> str:
    """Compatibility flat text with explicit newlines between items."""
    if not isinstance(stem, dict):
        return ""
    prompt = str(stem.get("prompt") or "").strip()
    lines: list[str] = []
    if prompt:
        lines.append(prompt)
    for item in stem.get("items") or []:
        if not isinstance(item, dict):
            continue
        group = normalize_group_label(item.get("group_label"))
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        lines.append(f"{group} {text}".strip() if group else text)
    return "\n".join(lines)


def extract_stem_structure(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    """Read stem structure from payload / matrix / metadata."""
    if not isinstance(payload, dict):
        return None
    for key in ("stem_structure", "question_stem", "multipart_stem"):
        raw = payload.get(key)
        if isinstance(raw, dict) and isinstance(raw.get("items"), list) and raw.get("items"):
            return build_stem_structure(str(raw.get("prompt") or ""), list(raw.get("items") or []))
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    for key in ("stem_structure", "question_stem", "multipart_stem"):
        raw = meta.get(key)
        if isinstance(raw, dict) and isinstance(raw.get("items"), list) and raw.get("items"):
            return build_stem_structure(str(raw.get("prompt") or ""), list(raw.get("items") or []))
    return None
