# -*- coding: utf-8 -*-
"""Regression tests for V3 CURRICULUM_BINDING authoritative chapter/section resolution."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app import create_app
from core.textbook_importer_v3_pipeline import (
    V3PipelineError,
    _fill_chapter_section_from_outline_or_lines,
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
