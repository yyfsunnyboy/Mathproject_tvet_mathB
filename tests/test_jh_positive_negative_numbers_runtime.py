from __future__ import annotations

import base64
import uuid
from types import ModuleType, SimpleNamespace
import pytest

from app import create_app
from models import SkillCurriculum, SkillInfo, User, db
from skills.jh_數學1上_PositiveAndNegativeNumbers import generate, check

def test_100_runs_without_name_error() -> None:
    # 1. 100 runs loop
    text_count = 0
    image_count = 0
    
    for i in range(100):
        res = generate(level=1)
        assert isinstance(res, dict)
        assert "question_text" in res
        assert "answer" in res or "correct_answer" in res
        
        img = res.get("image_base64", "")
        if img:
            image_count += 1
            decoded = base64.b64decode(img)
            assert decoded.startswith(b"\x89PNG\r\n\x1a\n")
        else:
            text_count += 1
            
    print(f"\n100 runs stats: text_count={text_count}, image_count={image_count}")

def test_specific_number_line_generation(monkeypatch) -> None:
    # Force _generate_number_line_problem to verify image correctness
    from skills.jh_數學1上_PositiveAndNegativeNumbers import _generate_number_line_problem
    
    res = _generate_number_line_problem()
    assert isinstance(res, dict)
    assert res.get("image_base64") != ""
    decoded = base64.b64decode(res["image_base64"])
    assert decoded.startswith(b"\x89PNG\r\n\x1a\n")

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

def test_http_route_integration(monkeypatch) -> None:
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"legacy_route_check_2_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id

    # Use the real module for practice get_next_question test
    import skills.jh_數學1上_PositiveAndNegativeNumbers as real_mod
    monkeypatch.setattr("core.routes.practice.get_skill", lambda *a, **k: real_mod)
    real_session_get = db.session.get

    def fake_session_get(model, key, *args, **kwargs):
        if model == SkillInfo:
            return SimpleNamespace(input_type="text", skill_ch_name="正負數")
        return real_session_get(model, key, *args, **kwargs)

    monkeypatch.setattr("core.routes.practice.db.session.get", fake_session_get)
    monkeypatch.setattr(
        "core.routes.practice.db.session.query",
        lambda model_class, *a, **k: MockQuery(model_class),
    )

    client = app.test_client()
    _login(client, uid)

    resp = client.get("/get_next_question?skill=jh_數學1上_PositiveAndNegativeNumbers&level=1")
    data = resp.get_json() or {}

    assert resp.status_code == 200, data
    assert data["route_source"] == "legacy_skill"
    assert data["generator_mode"] == "legacy"
