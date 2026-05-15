import base64
import json
import sqlite3

from scripts.convert_b1_1_1_formula_assets_to_png import run_conversion


def _write_png(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    )
    path.write_bytes(data)


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


def test_dry_run_does_not_write_db(tmp_path):
    source = tmp_path / "uploads" / "a.wmf"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(b"wmf")
    db = tmp_path / "c.sqlite"
    notes = {"formula_assets": [{"path": "uploads/a.wmf", "original_format": "wmf", "placeholder_token": "[FORMULA_IMAGE_1]"}]}
    _make_db(db, notes)

    def ok_converter(_in, out):
        _write_png(tmp_path / out)
        return True, None

    result = run_conversion(
        db_path=db,
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        limit_assets=10,
        dry_run=True,
        write_converted_path=False,
        converter=ok_converter,
    )
    assert result["summary"]["conversion_success"] == 1
    conn = sqlite3.connect(db)
    stored = conn.execute("SELECT notes FROM textbook_examples WHERE id=1").fetchone()[0]
    conn.close()
    assert json.loads(stored) == notes


def test_conversion_success_has_converted_path(tmp_path):
    source = tmp_path / "uploads" / "b.emf"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(b"emf")
    db = tmp_path / "s.sqlite"
    notes = {"formula_assets": [{"path": "uploads/b.emf", "original_format": "emf", "placeholder_token": "[FORMULA_IMAGE_1]"}]}
    _make_db(db, notes)

    def ok_converter(_in, out):
        _write_png(tmp_path / out)
        return True, None

    result = run_conversion(
        db_path=db,
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        limit_assets=10,
        dry_run=True,
        write_converted_path=False,
        converter=ok_converter,
    )
    row = result["rows"][0]
    assert row["summary"]["success_count"] == 1
    assert row["summary"]["sample_converted_path"].endswith(".png")


def test_conversion_failure_is_reported_without_raise(tmp_path):
    source = tmp_path / "uploads" / "c.wmf"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(b"wmf")
    db = tmp_path / "f.sqlite"
    notes = {"formula_assets": [{"path": "uploads/c.wmf", "original_format": "wmf", "placeholder_token": "[FORMULA_IMAGE_1]"}]}
    _make_db(db, notes)

    def fail_converter(_in, _out):
        return False, "tool_not_available"

    result = run_conversion(
        db_path=db,
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        limit_assets=10,
        dry_run=True,
        write_converted_path=False,
        converter=fail_converter,
    )
    assert result["summary"]["conversion_failed"] == 1
    assert "tool_not_available" in result["rows"][0]["summary"]["sample_error"]


def test_vector_without_path_is_skipped_missing_path(tmp_path):
    db = tmp_path / "m.sqlite"
    notes = {"formula_assets": [{"original_format": "wmf", "placeholder_token": "[FORMULA_IMAGE_1]"}]}
    _make_db(db, notes)
    result = run_conversion(
        db_path=db,
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        limit_assets=10,
        dry_run=True,
        write_converted_path=False,
        converter=lambda *_: (True, None),
    )
    assert result["summary"]["skipped_missing_path"] == 1
    assert result["summary"]["conversion_failed"] == 1


def test_png_is_skipped_non_vector(tmp_path):
    db = tmp_path / "n.sqlite"
    notes = {"formula_assets": [{"path": "uploads/a.png", "original_format": "png", "placeholder_token": "[FORMULA_IMAGE_1]"}]}
    _make_db(db, notes)
    result = run_conversion(
        db_path=db,
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        limit_assets=10,
        dry_run=True,
        write_converted_path=False,
        converter=lambda *_: (True, None),
    )
    assert result["summary"]["candidate_assets"] == 0
    assert result["summary"]["skipped_non_vector"] == 1


def test_write_converted_path_writes_metadata_only(tmp_path):
    source = tmp_path / "uploads" / "d.wmf"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(b"wmf")
    db = tmp_path / "w.sqlite"
    notes = {"formula_assets": [{"path": "uploads/d.wmf", "original_format": "wmf", "placeholder_token": "[FORMULA_IMAGE_1]"}]}
    _make_db(db, notes)

    def ok_converter(_in, out):
        _write_png(tmp_path / out)
        return True, None

    run_conversion(
        db_path=db,
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        limit_assets=10,
        dry_run=False,
        write_converted_path=True,
        converter=ok_converter,
    )
    conn = sqlite3.connect(db)
    stored_notes, stored_problem = conn.execute("SELECT notes, problem_text FROM textbook_examples WHERE id=1").fetchone()
    conn.close()
    data = json.loads(stored_notes)
    assert data["formula_assets"][0]["converted_path"].endswith(".png")
    assert data["formula_assets"][0]["conversion_status"] == "success"
    assert stored_problem == "題目 [FORMULA_IMAGE_1]"


def test_conversion_prefers_persistent_over_tmp_same_hash(tmp_path):
    src = tmp_path / "uploads" / "question_assets" / "x.wmf"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_bytes(b"wmf")
    db = tmp_path / "pref.sqlite"
    notes = {
        "formula_assets": [
            {
                "path": "uploads/tmp_docx_media/a/media/x.wmf",
                "original_path": "uploads/tmp_docx_media/a/media/x.wmf",
                "old_temp_path": "uploads/tmp_docx_media/a/media/x.wmf",
                "asset_hash": "h1",
                "original_format": "wmf",
                "placeholder_token": "[FORMULA_IMAGE_1]",
            },
            {
                "path": "uploads/question_assets/x.wmf",
                "original_path": "uploads/question_assets/x.wmf",
                "old_temp_path": "uploads/tmp_docx_media/a/media/x.wmf",
                "asset_hash": "h1",
                "persist_status": "persisted",
                "original_format": "wmf",
                "placeholder_token": "[FORMULA_IMAGE_1]",
            },
        ]
    }
    _make_db(db, notes)

    def ok_converter(_in, out):
        _write_png(tmp_path / out)
        return True, None

    result = run_conversion(
        db_path=db,
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        limit_assets=10,
        dry_run=True,
        write_converted_path=False,
        converter=ok_converter,
    )
    s = result["summary"]
    assert s["selected_tmp_assets"] == 0
    assert s["selected_persistent_assets"] >= 1
    assert s["conversion_success"] == 1
