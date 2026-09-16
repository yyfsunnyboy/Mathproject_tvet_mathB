from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

import pytest

from app import create_app
from models import (
    PracticeAttempt,
    Progress,
    SkillCurriculum,
    SkillInfo,
    TextbookExample,
    User,
    db,
)


@pytest.fixture()
def mock_exam_app(tmp_path: Path):
    import config as app_config

    db_path = tmp_path / "vocational_mock_exam.db"
    previous_uri = app_config.Config.SQLALCHEMY_DATABASE_URI
    app_config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            users = [
                User(username="voc_mock", password_hash="x", role="student", curriculum_code="vocational"),
                User(username="jh_mock", password_hash="x", role="student", curriculum_code="junior_high"),
                User(username="teacher_mock", password_hash="x", role="teacher", curriculum_code="vocational"),
                User(username="admin_mock", password_hash="x", role="admin"),
            ]
            db.session.add_all(users)
            skills = [
                ("vh_數學B1_MockCoordinate", "坐標練習", True, "數學B1", "1 坐標系與函數圖形", "1-2", 1),
                ("vh_數學B2_MockTrig", "三角函數練習", True, "數學B2", "第1章 三角函數", "1-2", 2),
                ("vh_數學B3_MockEquation", "方程式練習", True, "數學B3", "第2章 方程式與不等式", "2-1", 3),
                ("vh_數學B3_MockEquationInactive", "未啟用方程式", False, "數學B3", "第3章 複數", "3-1", 4),
                ("vh_數學B4_MockCombination", "排列組合練習", True, "數學B4", "1 排列組合", "1-1", 5),
                ("vh_數學B4_MockProbability", "機率練習", True, "數學B4", "2 機率", "2-1", 6),
                ("vh_數學B4_MockStatistics", "統計練習", True, "數學B4", "3 統計", "3-1", 7),
            ]
            for skill_id, name, active, volume, chapter, section, order in skills:
                db.session.add(
                    SkillInfo(
                        skill_id=skill_id,
                        skill_en_name=skill_id,
                        skill_ch_name=name,
                        description="test",
                        gemini_prompt="test",
                        is_active=active,
                    )
                )
                db.session.add(
                    SkillCurriculum(
                        skill_id=skill_id,
                        curriculum="vocational",
                        grade=10 if volume in {"數學B1", "數學B2"} else 11,
                        volume=volume,
                        chapter=chapter,
                        section=section,
                        display_order=order,
                    )
                )
            db.session.commit()
            user_ids = {user.username: user.id for user in users}
        yield app, user_ids
    finally:
        app_config.Config.SQLALCHEMY_DATABASE_URI = previous_uri


def _login(client, user_id: int) -> None:
    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True


def test_vocational_home_shows_three_grade3_mock_exam_cards(mock_exam_app):
    app, user_ids = mock_exam_app
    client = app.test_client()
    _login(client, user_ids["voc_mock"])

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "三年級".encode() in response.data
    for label in ("第一次模擬考", "第二次模擬考", "第五次模擬考"):
        assert label.encode() in response.data


@pytest.mark.parametrize("exam_id", ["exam_1", "exam_2", "exam_5"])
def test_all_mock_exam_routes_are_available_to_vocational_students(mock_exam_app, exam_id: str):
    app, user_ids = mock_exam_app
    client = app.test_client()
    _login(client, user_ids["voc_mock"])

    response = client.get(f"/vocational/mock-exam/{exam_id}")

    assert response.status_code == 200


def test_exam_scope_reuses_only_enabled_existing_skill_links(mock_exam_app):
    app, user_ids = mock_exam_app
    client = app.test_client()
    _login(client, user_ids["voc_mock"])

    exam_1 = client.get("/vocational/mock-exam/exam_1")
    exam_5 = client.get("/vocational/mock-exam/exam_5")

    assert "/practice/vh_%E6%95%B8%E5%AD%B8B1_MockCoordinate".encode() in exam_1.data
    assert "vh_數學B3_MockEquationInactive".encode() not in exam_1.data
    assert "目前沒有已啟用的練習技能".encode() in exam_1.data
    assert "/practice/vh_%E6%95%B8%E5%AD%B8B4_MockCombination".encode() in exam_5.data
    assert "/practice/vh_%E6%95%B8%E5%AD%B8B4_MockProbability".encode() in exam_5.data
    assert "/practice/vh_%E6%95%B8%E5%AD%B8B4_MockStatistics".encode() in exam_5.data


def test_dashboard_and_mock_exam_share_card_mastery_and_practice_link(mock_exam_app):
    app, user_ids = mock_exam_app
    skill_id = "vh_數學B1_MockCoordinate"
    with app.app_context():
        for index in range(4):
            db.session.add(
                TextbookExample(
                    skill_id=skill_id,
                    source_curriculum="vocational",
                    source_volume="數學B1",
                    source_chapter="1 坐標系與函數圖形",
                    source_section="1-2",
                    source_description=f"reference {index}",
                    problem_text=f"question {index}",
                )
            )
        db.session.add(
            Progress(
                user_id=user_ids["voc_mock"],
                skill_id=skill_id,
                consecutive_correct=2,
            )
        )
        now = datetime.utcnow()
        for index, correct in enumerate((True, False, True)):
            db.session.add(
                PracticeAttempt(
                    student_id=user_ids["voc_mock"],
                    skill_id=skill_id,
                    is_correct=correct,
                    source="test",
                    created_at=now + timedelta(seconds=index),
                )
            )
        db.session.commit()

    client = app.test_client()
    _login(client, user_ids["voc_mock"])
    dashboard_html = client.get(
        "/dashboard?view=curriculum&curriculum=vocational"
        "&volume=數學B1&chapter=1%20坐標系與函數圖形"
    ).get_data(as_text=True)
    exam_html = client.get("/vocational/mock-exam/exam_5").get_data(as_text=True)

    for expected in (
        "status-learning",
        "熟練度 66.7%",
        "連續答對 2 / 4 題",
        "最近 3 題 | 累計作答 3 題",
        f"/practice/{quote(skill_id, safe='')}",
    ):
        assert expected in dashboard_html
        assert expected in exam_html


def test_dashboard_home_and_mock_exam_templates_use_shared_skill_card_partial():
    root = Path(__file__).resolve().parents[1]
    include = "include 'partials/skill_card.html'"
    for relative in (
        "templates/dashboard.html",
        "templates/vocational_student_home.html",
        "templates/vocational_mock_exam_scope.html",
    ):
        assert include in (root / relative).read_text(encoding="utf-8")


def test_exam_5_uses_all_enabled_vocational_b1_to_b4_curriculum_rows(mock_exam_app):
    app, user_ids = mock_exam_app
    client = app.test_client()
    _login(client, user_ids["voc_mock"])

    html = client.get("/vocational/mock-exam/exam_5").get_data(as_text=True)

    for volume in ("數學B1", "數學B2", "數學B3", "數學B4"):
        assert volume in html
    for chapter in (
        "1 坐標系與函數圖形",
        "第1章 三角函數",
        "第2章 方程式與不等式",
        "1 排列組合",
        "2 機率",
        "3 統計",
    ):
        assert chapter in html
    assert "未啟用方程式" not in html


def test_exam_5_keeps_shared_skill_in_each_existing_curriculum_chapter(mock_exam_app):
    app, user_ids = mock_exam_app
    with app.app_context():
        db.session.add(
            SkillCurriculum(
                skill_id="vh_數學B1_MockCoordinate",
                curriculum="vocational",
                grade=11,
                volume="數學B3",
                chapter="第4章 共用技能章節",
                section="4-1",
                display_order=8,
            )
        )
        db.session.commit()

    client = app.test_client()
    _login(client, user_ids["voc_mock"])
    html = client.get("/vocational/mock-exam/exam_5").get_data(as_text=True)

    assert "第4章 共用技能章節" in html
    assert html.count("vh_%E6%95%B8%E5%AD%B8B1_MockCoordinate") == 2


def test_exam_1_and_exam_2_keep_their_configured_scope(mock_exam_app):
    app, user_ids = mock_exam_app
    client = app.test_client()
    _login(client, user_ids["voc_mock"])

    exam_1 = client.get("/vocational/mock-exam/exam_1").get_data(as_text=True)
    exam_2 = client.get("/vocational/mock-exam/exam_2").get_data(as_text=True)

    assert "1 排列組合" not in exam_1
    assert "2 機率" not in exam_1
    assert "3 統計" not in exam_1
    assert "1 排列組合" not in exam_2
    assert "2 機率" not in exam_2
    assert "3 統計" not in exam_2


def test_mock_exam_route_rejects_non_vocational_student(mock_exam_app):
    app, user_ids = mock_exam_app
    client = app.test_client()
    _login(client, user_ids["jh_mock"])

    assert client.get("/vocational/mock-exam/exam_1").status_code == 403


@pytest.mark.parametrize("username", ["teacher_mock", "admin_mock"])
def test_teacher_and_admin_vocational_dashboard_preview_shows_grade3_cards(mock_exam_app, username: str):
    app, user_ids = mock_exam_app
    client = app.test_client()
    _login(client, user_ids[username])

    response = client.get("/dashboard?view=curriculum&curriculum=vocational")

    assert response.status_code == 200
    assert "一年級".encode() in response.data
    assert "二年級".encode() in response.data
    assert "三年級".encode() in response.data
    assert b"/vocational/mock-exam/exam_1" in response.data
    assert b"/vocational/mock-exam/exam_2" in response.data
    assert b"/vocational/mock-exam/exam_5" in response.data
    assert client.get("/vocational/mock-exam/exam_5").status_code == 200


def test_grade3_mock_exam_cards_do_not_render_for_non_vocational_curriculum(mock_exam_app):
    app, user_ids = mock_exam_app
    client = app.test_client()
    _login(client, user_ids["admin_mock"])

    response = client.get("/dashboard?view=curriculum&curriculum=junior_high")

    assert response.status_code == 200
    assert b"/vocational/mock-exam/" not in response.data


def test_mock_exam_route_rejects_unknown_exam_id(mock_exam_app):
    app, user_ids = mock_exam_app
    client = app.test_client()
    _login(client, user_ids["voc_mock"])

    assert client.get("/vocational/mock-exam/exam_99").status_code == 404
