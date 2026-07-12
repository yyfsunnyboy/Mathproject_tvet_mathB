# -*- coding: utf-8 -*-
"""
公開唯讀 Demo 模式測試 (/demo, /demo/practice, /demo/teacher-overview)。

驗證重點：
1. 未登入可存取 demo 路由。
2. 未登入不可存取正式 /teacher_dashboard（仍會被導向登入頁）。
3. demo 模式的 POST 端點不會寫入資料庫（純固定假資料運算）。
4. demo 頁面內容不含任何真實學生使用者名稱。
"""
from __future__ import annotations

import uuid

import pytest

from app import create_app
from models import User, db


@pytest.fixture()
def app_ctx():
    import config as _cfg
    from pathlib import Path

    db_path = Path("reports") / f"pytest_demo_mode_{uuid.uuid4().hex[:8]}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        real_username = f"real_student_{uuid.uuid4().hex[:6]}"
        with app.app_context():
            student = User(username=real_username, password_hash="x", role="student")
            teacher = User(username=f"real_teacher_{uuid.uuid4().hex[:6]}", password_hash="x", role="teacher")
            db.session.add(student)
            db.session.add(teacher)
            db.session.commit()
            yield app, real_username
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        try:
            if db_path.exists():
                db_path.unlink()
        except OSError:
            pass


def _user_count(app) -> int:
    with app.app_context():
        return db.session.query(User).count()


def test_demo_index_accessible_without_login(app_ctx):
    app, _ = app_ctx
    client = app.test_client()
    resp = client.get("/demo")
    assert resp.status_code == 200
    assert "公開展示模式".encode("utf-8") in resp.data
    assert "資料修改功能已停用".encode("utf-8") in resp.data


def test_demo_practice_accessible_without_login(app_ctx):
    app, _ = app_ctx
    client = app.test_client()
    resp = client.get("/demo/practice")
    assert resp.status_code == 200
    assert "公開展示模式".encode("utf-8") in resp.data


def test_demo_teacher_overview_accessible_without_login(app_ctx):
    app, _ = app_ctx
    client = app.test_client()
    resp = client.get("/demo/teacher-overview")
    assert resp.status_code == 200
    assert "公開展示模式".encode("utf-8") in resp.data


def test_teacher_dashboard_still_requires_login(app_ctx):
    app, _ = app_ctx
    client = app.test_client()
    resp = client.get("/teacher_dashboard", follow_redirects=False)
    # Flask-Login redirects unauthenticated users to the login view.
    assert resp.status_code in (301, 302)
    assert "/login" in resp.headers.get("Location", "")


def test_demo_check_answer_does_not_write_to_database(app_ctx):
    app, _ = app_ctx
    client = app.test_client()
    before = _user_count(app)

    correct_resp = client.post("/demo/practice/check", json={"answer": "4"})
    assert correct_resp.status_code == 200
    body = correct_resp.get_json()
    assert body["demo_mode"] is True
    assert body["correct"] is True

    wrong_resp = client.post("/demo/practice/check", json={"answer": "999"})
    assert wrong_resp.status_code == 200
    assert wrong_resp.get_json()["correct"] is False

    after = _user_count(app)
    assert after == before


def test_demo_hint_does_not_write_to_database(app_ctx):
    app, _ = app_ctx
    client = app.test_client()
    before = _user_count(app)

    resp = client.post("/demo/practice/hint")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["demo_mode"] is True
    assert "hint" in body

    after = _user_count(app)
    assert after == before


def test_demo_pages_contain_no_real_student_data(app_ctx):
    app, real_username = app_ctx
    client = app.test_client()

    for path in ("/demo", "/demo/practice", "/demo/teacher-overview"):
        resp = client.get(path)
        assert resp.status_code == 200
        assert real_username.encode("utf-8") not in resp.data
        # Only the fixed demo placeholder names should appear, never a live User row.
        assert "示範學生".encode("utf-8") in resp.data or path != "/demo/teacher-overview"
