from __future__ import annotations

import uuid
from types import ModuleType, SimpleNamespace

from app import create_app
from models import SkillCurriculum, SkillInfo, User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
        sess["current_curriculum"] = "general"


def test_get_next_question_legacy_jh_does_not_pass_seed_or_component_id(monkeypatch) -> None:
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"legacy_route_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id

    calls = []
    mod = ModuleType("skills.jh_test_legacy")
    mod.__file__ = r"D:\Python\Mathproject_tvet_mathB\skills\jh_test_legacy.py"

    def generate(level=1, **kwargs):
        calls.append({"level": level})
        return {
            "question_text": "legacy route question",
            "answer": "42",
        }

    mod.generate = generate

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
                return SimpleNamespace(difficulty_level=2)
            return SimpleNamespace(consecutive_correct=0)

        def all(self):
            return []

    monkeypatch.setattr("core.routes.practice.get_skill", lambda *a, **k: mod)
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

    resp = client.get("/get_next_question?skill=jh_test_legacy&level=2&gen_seed=123")
    data = resp.get_json() or {}

    assert resp.status_code == 200, data
    assert calls == [{"level": 2}]
    assert data["question_text"] == "legacy route question"
    assert data["new_question_text"] == "legacy route question"
    assert data["answer"] == "42"
    assert data["correct_answer"] == "42"
    assert data["answer_type"] == "text"
    assert data.get("generator_mode") in ("legacy", "gencode_wrapper")
    assert data.get("route_source") in ("legacy_skill", "gencode_wrapper")


def test_practice_real_route_does_not_bypass_resolver(monkeypatch) -> None:
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"legacy_route_check_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id

    calls = []
    mod = ModuleType("skills.jh_數學1上_PositiveAndNegativeNumbers")
    mod.__file__ = r"E:\Python\Mathproject_tvet_mathB\skills\jh_數學1上_PositiveAndNegativeNumbers.py"

    def generate(level=1, **kwargs):
        calls.append(kwargs)
        return {
            "question_text": "real legacy check question",
            "answer": "100",
        }

    mod.generate = generate

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

    monkeypatch.setattr("core.routes.practice.get_skill", lambda *a, **k: mod)
    real_session_get = db.session.get

    def fake_session_get(model, key, *args, **kwargs):
        if model == SkillInfo:
            return SimpleNamespace(input_type="text", skill_ch_name="RealLegacy")
        return real_session_get(model, key, *args, **kwargs)

    monkeypatch.setattr("core.routes.practice.db.session.get", fake_session_get)
    monkeypatch.setattr(
        "core.routes.practice.db.session.query",
        lambda model_class, *a, **k: MockQuery(model_class),
    )

    client = app.test_client()
    _login(client, uid)

    resp = client.get("/get_next_question?skill=jh_數學1上_PositiveAndNegativeNumbers&level=1&gen_seed=999")
    data = resp.get_json() or {}

    assert resp.status_code == 200, data
    assert len(calls) == 1
    assert calls[0] == {} # No seed or component_id should be received
    assert data["route_source"] == "legacy_skill"
    assert data["generator_mode"] == "legacy"

