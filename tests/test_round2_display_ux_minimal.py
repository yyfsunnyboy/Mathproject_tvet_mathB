# -*- coding: utf-8 -*-
"""Minimal regressions for B1/B2 round-2 display / UX fixes."""

from __future__ import annotations

import random
from pathlib import Path

from core.domain.polynomial_domain import _build_synthetic_division
from core.gencode.answer_format_hint import build_answer_format_suffix_for_stem
from core.gencode.answer_grading import grade_answer_for_current_question


ROOT = Path(__file__).resolve().parents[1]


def _multipart_current(*, parts: list[dict], correct: dict) -> dict:
    return {
        "skill": "vh_test_round2",
        "skill_id": "vh_test_round2",
        "question_text": "試題",
        "answer_type": "multi_part",
        "correct_answer": correct,
        "answer_contract": {
            "answer_type": "multi_part",
            "answer_shape": "multi_part",
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "canonical_answer": correct,
            "parts": parts,
        },
    }


def test_synthetic_division_exposes_quotient_remainder_labels():
    built = _build_synthetic_division(random.Random(7))
    labels = (built.get("answer") or {}).get("part_labels") or {}
    assert labels
    assert any("商式" in str(v) for v in labels.values())
    assert any("餘式" in str(v) for v in labels.values())
    assert any("g(x)" in str(v) for v in labels.values())


def test_blank_multipart_message_uses_submit_and_ai_check_labels():
    current = _multipart_current(
        parts=[
            {"key": "part_1", "display_label": "商式"},
            {"key": "part_2", "display_label": "餘式"},
        ],
        correct={"part_1": "x+1", "part_2": "2"},
    )
    result = grade_answer_for_current_question(
        {"part_1": "", "part_2": ""}, current, current["skill_id"]
    )
    assert result is not None
    msg = str(result.get("result") or result.get("message") or "")
    assert "提交" in msg
    assert "AI檢查" in msg
    assert "送出答案" not in msg
    assert "AI 檢查" not in msg


def test_single_part_wrong_avoids_multipart_error_template():
    current = _multipart_current(
        parts=[{"key": "part_1", "display_label": "k"}],
        correct={"part_1": "3"},
    )
    result = grade_answer_for_current_question({"part_1": "9"}, current, current["skill_id"])
    assert result is not None
    msg = str(result.get("result") or "")
    assert "部分小題" not in msg


def test_stem_asking_k_suppresses_or_aligns_x_format_example():
    suffix, reason = build_answer_format_suffix_for_stem(
        {
            "checker": "structured_text_checker",
            "answer_format_example": "x=3",
        },
        "若方程式有解，則 k =",
    )
    assert suffix == ""
    assert reason in {"stem_fill_in_cue", "stem_states_answer_format"}


def test_practice_page_keeps_tutor_markdown_and_handwriting_blank_guards():
    source = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert "stripTutorMarkdownFences" in source
    assert "白板上的答案還無法對應到每一個填空" in source
    assert "dataset.hadInitial" in source


def test_skill_card_renderer_keeps_fraction_overflow_visible():
    renderer = (ROOT / "templates/partials/skill_card_math_renderer.html").read_text(
        encoding="utf-8"
    )
    assert "overflow-y: visible" in renderer
