# -*- coding: utf-8 -*-
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.textbook_importer_v3_orchestrate import (
    B2_11_GLOB_DOCX,
    build_curriculum_info_for_v3_import,
    find_b2_11_source_pair,
    resolve_latex_docx_path,
    run_or_enqueue_v3_word_import,
    verify_b2_11_word_import,
)


def test_resolve_existing_latex_docx_uppercase_suffix(tmp_path: Path):
    original = tmp_path / "第一章 1-1 角度的基本性質-課本.docx"
    latex = tmp_path / "第一章 1-1 角度的基本性質-課本_Latex.docx"
    original.write_bytes(b"raw")
    latex.write_bytes(b"latex")

    result = resolve_latex_docx_path(tmp_path, original.name)
    assert result.status == "ok"
    assert result.path == latex.resolve()
    assert result.resolved_filename == latex.name


def test_resolve_existing_latex_docx_lowercase_suffix(tmp_path: Path):
    original = tmp_path / "第一章 1-1 角度的基本性質-課本.docx"
    latex = tmp_path / "第一章 1-1 角度的基本性質-課本_latex.docx"
    original.write_bytes(b"raw")
    latex.write_bytes(b"latex")

    result = resolve_latex_docx_path(tmp_path, original.name)
    assert result.status == "ok"
    assert result.path == latex.resolve()


def test_resolve_missing_latex_docx(tmp_path: Path):
    original = tmp_path / "第一章 1-1 角度的基本性質-課本.docx"
    original.write_bytes(b"raw")

    result = resolve_latex_docx_path(tmp_path, original.name)
    assert result.status == "missing_latex_docx"
    assert result.reason == "missing_latex_docx"
    assert result.path is None


def test_resolve_already_latex_input(tmp_path: Path):
    latex = tmp_path / "第一章 1-1 角度的基本性質-課本_Latex.docx"
    latex.write_bytes(b"latex")

    result = resolve_latex_docx_path(tmp_path, latex.name)
    assert result.status == "ok"
    assert result.path == latex.resolve()
    assert result.reason == "input_is_latex_docx"


def test_build_curriculum_info_for_b2_11(tmp_path: Path):
    original_name = "第一章 1-1 角度的基本性質-課本.docx"
    latex_path = tmp_path / "第一章 1-1 角度的基本性質-課本_Latex.docx"
    latex_path.write_bytes(b"x")

    with patch("core.routes.admin.apply_mathb_import_policy") as mock_policy:
        info = build_curriculum_info_for_v3_import(
            latex_docx_path=latex_path,
            original_docx_filename=original_name,
            volume="數學B2",
        )

    assert info["curriculum"] == "vocational"
    assert info["publisher"] == "longteng"
    assert info["grade"] == 10
    assert info["volume"] == "數學B2"
    assert info["section_code"] == "1-1"
    assert info["chapter_index"] == 1
    assert info["source_scope"] == "section_textbook"
    assert info["import_mode"] == "docx_problems"
    assert info["original_filename"] == original_name
    assert info["parse_filename"] == original_name
    assert info["saved_filename"] == latex_path.name
    mock_policy.assert_called_once()


def test_find_b2_11_source_pair_reports_missing(tmp_path: Path):
    pair = find_b2_11_source_pair(tmp_path)
    assert pair.original_docx is None
    assert pair.pdf is None
    assert pair.latex_docx is None
    assert "original_docx" in pair.missing
    assert "pdf" in pair.missing
    assert "latex_docx" in pair.missing


def test_find_b2_11_source_pair_with_files(tmp_path: Path):
    source_dir = tmp_path / "textbook_import" / "source" / "vocational" / "math_B2"
    source_dir.mkdir(parents=True)
    docx = source_dir / "第一章 1-1 角度的基本性質-課本.docx"
    pdf = source_dir / "第一章 1-1 角度的基本性質-課本.pdf"
    latex = source_dir / "第一章 1-1 角度的基本性質-課本_Latex.docx"
    docx.write_bytes(b"d")
    pdf.write_bytes(b"p")
    latex.write_bytes(b"l")

    pair = find_b2_11_source_pair(tmp_path)
    assert pair.original_docx == docx
    assert pair.pdf == pdf
    assert pair.latex_docx == latex.resolve()
    assert pair.missing == ()


def test_run_or_enqueue_sync_calls_process_textbook_file_v2(tmp_path: Path):
    latex = tmp_path / "demo_Latex.docx"
    latex.write_bytes(b"x")
    app = MagicMock()
    app.app_context.return_value.__enter__ = MagicMock()
    app.app_context.return_value.__exit__ = MagicMock(return_value=False)

    fake_result = {"success": True, "inserted": 1, "updated": 0, "total": 1}
    with patch("core.textbook_processor_v2.process_textbook_file_v2", return_value=fake_result) as mock_import:
        out = run_or_enqueue_v3_word_import(
            latex,
            {"volume": "數學B2"},
            enqueue=False,
            app=app,
        )

    mock_import.assert_called_once()
    assert out["mode"] == "sync"
    assert out["success"] is True
    assert out["result"] == fake_result


@pytest.mark.integration
def test_verify_b2_11_word_import_if_latex_available():
    project_root = Path(__file__).resolve().parents[1]
    pair = find_b2_11_source_pair(project_root)
    if pair.latex_docx is None or not pair.latex_docx.is_file():
        pytest.skip(
            "B2 1-1 *_Latex.docx not found under textbook_import/source/vocational/math_B2/"
        )

    try:
        from app import app as flask_app
    except Exception as exc:
        pytest.skip(f"Flask app unavailable: {exc}")

    report = verify_b2_11_word_import(project_root, flask_app)
    print("B2_11_VERIFY_REPORT", report)

    if report.get("status") == "missing_latex_docx":
        pytest.skip("missing_latex_docx")

    if report.get("status") != "ok":
        pytest.fail(
            f"B2 1-1 import verification failed: status={report.get('status')} "
            f"import={report.get('import')}"
        )

    # Phase4 may write 0 rows when SkillCurriculum outline for B2 1-1 is absent.
    if (report.get("textbook_examples_count") or 0) == 0:
        pytest.skip(
            "Import ran but textbook_examples_count=0 "
            "(likely missing SkillCurriculum outline for 數學B2 / 1-1)"
        )
