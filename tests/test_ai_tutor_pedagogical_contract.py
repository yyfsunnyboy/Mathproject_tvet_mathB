"""Shared AI Tutor pedagogical contract (all curricula)."""

from __future__ import annotations

import base64
import io
import json

import pytest
from PIL import Image

from app import create_app
from core.ai_conversation_context import add_turn, get_context, normalize_suggested_questions
from core.ai_tutor_pedagogy import classify_tutor_intent, quoted_math_is_unseen
from core.models.prompt_template import PromptTemplate
from core.practice_question_store import _STORE
from core.prompts.default_templates import DEFAULT_PROMPT_TEMPLATES
from models import db

MIDPOINT_QUESTION = "若 P 為 A(3,9) 與 B(-1,5) 兩點之中點，求 P 點與原點 O 的距離。"
MIDPOINT_ANSWER = "5\\sqrt{2}"
MIDPOINT_STEPS = ["(3+(-1))/2 = 1", "(9+5)/2 = 7"]
VAGUE_ONLY = ("再想一想", "從第一步重新檢查", "哪裡不對呢", "試試看下一步")


@pytest.fixture()
def tutor_app(tmp_path):
    import config as config_module

    previous_uri = config_module.Config.SQLALCHEMY_DATABASE_URI
    config_module.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(tmp_path / "pedagogy.db").replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            for key in ("chat_tutor_prompt", "chat_guardrail_prompt", "handwriting_feedback_prompt"):
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


def _image_data_url() -> str:
    image = Image.new("RGB", (16, 16), "white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def _install(owner_sid, uid, *, skill_id="vh_數學B1_DistanceBetweenTwoPoints",
             question=MIDPOINT_QUESTION, answer=MIDPOINT_ANSWER):
    _STORE[f"sid:{owner_sid}"] = {uid: {
        "question_uid": uid, "skill_id": skill_id,
        "question_text": question, "correct_answer": answer, "status": "generated",
    }}


def _client(app, owner_sid):
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_practice_owner_sid"] = owner_sid
    return client


def _seed_handwriting(app, owner_sid, uid, steps):
    with app.test_request_context("/"):
        from flask import session
        session["_practice_owner_sid"] = owner_sid
        work = "\n".join(steps)
        add_turn(uid, role="student", kind="handwriting_feedback",
                 content=f"辨識式：{work}", handwriting_summary=work)


def _fake_chat(monkeypatch, replies):
    import core.routes.analysis as analysis

    calls = {"prompts": []}

    def fake(prompt, **_kwargs):
        calls["prompts"].append(prompt)
        reply = replies[min(len(calls["prompts"]) - 1, len(replies) - 1)]
        return dict(reply) if isinstance(reply, dict) else {"reply": reply, "follow_up_prompts": []}

    monkeypatch.setattr(analysis, "get_chat_response", fake)
    return calls


def _hw_login(monkeypatch, user_id):
    from app import login_manager
    from flask_login import UserMixin

    class Student(UserMixin):
        id = user_id

    monkeypatch.setattr(login_manager, "_user_callback", lambda _user_id: Student())


def _fake_second_stage(monkeypatch, reply_payload):
    import core.routes.analysis as analysis

    prompts = []

    class Reply:
        text = json.dumps(reply_payload, ensure_ascii=False)

    def fake(*args, **kwargs):
        prompts.append(str(kwargs.get("prompt") or (args[1] if len(args) > 1 else "")))
        return Reply()

    monkeypatch.setattr(analysis, "call_ai", fake)
    monkeypatch.setattr(analysis, "call_google_model", fake)
    return prompts


# --- intent classification -------------------------------------------------

@pytest.mark.parametrize("text,intent", [
    ("距離公式是什麼？", "formula_definition"),
    ("中點的定義是什麼？", "formula_definition"),
    ("你剛剛說的距離公式，為什麼是這樣？", "why_step"),
    ("我這樣寫對嗎？", "check_work"),
    ("我不知道下一步要做什麼", "next_step"),
    ("下一步是什麼？", "next_step"),
    ("可以講簡單一點嗎", "simpler"),
    ("我哪裡錯了？", "where_wrong"),
    ("直接告訴我答案", "full_solution"),
])
def test_intent_classification_is_curriculum_agnostic(text, intent):
    assert classify_tutor_intent(text) == intent


# --- 1. correct but incomplete (chat) --------------------------------------

def test_correct_but_incomplete_work_is_confirmed_not_replaced(tutor_app, monkeypatch):
    _install("mid", "q-mid")
    _seed_handwriting(tutor_app, "mid", "q-mid", MIDPOINT_STEPS)
    reply = (
        "你寫的 $\\frac{3+(-1)}{2}=1$ 和 $\\frac{9+5}{2}=7$ 都正確，所以中點是 $P(1,7)$。\n"
        "下一步用距離公式 $OP=\\sqrt{(1-0)^2+(7-0)^2}$，把根號裡算出來。"
    )
    calls = _fake_chat(monkeypatch, [reply])
    response = _client(tutor_app, "mid").post("/chat_ai", json={"question_uid": "q-mid", "question": "我這樣寫對嗎？"})

    body = response.get_json()
    assert response.status_code == 200
    assert len(calls["prompts"]) == 1, "a faithful LaTeX quote must not trigger the rewrite pass"
    assert body["reply"] == reply
    prompt = calls["prompts"][0]
    assert "(3+(-1))/2 = 1" in prompt and "(9+5)/2 = 7" in prompt
    assert "共用教學契約" in prompt
    assert "【本輪意圖】請你檢查手寫" in prompt
    assert "只比對最後一行的自動推測" in prompt
    assert len(body["suggested_questions"]) == 3


# --- 2. explicit calculation error (handwriting second stage) --------------

def test_explicit_calculation_error_is_named_with_the_line(tutor_app, monkeypatch):
    _hw_login(monkeypatch, 71)
    _STORE["user:71"] = {"q-err": {
        "question_uid": "q-err", "skill_id": "vh_test",
        "question_text": MIDPOINT_QUESTION, "correct_answer": MIDPOINT_ANSWER,
    }}
    reply = "你寫的 (3+(-1))/2 = 2 這一行算錯：$3+(-1)=2$，$2\\div 2=1$，所以應寫 $(3+(-1))/2=1$。接著再算 y 座標。"
    prompts = _fake_second_stage(monkeypatch, {"reply": reply, "suggested_questions": []})
    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "71"
        sess["_fresh"] = True
    response = client.post("/analyze_handwriting", json={
        "question_uid": "q-err", "image_data_url": _image_data_url(),
        "normalized_answer": "(3+(-1))/2 = 2", "recognized_steps": ["(3+(-1))/2 = 2"],
    })
    body = response.get_json()
    assert response.status_code == 200
    assert "(3+(-1))/2 = 2" in body["reply"]
    assert "算錯" in body["reply"]
    assert "第一階段判定的意思" in prompts[0]
    assert "共用教學契約" in prompts[0]
    assert len(body["suggested_questions"]) == 3


def test_handwriting_correct_but_unfinished_is_not_replaced_by_generic_fallback(tutor_app, monkeypatch):
    _hw_login(monkeypatch, 72)
    _STORE["user:72"] = {"q-unfinished": {
        "question_uid": "q-unfinished", "skill_id": "vh_test",
        "question_text": MIDPOINT_QUESTION, "correct_answer": MIDPOINT_ANSWER,
    }}
    reply = (
        "你寫的 (3+(-1))/2 = 1 和 (9+5)/2 = 7 都正確，中點是 $P(1,7)$。\n"
        "接著用距離公式 $OP=\\sqrt{x^2+y^2}$，代入 $\\sqrt{1^2+7^2}$ 算出 OP。"
    )
    _fake_second_stage(monkeypatch, {
        "reply": reply,
        "suggested_questions": ["把 1 和 7 代入距離公式要怎麼寫？", "根號裡的 1²+7² 等於多少？", "OP 的根號要怎麼化簡？"],
    })
    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "72"
        sess["_fresh"] = True
    response = client.post("/analyze_handwriting", json={
        "question_uid": "q-unfinished", "image_data_url": _image_data_url(),
        "normalized_answer": "(9+5)/2 = 7", "recognized_steps": MIDPOINT_STEPS,
    })
    body = response.get_json()
    assert response.status_code == 200
    assert "都正確" in body["reply"]
    assert "\\sqrt{x^2+y^2}" in body["reply"]
    assert not any(phrase in body["reply"] for phrase in VAGUE_ONLY)
    assert "對不上" not in body["reply"]
    assert body["suggested_questions"][0] == "把 1 和 7 代入距離公式要怎麼寫？"


def test_handwriting_never_says_correct_when_checker_rejected(tutor_app, monkeypatch):
    import core.routes.analysis as analysis

    _hw_login(monkeypatch, 73)
    _STORE["user:73"] = {"q-checker": {
        "question_uid": "q-checker", "skill_id": "jh_test",
        "question_text": "1+1=?", "correct_answer": "2",
    }}
    monkeypatch.setattr(analysis, "_handwriting_structured_analysis", lambda *_a, **_k: {
        "recognized_expression": "1+1=2", "final_expression": "2", "expected_answer": "2",
        "is_correct": True, "process_correct": True, "status": "correct", "main_issue": "",
        "error_mechanism": "unknown", "family_id": "", "family_description_zh": "",
    })
    prompts = _fake_second_stage(monkeypatch, {"reply": "你寫的 1+1=2 數值正確，但最後答案要只寫成題目要求的形式，接著把答案單獨寫一行。"})
    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "73"
        sess["_fresh"] = True
        sess["chat_tutor_authoritative_result"] = {
            "question_uid": "q-checker", "correct": False, "status": "incorrect",
            "handwriting_submission_id": "sub-1",
        }
    response = client.post("/analyze_handwriting", json={
        "question_uid": "q-checker", "image_data_url": _image_data_url(),
        "normalized_answer": "1+1=2", "recognized_steps": ["1+1=2"],
        "handwriting_submission_id": "sub-1",
    })
    body = response.get_json()
    assert response.status_code == 200
    assert body["correct"] is False
    assert "答對了" not in body["reply"]
    assert body["handwriting_status"] == "partially_correct"
    assert len(prompts) == 1


# --- 3/4. formula and definition questions ----------------------------------

@pytest.mark.parametrize("question,reply", [
    ("距離公式是什麼？", "點 $P(x,y)$ 到原點的距離是 $OP=\\sqrt{x^2+y^2}$。\n你已求出 $P(1,7)$，代入得 $OP=\\sqrt{1^2+7^2}$。"),
    ("中點的定義是什麼？", "中點是線段上到兩端距離相等的點，座標是 $\\left(\\frac{x_1+x_2}{2},\\frac{y_1+y_2}{2}\\right)$。\n你寫的 (3+(-1))/2 = 1 就是 x 座標。"),
])
def test_formula_and_definition_questions_are_answered_directly(tutor_app, monkeypatch, question, reply):
    _install("formula", "q-formula")
    _seed_handwriting(tutor_app, "formula", "q-formula", MIDPOINT_STEPS)
    calls = _fake_chat(monkeypatch, [reply])
    response = _client(tutor_app, "formula").post("/chat_ai", json={"question_uid": "q-formula", "question": question})
    body = response.get_json()
    assert response.status_code == 200
    assert body["reply"] == reply
    assert len(calls["prompts"]) == 1
    assert "【本輪意圖】問公式／定義／概念" in calls["prompts"][0]
    assert "第一句直接寫出學生問的公式或定義" in calls["prompts"][0]


# --- 5. explain the previous hint ------------------------------------------

def test_explaining_previous_hint_sees_that_hint(tutor_app, monkeypatch):
    _install("prior", "q-prior")
    _seed_handwriting(tutor_app, "prior", "q-prior", MIDPOINT_STEPS)
    calls = _fake_chat(monkeypatch, [
        "下一步用距離公式 $OP=\\sqrt{x^2+y^2}$。",
        "因為 $OP$ 是直角三角形的斜邊，兩股是 1 和 7，由畢氏定理 $OP^2=1^2+7^2$。",
    ])
    client = _client(tutor_app, "prior")
    client.post("/chat_ai", json={"question_uid": "q-prior", "question": "下一步呢？"})
    second = client.post("/chat_ai", json={"question_uid": "q-prior", "question": "你剛剛說的距離公式，為什麼是這樣？"})
    assert second.status_code == 200
    assert "畢氏定理" in second.get_json()["reply"]
    assert "下一步用距離公式" in calls["prompts"][1]
    assert "【本輪意圖】問某一步為什麼" in calls["prompts"][1]


# --- 6. second-round revised handwriting -----------------------------------

def test_second_round_uses_revised_handwriting(tutor_app, monkeypatch):
    _install("revise", "q-revise")
    _seed_handwriting(tutor_app, "revise", "q-revise", ["(3+(-1))/2 = 2"])
    calls = _fake_chat(monkeypatch, ["第一行算錯", "你寫的 (3+(-1))/2 = 1 現在正確了。"])
    client = _client(tutor_app, "revise")
    client.post("/chat_ai", json={"question_uid": "q-revise", "question": "我哪裡錯了？"})
    _seed_handwriting(tutor_app, "revise", "q-revise", ["(3+(-1))/2 = 1"])
    second = client.post("/chat_ai", json={"question_uid": "q-revise", "question": "我改好了，這樣對嗎？"})
    assert second.get_json()["reply"] == "你寫的 (3+(-1))/2 = 1 現在正確了。"
    assert "【學生目前已寫的內容】\n(3+(-1))/2 = 1" in calls["prompts"][1]


# --- 7. uncertain recognition ----------------------------------------------

def test_uncertain_recognition_asks_about_the_symbol_without_guessing(tutor_app, monkeypatch):
    _install("unclear", "q-unclear")
    reply = "第二行的「5」我看不太清楚，是 5 還是 S？如果是 5，$(9+5)/2=7$ 是正確的。"
    calls = _fake_chat(monkeypatch, [reply])
    response = _client(tutor_app, "unclear").post("/chat_ai", json={
        "question_uid": "q-unclear", "question": "我這樣寫對嗎？",
        "student_answer": "(3+(-1))/2 = 1\n(9+5)/2 = 7", "recognition_incomplete": True,
    })
    assert response.get_json()["reply"] == reply
    assert "辨識狀態" in calls["prompts"][0]
    assert "直接說是哪一行的哪個符號看不清楚" in calls["prompts"][0]


# --- 8/9. structured-output robustness -------------------------------------

def test_missing_suggested_questions_keeps_reply_and_builds_three(tutor_app, monkeypatch):
    _install("nosugg", "q-nosugg")
    _seed_handwriting(tutor_app, "nosugg", "q-nosugg", MIDPOINT_STEPS)
    _fake_chat(monkeypatch, [{"reply": "中點 $P(1,7)$ 正確，下一步用 $OP=\\sqrt{x^2+y^2}$。"}])
    body = _client(tutor_app, "nosugg").post("/chat_ai", json={"question_uid": "q-nosugg", "question": "下一步呢？"}).get_json()
    assert body["reply"].startswith("中點")
    assert len(body["suggested_questions"]) == len(set(body["suggested_questions"])) == 3
    assert all("我目前寫出的步驟" not in item for item in body["suggested_questions"])
    assert all(item.endswith("？") for item in body["suggested_questions"])


@pytest.mark.parametrize("raw", [
    '{"reply": "距離公式是 $\\\\sqrt{x^2+y^2}$，代入 $P(1,7)$。", "suggested_questions": ["代入後怎麼算？"',
    '```json\n{"reply": "距離公式是 $\\\\sqrt{x^2+y^2}$，代入 $P(1,7)$。"}\n```',
    '{"reply": "距離公式是 $\\sqrt{x^2+y^2}$，代入 $P(1,7)$。", "suggested_questions": []}',
])
def test_valid_reply_survives_broken_json(raw):
    from core.ai_analyzer import parse_tutor_model_text, _finalize_tutor_payload

    payload = _finalize_tutor_payload(parse_tutor_model_text(raw), user_question="距離公式是什麼？")
    assert payload is not None
    assert "\\sqrt{x^2+y^2}" in payload["reply"]
    assert '"reply"' not in payload["reply"]
    assert len(payload["follow_up_prompts"]) == 3


def test_json_escape_damage_to_latex_is_repaired():
    from core.ai_analyzer import parse_tutor_model_text, _finalize_tutor_payload

    raw = '{"reply": "中點 $x=\\frac{3+(-1)}{2}$，乘號 $2\\times 3$。"}'
    payload = _finalize_tutor_payload(parse_tutor_model_text(raw))
    assert "\\frac{3+(-1)}{2}" in payload["reply"]
    assert "\\times" in payload["reply"]


def test_over_escaped_newline_becomes_a_line_break_but_latex_survives():
    from core.ai_analyzer import parse_tutor_model_text, _finalize_tutor_payload

    raw = '{"reply": "中點 $P(1,7)$ 正確！\\\\n接著代入 $\\\\sqrt{1^2+7^2}$，且 $1 \\\\neq 7$。"}'
    reply = _finalize_tutor_payload(parse_tutor_model_text(raw))["reply"]
    assert "\\n接著" not in reply
    assert "正確！\n接著" in reply
    assert "\\neq" in reply and "\\sqrt{1^2+7^2}" in reply


def test_unrecoverable_output_is_reported_as_model_failure(tutor_app, monkeypatch):
    import core.ai_analyzer as analyzer

    class Broken:
        def generate_content(self, *_args, **_kwargs):
            return type("R", (), {"text": '{"suggested_questions": ['})()

    monkeypatch.setattr(analyzer, "get_ai_client", lambda **_kwargs: Broken())
    monkeypatch.setattr(analyzer, "gemini_model", Broken())
    with tutor_app.app_context():
        result = analyzer.get_chat_response("prompt")
    assert result["ai_unavailable"] is True
    assert "換個方式" not in result["reply"]


def test_model_failure_returns_retryable_error_and_keeps_history_clean(tutor_app, monkeypatch):
    import core.routes.analysis as analysis
    from core.ai_analyzer import _tutor_unavailable_payload

    _install("down", "q-down")
    monkeypatch.setattr(analysis, "get_chat_response", lambda *_a, **_k: _tutor_unavailable_payload("model_call_failed"))
    client = _client(tutor_app, "down")
    response = client.post("/chat_ai", json={"question_uid": "q-down", "question": "距離公式是什麼？"})
    body = response.get_json()
    assert response.status_code == 503
    assert body["ai_unavailable"] is True and body["retryable"] is True
    assert "不是你的問題問得不好" in body["reply"]
    with tutor_app.test_request_context("/"):
        from flask import session
        session["_practice_owner_sid"] = "down"
        assert get_context("q-down") == []


# --- quote guard -----------------------------------------------------------

def test_quote_guard_accepts_latex_rewrites_and_rejects_invented_work():
    work = "(3+(-1))/2 = 1\n(9+5)/2 = 7"
    assert not quoted_math_is_unseen(" $\\frac{3+(-1)}{2}=1$ 正確", work)
    assert not quoted_math_is_unseen(" (9+5)/2 = 7，算得很好", work)
    assert not quoted_math_is_unseen("第一步很清楚", work)
    assert quoted_math_is_unseen(" (9+5)/2 = 8", work)
    assert quoted_math_is_unseen(" x≤2", "2x+3=11\n2x=6")


# --- suggestions follow the solving state ----------------------------------

def test_fallback_suggestions_follow_latest_work_and_reply():
    prompts = normalize_suggested_questions(
        [], question_text=MIDPOINT_QUESTION,
        student_work="(3+(-1))/2 = 1\n(9+5)/2 = 7",
        ai_reply="中點正確。\n下一步用 $OP=\\sqrt{x^2+y^2}$ 代入 P(1,7)",
        correct_answer=MIDPOINT_ANSWER,
    )
    assert len(prompts) == 3
    assert "(9+5)/2 = 7" in prompts[0]
    assert "√(x^2+y^2)" in prompts[1]
    assert all("$" not in item and "\\" not in item for item in prompts)


# --- 10. JH / GH / VH representative ---------------------------------------

@pytest.mark.parametrize("skill_id,question_text,work,user_question", [
    ("jh_數學1上_FourArithmeticOperationsOfIntegers", "計算 (-3)×4+5", "(-3)×4 = -12", "下一步呢？"),
    ("gh_RationalNumbers", "將 3/4 寫成小數", "3÷4", "小數的定義是什麼？"),
    ("vh_數學B1_SlopeOfALine", "求 A(1,2)、B(3,8) 連線的斜率", "8-2 = 6", "斜率公式是什麼？"),
    ("vh_數學B2_AngleMeasurementAndConversion", "將 180 度換成弧度", "180×π", "為什麼要乘 π？"),
    ("vh_數學B3_SubSection_1_1_4", "求 f(x)=2x+1 在 x=3 的值", "2×3 = 6", "我這樣寫對嗎？"),
    ("vh_數學B4_ProbabilityDefinition", "擲一顆骰子，求出現偶數的機率", "偶數有 2,4,6", "我不知道下一步"),
])
def test_contract_is_shared_across_curricula(tutor_app, monkeypatch, skill_id, question_text, work, user_question):
    uid = "q-" + skill_id
    _install("curr", uid, skill_id=skill_id, question=question_text, answer="hidden-answer")
    _seed_handwriting(tutor_app, "curr", uid, [work])
    reply = f"你寫的 {work} 正確。下一步把結果代入題目要求的式子，寫出下一行算式。"
    calls = _fake_chat(monkeypatch, [reply])
    response = _client(tutor_app, "curr").post("/chat_ai", json={"question_uid": uid, "question": user_question})
    body = response.get_json()
    assert response.status_code == 200
    assert body["reply"] == reply
    assert len(body["suggested_questions"]) == 3
    prompt = calls["prompts"][0]
    assert question_text in prompt and work in prompt
    assert "共用教學契約" in prompt
    assert f"【本輪意圖】" in prompt


# --- 11. three-round teaching policy (server-counted) -----------------------

LINE_QUESTION = "已知直線的斜率為 2/3，y 截距為 -5，求此直線的方程式。"
LINE_ANSWER = "y=\\frac{2}{3}x-5"
LINE_WORK = "y=2x/3+5"
LINE_FULL_REPLY = (
    "斜率 2/3 用對了，但 y 截距是 $-5$，常數項的符號要改。\n"
    "斜截式 $y=mx+b$ 代入 $m=\\frac{2}{3}$、$b=-5$，整理得 $3y=2x-15$，所以 $y=\\frac{2}{3}x-5$。"
)


def _chat(client, uid, question):
    response = client.post("/chat_ai", json={"question_uid": uid, "question": question})
    return response.status_code, response.get_json()


def test_three_rounds_hint_then_deepen_then_full_solution_on_request(tutor_app, monkeypatch):
    _install("line", "q-line", skill_id="vh_數學B1_EquationOfALine", question=LINE_QUESTION, answer=LINE_ANSWER)
    _seed_handwriting(tutor_app, "line", "q-line", [LINE_WORK])
    calls = _fake_chat(monkeypatch, [LINE_FULL_REPLY])
    client = _client(tutor_app, "line")

    status, first = _chat(client, "q-line", "直接告訴我答案")
    assert status == 200 and first["teaching_round"] == 1
    assert "3y=2x-15" not in first["reply"] and "\\frac{2}{3}x-5" not in first["reply"]
    assert "y=mx+b" in first["reply"], "the general formula must survive redaction"
    assert len(first["suggested_questions"]) == 3

    status, second = _chat(client, "q-line", "我改好了，這樣對嗎？")
    assert status == 200 and second["teaching_round"] == 2
    assert "3y=2x-15" not in second["reply"] and "\\frac{2}{3}x-5" not in second["reply"]
    assert len(second["suggested_questions"]) == 3

    status, third = _chat(client, "q-line", "直接告訴我答案")
    assert status == 200 and third["teaching_round"] == 3
    assert third["reply"] == LINE_FULL_REPLY
    assert len(third["suggested_questions"]) == 3

    assert any("【本題教學輪次】第 1 輪" in p for p in calls["prompts"])
    second_round_prompts = [p for p in calls["prompts"] if "【本題教學輪次】第 2 輪" in p]
    assert second_round_prompts and "第1輪 tutor/tutor_reply" in second_round_prompts[0]
    assert any("【本題教學輪次】第 3 輪" in p and "允許：學生已明確要求完整解答" in p for p in calls["prompts"])


def test_round_three_without_request_still_withholds_answer(tutor_app, monkeypatch):
    _install("line3", "q-line3", question=LINE_QUESTION, answer=LINE_ANSWER)
    _fake_chat(monkeypatch, [LINE_FULL_REPLY])
    client = _client(tutor_app, "line3")
    for _ in range(2):
        _chat(client, "q-line3", "下一步是什麼？")
    status, third = _chat(client, "q-line3", "下一步是什麼？")
    assert status == 200 and third["teaching_round"] == 3
    assert "\\frac{2}{3}x-5" not in third["reply"]


def test_failed_model_call_does_not_count_as_a_round(tutor_app, monkeypatch):
    import core.routes.analysis as analysis
    from core.ai_analyzer import _tutor_unavailable_payload

    _install("fail", "q-fail", question=LINE_QUESTION, answer=LINE_ANSWER)
    client = _client(tutor_app, "fail")
    monkeypatch.setattr(analysis, "get_chat_response", lambda *_a, **_k: _tutor_unavailable_payload("timeout"))
    status, body = _chat(client, "q-fail", "下一步是什麼？")
    assert status == 503 and body["retryable"] is True
    _fake_chat(monkeypatch, ["先寫出斜截式 $y=mx+b$。"])
    status, body = _chat(client, "q-fail", "下一步是什麼？")
    assert status == 200 and body["teaching_round"] == 1


def test_new_question_and_other_student_start_at_round_one(tutor_app, monkeypatch):
    _install("iso-a", "q-a", question=LINE_QUESTION, answer=LINE_ANSWER)
    _STORE["sid:iso-a"]["q-b"] = {
        "question_uid": "q-b", "skill_id": "vh_test", "question_text": "解 2x+3=11",
        "correct_answer": "x=4", "status": "generated",
    }
    _install("iso-b", "q-a", question=LINE_QUESTION, answer=LINE_ANSWER)
    _fake_chat(monkeypatch, ["先寫出斜截式 $y=mx+b$。"])
    student_a = _client(tutor_app, "iso-a")
    _chat(student_a, "q-a", "下一步是什麼？")
    assert _chat(student_a, "q-a", "下一步是什麼？")[1]["teaching_round"] == 2
    assert _chat(student_a, "q-b", "下一步是什麼？")[1]["teaching_round"] == 1
    assert _chat(_client(tutor_app, "iso-b"), "q-a", "下一步是什麼？")[1]["teaching_round"] == 1


def test_concurrent_same_round_replies_do_not_skip_and_resent_submission_keeps_round(tutor_app):
    from core.ai_conversation_context import current_teaching_round

    _install("race", "q-race")
    with tutor_app.test_request_context("/"):
        from flask import session
        session["_practice_owner_sid"] = "race"
        assert current_teaching_round("q-race") == 1
        add_turn("q-race", role="tutor", kind="tutor_reply", content="a", teaching_round=1)
        add_turn("q-race", role="tutor", kind="tutor_reply", content="b", teaching_round=1)
        assert current_teaching_round("q-race") == 2
        add_turn("q-race", role="student", kind="handwriting_feedback", content="c",
                 submission_id="sub-x", teaching_round=2)
        assert not add_turn("q-race", role="student", kind="handwriting_feedback", content="c",
                            submission_id="sub-x", teaching_round=3)
        assert current_teaching_round("q-race") == 3
        assert current_teaching_round("q-race", "sub-x") == 2


def _hw_client(app, user_id):
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
    return client


def _hw_post(client, uid, steps, submission_id=""):
    payload = {
        "question_uid": uid, "image_data_url": _image_data_url(),
        "normalized_answer": steps[-1], "recognized_steps": steps,
    }
    if submission_id:
        payload["handwriting_submission_id"] = submission_id
        with client.session_transaction() as sess:
            sess["chat_tutor_authoritative_result"] = {
                "question_uid": uid, "correct": False, "status": "incorrect",
                "handwriting_submission_id": submission_id,
            }
    response = client.post("/analyze_handwriting", json=payload)
    return response.status_code, response.get_json()


def test_handwriting_and_chat_share_rounds_and_duplicates_do_not_count(tutor_app, monkeypatch):
    _hw_login(monkeypatch, 74)
    _STORE["user:74"] = {"q-hw-line": {
        "question_uid": "q-hw-line", "skill_id": "vh_test",
        "question_text": LINE_QUESTION, "correct_answer": LINE_ANSWER,
    }}
    _fake_second_stage(monkeypatch, {"reply": LINE_FULL_REPLY, "suggested_questions": []})
    client = _hw_client(tutor_app, 74)

    status, first = _hw_post(client, "q-hw-line", [LINE_WORK], submission_id="sub-1")
    assert status == 200 and first["teaching_round"] == 1
    assert "\\frac{2}{3}x-5" not in first["reply"] and "3y=2x-15" not in first["reply"]
    assert len(first["suggested_questions"]) == 3

    status, duplicate = _hw_post(client, "q-hw-line", [LINE_WORK], submission_id="sub-1")
    assert status == 200 and duplicate["teaching_round"] == 1

    _fake_chat(monkeypatch, ["截距的符號再看一次：$b$ 應該是題目給的 y 截距。"])
    status, chat = _chat(client, "q-hw-line", "我哪裡錯了？")
    assert status == 200 and chat["teaching_round"] == 2


def test_handwriting_model_error_text_is_503_and_not_a_round(tutor_app, monkeypatch):
    import core.routes.analysis as analysis

    _hw_login(monkeypatch, 75)
    _STORE["user:75"] = {"q-hw-down": {
        "question_uid": "q-hw-down", "skill_id": "vh_test",
        "question_text": LINE_QUESTION, "correct_answer": LINE_ANSWER,
    }}

    class Failed:
        text = "Error: Gemini request timed out"

    monkeypatch.setattr(analysis, "call_ai", lambda *_a, **_k: Failed())
    monkeypatch.setattr(analysis, "call_google_model", lambda *_a, **_k: Failed())
    client = _hw_client(tutor_app, 75)
    status, body = _hw_post(client, "q-hw-down", [LINE_WORK])
    assert status == 503
    assert body["ai_unavailable"] is True and body["retryable"] is True
    assert "Error:" not in body["reply"]

    _fake_second_stage(monkeypatch, {"reply": "截距的符號再看一次：$b$ 應該是題目給的 y 截距。"})
    status, body = _hw_post(client, "q-hw-down", [LINE_WORK])
    assert status == 200 and body["teaching_round"] == 1


@pytest.mark.parametrize("skill_id,question_text,answer,answer_math", [
    ("jh_數學1上_FourArithmeticOperationsOfIntegers", "計算 (-3)×4+5", "-7", "-7"),
    ("jh_數學2上_FourArithmeticOperationsOfPolynomial", "展開 (x+2)(x+3)", "x^2+5x+6", "x^2+5x+6"),
    ("gh_RationalNumbers", "將 3/4 寫成小數", "0.75", "\\frac{3}{4}"),
    ("vh_數學B1_SlopeOfALine", "求 A(1,2)、B(3,8) 連線的斜率", "3", "\\frac{6}{2}"),
    ("vh_數學B2_AngleMeasurementAndConversion", "將 180 度換成弧度", "\\pi", "\\pi"),
    ("vh_數學B3_SubSection_1_1_4", "解 2x+3 ≥ 9", "x \\ge 3", "3 \\le x"),
    ("vh_數學B4_ProbabilityDefinition", "擲一顆骰子，求出現偶數的機率", "\\frac{1}{2}", "\\frac{3}{6}"),
])
def test_round_policy_is_shared_across_curricula(tutor_app, monkeypatch, skill_id, question_text,
                                                 answer, answer_math):
    owner = "cross-" + skill_id[-6:]
    uid = "q-round-" + skill_id
    _install(owner, uid, skill_id=skill_id, question=question_text, answer=answer)
    full = f"先列出本題要用的規則，再一步步計算。\n所以答案是 ${answer_math}$。"
    _fake_chat(monkeypatch, [full])
    client = _client(tutor_app, owner)
    for round_no in (1, 2):
        status, body = _chat(client, uid, "直接告訴我答案")
        assert status == 200 and body["teaching_round"] == round_no
        assert answer_math not in body["reply"], (skill_id, round_no, body["reply"])
        assert "先列出本題要用的規則" in body["reply"]
        assert len(body["suggested_questions"]) == 3
    status, body = _chat(client, uid, "直接告訴我答案")
    assert body["teaching_round"] == 3 and answer_math in body["reply"]


@pytest.mark.parametrize("reply", [
    # observed live Gemini wording: names the wrong sign without the older fixed keywords
    "你的 $y = \\frac{2}{3}x + 5$ 這一行常數項正負號看錯了。\n題目給的 $y$ 截距為 $-5$，所以常數項應代入 $-5$。\n請修正常數項，寫出 $y = mx + b$ 的直線方程式。",
    "第二行的 $(-3)^2$ 弄錯了，應該是 $9$；接著把 $9$ 代回原式。",
])
def test_specific_diagnosis_is_kept_not_replaced_by_rule_template(tutor_app, monkeypatch, reply):
    from core.routes.analysis import _handwriting_second_stage_compliance_flags

    assert _handwriting_second_stage_compliance_flags(reply, "incorrect", LINE_ANSWER)["compliance_ok"]
    _hw_login(monkeypatch, 76)
    _STORE["user:76"] = {"q-hw-diag": {
        "question_uid": "q-hw-diag", "skill_id": "vh_test",
        "question_text": LINE_QUESTION, "correct_answer": LINE_ANSWER,
    }}
    _fake_second_stage(monkeypatch, {"reply": reply})
    status, body = _hw_post(_hw_client(tutor_app, 76), "q-hw-diag", [LINE_WORK])
    assert status == 200
    assert body["reply"].rstrip("。") == reply.rstrip("。")
    assert "你已經把想法寫出來了" not in body["reply"]


def test_no_error_wording_is_not_counted_as_naming_an_error():
    from core.routes.analysis import _HW_SECOND_STAGE_NAMES_ERROR

    assert not _HW_SECOND_STAGE_NAMES_ERROR.search("這一步沒有錯，也不錯，沒錯。")
    assert _HW_SECOND_STAGE_NAMES_ERROR.search("正負號看錯了")


def test_model_error_text_is_not_parsed_as_a_tutor_reply():
    from core.ai_analyzer import parse_tutor_model_text

    assert parse_tutor_model_text("Error: 429 quota exceeded") is None
