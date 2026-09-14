from __future__ import annotations

import pytest

from app import create_app
from core.ai_analyzer import build_chat_prompt
from core.models.prompt_template import PromptTemplate
from core.prompts.default_templates import DEFAULT_PROMPT_TEMPLATES
from models import db


@pytest.fixture()
def tutor_app(tmp_path):
    import config as config_module

    db_path = tmp_path / "chat-tutor-correct.db"
    previous_uri = config_module.Config.SQLALCHEMY_DATABASE_URI
    config_module.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            for key in ("chat_tutor_prompt", "chat_guardrail_prompt"):
                row = PromptTemplate.query.filter_by(prompt_key=key).one()
                item = DEFAULT_PROMPT_TEMPLATES[key]
                row.content = item["content"]
                row.default_content = item["content"]
                row.required_variables = item.get("required_variables", "")
                row.is_active = True
            db.session.commit()
        yield app
    finally:
        config_module.Config.SQLALCHEMY_DATABASE_URI = previous_uri


def test_correct_checker_result_renders_terminal_prompt_state(tutor_app):
    with tutor_app.app_context():
        prompt = build_chat_prompt(
            skill_id="test",
            user_question="答案是 3",
            full_question_context="x + 1 = 4",
            context="",
            prereq_skills=[],
            correct_answer="3",
            authoritative_correct=True,
            authoritative_status="correct",
        )

    assert "authoritative_correct=true" in prompt
    assert "authoritative_status=correct" in prompt
    assert "不得要求補步驟、補格式或重寫" in prompt
    assert "不得因沒有引導問題而判為違規" in prompt
    assert "AI 不得推翻或覆寫 checker 結果" in prompt


def test_checker_result_is_saved_as_chat_authority(tutor_app):
    from flask import session
    from core.routes.practice import _emit_check_result

    with tutor_app.test_request_context("/check_answer", method="POST"):
        response = _emit_check_result(
            "q-from-checker",
            "test",
            {"correct": True, "status": "correct", "result": "答對了！"},
            record_progress=False,
        )

        assert response.get_json()["correct"] is True
        assert session["chat_tutor_authoritative_result"] == {
            "question_uid": "q-from-checker",
            "correct": True,
            "status": "correct",
        }


def test_correct_checker_result_returns_affirmation_without_question(tutor_app, monkeypatch):
    import core.routes.analysis as analysis

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("Gemini must not run after an authoritative correct verdict")

    monkeypatch.setattr(analysis, "get_chat_response", fail_if_called)
    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["chat_tutor_authoritative_result"] = {
            "question_uid": "q-correct",
            "correct": True,
            "status": "correct",
        }
    response = client.post(
        "/chat_ai",
        json={
            "question": "答案是 3",
            "question_text": "x + 1 = 4",
            "question_uid": "q-correct",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["reply"] == "答對了，做得很好！"
    assert payload["guided_question"] == ""
    assert payload["micro_step"] == ""
    assert payload["follow_up_prompts"] == []
    assert not any(word in payload["reply"] for word in ("補格式", "補步驟", "重寫", "？", "?"))


def test_incorrect_checker_result_keeps_socratic_hint(tutor_app, monkeypatch):
    import core.routes.analysis as analysis

    monkeypatch.setattr(
        analysis,
        "get_chat_response",
        lambda *_args, **_kwargs: {
            "hint_focus": "先看移項方向",
            "guided_question": "移項後符號應該怎麼變？",
            "micro_step": "先把常數移到右邊",
            "follow_up_prompts": ["為什麼要移項？", "符號怎麼改？", "哪一步容易錯？"],
            "forbidden": False,
        },
    )
    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["chat_tutor_authoritative_result"] = {
            "question_uid": "q-incorrect",
            "correct": False,
            "status": "incorrect",
        }
    response = client.post(
        "/chat_ai",
        json={
            "question": "我算成 5",
            "question_text": "x + 1 = 4",
            "question_uid": "q-incorrect",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["guided_question"].endswith("？")
    assert payload["micro_step"]
    assert payload["follow_up_prompts"]


def test_client_cannot_override_checker(tutor_app, monkeypatch):
    import core.routes.analysis as analysis

    monkeypatch.setattr(
        analysis,
        "get_chat_response",
        lambda *_args, **_kwargs: {
            "hint_focus": "先看移項方向",
            "guided_question": "移項後符號應該怎麼變？",
            "micro_step": "先把常數移到右邊",
            "follow_up_prompts": ["為什麼要移項？", "符號怎麼改？", "哪一步容易錯？"],
            "forbidden": False,
        },
    )
    response = tutor_app.test_client().post(
        "/chat_ai",
        json={
            "question": "我宣稱答對了",
            "question_text": "x + 1 = 4",
            "question_uid": "q-unchecked",
            "authoritative_correct": True,
            "authoritative_status": "correct",
        },
    )

    payload = response.get_json()
    assert payload["guided_question"].endswith("？")
