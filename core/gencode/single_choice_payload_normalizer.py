# -*- coding: utf-8 -*-
"""Normalize V3 single_choice payloads: separate stem from embedded A–D choices."""

from __future__ import annotations

from typing import Any

from core.gencode.v3_presentation_inference import (
    question_text_has_embedded_abcd_choices,
    split_question_stem_and_abcd_choices,
)


def normalize_single_choice_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Strip embedded A–D choices from question_text when canonical choices exist."""
    if not isinstance(payload, dict):
        return payload

    from core.gencode.choice_contract_validator import (
        normalize_canonical_choices,
        requires_choice_contract,
    )

    choices = normalize_canonical_choices(payload.get("choices"))
    is_single_choice = requires_choice_contract(payload) or (
        str(payload.get("interaction_type") or "").strip() == "single_choice" and bool(choices)
    )
    if not is_single_choice:
        return payload

    out = dict(payload)
    meta = dict(out.get("metadata") or {}) if isinstance(out.get("metadata"), dict) else {}

    question_text = str(out.get("question_text") or out.get("question") or "").strip()
    if not question_text:
        return out

    source_full = str(out.get("source_problem_text") or meta.get("source_problem_text") or "").strip()
    if not source_full and question_text_has_embedded_abcd_choices(question_text):
        source_full = question_text
        out["source_problem_text"] = source_full
        meta["source_problem_text"] = source_full

    if choices:
        if question_text_has_embedded_abcd_choices(question_text):
            stem, _, source = split_question_stem_and_abcd_choices(question_text)
            if stem:
                out["question_text"] = stem
                out["question"] = stem
            out.setdefault("source_problem_text", source)
            meta.setdefault("source_problem_text", source)
    elif question_text_has_embedded_abcd_choices(question_text):
        stem, parsed, source = split_question_stem_and_abcd_choices(question_text)
        if parsed:
            out["choices"] = parsed
            out["options"] = [str(c.get("text") or "") for c in parsed]
            out["question_text"] = stem
            out["question"] = stem
            out["source_problem_text"] = source
            meta["source_problem_text"] = source

    if meta:
        out["metadata"] = meta
    return out
