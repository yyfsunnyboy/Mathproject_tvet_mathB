# -*- coding: utf-8 -*-
"""Tests for textbook-driven V3 presentation inference."""

from __future__ import annotations

from core.gencode.v3_presentation_inference import (
    has_abcd_choice_group,
    infer_presentation_mode_from_textbook_row,
)


def _row(**kwargs: object) -> dict[str, object]:
    base = {
        "id": 1,
        "source_description": "",
        "source_section": "",
        "source_paragraph": "",
        "problem_type": "",
        "problem_text": "",
        "correct_answer": "",
    }
    base.update(kwargs)
    return base


def test_textbook_exercise_without_choices_is_short_answer():
    inferred = infer_presentation_mode_from_textbook_row(
        _row(
            problem_type="textbook_exercise",
            problem_text="試求通過 C(-4,3) 與 D(-4,6) 兩點之直線方程式。",
            source_description="2-2習題 基礎題 5",
        )
    )
    assert inferred["presentation_mode"] == "short_answer"
    assert inferred["answer_type"] == "expression"
    assert inferred["has_choices"] is False


def test_textbook_example_without_choices_is_short_answer():
    inferred = infer_presentation_mode_from_textbook_row(
        _row(
            problem_type="textbook_example",
            problem_text="(1) 求通過 A(0,-1) 與 B(4,-1) 的直線方程式。\n(2) 求通過 C(3,2) 與 D(3,-1) 的直線方程式。",
            source_description="例5",
        )
    )
    assert inferred["presentation_mode"] == "short_answer"
    assert inferred["has_choices"] is False


def test_in_class_practice_without_choices_is_short_answer():
    inferred = infer_presentation_mode_from_textbook_row(
        _row(
            problem_type="in_class_practice",
            problem_text="(1) 求通過 A(1,2) 與 B(1,5) 的直線方程式。",
            source_description="隨堂練習5",
        )
    )
    assert inferred["presentation_mode"] == "short_answer"


def test_self_assessment_with_abcd_choices_is_single_choice():
    inferred = infer_presentation_mode_from_textbook_row(
        _row(
            problem_type="self_assessment",
            problem_text=(
                "求通過兩點之直線方程式。\n"
                "(A) x = 1\n(B) y = 2\n(C) x + y = 3\n(D) x - y = 4"
            ),
            source_description="CH1自我評量 題10",
        )
    )
    assert inferred["presentation_mode"] == "single_choice"
    assert inferred["answer_type"] == "single_choice"
    assert inferred["has_choices"] is True


def test_subquestion_numbers_are_not_treated_as_choices():
    text = "(1) 求水平線\n(2) 求鉛直線"
    assert has_abcd_choice_group(text) is False
    inferred = infer_presentation_mode_from_textbook_row(
        _row(problem_type="textbook_example", problem_text=text)
    )
    assert inferred["presentation_mode"] == "short_answer"


def test_blank_correct_answer_does_not_force_single_choice():
    inferred = infer_presentation_mode_from_textbook_row(
        _row(
            problem_type="textbook_exercise",
            problem_text="試求通過兩點之直線方程式。",
            correct_answer="",
        )
    )
    assert inferred["presentation_mode"] == "short_answer"
