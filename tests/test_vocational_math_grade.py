# -*- coding: utf-8 -*-
"""Vocational Math B1–B4 grade mapping is volume-authoritative."""

import io

from werkzeug.datastructures import FileStorage

from core.textbook_importer_v3_orchestrate import build_curriculum_info_for_v3_import
from core.textbook_importer_v3_source import validate_textbook_source_batch
from core.textbook_processor import grade_for_vocational_math_volume
from core.textbook_processor_v2 import _resolve_outline_grade


def _make_file(filename: str, content: bytes = b"x") -> FileStorage:
    return FileStorage(
        stream=io.BytesIO(content),
        filename=filename,
        content_type="application/octet-stream",
    )


def test_grade_for_vocational_math_volume_b1_to_b4():
    assert grade_for_vocational_math_volume("數學B1") == 10
    assert grade_for_vocational_math_volume("數學B2") == 10
    assert grade_for_vocational_math_volume("數學B3") == 11
    assert grade_for_vocational_math_volume("數學B4") == 11
    assert grade_for_vocational_math_volume("數學 A1") is None


def test_resolve_outline_grade_volume_overrides_form():
    assert _resolve_outline_grade({"volume": "數學B2", "grade": 11}) == 10
    assert _resolve_outline_grade({"volume": "數學B1", "grade": 11}) == 10
    assert _resolve_outline_grade({"volume": "數學B3", "grade": 10}) == 11
    assert _resolve_outline_grade({"volume": "數學B4", "grade": 10}) == 11


def test_v3_curriculum_info_b2_ignores_form_grade_11(tmp_path):
    latex = tmp_path / "第一章 1-1 角度的基本性質-課本_Latex.docx"
    latex.write_bytes(b"x")
    info = build_curriculum_info_for_v3_import(
        latex_docx_path=latex,
        original_docx_filename="第一章 1-1 角度的基本性質-課本.docx",
        volume="數學B2",
        grade=11,
        apply_policy=False,
    )
    assert info["volume"] == "數學B2"
    assert info["grade"] == 10


def test_v3_source_batch_b2_overwrites_form_grade_11():
    payload, status = validate_textbook_source_batch(
        docx_files=[_make_file("第一章 1-1 角度的基本性質-課本.docx")],
        pdf_files=[_make_file("第一章 1-1 角度的基本性質-課本.pdf")],
        curriculum="vocational",
        publisher="longteng",
        grade=11,
        volume="數學B2",
    )
    assert status == 200
    assert payload["ok"] is True
    assert payload["batch"]["volume"] == "數學B2"
    assert payload["batch"]["grade"] == 10
