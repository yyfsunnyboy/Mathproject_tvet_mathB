from __future__ import annotations

import re

from werkzeug.security import generate_password_hash

from app import app
from core.mistake_notebook_service import create_active_mistake
from models import PracticeAttempt, SkillCurriculum, SkillInfo, User, db


SKILL = "test_notebook_cross_device"
CURRICULUM = "test_notebook_cross_device_curriculum"
PASSWORD = "pw-cross-device"
ANDROID_UA = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36"
)


def _student(username: str) -> User:
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username, password_hash=generate_password_hash(PASSWORD, method="pbkdf2:sha256"), role="student")
        db.session.add(user)
        db.session.flush()
    return user


def _form_login(username: str, user_agent: str | None = None):
    client = app.test_client()
    headers = {"User-Agent": user_agent} if user_agent else {}
    response = client.post("/login", data={"username": username, "password": PASSWORD}, headers=headers)
    assert response.status_code == 302 and "/login" not in response.location
    return client, headers


def _tree_count(client, headers) -> int:
    response = client.get("/api/mistake-notebook/tree", headers=headers)
    assert response.status_code == 200
    return sum(item["count"] for item in response.get_json()["curricula"])


def test_same_student_sees_same_mistakes_across_devices_and_others_are_isolated() -> None:
    with app.app_context():
        owner = _student("notebook_cross_device_owner")
        other = _student("notebook_cross_device_other")
        if db.session.get(SkillInfo, SKILL) is None:
            db.session.add(SkillInfo(
                skill_id=SKILL, skill_en_name=SKILL, skill_ch_name="跨裝置技能",
                category="test", description="test", gemini_prompt="test",
            ))
        if not SkillCurriculum.query.filter_by(skill_id=SKILL, curriculum=CURRICULUM).first():
            db.session.add(SkillCurriculum(
                skill_id=SKILL, curriculum=CURRICULUM, grade=1,
                volume="第一冊", chapter="第 1 章", section="1-1", display_order=1,
            ))
        attempt = PracticeAttempt(
            student_id=owner.id, skill_id=SKILL, question_text="$x+1=2$",
            user_answer="0", expected_answer="1", is_correct=False,
            source="general_practice", question_uid="cross-device-uid",
        )
        db.session.add(attempt)
        db.session.flush()
        entry = create_active_mistake(student_id=owner.id, attempt=attempt, question={"question_text": "求 $x$"}, user_answer="0")
        db.session.commit()
        owner_name, other_name, entry_id = owner.username, other.username, entry.id

    desktop, desktop_headers = _form_login(owner_name)
    android, android_headers = _form_login(owner_name, ANDROID_UA)
    stranger, stranger_headers = _form_login(other_name, ANDROID_UA)

    assert desktop.get("/mistake-notebook").status_code == 200
    page = android.get("/mistake-notebook", headers=android_headers)
    assert page.status_code == 200
    assert "mistake-notebook-tree" in page.get_data(as_text=True)

    assert _tree_count(desktop, desktop_headers) == _tree_count(android, android_headers) >= 1
    assert _tree_count(stranger, stranger_headers) == 0
    assert stranger.get(f"/mistake-notebook/review/{entry_id}", headers=stranger_headers).location.endswith("/mistake-notebook")

    anonymous = app.test_client().get("/mistake-notebook")
    assert anonymous.status_code == 302 and "/login" in anonymous.location


def test_student_navbar_logout_cannot_overlap_primary_pills() -> None:
    with open("templates/_student_navbar.html", encoding="utf-8") as handle:
        css = handle.read()
    primary = re.search(r"\.student-navbar__primary\s*\{([^}]*)\}", css).group(1)
    menu = re.search(r"\.student-navbar__menu\s*\{([^}]*)\}", css).group(1)
    assert "flex-shrink: 0" in primary and "min-width: 0" not in primary
    assert "justify-content: flex-start" in menu
