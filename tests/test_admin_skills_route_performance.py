# -*- coding: utf-8 -*-
from __future__ import annotations

import time
import uuid

import pytest

from app import create_app
from models import SkillCurriculum, SkillInfo, User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def app_ctx():
    import config as _cfg
    from pathlib import Path

    db_path = Path("reports") / f"pytest_admin_skills_perf_{uuid.uuid4().hex[:8]}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            teacher = User(username=f"teacher_{uuid.uuid4().hex[:6]}", password_hash="x", role="teacher")
            db.session.add(teacher)
            skill = SkillInfo(
                skill_id="perf_skill_route",
                skill_en_name="Perf Skill",
                skill_ch_name="效能測試技能",
                category="test",
                description="",
                input_type="text",
                gemini_prompt="prompt",
                consecutive_correct_required=3,
                is_active=True,
                order_index=1,
            )
            curriculum = SkillCurriculum(
                skill_id=skill.skill_id,
                curriculum="vocational",
                grade=10,
                volume="數學B1",
                chapter="1",
                section="1-1",
                display_order=1,
            )
            db.session.add(skill)
            db.session.add(curriculum)
            db.session.commit()
            yield app, teacher.id
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        try:
            if db_path.exists():
                db_path.unlink()
        except OSError:
            pass


def test_admin_skills_route_returns_within_budget(app_ctx):
    app, teacher_id = app_ctx
    client = app.test_client()
    _login(client, teacher_id)

    started = time.time()
    response = client.get("/skills?f_curriculum=vocational")
    elapsed = time.time() - started

    assert response.status_code == 200
    assert b"perf_skill_route" in response.data
    assert elapsed < 5.0, f"/skills too slow: {elapsed:.3f}s"
