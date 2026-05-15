import json
import sqlite3

from scripts.persist_b1_1_1_formula_assets import run_persist


def _make_db(path, notes, source_description="例題1 [source_type=textbook_example]"):
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
        VALUES (1, 'vocational', '數學B1', '1-1 數線與絕對值', ?, '題目 [FORMULA_IMAGE_1]', ?)
        """,
        (source_description, json.dumps(notes, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()


def test_dry_run_does_not_write_db(tmp_path):
    src = tmp_path / "uploads" / "tmp_docx_media" / "a" / "media" / "image1.wmf"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_bytes(b"wmf")
    db = tmp_path / "p.sqlite"
    _make_db(db, {"formula_assets": [{"path": "old/path.wmf"}]})
    override = {"例題1": [{"media_kind": "formula_asset", "path": "uploads/tmp_docx_media/a/media/image1.wmf", "original_format": "wmf", "placeholder_token": "[FORMULA_IMAGE_1]"}]}

    result = run_persist(
        db_path=db,
        docx_path=tmp_path / "fake.docx",
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        dry_run=True,
        write=False,
        docx_question_assets_override=override,
    )
    assert result["summary"]["copied_assets"] == 1
    conn = sqlite3.connect(db)
    stored = conn.execute("SELECT notes FROM textbook_examples WHERE id=1").fetchone()[0]
    conn.close()
    assert json.loads(stored)["formula_assets"][0]["path"] == "old/path.wmf"


def test_lookup_success_report_has_persistent_path(tmp_path):
    src = tmp_path / "uploads" / "tmp_docx_media" / "a" / "media" / "image1.wmf"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_bytes(b"wmf")
    db = tmp_path / "q.sqlite"
    _make_db(db, {"formula_assets": []})
    override = {"例題1": [{"media_kind": "formula_asset", "path": "uploads/tmp_docx_media/a/media/image1.wmf", "original_format": "wmf", "placeholder_token": "[FORMULA_IMAGE_1]"}]}
    result = run_persist(
        db_path=db,
        docx_path=tmp_path / "fake.docx",
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        dry_run=True,
        write=False,
        docx_question_assets_override=override,
    )
    assert result["rows"][0]["sample_persistent_path"].endswith("image1.wmf")


def test_write_updates_metadata_only_with_write_flag(tmp_path):
    src = tmp_path / "uploads" / "tmp_docx_media" / "a" / "media" / "image1.wmf"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_bytes(b"wmf")
    db = tmp_path / "w.sqlite"
    _make_db(db, {"formula_assets": [{"path": "old/path.wmf"}]})
    override = {"例題1": [{"media_kind": "formula_asset", "path": "uploads/tmp_docx_media/a/media/image1.wmf", "original_format": "wmf", "placeholder_token": "[FORMULA_IMAGE_1]"}]}
    run_persist(
        db_path=db,
        docx_path=tmp_path / "fake.docx",
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        dry_run=False,
        write=True,
        docx_question_assets_override=override,
    )
    conn = sqlite3.connect(db)
    notes, problem_text = conn.execute("SELECT notes, problem_text FROM textbook_examples WHERE id=1").fetchone()
    conn.close()
    meta = json.loads(notes)
    assert meta["formula_assets"][0]["path"].startswith("uploads/question_assets/longteng_數學B1/CH1/1-1/formula_assets/")
    assert meta["formula_assets"][0]["old_original_path"].endswith("image1.wmf")
    assert problem_text == "題目 [FORMULA_IMAGE_1]"


def test_docx_not_found_no_crash_no_write(tmp_path):
    db = tmp_path / "d.sqlite"
    _make_db(db, {"formula_assets": [{"path": "old/path.wmf"}]})
    result = run_persist(
        db_path=db,
        docx_path=tmp_path / "notfound.docx",
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        dry_run=True,
        write=False,
    )
    assert "docx_not_found" in result["docx_error"]
    conn = sqlite3.connect(db)
    notes = conn.execute("SELECT notes FROM textbook_examples WHERE id=1").fetchone()[0]
    conn.close()
    assert json.loads(notes)["formula_assets"][0]["path"] == "old/path.wmf"


def test_source_missing_counted(tmp_path):
    db = tmp_path / "m.sqlite"
    _make_db(db, {"formula_assets": []})
    override = {"例題1": [{"media_kind": "formula_asset", "path": "uploads/tmp_docx_media/a/media/missing.wmf", "original_format": "wmf", "placeholder_token": "[FORMULA_IMAGE_1]"}]}
    result = run_persist(
        db_path=db,
        docx_path=tmp_path / "fake.docx",
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        dry_run=True,
        write=False,
        docx_question_assets_override=override,
    )
    assert result["summary"]["source_missing"] == 1


def test_write_prefers_persistent_when_same_hash_exists(tmp_path):
    src = tmp_path / "uploads" / "tmp_docx_media" / "a" / "media" / "image1.wmf"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_bytes(b"wmf")
    db = tmp_path / "merge.sqlite"
    _make_db(
        db,
        {
            "formula_assets": [
                {
                    "path": "uploads/tmp_docx_media/a/media/image1.wmf",
                    "original_path": "uploads/tmp_docx_media/a/media/image1.wmf",
                    "asset_hash": "samehash",
                    "placeholder_token": "[FORMULA_IMAGE_1]",
                }
            ]
        },
    )
    override = {
        "例題1": [
            {
                "media_kind": "formula_asset",
                "path": "uploads/tmp_docx_media/a/media/image1.wmf",
                "original_format": "wmf",
                "placeholder_token": "[FORMULA_IMAGE_1]",
                "asset_hash": "samehash",
            }
        ]
    }
    run_persist(
        db_path=db,
        docx_path=tmp_path / "fake.docx",
        root_path=tmp_path,
        titles=["例題1"],
        limit_records=1,
        dry_run=False,
        write=True,
        docx_question_assets_override=override,
    )
    conn = sqlite3.connect(db)
    notes = conn.execute("SELECT notes FROM textbook_examples WHERE id=1").fetchone()[0]
    conn.close()
    assets = json.loads(notes)["formula_assets"]
    assert len(assets) == 1
    assert "tmp_docx_media" not in assets[0]["path"]
