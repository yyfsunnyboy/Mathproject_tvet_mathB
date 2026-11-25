# -*- coding: utf-8 -*-
"""Minimal regressions for Round-3 UI + B2 sector multipart labels."""

from __future__ import annotations

import random
from pathlib import Path

from core.domain.trigonometry_angle_domain import _build_sector
from core.gencode.trigonometry_angle_payload import generate_trigonometry_angle_payload
from core.utils import format_vocational_b_section_display


ROOT = Path(__file__).resolve().parents[1]


def test_equal_slices_r15_n8_answers_and_labels():
    built = _build_sector(
        random.Random(0),
        {"variant": "equal_slices", "radius": 15, "slices": 8},
    )
    parts = (built.get("answer") or {}).get("parts") or {}
    labels = (built.get("answer") or {}).get("part_labels") or {}
    assert parts.get("part_1") == "225*pi/8"
    assert parts.get("part_2") == "15*pi/4"
    assert "面積" in str(labels.get("part_1") or "")
    assert "弧長" in str(labels.get("part_2") or "")


def test_sector_payload_exposes_student_facing_labels():
    payload = generate_trigonometry_angle_payload(
        skill_id="vh_數學B2_ArcLengthAndAreaOfSector",
        domain_operation="sector_arc_and_area",
        presentation_mode="short_answer",
        answer_type="multi_part",
        problem_type_id="sector_arc_and_area",
        textbook_example_id=11608,
        component_id="src_11608",
        seed=42,
        extra_constraints={"variant": "equal_slices", "radius": 15, "slices": 8},
    )
    contract_parts = ((payload.get("answer_contract") or {}).get("parts") or [])
    assert len(contract_parts) >= 2
    labels = [str(p.get("display_label") or p.get("label") or "") for p in contract_parts]
    joined = " ".join(labels)
    assert "part_1" not in joined
    assert "part_2" not in joined
    assert "面積" in joined
    assert "弧長" in joined
    # Payload answer may be dict parts or contract expected_answer fields.
    expected = {
        str(p.get("key")): str(p.get("expected_answer") or "")
        for p in contract_parts
        if isinstance(p, dict)
    }
    assert expected.get("part_1") == "225*pi/8"
    assert expected.get("part_2") == "15*pi/4"


def test_chapter_display_collapses_vector_spacing():
    assert "向 量" not in format_vocational_b_section_display("第3章 向 量", "")
    assert "向量" in format_vocational_b_section_display("第3章 向 量", "")


def test_similar_questions_route_title_is_utf8():
    source = (ROOT / "core" / "routes" / "practice.py").read_text(encoding="utf-8")
    assert "skill_ch_name='類題練習'" in source
    assert "憿?蝺渡?" not in source


def test_practice_page_has_math_chips_and_pen_color_attrs():
    source = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert 'data-insert="pi"' in source
    assert 'data-insert="sqrt("' in source
    assert 'data-insert="^2"' in source
    assert 'data-pen-color="blue"' in source
    assert 'data-pen-color="green"' in source
    assert "stale-question" in source


def test_skill_card_distinguishes_accuracy_and_type_mastery():
    card = (ROOT / "templates" / "partials" / "skill_card.html").read_text(encoding="utf-8")
    assert "最近正確率" in card
    assert "已掌握題型" in card
    assert "textbook_import" in card  # guard against path leakage
