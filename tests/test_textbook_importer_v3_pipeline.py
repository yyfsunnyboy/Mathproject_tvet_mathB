# -*- coding: utf-8 -*-
"""V3 full orchestration pipeline tests (mocked Gemini / Phase4 as needed)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.textbook_importer_v3_pipeline import (
    STAGE_AI_ALIGNMENT,
    STAGE_DB_WRITE,
    STAGE_FORMULA_CONVERSION,
    STAGE_PDF_VISUAL,
    STAGE_IMAGE_LINKING,
    build_v3_ui_result_payload,
    ensure_db_backup,
    run_v3_pair_pipeline,
)


def _minimal_docx_bytes() -> bytes:
    return b"PK\x03\x04fake"


@pytest.fixture
def pair_paths(tmp_path: Path):
    docx = tmp_path / "第一章 1-1 角度的基本性質-課本.docx"
    pdf = tmp_path / "第一章 1-1 角度的基本性質-課本.pdf"
    docx.write_bytes(_minimal_docx_bytes())
    pdf.write_bytes(b"%PDF-1.4")
    return docx, pdf


def _mock_app():
    app = MagicMock()
    ctx = MagicMock()
    app.app_context.return_value = ctx
    ctx.__enter__ = MagicMock(return_value=None)
    ctx.__exit__ = MagicMock(return_value=False)
    return app


def test_ui_result_marks_pdf_visual_null_and_counts():
    batch = {
        "task_id": "t1",
        "pairs": [
            {
                "ok": True,
                "base_name": "demo",
                "metrics": {
                    "word_scan": {"word_tables": 14, "table_cells": 71},
                    "formula_conversion": {
                        "mathtype_found": 10,
                        "mathtype_converted": 9,
                        "formula_failures": 1,
                        "eq_fields": 2,
                    },
                    "question_parse": {"phase2_blocks": 19},
                    "curriculum_binding": {
                        "concepts_found": 4,
                        "formal_skills_created": 0,
                        "formal_skills_reused": 4,
                    },
                    "ai_alignment": {"gemini_requests": 3, "gemini_total_tokens": 100},
                    "anchor": {"collision_count": 0},
                    "db_write": {"inserted": 19, "updated": 0},
                },
            }
        ],
    }
    ui = build_v3_ui_result_payload(batch)
    assert ui["status"] == "success"
    assert ui["contentParsing"]["mathTypeFound"] == 10
    assert ui["contentParsing"]["formulaFailures"] == 1
    assert ui["questions"]["parsed"] == 19
    assert ui["questions"]["formalSkillsReused"] == 4
    assert ui["images"]["pdfVisualAssets"] == 0
    assert ui["images"]["linked"] == 0
    assert ui["database"]["questionsWritten"] == 19


def test_ensure_db_backup_copies_file(tmp_path: Path):
    inst = tmp_path / "instance"
    inst.mkdir()
    db = inst / "kumon_math.db"
    db.write_bytes(b"sqlite")
    info = ensure_db_backup(project_root=tmp_path, label="unit_test")
    assert Path(info["backup_path"]).is_file()
    assert Path(info["backup_path"]).read_bytes() == b"sqlite"


def test_pipeline_gemini_failure_skips_db_write(pair_paths, tmp_path: Path):
    docx, pdf = pair_paths
    latex = docx.with_name(docx.stem + "_Latex.docx")
    app = _mock_app()

    def fake_convert(src, out=None):
        dest = Path(out) if out else latex
        dest.write_bytes(b"latex")
        return {
            "mathtype_ole": 1,
            "converted_ok": 1,
            "converted_failed": 0,
            "eq_fields": 0,
            "eq_converted_ok": 0,
            "original_unchanged": True,
            "output": str(dest),
        }

    fake_blocks = {"例1": "題幹"}
    fake_meta = {
        "例1": {
            "anchor": "例1",
            "source_type": "textbook_example",
            "problem_text": "題幹",
            "concept_code": "1-1.1",
            "concept_name": "有向角",
            "concept_en_id": "DirectedAngle",
            "formal_skill_id": "vh_數學B2_DirectedAngle",
            "section_code": "1-1",
        }
    }
    curriculum_info = {
        "curriculum": "vocational",
        "volume": "數學B2",
        "section_code": "1-1",
        "chapter": "1 三角函數",
        "section": "1-1 角度的基本性質",
        "grade": 10,
        "source_scope": "section_textbook",
        "parse_filename": docx.name,
        "original_filename": docx.name,
        "saved_filename": latex.name,
        "publisher": "longteng",
    }

    with patch(
        "core.textbook_importer_v3_pipeline.parse_docx_summary",
        return_value={
            "summary": {
                "tables": 1,
                "table_cells": 2,
                "mathtype_ole": 1,
                "eq_fields": 0,
                "independent_images": 0,
            }
        },
    ), patch(
        "core.textbook_importer_v3_pipeline.convert_docx_mathtype_to_latex_docx",
        side_effect=fake_convert,
    ), patch(
        "core.textbook_importer_v3_pipeline.build_curriculum_info_for_v3_import",
        return_value=dict(curriculum_info),
    ), patch("core.textbook_processor_v2.phase1_extract_docx_lines", return_value=["l1"]    ), patch(
        "core.textbook_processor_v2._resolve_import_source_metadata",
        return_value={
            "curriculum_info": dict(curriculum_info),
            "source_scope": "section_textbook",
        },
    ), patch(
        "core.textbook_importer_v3_pipeline._fill_chapter_section_from_outline_or_lines",
        side_effect=lambda info, lines: dict(info),
    ), patch(
        "core.textbook_section_outline.ensure_section_outline_from_authoritative_metadata_v2",
        return_value={
            "action": "existing",
            "skill_id": "outline_vocational_數學B2_11",
            "chapter": "1 三角函數",
            "section": "1-1 角度的基本性質",
        },
    ), patch(
        "core.textbook_processor_v2.phase2_deterministic_block_slice",
        return_value=fake_blocks,
    ), patch(
        "core.textbook_processor_v2._DOCX_BLOCK_META",
        fake_meta,
    ), patch(
        "core.textbook_importer_v3_pipeline._ensure_formal_concepts_for_headings",
        return_value=[
            {
                "action": "existing",
                "skill_id": "vh_數學B2_DirectedAngle",
                "concept_name": "有向角",
            }
        ],
    ), patch(
        "core.textbook_formal_concept.get_section_formal_skill_candidates",
        return_value=[{"skill_id": "vh_數學B2_DirectedAngle"}],
    ), patch("core.ai_analyzer.get_model", return_value=MagicMock()), patch(
        "core.textbook_processor_v2.phase3_ai_metadata_alignment",
        side_effect=RuntimeError("gemini down"),
    ), patch(
        "core.textbook_processor_v2.phase4_absolute_hydrate_and_save"
    ) as mock_phase4, patch("models.db") as mock_db:
        mock_db.session.commit = MagicMock()
        mock_db.session.rollback = MagicMock()
        report = run_v3_pair_pipeline(
            project_root=tmp_path,
            docx_path=docx,
            pdf_path=pdf,
            curriculum="vocational",
            volume="數學B2",
            allow_phase4=True,
            emit_stream_end=False,
            app=app,
        )

    assert report["ok"] is False
    assert report["error"]["stage"] == STAGE_AI_ALIGNMENT
    assert report["error"]["error_code"] == "gemini_api_error"
    mock_phase4.assert_not_called()


def test_pipeline_happy_path_calls_phase4_and_pdf_visual(pair_paths, tmp_path: Path):
    docx, pdf = pair_paths
    latex = docx.with_name(docx.stem + "_Latex.docx")
    app = _mock_app()

    def fake_convert(src, out=None):
        dest = Path(out) if out else latex
        dest.write_bytes(b"latex")
        return {
            "mathtype_ole": 2,
            "converted_ok": 2,
            "converted_failed": 0,
            "eq_fields": 1,
            "eq_converted_ok": 1,
            "original_unchanged": True,
            "output": str(dest),
        }

    fake_blocks = {"例1": "題幹"}
    fake_meta = {
        "例1": {
            "anchor": "例1",
            "source_type": "textbook_example",
            "problem_text": "題幹",
            "concept_code": "1-1.1",
            "concept_name": "有向角",
            "concept_en_id": "DirectedAngle",
            "formal_skill_id": "vh_數學B2_DirectedAngle",
            "section_code": "1-1",
        }
    }
    phase3 = {
        "chapters": [
            {
                "chapter_title": "1 三角函數",
                "sections": [
                    {
                        "section_code": "1-1",
                        "section_title": "1-1 角度的基本性質",
                        "concepts": [
                            {
                                "concept_name": "有向角",
                                "examples": [{"title": "例1", "correct_answer": ""}],
                                "practice_questions": [],
                            }
                        ],
                    }
                ],
            }
        ]
    }
    curriculum_info = {
        "curriculum": "vocational",
        "volume": "數學B2",
        "section_code": "1-1",
        "chapter": "1 三角函數",
        "section": "1-1 角度的基本性質",
        "grade": 10,
        "source_scope": "section_textbook",
        "parse_filename": docx.name,
        "publisher": "longteng",
    }

    te_query = MagicMock()
    te_query.filter_by.return_value.count.return_value = 0
    te_query.filter_by.return_value.all.return_value = []
    te_query.count.return_value = 100

    with patch(
        "core.textbook_importer_v3_pipeline.parse_docx_summary",
        return_value={
            "summary": {
                "tables": 1,
                "table_cells": 2,
                "mathtype_ole": 2,
                "eq_fields": 1,
                "independent_images": 0,
            }
        },
    ), patch(
        "core.textbook_importer_v3_pipeline.convert_docx_mathtype_to_latex_docx",
        side_effect=fake_convert,
    ), patch(
        "core.textbook_importer_v3_pipeline.build_curriculum_info_for_v3_import",
        return_value=dict(curriculum_info),
    ), patch(
        "core.textbook_processor_v2.phase1_extract_docx_lines",
        return_value=["1 三角函數", "l2"],
    ), patch(
        "core.textbook_processor_v2._resolve_import_source_metadata",
        side_effect=lambda **kw: {
            "curriculum_info": kw["curriculum_info"],
            "source_scope": "section_textbook",
        },
    ), patch(
        "core.textbook_importer_v3_pipeline._fill_chapter_section_from_outline_or_lines",
        side_effect=lambda info, lines: dict(info),
    ), patch(
        "core.textbook_section_outline.ensure_section_outline_from_authoritative_metadata_v2",
        return_value={
            "action": "existing",
            "skill_id": "outline_vocational_數學B2_11",
            "chapter": "1 三角函數",
            "section": "1-1 角度的基本性質",
        },
    ), patch(
        "core.textbook_processor_v2.phase2_deterministic_block_slice",
        return_value=fake_blocks,
    ), patch(
        "core.textbook_processor_v2._DOCX_BLOCK_META",
        fake_meta,
    ), patch(
        "core.textbook_importer_v3_pipeline._ensure_formal_concepts_for_headings",
        return_value=[{"action": "existing", "skill_id": "vh_數學B2_DirectedAngle"}],
    ), patch(
        "core.textbook_formal_concept.get_section_formal_skill_candidates",
        return_value=[{"skill_id": "vh_數學B2_DirectedAngle"}],
    ), patch("core.ai_analyzer.get_model", return_value=MagicMock()), patch(
        "core.ai_analyzer.gemini_model_name", "mock-model"
    ), patch(
        "core.textbook_processor_v2.phase3_ai_metadata_alignment",
        return_value=phase3,
    ), patch(
        "core.textbook_importer_v3_pipeline._attach_anchor_notes_to_phase3",
        return_value=([], {"collision_count": 0, "total": 1}),
    ), patch(
        "core.textbook_importer_v3_pipeline.ensure_db_backup",
        return_value={"backup_path": str(tmp_path / "b.db"), "created": True},
    ), patch(
        "core.textbook_processor_v2.phase4_absolute_hydrate_and_save",
        return_value={"inserted": 1, "updated": 0, "total": 1, "skipped": 0},
    ) as mock_phase4, patch("models.TextbookExample") as mock_te, patch(
        "models.db"
    ) as mock_db:
        mock_te.query = te_query
        mock_db.session.commit = MagicMock()
        mock_db.session.rollback = MagicMock()

        report = run_v3_pair_pipeline(
            project_root=tmp_path,
            docx_path=docx,
            pdf_path=pdf,
            curriculum="vocational",
            volume="數學B2",
            allow_phase4=True,
            emit_stream_end=False,
            app=app,
        )

    assert report["ok"] is True
    assert latex.is_file()
    mock_phase4.assert_called_once()
    assert report["metrics"]["formula_conversion"]["mathtype_found"] == 2

    from core.globals import V3_IMPORT_TASKS

    state = V3_IMPORT_TASKS.get(report["task_id"]) or {}
    st = state.get("stages") or {}
    assert st.get(STAGE_PDF_VISUAL, {}).get("status") in {"success", "skipped"}
    assert st.get(STAGE_IMAGE_LINKING, {}).get("status") in {"success", "skipped"}
    assert st.get(STAGE_DB_WRITE, {}).get("status") == "success"
    assert st.get(STAGE_FORMULA_CONVERSION, {}).get("status") == "success"


def test_find_existing_any_skill_helper_exists():
    from core.textbook_processor_v2 import _find_existing_by_structural_title_any_skill

    assert callable(_find_existing_by_structural_title_any_skill)
