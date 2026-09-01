from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from core.vocational_student_home import (
    build_vocational_home_context,
    is_vocational_student,
)
from models import (
    Class,
    ClassStudent,
    PracticeAttempt,
    Progress,
    SkillCurriculum,
    SkillInfo,
    User,
    db,
)


@pytest.fixture()
def app_ctx():
    import config as _cfg

    db_path = Path("reports") / f"pytest_voc_home_{uuid.uuid4().hex[:8]}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            yield app
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        try:
            if db_path.exists():
                db_path.unlink()
        except OSError:
            pass


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _seed_users(app):
    teacher = User(
        username=f"t_{uuid.uuid4().hex[:6]}",
        password_hash="x",
        role="teacher",
        real_name="王老師",
    )
    voc = User(
        username="315001",
        password_hash="x",
        role="student",
        real_name="李家同",
        curriculum_code="vocational",
    )
    voc_no_name = User(
        username="315099",
        password_hash="x",
        role="student",
        curriculum_code="vocational",
    )
    voc_no_class = User(
        username="315088",
        password_hash="x",
        role="student",
        real_name="NoClassStu",
        curriculum_code="vocational",
    )
    jh = User(
        username="jh_stu",
        password_hash="x",
        role="student",
        real_name="國中生",
        curriculum_code="junior_high",
    )
    admin = User(
        username=f"a_{uuid.uuid4().hex[:6]}",
        password_hash="x",
        role="admin",
        real_name="系統管理員",
    )
    db.session.add_all([teacher, voc, voc_no_name, voc_no_class, jh, admin])
    db.session.commit()
    cls = Class(name="多三甲", teacher_id=teacher.id, class_code="ABC12345")
    db.session.add(cls)
    db.session.commit()
    db.session.add(ClassStudent(class_id=cls.id, student_id=voc.id, seat_no=1))
    db.session.add(ClassStudent(class_id=cls.id, student_id=voc_no_name.id, seat_no=2))
    db.session.commit()
    skill = SkillInfo(
        skill_id="vh_數學B1_AbsoluteValueInequality",
        skill_en_name="abs ineq",
        skill_ch_name="絕對值不等式",
        description="d",
        gemini_prompt="p",
        is_active=True,
    )
    db.session.add(skill)
    db.session.add(
        SkillCurriculum(
            skill_id=skill.skill_id,
            curriculum="vocational",
            grade=10,
            volume="數學B1",
            chapter="第一章 數與式",
            section="1-3",
            display_order=1,
        )
    )
    db.session.commit()
    return {
        "teacher": teacher,
        "voc": voc,
        "voc_no_name": voc_no_name,
        "voc_no_class": voc_no_class,
        "jh": jh,
        "admin": admin,
    }


def test_vocational_home_hides_curriculum_switch_and_shows_identity(app_ctx):
    app = app_ctx
    with app.app_context():
        users = _seed_users(app)
        client = app.test_client()
        _login(client, users["voc"].id)
        html = client.get("/dashboard").get_data(as_text=True)
        assert "歡迎回來，李家同" in html
        assert "多三甲" in html
        assert "座號 1" in html
        assert "315001" in html
        assert ">國中<" not in html
        assert ">普高<" not in html
        assert "繼續學習" in html
        assert "開始你的第一次練習" in html
        assert "/practice/vh_數學B1_AbsoluteValueInequality" not in html


def test_real_name_fallback_username(app_ctx):
    app = app_ctx
    with app.app_context():
        users = _seed_users(app)
        client = app.test_client()
        _login(client, users["voc_no_name"].id)
        html = client.get("/dashboard").get_data(as_text=True)
        assert "歡迎回來，315099" in html
        assert "多三甲" in html
        assert "NoClassStu" not in html


def test_no_class_does_not_error(app_ctx):
    app = app_ctx
    with app.app_context():
        users = _seed_users(app)
        no_class = users["voc_no_class"]
        ctx = build_vocational_home_context(no_class)
        assert ctx["display_name"] == "NoClassStu"
        assert ctx["class_rows"] == []
        assert ctx["primary_class_name"] == ""

        client = app.test_client()
        _login(client, no_class.id)
        resp = client.get("/dashboard")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "NoClassStu" in html
        assert "315088" in html
        assert "尚未加入班級" in html
        assert "多三甲" not in html
        assert "vhome-hero" in html


def test_continue_learning_from_practice_attempts(app_ctx):
    app = app_ctx
    with app.app_context():
        users = _seed_users(app)
        db.session.add(
            PracticeAttempt(
                student_id=users["voc"].id,
                skill_id="vh_數學B1_AbsoluteValueInequality",
                is_correct=True,
                source="practice",
                created_at=datetime.utcnow(),
            )
        )
        db.session.commit()
        client = app.test_client()
        _login(client, users["voc"].id)
        html = client.get("/dashboard").get_data(as_text=True)
        skill_id = "vh_數學B1_AbsoluteValueInequality"
        assert "絕對值不等式" in html
        assert "AbsoluteValueInequality" in html
        assert "繼續練習" in html
        assert quote(skill_id, safe="") in html or f"/practice/{skill_id}" in html
        assert "本週練習題數" in html


def test_progress_fallback_when_no_attempts(app_ctx):
    app = app_ctx
    with app.app_context():
        users = _seed_users(app)
        db.session.add(
            Progress(
                user_id=users["voc"].id,
                skill_id="vh_數學B1_AbsoluteValueInequality",
                last_practiced=datetime.utcnow(),
            )
        )
        db.session.commit()
        ctx = build_vocational_home_context(users["voc"])
        assert ctx["continue_learning"]["source"] == "progress"
        assert ctx["continue_learning"]["skill_id"] == "vh_數學B1_AbsoluteValueInequality"


def test_weekly_stats_accuracy(app_ctx):
    app = app_ctx
    with app.app_context():
        users = _seed_users(app)
        now = datetime.utcnow()
        db.session.add_all(
            [
                PracticeAttempt(
                    student_id=users["voc"].id,
                    skill_id="vh_數學B1_AbsoluteValueInequality",
                    is_correct=True,
                    source="practice",
                    created_at=now,
                ),
                PracticeAttempt(
                    student_id=users["voc"].id,
                    skill_id="vh_數學B1_AbsoluteValueInequality",
                    is_correct=False,
                    source="practice",
                    created_at=now,
                ),
                PracticeAttempt(
                    student_id=users["voc"].id,
                    skill_id="vh_數學B1_AbsoluteValueInequality",
                    is_correct=True,
                    source="practice",
                    created_at=now - timedelta(days=10),
                ),
            ]
        )
        db.session.commit()
        stats = build_vocational_home_context(users["voc"])["weekly_stats"]
        assert stats["week_count"] == 2
        assert stats["week_correct_rate"] == 50


def test_junior_and_teacher_keep_old_dashboard(app_ctx):
    app = app_ctx
    with app.app_context():
        users = _seed_users(app)
        client = app.test_client()
        _login(client, users["jh"].id)
        html = client.get("/dashboard").get_data(as_text=True)
        assert "國中" in html
        assert "普高" in html
        assert "技高" in html
        assert "歡迎回來，李家同" not in html
        assert not is_vocational_student(users["teacher"])
        assert not is_vocational_student(users["admin"])
        _login(client, users["teacher"].id)
        thtml = client.get("/dashboard").get_data(as_text=True)
        assert "國中" in thtml
        assert "繼續學習" not in thtml or "學習儀表板" in thtml
        _login(client, users["admin"].id)
        ahtml = client.get("/dashboard").get_data(as_text=True)
        assert "學習儀表板" in ahtml
        assert "vhome-hero" not in ahtml
