# -*- coding: utf-8 -*-
"""Regression: db_maintenance with practice_attempts + class_students.seat_no."""
from __future__ import annotations

import io
import shutil
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import inspect, text

from app import create_app
from core.backup.backup_registry import get_core_table_names, get_table_spec
from core.data_importer import import_excel_to_db
from core.practice_attempt_service import SOURCE_GENERAL_PRACTICE
from core.routes.admin import _hard_clear_vocational_math_b_core, _run_full_clear
from core.teacher_analysis_service import get_class_students_stats, get_student_overview, parse_time_range
from models import Class, ClassStudent, PracticeAttempt, SkillCurriculum, SkillInfo, User, db

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = PROJECT_ROOT / "reports" / "pytest_db_maint_practice_attempts"


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def app_ctx(tmp_path):
    import config as _cfg

    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    run_dir = TEST_ROOT / uuid.uuid4().hex[:8]
    run_dir.mkdir(parents=True, exist_ok=True)
    db_path = run_dir / "maint.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            admin = User(username=f"admin_{uuid.uuid4().hex[:6]}", password_hash="x", role="admin")
            db.session.add(admin)
            db.session.commit()
            yield app, admin.id, run_dir
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        shutil.rmtree(run_dir, ignore_errors=True)


def _seed_roster_with_attempts() -> dict:
    teacher = User(id=501, username="teacher_m", password_hash="h", role="teacher")
    student = User(id=502, username="315001_like", password_hash="h", role="student", real_name="測試生")
    db.session.add_all([teacher, student])
    db.session.flush()
    clazz = Class(id=701, name="多三甲", teacher_id=501, class_code="MAINT0001")
    db.session.add(clazz)
    db.session.flush()
    db.session.add(ClassStudent(id=801, class_id=701, student_id=502, seat_no=1))
    skill = "vh_數學B1_AbsoluteValue"
    db.session.add(
        SkillInfo(skill_id=skill, skill_en_name="e", skill_ch_name="絕對值", description="d", gemini_prompt="p")
    )
    db.session.add(
        SkillCurriculum(
            skill_id=skill,
            curriculum="vocational",
            grade=10,
            volume="數學B1",
            chapter="1 絕對值",
            section="1-1",
            paragraph="",
        )
    )
    now = datetime.utcnow()
    db.session.add_all([
        PracticeAttempt(
            id=1001,
            student_id=502,
            class_id=701,
            skill_id=skill,
            question_text="解 |x| = 3",
            user_answer="3",
            expected_answer="3,-3",
            is_correct=True,
            source=SOURCE_GENERAL_PRACTICE,
            created_at=now,
        ),
        PracticeAttempt(
            id=1002,
            student_id=502,
            class_id=701,
            skill_id=skill,
            question_text="解 |x| >= 18",
            user_answer="x>=18",
            expected_answer="(-∞,-18] ∪ [18,∞)",
            is_correct=True,
            source=SOURCE_GENERAL_PRACTICE,
            created_at=now,
        ),
        PracticeAttempt(
            id=1003,
            student_id=502,
            class_id=701,
            skill_id=skill,
            question_text="解 |x| < 2",
            user_answer="wrong",
            expected_answer="(-2,2)",
            is_correct=False,
            source=SOURCE_GENERAL_PRACTICE,
            created_at=now,
        ),
    ])
    db.session.commit()
    return {"student_id": 502, "class_id": 701, "skill": skill}


def _integrity_ok(db_path: Path) -> tuple[str, int]:
    conn = sqlite3.connect(db_path)
    try:
        ic = conn.execute("PRAGMA integrity_check").fetchone()[0]
        fk_rows = conn.execute("PRAGMA foreign_key_check").fetchall()
        return ic, len(fk_rows)
    finally:
        conn.close()


def test_registry_includes_practice_attempts():
    assert "practice_attempts" in get_core_table_names(include="export")
    spec = get_table_spec("practice_attempts")
    assert spec is not None
    assert spec.include_in_core_export
    assert spec.include_in_core_import
    assert spec.include_in_core_clear
    assert spec.clear_mode == "student_fk"
    assert spec.clear_fk_column == "student_id"


def test_core_export_contains_practice_attempts_and_seat_no(app_ctx):
    app, admin_id, _run = app_ctx
    with app.app_context():
        _seed_roster_with_attempts()
        client = app.test_client()
        _login(client, admin_id)
        resp = client.post("/db_maintenance", data={"action": "export_db", "mode": "core"})
        assert resp.status_code == 200
        sheets = pd.read_excel(io.BytesIO(resp.data), sheet_name=None, engine="openpyxl")
        assert "practice_attempts" in sheets
        assert "class_students" in sheets
        pa = sheets["practice_attempts"]
        cs = sheets["class_students"]
        assert len(pa) == 3
        assert "seat_no" in cs.columns
        assert int(cs.iloc[0]["seat_no"]) == 1


def test_core_round_trip_preserves_seat_no_and_attempts(app_ctx):
    app, admin_id, run_dir = app_ctx
    with app.app_context():
        seeded = _seed_roster_with_attempts()
        client = app.test_client()
        _login(client, admin_id)

        export = client.post("/db_maintenance", data={"action": "export_db", "mode": "core"})
        assert export.status_code == 200
        xlsx = run_dir / "core_roundtrip.xlsx"
        xlsx.write_bytes(export.data)

        PracticeAttempt.query.delete()
        ClassStudent.query.delete()
        Class.query.delete()
        User.query.filter(User.role == "student").delete()
        db.session.commit()
        assert PracticeAttempt.query.count() == 0

        ok, msg = import_excel_to_db(str(xlsx), mode="core")
        assert ok, msg

        link = ClassStudent.query.filter_by(class_id=701, student_id=502).first()
        assert link is not None
        assert link.seat_no == 1

        attempts = PracticeAttempt.query.filter_by(student_id=502).order_by(PracticeAttempt.id).all()
        assert len(attempts) == 3
        assert sum(1 for a in attempts if a.is_correct) == 2
        assert attempts[0].question_text == "解 |x| = 3"
        assert attempts[2].user_answer == "wrong"

        student = db.session.get(User, seeded["student_id"])
        overview = get_student_overview(student, parse_time_range("all"))
        assert overview["stats"].total == 3
        assert overview["stats"].correct == 2
        assert overview["stats"].incorrect == 1

        cls = db.session.get(Class, seeded["class_id"])
        rows = get_class_students_stats(cls, parse_time_range("all"))
        assert rows[0]["seat_no"] == 1
        assert rows[0]["stats"].total == 3


def test_legacy_import_without_practice_attempts_sheet(app_ctx):
    app, _admin_id, run_dir = app_ctx
    with app.app_context():
        xlsx = run_dir / "legacy_no_pa.xlsx"
        with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
            pd.DataFrame([
                {"id": 501, "username": "teacher_m", "password_hash": "h", "role": "teacher"},
                {"id": 502, "username": "stu", "password_hash": "h", "role": "student"},
            ]).to_excel(w, sheet_name="users", index=False)
            pd.DataFrame([{"id": 701, "name": "班", "teacher_id": 501, "class_code": "LEG00001"}]).to_excel(
                w, sheet_name="classes", index=False
            )
            pd.DataFrame([{"id": 801, "class_id": 701, "student_id": 502}]).to_excel(
                w, sheet_name="class_students", index=False
            )
            for name in get_core_table_names(include="export"):
                if name not in ("users", "classes", "class_students"):
                    pd.DataFrame().to_excel(w, sheet_name=name, index=False)

        ok, msg = import_excel_to_db(str(xlsx), mode="core")
        assert ok, msg
        assert PracticeAttempt.query.count() == 0
        link = ClassStudent.query.filter_by(id=801).first()
        assert link.seat_no is None


def test_delete_core_clears_practice_attempts(app_ctx):
    app, _admin_id, _run = app_ctx
    with app.app_context():
        _seed_roster_with_attempts()
        assert PracticeAttempt.query.count() == 3
        _hard_clear_vocational_math_b_core(execute=True)
        assert PracticeAttempt.query.count() == 0
        assert User.query.filter_by(role="student").count() == 0
        db.session.execute(text("PRAGMA foreign_keys = ON"))
        assert db.session.execute(text("PRAGMA foreign_key_check")).fetchall() == []


def test_delete_full_clears_practice_attempts(app_ctx):
    app, _admin_id, run_dir = app_ctx
    with app.app_context():
        _seed_roster_with_attempts()
        db_path = Path(run_dir) / "maint.db"
        inspector = inspect(db.engine)
        result = _run_full_clear(execute=True, table_names=inspector.get_table_names())
        assert not result.get("failed_tables")
        assert PracticeAttempt.query.count() == 0
        ic, fk_n = _integrity_ok(db_path)
        assert ic == "ok"
        assert fk_n == 0


def test_db_maintenance_page_200(app_ctx):
    app, admin_id, _run = app_ctx
    with app.app_context():
        client = app.test_client()
        _login(client, admin_id)
        r = client.get("/db_maintenance")
        assert r.status_code == 200
        body = r.get_data(as_text=True)
        assert "practice_attempts" in body or "逐題作答" in body


def test_fresh_db_has_practice_attempts_schema(tmp_path):
    import config as _cfg

    db_path = tmp_path / "fresh.db"
    prev = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        with app.app_context():
            admin = User(username="admin_fresh", password_hash="x", role="admin")
            db.session.add(admin)
            db.session.commit()
            client = app.test_client()
            _login(client, admin.id)
            assert client.get("/db_maintenance").status_code == 200
            conn = sqlite3.connect(db_path)
            cols = [r[1] for r in conn.execute("PRAGMA table_info(practice_attempts)")]
            cs_cols = [r[1] for r in conn.execute("PRAGMA table_info(class_students)")]
            conn.close()
            assert "student_id" in cols
            assert "seat_no" in cs_cols
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev


def test_full_export_contains_practice_attempts(app_ctx):
    app, admin_id, _run = app_ctx
    with app.app_context():
        _seed_roster_with_attempts()
        client = app.test_client()
        _login(client, admin_id)
        resp = client.post("/db_maintenance", data={"action": "export_db", "mode": "full"})
        assert resp.status_code == 200
        sheets = pd.read_excel(io.BytesIO(resp.data), sheet_name=None, engine="openpyxl")
        assert "practice_attempts" in sheets
        assert len(sheets["practice_attempts"]) == 3
        cs = sheets["class_students"]
        assert "seat_no" in cs.columns
        assert int(cs.iloc[0]["seat_no"]) == 1


def test_full_round_trip_preserves_seat_no_and_attempts(app_ctx):
    from core.data_importer import FULL_CONFIRM_TOKEN

    app, admin_id, run_dir = app_ctx
    with app.app_context():
        _seed_roster_with_attempts()
        client = app.test_client()
        _login(client, admin_id)

        export = client.post("/db_maintenance", data={"action": "export_db", "mode": "full"})
        assert export.status_code == 200
        xlsx = run_dir / "full_roundtrip.xlsx"
        xlsx.write_bytes(export.data)

        inspector = inspect(db.engine)
        result = _run_full_clear(execute=True, table_names=inspector.get_table_names())
        assert not result.get("failed_tables")
        assert PracticeAttempt.query.count() == 0

        ok, msg = import_excel_to_db(str(xlsx), mode="full", confirm_full_clear=FULL_CONFIRM_TOKEN)
        assert ok, msg

        link = ClassStudent.query.filter_by(class_id=701, student_id=502).first()
        assert link is not None
        assert link.seat_no == 1
        assert PracticeAttempt.query.filter_by(student_id=502).count() == 3


def test_legacy_db_upgrade_adds_seat_no_and_practice_attempts(tmp_path):
    import config as _cfg

    db_path = tmp_path / "legacy.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password_hash TEXT,
            role TEXT DEFAULT 'student',
            email TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE classes (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            class_code TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE class_students (
            id INTEGER PRIMARY KEY,
            class_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            joined_at DATETIME
        );
        INSERT INTO users (id, username, password_hash, role) VALUES
            (1, 'admin_legacy', 'x', 'admin'),
            (2, 'teacher_legacy', 'x', 'teacher'),
            (3, 'student_legacy', 'x', 'student');
        INSERT INTO classes (id, name, teacher_id, class_code) VALUES (10, '舊班', 2, 'LEG00001');
        INSERT INTO class_students (id, class_id, student_id) VALUES (100, 10, 3);
        """
    )
    conn.commit()
    conn.close()

    prev = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        with app.app_context():
            conn = sqlite3.connect(db_path)
            cs_cols = [r[1] for r in conn.execute("PRAGMA table_info(class_students)")]
            pa_exists = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='practice_attempts'"
            ).fetchone()
            conn.close()
            assert "seat_no" in cs_cols
            assert pa_exists is not None

            conn = sqlite3.connect(db_path)
            assert conn.execute("SELECT COUNT(*) FROM users WHERE username='student_legacy'").fetchone()[0] == 1
            assert conn.execute("SELECT COUNT(*) FROM classes WHERE name='舊班'").fetchone()[0] == 1
            seat = conn.execute("SELECT seat_no FROM class_students WHERE id=100").fetchone()[0]
            conn.close()
            assert seat is None

            admin = User.query.filter_by(role="admin").first()
            teacher = User.query.filter_by(username="teacher_legacy").first()
            client = app.test_client()
            _login(client, admin.id)
            assert client.get("/db_maintenance").status_code == 200
            _login(client, teacher.id)
            assert client.get("/teacher/analysis").status_code == 200
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev
