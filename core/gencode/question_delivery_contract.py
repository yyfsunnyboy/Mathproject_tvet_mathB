# -*- coding: utf-8 -*-
"""Shared question delivery contract for practice runtime payloads.

``question_text`` is the canonical stem field. Supported legacy aliases are folded into it
at the shared normalization boundary, and a payload whose canonical stem is still missing
or blank must never be delivered to a student.
"""

from __future__ import annotations

from typing import Any

from core.gencode.multipart_stem_contract import extract_stem_structure, stem_structure_to_question_text

QUESTION_TEXT_FIELD = "question_text"
LEGACY_QUESTION_TEXT_ALIASES = ("new_question_text", "question", "problem_text", "prompt")


def _is_non_blank_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def canonicalize_question_text(payload: Any) -> Any:
    """Return a copy whose ``question_text`` is filled from a supported alias when blank.

    Priority: existing non-blank ``question_text`` > legacy string aliases > flattened
    multipart ``stem_structure``. Payloads without any usable stem are returned unchanged
    so that :func:`question_delivery_errors` can reject them.
    """
    if not isinstance(payload, dict) or _is_non_blank_str(payload.get(QUESTION_TEXT_FIELD)):
        return payload
    out = dict(payload)
    for key in LEGACY_QUESTION_TEXT_ALIASES:
        if _is_non_blank_str(out.get(key)):
            out[QUESTION_TEXT_FIELD] = out[key]
            return out
    flattened = stem_structure_to_question_text(extract_stem_structure(out))
    if _is_non_blank_str(flattened):
        out[QUESTION_TEXT_FIELD] = flattened
    return out


def question_delivery_errors(payload: Any) -> list[str]:
    """Fail-closed delivery gate: empty list means the payload may be shown to a student."""
    if not isinstance(payload, dict):
        return ["payload_not_dict"]
    if QUESTION_TEXT_FIELD not in payload:
        return ["question_text_missing"]
    value = payload.get(QUESTION_TEXT_FIELD)
    if not isinstance(value, str):
        return ["question_text_not_str"]
    if not value.strip():
        return ["question_text_blank"]
    return []
