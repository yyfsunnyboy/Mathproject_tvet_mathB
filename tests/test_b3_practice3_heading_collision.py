# -*- coding: utf-8 -*-
"""Regression: practice-zone heading fragment must not steal 隨堂練習N."""

from __future__ import annotations

from core.textbook_processor_v2 import (
    _looks_like_practice_question_body,
    _practice_body_is_heading_fragment,
    _problem_texts_compatible_for_missing_skip,
    phase2_deterministic_block_slice,
)


def test_heading_fragment_rejected_as_practice_body():
    assert _practice_body_is_heading_fragment("數列的相加—級數")
    assert not _looks_like_practice_question_body("數列的相加—級數")


def test_real_practice_stem_accepted():
    body = (
        r"已知一等差數列\(\left \langle { a_{ n } } \right \rangle\)中，"
        r"\(a_{ 3 } =-2\)，\(a_{ 8 } =-17\)，試求："
        r"\n(1)公差d。 (2)\(a_{ 15 }\)之值。"
    )
    assert not _practice_body_is_heading_fragment(body)
    assert _looks_like_practice_question_body(body)


def test_missing_skip_rejects_heading_vs_real_collision():
    assert not _problem_texts_compatible_for_missing_skip(
        "數列的相加—級數",
        r"已知一等差數列中，\(a_{ 3 } =-2\)，\(a_{ 8 } =-17\)，試求公差d與\(a_{ 15 }\)。",
    )
    assert _problem_texts_compatible_for_missing_skip(
        r"已知一等差數列中，\(a_{ 3 } =-2\)，試求公差。",
        r"已知一等差數列中，\(a_{ 3 } =-2\)，試求公差。",
    )


def test_practice_zone_does_not_keep_heading_as_suitang3():
    lines = [
        "例1",
        "試寫出下列各數列的前3項：",
        "隨堂練習………………………………………………………………………………",
        "__NEW_QUESTION_TRIGGER__ 1. 試寫出下列各數列的前4項：",
        "觀察一數列的規律……",
        "__NEW_QUESTION_TRIGGER__ 3. 數列的相加—級數",
        "當我們把一個數列的每一項用加號連接起來，就稱為級數。",
        "__NEW_QUESTION_TRIGGER__ 1-1.2 等差數列",
        "例3",
        "棒球投手桃太郎從4月1日開始自主訓練。",
        "隨堂練習………………………………………………………………………………",
        (
            "__NEW_QUESTION_TRIGGER__ 3. 已知一等差數列"
            r"\(\left \langle { a_{ n } } \right \rangle\)中，"
            r"\(a_{ 3 } =-2\)，\(a_{ 8 } =-17\)，試求："
            r"\n(1)公差d。 (2)\(a_{ 15 }\)之值。"
        ),
        "例4",
    ]
    blocks = phase2_deterministic_block_slice(
        lines,
        curriculum_info={
            "curriculum": "vocational",
            "volume": "數學B3",
            "grade": 11,
            "section_code": "1-1",
            "chapter": "第1章 數列與級數",
            "section": "1-1 等差數列與等差級數",
            "source_scope": "section_textbook",
        },
        read_only=True,
    )
    assert "隨堂練習3" in blocks
    assert "-17" in blocks["隨堂練習3"]
    assert "a_{ 3 }" in blocks["隨堂練習3"] or "a_{3}" in blocks["隨堂練習3"]
    assert "數列的相加" not in blocks["隨堂練習3"]
    assert "隨堂練習1" in blocks
