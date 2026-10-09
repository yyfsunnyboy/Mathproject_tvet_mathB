from __future__ import annotations

import base64
import io
import json
import threading

import pytest
from PIL import Image

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


def _image_data_url() -> str:
    image = Image.new("RGB", (16, 16), "white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


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
        uid: {
            "question_uid": uid,
            "skill_id": "test",
            "question_text": "x+1=4",
            "correct_answer": "3",
            "status": "generated",
        }
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
    assert len(first.get_json()["suggested_questions"]) == 3
    assert len(second.get_json()["suggested_questions"]) == 3
    assert second.get_json()["suggested_questions"] != first.get_json()["suggested_questions"]
    assert "斜率法和畫圖法兩種方法" in prompts[1]
    assert "tutor/tutor_reply" in prompts[1]
    assert "指涉語句承接規則" in prompts[1]
    assert "回覆必須先用一句短句明確說出你承接的是什麼" in prompts[1]


def test_unknown_question_uid_is_rejected(tutor_app):
    response = tutor_app.test_client().post(
        "/chat_ai", json={"question_uid": "forged", "question": "上一題是什麼？"}
    )
    assert response.status_code == 409


def test_handwriting_question_identity_is_server_authoritative(tutor_app, monkeypatch):
    import core.routes.analysis as analysis
    from app import login_manager
    from flask_login import UserMixin

    class Student(UserMixin):
        id = 777

    monkeypatch.setattr(login_manager, "_user_callback", lambda _user_id: Student())
    owner = "user:777"
    _STORE[owner] = {
        "q-trusted": {
            "question_uid": "q-trusted",
            "skill_id": "test",
            "question_text": "2x+3=11",
            "correct_answer": "x=4",
            "status": "generated",
        },
        "q-expired": {
            "question_uid": "q-expired",
            "skill_id": "test",
            "question_text": "x+1=4",
            "correct_answer": "3",
            "status": "expired",
        },
        "q-other-session": {
            "question_uid": "q-other-session",
            "skill_id": "test",
            "question_text": "x+2=5",
            "correct_answer": "3",
            "practice_session": "issued-session",
            "status": "generated",
        },
    }
    _STORE["user:other"] = {
        "q-other": {
            "question_uid": "q-other",
            "skill_id": "test",
            "question_text": "other",
            "correct_answer": "other",
            "status": "generated",
        }
    }
    captured: dict[str, str] = {}

    def fake_analysis(expr, expected_answer, question_text, family_id):
        captured.update(
            expr=expr,
            expected_answer=expected_answer,
            question_text=question_text,
            family_id=family_id,
        )
        return {
            "status": "correct",
            "process_correct": True,
            "recognized_expression": expr,
            "expected_answer": expected_answer,
        }

    monkeypatch.setattr(analysis, "_handwriting_structured_analysis", fake_analysis)
    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "777"
        sess["_fresh"] = True
        sess["_practice_session_sid"] = "other-session"

    image_data_url = _image_data_url()
    missing = client.post("/analyze_handwriting", json={"image_data_url": image_data_url})
    forged = client.post(
        "/analyze_handwriting",
        json={"question_uid": "forged", "image_data_url": image_data_url},
    )
    cross_user = client.post(
        "/analyze_handwriting",
        json={"question_uid": "q-other", "image_data_url": image_data_url},
    )
    expired = client.post(
        "/analyze_handwriting",
        json={"question_uid": "q-expired", "image_data_url": image_data_url},
    )
    cross_session = client.post(
        "/analyze_handwriting",
        json={"question_uid": "q-other-session", "image_data_url": image_data_url},
    )
    valid = client.post(
        "/analyze_handwriting",
        json={
            "question_uid": "q-trusted",
            "image_data_url": image_data_url,
            "normalized_answer": "2x=8",
            "recognized_steps": ["2x+3=11", "2x=8"],
            "question_text": "偽造題目",
            "expected_answer": "x=999",
            "correct_answer": "x=999",
        },
    )

    assert missing.status_code == 400
    assert missing.get_json()["error"] == "question_uid_required"
    assert forged.status_code == cross_user.status_code == 409
    assert cross_session.status_code == 409
    assert expired.status_code == 409
    assert expired.get_json()["error"] == "question_expired"
    assert valid.status_code == 200
    assert captured["question_text"] == "2x+3=11"
    assert captured["expected_answer"] == "x=4"


def test_tree_handwriting_rubric_ignores_client_expected_fields(tutor_app, monkeypatch):
    import core.routes.analysis as analysis
    from app import login_manager
    from flask_login import UserMixin

    class Student(UserMixin):
        id = 778

    monkeypatch.setattr(login_manager, "_user_callback", lambda _user_id: Student())
    _STORE["user:778"] = {
        "q-tree": {
            "question_uid": "q-tree",
            "skill_id": "tree-test",
            "question_text": "列出投擲兩次硬幣的所有結果",
            "correct_answer": "正正、正反、反正、反反",
            "problem_type_id": "tree_diagram_listing",
            "variant": "coin_twice",
            "expected_paths": ["正正", "正反", "反正", "反反"],
            "expected_count": 4,
            "status": "generated",
        }
    }
    prompts: list[str] = []

    class Reply:
        text = '{"status":"needs_review","feedback":"請把路徑寫清楚。"}'

    def fake_call(*args, **kwargs):
        prompts.append(str(kwargs.get("prompt") or (args[1] if len(args) > 1 else "")))
        return Reply()

    monkeypatch.setattr(analysis, "call_ai", fake_call)
    monkeypatch.setattr(analysis, "call_google_model", fake_call)
    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "778"
        sess["_fresh"] = True

    response = client.post(
        "/analyze_handwriting",
        json={
            "question_uid": "q-tree",
            "image_data_url": _image_data_url(),
            "problem_type": "pascal_triangle_handwriting",
            "question_text": "偽造題目",
            "variant": "tampered",
            "expected_paths": ["偽造路徑"],
            "expected_count": 999,
        },
    )

    assert response.status_code == 200
    assert "列出投擲兩次硬幣的所有結果" in prompts[0]
    assert "正正" in prompts[0]
    assert "Total expected paths count: 4" in prompts[0]
    assert "偽造" not in prompts[0]
    assert "999" not in prompts[0]


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


def test_handwriting_steps_and_image_reference_survive_next_turn(tutor_app):
    from flask import session
    from core.handwriting_ai_check import HandwritingCheckContext
    from core.routes.adaptive_api import _persist_drawing_feedback

    with tutor_app.test_request_context("/"):
        session["_practice_owner_sid"] = "steps"
        _install("sid:steps", "q-steps")
        ctx = HandwritingCheckContext(question_uid="q-steps", question_text="2x+1=7")
        _persist_drawing_feedback(ctx, {
            "recognized_answer": "x=3", "recognized_steps": ["2x=7+1", "x=4"],
            "feedback": "移項的符號要檢查", "final_answer_correct": False,
            "handwriting_submission_id": "submission-1",
            "submission_audit": {"image_sha256": "a" * 64},
        })
        _persist_drawing_feedback(ctx, {
            "recognized_answer": "x=3", "recognized_steps": ["2x=7+1", "x=4"],
            "feedback": "移項的符號要檢查", "final_answer_correct": False,
            "handwriting_submission_id": "submission-1",
        })
        turns = get_context("q-steps")
        assert len(turns) == 1
        assert "2x=7+1" in turns[0]["handwriting_summary"]
        assert turns[0]["handwriting_image_reference"] == "a" * 64
        assert "2x=7+1" in format_for_prompt("q-steps")
        assert turns[0]["at"]


def test_suggested_questions_are_three_and_contextual():
    from core.ai_conversation_context import normalize_suggested_questions

    prompts = normalize_suggested_questions(
        ["固定問題", "固定問題"], question_text="2x+1=7",
        student_work="2x=7+1", ai_reply="移項時先檢查正負號",
    )
    assert len(prompts) == len(set(prompts)) == 3
    assert "2x=7+1" in prompts[0]
    assert "移項時先檢查正負號" in prompts[1]


def test_model_suggestions_are_preserved_and_single_digit_answer_is_filtered():
    from core.ai_conversation_context import normalize_suggested_questions

    proposed = [
        "為什麼移項後要改變正負號？",
        "題目中的等號代表兩邊有什麼關係？",
        "答案是 3，接著直接代回去嗎？",
    ]
    prompts = normalize_suggested_questions(
        proposed, question_text="2x+1=7", student_work="2x=6",
        ai_reply="先檢查等號兩邊。", correct_answer="3",
    )
    assert len(prompts) == 3
    assert prompts[:2] == proposed[:2]
    assert all("答案是 3" not in item for item in prompts)


def test_duplicate_submission_append_is_atomic(tutor_app):
    owner = "sid:atomic"
    uid = "q-atomic"
    _install(owner, uid)
    barrier = threading.Barrier(3)
    outcomes: list[bool] = []

    def append_once():
        with tutor_app.test_request_context("/"):
            from flask import session
            session["_practice_owner_sid"] = "atomic"
            barrier.wait()
            outcomes.append(add_turn(
                uid, role="student", kind="handwriting_feedback",
                content="2x=6", submission_id="same-submission",
            ))

    threads = [threading.Thread(target=append_once) for _ in range(2)]
    for thread in threads:
        thread.start()
    barrier.wait()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == [False, True]
    with tutor_app.test_request_context("/"):
        from flask import session
        session["_practice_owner_sid"] = "atomic"
        assert len(get_context(uid)) == 1


def test_conversation_rejects_different_owner_and_practice_session(tutor_app):
    from flask import session
    from core.practice_question_store import slim_payload_for_store, get_question_by_uid

    with tutor_app.test_request_context("/"):
        session["_practice_owner_sid"] = "student-a"
        row = slim_payload_for_store(
            {"question_text": "x+1=4", "answer": "3"}, skill_id="jh_test", question_uid="q-private"
        )
        _STORE["sid:student-a"] = {"q-private": row}
        add_turn("q-private", role="student", kind="chat_message", content="我的做法")
        assert get_question_by_uid("q-private") is not None
        session["_practice_session_sid"] = "other-browser-session"
        assert get_question_by_uid("q-private") is None
        assert get_context("q-private") == []
        session["_practice_owner_sid"] = "student-b"
        assert get_context("q-private") == []


@pytest.mark.parametrize("skill_id,question_text", [
    ("jh_數學1上_FourArithmeticOperationsOfIntegers", "(-3)+5=?"),
    ("gh_RationalNumbers", "將 3/4 寫成小數"),
    ("vh_數學B1_SlopeOfALine", "求兩點連線的斜率"),
    ("vh_數學B2_AngleMeasurementAndConversion", "將 180 度換成弧度"),
    ("vh_數學B3_SubSection_1_1_4", "依圖判斷函數變化"),
    ("vh_數學B4_ProbabilityDefinition", "擲骰子求事件機率"),
])
def test_shared_chat_contract_across_curricula(tutor_app, monkeypatch, skill_id, question_text):
    import core.routes.analysis as analysis

    uid = "q-" + skill_id
    owner = "sid:curriculum-check"
    _STORE[owner] = {uid: {
        "question_uid": uid, "skill_id": skill_id,
        "question_text": question_text, "correct_answer": "hidden",
    }}
    prompts = []

    def fake_chat(prompt, **_kwargs):
        prompts.append(prompt)
        return {"reply": "請先核對你寫的第一步。", "follow_up_prompts": []}

    monkeypatch.setattr(analysis, "get_chat_response", fake_chat)
    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["_practice_owner_sid"] = "curriculum-check"
    first = client.post("/chat_ai", json={
        "question_uid": uid, "question": "我先列出已知條件",
        "question_text": "偽造題目", "correct_answer": "x=999", "expected_answer": "x=999",
    })
    second = client.post("/chat_ai", json={
        "question_uid": uid, "question": "下一步呢？", "question_text": "偽造題目",
    })
    assert first.status_code == second.status_code == 200
    assert len(second.get_json()["suggested_questions"]) == 3
    assert question_text in prompts[0]
    assert "偽造題目" not in prompts[0]
    assert "x=999" not in prompts[0]
    assert "我先列出已知條件" in prompts[1]


def test_legacy_model_fallback_has_no_shared_chat_session(tutor_app, monkeypatch):
    import core.ai_analyzer as analyzer

    prompts = []

    class FakeModel:
        def generate_content(self, content, **_kwargs):
            prompts.append(content[0])
            return type("Response", (), {"text": '{"reply":"請核對步驟","follow_up_prompts":[]}'})()

    monkeypatch.setattr(analyzer, "get_ai_client", lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("offline")))
    monkeypatch.setattr(analyzer, "gemini_model", FakeModel())
    monkeypatch.setattr(analyzer, "gemini_chat", None)
    with tutor_app.app_context():
        analyzer.get_chat_response("question-A")
        analyzer.get_chat_response("question-B")
    assert len(prompts) == 2
    assert "question-A" not in prompts[1]
    assert analyzer.gemini_chat is None


def test_third_turn_sees_revised_handwriting_and_previous_hint(tutor_app, monkeypatch):
    import core.routes.analysis as analysis

    owner = "sid:three-turns"
    uid = "q-revision"
    _STORE[owner] = {uid: {
        "question_uid": uid, "skill_id": "gh_RationalNumbers",
        "question_text": "2x+1=7", "correct_answer": "3",
    }}
    prompts = []

    def fake_chat(prompt, **_kwargs):
        prompts.append(prompt)
        return {"reply": "移項時請留意正負號。", "follow_up_prompts": []}

    monkeypatch.setattr(analysis, "get_chat_response", fake_chat)
    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["_practice_owner_sid"] = "three-turns"
    with tutor_app.test_request_context("/"):
        from flask import session
        session["_practice_owner_sid"] = "three-turns"
        add_turn(uid, role="student", kind="handwriting_feedback",
                 content="2x=7+1", handwriting_summary="2x=7+1")
    first = client.post("/chat_ai", json={
        "question_uid": uid, "question": "我的移項對嗎？",
    })
    with tutor_app.test_request_context("/"):
        from flask import session
        session["_practice_owner_sid"] = "three-turns"
        add_turn(uid, role="student", kind="handwriting_feedback",
                 content="2x=7-1", handwriting_summary="2x=7-1")
    third = client.post("/chat_ai", json={
        "question_uid": uid, "question": "我已改寫，現在有進步嗎？",
    })
    assert first.status_code == third.status_code == 200
    assert "2x=7+1" in prompts[1]
    assert "2x=7-1" in prompts[1]
    assert "移項時請留意正負號" in prompts[1]


def test_handwriting_follow_up_revised_handwriting_api_flow(tutor_app, monkeypatch):
    import core.routes.analysis as analysis
    from app import login_manager
    from flask_login import UserMixin

    class Student(UserMixin):
        id = 42

    monkeypatch.setattr(login_manager, "_user_callback", lambda _user_id: Student())
    owner = "user:42"
    uid = "q-api-revision"
    _STORE[owner] = {uid: {
        "question_uid": uid, "skill_id": "gh_RationalNumbers",
        "question_text": "2x+1=7", "correct_answer": "3",
    }}
    handwriting_prompts: list[str] = []
    chat_prompts: list[str] = []

    class Reply:
        text = json.dumps({
            "reply": "先檢查移項後的符號，再驗證下一行。",
            "suggested_questions": ["為什麼移項要改符號？", "等號兩邊要怎麼維持相等？", "我最可能錯在哪一步？"],
            "follow_up_prompts": ["為什麼移項要改符號？", "等號兩邊要怎麼維持相等？", "我最可能錯在哪一步？"],
        }, ensure_ascii=False)

    def fake_handwriting_ai(*_args, **kwargs):
        handwriting_prompts.append(str(kwargs.get("prompt") or (_args[1] if len(_args) > 1 else "")))
        return Reply()

    def fake_chat(prompt, **_kwargs):
        chat_prompts.append(prompt)
        return {
            "reply": "我承接你剛才的移項步驟；先看常數項的符號。",
            "follow_up_prompts": ["為什麼常數項要移到另一邊？", "等號在這裡代表什麼？", "哪個符號最容易抄錯？"],
        }

    monkeypatch.setattr(analysis, "call_ai", fake_handwriting_ai)
    monkeypatch.setattr(analysis, "call_google_model", fake_handwriting_ai)
    monkeypatch.setattr(analysis, "get_chat_response", fake_chat)

    image = Image.new("RGB", (16, 16), "white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_data_url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")

    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "42"
        sess["_fresh"] = True

    first = client.post("/analyze_handwriting", json={
        "question_uid": uid, "image_data_url": image_data_url,
        "normalized_answer": "x=4", "recognized_steps": ["2x=7+1", "x=4"],
    })
    follow_up = client.post("/chat_ai", json={
        "question_uid": uid, "question": "為什麼這一步要變號？",
    })
    revised = client.post("/analyze_handwriting", json={
        "question_uid": uid, "image_data_url": image_data_url,
        "normalized_answer": "x=4", "recognized_steps": ["2x=7-1", "x=4"],
    })

    assert first.status_code == follow_up.status_code == revised.status_code == 200
    assert len(first.get_json()["suggested_questions"]) == 3
    assert len(follow_up.get_json()["suggested_questions"]) == 3
    assert len(revised.get_json()["suggested_questions"]) == 3
    assert "2x=7+1" in chat_prompts[0]
    assert len(handwriting_prompts) == 2
    assert "2x=7+1" in handwriting_prompts[1]
    assert "2x=7-1" in handwriting_prompts[1]
    assert "我承接你剛才的移項步驟" in handwriting_prompts[1]
