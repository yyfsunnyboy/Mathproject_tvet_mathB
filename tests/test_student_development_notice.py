from __future__ import annotations

import uuid

import pytest

from app import create_app
from models import User, db

NOTICE = "功能開發中"


def _client_for(curriculum_code: str | None):
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"dev_notice_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
            curriculum_code=curriculum_code,
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client


@pytest.mark.parametrize("curriculum_code", [None, "vocational"])
def test_student_home_has_no_development_notice(curriculum_code) -> None:
    resp = _client_for(curriculum_code).get("/dashboard")
    assert resp.status_code == 200
    assert NOTICE not in resp.get_data(as_text=True)


@pytest.mark.parametrize(
    "path",
    ["/practice?skill=vh_數學B4_CentralTendencyMeasures", "/student/diagnosis"],
)
def test_regular_pages_have_no_development_notice(path) -> None:
    resp = _client_for(None).get(path)
    assert resp.status_code == 200
    assert NOTICE not in resp.get_data(as_text=True)


@pytest.mark.parametrize(
    "path,original_marker",
    [
        ("/exam_upload_page", "page-header"),
        ("/mistake-notebook", 'id="mistake-entries-container"'),
        ("/add_mistake_page", 'id="add-mistake-form"'),
        ("/knowledge-graph", "page-header"),
        ("/practice/similar_questions", 'id="similar-upload-btn"'),
        ("/similar-questions-page", 'id="generate-button"'),
    ],
)
def test_development_pages_show_notice_and_keep_content(path, original_marker) -> None:
    resp = _client_for(None).get(path)
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert NOTICE in html
    assert html.count("data-development-notice") == 1
    assert original_marker in html
