# -*- coding: utf-8 -*-
"""Regression tests for V3 CURRICULUM_BINDING authoritative chapter/section resolution."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app import create_app
from core.textbook_importer_v3_pipeline import (
    V3PipelineError,
    _fill_chapter_section_from_outline_or_lines,
    _resolve_catalog_chapter_title,
)


def _with_app_context(fn):
    app = create_app()
    with app.app_context():
        return fn()


@patch("core.textbook_processor_v2._lookup_outline_section_curriculum_row")
def test_section_textbook_filename_meta_resolves_chapter_section(mock_lookup):
    mock_lookup.return_value = None

    def run():
        info = {
            "curriculum": "vocational",
            "volume": "數學B2",
            "grade": 10,
            "source_scope": "section_textbook",
            "section_code": "1-2",
            "chapter_index": 1,
            "chapter_label": "第1章",
            "section_title": "1-2銳角三角函數",
            "filename_meta": {
                "chapter_index": 1,
                "chapter_label": "第1章",
                "section_code": "1-2",
                "section_index": 2,
                "section_title": "1-2銳角三角函數",
                "source_scope": "section_textbook",
            },
        }
        result = _fill_chapter_section_from_outline_or_lines(info, [])
        assert result["chapter"] == "第1章"
        assert result["section"] == "1-2銳角三角函數"
        assert result["section_code"] == "1-2"

    _with_app_context(run)


@patch("core.textbook_processor_v2._lookup_outline_section_curriculum_row")
def test_section_textbook_chapter_section_conflict_raises(mock_lookup):
    mock_lookup.return_value = None

    def run():
        info = {
            "curriculum": "vocational",
            "volume": "數學B2",
            "grade": 10,
            "source_scope": "section_textbook",
            "section_code": "2-3",
            "chapter_index": 1,
            "chapter_label": "第1章",
            "section_title": "2-3銳角三角函數",
            "filename_meta": {
                "chapter_index": 1,
                "section_code": "2-3",
                "section_index": 3,
                "section_title": "2-3銳角三角函數",
                "source_scope": "section_textbook",
            },
        }
        with pytest.raises(V3PipelineError) as exc_info:
            _fill_chapter_section_from_outline_or_lines(info, [])
        err = exc_info.value
        assert err.error_code == "authoritative_chapter_section_conflict"
        assert "1" in err.message
        assert "2-3" in err.message

    _with_app_context(run)


@patch("core.textbook_processor_v2._lookup_outline_section_curriculum_row")
def test_existing_chapter_not_overridden_by_filename_meta(mock_lookup):
    mock_lookup.return_value = None

    def run():
        info = {
            "curriculum": "vocational",
            "volume": "數學B2",
            "grade": 10,
            "source_scope": "section_textbook",
            "section_code": "1-2",
            "chapter": "1 三角函數",
            "chapter_index": 1,
            "chapter_label": "第1章",
            "section_title": "1-2銳角三角函數",
        }
        result = _fill_chapter_section_from_outline_or_lines(info, [])
        assert result["chapter"] == "1 三角函數"
        assert result["section"] == "1-2銳角三角函數"

    _with_app_context(run)


@patch("core.textbook_importer_v3_pipeline._resolve_catalog_chapter_title")
def test_chapter_self_assessment_allows_missing_document_section(mock_resolve):
    mock_resolve.return_value = "第2章 三角函數的應用"

    def run():
        info = {
            "curriculum": "vocational",
            "volume": "數學B2",
            "grade": 10,
            "source_scope": "chapter_self_assessment",
            "chapter_index": 2,
            "chapter_label": "第2章",
            "filename_meta": {
                "chapter_index": 2,
                "chapter_label": "第2章",
                "section_code": None,
                "source_scope": "chapter_self_assessment",
            },
        }
        result = _fill_chapter_section_from_outline_or_lines(info, [])
        assert result["chapter"] == "第2章 三角函數的應用"
        assert result.get("section") in ("", None)
        assert result.get("section_code") in ("", None)
        mock_resolve.assert_called()

    _with_app_context(run)


@patch("core.textbook_importer_v3_pipeline._resolve_catalog_chapter_title", return_value="")
@patch("core.textbook_importer_v3_pipeline._extract_chapter_title_from_lines", return_value="")
def test_chapter_self_assessment_fails_without_chapter(mock_lines, mock_resolve):
    def run():
        info = {
            "curriculum": "vocational",
            "volume": "數學B2",
            "grade": 10,
            "source_scope": "chapter_self_assessment",
            "chapter_index": None,
            "chapter_label": "",
            "filename_meta": {"source_scope": "chapter_self_assessment"},
        }
        result = _fill_chapter_section_from_outline_or_lines(info, [])
        assert not str(result.get("chapter") or "").strip()

    _with_app_context(run)


@patch("core.textbook_processor_v2._lookup_outline_section_curriculum_row")
def test_section_textbook_still_requires_section(mock_lookup):
    mock_lookup.return_value = None

    def run():
        info = {
            "curriculum": "vocational",
            "volume": "數學B2",
            "grade": 10,
            "source_scope": "section_textbook",
            "chapter": "第1章 角度",
            "section_code": "",
            "section": "",
            "filename_meta": {"source_scope": "section_textbook"},
        }
        result = _fill_chapter_section_from_outline_or_lines(info, [])
        assert result["chapter"] == "第1章 角度"
        assert not str(result.get("section") or "").strip()
        assert not str(result.get("section_code") or "").strip()

    _with_app_context(run)


def test_resolve_catalog_chapter_title_uses_identity_not_hardcode():
    row_a = MagicMock(chapter="第2章 三角函數的應用")
    row_b = MagicMock(chapter="第1章 角度")

    class _Query:
        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            return [row_b, row_a]

    with patch("models.SkillCurriculum") as mock_sc:
        mock_sc.query = _Query()
        title = _resolve_catalog_chapter_title(
            curriculum="vocational",
            volume="數學B2",
            chapter_index=2,
            chapter_label="第2章",
        )
    assert title == "第2章 三角函數的應用"
