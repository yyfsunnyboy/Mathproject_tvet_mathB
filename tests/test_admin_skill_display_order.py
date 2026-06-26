# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from app import create_app
from core.utils import get_skills_by_volume_chapter
from models import SkillCurriculum, SkillInfo, User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _make_skill(
    *,
    skill_id: str,
    ch_name: str,
    display_order: int,
    volume: str = "數學B4",
    chapter: str = "3 統計資料的分析",
    section: str = "3-1",
) -> None:
    skill = SkillInfo(
        skill_id=skill_id,
        skill_en_name=skill_id,
        skill_ch_name=ch_name,
        category="statistics",
        description="test",
        input_type="text",
        gemini_prompt="prompt",
        consecutive_correct_required=3,
        is_active=True,
        order_index=999,
    )
    curriculum = SkillCurriculum(
        skill_id=skill_id,
        curriculum="vocational",
        grade=10,
        volume=volume,
        chapter=chapter,
        section=section,
        display_order=display_order,
    )
    db.session.add(skill)
    db.session.add(curriculum)
    db.session.commit()


@pytest.fixture()
def app_ctx():
    import config as _cfg

    db_path = Path("reports") / f"pytest_skill_display_order_{uuid.uuid4().hex[:8]}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            teacher = User(username=f"teacher_{uuid.uuid4().hex[:6]}", password_hash="x", role="teacher")
            student = User(username=f"student_{uuid.uuid4().hex[:6]}", password_hash="x", role="student")
            db.session.add(teacher)
            db.session.add(student)
            db.session.commit()
            yield app, teacher.id, student.id
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        try:
            if db_path.exists():
                db_path.unlink()
        except OSError:
            pass


def test_update_display_order_persists(app_ctx):
    app, teacher_id, _student_id = app_ctx
    client = app.test_client()
    _login(client, teacher_id)

    skill_id = "vh_test_order_skill_a"
    _make_skill(skill_id=skill_id, ch_name="技能A", display_order=999)

    payload = {
        "skill_en_name": skill_id,
        "skill_ch_name": "技能A",
        "category": "statistics",
        "description": "test",
        "input_type": "text",
        "gemini_prompt": "prompt",
        "consecutive_correct_required": 3,
        "is_active": True,
        "display_order": 2,
        "curriculum": "vocational",
        "grade": 10,
        "volume": "數學B4",
        "chapter": "3 統計資料的分析",
        "section": "3-1",
    }
    response = client.post(
        f"/skills/edit/{skill_id}",
        json=payload,
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True

    row = SkillCurriculum.query.filter_by(skill_id=skill_id).first()
    assert row is not None
    assert row.display_order == 2

    details = client.get(
        f"/skills/{skill_id}/details"
        f"?curriculum=vocational&grade=10&volume=數學B4&chapter=3 統計資料的分析&section=3-1"
    )
    assert details.get_json()["data"]["display_order"] == 2


def test_admin_and_student_skill_ordering(app_ctx):
    app, teacher_id, student_id = app_ctx
    client = app.test_client()

    volume = "數學B4"
    chapter = "3 統計資料的分析"
    section = "3-1"

    _make_skill(skill_id="vh_order_skill_b", ch_name="技能B", display_order=10, volume=volume, chapter=chapter, section=section)
    _make_skill(skill_id="vh_order_skill_c", ch_name="技能C", display_order=20, volume=volume, chapter=chapter, section=section)
    _make_skill(skill_id="vh_order_skill_a", ch_name="技能A", display_order=30, volume=volume, chapter=chapter, section=section)

    _login(client, teacher_id)
    admin_resp = client.get(
        "/skills"
        f"?f_curriculum=vocational&f_grade=10&f_volume={volume}"
        f"&f_chapter={chapter}&f_section={section}"
    )
    assert admin_resp.status_code == 200
    admin_html = admin_resp.get_data(as_text=True)
    admin_pos_b = admin_html.index("技能B")
    admin_pos_c = admin_html.index("技能C")
    admin_pos_a = admin_html.index("技能A")
    assert admin_pos_b < admin_pos_c < admin_pos_a

    with app.app_context():
        student_skills = get_skills_by_volume_chapter(volume, chapter)
        ordered_names = [s["skill_ch_name"] for s in student_skills if s["section"] == section]
        assert ordered_names[:3] == ["技能B", "技能C", "技能A"]


def test_invalid_display_order_returns_400(app_ctx):
    app, teacher_id, _student_id = app_ctx
    client = app.test_client()
    _login(client, teacher_id)

    skill_id = "vh_test_invalid_order"
    _make_skill(skill_id=skill_id, ch_name="無效排序測試", display_order=5)

    response = client.post(
        f"/skills/edit/{skill_id}",
        json={
            "skill_en_name": skill_id,
            "skill_ch_name": "無效排序測試",
            "category": "statistics",
            "description": "test",
            "input_type": "text",
            "gemini_prompt": "prompt",
            "consecutive_correct_required": 3,
            "display_order": "abc",
            "curriculum": "vocational",
            "grade": 10,
            "volume": "數學B4",
            "chapter": "3 統計資料的分析",
            "section": "3-1",
        },
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert "排序順序必須是整數" in body["message"]


def test_admin_skills_page_has_no_mojibake_flash_source(app_ctx):
    app, teacher_id, _student_id = app_ctx
    client = app.test_client()
    _login(client, teacher_id)

    skill_id = "vh_test_flash_encoding"
    _make_skill(skill_id=skill_id, ch_name="編碼測試", display_order=1)

    response = client.post(
        f"/skills/edit/{skill_id}",
        data={
            "skill_en_name": skill_id,
            "skill_ch_name": "編碼測試",
            "category": "statistics",
            "description": "test",
            "input_type": "text",
            "gemini_prompt": "prompt",
            "consecutive_correct_required": 3,
            "display_order": 1,
            "curriculum": "vocational",
            "grade": 10,
            "volume": "數學B4",
            "chapter": "3 統計資料的分析",
            "section": "3-1",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "技能資料已更新" in html
    assert "?皝" not in html
    assert "技能管理中心" in html
