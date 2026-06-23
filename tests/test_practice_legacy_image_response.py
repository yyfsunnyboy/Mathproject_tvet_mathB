import base64
import uuid
from types import ModuleType, SimpleNamespace

import pytest

from app import create_app
from core.routes.practice import get_current
from models import SkillCurriculum, SkillInfo, User, db

VALID_PNG_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
        sess["current_curriculum"] = "general"

class MockQuery:
    def __init__(self, model_class=None):
        self.model_class = model_class

    def filter_by(self, **kwargs):
        return self

    def join(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        if self.model_class == SkillCurriculum:
            return SimpleNamespace(difficulty_level=1)
        return SimpleNamespace(consecutive_correct=0)

    def all(self):
        return []

@pytest.fixture
def app_and_client(monkeypatch):
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"legacy_img_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id

    real_session_get = db.session.get

    def fake_session_get(model, key, *args, **kwargs):
        if model == SkillInfo:
            return SimpleNamespace(input_type="text", skill_ch_name="Legacy")
        return real_session_get(model, key, *args, **kwargs)

    monkeypatch.setattr("core.routes.practice.db.session.get", fake_session_get)
    monkeypatch.setattr(
        "core.routes.practice.db.session.query",
        lambda model_class, *a, **k: MockQuery(model_class),
    )

    client = app.test_client()
    _login(client, uid)
    
    return app, client

def test_legacy_skill_with_image(app_and_client, monkeypatch):
    app, client = app_and_client

    mod = ModuleType("skills.jh_數學1上_NumberLine")
    mod.__file__ = r"D:\Python\Mathproject_tvet_mathB\skills\jh_數學1上_NumberLine.py"

    def generate(level=1, **kwargs):
        return {
            "question_text": "請寫出數線上 P 點的座標。",
            "answer": "-2",
            "correct_answer": "-2",
            "image_base64": VALID_PNG_BASE64,
        }

    mod.generate = generate
    monkeypatch.setattr("core.routes.practice.get_skill", lambda *a, **k: mod)

    with app.test_request_context():
        resp = client.get("/get_next_question?skill=jh_數學1上_NumberLine&level=1")
        data = resp.get_json() or {}

        assert resp.status_code == 200, data
        assert data.get("image_base64") != ""
        assert data.get("image_base64") == VALID_PNG_BASE64

        decoded = base64.b64decode(data["image_base64"])
        assert decoded.startswith(b"\x89PNG\r\n\x1a\n")

        # Session should not contain image_base64
        with client.session_transaction() as sess:
            practice_ref = sess.get("current_practice_jh_數學1上_NumberLine", {})
            assert "image_base64" not in practice_ref

        # Check internal practice_ref using get_current
        # Wait, get_current is an internal flask session helper, we can't easily check without a request context
        # But practice_ref from session_transaction is enough

def test_legacy_skill_without_image(app_and_client, monkeypatch):
    app, client = app_and_client

    mod = ModuleType("skills.jh_test_legacy_no_img")
    mod.__file__ = r"D:\Python\Mathproject_tvet_mathB\skills\jh_test_legacy_no_img.py"

    def generate(level=1, **kwargs):
        return {
            "question_text": "文字題",
            "answer": "1",
            "correct_answer": "1",
        }

    mod.generate = generate
    monkeypatch.setattr("core.routes.practice.get_skill", lambda *a, **k: mod)

    resp = client.get("/get_next_question?skill=jh_test_legacy_no_img&level=1")
    data = resp.get_json() or {}

    assert resp.status_code == 200, data
    assert data["image_base64"] == ""
    assert data["question_text"] == "文字題"
