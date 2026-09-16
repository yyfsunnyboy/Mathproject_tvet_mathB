from __future__ import annotations

import pytest

from app import create_app
from core.ai_conversation_context import (
    AI_CONVERSATION_MAX_TURNS,
    add_turn,
    format_for_prompt,
    get_context,
)
from core.practice_question_store import _STORE
from core.models.prompt_template import PromptTemplate
from core.prompts.default_templates import DEFAULT_PROMPT_TEMPLATES
from models import db


@pytest.fixture()
def tutor_app(tmp_path):
    import config as config_module

    db_path = tmp_path / "per-question-context.db"
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
        _STORE.clear()


def _install(owner: str, *uids: str) -> None:
    _STORE[owner] = {
        uid: {"question_uid": uid, "skill_id": "test", "status": "generated"}
        for uid in uids
    }


def test_second_chat_question_can_see_first_turn(tutor_app, monkeypatch):
    import core.routes.analysis as analysis

    owner = "sid:conversation-chat"
    _install(owner, "q-chat")
    prompts: list[str] = []

    def fake_chat(prompt, **_kwargs):
        prompts.append(prompt)
        return {
            "hint_focus": "先整理式子",
            "guided_question": "你先前提到的那一步用了哪個規則？",
            "micro_step": "先核對第一步",
            "follow_up_prompts": [],
            "forbidden": False,
        }

    monkeypatch.setattr(analysis, "get_chat_response", fake_chat)
    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["_practice_owner_sid"] = "conversation-chat"

    first = client.post(
        "/chat_ai",
        json={"question_uid": "q-chat", "question": "我想到斜率法和畫圖法兩種方法", "question_text": "x+1=4"},
    )
    second = client.post(
        "/chat_ai",
        json={"question_uid": "q-chat", "question": "所以兩種方法都可以嗎？", "question_text": "x+1=4"},
    )

    assert first.status_code == second.status_code == 200
    assert "斜率法和畫圖法兩種方法" in prompts[1]
    assert "tutor/tutor_reply" in prompts[1]
    assert "指涉語句承接規則" in prompts[1]
    assert "回覆必須先用一句短句明確說出你承接的是什麼" in prompts[1]


def test_handwriting_then_chat_and_chat_then_handwriting_share_provider(tutor_app):
    from core.routes.analysis import _handwriting_feedback_second_prompt

    with tutor_app.test_request_context("/"):
        _install("sid:cross-mode", "q-shared")
        from flask import session

        session["_practice_owner_sid"] = "cross-mode"
        add_turn(
            "q-shared",
            role="student",
            kind="handwriting_feedback",
            content="辨識式：x=5\n回饋摘要：移項符號需再檢查",
            authoritative_correct=False,
            authoritative_status="incorrect",
        )
        chat_context = format_for_prompt("q-shared")
        assert "移項符號需再檢查" in chat_context

        add_turn("q-shared", role="student", kind="chat_message", content="為什麼要變號？")
        prompt = _handwriting_feedback_second_prompt(
            {"status": "incorrect", "recognized_expression": "x=5"},
            "x+1=4",
            "",
            "",
            "test",
            format_for_prompt("q-shared"),
        )
        assert "為什麼要變號？" in prompt


def test_context_isolated_by_question_uid_and_bounded(tutor_app):
    with tutor_app.test_request_context("/"):
        from flask import session

        session["_practice_owner_sid"] = "isolation"
        _install("sid:isolation", "q-old", "q-new")
        add_turn("q-old", role="student", kind="chat_message", content="舊題內容")
        assert not get_context("q-new")

        for index in range(AI_CONVERSATION_MAX_TURNS + 3):
            add_turn("q-new", role="student", kind="chat_message", content=f"turn-{index}")
        turns = get_context("q-new")
        assert len(turns) == AI_CONVERSATION_MAX_TURNS
        assert turns[0]["content"] == "turn-3"


def test_history_does_not_store_correct_answer_field_or_change_grade(tutor_app, monkeypatch):
    import core.routes.analysis as analysis

    owner = "sid:authority"
    _install(owner, "q-correct")
    _STORE[owner]["q-correct"]["grade_result"] = {"correct": True, "result": "答對了"}
    add_called = {"llm": False}

    def fail_llm(*_args, **_kwargs):
        add_called["llm"] = True
        raise AssertionError("authoritative correct must bypass the LLM")

    monkeypatch.setattr(analysis, "get_chat_response", fail_llm)
    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["_practice_owner_sid"] = "authority"
        sess["chat_tutor_authoritative_result"] = {
            "question_uid": "q-correct",
            "correct": True,
            "status": "correct",
        }
    response = client.post(
        "/chat_ai",
        json={"question_uid": "q-correct", "question": "可是舊提示說我錯", "question_text": "x+1=4"},
    )

    assert response.get_json()["reply"] == "答對了，做得很好！"
    assert add_called["llm"] is False
    assert _STORE[owner]["q-correct"]["grade_result"]["correct"] is True
    for turn in _STORE[owner]["q-correct"]["ai_conversation_context"]:
        assert "correct_answer" not in turn


def test_chat_context_is_supplied_to_drawing_checker(tutor_app, monkeypatch):
    import core.ai_analyzer as analyzer
    from flask import session
    from core.handwriting_ai_check import HandwritingCheckContext
    from core.routes.adaptive_api import _call_ai_handwriting_checker

    with tutor_app.test_request_context("/"):
        session["_practice_owner_sid"] = "chat-to-drawing"
        _install("sid:chat-to-drawing", "q-drawing")
        add_turn(
            "q-drawing",
            role="student",
            kind="chat_message",
            content="我想用斜率法和畫圖法比較",
        )
        captured: dict[str, str] = {}

        def fake_analyze(**kwargs):
            captured["context"] = kwargs["context"]
            return {"feedback": "請補上橫軸"}

        monkeypatch.setattr(analyzer, "analyze", fake_analyze)
        _call_ai_handwriting_checker(
            {"image_base64": "data:image/png;base64,abc"},
            HandwritingCheckContext(question_uid="q-drawing", question_text="畫出函數圖形"),
        )
        assert "我想用斜率法和畫圖法比較" in captured["context"]


def test_drawing_feedback_persists_for_chat_and_next_drawing(tutor_app):
    from flask import session
    from core.handwriting_ai_check import HandwritingCheckContext
    from core.routes.adaptive_api import _persist_drawing_feedback

    with tutor_app.test_request_context("/"):
        session["_practice_owner_sid"] = "drawing-shared"
        _install("sid:drawing-shared", "q-drawing", "q-next")
        ctx = HandwritingCheckContext(question_uid="q-drawing", question_text="畫出函數圖形")
        _persist_drawing_feedback(
            ctx,
            {
                "feedback": "缺少橫軸、縱軸、function_line",
                "final_answer_correct": False,
                "raw_payload": {"image_base64": "must-not-be-stored"},
            },
        )

        prompt_context = format_for_prompt("q-drawing")
        assert "student_action=drawing_check" in prompt_context
        assert "feedback_summary=缺少橫軸、縱軸、function_line" in prompt_context
        assert "image_base64" not in prompt_context
        assert "must-not-be-stored" not in prompt_context
        # The same formatted history is consumed by both chat and a subsequent drawing check.
        assert "drawing_feedback" in prompt_context
        assert not get_context("q-next")
