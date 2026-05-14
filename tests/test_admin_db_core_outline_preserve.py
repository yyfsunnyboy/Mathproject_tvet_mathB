# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid

import pytest

from app import create_app
from core.routes.admin import _clear_core_textbook_data, _preview_core_textbook_data
from models import SkillCurriculum, SkillInfo, TextbookExample, User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def app_ctx(tmp_path):
    import config as _cfg

    db_path = tmp_path / f"db_core_outline_{uuid.uuid4().hex[:8]}.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            admin = User(username=f"admin_{uuid.uuid4().hex[:6]}", password_hash="x", role="admin")
            db.session.add(admin)
            db.session.commit()
            yield app, admin.id
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri


def _mk_skill(skill_id: str) -> SkillInfo:
    return SkillInfo(
        skill_id=skill_id,
        skill_en_name=skill_id,
        skill_ch_name=skill_id,
        description="d",
        gemini_prompt="p",
    )


def _mk_curr(skill_id: str, section: str) -> SkillCurriculum:
    return SkillCurriculum(
        skill_id=skill_id,
        curriculum="vocational",
        grade=10,
        volume="數學B1",
        chapter="1 坐標系與函數圖形",
        section=section,
        paragraph="",
        display_order=0,
        difficulty_level=1,
    )


def _mk_ex(skill_id: str, section: str) -> TextbookExample:
    return TextbookExample(
        skill_id=skill_id,
        source_curriculum="vocational",
        source_volume="數學B1",
        source_chapter="1 坐標系與函數圖形",
        source_section=section,
        source_description=f"{section}-{skill_id}",
        problem_text=f"題目 {skill_id}",
        problem_type="textbook_example",
        correct_answer="1",
        detailed_solution="s",
        difficulty_level=1,
    )


def test_filtered_section_clear_preserves_outline_and_preview_counts(app_ctx):
    app, _ = app_ctx
    with app.app_context():
        outline_11 = "outline_vocational_數學B1_11"
        normal_11 = "vh_數學B1_AbsoluteValue"
        outline_12 = "outline_vocational_數學B1_12"
        normal_12 = "vh_數學B1_CoordinatePlane"

        db.session.add_all([
            _mk_skill(outline_11),
            _mk_skill(normal_11),
            _mk_skill(outline_12),
            _mk_skill(normal_12),
        ])
        db.session.add_all([
            _mk_curr(outline_11, "1-1 數線與絕對值"),
            _mk_curr(normal_11, "1-1 數線與絕對值"),
            _mk_curr(outline_12, "1-2 平面坐標系與線型函數"),
            _mk_curr(normal_12, "1-2 平面坐標系與線型函數"),
        ])
        db.session.add_all([
            _mk_ex(normal_11, "1-1 數線與絕對值"),
            _mk_ex(normal_12, "1-2 平面坐標系與線型函數"),
        ])
        db.session.commit()

        filters = {
            "scope_mode": "filtered",
            "curriculum": "vocational",
            "grade": 10,
            "volume": "數學B1",
            "chapter": "1 坐標系與函數圖形",
            "section": "1-1 數線與絕對值",
        }

        preview = _preview_core_textbook_data(filters)
        assert preview["preserved_outline_curriculum"] == 1
        assert preview["deleted_skill_curriculum"] == 1
        assert preview["deleted_textbook_examples"] == 1

        stats = _clear_core_textbook_data(filters)
        assert stats["preserved_outline_curriculum"] == 1
        assert stats["deleted_skill_curriculum"] == 1
        assert stats["deleted_textbook_examples"] == 1

        assert SkillCurriculum.query.filter_by(skill_id=outline_11).count() == 1
        assert SkillCurriculum.query.filter_by(skill_id=normal_11).count() == 0
        assert SkillCurriculum.query.filter_by(skill_id=outline_12).count() == 1
        assert SkillCurriculum.query.filter_by(skill_id=normal_12).count() == 1
        assert TextbookExample.query.filter_by(skill_id=normal_11).count() == 0
        assert TextbookExample.query.filter_by(skill_id=normal_12).count() == 1

