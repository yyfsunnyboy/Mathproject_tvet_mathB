"""Focused regression coverage for XML-safe backup export."""

from __future__ import annotations

import io
import sqlite3

import openpyxl
import pandas as pd

from core.backup.backup_validator import write_workbook_bytes
from core.backup.excel_sanitizer import (
    repair_known_latex_escape_corruption,
    sanitize_excel_text,
    sanitize_export_frames,
)
from core.practice_attempt_service import _normalize_answer_text


def test_repairs_only_evidence_backed_form_feed_frac() -> None:
    broken = "x \\ge \x0crac{17}{9}"
    repaired, labels = repair_known_latex_escape_corruption(broken)
    assert repaired == r"x \ge \frac{17}{9}"
    assert labels == ["form_feed_frac"]


def test_valid_latex_is_unchanged_through_persistence_normalization() -> None:
    valid = r"\frac{17}{9} \theta \beta \rho \nabla"
    repaired, labels = repair_known_latex_escape_corruption(valid)
    assert repaired == valid
    assert labels == []
    assert _normalize_answer_text(valid) == valid


def test_latex_repair_survives_sqlite_serialization_round_trip() -> None:
    source = "x \\ge \x0crac{17}{9}"
    serialized = _normalize_answer_text(source)
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE attempts (answer TEXT NOT NULL)")
        connection.execute("INSERT INTO attempts(answer) VALUES (?)", (serialized,))
        restored = connection.execute("SELECT answer FROM attempts").fetchone()[0]
    finally:
        connection.close()
    assert restored == r"x \ge \frac{17}{9}"


def test_excel_export_repairs_latex_and_reopens() -> None:
    frames = {
        "practice_attempts": pd.DataFrame(
            [{"id": 7, "user_answer": "x \\ge \x0crac{17}{9}"}]
        )
    }
    manifest = pd.DataFrame([{"section": "meta", "key": "ok", "value": "1"}])
    sanitized, report = sanitize_export_frames(frames)
    assert sanitized["practice_attempts"].at[0, "user_answer"] == r"x \ge \frac{17}{9}"
    assert report.repaired_latex_cells == 1
    payload = write_workbook_bytes(frames, manifest)
    workbook = openpyxl.load_workbook(io.BytesIO(payload), read_only=True)
    rows = list(workbook["practice_attempts"].values)
    assert rows[1][1] == r"x \ge \frac{17}{9}"


def test_excel_export_preserves_legal_whitespace_and_escapes_unknown_control() -> None:
    legal = "first\tsecond\nthird\rfourth"
    unknown = "a\x01b"
    cleaned_legal, repairs, escaped = sanitize_excel_text(legal)
    assert cleaned_legal == legal
    assert repairs == []
    assert escaped == []
    cleaned_unknown, _, escaped_unknown = sanitize_excel_text(unknown)
    assert cleaned_unknown == r"a\u0001b"
    assert escaped_unknown == ["U+0001"]
    payload = write_workbook_bytes(
        {"notes": pd.DataFrame([{"legal": legal, "unknown": unknown}])},
        pd.DataFrame([{"section": "meta", "key": "ok", "value": "1"}]),
    )
    workbook = openpyxl.load_workbook(io.BytesIO(payload), read_only=True)
    row = list(workbook["notes"].values)[1]
    assert row == (legal, r"a\u0001b")
