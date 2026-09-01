# -*- coding: utf-8 -*-
"""Tests for canonical practice_attempts (PHASE A)."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest
from flask_login import login_user

from app import create_app
from core.practice_attempt_service import SOURCE_GENERAL_PRACTICE, persist_practice_attempt
from core.teacher_analysis_service import (
    get_class_students_stats,
    get_recent_attempts,
    get_student_overview,
    get_student_unit_detail,
    parse_time_range,
)
from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
    is_b4_chapter2_phase6c1_deterministic_skill,
)
from models import (
    AdaptiveLearningLog,
    B4Chap2VisibilityAuditLog,
    Class,
    ClassStudent,
    PracticeAttempt,
    SkillCurriculum,
    SkillInfo,
    User,
    db,
)


@pytest.fixture()
def app_ctx(tmp_path):
    import config as _cfg

    db_path = tmp_path / f"pytest_practice_attempts_{uuid.uuid4().hex[:8]}.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            _seed()
            yield app
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri


def _seed() -> None:
    teacher = User(id=101, username="teacher_pa", password_hash="x", role="teacher")
    student = User(id=201, username="stu_pa", password_hash="x", role="student", real_name="測試生")
    cls = Class(id=1, name="測試班", teacher_id=101, class_code="PA000001")
    db.session.add_all([teacher, student, cls, ClassStudent(class_id=1, student_id=201)])

    b1_skill = "vh_數學B1_AbsoluteValue"
    b4_skill = "vh_數學B4_ProbabilityDefinition"
    for sid, ch in [(b1_skill, "1 絕對值"), (b4_skill, "2 概率")]:
        db.session.add(SkillInfo(
            skill_id=sid,
            skill_en_name=sid,
            skill_ch_name=ch,
            description="d",
            gemini_prompt="p",
        ))
    db.session.add(SkillCurriculum(
        skill_id=b1_skill,
        curriculum="vocational",
        grade=1,
        volume="數學B1",
        chapter="1 絕對值",
        section="1-1",
        display_order=1,
    ))
    db.session.commit()


def test_practice_attempt_model_insert(app_ctx):
    row = PracticeAttempt(
        student_id=201,
        class_id=1,
        skill_id="vh_數學B1_AbsoluteValue",
        problem_type_id="abs_basic",
        question_uid="uid-1",
        question_text="解 |x| = 3",
        user_answer="3",
        expected_answer="3,-3",
        is_correct=True,
        source=SOURCE_GENERAL_PRACTICE,
    )
    db.session.add(row)
    db.session.commit()
    loaded = db.session.get(PracticeAttempt, row.id)
    assert loaded is not None
    assert loaded.student_id == 201
    assert loaded.is_correct is True
    assert loaded.source == SOURCE_GENERAL_PRACTICE


def test_persist_practice_attempt_writes_fields(app_ctx):
    app = app_ctx
    with app.test_request_context():
        login_user(db.session.get(User, 201))
        row = persist_practice_attempt(
            skill_id="vh_數學B1_AbsoluteValue",
            is_correct=False,
            user_answer="x=1",
            current_question={
                "question_text": "解 |x| >= 18",
                "correct_answer": "(-∞,-18] ∪ [18,∞)",
                "problem_type_id": "abs_ineq",
                "level": 1,
            },
            question_uid="q-abc",
        )
    assert row is not None
    assert row.student_id == 201
    assert row.class_id == 1
    assert row.skill_id == "vh_數學B1_AbsoluteValue"
    assert row.is_correct is False
    assert row.source == SOURCE_GENERAL_PRACTICE
    assert row.question_text == "解 |x| >= 18"
    assert row.user_answer == "x=1"
    assert "18" in (row.expected_answer or "")


def test_persist_skips_b4_deterministic_skill(app_ctx):
    app = app_ctx
    b4_skill = "vh_數學B4_ProbabilityDefinition"
    assert is_b4_chapter2_phase6c1_deterministic_skill(b4_skill)
    with app.test_request_context():
        login_user(db.session.get(User, 201))
        row = persist_practice_attempt(
            skill_id=b4_skill,
            is_correct=True,
            user_answer="1/2",
            current_question={"question_text": "q", "correct_answer": "1/2"},
        )
    assert row is None
    assert PracticeAttempt.query.count() == 0


def test_teacher_analysis_general_practice_stats(app_ctx):
    now = datetime.utcnow()
    for i, ok in enumerate([True, True, True, False]):
        db.session.add(PracticeAttempt(
            student_id=201,
            class_id=1,
            skill_id="vh_數學B1_AbsoluteValue",
            is_correct=ok,
            source=SOURCE_GENERAL_PRACTICE,
            created_at=now - timedelta(minutes=i),
        ))
    db.session.commit()

    student = db.session.get(User, 201)
    overview = get_student_overview(student, parse_time_range("all"))
    assert overview["stats"].total == 4
    assert overview["stats"].correct == 3
    assert overview["stats"].incorrect == 1
    assert overview["stats"].accuracy == pytest.approx(0.75)


def test_teacher_analysis_three_sources(app_ctx):
    now = datetime.utcnow()
    db.session.add(PracticeAttempt(
        student_id=201, class_id=1, skill_id="vh_數學B1_AbsoluteValue",
        is_correct=True, source=SOURCE_GENERAL_PRACTICE, created_at=now,
    ))
    db.session.add(PracticeAttempt(
        student_id=201, class_id=1, skill_id="vh_數學B1_AbsoluteValue",
        is_correct=False, source=SOURCE_GENERAL_PRACTICE, created_at=now,
    ))
    db.session.add(B4Chap2VisibilityAuditLog(
        record_kind="deterministic_answer",
        student_id=201,
        skill_id="vh_數學B4_ProbabilityDefinition",
        is_correct=True,
        created_at=now,
    ))
    db.session.add(B4Chap2VisibilityAuditLog(
        record_kind="deterministic_answer",
        student_id=201,
        skill_id="vh_數學B4_ProbabilityDefinition",
        is_correct=True,
        created_at=now,
    ))
    db.session.add(B4Chap2VisibilityAuditLog(
        record_kind="deterministic_answer",
        student_id=201,
        skill_id="vh_數學B4_ProbabilityDefinition",
        is_correct=False,
        created_at=now,
    ))
    for i in range(4):
        db.session.add(AdaptiveLearningLog(
            student_id=201,
            session_id="s1",
            step_number=i + 1,
            target_family_id="I1",
            target_subskills='["a"]',
            is_correct=(i < 3),
            current_apr=0.5,
            ppo_strategy=0,
            execution_latency=0,
            created_at=now - timedelta(minutes=i),
        ))
    db.session.commit()

    student = db.session.get(User, 201)
    overview = get_student_overview(student, parse_time_range("all"))
    assert overview["stats"].total == 9
    assert overview["stats"].correct == 6
    assert overview["stats"].incorrect == 3


def test_time_filter_today(app_ctx):
    now = datetime.utcnow()
    db.session.add(PracticeAttempt(
        student_id=201, class_id=1, skill_id="vh_數學B1_AbsoluteValue",
        is_correct=True, source=SOURCE_GENERAL_PRACTICE, created_at=now,
    ))
    db.session.add(PracticeAttempt(
        student_id=201, class_id=1, skill_id="vh_數學B1_AbsoluteValue",
        is_correct=False, source=SOURCE_GENERAL_PRACTICE,
        created_at=now - timedelta(days=10),
    ))
    db.session.commit()
    student = db.session.get(User, 201)
    overview = get_student_overview(student, parse_time_range("today"))
    assert overview["stats"].total == 1


def test_unit_mapping_and_recent_attempts(app_ctx):
    now = datetime.utcnow()
    db.session.add(PracticeAttempt(
        student_id=201,
        class_id=1,
        skill_id="vh_數學B1_AbsoluteValue",
        question_text="解 |x| = 5",
        user_answer="5",
        expected_answer="5,-5",
        is_correct=True,
        source=SOURCE_GENERAL_PRACTICE,
        created_at=now,
    ))
    db.session.commit()

    detail = get_student_unit_detail(
        201,
        volume="數學B1",
        chapter="1 絕對值",
        skill_unit=None,
        time_range=parse_time_range("all"),
    )
    assert detail["stats"].total == 1
    recent = get_recent_attempts(201, {"vh_數學B1_AbsoluteValue"}, parse_time_range("all"))
    assert len(recent) == 1
    assert recent[0]["question_text"] == "解 |x| = 5"
    assert recent[0]["source"] == SOURCE_GENERAL_PRACTICE


def test_class_students_stats_includes_practice_attempts(app_ctx):
    db.session.add(PracticeAttempt(
        student_id=201, class_id=1, skill_id="vh_數學B1_AbsoluteValue",
        is_correct=True, source=SOURCE_GENERAL_PRACTICE,
    ))
    db.session.commit()
    cls = db.session.get(Class, 1)
    rows = get_class_students_stats(cls, parse_time_range("all"))
    assert rows[0]["stats"].total == 1
