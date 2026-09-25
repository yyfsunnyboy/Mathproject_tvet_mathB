# -*- coding: utf-8 -*-
"""Generic single-choice contract builder for V3 generate payloads."""

from __future__ import annotations

import random
import re
from typing import Any

from core.gencode.choice_contract_validator import (
    MAX_SINGLE_CHOICE_COUNT,
    MIN_SINGLE_CHOICE_COUNT,
    VOCATIONAL_MC_CHOICE_COUNT,
    normalize_canonical_choices,
)

_TRAILING_PUNCT = re.compile(r"[。．.,，;；]+$")


def _clean_choice_text(text: str) -> str:
    return _TRAILING_PUNCT.sub("", str(text or "").strip())


def _normalize_source_choices(
    source_choices: list[Any],
    *,
    source_answer_label: str,
) -> tuple[list[dict[str, str]], str]:
    """Preserve textbook choice keys/text when source material is authoritative."""
    answer_key = str(source_answer_label or "").strip().strip("()[] .").upper()
    if not answer_key:
        raise ValueError("source_answer_label_required")

    choices: list[dict[str, str]] = []
    for index, item in enumerate(source_choices):
        if isinstance(item, dict):
            key = str(item.get("key") or item.get("label") or chr(ord("A") + index)).strip().upper()
            text = _clean_choice_text(str(item.get("text") or item.get("value") or ""))
        else:
            key = chr(ord("A") + index)
            text = _clean_choice_text(str(item))
        if not text:
            continue
        choices.append({"key": key, "label": key, "text": text, "value": text})

    if len(choices) < MIN_SINGLE_CHOICE_COUNT:
        raise ValueError("source_choices_incomplete")

    labels = {str(choice["key"]).upper() for choice in choices}
    if answer_key not in labels:
        raise ValueError("source_answer_not_in_choices")

    return choices[:MAX_SINGLE_CHOICE_COUNT], answer_key


def build_single_choice_contract(
    correct_answer: str,
    distractor_candidates: list[str] | None = None,
    *,
    source_choices: list[Any] | None = None,
    source_answer_label: str | None = None,
    seed: int | None = None,
    preserve_source_choices: bool = False,
    curriculum_profile: str | None = None,
) -> dict[str, Any]:
    """Build canonical single-choice payload fields.

    When ``preserve_source_choices`` is true and source material is present,
    textbook keys/text are kept. Otherwise distractors are synthesized from
  ``distractor_candidates`` around ``correct_answer`` (domain-owned values).
    """
    canonical = _clean_choice_text(correct_answer)
    choice_count = (VOCATIONAL_MC_CHOICE_COUNT if str(curriculum_profile or "").startswith("vocational") else MAX_SINGLE_CHOICE_COUNT)
    if preserve_source_choices and source_choices and source_answer_label:
        choices, correct_label = _normalize_source_choices(
            list(source_choices),
            source_answer_label=str(source_answer_label),
        )
        if choice_count == VOCATIONAL_MC_CHOICE_COUNT and len(choices) != choice_count:
            raise ValueError("source_choice_count_invalid")
        return {
            "choices": choices,
            "correct_label": correct_label,
            "correct_answer": correct_label,
            "canonical_answer": canonical,
            "checker_key": "choice_label_checker",
            "equivalence_type": "choice_label",
            "answer_type": "single_choice",
            "presentation_mode": "single_choice",
            "ui_contract": {"response_mode": "single_choice", "text_input_enabled": False},
        }

    if not canonical:
        raise ValueError("correct_answer_required")

    unique_wrong: list[str] = []
    from core.gencode.choice_contract_validator import choice_semantic_key

    seen = {choice_semantic_key(canonical)}
    for item in list(distractor_candidates or []):
        text = _clean_choice_text(str(item))
        key = choice_semantic_key(text)
        if not text or not key or key in seen:
            continue
        if re.search(r"_+\d+$", text):
            continue
        seen.add(key)
        unique_wrong.append(text)

    option_texts = [canonical] + unique_wrong
    if len(option_texts) < (choice_count if choice_count == VOCATIONAL_MC_CHOICE_COUNT else MIN_SINGLE_CHOICE_COUNT):
        raise ValueError("insufficient_distractor_candidates")

    option_texts = option_texts[:choice_count]
    rng = random.Random(int(seed) if seed is not None else sum(ord(ch) for ch in canonical))
    rng.shuffle(option_texts)

    choices: list[dict[str, str]] = []
    correct_label = "A"
    for index, text in enumerate(option_texts):
        label = chr(ord("A") + index)
        choices.append({"key": label, "label": label, "text": text, "value": text})
        if text == canonical:
            correct_label = label

    return {
        "choices": normalize_canonical_choices(choices),
        "correct_label": correct_label,
        "correct_answer": correct_label,
        "canonical_answer": canonical,
        "checker_key": "choice_label_checker",
        "equivalence_type": "choice_label",
        "answer_type": "single_choice",
        "presentation_mode": "single_choice",
        "ui_contract": {"response_mode": "single_choice", "text_input_enabled": False},
    }
