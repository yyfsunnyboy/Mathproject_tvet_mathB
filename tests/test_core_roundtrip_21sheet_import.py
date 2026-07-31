# -*- coding: utf-8 -*-
"""Core round-trip: export-equivalent 21-sheet workbook → clear → import → PK/count/FK checks."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import text

from app import create_app
from core.backup.backup_registry import get_core_table_names
from core.data_importer import import_excel_to_db
from core.routes.admin import _hard_clear_core_data
from core.session_safety import summarize_import_result
from models import User, db

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = PROJECT_ROOT / "reports" / "pytest_core_roundtrip_21sheet"
SOURCE_XLSX = Path(r"C:\Users\Owner\Downloads\kumon_math_backup_20260731_1511.xlsx")


@pytest.fixture()
def app_ctx():
    import config as _cfg

    if not SOURCE_XLSX.exists():
        pytest.skip(f"missing source workbook: {SOURCE_XLSX}")

    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    run_dir = TEST_ROOT / uuid.uuid4().hex[:10]
    run_dir.mkdir(parents=True, exist_ok=True)
    db_path = run_dir / "roundtrip.db"
    prev = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            # Colliding leftover admin (reproduces live failure mode).
            db.session.add(User(id=2589, username="admin", password_hash="x", role="teacher"))
            db.session.commit()
            yield app, run_dir
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev
        shutil.rmtree(run_dir, ignore_errors=True)


def _pk_columns(table: str) -> list[str]:
    rows = db.session.execute(text(f'PRAGMA table_info("{table}")')).fetchall()
    # row: cid, name, type, notnull, dflt, pk
    return [r[1] for r in rows if int(r[5] or 0) > 0]


def _pk_set(table: str) -> set:
    cols = _pk_columns(table)
    if not cols:
        return set()
    if len(cols) == 1:
        return set(db.session.execute(text(f'SELECT "{cols[0]}" FROM "{table}"')).scalars().all())
    rows = db.session.execute(
        text(f'SELECT {", ".join(f"\"{c}\"" for c in cols)} FROM "{table}"')
    ).fetchall()
    return set(tuple(r) for r in rows)


def test_core_roundtrip_21sheet_workbook(app_ctx):
    app, run_dir = app_ctx
    xlsx_path = run_dir / "source.xlsx"
    shutil.copy2(SOURCE_XLSX, xlsx_path)
    source = pd.read_excel(xlsx_path, sheet_name=None, engine="openpyxl")
    core_tables = get_core_table_names(include="import")
    assert set(source.keys()) >= set(core_tables) or len(source) == 21

    with app.app_context():
        # Import into empty-ish DB (only colliding admin).
        ok, msg = import_excel_to_db(str(xlsx_path), mode="core")
        summary = summarize_import_result((ok, msg))
        assert ok is True, msg[-2000:]
        assert summary["failed_rows"] == 0
        assert summary["fatal_errors"] == 0
        assert summary.get("orphan_skill_curriculum_count", 0) == 0
        assert summary["final_status"] in {"completed", "completed_with_warnings"}
        assert "INFO: core restore order=" in msg
        order_line = [ln for ln in msg.splitlines() if ln.startswith("INFO: core restore order=")][0]
        order = order_line.split("=", 1)[1].split(",")
        assert order.index("users") < order.index("classes") < order.index("class_students")
        assert order.index("skills_info") < order.index("skill_curriculum")
        assert order.index("skills_info") < order.index("textbook_examples")
        assert order.index("textbook_examples") < order.index("gencode_component_tracker")

        db.session.execute(text("PRAGMA foreign_keys = ON"))
        assert db.session.execute(text("PRAGMA foreign_key_check")).fetchall() == []

        # Snapshot after successful import.
        after_import_counts = {
            t: int(db.session.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar() or 0)
            for t in core_tables
            if db.session.execute(
                text("SELECT 1 FROM sqlite_master WHERE type='table' AND name=:n"),
                {"n": t},
            ).first()
        }
        after_import_pks = {t: _pk_set(t) for t in after_import_counts}

        # Clear all core textbook + students, keep settings path unused here.
        _hard_clear_core_data(execute=True)
        # After clear, curriculum empty; users may keep teacher stubs from materialization? 
        # hard clear deletes students only — stub students removed; teacher admin id=1 may remain if role teacher.
        ok2, msg2 = import_excel_to_db(str(xlsx_path), mode="core")
        summary2 = summarize_import_result((ok2, msg2))
        assert ok2 is True, msg2[-2000:]
        assert summary2["failed_rows"] == 0
        assert summary2["fatal_errors"] == 0
        assert summary2.get("orphan_skill_curriculum_count", 0) == 0

        for table, count in after_import_counts.items():
            now = int(db.session.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar() or 0)
            assert now == count, (table, now, count)
            assert _pk_set(table) == after_import_pks[table], table

        db.session.execute(text("PRAGMA foreign_keys = ON"))
        assert db.session.execute(text("PRAGMA foreign_key_check")).fetchall() == []


def test_validation_failure_rolls_back_half_import(app_ctx):
    """If post-import validation fails, transaction must not leave half-imported core data."""
    app, run_dir = app_ctx
    from core import data_importer as di

    xlsx_path = run_dir / "bad.xlsx"
    frames = {
        "users": pd.DataFrame([{"id": 1, "username": "t1", "password_hash": "x", "role": "teacher"}]),
        "classes": pd.DataFrame(columns=["id", "name", "teacher_id", "class_code"]),
        "class_students": pd.DataFrame(columns=["id", "class_id", "student_id"]),
        "skills_info": pd.DataFrame(
            [
                {
                    "skill_id": "vh_數學B1_Keep",
                    "skill_en_name": "Keep",
                    "skill_ch_name": "保留",
                    "description": "d",
                    "gemini_prompt": "p",
                }
            ]
        ),
        # Orphan curriculum skill (not in skills_info) — FK violation after import.
        "skill_curriculum": pd.DataFrame(
            [
                {
                    "skill_id": "jh_數學1上_MissingParent",
                    "curriculum": "junior_high",
                    "grade": 7,
                    "volume": "數學1上",
                    "chapter": "1",
                    "section": "1-1",
                    "paragraph": "",
                }
            ]
        ),
        "questions": pd.DataFrame(columns=["id", "skill_id", "content"]),
        "progress": pd.DataFrame(columns=["user_id", "skill_id"]),
        "student_abilities": pd.DataFrame(columns=["id", "user_id", "skill_id"]),
        "quiz_attempts": pd.DataFrame(columns=["id", "user_id", "question_id"]),
        "adaptive_learning_logs": pd.DataFrame(columns=["id", "student_id"]),
        "mistake_logs": pd.DataFrame(columns=["id", "user_id"]),
        "mistake_notebook_entries": pd.DataFrame(columns=["id", "student_id"]),
        "exam_analysis": pd.DataFrame(columns=["id", "user_id"]),
        "student_uploaded_questions": pd.DataFrame(columns=["id", "student_id"]),
        "node_competency": pd.DataFrame(columns=["id", "user_id"]),
        "learning_diagnosis": pd.DataFrame(columns=["id", "student_id"]),
        "b4_chap2_visibility_audit_logs": pd.DataFrame(columns=["id", "student_id"]),
        "textbook_examples": pd.DataFrame(columns=["id", "skill_id"]),
        "skill_family_bridge": pd.DataFrame(columns=["bridge_id", "skill_id", "family_id"]),
        "skill_prerequisites": pd.DataFrame(columns=["id", "skill_id", "prerequisite_id"]),
        "gencode_component_tracker": pd.DataFrame(columns=["id", "textbook_example_id", "skill_id", "component_id"]),
    }
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        for name, df in frames.items():
            df.to_excel(writer, sheet_name=name, index=False)

    with app.app_context():
        original = di._augment_core_workbook_missing_parents
        di._augment_core_workbook_missing_parents = lambda xls: []
        try:
            before_skills = int(db.session.execute(text("SELECT COUNT(*) FROM skills_info")).scalar() or 0)
            ok, msg = import_excel_to_db(str(xlsx_path), mode="core")
        finally:
            di._augment_core_workbook_missing_parents = original

        assert ok is False
        assert "post_import_validation_failed" in msg
        after_skills = int(db.session.execute(text("SELECT COUNT(*) FROM skills_info")).scalar() or 0)
        assert after_skills == before_skills
        assert (
            db.session.execute(
                text("SELECT COUNT(*) FROM skills_info WHERE skill_id='vh_數學B1_Keep'")
            ).scalar()
            == 0
        )
        assert db.session.execute(text("SELECT COUNT(*) FROM skill_curriculum")).scalar() == 0
