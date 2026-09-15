from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from app import create_app
from core.routes.practice import _is_incorrect_resubmit, update_progress
from core.skill_card_mastery import build_skill_card_mastery, get_pass_target
from models import Progress, SkillInfo, TextbookExample, User, db


@pytest.fixture()
def streak_app(tmp_path):
    import config as cfg

    db_path = tmp_path / "practice_streak.db"
    previous_uri = cfg.Config.SQLALCHEMY_DATABASE_URI
    cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            yield app
    finally:
        cfg.Config.SQLALCHEMY_DATABASE_URI = previous_uri


def _seed_skill(skill_id: str, reference_count: int) -> int:
    user = User(username=f"user-{skill_id}", password_hash="x", role="student")
    db.session.add(user)
    db.session.add(
        SkillInfo(
            skill_id=skill_id,
            skill_en_name=skill_id,
            skill_ch_name=skill_id,
            category="streak-test",
            description="skill",
            gemini_prompt="prompt",
            is_active=True,
        )
    )
    for index in range(reference_count):
        db.session.add(
            TextbookExample(
                skill_id=skill_id,
                source_curriculum="general",
                source_volume="book",
                source_chapter="chapter",
                source_section="section",
                source_description=f"reference {index}",
                problem_text=f"question {index}",
            )
        )
    db.session.commit()
    return user.id


def test_wrong_retry_correct_then_next_correct_restarts_streak(streak_app):
    student_id = _seed_skill("global_streak_semantics", 4)
    db.session.add(
        Progress(user_id=student_id, skill_id="global_streak_semantics", consecutive_correct=2)
    )
    db.session.commit()

    update_progress(student_id, "global_streak_semantics", False)
    assert db.session.get(Progress, (student_id, "global_streak_semantics")).consecutive_correct == 0

    update_progress(student_id, "global_streak_semantics", True)
    assert db.session.get(Progress, (student_id, "global_streak_semantics")).consecutive_correct == 1

    update_progress(student_id, "global_streak_semantics", True)
    assert db.session.get(Progress, (student_id, "global_streak_semantics")).consecutive_correct == 2


def test_only_incorrect_answered_question_is_open_for_resubmit():
    assert _is_incorrect_resubmit({"duplicate_submission": True, "correct": False}) is True
    assert _is_incorrect_resubmit({"duplicate_submission": True, "correct": True}) is False
    assert _is_incorrect_resubmit({"stale_question": True, "correct": False}) is False


def test_practice_and_dashboard_share_reference_count_authority(streak_app):
    student_id = _seed_skill("global_shared_target", 5)
    assert get_pass_target("global_shared_target") == 5
    dashboard = build_skill_card_mastery(student_id=student_id, skill_ids=["global_shared_target"])
    assert dashboard["global_shared_target"]["pass_target"] == 5

    _seed_skill("global_zero_reference", 0)
    assert get_pass_target("global_zero_reference") == 0


def test_standard_practice_ui_uses_authoritative_progress_fields():
    template = (Path(__file__).parents[1] / "templates" / "index.html").read_text(encoding="utf-8")
    assert "連續答對 ${normalizedStreak} / ${normalizedTarget} 題" in template
    assert "連續答對：暫無門檻" in template
    assert "data.consecutive_correct, data.pass_target" in template
    assert "3 / 10" not in template
    assert "get_pass_target" in inspect.getsource(build_skill_card_mastery)
