"""Recognized steps stay intact, and handwriting context follows the question lifecycle."""

from __future__ import annotations

import base64
import io
import json
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

from core.handwriting_ai_check import (
    RECOGNITION_INCOMPLETE_REPLY,
    ink_band_count,
    join_recognized_work,
    recognition_is_last_line_only,
)
from models import User, db

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def tutor_app(tmp_path):
    import config as config_module
    from app import create_app

    db_path = tmp_path / "handwriting-lifecycle.db"
    previous_uri = config_module.Config.SQLALCHEMY_DATABASE_URI
    config_module.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        yield app
    finally:
        config_module.Config.SQLALCHEMY_DATABASE_URI = previous_uri


def test_join_recognized_work_keeps_every_line():
    work = join_recognized_work(
        "x=4",
        ["3x-5=7", "3x=12", "x=4"],
    )
    assert work.splitlines() == ["3x-5=7", "3x=12", "x=4"]
    assert recognition_is_last_line_only(work, ink_bands=4) is False


def test_last_line_only_needs_multiple_ink_bands():
    image = _two_band_png()
    assert ink_band_count(image) >= 2
    assert recognition_is_last_line_only("x=4", ink_band_count(image)) is True
    assert recognition_is_last_line_only("3x=12\nx=4", ink_band_count(image)) is False
    assert recognition_is_last_line_only("x=4", ink_bands=1) is False


def test_handwriting_transient_lifecycle_keeps_same_question():
    script = _lifecycle_script() + """
const steps = ['3x-5=7', '3x=12', 'x=4'];
let state = applyHandwritingTransientLifecycle(null, {
  type: 'ai-check-result',
  questionUid: 'q1',
  recognizedSteps: steps,
  normalizedAnswer: 'x=4',
  recognitionIncomplete: false,
});
state = applyHandwritingTransientLifecycle(state, { type: 'rerender', questionUid: 'q1' });
if (!state || state.recognizedSteps.join('|') !== steps.join('|')) {
  throw new Error('same-question rerender cleared work');
}
state = applyHandwritingTransientLifecycle(state, { type: 'rerender', questionUid: 'q2' });
if (state !== null) throw new Error('next question identity kept old work');
state = applyHandwritingTransientLifecycle({ questionUid: 'q2', recognizedSteps: ['x≤2'] }, { type: 'next-question' });
if (state !== null) throw new Error('next-question button kept old work');
state = applyHandwritingTransientLifecycle({ questionUid: 'q2', recognizedSteps: ['x≤2'] }, { type: 'clear-canvas' });
if (state !== null) throw new Error('clear-canvas kept old work');
state = applyHandwritingTransientLifecycle({ questionUid: 'q1', recognizedSteps: ['x≤2'], recognitionIncomplete: true }, {
  type: 'ai-check-start', questionUid: 'q1', submissionId: 'hw-new'
});
if (state.recognizedSteps.length !== 0 || state.recognitionIncomplete !== false) {
  throw new Error('new AI check did not overwrite old work');
}
state = applyHandwritingTransientLifecycle(state, {
  type: 'ai-check-result',
  questionUid: 'q1',
  recognizedSteps: ['2x>8', 'x>4'],
  normalizedAnswer: 'x>4',
  recognitionIncomplete: false,
});
if (JSON.stringify(state).includes('x≤2')) throw new Error('stale step survived a new check');
if (state.recognizedSteps[0] !== '2x>8') throw new Error('new steps were not stored');

function chatPayload(handwritingTransientState, questionUid) {
  const currentQuestion = { question_uid: questionUid };
  const activeHandwriting = handwritingTransientState
    && handwritingTransientState.questionUid === String((currentQuestion && currentQuestion.question_uid) || '')
    ? handwritingTransientState
    : null;
  return {
    student_answer: (activeHandwriting?.recognizedSteps || []).length
      ? activeHandwriting.recognizedSteps.join('\\n')
      : (activeHandwriting?.normalizedAnswer || ''),
    recognized_steps: activeHandwriting?.recognizedSteps || [],
    recognition_incomplete: activeHandwriting?.recognitionIncomplete === true,
  };
}
const previous = applyHandwritingTransientLifecycle(null, {
  type: 'ai-check-result',
  questionUid: 'q-old',
  recognizedSteps: ['x≤2'],
  normalizedAnswer: 'x≤2',
  recognitionIncomplete: false,
});
const nextQuestion = applyHandwritingTransientLifecycle(previous, { type: 'next-question' });
const nextPayload = JSON.stringify(chatPayload(nextQuestion, 'q-new'));
if (nextPayload.includes('x≤2')) throw new Error('previous student_work leaked into the next /chat_ai payload');
"""
    _run_node(script)


def test_student_visible_reply_rejects_raw_json():
    html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    start = html.index("function studentVisibleReply")
    end = html.index("function showSuggestions", start)
    script = html[start:end] + """
if (studentVisibleReply({reply: '先把常數移到右邊。'}, 'fallback') !== '先把常數移到右邊。') {
  throw new Error('plain reply was hidden');
}
const unwrapped = studentVisibleReply('{"reply":"先移項","follow_up_prompts":[]}', 'fallback');
if (unwrapped !== '先移項' || unwrapped.includes('{') || unwrapped.includes('"reply"')) {
  throw new Error('raw JSON was shown: ' + unwrapped);
}
if (studentVisibleReply('看不懂 {reply} 這段', 'fallback') !== 'fallback') {
  throw new Error('raw JSON fragment was shown');
}
"""
    _run_node(script)


def test_incomplete_recognition_skips_second_stage(tutor_app, monkeypatch):
    client = _login(tutor_app)
    calls = _block_second_stage(monkeypatch)
    response = client.post(
        "/analyze_handwriting",
        json={
            "image_data_url": "data:image/png;base64," + _png_b64(_two_band_png()),
            "normalized_answer": "x=4",
            "recognized_steps": ["x=4"],
            "question_text": "3x - 5 = 7",
            "expected_answer": "x=4",
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert calls["n"] == 0
    assert body["reply"] == RECOGNITION_INCOMPLETE_REPLY
    assert "兩個條件" not in body["reply"]
    assert "x≤2" not in body["reply"]


def test_correct_work_skips_second_stage(tutor_app, monkeypatch):
    client = _login(tutor_app)
    calls = _block_second_stage(monkeypatch)
    response = client.post(
        "/analyze_handwriting",
        json={
            "image_data_url": "data:image/png;base64," + _png_b64(_two_band_png()),
            "normalized_answer": "x>4",
            "recognized_steps": ["2x>8", "x>4"],
            "question_text": "2x - 1 > 7",
            "expected_answer": "x>4",
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert calls["n"] == 0
    assert body["handwriting_status"] == "correct"
    assert "2x>8" in body["handwriting_analysis"]["recognized_expression"]


def test_wrong_work_quotes_only_actual_steps(tutor_app, monkeypatch):
    client = _login(tutor_app)

    class _Reply:
        text = json.dumps({"reply": "你寫了 x≤2。下一步先改這一筆？", "is_process_correct": False, "correct": False})

    calls = {"n": 0}

    def fake(*_args, **_kwargs):
        calls["n"] += 1
        return _Reply()

    monkeypatch.setattr("core.routes.analysis.call_ai", fake)
    monkeypatch.setattr("core.routes.analysis.call_google_model", fake)
    response = client.post(
        "/analyze_handwriting",
        json={
            "image_data_url": "data:image/png;base64," + _png_b64(_two_band_png()),
            "normalized_answer": "2x=6",
            "recognized_steps": ["2x+3=11", "2x=6"],
            "question_text": "2x + 3 = 11",
            "expected_answer": "x=4",
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert calls["n"] == 1
    assert "x≤2" not in body["reply"]
    assert "兩個條件" not in body["reply"]
    assert "2x+3=11" in body["handwriting_analysis"]["recognized_expression"]


def _login(app):
    with app.app_context():
        if User.query.filter_by(username="hw_life").one_or_none() is None:
            db.session.add(User(
                username="hw_life",
                password_hash=generate_password_hash("pass1234"),
                role="student",
            ))
            db.session.commit()
    client = app.test_client()
    login = client.post("/login", data={"username": "hw_life", "password": "pass1234"})
    assert login.status_code == 302
    return client


def _block_second_stage(monkeypatch):
    calls = {"n": 0}

    def fail(*_args, **_kwargs):
        calls["n"] += 1
        raise AssertionError("second stage should not run")

    monkeypatch.setattr("core.routes.analysis.call_ai", fail)
    monkeypatch.setattr("core.routes.analysis.call_google_model", fail)
    return calls


def _two_band_png() -> bytes:
    from PIL import Image

    image = Image.new("L", (80, 80), 255)
    pixels = image.load()
    for x in range(8, 72):
        pixels[x, 12] = 0
        pixels[x, 13] = 0
        pixels[x, 52] = 0
        pixels[x, 53] = 0
    return _png_bytes(image)


def _png_bytes(image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _png_b64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("ascii")


def _lifecycle_script() -> str:
    html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    start = html.index("function applyHandwritingTransientLifecycle")
    end = html.index("let handwritingSubmissionSequence", start)
    return html[start:end]


def _node_binary() -> str:
    import os
    import shutil

    found = shutil.which("node")
    if found:
        return found
    local = os.environ.get("LOCALAPPDATA", "")
    candidate = Path(local) / "Programs" / "cursor" / "resources" / "app" / "resources" / "helpers" / "node.exe"
    if candidate.is_file():
        return str(candidate)
    raise AssertionError("node is required for the handwriting lifecycle check")


def _run_node(script: str) -> None:
    import subprocess

    node = _node_binary()
    completed = subprocess.run([node, "-e", script], check=False, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr or completed.stdout
