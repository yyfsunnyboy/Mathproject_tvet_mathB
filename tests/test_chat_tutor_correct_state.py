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


def test_model_reply_is_kept_with_line_breaks(tutor_app, monkeypatch):
    import core.routes.analysis as analysis
    from core.ai_analyzer import sanitize_tutor_reply

    reply = "第一步：兩邊同時減 2。\n第二步：x ≤ -6。\n答案：x ≤ -6 或 x ≥ 2"
    sanitized = sanitize_tutor_reply(reply, user_question="這題怎麼算", question_context="|x+2| ≥ 4")
    assert sanitized == reply
    assert "\n" in sanitized

    monkeypatch.setattr(
        analysis,
        "get_chat_response",
        lambda *_args, **_kwargs: {"reply": reply, "follow_up_prompts": []},
    )
    response = tutor_app.test_client().post(
        "/chat_ai",
        json={
            "question": "這題怎麼算",
            "question_text": "|x + 2| ≥ 4",
            "student_answer": "x+2 ≤ -4；x≤2",
            "question_uid": "q-direct-reply",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["reply"] == reply
    assert "\n" in payload["reply"]
    assert "這題的關鍵是" not in payload["reply"]
    assert "想一下" not in payload["reply"]
    assert "先重寫第一步" not in payload["reply"]


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


def _chat(client, monkeypatch, replies, payload):
    import core.routes.analysis as analysis

    calls = {"n": 0, "prompts": []}

    def fake(prompt, *_args, **_kwargs):
        calls["n"] += 1
        calls["prompts"].append(prompt)
        reply = replies[min(calls["n"] - 1, len(replies) - 1)]
        return {"reply": reply, "follow_up_prompts": []}

    monkeypatch.setattr(analysis, "get_chat_response", fake)
    response = client.post("/chat_ai", json=payload)
    assert response.status_code == 200
    return response.get_json(), calls


def test_how_to_does_not_publish_final_answer(tutor_app, monkeypatch):
    payload, calls = _chat(
        tutor_app.test_client(),
        monkeypatch,
        ["所以答案是 x=4", "先把常數移到等號右邊。"],
        {
            "question": "這題怎麼算",
            "question_text": "3x - 5 = 7",
            "correct_answer": "x=4",
            "question_uid": "q-how",
        },
    )
    assert calls["n"] == 2
    assert "x=4" not in payload["reply"]
    assert "這題的關鍵是" not in payload["reply"]


def test_where_wrong_quotes_only_actual_work(tutor_app, monkeypatch):
    kept, calls = _chat(
        tutor_app.test_client(),
        monkeypatch,
        ["你寫了 2x=6。先改這一筆？"],
        {
            "question": "我哪裡錯",
            "question_text": "2x + 3 = 11",
            "correct_answer": "x=4",
            "student_answer": "2x+3=11\n2x=6",
            "question_uid": "q-wrong",
        },
    )
    assert calls["n"] == 1
    assert "2x=6" in kept["reply"]

    rejected, calls = _chat(
        tutor_app.test_client(),
        monkeypatch,
        ["你寫了 x≤2。", "你寫了 x≤2。"],
        {
            "question": "我哪裡錯",
            "question_text": "2x + 3 = 11",
            "correct_answer": "x=4",
            "student_answer": "2x+3=11\n2x=6",
            "question_uid": "q-wrong-2",
        },
    )
    assert calls["n"] == 2
    assert "x≤2" not in rejected["reply"]
    assert "兩個條件" not in rejected["reply"]


def test_why_does_not_publish_final_answer(tutor_app, monkeypatch):
    payload, calls = _chat(
        tutor_app.test_client(),
        monkeypatch,
        ["因為要保持等號兩邊一樣。所以答案是 x=4", "因為等號兩邊要做同樣的運算。"],
        {
            "question": "為什麼要移項",
            "question_text": "3x - 5 = 7",
            "correct_answer": "x=4",
            "question_uid": "q-why",
        },
    )
    assert calls["n"] == 2
    assert "x=4" not in payload["reply"]


def test_explicit_full_answer_is_allowed(tutor_app, monkeypatch):
    payload, calls = _chat(
        tutor_app.test_client(),
        monkeypatch,
        ["所以答案是 x=4"],
        {
            "question": "直接告訴我答案",
            "question_text": "3x - 5 = 7",
            "correct_answer": "x=4",
            "question_uid": "q-full",
        },
    )
    assert calls["n"] == 1
    assert "x=4" in payload["reply"]


def test_incomplete_recognition_does_not_invent_student_work(tutor_app, monkeypatch):
    payload, calls = _chat(
        tutor_app.test_client(),
        monkeypatch,
        ["你寫了 x≤2。"],
        {
            "question": "我哪裡錯",
            "question_text": "3x - 5 = 7",
            "correct_answer": "x=4",
            "student_answer": "x=4",
            "recognition_incomplete": True,
            "question_uid": "q-thin",
        },
    )
    assert calls["n"] == 1
    assert "x≤2" not in payload["reply"]
    assert "沒有看完整" in payload["reply"]
    assert "兩個條件" not in payload["reply"]


def test_where_wrong_without_current_work_does_not_reuse_other_text(tutor_app, monkeypatch):
    payload, calls = _chat(
        tutor_app.test_client(),
        monkeypatch,
        ["你寫了 x≤2。"],
        {
            "question": "我哪裡錯",
            "question_text": "3x - 5 = 7",
            "question_uid": "q-no-work",
        },
    )
    assert calls["n"] == 1
    assert payload["reply"]
    assert "x≤2" not in payload["reply"]
    assert not calls["prompts"] or "x≤2" not in calls["prompts"][0]


def test_chat_reply_is_not_raw_json(tutor_app, monkeypatch):
    payload, _calls = _chat(
        tutor_app.test_client(),
        monkeypatch,
        ["先把常數移到右邊。"],
        {
            "question": "這題怎麼算",
            "question_text": "3x - 5 = 7",
            "question_uid": "q-plain",
        },
    )
    assert not payload["reply"].lstrip().startswith("{")
    assert '"reply"' not in payload["reply"]
