from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import event

from app import create_app
from core.skill_card_mastery import build_skill_card_mastery, classify_skill_card_status
from models import PracticeAttempt, Progress, SkillCurriculum, SkillInfo, TextbookExample, User, db


@pytest.fixture()
def mastery_app(tmp_path):
    import config as _cfg

    db_path = tmp_path / "skill_card_mastery.db"
    previous_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            yield app
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = previous_uri


def _add_skill(skill_id: str, *, references: int, curriculum: str = "general") -> None:
    db.session.add(
        SkillInfo(
            skill_id=skill_id,
            skill_en_name=skill_id,
            skill_ch_name=skill_id,
            category="skill-card-test",
            description="skill",
            gemini_prompt="prompt",
            consecutive_correct_required=999,
            is_active=True,
        )
    )
    for index in range(references):
        db.session.add(
            TextbookExample(
                skill_id=skill_id,
                source_curriculum=curriculum,
                source_volume="book",
                source_chapter="chapter",
                source_section="section",
                source_description=f"reference {index}",
                problem_text=f"question {index}",
            )
        )


def _add_attempts(student_id: int, skill_id: str, answers: list[bool]) -> None:
    now = datetime.utcnow()
    for index, correct in enumerate(answers):
        db.session.add(
            PracticeAttempt(
                student_id=student_id,
                skill_id=skill_id,
                is_correct=correct,
                source="test",
                created_at=now + timedelta(seconds=index),
            )
        )


@pytest.mark.parametrize(
    ("attempt_count", "accuracy", "pass_target", "binding_issue", "expected"),
    [
        (0, 0.0, 4, False, "unpracticed"),
        (1, 49.9, 4, False, "needs_improvement"),
        (1, 50.0, 4, False, "learning"),
        (3, 69.9, 4, False, "learning"),
        (3, 70.0, 4, False, "proficient"),
        (3, 84.9, 4, False, "proficient"),
        (4, 85.0, 4, False, "mastered"),
        (3, 100.0, 4, False, "proficient"),
        (10, 100.0, 0, True, "proficient"),
    ],
)
def test_status_boundaries_are_global(
    attempt_count: int,
    accuracy: float,
    pass_target: int,
    binding_issue: bool,
    expected: str,
) -> None:
    assert classify_skill_card_status(
        attempt_count=attempt_count,
        recent_accuracy=accuracy,
        pass_target=pass_target,
        binding_issue=binding_issue,
    ) == expected


def test_global_status_rules_reference_targets_and_two_batch_queries(mastery_app) -> None:
    student = User(username="mastery_student", password_hash="x", role="student")
    db.session.add(student)
    db.session.flush()
    student_id = student.id
    cases = {
        "jh_white": (2, []),
        "jh_red": (2, [True, False, False, False]),
        "gh_light": (12, [True] * 6 + [False] * 4),
        "gh_medium": (12, [True] * 8 + [False] * 2),
        "vh_dark": (5, [True] * 9 + [False]),
        "vh_zero_reference": (0, [True] * 10),
        "global_recent_window": (20, [False] * 5 + [True] * 10),
    }
    for skill_id, (references, answers) in cases.items():
        _add_skill(skill_id, references=references)
        _add_attempts(student_id, skill_id, answers)
    db.session.commit()

    selects: list[str] = []

    def _count_selects(_conn, _cursor, statement, _parameters, _context, _executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            selects.append(statement)

    event.listen(db.engine, "before_cursor_execute", _count_selects)
    try:
        cards = build_skill_card_mastery(
            student_id=student_id,
            skill_ids=list(cases),
            current_streak_by_skill={skill_id: 7 for skill_id in cases},
        )
    finally:
        event.remove(db.engine, "before_cursor_execute", _count_selects)

    assert len(selects) == 2
    assert cards["jh_white"]["card_color"] == "white"
    assert cards["jh_red"]["card_color"] == "red"
    assert cards["gh_light"]["card_color"] == "light_green"
    assert cards["gh_medium"]["card_color"] == "medium_green"
    assert cards["vh_dark"]["card_color"] == "dark_green"
    assert cards["vh_dark"]["pass_target"] == 5
    assert cards["vh_dark"]["current_streak"] == 7
    assert cards["vh_dark"]["attempt_count"] == 10
    assert cards["vh_dark"]["recent_accuracy"] == 90.0
    assert cards["vh_zero_reference"]["binding_issue"] is True
    assert cards["vh_zero_reference"]["pass_target"] == 0
    assert cards["vh_zero_reference"]["card_color"] == "medium_green"
    assert cards["global_recent_window"]["attempt_count"] == 15
    assert cards["global_recent_window"]["recent_attempt_count"] == 10
    assert cards["global_recent_window"]["recent_accuracy"] == 100.0
    assert cards["global_recent_window"]["card_color"] == "medium_green"


def test_none_student_returns_unpracticed_without_reading_personal_records(mastery_app) -> None:
    student = User(username="real_student_must_not_leak", password_hash="x", role="student")
    db.session.add(student)
    db.session.flush()
    _add_skill("guest_no_data_skill", references=2)
    _add_attempts(student.id, "guest_no_data_skill", [True, True, True])
    db.session.add(
        Progress(
            user_id=student.id,
            skill_id="guest_no_data_skill",
            consecutive_correct=3,
            questions_solved=3,
        )
    )
    db.session.commit()

    selects: list[str] = []

    def _capture_selects(_conn, _cursor, statement, _parameters, _context, _executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            selects.append(statement)

    event.listen(db.engine, "before_cursor_execute", _capture_selects)
    try:
        cards = build_skill_card_mastery(
            student_id=None,
            skill_ids=["guest_no_data_skill"],
            current_streak_by_skill={"guest_no_data_skill": 999},
        )
    finally:
        event.remove(db.engine, "before_cursor_execute", _capture_selects)

    card = cards["guest_no_data_skill"]
    assert card["card_status"] == "unpracticed"
    assert card["card_status_label"] == "展示模式／尚無個人學習紀錄"
    assert card["current_streak"] == 0
    assert card["attempt_count"] == 0
    assert card["recent_attempt_count"] == 0
    assert card["recent_correct_count"] == 0
    assert card["recent_accuracy"] == 0.0
    assert card["pass_target"] == 2
    assert len(selects) == 1
    assert "practice_attempts" not in selects[0].lower()
    assert "progress" not in selects[0].lower()


def test_dashboard_uses_dynamic_target_and_recent_accuracy_without_n_plus_one(mastery_app) -> None:
    student = User(
        username="dashboard_mastery_student",
        password_hash="x",
        role="student",
        curriculum_code="junior_high",
    )
    db.session.add(student)
    db.session.flush()
    for index in range(12):
        skill_id = f"jh_global_card_{index}"
        _add_skill(skill_id, references=0 if index == 11 else 4, curriculum="junior_high")
        db.session.add(
            SkillCurriculum(
                skill_id=skill_id,
                curriculum="junior_high",
                grade=7,
                volume="數學1上",
                chapter="第一章",
                section="1-1",
                display_order=index,
            )
        )
    target_skill = "jh_global_card_0"
    db.session.add(
        Progress(
            user_id=student.id,
            skill_id=target_skill,
            consecutive_correct=2,
            questions_solved=3,
        )
    )
    _add_attempts(student.id, target_skill, [True, False, True])
    db.session.commit()

    client = mastery_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(student.id)
        sess["_fresh"] = True

    selects: list[str] = []

    def _count_selects(_conn, _cursor, statement, _parameters, _context, _executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            selects.append(statement)

    event.listen(db.engine, "before_cursor_execute", _count_selects)
    try:
        response = client.get(
            "/dashboard?view=curriculum&curriculum=junior_high&volume=數學1上&chapter=第一章"
        )
    finally:
        event.remove(db.engine, "before_cursor_execute", _count_selects)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "連續答對 2 / 4 題" in html
    assert "熟練度 66.7%" in html
    assert "status-learning" in html
    assert "教材參考題綁定異常" in html
    assert "連續答對 0 / 暫無門檻" in html
    assert "連續答對 0 / 0 題" not in html
    assert "連續答對 0 / 3 題" not in html
    assert "consecutive_correct_required" not in html
    assert len(selects) == 5

    category_response = client.get("/dashboard?view=all&category=skill-card-test")
    assert category_response.status_code == 200
    category_html = category_response.get_data(as_text=True)
    assert "連續答對 2 / 4 題" in category_html
    assert "熟練度 66.7%" in category_html
