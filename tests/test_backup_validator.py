# -*- coding: utf-8 -*-
"""Tests for export workbook validation and backup manifest."""
from __future__ import annotations

import io
import shutil
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from app import create_app
from core.backup.backup_registry import get_core_table_names
from core.backup.backup_validator import (
    BACKUP_FORMAT_VERSION,
    ExportValidationError,
    MANIFEST_SHEET,
    SUPPORTED_BACKUP_FORMAT_VERSION,
    build_and_validate_export,
    build_manifest_dataframe,
    collect_source_counts,
    count_dataframe_rows,
    ensure_dataframe_columns,
    parse_manifest_dataframe,
    validate_export_workbook,
    validate_legacy_workbook_structure,
    write_workbook_bytes,
)
from core.data_importer import import_excel_to_db
from core.practice_attempt_service import SOURCE_GENERAL_PRACTICE
from models import Class, ClassStudent, PracticeAttempt, SkillCurriculum, SkillInfo, User, db

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = PROJECT_ROOT / "reports" / "pytest_backup_validator"


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
    db_path = run_dir / "validator.db"
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


def _seed_unicode_fixture() -> dict:
    teacher = User(id=501, username="315001", password_hash="hash-keep", role="student", real_name="李家同")
    db.session.add(teacher)
    db.session.flush()
    clazz = Class(id=701, name="多三甲", teacher_id=501, class_code="VAL00001")
    db.session.add(clazz)
    db.session.flush()
    db.session.add(ClassStudent(id=801, class_id=701, student_id=501, seat_no=1))
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
            student_id=501,
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
            student_id=501,
            class_id=701,
            skill_id=skill,
            question_text="解 |x| < 2",
            user_answer="wrong",
            expected_answer="(-2,2)",
            is_correct=False,
            source=SOURCE_GENERAL_PRACTICE,
            problem_type_id=None,
            session_id=None,
            created_at=now,
        ),
    ])
    db.session.commit()
    return {"student_id": 501, "class_id": 701}


def test_core_export_has_all_expected_sheets_and_manifest(app_ctx):
    app, admin_id, _run = app_ctx
    with app.app_context():
        _seed_unicode_fixture()
        client = app.test_client()
        _login(client, admin_id)
        resp = client.post("/db_maintenance", data={"action": "export_db", "mode": "core"})
        assert resp.status_code == 200
        sheets = pd.read_excel(io.BytesIO(resp.data), sheet_name=None, engine="openpyxl")
        expected = get_core_table_names(include="export")
        for name in expected:
            assert name in sheets, f"missing sheet {name}"
        assert MANIFEST_SHEET in sheets


def test_practice_attempts_zero_rows_still_has_headers(app_ctx):
    app, admin_id, _run = app_ctx
    with app.app_context():
        _seed_unicode_fixture()
        PracticeAttempt.query.delete()
        db.session.commit()
        client = app.test_client()
        _login(client, admin_id)
        resp = client.post("/db_maintenance", data={"action": "export_db", "mode": "core"})
        assert resp.status_code == 200
        sheets = pd.read_excel(io.BytesIO(resp.data), sheet_name="practice_attempts", engine="openpyxl")
        cols = set(str(c) for c in sheets.columns)
        for required in (
            "id", "student_id", "class_id", "skill_id", "question_text",
            "user_answer", "expected_answer", "is_correct", "source", "created_at",
        ):
            assert required in cols
        assert count_dataframe_rows(sheets) == 0


def test_validator_detects_missing_sheet():
    frames = {"users": pd.DataFrame([{"id": 1, "username": "a", "role": "student", "real_name": "x"}])}
    manifest = build_manifest_dataframe(
        export_mode="core",
        expected_tables=["users", "practice_attempts"],
        source_counts={"users": 1, "practice_attempts": 0},
        exported_frames=frames,
        source_database_name="test.db",
        integrity_check="ok",
        foreign_key_check_rows=0,
    )
    payload = write_workbook_bytes(frames, manifest)
    report = validate_export_workbook(
        payload,
        expected_tables=["users", "practice_attempts"],
        source_counts={"users": 1, "practice_attempts": 0},
        export_mode="core",
        require_manifest=True,
    )
    assert not report.valid
    assert "practice_attempts" in report.missing_sheets


def test_validator_detects_missing_column():
    frames = {
        "class_students": pd.DataFrame([{"class_id": 1, "student_id": 2}]),
    }
    manifest = build_manifest_dataframe(
        export_mode="core",
        expected_tables=["class_students"],
        source_counts={"class_students": 1},
        exported_frames=frames,
        source_database_name="test.db",
        integrity_check="ok",
        foreign_key_check_rows=0,
    )
    payload = write_workbook_bytes(frames, manifest)
    report = validate_export_workbook(
        payload,
        expected_tables=["class_students"],
        source_counts={"class_students": 1},
        export_mode="core",
    )
    assert not report.valid
    assert "seat_no" in report.column_errors.get("class_students", [])


def test_validator_detects_row_count_mismatch():
    frames = {
        "users": pd.DataFrame([
            {"id": 1, "username": "a", "role": "student", "real_name": "x"},
            {"id": 2, "username": "b", "role": "student", "real_name": "y"},
        ]),
    }
    manifest = build_manifest_dataframe(
        export_mode="core",
        expected_tables=["users"],
        source_counts={"users": 1},
        exported_frames=frames,
        source_database_name="test.db",
        integrity_check="ok",
        foreign_key_check_rows=0,
    )
    payload = write_workbook_bytes(frames, manifest)
    report = validate_export_workbook(
        payload,
        expected_tables=["users"],
        source_counts={"users": 1},
        export_mode="core",
    )
    assert not report.valid
    assert "users" in report.row_count_errors


def test_manifest_parsed_correctly():
    manifest_df = build_manifest_dataframe(
        export_mode="core",
        expected_tables=["users"],
        source_counts={"users": 3},
        exported_frames={"users": pd.DataFrame(columns=["id", "username", "role", "real_name"])},
        source_database_name="kumon_math.db",
        integrity_check="ok",
        foreign_key_check_rows=0,
    )
    parsed = parse_manifest_dataframe(manifest_df)
    assert int(parsed["backup_format_version"]) == BACKUP_FORMAT_VERSION
    assert parsed["export_mode"] == "core"
    assert "users" in parsed["tables"]


def test_legacy_workbook_without_manifest_can_import(app_ctx, tmp_path):
    app, _admin_id, _run = app_ctx
    with app.app_context():
        _seed_unicode_fixture()
        xlsx = tmp_path / "legacy_no_manifest.xlsx"
        core_tables = get_core_table_names(include="export")
        with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
            pd.DataFrame([{
                "id": 501, "username": "315001", "password_hash": "hash-keep",
                "role": "student", "real_name": "李家同",
            }]).to_excel(w, sheet_name="users", index=False)
            pd.DataFrame([{"id": 701, "name": "多三甲", "teacher_id": 501, "class_code": "VAL00001"}]).to_excel(
                w, sheet_name="classes", index=False
            )
            pd.DataFrame([{"id": 801, "class_id": 701, "student_id": 501, "seat_no": 1}]).to_excel(
                w, sheet_name="class_students", index=False
            )
            for name in core_tables:
                if name not in ("users", "classes", "class_students"):
                    pd.DataFrame().to_excel(w, sheet_name=name, index=False)
        report = validate_legacy_workbook_structure(
            xlsx.read_bytes(),
            expected_tables=core_tables,
            source_counts={},
        )
        assert report.legacy_backup
        ok, msg = import_excel_to_db(str(xlsx), mode="core")
        assert ok, msg


def test_unsupported_manifest_version_rejects_import(app_ctx, tmp_path):
    app, _admin_id, _run = app_ctx
    with app.app_context():
        xlsx = tmp_path / "future_manifest.xlsx"
        with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
            pd.DataFrame([{"id": 1, "username": "a", "password_hash": "h", "role": "student"}]).to_excel(
                w, sheet_name="users", index=False
            )
            pd.DataFrame([
                {"section": "meta", "key": "backup_format_version", "value": str(SUPPORTED_BACKUP_FORMAT_VERSION + 3)},
            ]).to_excel(w, sheet_name=MANIFEST_SHEET, index=False)
        ok, msg = import_excel_to_db(str(xlsx), mode="core")
        assert not ok
        assert "較新版本" in msg


def test_unicode_boolean_datetime_null_round_trip(app_ctx, tmp_path):
    app, admin_id, run_dir = app_ctx
    with app.app_context():
        _seed_unicode_fixture()
        client = app.test_client()
        _login(client, admin_id)
        export = client.post("/db_maintenance", data={"action": "export_db", "mode": "core"})
        assert export.status_code == 200
        xlsx = run_dir / "unicode_roundtrip.xlsx"
        xlsx.write_bytes(export.data)

        sheets = pd.read_excel(xlsx, sheet_name=None, engine="openpyxl")
        users = sheets["users"]
        assert users[users["username"].astype(str) == "315001"].iloc[0]["real_name"] == "李家同"
        cs = sheets["class_students"]
        assert int(cs.iloc[0]["seat_no"]) == 1
        pa = sheets["practice_attempts"].sort_values("id")
        assert len(pa) == 2
        assert pa.iloc[0]["question_text"] == "解 |x| = 3"
        assert bool(pa.iloc[0]["is_correct"]) is True
        assert pa.iloc[1]["user_answer"] == "wrong"
        assert pd.isna(pa.iloc[1]["problem_type_id"]) or pa.iloc[1]["problem_type_id"] in ("", None)

        PracticeAttempt.query.delete()
        User.query.filter_by(username="315001").delete()
        db.session.commit()

        ok, msg = import_excel_to_db(str(xlsx), mode="core")
        assert ok, msg
        user = User.query.filter_by(username="315001").first()
        assert user.real_name == "李家同"
        link = ClassStudent.query.filter_by(student_id=user.id).first()
        assert link.seat_no == 1
        attempts = PracticeAttempt.query.filter_by(student_id=user.id).order_by(PracticeAttempt.id).all()
        assert len(attempts) == 2
        assert attempts[0].is_correct is True
        assert attempts[1].is_correct is False
        assert attempts[1].problem_type_id is None
        assert attempts[1].session_id is None


def test_validation_failure_blocks_download(app_ctx):
    app, admin_id, _run = app_ctx
    with app.app_context():
        _seed_unicode_fixture()
        client = app.test_client()
        _login(client, admin_id)
        expected = get_core_table_names(include="export")
        frames = {"users": pd.DataFrame([{"id": 1, "username": "a", "role": "student", "real_name": "x"}])}
        source_counts = collect_source_counts(db.engine, expected)
        with pytest.raises(ExportValidationError):
            build_and_validate_export(
                mode="core",
                engine=db.engine,
                frames=frames,
                expected_tables=expected,
                source_counts=source_counts,
                source_database_name="validator.db",
            )


def test_ensure_dataframe_columns_from_model(app_ctx):
    app, _admin_id, _run = app_ctx
    with app.app_context():
        empty = ensure_dataframe_columns("practice_attempts", pd.DataFrame(), db.engine)
        assert "seat_no" not in empty.columns
        assert "student_id" in empty.columns
        assert "question_text" in empty.columns
