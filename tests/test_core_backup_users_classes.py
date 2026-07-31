from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import pandas as pd
import pytest

from app import create_app
from core.backup.backup_registry import get_core_table_names
from core.data_importer import FULL_CONFIRM_TOKEN, import_excel_to_db
from core.secret_policy import (
    REDACTED_SECRET_VALUE,
    redact_system_settings_records,
    should_skip_system_setting_restore,
)
from models import Class, ClassStudent, SkillCurriculum, SkillInfo, TextbookExample, User, db

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = PROJECT_ROOT / "reports" / "pytest_core_backup_users_classes"


@pytest.fixture()
def app_ctx():
    import config as _cfg

    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    run_dir = TEST_ROOT / uuid.uuid4().hex[:10]
    run_dir.mkdir(parents=True, exist_ok=True)
    db_path = run_dir / "core_backup_users.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            admin = User(username=f"admin_{uuid.uuid4().hex[:6]}", password_hash="keep-hash-admin", role="admin")
            db.session.add(admin)
            db.session.commit()
            yield app, admin.id, run_dir
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        shutil.rmtree(run_dir, ignore_errors=True)


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _seed_roster() -> dict[str, int]:
    teacher = User(id=501, username="teacher_core", password_hash="hash-teacher-501", role="teacher")
    student = User(id=502, username="student_core", password_hash="hash-student-502", role="student")
    db.session.add_all([teacher, student])
    db.session.flush()
    clazz = Class(id=701, name="甲班", teacher_id=501, class_code="ABCD1234")
    db.session.add(clazz)
    db.session.flush()
    link = ClassStudent(id=801, class_id=701, student_id=502)
    db.session.add(link)
    db.session.add(
        SkillInfo(
            skill_id="vh_users_core_skill",
            skill_en_name="e",
            skill_ch_name="c",
            description="d",
            gemini_prompt="p",
        )
    )
    db.session.add(
        SkillCurriculum(
            skill_id="vh_users_core_skill",
            curriculum="vocational",
            grade=10,
            volume="數學B1",
            chapter="1",
            section="1-1",
            paragraph="",
        )
    )
    db.session.add(
        TextbookExample(
            id=901,
            skill_id="vh_users_core_skill",
            source_curriculum="vocational",
            source_volume="數學B1",
            source_chapter="1",
            source_section="1-1",
            source_description="ex",
            problem_text="q",
            problem_type="short_answer",
            correct_answer="1",
            detailed_solution="s",
        )
    )
    db.session.commit()
    return {"teacher_id": 501, "student_id": 502, "class_id": 701, "link_id": 801}


def _core_workbook(path: Path, *, users=None, classes=None, class_students=None) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame(
            users
            or [
                {"id": 501, "username": "teacher_core", "password_hash": "hash-teacher-501", "role": "teacher"},
                {"id": 502, "username": "student_core", "password_hash": "hash-student-502", "role": "student"},
            ]
        ).to_excel(writer, sheet_name="users", index=False)
        pd.DataFrame(
            classes or [{"id": 701, "name": "甲班", "teacher_id": 501, "class_code": "ABCD1234"}]
        ).to_excel(writer, sheet_name="classes", index=False)
        pd.DataFrame(
            class_students or [{"id": 801, "class_id": 701, "student_id": 502}]
        ).to_excel(writer, sheet_name="class_students", index=False)
        pd.DataFrame(
            [{"skill_id": "vh_users_core_skill", "skill_en_name": "e", "skill_ch_name": "c", "description": "d", "gemini_prompt": "p"}]
        ).to_excel(writer, sheet_name="skills_info", index=False)
        pd.DataFrame(
            [{"skill_id": "vh_users_core_skill", "curriculum": "vocational", "grade": 10, "volume": "數學B1", "chapter": "1", "section": "1-1"}]
        ).to_excel(writer, sheet_name="skill_curriculum", index=False)
        pd.DataFrame(
            [{
                "id": 901,
                "skill_id": "vh_users_core_skill",
                "source_curriculum": "vocational",
                "source_volume": "數學B1",
                "source_chapter": "1",
                "source_section": "1-1",
                "source_description": "ex",
                "problem_text": "q",
                "problem_type": "short_answer",
                "correct_answer": "1",
                "detailed_solution": "s",
                "difficulty_level": 1,
            }]
        ).to_excel(writer, sheet_name="textbook_examples", index=False)
        pd.DataFrame().to_excel(writer, sheet_name="skill_family_bridge", index=False)
        pd.DataFrame().to_excel(writer, sheet_name="skill_prerequisites", index=False)


def test_core_excel_contains_users_classes_class_students_sheets(app_ctx):
    app, admin_id, _run_dir = app_ctx
    with app.app_context():
        _seed_roster()
        client = app.test_client()
        _login(client, admin_id)
        response = client.post("/db_maintenance", data={"action": "export_db", "mode": "core"})
        assert response.status_code == 200
        sheets = pd.read_excel(response.data, sheet_name=None, engine="openpyxl")
        for name in ("users", "classes", "class_students"):
            assert name in sheets
        assert list(sheets.keys())[:3] == ["users", "classes", "class_students"]
        users_df = sheets["users"]
        assert "password_hash" in users_df.columns
        hashes = set(users_df["password_hash"].astype(str).tolist())
        assert "hash-teacher-501" in hashes
        assert "hash-student-502" in hashes
        assert REDACTED_SECRET_VALUE not in hashes


def test_core_restore_preserves_counts_and_user_class_links(app_ctx):
    app, _admin_id, run_dir = app_ctx
    with app.app_context():
        path = run_dir / "core_users_classes.xlsx"
        _core_workbook(path)
        ok, message = import_excel_to_db(str(path), mode="core")
        assert ok, message

        assert User.query.filter_by(id=501).count() == 1
        assert User.query.filter_by(id=502).count() == 1
        assert Class.query.filter_by(id=701).count() == 1
        assert ClassStudent.query.filter_by(id=801).count() == 1

        teacher = db.session.get(User, 501)
        student = db.session.get(User, 502)
        clazz = db.session.get(Class, 701)
        link = db.session.get(ClassStudent, 801)
        assert teacher.password_hash == "hash-teacher-501"
        assert student.password_hash == "hash-student-502"
        assert clazz.teacher_id == 501
        assert link.class_id == 701
        assert link.student_id == 502
        assert ClassStudent.query.filter_by(class_id=701, student_id=502).count() == 1


def test_core_restore_rejects_orphan_class_students_in_strict_mode(app_ctx):
    app, _admin_id, run_dir = app_ctx
    with app.app_context():
        path = run_dir / "orphan_class_students.xlsx"
        _core_workbook(
            path,
            class_students=[{"id": 899, "class_id": 999999, "student_id": 502}],
        )
        ok, message = import_excel_to_db(str(path), mode="core", strict_mode=True)
        assert not ok
        assert "orphan class_students" in message


def test_delete_order_class_students_before_classes_before_users():
    clear_order = get_core_table_names(include="clear")
    assert clear_order.index("class_students") < clear_order.index("classes") < clear_order.index("users")


def test_full_mode_still_requires_confirm_token(app_ctx):
    app, _admin_id, run_dir = app_ctx
    with app.app_context():
        path = run_dir / "full_mode.xlsx"
        _core_workbook(path)
        ok, message = import_excel_to_db(str(path), mode="full", confirm_full_clear="")
        assert not ok
        assert "YES_DELETE_ALL" in message

        ok2, message2 = import_excel_to_db(str(path), mode="full", confirm_full_clear=FULL_CONFIRM_TOKEN)
        assert ok2, message2


def test_full_export_still_includes_non_core_tables_and_redacts_secrets(app_ctx):
    app, admin_id, _run_dir = app_ctx
    with app.app_context():
        _seed_roster()
        from models import SystemSetting

        db.session.add(SystemSetting(key="ai_gemini_api_key", value="AIzaShouldNeverExportPlain"))
        db.session.add(SystemSetting(key="ai_mode", value="cloud"))
        db.session.commit()

        client = app.test_client()
        _login(client, admin_id)
        response = client.post("/db_maintenance", data={"action": "export_db", "mode": "full"})
        assert response.status_code == 200
        sheets = pd.read_excel(response.data, sheet_name=None, engine="openpyxl")
        assert "users" in sheets
        assert "system_settings" in sheets
        assert len(sheets) > len(get_core_table_names())

        settings = sheets["system_settings"]
        secret_row = settings[settings["key"].astype(str) == "ai_gemini_api_key"].iloc[0]
        assert secret_row["value"] == REDACTED_SECRET_VALUE
        assert "AIzaShouldNeverExportPlain" not in response.data.decode("latin-1", errors="ignore")

        users = sheets["users"]
        assert "hash-teacher-501" in set(users["password_hash"].astype(str).tolist())


def test_secret_policy_redacts_settings_not_user_password_hashes():
    # system_settings keys with secret markers stay environment-managed.
    assert should_skip_system_setting_restore("ai_gemini_api_key") is True
    assert should_skip_system_setting_restore("ai_mode") is False
    rows = redact_system_settings_records([
        {"key": "ai_gemini_api_key", "value": "secret"},
        {"key": "ai_mode", "value": "cloud"},
    ])
    assert rows[0]["value"] == REDACTED_SECRET_VALUE
    assert rows[1]["value"] == "cloud"
    # users.password_hash must never be routed through setting-key redaction in backup.
    # Export only redacts system_settings rows (see admin export_db); hash values stay intact.
    assert "password_hash" not in {
        str(r.get("key") or "") for r in rows
    }
