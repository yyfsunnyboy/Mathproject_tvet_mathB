import base64
import json
import sqlite3

from scripts.docx_formula_ocr_backfill import (
    BackfillRow,
    process_row,
    render_markdown_report,
    run_backfill,
    write_report,
)


def _write_png(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    )
    path.write_bytes(data)


def _meta(asset):
    return {
        "formula_assets": [asset],
        "needs_review": True,
        "needs_formula_review": True,
    }


def _row(notes, problem_text="題目 [FORMULA_IMAGE_1]"):
    return BackfillRow(
        id=1,
        source_description="例題1 [source_type=textbook_example]",
        problem_text=problem_text,
        notes=json.dumps(notes, ensure_ascii=False),
    )


def _make_db(path, notes):
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            source_curriculum TEXT,
            source_volume TEXT,
            source_section TEXT,
            source_description TEXT,
            problem_text TEXT,
            notes TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO textbook_examples
        (id, source_curriculum, source_volume, source_section, source_description, problem_text, notes)
        VALUES (1, 'vocational', '數學B1', '1-1 數線與絕對值', '例題1', '題目 [FORMULA_IMAGE_1]', ?)
        """,
        (json.dumps(notes, ensure_ascii=False),),
    )
    conn.commit()
    conn.close()


def test_dry_run_does_not_write_db_and_returns_preview(tmp_path):
    img = tmp_path / "uploads" / "formula.png"
    _write_png(img)
    db = tmp_path / "test.sqlite"
    notes = _meta(
        {
            "path": "uploads/formula.png",
            "display_path": "uploads/formula.png",
            "original_format": "png",
            "placeholder_token": "[FORMULA_IMAGE_1]",
            "conversion_status": "not_required",
        }
    )
    _make_db(db, notes)

    result = run_backfill(
        db_path=db,
        root_path=tmp_path,
        dry_run=True,
        ocr_enabled=True,
        titles=[],
        ocr_callable=lambda *_: ("x+1", "fake-vision"),
    )

    conn = sqlite3.connect(db)
    stored = conn.execute("SELECT notes FROM textbook_examples WHERE id=1").fetchone()[0]
    conn.close()
    assert json.loads(stored) == notes
    assert result["summary"]["success_count"] == 1
    assert result["rows"][0]["metadata_after"]["formula_assets"][0]["formula_ocr_text"] == "x+1"


def test_no_readable_image_marks_skipped_no_readable_image(tmp_path):
    notes = _meta(
        {
            "path": "uploads/formula.wmf",
            "original_format": "wmf",
            "placeholder_token": "[FORMULA_IMAGE_1]",
            "conversion_status": "failed",
        }
    )
    result = process_row(_row(notes), root_path=tmp_path, ocr_enabled=True)
    asset = result["metadata_after"]["formula_assets"][0]
    assert asset["formula_ocr_status"] == "skipped_no_readable_image"
    assert asset["review_required"] is True
    assert result["summary"]["skipped_count"] == 1
    assert result["summary"]["skipped_no_readable_image"] == 1


def test_ocr_success_writes_metadata_but_problem_text_unchanged(tmp_path):
    img = tmp_path / "formula.png"
    _write_png(img)
    notes = _meta(
        {
            "path": "formula.png",
            "display_path": "formula.png",
            "original_format": "png",
            "placeholder_token": "[FORMULA_IMAGE_1]",
            "conversion_status": "not_required",
        }
    )
    result = process_row(
        _row(notes),
        root_path=tmp_path,
        ocr_enabled=True,
        ocr_callable=lambda *_: ("|x|", "fake-vision"),
    )
    asset = result["metadata_after"]["formula_assets"][0]
    assert asset["formula_ocr_status"] == "success"
    assert asset["formula_ocr_text"] == "|x|"
    assert asset["formula_ocr_source"] == "gemini_vision"
    assert asset["review_required"] is True
    assert result["problem_text"] == "題目 [FORMULA_IMAGE_1]"


def test_ocr_failure_keeps_placeholder_and_does_not_raise(tmp_path):
    img = tmp_path / "formula.png"
    _write_png(img)
    notes = _meta(
        {
            "display_path": "formula.png",
            "original_format": "png",
            "placeholder_token": "[FORMULA_IMAGE_1]",
            "conversion_status": "not_required",
        }
    )

    def boom(*_):
        raise RuntimeError("vision down")

    result = process_row(_row(notes), root_path=tmp_path, ocr_enabled=True, ocr_callable=boom)
    asset = result["metadata_after"]["formula_assets"][0]
    assert asset["formula_ocr_status"] == "failed"
    assert "vision down" in asset["formula_ocr_error"]
    assert "[FORMULA_IMAGE_1]" in result["problem_text"]


def test_review_flags_are_preserved(tmp_path):
    notes = _meta(
        {
            "path": "formula.emf",
            "original_format": "emf",
            "placeholder_token": "[FORMULA_IMAGE_1]",
            "conversion_status": "pending",
        }
    )
    result = process_row(_row(notes), root_path=tmp_path, ocr_enabled=True)
    assert result["metadata_after"]["needs_review"] is True
    assert result["metadata_after"]["needs_formula_review"] is True


def test_report_contains_success_and_failed_statistics(tmp_path):
    result = {
        "scope": {"curriculum": "vocational", "volume": "數學B1", "section": "1-1", "limit": 10},
        "dry_run": True,
        "ocr_enabled": True,
        "question_count": 2,
        "summary": {
            "total_assets": 2,
            "processed_records": 2,
            "processed_assets": 2,
            "readable_assets": 2,
            "skipped_no_readable_image": 0,
            "vision_success": 1,
            "vision_failed": 1,
            "success_count": 1,
            "failed_count": 1,
            "skipped_count": 0,
            "unreadable_count": 0,
        },
        "rows": [
            {
                "asset_summaries": [
                    {
                        "id": 1,
                        "source_description": "例題1",
                        "problem_text": "題目 [FORMULA_IMAGE_1]",
                        "placeholder_token": "[FORMULA_IMAGE_1]",
                        "asset_path": "a.png",
                        "converted_path": "",
                        "conversion_status": "not_required",
                        "formula_ocr_status": "success",
                        "formula_ocr_text": "x+1",
                        "formula_ocr_source": "gemini_vision",
                        "formula_ocr_model": "fake-vision",
                        "review_required": True,
                    },
                    {
                        "id": 2,
                        "source_description": "例題2",
                        "problem_text": "題目 [FORMULA_IMAGE_1]",
                        "placeholder_token": "[FORMULA_IMAGE_1]",
                        "asset_path": "b.png",
                        "converted_path": "",
                        "conversion_status": "not_required",
                        "formula_ocr_status": "failed",
                        "formula_ocr_error": "vision down",
                        "formula_ocr_source": "gemini_vision",
                        "formula_ocr_model": "fake-vision",
                        "review_required": True,
                    },
                ]
            },
            {
                "row_id": 1,
                "source_description": "例題1 [source_type=textbook_example]",
                "summary": {"processed_assets": 1, "readable_assets": 1, "skipped_no_readable_image": 0},
                "asset_summaries": [],
            },
        ],
    }
    report = render_markdown_report(result)
    assert "- success: 1" in report
    assert "- failed: 1" in report
    assert "- processed_assets: 2" in report
    assert "- vision_success: 1" in report
    assert "- vision_failed: 1" in report
    assert "- OCR / vision candidates:" in report
    path = write_report(result, tmp_path / "report.md")
    assert path.exists()


def test_tesseract_absent_does_not_raise_with_png_and_mock_vision(tmp_path):
    img = tmp_path / "uploads" / "formula.png"
    _write_png(img)
    notes = _meta(
        {
            "display_path": "uploads/formula.png",
            "original_format": "png",
            "placeholder_token": "[FORMULA_IMAGE_1]",
        }
    )
    result = process_row(
        _row(notes),
        root_path=tmp_path,
        ocr_enabled=True,
        ocr_callable=lambda *_: ("x^2", "fake-vision"),
    )
    assert result["summary"]["vision_success"] == 1
    assert result["metadata_after"]["formula_assets"][0]["formula_ocr_text"] == "x^2"


def test_run_backfill_supports_title_filter(tmp_path):
    img = tmp_path / "uploads" / "formula.png"
    _write_png(img)
    db = tmp_path / "title_filter.sqlite"
    conn = sqlite3.connect(db)
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            source_curriculum TEXT,
            source_volume TEXT,
            source_section TEXT,
            source_description TEXT,
            problem_text TEXT,
            notes TEXT
        )
        """
    )
    notes = json.dumps(_meta({"display_path": "uploads/formula.png", "original_format": "png", "placeholder_token": "[FORMULA_IMAGE_1]"}), ensure_ascii=False)
    conn.execute(
        """
        INSERT INTO textbook_examples
        (id, source_curriculum, source_volume, source_section, source_description, problem_text, notes)
        VALUES (1, 'vocational', '數學B1', '1-1 數線與絕對值', '例題1', '題目 [FORMULA_IMAGE_1]', ?)
        """,
        (notes,),
    )
    conn.execute(
        """
        INSERT INTO textbook_examples
        (id, source_curriculum, source_volume, source_section, source_description, problem_text, notes)
        VALUES (2, 'vocational', '數學B1', '1-1 數線與絕對值', '例題2', '題目 [FORMULA_IMAGE_1]', ?)
        """,
        (notes,),
    )
    conn.commit()
    conn.close()

    result = run_backfill(
        db_path=db,
        root_path=tmp_path,
        curriculum="vocational",
        volume="數學B1",
        section="1-1 數線與絕對值",
        titles=["例題1"],
        limit=None,
        dry_run=True,
        ocr_enabled=True,
        ocr_callable=lambda *_: ("x+1", "fake-vision"),
    )
    assert result["question_count"] == 1
