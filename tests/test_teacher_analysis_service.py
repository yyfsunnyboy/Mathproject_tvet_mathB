# -*- coding: utf-8 -*-
"""Tests for teacher analysis service and routes."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest

from app import create_app
from core.teacher_analysis_service import (
    LEARNING_TIME_UNAVAILABLE,
    STATUS_ATTENTION,
    STATUS_LOW_SAMPLE,
    STATUS_NO_DATA,
    STATUS_NORMAL,
    STATUS_WATCH,
    build_analysis_page_context,
    calculate_learning_status,
    format_accuracy,
    format_learning_time,
    get_class_for_user,
    get_student_units,
    get_student_unit_detail,
    parse_time_range,
    student_display_name,
    teacher_analysis_authorized,
    verify_student_in_class,
)
from models import (
    AdaptiveLearningLog,
    B4Chap2VisibilityAuditLog,
    Class,
    ClassStudent,
    SkillCurriculum,
    SkillFamilyBridge,
    SkillInfo,
    User,
    db,
)


@pytest.fixture()
def app_ctx(tmp_path):
    import config as _cfg

    db_path = tmp_path / f"pytest_teacher_analysis_{uuid.uuid4().hex[:8]}.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            _seed_fixture_data()
            yield app
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri


def _seed_fixture_data() -> None:
    teacher = User(id=101, username="teacher_a", password_hash="x", role="teacher")
    other_teacher = User(id=102, username="teacher_b", password_hash="x", role="teacher")
    admin = User(id=103, username="admin_user", password_hash="x", role="admin")
    s1 = User(id=201, username="stu001", password_hash="x", role="student", real_name="王小明")
    s2 = User(id=202, username="stu002", password_hash="x", role="student")
    s3 = User(id=203, username="stu003", password_hash="x", role="student")
    outsider = User(id=204, username="outsider", password_hash="x", role="student")

    cls_a = Class(id=1, name="一年甲班", teacher_id=101, class_code="AAAA1111")
    cls_b = Class(id=2, name="一年乙班", teacher_id=102, class_code="BBBB2222")

    db.session.add_all([teacher, other_teacher, admin, s1, s2, s3, outsider, cls_a, cls_b])
    db.session.add_all([
        ClassStudent(class_id=1, student_id=201),
        ClassStudent(class_id=1, student_id=202),
        ClassStudent(class_id=2, student_id=203),
    ])

    skill_mapped = "vh_數學B4_ProbabilityDefinition"
    skill_unmapped = "vh_數學B4_OrphanSkill"
    db.session.add(SkillInfo(
        skill_id=skill_mapped,
        skill_en_name="ProbDef",
        skill_ch_name="概率的定義",
        description="d",
        gemini_prompt="p",
    ))
    db.session.add(SkillInfo(
        skill_id=skill_unmapped,
        skill_en_name="Orphan",
        skill_ch_name="孤立技能",
        description="d",
        gemini_prompt="p",
    ))
    db.session.add(SkillCurriculum(
        skill_id=skill_mapped,
        curriculum="vocational",
        grade=1,
        volume="數學B4",
        chapter="2 概率",
        section="2-2 概率的運算",
        display_order=1,
    ))
    db.session.add(SkillFamilyBridge(
        skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers",
        family_id="I1",
        skill_name="int",
        family_name="int_add",
        subskill_nodes='["a"]',
    ))

    now = datetime.utcnow()
    for i in range(12):
        db.session.add(B4Chap2VisibilityAuditLog(
            record_kind="deterministic_answer",
            student_id=201,
            skill_id=skill_mapped,
            problem_type_id="classical_probability_fraction",
            user_answer="1/2",
            expected_answer="1/2",
            is_correct=(i < 8),
            created_at=now - timedelta(days=i % 5),
        ))
    db.session.add(B4Chap2VisibilityAuditLog(
        record_kind="deterministic_answer",
        student_id=201,
        skill_id=skill_unmapped,
        problem_type_id="orphan_type",
        user_answer="x",
        expected_answer="y",
        is_correct=False,
        created_at=now,
    ))
    for i in range(5):
        db.session.add(AdaptiveLearningLog(
            student_id=201,
            session_id="sess-1",
            step_number=i + 1,
            target_family_id="I1",
            target_subskills='["sign"]',
            is_correct=(i < 2),
            current_apr=0.55,
            ppo_strategy=0,
            execution_latency=1,
            created_at=now - timedelta(hours=i),
        ))
    db.session.add(AdaptiveLearningLog(
        student_id=201,
        session_id="sess-2",
        step_number=1,
        target_family_id="B4_F1",
        target_subskills='["x"]',
        is_correct=False,
        current_apr=0.40,
        ppo_strategy=0,
        execution_latency=0,
        created_at=now,
    ))
    db.session.add(B4Chap2VisibilityAuditLog(
        record_kind="deterministic_answer",
        student_id=204,
        skill_id=skill_mapped,
        problem_type_id="t",
        user_answer="a",
        expected_answer="b",
        is_correct=False,
        created_at=now,
    ))
    db.session.commit()


class TestCalculateLearningStatus:
    def test_no_data(self):
        r = calculate_learning_status(0, 0)
        assert r["status"] == STATUS_NO_DATA

    def test_low_sample(self):
        r = calculate_learning_status(6, 4)
        assert r["status"] == STATUS_LOW_SAMPLE

    def test_attention(self):
        r = calculate_learning_status(18, 7)
        assert r["status"] == STATUS_ATTENTION

    def test_watch(self):
        r = calculate_learning_status(20, 13)
        assert r["status"] == STATUS_WATCH

    def test_normal(self):
        r = calculate_learning_status(20, 16)
        assert r["status"] == STATUS_NORMAL

    def test_divide_by_zero_safe(self):
        r = calculate_learning_status(0, 0)
        assert r["status"] == STATUS_NO_DATA


class TestHelpers:
    def test_format_accuracy_none(self):
        assert format_accuracy(None) == "—"

    def test_format_accuracy_value(self):
        assert format_accuracy(0.786) == "79%"

    def test_learning_time_unavailable(self):
        assert format_learning_time() == "—"
        assert LEARNING_TIME_UNAVAILABLE == "—"

    def test_student_display_name_real_name(self):
        u = User(username="x", real_name="  張三  ")
        assert student_display_name(u) == "張三"

    def test_student_display_name_fallback_username(self):
        u = User(username="stu002")
        assert student_display_name(u) == "stu002"


class TestAuthorization:
    def test_teacher_authorized(self, app_ctx):
        app = app_ctx
        with app.app_context():
            assert teacher_analysis_authorized(db.session.get(User, 101)) is True
            assert teacher_analysis_authorized(db.session.get(User, 103)) is True
            assert teacher_analysis_authorized(db.session.get(User, 201)) is False

    def test_teacher_ownership(self, app_ctx):
        app = app_ctx
        with app.app_context():
            assert get_class_for_user(1, db.session.get(User, 101)) is not None
            assert get_class_for_user(1, db.session.get(User, 102)) is None

    def test_admin_sees_all_classes(self, app_ctx):
        app = app_ctx
        with app.app_context():
            admin = db.session.get(User, 103)
            assert get_class_for_user(1, admin) is not None
            assert get_class_for_user(2, admin) is not None

    def test_verify_student_in_class(self, app_ctx):
        app = app_ctx
        with app.app_context():
            assert verify_student_in_class(201, 1) is True
            assert verify_student_in_class(203, 1) is False


class TestServiceAggregations:
    def test_student_overview_includes_unmapped_adaptive(self, app_ctx):
        app = app_ctx
        with app.app_context():
            ctx = build_analysis_page_context(
                db.session.get(User, 101),
                class_id=1,
                student_id=201,
                volume=None,
                chapter=None,
                skill_unit=None,
                time_range=parse_time_range("all"),
            )
            stats = ctx["student_overview"]["stats"]
            assert stats.total == 19

    def test_unit_grouping_volume_chapter(self, app_ctx):
        app = app_ctx
        with app.app_context():
            units = get_student_units(201, parse_time_range("all"))
            labels = [u["unit_label"] for u in units]
            assert any("數學B4" in lb and "概率" in lb for lb in labels)

    def test_unmapped_skill_separate_unit(self, app_ctx):
        app = app_ctx
        with app.app_context():
            units = get_student_units(201, parse_time_range("all"))
            orphan = next(u for u in units if u.get("kind") == "skill" and u.get("skill_id") == "vh_數學B4_OrphanSkill")
            assert orphan["unit_label"] == "孤立技能"

    def test_adaptive_unmapped_excluded_from_unit_detail(self, app_ctx):
        app = app_ctx
        with app.app_context():
            detail = get_student_unit_detail(
                201,
                volume="數學B4",
                chapter="2 概率",
                skill_unit=None,
                time_range=parse_time_range("all"),
            )
            assert detail["stats"].total == 12

    def test_time_filter_reduces_counts(self, app_ctx):
        app = app_ctx
        with app.app_context():
            all_stats = build_analysis_page_context(
                db.session.get(User, 101),
                class_id=1,
                student_id=201,
                volume=None,
                chapter=None,
                skill_unit=None,
                time_range=parse_time_range("all"),
            )["student_overview"]["stats"]
            today_stats = build_analysis_page_context(
                db.session.get(User, 101),
                class_id=1,
                student_id=201,
                volume=None,
                chapter=None,
                skill_unit=None,
                time_range=parse_time_range("today"),
            )["student_overview"]["stats"]
            assert today_stats.total <= all_stats.total


class TestRoutes:
    def _login(self, client, user_id: int):
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user_id)
            sess["_fresh"] = True

    def test_home_200_teacher(self, app_ctx):
        app = app_ctx
        client = app.test_client()
        self._login(client, 101)
        resp = client.get("/teacher/analysis")
        assert resp.status_code == 200
        assert "學生學習分析".encode("utf-8") in resp.data

    def test_class_page_shows_students(self, app_ctx):
        app = app_ctx
        client = app.test_client()
        self._login(client, 101)
        resp = client.get("/teacher/analysis?class_id=1")
        assert resp.status_code == 200
        assert "王小明".encode("utf-8") in resp.data

    def test_student_no_practice_empty_state(self, app_ctx):
        app = app_ctx
        client = app.test_client()
        self._login(client, 101)
        resp = client.get("/teacher/analysis?class_id=1&student_id=202")
        assert resp.status_code == 200
        assert "尚無練習紀錄".encode("utf-8") in resp.data

    def test_illegal_class_id_redirects(self, app_ctx):
        app = app_ctx
        client = app.test_client()
        self._login(client, 101)
        resp = client.get("/teacher/analysis?class_id=9999")
        assert resp.status_code == 302

    def test_student_not_in_class_redirects(self, app_ctx):
        app = app_ctx
        client = app.test_client()
        self._login(client, 101)
        resp = client.get("/teacher/analysis?class_id=1&student_id=203")
        assert resp.status_code == 302

    def test_student_role_forbidden(self, app_ctx):
        app = app_ctx
        client = app.test_client()
        self._login(client, 201)
        resp = client.get("/teacher/analysis")
        assert resp.status_code == 302

    def test_other_teacher_cannot_view_class(self, app_ctx):
        app = app_ctx
        client = app.test_client()
        self._login(client, 102)
        resp = client.get("/teacher/analysis?class_id=1")
        assert resp.status_code == 302

    def test_unit_detail_page(self, app_ctx):
        app = app_ctx
        client = app.test_client()
        self._login(client, 101)
        resp = client.get(
            "/teacher/analysis?class_id=1&student_id=201"
            "&volume=數學B4&chapter=2 概率"
        )
        assert resp.status_code == 200
        assert "技能分析".encode("utf-8") in resp.data

    def test_learning_time_dash_in_page(self, app_ctx):
        app = app_ctx
        client = app.test_client()
        self._login(client, 101)
        resp = client.get("/teacher/analysis?class_id=1")
        assert resp.status_code == 200
        assert "0 分鐘".encode("utf-8") not in resp.data
