# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from app import create_app
from core.models.prompt_template import PromptTemplate
from core.routes.admin import _clear_core_textbook_data
from models import SkillCurriculum, SkillInfo, SystemSetting, TextbookExample, User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def app_ctx(tmp_path):
    import config as _cfg

    db_path = tmp_path / f"db_core_scope_{uuid.uuid4().hex[:8]}.db"
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


def _mk_curr(
    skill_id: str,
    *,
    curriculum: str = "vocational",
    grade: int = 10,
    volume: str = "數學B1",
    chapter: str = "1 坐標系與函數圖形",
    section: str = "1-1 數線與絕對值",
) -> SkillCurriculum:
    return SkillCurriculum(
        skill_id=skill_id,
        curriculum=curriculum,
        grade=grade,
        volume=volume,
        chapter=chapter,
        section=section,
        paragraph="",
        display_order=0,
        difficulty_level=1,
    )


def _mk_ex(
    skill_id: str,
    *,
    volume: str = "數學B1",
    chapter: str = "1 坐標系與函數圖形",
    section: str = "1-1 數線與絕對值",
) -> TextbookExample:
    return TextbookExample(
        skill_id=skill_id,
        source_curriculum="vocational",
        source_volume=volume,
        source_chapter=chapter,
        source_section=section,
        source_description=f"{section}-{skill_id}",
        problem_text=f"題目 {skill_id}",
        problem_type="textbook_example",
        correct_answer="1",
        detailed_solution="s",
        difficulty_level=1,
    )


def _seed_scope_tree():
    s11 = "vh_b1_sec11"
    s12 = "vh_b1_sec12"
    s21 = "vh_b1_sec21"
    b2s11 = "vh_b2_sec11"
    rows = [
        _mk_skill(s11),
        _mk_skill(s12),
        _mk_skill(s21),
        _mk_skill(b2s11),
        _mk_curr(skill_id=s11, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
        _mk_curr(skill_id=s12, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-2 平面坐標系與線型函數"),
        _mk_curr(skill_id=s21, volume="數學B1", chapter="2 直線方程式", section="2-1 斜率"),
        _mk_curr(skill_id=b2s11, volume="數學B2", chapter="1 三角函數", section="1-1 有向角"),
    ]
    db.session.add_all(rows)
    db.session.commit()


def test_core_scope_options_without_filters_returns_curricula(app_ctx):
    app, admin_id = app_ctx
    with app.app_context():
        _seed_scope_tree()
        client = app.test_client()
        _login(client, admin_id)
        r = client.get("/db_maintenance/core_scope_options")
        assert r.status_code == 200
        data = r.get_json()
        assert "vocational" in data["curricula"]


def test_core_scope_options_curriculum_filter_narrows_grades_and_volumes(app_ctx):
    app, admin_id = app_ctx
    with app.app_context():
        _seed_scope_tree()
        db.session.add_all([
            _mk_skill("jh_b1"),
            _mk_curr(skill_id="jh_b1", curriculum="general", grade=7, volume="數學A1", chapter="1 整數", section="1-1"),
        ])
        db.session.commit()

        client = app.test_client()
        _login(client, admin_id)
        r = client.get("/db_maintenance/core_scope_options?curriculum=vocational")
        data = r.get_json()
        assert data["grades"] == [10]
        assert "數學B1" in data["volumes"]
        assert "數學A1" not in data["volumes"]


def test_core_scope_options_volume_filter_narrows_chapters(app_ctx):
    app, admin_id = app_ctx
    with app.app_context():
        _seed_scope_tree()
        client = app.test_client()
        _login(client, admin_id)
        r = client.get("/db_maintenance/core_scope_options?curriculum=vocational&grade=10&volume=數學B1")
        data = r.get_json()
        assert "1 坐標系與函數圖形" in data["chapters"]
        assert "2 直線方程式" in data["chapters"]
        assert "1 三角函數" not in data["chapters"]


def test_core_scope_options_chapter_filter_narrows_sections(app_ctx):
    app, admin_id = app_ctx
    with app.app_context():
        _seed_scope_tree()
        client = app.test_client()
        _login(client, admin_id)
        r = client.get(
            "/db_maintenance/core_scope_options?curriculum=vocational&grade=10&volume=數學B1&chapter=1 坐標系與函數圖形"
        )
        data = r.get_json()
        assert data["sections"] == ["1-1 數線與絕對值", "1-2 平面坐標系與線型函數"]
        assert "2-1 斜率" not in data["sections"]
        assert "1-1 有向角" not in data["sections"]


def test_section_level_core_clear_keeps_other_section(app_ctx):
    app, _ = app_ctx
    with app.app_context():
        s11 = "vh_B1_sec11_only"
        s12 = "vh_B1_sec12_only"
        db.session.add_all([_mk_skill(s11), _mk_skill(s12)])
        db.session.add_all([
            _mk_curr(skill_id=s11, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
            _mk_curr(skill_id=s12, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-2 平面坐標系與線型函數"),
        ])
        db.session.add_all([
            _mk_ex(skill_id=s11, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
            _mk_ex(skill_id=s12, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-2 平面坐標系與線型函數"),
        ])
        db.session.commit()

        stats = _clear_core_textbook_data(
            {
                "scope_mode": "filtered",
                "curriculum": "vocational",
                "grade": 10,
                "volume": "數學B1",
                "chapter": "1 坐標系與函數圖形",
                "section": "1-1 數線與絕對值",
            }
        )
        assert stats["deleted_skill_curriculum"] == 1
        assert stats["deleted_textbook_examples"] == 1
        assert SkillCurriculum.query.filter_by(skill_id=s11).count() == 0
        assert SkillCurriculum.query.filter_by(skill_id=s12).count() == 1


def test_volume_level_core_clear_keeps_other_volume(app_ctx):
    app, _ = app_ctx
    with app.app_context():
        b1 = "vh_B1_only"
        b2 = "vh_B2_only"
        db.session.add_all([_mk_skill(b1), _mk_skill(b2)])
        db.session.add_all([
            _mk_curr(skill_id=b1, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
            _mk_curr(skill_id=b2, volume="數學B2", chapter="1 三角函數", section="1-1 有向角"),
        ])
        db.session.add_all([
            _mk_ex(skill_id=b1, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
            _mk_ex(skill_id=b2, volume="數學B2", chapter="1 三角函數", section="1-1 有向角"),
        ])
        db.session.commit()

        _clear_core_textbook_data(
            {"scope_mode": "filtered", "curriculum": "vocational", "grade": 10, "volume": "數學B1", "chapter": "", "section": ""}
        )
        assert SkillCurriculum.query.filter_by(skill_id=b1).count() == 0
        assert SkillCurriculum.query.filter_by(skill_id=b2).count() == 1


def test_shared_skill_is_skipped_for_textbook_examples(app_ctx):
    app, _ = app_ctx
    with app.app_context():
        shared = "vh_B1_shared"
        db.session.add(_mk_skill(shared))
        db.session.add_all([
            _mk_curr(skill_id=shared, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
            _mk_curr(skill_id=shared, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-2 平面坐標系與線型函數"),
        ])
        db.session.add(_mk_ex(skill_id=shared, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"))
        db.session.commit()

        stats = _clear_core_textbook_data(
            {
                "scope_mode": "filtered",
                "curriculum": "vocational",
                "grade": 10,
                "volume": "數學B1",
                "chapter": "1 坐標系與函數圖形",
                "section": "1-1 數線與絕對值",
            }
        )
        assert shared in stats["skipped_shared_skill_ids"]
        assert stats["deleted_textbook_examples"] == 0
        assert TextbookExample.query.filter_by(skill_id=shared).count() == 1


def test_orphan_skill_cleanup_only_when_unused(app_ctx):
    app, _ = app_ctx
    with app.app_context():
        orphan = "vh_orphan_after_clear"
        keep = "vh_keep_used"
        db.session.add_all([_mk_skill(orphan), _mk_skill(keep)])
        db.session.add_all([
            _mk_curr(skill_id=orphan, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
            _mk_curr(skill_id=keep, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-2 平面坐標系與線型函數"),
        ])
        db.session.add(_mk_ex(skill_id=keep, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-2 平面坐標系與線型函數"))
        db.session.commit()

        _clear_core_textbook_data(
            {
                "scope_mode": "filtered",
                "curriculum": "vocational",
                "grade": 10,
                "volume": "數學B1",
                "chapter": "1 坐標系與函數圖形",
                "section": "1-1 數線與絕對值",
            }
        )
        assert SkillInfo.query.filter_by(skill_id=orphan).count() == 0
        assert SkillInfo.query.filter_by(skill_id=keep).count() == 1


def test_core_filtered_clear_does_not_require_confirm_core_clear(app_ctx):
    app, admin_id = app_ctx
    with app.app_context():
        sid = "vh_clear_without_confirm"
        db.session.add_all([
            _mk_skill(sid),
            _mk_curr(skill_id=sid, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
            _mk_ex(skill_id=sid, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
        ])
        db.session.commit()

        client = app.test_client()
        _login(client, admin_id)
        r = client.post(
            "/db_maintenance",
            data={
                "action": "clear_all_data",
                "mode": "core",
                "core_scope_mode": "filtered",
                "core_curriculum": "vocational",
                "core_grade": "10",
                "core_volume": "數學B1",
                "core_chapter": "1 坐標系與函數圖形",
                "core_section": "1-1 數線與絕對值",
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert SkillCurriculum.query.filter_by(skill_id=sid).count() == 0


def test_core_clear_does_not_delete_users_prompts_system_settings(app_ctx):
    app, _ = app_ctx
    with app.app_context():
        sid = "vh_non_core_guard"
        db.session.add_all([
            _mk_skill(sid),
            _mk_curr(skill_id=sid, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
            _mk_ex(skill_id=sid, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
        ])
        db.session.add(User(username=f"user_{uuid.uuid4().hex[:6]}", password_hash="x", role="student"))
        db.session.add(SystemSetting(key=f"sys_{uuid.uuid4().hex[:6]}", value="v"))
        db.session.add(
            PromptTemplate(
                prompt_key=f"p_{uuid.uuid4().hex[:6]}",
                title="t",
                category="c",
                content="x",
                default_content="x",
            )
        )
        db.session.commit()
        users_before = User.query.count()
        prompts_before = PromptTemplate.query.count()
        settings_before = SystemSetting.query.count()

        _clear_core_textbook_data({"scope_mode": "all", "curriculum": "", "grade": None, "volume": "", "chapter": "", "section": ""})

        assert User.query.count() == users_before
        assert PromptTemplate.query.count() == prompts_before
        assert SystemSetting.query.count() == settings_before


def test_preview_core_clear_does_not_delete_and_uses_same_filters(app_ctx):
    app, admin_id = app_ctx
    with app.app_context():
        sid = "vh_preview_only"
        db.session.add_all([
            _mk_skill(sid),
            _mk_curr(skill_id=sid, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
            _mk_ex(skill_id=sid, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
        ])
        db.session.commit()
        client = app.test_client()
        _login(client, admin_id)
        r = client.post(
            "/db_maintenance",
            data={
                "action": "preview_core_clear",
                "mode": "core",
                "core_scope_mode": "filtered",
                "core_curriculum": "vocational",
                "core_grade": "10",
                "core_volume": "數學B1",
                "core_chapter": "1 坐標系與函數圖形",
                "core_section": "1-1 數線與絕對值",
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert SkillCurriculum.query.filter_by(skill_id=sid).count() == 1
        assert TextbookExample.query.filter_by(skill_id=sid).count() == 1


def test_full_clear_guard_still_requires_original_confirmation(app_ctx):
    app, admin_id = app_ctx
    with app.app_context():
        sid = "vh_full_guard"
        db.session.add_all([
            _mk_skill(sid),
            _mk_curr(skill_id=sid, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
            _mk_ex(skill_id=sid, volume="數學B1", chapter="1 坐標系與函數圖形", section="1-1 數線與絕對值"),
        ])
        db.session.commit()
        client = app.test_client()
        _login(client, admin_id)
        r = client.post(
            "/db_maintenance",
            data={"action": "clear_all_data", "mode": "full", "confirm_full_clear": "WRONG"},
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert SkillCurriculum.query.filter_by(skill_id=sid).count() == 1


def test_template_has_no_mojibake_keywords():
    template_path = Path("templates/db_maintenance.html")
    text = template_path.read_text(encoding="utf-8")
    bad_tokens = ["鞈", "摨", "蝣", "隢", "嚗", "", ""]
    for token in bad_tokens:
        assert token not in text


def test_template_core_no_confirm_field_and_single_column_buttons():
    template_path = Path("templates/db_maintenance.html")
    text = template_path.read_text(encoding="utf-8")
    assert "name=\"confirm_core_clear\"" not in text
    assert "id=\"coreConfirmClear\"" not in text
    assert text.count("刪除前預覽") == 1
    assert text.count("清空指定範圍教材資料") >= 1
    assert "grid-2" not in text
