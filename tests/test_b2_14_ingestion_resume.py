from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import zipfile
from pathlib import Path
from unittest.mock import patch

from flask import Flask
from sqlalchemy import text


def _table_snapshot(db, table: str):
    return tuple(tuple(row) for row in db.session.execute(text(f"SELECT * FROM {table}")))


def test_b2_14_full_dry_run_is_source_faithful_and_write_free(tmp_path, monkeypatch):
    from models import db
    from core import ai_analyzer
    from core import textbook_processor_v2 as tp
    from core.textbook_importer_v3_pipeline import run_v3_pair_pipeline

    root = Path(__file__).resolve().parents[1]
    source_dir = root / "textbook_import/source/vocational/math_B2"
    docx = next(p for p in source_dir.glob("*1-4*課本.docx") if not p.stem.casefold().endswith("_latex"))
    pdf = next(source_dir.glob("*1-4*課本.pdf"))
    work_docx = tmp_path / docx.name
    work_pdf = tmp_path / pdf.name
    shutil.copy2(docx, work_docx)
    shutil.copy2(pdf, work_pdf)

    prod = root / "instance/kumon_math.db"
    prod_hash_before = hashlib.sha256(prod.read_bytes()).hexdigest()
    app = Flask("b2_14_dry_run")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    db.init_app(app)

    def forbidden(*args, **kwargs):
        raise AssertionError("dry-run must not depend on Gemini")

    monkeypatch.setattr(tp, "get_model", forbidden)
    monkeypatch.setattr(ai_analyzer, "get_model", forbidden)

    with app.app_context():
        raw = db.engine.raw_connection()
        with sqlite3.connect(prod.as_uri() + "?mode=ro", uri=True) as ro:
            ro.backup(raw.driver_connection)
        raw.close()
        tables = ("skills_info", "skill_curriculum", "textbook_examples")
        before = {table: _table_snapshot(db, table) for table in tables}
        report = run_v3_pair_pipeline(
            project_root=tmp_path,
            docx_path=work_docx,
            pdf_path=work_pdf,
            curriculum="vocational",
            volume="數學B2",
            allow_phase4=False,
            app=app,
        )
        after = {table: _table_snapshot(db, table) for table in tables}

    assert report["ok"], report.get("error")
    metrics = report["metrics"]
    assert metrics["formula_conversion"] == {
        **metrics["formula_conversion"],
        "mathtype_found": 287,
        "mathtype_converted": 287,
        "formula_failures": 0,
    }
    assert metrics["question_parse"]["phase2_blocks"] == 21
    assert metrics["ai_alignment"]["phase3_questions"] == 21
    assert metrics["anchor"]["collision_count"] == 0
    assert metrics["db_write"] == {"skipped": True}
    assert metrics["image_linking"]["linked_count"] == 0
    assert before == after
    assert hashlib.sha256(prod.read_bytes()).hexdigest() == prod_hash_before
    rows = metrics["pdf_visual"]["rows"]
    with zipfile.ZipFile(metrics["formula_conversion"]["latex_docx"]) as converted:
        assert b"MATH_PARSE_FAILED" not in converted.read("word/document.xml")
    assert len({row["source_description"] for row in rows}) == 21
    visual = metrics["pdf_visual"]
    required = [row for row in rows if row.get("source_visual_class") == "QUESTION_REQUIRED"]
    assert visual["question_required"] == 8
    assert visual["matched"] == 8
    assert visual["unmatched"] == 0
    assert visual["source_image_provenance_count"] == 8
    assert [row["visual_page"] for row in required] == [7, 8, 9, 9, 13, 13, 14, 15]
    assert len({(row["visual_page"], tuple(row["visual_bbox"])) for row in required}) == 8
    assert all(row["match_method"] == "ordered_figure_cue" for row in required)
    assert all(row.get("source_image_provenance", {}).get("relationship_id") for row in required)
    assert not any(row.get("should_mount") for row in rows if row not in required)
    from core.textbook_pdf_visual import build_pdf_visual_asset_record
    for row in required:
        asset = build_pdf_visual_asset_record(
            rel_path="uploads/dry-run.png", page_1based=row["visual_page"],
            bbox=row["visual_bbox"], classification="required", visual_type=row["visual_type"],
            match_method=row["match_method"], match_score=row["match_score"],
            reason=row["visual_reason"], image_meta={}, anchor_id=row["anchor_id"],
        )
        assert asset["source"] == "pdf"
        assert asset["question_anchor"] == row["anchor_id"]
        assert asset["display_path"] and asset["bbox"] and asset["source_page"]
    print("B2_14_RESUME_METRICS=" + json.dumps({
        "formula": metrics["formula_conversion"],
        "question_parse": metrics["question_parse"],
        "ai_alignment": metrics["ai_alignment"],
        "curriculum_binding": metrics["curriculum_binding"],
        "anchor": metrics["anchor"],
        "pdf_visual": {k: v for k, v in metrics["pdf_visual"].items() if k != "rows"},
        "required_rows": [{k: row.get(k) for k in (
            "source_description", "match_method", "match_score", "pdf_match",
            "visual_page", "visual_bbox", "visual_reason", "source_image_provenance")}
            for row in rows if row.get("source_visual_class") == "QUESTION_REQUIRED"],
        "db_write": metrics["db_write"],
        "image_linking": metrics["image_linking"],
    }, ensure_ascii=False))


def test_pipeline_rejects_latex_output_as_direct_source(tmp_path):
    from core.textbook_importer_v3_pipeline import run_v3_pair_pipeline

    source = tmp_path / "generic_Latex.docx"
    source.write_bytes(b"not authoritative")
    report = run_v3_pair_pipeline(
        project_root=tmp_path,
        docx_path=source,
        pdf_path=None,
        curriculum="vocational",
        volume="數學B2",
        allow_phase4=False,
        emit_stream_end=False,
    )
    assert report["ok"] is False
    assert report["error"]["error_code"] == "generated_latex_docx_not_source"


def test_formula_fidelity_failure_stops_before_question_parse(tmp_path):
    from core.textbook_importer_v3_pipeline import run_v3_pair_pipeline

    source = tmp_path / "generic.docx"
    source.write_bytes(b"source")

    def failed_convert(src, output):
        Path(output).write_bytes(b"failed conversion artifact")
        return {"mathtype_ole": 2, "converted_ok": 1, "converted_failed": 1}

    with patch("core.textbook_importer_v3_pipeline.parse_docx_summary", return_value={
        "summary": {"mathtype_ole": 2}
    }), patch(
        "core.textbook_importer_v3_pipeline.convert_docx_mathtype_to_latex_docx",
        side_effect=failed_convert,
    ), patch(
        "core.textbook_processor_v2.phase1_extract_docx_lines"
    ) as question_parse:
        report = run_v3_pair_pipeline(
            project_root=tmp_path,
            docx_path=source,
            pdf_path=None,
            curriculum="vocational",
            volume="數學B2",
            allow_phase4=False,
            emit_stream_end=False,
        )
    assert report["ok"] is False
    assert report["error"]["error_code"] == "source_fidelity_formula_failed"
    question_parse.assert_not_called()
