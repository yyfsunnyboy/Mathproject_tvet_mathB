# -*- coding: utf-8 -*-
"""Math B 章節座標：不得將整本 B1 強制寫成第 1 章。"""

from unittest.mock import MagicMock

import pytest

from core.textbook_processor_v2 import (
    MATHB1_CHAPTER1_CANONICAL_TITLE,
    _canonical_db_chapter_from_row,
    _canonical_outline_chapter_title,
    _ensure_formal_skill_info_and_curriculum_v2,
    _force_mathb_chapter_title_if_section_matches,
    _is_chapter_self_assessment_import,
)


class _FakeOutlineRow:
    def __init__(self, chapter: str, section: str):
        self.chapter = chapter
        self.section = section
        self.skill_id = "outline_vocational_數學B1_21"
        self.curriculum = "vocational"
        self.volume = "數學B1"
        self.grade = 10
        self.display_order = 1
        self.id = 1


def test_canonical_db_chapter_from_row_chapter2_not_forced_to_chapter1():
    row = _FakeOutlineRow("2 直線方程式", "2-1 斜率")
    info = {"curriculum": "vocational", "volume": "數學B1", "grade": 10}
    assert _canonical_db_chapter_from_row(row, info) == "2 直線方程式"  # type: ignore[arg-type]


def test_force_mathb_chapter_title_section21_returns_chapter2():
    assert (
        _force_mathb_chapter_title_if_section_matches(
            "2 直線方程式",
            "2-1",
        )
        == "2 直線方程式"
    )
    assert (
        _force_mathb_chapter_title_if_section_matches(
            "第2章 直線方程式",
            "2-1",
        )
        == "2 直線方程式"
    )


def test_force_mathb_chapter_title_section11_can_normalize_chapter1():
    assert (
        _force_mathb_chapter_title_if_section_matches(
            "第1章 坐標系與函數圖形",
            "1-1",
        )
        == MATHB1_CHAPTER1_CANONICAL_TITLE
    )


def test_canonical_outline_chapter_title_chapter2_unchanged():
    info = {"curriculum": "vocational", "grade": 10, "volume": "數學B1"}
    assert _canonical_outline_chapter_title("第2章 直線方程式", info) == "2 直線方程式"


def test_ensure_formal_skill_curriculum_chapter2(monkeypatch):
    from contextlib import nullcontext

    curriculum_rows: list[dict] = []

    def _capture_curriculum_init(self, **kwargs):
        curriculum_rows.append(kwargs)
        self.__dict__.update(kwargs)

    curriculum_chain = MagicMock()
    curriculum_chain.filter_by.return_value = curriculum_chain
    curriculum_chain.order_by.return_value = curriculum_chain
    curriculum_chain.first.return_value = None

    sc_id = MagicMock()
    sc_id.asc.return_value = MagicMock()

    mock_session = MagicMock()
    mock_session.get.return_value = None
    mock_session.no_autoflush = nullcontext()

    monkeypatch.setattr("core.textbook_processor_v2.db.session", mock_session)
    monkeypatch.setattr(
        "core.textbook_processor_v2.SkillCurriculum",
        type(
            "SC",
            (),
            {
                "query": curriculum_chain,
                "id": sc_id,
                "__init__": _capture_curriculum_init,
            },
        ),
    )
    monkeypatch.setattr(
        "core.textbook_processor_v2.SkillInfo",
        type(
            "SI",
            (),
            {
                "__init__": lambda self, **kwargs: self.__dict__.update(kwargs),
            },
        ),
    )

    row = _ensure_formal_skill_info_and_curriculum_v2(
        formal_skill_id="vh_數學B1_SlopeOfALine",
        concept_name="直線的斜率",
        concept_en_id="SlopeOfALine",
        curriculum="vocational",
        grade=10,
        volume="數學B1",
        chapter_title="2 直線方程式",
        section_title="2-1 斜率",
        section_code="2-1",
        concept_code="2-1.1",
    )
    assert curriculum_rows
    assert curriculum_rows[0]["chapter"] == "2 直線方程式"
    assert curriculum_rows[0]["section"] == "2-1 斜率"
    assert row.chapter == "2 直線方程式"
    assert row.section == "2-1 斜率"


def test_chapter1_section11_still_canonical():
    assert (
        _force_mathb_chapter_title_if_section_matches(
            "第一章 坐標系與函數圖形",
            "1-1",
        )
        == MATHB1_CHAPTER1_CANONICAL_TITLE
    )


def test_self_assessment_import_detection_unchanged():
    assert _is_chapter_self_assessment_import("第1章 自我評量", {}) is True
