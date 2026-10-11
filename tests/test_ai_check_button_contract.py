"""Shared AI-check button contract in both practice templates (source-level)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
ADAPTIVE = (ROOT / "templates" / "adaptive_practice_v2.html").read_text(encoding="utf-8")


def _function_body(source: str, signature: str, end_marker: str) -> str:
    start = source.index(signature)
    return source[start:source.index(end_marker, start + len(signature))]


def test_optional_ai_check_is_available_when_canvas_exists():
    for source in (INDEX, ADAPTIVE):
        assert "ui.handwriting_enabled !== false && ui.canvas_required !== false" in source
        assert "AI check blocked by ui_contract" not in source


def test_index_checks_ink_before_any_request_and_never_needs_the_text_field():
    body = _function_body(INDEX, "async function submitHandwritingAsAnswer", "function setupAIButton")
    blank = body.index("isInkCanvasBlank()")
    assert blank < body.index("/api/practice/ai-check-handwriting")
    assert "請先在白板寫下你的作答" in body
    assert "answer-input" not in body[:body.index("/api/practice/ai-check-handwriting")]


def test_index_requests_are_bounded_and_failures_are_readable():
    body = _function_body(INDEX, "async function submitHandwritingAsAnswer", "function setupAIButton")
    for url in ("'/check_answer'", "'/analyze_handwriting'"):
        assert f"postJsonWithTimeout({url}" in body
    assert "'/api/practice/ai-check-handwriting'" in body
    assert body.count("aiCheckFailureMessage(") >= 3
    assert "recognized_steps" in body
    assert "correct_answer" not in body.split("const payload", 1)[-1].split("};", 1)[0]
    helper = _function_body(INDEX, "function aiCheckFailureMessage", "async function submitHandwritingAsAnswer")
    assert "ai_unavailable" in helper and "409" in helper


def test_index_button_always_releases_and_resets_on_new_question():
    body = _function_body(INDEX, "function setupAIButton", "isProcessing = true;\n                analyzeBtn.textContent = '分析中...'")
    assert "const runId = ++aiCheckRunId;" in body
    finally_block = body[body.index("} finally {"):]
    assert "releaseAiCheckButton();" in finally_block
    assert "window.resetAiCheckForNewQuestion" in body
    reset = _function_body(INDEX, "function resetAIChat", "}\n")
    assert "resetAiCheckForNewQuestion" in reset
    assert "這一題沒有手寫區" in body


def test_adaptive_checks_ink_guards_double_submit_and_releases_button():
    body = _function_body(ADAPTIVE, "async function analyzeHandwriting", "      return;\n      try {")
    assert body.index("isCanvasBlank()") < body.index('fetch("/api/practice/ai-check-handwriting"')
    guard = body.index("if (analyzeCanvasBtn.disabled) return;")
    assert guard < body.index("analyzeCanvasBtn.disabled = true;")
    assert body.count("signal: aiCheckTimeoutSignal()") >= 3
    assert "recognized_steps" in body
    finally_block = body[body.rindex("} finally {"):]
    assert "analyzeCanvasBtn.disabled = false;" in finally_block
    assert "aiCheckErrorText(err)" in body
    assert "resolveDrawingUiContract(question).aiCheckAvailable" in body
    # The adaptive page has no status bar element, so notices must reach the chat.
    assert 'id="statusText"' not in ADAPTIVE
    assert 'addMessage("bot", text)' in body
    assert body.index('await notify("請先在白板寫下你的作答') < body.index('fetch("/api/practice/ai-check-handwriting"')


def test_neither_template_sends_a_frontend_correct_answer_to_the_tutor():
    for source, signature, end in (
        (INDEX, "async function submitHandwritingAsAnswer", "function setupAIButton"),
        (ADAPTIVE, "async function analyzeHandwriting", "      return;\n      try {"),
    ):
        body = _function_body(source, signature, end)
        assert "expected_answer:" not in body
        assert "correct_answer:" not in body
