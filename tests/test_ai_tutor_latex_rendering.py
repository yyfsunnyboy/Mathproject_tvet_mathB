"""AI Tutor LaTeX display: parsing keeps TeX, and every tutor bubble shares one renderer."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from core.ai_analyzer import clean_and_parse_json, parse_tutor_model_text
from core.practice_question_store import _STORE
from tests.test_ai_tutor_pedagogical_contract import (  # noqa: F401  (fixture)
    MIDPOINT_ANSWER,
    MIDPOINT_QUESTION,
    _client,
    _hw_login,
    _image_data_url,
    _install,
    _seed_handwriting,
    tutor_app,
)

ROOT = Path(__file__).resolve().parents[1]
NORMALIZER = ROOT / "static" / "js" / "math_display_normalizer.js"
CONTROL_CHARS = re.compile(r"[\t\f\b\r\x0b]")

# Raw model text exactly as Gemini emits it: single backslashes inside JSON strings.
RAW_REPLY_JSON = (
    '{"reply": "你寫的 $4 \\times 4 \\times 4$ 是對的。\\n'
    '接著看 \\frac{2}{3} 與 \\sqrt{x^2+y^2}，並確認 $x \\leq 3$、\\(a \\neq b\\)。\\n'
    '最後 \\[\\left(1\\right)\\] 也要寫出來。", '
    '"suggested_questions": ["為什麼 $4 \\times 4 \\times 4$ 可以寫成次方？", '
    '"\\frac{2}{3} 要怎麼化成小數？", "x \\leq 3 包含 3 嗎？"]}'
)
LATEX_TOKENS = ("\\times", "\\frac{2}{3}", "\\sqrt{x^2+y^2}", "\\leq", "\\(a \\neq b\\)", "\\[\\left(1\\right)\\]")


def _assert_latex_kept(reply: str) -> None:
    for token in LATEX_TOKENS:
        assert token in reply, token
    assert not CONTROL_CHARS.search(reply)
    assert "imes" not in reply.replace("\\times", "")
    assert reply.count("\n") == 2


@pytest.mark.parametrize("parser", [clean_and_parse_json, parse_tutor_model_text])
def test_single_backslash_latex_survives_model_json_parsing(parser):
    data = parser(RAW_REPLY_JSON)
    _assert_latex_kept(data["reply"])
    assert data["suggested_questions"] == [
        "為什麼 $4 \\times 4 \\times 4$ 可以寫成次方？", "\\frac{2}{3} 要怎麼化成小數？", "x \\leq 3 包含 3 嗎？",
    ]


@pytest.mark.parametrize("parser", [clean_and_parse_json, parse_tutor_model_text])
def test_properly_escaped_json_is_not_double_escaped(parser):
    payload = {"reply": "先算 $4 \\times 4$，\n再看 \\frac{1}{2}。", "suggested_questions": ["a", "b", "c"]}
    data = parser(json.dumps(payload, ensure_ascii=False))
    assert data["reply"] == payload["reply"]


def test_round_one_handwriting_reply_keeps_latex(tutor_app, monkeypatch):
    import core.routes.analysis as analysis

    _hw_login(monkeypatch, 81)
    _STORE["user:81"] = {"q-tex": {
        "question_uid": "q-tex", "skill_id": "vh_test",
        "question_text": MIDPOINT_QUESTION, "correct_answer": MIDPOINT_ANSWER,
    }}

    class Reply:
        text = RAW_REPLY_JSON

    monkeypatch.setattr(analysis, "call_ai", lambda *a, **k: Reply())
    monkeypatch.setattr(analysis, "call_google_model", lambda *a, **k: Reply())
    client = tutor_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "81"
        sess["_fresh"] = True
    response = client.post("/analyze_handwriting", json={
        "question_uid": "q-tex", "image_data_url": _image_data_url(),
        "normalized_answer": "4 \\times 4 \\times 4", "recognized_steps": ["4 \\times 4 \\times 4"],
    })
    body = response.get_json()
    assert response.status_code == 200
    _assert_latex_kept(body["reply"])
    assert len(body["suggested_questions"]) == 3
    assert "\\frac{2}{3} 要怎麼化成小數？" in body["suggested_questions"]


def test_round_two_chat_reply_keeps_latex(tutor_app, monkeypatch):
    import core.ai_analyzer as analyzer
    import core.ai_wrapper as ai_wrapper

    _install("tex2", "q-tex2")
    _seed_handwriting(tutor_app, "tex2", "q-tex2", ["4 \\times 4 \\times 4"])

    class Reply:
        text = RAW_REPLY_JSON.replace('"suggested_questions"', '"follow_up_prompts"')

    monkeypatch.setattr(analyzer, "get_ai_client", lambda **_k: object())
    monkeypatch.setattr(ai_wrapper, "call_ai_with_retry", lambda *a, **k: Reply())
    response = _client(tutor_app, "tex2").post(
        "/chat_ai", json={"question_uid": "q-tex2", "question": "下一步是什麼？"})
    body = response.get_json()
    assert response.status_code == 200
    _assert_latex_kept(body["reply"])
    assert len(body["suggested_questions"]) == 3


# --- shared display normalizer (Node) --------------------------------------

def _node() -> str:
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed")
    return node


def _tutor_normalize(values: list[str]) -> list[str]:
    script = (
        "const n=require(process.argv[1]);"
        "process.stdout.write(JSON.stringify(JSON.parse(process.argv[2]).map(v=>n.normalizeTutorText(v))));"
    )
    completed = subprocess.run(
        [_node(), "-e", script, str(NORMALIZER), json.dumps(values, ensure_ascii=False)],
        cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8",
    )
    return json.loads(completed.stdout)


def test_bare_latex_runs_are_wrapped_without_wrapping_chinese_prose():
    assert _tutor_normalize([
        "其實 4 \\times 4 \\times 4 就是 4 的 3 次方。",
        "先算 \\frac{2}{3} 再看 \\sqrt{x^2+y^2}。",
        "條件是 x \\leq 3，對嗎？",
        "第一行 f(x) = 2x \\times 3\n第二行 \\frac{1}{2}",
    ]) == [
        "其實 \\(4 \\times 4 \\times 4\\) 就是 4 的 3 次方。",
        "先算 \\(\\frac{2}{3}\\) 再看 \\(\\sqrt{x^2+y^2}\\)。",
        "條件是 \\(x \\leq 3\\)，對嗎？",
        "第一行 \\(f(x) = 2x \\times 3\\)\n第二行 \\(\\frac{1}{2}\\)",
    ]


def test_delimited_math_prose_and_paths_are_left_alone():
    values = [
        "其實 $4 \\times 4 \\times 4$ 就是 $4^3$。",
        "已知 \\(a \\neq b\\) 與 \\[\\left(1\\right)\\]",
        "$$\\frac{1}{2}$$ 是一半",
        "純文字說明，沒有數學。",
        "Let x \\leq 3 hold for every value",
        "路徑 C:\\tmp\\file 不要動",
        "<img src=x onerror=alert(1)>",
    ]
    assert _tutor_normalize(values) == values


# --- one renderer for every tutor surface -----------------------------------

def _between(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    return source[begin:source.index(end, begin)]


def test_practice_page_rounds_and_suggestions_share_tutor_renderer():
    source = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert "math_display_normalizer.js') }}?v=tutor-math-1" in source
    assert "MathDisplayNormalizer.typesetTutorElement(element)" in source
    round_one = _between(source, "async function requestHandwritingTutorFeedback", "\n            }\n")
    assert "msg.textContent = studentVisibleReply(" in round_one
    assert "renderTutorMath(msg)" in round_one
    round_two = _between(source, "function addBotMessage(text)", "\n        }\n")
    assert "messageDiv.textContent" in round_two
    assert "renderTutorMath(messageDiv)" in round_two
    assert "typesetPromise" not in round_two
    dynamic = _between(source, "function showDynamicSuggestions", "\n        }\n")
    assert "btn.textContent = promptText" in dynamic and "renderTutorMath(container)" in dynamic
    legacy = _between(source, "function showSuggestions(prompts)", "\n        }\n")
    assert "innerHTML = promptText" not in legacy and "btn.textContent = promptText" in legacy
    observer = _between(source, "const forceRender = () => {", "};")
    assert "renderTutorMath(chatBox)" in observer and "typesetPromise" not in observer


def test_adaptive_page_tutor_bubbles_and_suggestions_share_tutor_renderer():
    source = (ROOT / "templates" / "adaptive_practice_v2.html").read_text(encoding="utf-8")
    assert "math_display_normalizer.js') }}?v=tutor-math-1" in source
    assert "MathDisplayNormalizer.typesetTutorElement(element)" in source
    assert "await typesetTutorMath(div)" in source
    assert "typesetMath(thinking)" not in source
    assert source.count("await typesetTutorMath(thinking)") == 5
    assert "if (questions.length) typesetTutorMath(box)" in source
    assert 'element.innerHTML = escapeHtml(text).replace(/\\n/g, "<br>")' in source


def test_tutor_typeset_is_serialized_and_waits_for_dom_insertion():
    source = NORMALIZER.read_text(encoding="utf-8")
    tutor = _between(source, "function typesetTutorElement(element)", "\n  }\n")
    assert "normalizeTutorElement(element)" in tutor and "typesetSerialized(element" in tutor
    queue = _between(source, "function typesetSerialized(element, clearFirst)", "\n  }\n")
    assert "typesetChain = typesetChain" in queue
    assert ".then(mathJaxReady)" in queue
    assert "element.isConnected" in queue
    assert "mathJax.startup.promise" in _between(source, "function mathJaxReady()", "\n  }\n")
