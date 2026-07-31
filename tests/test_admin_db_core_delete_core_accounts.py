# -*- coding: utf-8 -*-
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import pytest
from sqlalchemy import text

from app import create_app
from core.backup.backup_registry import get_core_account_clear_specs
from core.models.prompt_template import PromptTemplate
from core.routes.admin import CORE_CLEAR_CONFIRM_TOKEN, _hard_clear_vocational_math_b_core
from models import Class, ClassStudent, Progress, QuizAttempt, SkillCurriculum, SkillInfo, SystemSetting, TextbookExample, User, db

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = PROJECT_ROOT / "reports" / "pytest_core_delete_core_students"


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def app_ctx():
    import config as _cfg

    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    run_dir = TEST_ROOT / uuid.uuid4().hex[:10]
    run_dir.mkdir(parents=True, exist_ok=True)
    db_path = run_dir / "delete_core_students.db"
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


def _seed():
    teacher = User(id=501, username="teacher_keep", password_hash="h", role="teacher")
    student = User(id=502, username="student_drop", password_hash="h", role="student")
    student2 = User(id=503, username="student_drop2", password_hash="h", role="student")
    db.session.add_all([teacher, student, student2])
    db.session.flush()
    # Teacher-owned progress row must survive student-scoped deletes.
    db.session.add(Progress(user_id=501, skill_id="vh_數學B1_KeepTeacherProg", consecutive_correct=1, questions_solved=1))
    db.session.add(Progress(user_id=502, skill_id="vh_數學B1_StudentProg", consecutive_correct=2, questions_solved=2))
    db.session.add(Class(id=701, name="甲班", teacher_id=501, class_code="STUCLR01"))
    db.session.flush()
    db.session.add(ClassStudent(id=801, class_id=701, student_id=502))
    sid = "vh_數學B1_DeleteCoreStudentOnly"
    db.session.add(SkillInfo(skill_id=sid, skill_en_name="e", skill_ch_name="c", description="d", gemini_prompt="p"))
    db.session.add(
        SkillCurriculum(
            skill_id=sid,
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
            skill_id=sid,
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
    setting = SystemSetting(key=f"keep_sys_{uuid.uuid4().hex[:6]}", value="keep")
    prompt = PromptTemplate(
        prompt_key=f"keep_p_{uuid.uuid4().hex[:6]}",
        title="t",
        category="c",
        content="x",
        default_content="x",
    )
    db.session.add_all([setting, prompt])
    db.session.commit()
    return {
        "admin_count": User.query.filter_by(role="admin").count(),
        "teacher_count": User.query.filter_by(role="teacher").count(),
        "student_count": User.query.filter_by(role="student").count(),
        "settings_before": SystemSetting.query.count(),
        "prompts_before": PromptTemplate.query.count(),
        "setting_key": setting.key,
        "prompt_key": prompt.prompt_key,
        "skill_id": sid,
    }


def test_preview_counts_students_only_for_users(app_ctx):
    app, admin_id, _ = app_ctx
    with app.app_context():
        seeded = _seed()
        client = app.test_client()
        _login(client, admin_id)
        r = client.post(
            "/db_maintenance",
            data={"action": "preview_core_clear", "mode": "core", "core_scope_mode": "all"},
            follow_redirects=True,
        )
        body = r.get_data(as_text=True)
        assert r.status_code == 200
        assert f"users(student)={seeded['student_count']}" in body
        assert User.query.filter_by(role="admin").count() == seeded["admin_count"]
        assert User.query.filter_by(role="teacher").count() == seeded["teacher_count"]
        assert User.query.filter_by(role="student").count() == seeded["student_count"]


def test_execute_deletes_students_keeps_admin_teacher(app_ctx):
    app, admin_id, _ = app_ctx
    with app.app_context():
        seeded = _seed()
        before_admin = User.query.filter_by(role="admin").count()
        before_teacher = User.query.filter_by(role="teacher").count()
        before_student = User.query.filter_by(role="student").count()
        assert before_student >= 2
        assert before_teacher >= 1
        assert before_admin >= 1

        preview = _hard_clear_vocational_math_b_core(execute=False)
        plan = preview["plan"]
        assert plan.index("class_students") < plan.index("classes") < plan.index("users")
        wheres = {item["table"]: item["where"] for item in preview["account_clear"]}
        assert wheres["users"] == "role = 'student'"
        assert wheres["classes"] == "1=1"
        assert wheres["class_students"] == "1=1"
        assert "role = 'student'" in wheres["progress"]

        result = _hard_clear_vocational_math_b_core(execute=True)
        assert result["deleted"]["users"] == before_student
        assert User.query.filter_by(role="student").count() == 0
        assert User.query.filter_by(role="admin").count() == before_admin
        assert User.query.filter_by(role="teacher").count() == before_teacher
        assert Class.query.count() == 0
        assert ClassStudent.query.count() == 0
        assert Progress.query.filter_by(user_id=502).count() == 0
        assert Progress.query.filter_by(user_id=501).count() == 1
        assert SystemSetting.query.count() == seeded["settings_before"]
        assert PromptTemplate.query.count() == seeded["prompts_before"]
        db.session.execute(text("PRAGMA foreign_keys = ON"))
        assert db.session.execute(text("PRAGMA foreign_key_check")).fetchall() == []


def test_wrong_confirm_does_not_execute(app_ctx):
    app, admin_id, _ = app_ctx
    with app.app_context():
        seeded = _seed()
        client = app.test_client()
        _login(client, admin_id)
        r = client.post(
            "/db_maintenance",
            data={
                "action": "clear_all_data",
                "mode": "core",
                "core_scope_mode": "all",
                "core_clear_confirm": "WRONG",
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert User.query.filter_by(role="student").count() == seeded["student_count"]
        assert Class.query.count() == 1


def test_admin_session_survives_delete_core(app_ctx):
    app, admin_id, _ = app_ctx
    with app.app_context():
        _seed()
        client = app.test_client()
        _login(client, admin_id)
        r = client.post(
            "/db_maintenance",
            data={
                "action": "clear_all_data",
                "mode": "core",
                "core_scope_mode": "all",
                "core_clear_confirm": CORE_CLEAR_CONFIRM_TOKEN,
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        body = r.get_data(as_text=True)
        assert "DELETE_CORE 完成" in body
        assert "管理員與教師帳號" in body or "已保留" in body
        with client.session_transaction() as sess:
            assert sess.get("_user_id") == str(admin_id)
        assert db.session.get(User, admin_id) is not None
        assert db.session.get(User, admin_id).role == "admin"


def test_template_student_only_warning():
    text_out = (PROJECT_ROOT / "templates" / "db_maintenance.html").read_text(encoding="utf-8")
    assert "全部國中、普通高中及高職教材資料" in text_out
    assert "system_settings、prompt_templates 將保留" in text_out


def test_account_clear_specs_have_no_users_full_mode():
    for spec in get_core_account_clear_specs():
        assert spec.clear_mode != "full"
        if spec.table_name == "users":
            assert spec.clear_mode == "users_students"
