"""Practice question API keeps login protection and returns JSON to fetch callers."""

from __future__ import annotations

from urllib.parse import quote

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from models import User, db


SKILL = "vh_數學B2_SubSection_2_1_2"


@pytest.fixture()
def practice_auth_app(tmp_path, monkeypatch):
    import config

    uri = "sqlite:///" + str((tmp_path / "practice_auth.db").resolve()).replace("\\", "/")
    monkeypatch.setattr(config.Config, "SQLALCHEMY_DATABASE_URI", uri)
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        db.session.add_all([
            User(username="preview_admin", password_hash=generate_password_hash("pass1234"), role="admin"),
            User(username="practice_student", password_hash=generate_password_hash("pass1234"), role="student"),
            User(username="admin", password_hash=generate_password_hash("pass1234"), role="teacher"),
        ])
        db.session.commit()
    return app


@pytest.mark.parametrize("username", ["preview_admin", "practice_student"])
def test_authenticated_page_and_question_api(practice_auth_app, username):
    client = practice_auth_app.test_client()
    login = client.post("/login", data={"username": username, "password": "pass1234"})
    assert login.status_code == 302
    page = client.get(f"/practice/{quote(SKILL)}")
    assert page.status_code == 200
    response = client.get(f"/get_next_question?skill={quote(SKILL)}&level=1&gen_seed=1")
    assert response.status_code == 200
    assert response.is_json
    assert (response.get_json() or {}).get("question_text")


def test_anonymous_question_api_is_json_401(practice_auth_app):
    client = practice_auth_app.test_client()
    response = client.get(f"/get_next_question?skill={quote(SKILL)}", follow_redirects=False)
    assert response.status_code == 401
    assert response.is_json
    assert response.headers.get("Location") is None
    assert response.get_json()["error"] == "authentication_required"


def test_existing_guest_review_question_access_is_preserved(practice_auth_app):
    client = practice_auth_app.test_client()
    with client.session_transaction() as session:
        session["guest_demo"] = True
    response = client.get(f"/get_next_question?skill={quote(SKILL)}&level=1&gen_seed=1")
    assert response.status_code == 200
    assert (response.get_json() or {}).get("question_text")
