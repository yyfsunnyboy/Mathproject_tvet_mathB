import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from core.textbook_uploaded_sources import retain_uploaded_pair, resolve_db_source_pair


def test_pair_survives_temporary_cleanup_and_reuses_same_content(tmp_path):
    temporary = tmp_path / "uploads"
    temporary.mkdir()
    docx, pdf = temporary / "03-.docx", temporary / "03-.pdf"
    docx.write_bytes(b"original docx")
    pdf.write_bytes(b"original pdf")
    files = [(docx, "單元03-指數.docx"), (pdf, "單元03-指數.pdf")]
    first = retain_uploaded_pair(tmp_path, files, "general", "數學1")
    second = retain_uploaded_pair(tmp_path, files, "general", "數學1")
    assert first == second
    assert len(list((tmp_path / "textbook_import/uploaded_sources/general/數學1").glob("*.docx"))) == 1
    docx.unlink()
    pdf.unlink()
    notes = {"source_provenance": {"primary": first["docx"], "optional_enrich_pdf": first["pdf"]}}
    found = resolve_db_source_pair(tmp_path, notes, "general", "數學1")
    assert [p.read_bytes() for p in found] == [b"original docx", b"original pdf"]
    manifest = next((tmp_path / "textbook_import/uploaded_sources/general/數學1").glob("*.json"))
    assert json.loads(manifest.read_text(encoding="utf-8"))["status"] == "retained_pending_import"


def test_same_name_different_content_keeps_versions(tmp_path):
    a, b = tmp_path / "a.docx", tmp_path / "b.pdf"
    a.write_bytes(b"first")
    b.write_bytes(b"pdf")
    pair = [(a, "unit.docx"), (b, "unit.pdf")]
    first = retain_uploaded_pair(tmp_path, pair, "general", "數學1")
    a.write_bytes(b"second")
    second = retain_uploaded_pair(tmp_path, pair, "general", "數學1")
    assert first["docx"]["stored_path"] != second["docx"]["stored_path"]
    for record, expected in ((first["docx"], b"first"), (second["docx"], b"second")):
        assert (tmp_path / record["stored_path"]).read_bytes() == expected


def test_legacy_hash_location_and_mismatch(tmp_path):
    a, b = tmp_path / "a.docx", tmp_path / "b.pdf"
    a.write_bytes(b"docx")
    b.write_bytes(b"pdf")
    pair = retain_uploaded_pair(tmp_path, [(a, "03-.docx"), (b, "03-.pdf")], "general", "數學1")
    legacy = {key: {name: val for name, val in record.items() if name != "stored_path"} for key, record in pair.items()}
    notes = {"source_provenance": {"primary": legacy["docx"], "optional_enrich_pdf": legacy["pdf"]}}
    assert resolve_db_source_pair(tmp_path, notes, "general", "數學1")[0].read_bytes() == b"docx"
    notes["source_provenance"]["primary"]["sha256"] = hashlib.sha256(b"wrong").hexdigest()
    with pytest.raises(ValueError, match="source_missing_or_ambiguous"):
        resolve_db_source_pair(tmp_path, notes, "general", "數學1")


def test_existing_unit3_db_provenance_resolves_read_only():
    root = Path(__file__).resolve().parents[1]
    db = root / "instance/kumon_math.db"
    if not db.is_file():
        pytest.skip("local production snapshot unavailable")
    with sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True) as connection:
        row = connection.execute("select notes,source_curriculum,source_volume from textbook_examples where id=12339").fetchone()
    if row is None:
        pytest.skip("Unit 3 import unavailable")
    docx, pdf = resolve_db_source_pair(root, row[0], row[1], row[2])
    assert docx.suffix == ".docx" and pdf.suffix == ".pdf"


def test_legacy_manual_source_is_unchanged(tmp_path):
    from core.textbook_uploaded_sources import resolve_stage1_source_pair

    directory = tmp_path / "textbook_import/source/vocational/math_B2"
    directory.mkdir(parents=True)
    docx = directory / "第一章 1-4 正弦、餘弦函數的圖形-課本.docx"
    pdf = docx.with_suffix(".pdf")
    docx.write_bytes(b"docx")
    pdf.write_bytes(b"pdf")
    assert resolve_stage1_source_pair(tmp_path, {}, "vocational", "數學B2", "1-4 正弦、餘弦函數的圖形") == (docx.resolve(), pdf.resolve())
