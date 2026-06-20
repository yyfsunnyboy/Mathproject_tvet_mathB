# -*- coding: utf-8 -*-
"""Tests for V3 example source construction and hashing."""

from __future__ import annotations

import pytest
from core.gencode.services.v3_example_semantic_classifier import (
    TextbookExampleSource,
    calculate_source_hash,
    parse_choices_from_text,
)


def test_calculate_source_hash_different():
    h1 = calculate_source_hash("Question 1", "Answer 1", "Sol 1")
    h2 = calculate_source_hash("Question 2", "Answer 1", "Sol 1")
    h3 = calculate_source_hash("Question 1", "Answer 2", "Sol 1")
    h4 = calculate_source_hash("Question 1", "Answer 1", "Sol 2")

    assert h1 != h2
    assert h1 != h3
    assert h1 != h4
    assert len(h1) == 32


def test_parse_choices_from_text():
    text = "Find slope: (A) 1 (B) 2 (C) 3 (D) 4"
    choices = parse_choices_from_text(text)
    assert choices == ["1", "2", "3", "4"]

    text_no_choices = "Find slope: 3x + 2y = 0"
    choices_none = parse_choices_from_text(text_no_choices)
    assert choices_none == []


def test_source_payload_creation():
    src = TextbookExampleSource(
        skill_id="test_skill",
        textbook_example_id=123,
        question_text="Find slope L: 3x - 2y + 1 = 0",
        answer="3/2",
        choices=[],
        explanation="Slope is -A/B",
        source_label="Ex 1",
        source_type="general",
        presentation_mode="short_answer",
        question_type="general",
        source_hash=calculate_source_hash("Find slope L: 3x - 2y + 1 = 0", "3/2", "Slope is -A/B"),
    )
    assert src.skill_id == "test_skill"
    assert src.textbook_example_id == 123
    assert src.question_text == "Find slope L: 3x - 2y + 1 = 0"
    assert src.answer == "3/2"
    assert src.source_hash is not None
