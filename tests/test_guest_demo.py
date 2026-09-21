"""Integration coverage for the token-protected, read-only review mode."""
from __future__ import annotations

import pytest
from flask_login import current_user
from sqlalchemy import inspect, text
from types import SimpleNamespace

from app import app
from models import db, PracticeAttempt, Progress, StudentAbility, TextbookExample


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("REVIEW_DEMO_ENABLED", "1")
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def _enter(client):
    response = client.get("/review-demo")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/teacher_dashboard")


def _database_counts():
    with app.app_context():
        names = inspect(db.engine).get_table_names()
        return {
            name: db.session.execute(text(f'SELECT COUNT(*) FROM "{name}"')).scalar()
            for name in names
        }


def _database_schema():
    with app.app_context():
        inspector = inspect(db.engine)
        return {
            table: tuple(
                (column["name"], str(column["type"]), bool(column["nullable"]))
                for column in inspector.get_columns(table)
            )
            for table in inspector.get_table_names()
        }


def _database_state():
    with app.app_context():
        inspector = inspect(db.engine)
        state = {}
        for table in inspector.get_table_names():
            columns = [column["name"] for column in inspector.get_columns(table)]
            quoted = ", ".join(f'"{column}"' for column in columns)
            rows = db.session.execute(text(f'SELECT {quoted} FROM "{table}"')).all()
            state[table] = tuple(sorted(repr(tuple(row)) for row in rows))
        return state


def test_demo_disabled_is_not_available(client, monkeypatch):
    monkeypatch.setenv("REVIEW_DEMO_ENABLED", "0")
    assert client.get("/review-demo").status_code == 404


def test_correct_token_redirects_to_actual_admin_home(client):
    _enter(client)
    assert client.get("/teacher_dashboard").status_code == 200


def test_guest_is_not_a_flask_login_user(client):
    _enter(client)
    with client.session_transaction() as sess:
        assert sess["guest_demo"] is True
        assert "_user_id" not in sess
    assert current_user.is_authenticated is False


@pytest.mark.parametrize("path", [
    "/teacher_dashboard",
    "/curriculum",
    "/skills",
    "/teacher/analysis",
    "/api/teacher/classes",
])
def test_guest_can_browse_existing_admin_teacher_pages(client, path):
    _enter(client)
    response = client.get(path)
    assert response.status_code == 200


def test_guest_can_open_student_dashboard_with_no_personal_data(client):
    _enter(client)
    before = _database_state()

    response = client.get("/dashboard?view=all")

    assert response.status_code == 200
    assert b"TypeError" not in response.data
    assert _database_state() == before


def test_guest_can_open_and_grade_without_database_change(client):
    before = _database_counts()
    _enter(client)
    assert client.get("/free_response_practice").status_code == 200
    response = client.post(
        "/api/free_response/tree_diagram/submit",
        json={"variant": "early_stopping_game", "answer_text": "HH, HT, TH, TT"},
    )
    assert response.status_code == 200
    assert response.get_json()["ok"] is True
    assert _database_counts() == before


def _seed_guest_practice_question(client):
    with client.session_transaction() as sess:
        sess["current_data"] = {
            "skill": "guest_demo_choice_test",
            "skill_id": "guest_demo_choice_test",
            "question_uid": "guest-demo-question-1",
            "question_text": "1 + 1 = ?",
            "choices": ["1", "2", "3"],
            "answer": "B",
            "correct_answer": "B",
            "answer_type": "choice_label",
            "presentation_mode": "single_choice",
        }


def _guest_learning_counts():
    with app.app_context():
        return {
            "practice_attempts": db.session.query(PracticeAttempt).count(),
            "progress": db.session.query(Progress).count(),
            "mastery": db.session.query(StudentAbility).count(),
        }


def test_guest_practice_submit_returns_normal_json_without_learning_mutation(client):
    _enter(client)
    assert client.get("/practice/guest_demo_choice_test").status_code == 200
    before = _guest_learning_counts()

    _seed_guest_practice_question(client)
    correct = client.post("/check_answer", json={"answer": "B"})
    assert correct.status_code == 200
    assert correct.content_type.startswith("application/json")
    assert correct.get_json()["correct"] is True
    assert "result" in correct.get_json()

    _seed_guest_practice_question(client)
    wrong = client.post("/check_answer", json={"answer": "A"})
    assert wrong.status_code == 200
    assert wrong.content_type.startswith("application/json")
    assert wrong.get_json()["correct"] is False
    assert "result" in wrong.get_json()

    assert _guest_learning_counts() == before
    with client.session_transaction() as sess:
        assert "review_history" not in sess
        assert "skill_stats" not in sess
        assert "adaptive_state" not in sess


def test_guest_practice_owner_never_reads_anonymous_id(monkeypatch):
    import core.practice_question_store as store

    class StrictAnonymous:
        is_authenticated = False

        @property
        def id(self):
            raise AssertionError("AnonymousUser.id must not be read")

    monkeypatch.setattr(store, "current_user", StrictAnonymous())
    with app.test_request_context("/check_answer"):
        owner = store.get_practice_owner_key()
        assert owner.startswith("sid:")


def test_guest_check_answer_uses_session_owner_without_409(client):
    import core.practice_question_store as store

    _enter(client)
    uid = "guest-owned-runtime-question"
    owner_sid = "guest-owner-test"
    skill_id = "guest_demo_choice_test"
    with client.session_transaction() as sess:
        sess["_practice_owner_sid"] = owner_sid
        sess["current_skill_id"] = skill_id
        sess["current_question_uid"] = uid
        sess["practice_ref"] = {"skill_id": skill_id, "question_uid": uid}
    store._STORE[f"sid:{owner_sid}"] = {
        uid: {
            "skill": skill_id,
            "skill_id": skill_id,
            "question_uid": uid,
            "question_text": "1 + 1 = ?",
            "choices": [
                {"label": "A", "text": "1"},
                {"label": "B", "text": "2"},
            ],
            "answer": "B",
            "correct_answer": "B",
            "answer_type": "choice_label",
            "presentation_mode": "single_choice",
            "status": store.STATUS_GENERATED,
            "grade_result": None,
        }
    }

    response = client.post(
        "/check_answer",
        json={"answer": "B", "skill_id": skill_id, "question_uid": uid},
    )

    assert response.status_code == 200
    assert response.content_type.startswith("application/json")
    assert response.get_json()["correct"] is True
    assert response.get_json().get("stale_question") is not True


def test_guest_ai_handwriting_is_json_and_does_not_persist(client, monkeypatch):
    import core.routes.adaptive_api as adaptive_api

    _enter(client)
    _seed_guest_practice_question(client)
    before = _database_state()

    monkeypatch.setattr(
        adaptive_api,
        "_call_ai_handwriting_checker",
        lambda _payload, _ctx: {
            "recognized_answer": "2",
            "recognized_expression": "2",
            "confidence": 0.99,
        },
    )
    response = client.post(
        "/api/practice/ai-check-handwriting",
        json={
            "image_base64": "data:image/png;base64,aGVsbG8=",
            "question_uid": "guest-demo-question-1",
            "skill_id": "guest_demo_choice_test",
            "question_text": "1 + 1 = ?",
        },
    )

    assert response.status_code == 200
    assert response.content_type.startswith("application/json")
    assert response.headers.get("Location") is None
    assert response.get_json() is not None
    assert _database_state() == before
    with client.session_transaction() as sess:
        assert "conversation_history" not in sess


def test_guest_can_generate_v3_preview_without_any_database_change(client, monkeypatch):
    from core.gencode.services import v3_component_preview_service as preview_service

    original_get = db.session.get

    def fake_get(model, ident):
        if model is TextbookExample and ident == 987654:
            return SimpleNamespace(id=ident, skill_id="vh_preview_test")
        return original_get(model, ident)

    def fake_generate(example_id, seed=42, timeout_seconds=5.0, *, persist=False):
        assert example_id == 987654
        assert persist is False
        return {
            "success": True,
            "example_id": example_id,
            "skill_id": "vh_preview_test",
            "component_id": "src_987654",
            "artifact_source": "dryrun",
            "artifact_path": "read-only-test-component",
            "problem_type_id": "preview_test",
            "question": {
                "question_text": "1 + 1 = ?",
                "choices": [],
                "answer_type": "short_answer",
                "answer": "2",
            },
        }

    monkeypatch.setattr(db.session, "get", fake_get)
    monkeypatch.setattr(preview_service, "generate_component_preview", fake_generate)
    before = _database_state()
    _enter(client)

    response = client.post("/admin/textbook-examples/987654/v3-preview/generate")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["question"]["question_text"] == "1 + 1 = ?"
    assert _database_state() == before


@pytest.mark.parametrize("path,payload", [
    ("/chat_ai", {}),
    ("/api/rag_chat", {}),
    ("/api/adaptive/submit_and_get_next", {}),
])
def test_guest_ai_and_adaptive_posts_reach_existing_handlers(client, path, payload):
    _enter(client)
    response = client.post(path, json=payload)
    assert response.status_code != 403


@pytest.mark.parametrize("method,path", [
    ("post", "/classes/create"),
    ("post", "/skills/add"),
    ("delete", "/api/prompts/1"),
    ("post", "/admin/init_db"),
    ("post", "/admin/ai_prompt_settings/update"),
    ("post", "/test_api_key"),
])
def test_guest_mutations_are_blocked_as_api(client, method, path):
    before = _database_counts()
    _enter(client)
    response = getattr(client, method)(path, json={})
    assert response.status_code == 403
    assert response.get_json() == {
        "success": False,
        "error": "login_required_for_persistence",
    }
    assert _database_counts() == before


def test_guest_cannot_open_database_maintenance(client):
    _enter(client)
    response = client.get("/db_maintenance")
    assert response.status_code == 302


def test_web_mutation_flashes_and_preserves_schema_and_data(client):
    schema_before = _database_schema()
    data_before = _database_counts()
    _enter(client)
    response = client.post(
        "/classes/create",
        data={"name": "must-not-be-created"},
        headers={"Referer": "/teacher_dashboard"},
    )
    assert response.status_code == 302
    with client.session_transaction() as sess:
        messages = [message for _category, message in sess.get("_flashes", [])]
    assert "此功能需要登入後才能儲存。展示模式不會修改系統資料。" in messages
    assert _database_schema() == schema_before
    assert _database_counts() == data_before


def test_non_demo_auth_behavior_is_unchanged(client):
    response = client.get("/teacher_dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
