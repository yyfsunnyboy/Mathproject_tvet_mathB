from __future__ import annotations

from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from models import User, db


@pytest.fixture()
def login_app(tmp_path: Path):
    import config as app_config

    db_path = tmp_path / "login_role_auto_routing.db"
    previous_uri = app_config.Config.SQLALCHEMY_DATABASE_URI
    app_config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            db.session.add_all(
                [
                    User(username="route_student", password_hash=generate_password_hash("pass1234"), role="student"),
                    User(username="route_teacher", password_hash=generate_password_hash("pass1234"), role="teacher"),
                    User(username="route_admin", password_hash=generate_password_hash("pass1234"), role="admin"),
                ]
            )
            db.session.commit()
        yield app
    finally:
        app_config.Config.SQLALCHEMY_DATABASE_URI = previous_uri


@pytest.mark.parametrize(
    ("username", "destination"),
    [
        ("route_student", "/dashboard"),
        ("route_teacher", "/teacher_dashboard"),
        ("route_admin", "/teacher_dashboard"),
    ],
)
def test_login_redirects_from_database_role(login_app, username: str, destination: str):
    response = login_app.test_client().post(
        "/login",
        data={"username": username, "password": "pass1234"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(destination)


def test_wrong_password_keeps_existing_login_failure(login_app):
    response = login_app.test_client().post(
        "/login",
        data={"username": "route_student", "password": "wrong"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "帳號或密碼錯誤".encode() in response.data


def test_forged_role_cannot_change_database_identity(login_app):
    client = login_app.test_client()
    response = client.post(
        "/login",
        data={"username": "route_student", "password": "pass1234", "role": "admin"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with client.session_transaction() as session:
        user_id = int(session["_user_id"])
    with login_app.app_context():
        assert db.session.get(User, user_id).role == "student"


def test_login_page_has_no_role_selector(login_app):
    response = login_app.test_client().get("/login")

    assert response.status_code == 200
    assert b'name="role"' not in response.data
    assert "身分:".encode() not in response.data
