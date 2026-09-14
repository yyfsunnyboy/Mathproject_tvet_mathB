from __future__ import annotations

import base64
import io
from pathlib import Path
import uuid

import pytest
from PIL import Image

from app import create_app
from core.handwriting_ai_check import _looks_blank_image, build_handwriting_check_response, HandwritingCheckContext
from models import SkillInfo, User, db


ROOT = Path(__file__).resolve().parents[1]
SKILL = "test_handwriting_canvas_capture"


def _png_data_url(*, with_stroke: bool) -> str:
    img = Image.new("RGBA", (48, 48), (255, 255, 255, 255) if with_stroke else (0, 0, 0, 0))
    if with_stroke:
        for x in range(6, 42):
            img.putpixel((x, 24), (0, 0, 0, 255))
            img.putpixel((x, 25), (0, 0, 0, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


@pytest.fixture()
def runtime_app(tmp_path):
    import config as cfg

    previous_uri = cfg.Config.SQLALCHEMY_DATABASE_URI
    cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + (tmp_path / "handwriting-canvas.db").as_posix()
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            user = User(username=f"hwc_{uuid.uuid4().hex[:10]}", password_hash="x", role="student")
            db.session.add(user)
            db.session.add(
                SkillInfo(
                    skill_id=SKILL,
                    skill_en_name="Handwriting canvas",
                    skill_ch_name="手寫畫布",
                    description="test",
                    gemini_prompt="test",
                    is_active=True,
                )
            )
            db.session.commit()
            yield app, user.id
    finally:
        cfg.Config.SQLALCHEMY_DATABASE_URI = previous_uri


def test_stroke_png_is_not_blank_and_empty_recognition_is_not_blank_canvas():
    stroke = _png_data_url(with_stroke=True)
    assert _looks_blank_image(stroke) is False
    result = build_handwriting_check_response(
        image_base64=stroke,
        ctx=HandwritingCheckContext(correct_answer="-12, 12"),
        ai_result={"mode": "unrecognized", "expression": "", "confidence": 0.99},
        checker=lambda *_a, **_k: False,
    )
    assert result["is_blank"] is False
    assert result["vision_invoked"] is True
    assert result["completion_state"] == "in_progress"
    assert "請先在白板作答" not in result["feedback"]


def test_transparent_blank_png_is_blank():
    blank = _png_data_url(with_stroke=False)
    assert _looks_blank_image(blank) is True
    result = build_handwriting_check_response(
        image_base64=blank,
        ctx=HandwritingCheckContext(correct_answer="-12, 12"),
        ai_result={"mode": "final_answer_only", "expression": "x=±12", "confidence": 0.99},
        checker=lambda *_a, **_k: True,
    )
    assert result["completion_state"] == "blank"
    assert result["is_blank"] is True
    assert result["vision_invoked"] is False
    assert "請先在白板作答" in result["feedback"]


def test_endpoint_with_strokes_invokes_vision_and_reaches_checker(runtime_app, monkeypatch):
    import core.routes.adaptive_api as adaptive_api
    import core.routes.practice as practice

    app, user_id = runtime_app
    client = app.test_client()
    uid = "canvas-stroke-pm12"
    stroke = _png_data_url(with_stroke=True)
    current = {
        "skill": SKILL,
        "skill_id": SKILL,
        "question_uid": uid,
        "question_text": "|x| = 12",
        "correct_answer": "-12, 12",
        "answer": "-12, 12",
        "answer_type": "solution_set",
        "checker": "solution_set_checker",
        "equivalence": "unordered_set",
        "answer_contract": {
            "answer_type": "solution_set",
            "checker": "solution_set_checker",
            "answer_equivalence": "unordered_set",
        },
    }
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
        sess["current_data"] = current
        sess["current_question_uid"] = uid
        sess["current_skill_id"] = SKILL

    vision_calls = {"n": 0}

    def _fake_vision(*_a, **_k):
        vision_calls["n"] += 1
        return {"expression": "x=±12", "mode": "final_answer_only", "confidence": 0.99}

    monkeypatch.setattr(adaptive_api, "_call_ai_handwriting_checker", _fake_vision)
    monkeypatch.setattr(practice, "resolve_check_context", lambda _body: (current, None))

    recognition = client.post(
        "/api/practice/ai-check-handwriting",
        json={"image_data_url": stroke, "image_base64": stroke, "question_uid": uid},
    ).get_json()
    assert recognition["is_blank"] is False
    assert recognition["image_payload_nonempty"] is True
    assert recognition["vision_invoked"] is True
    assert vision_calls["n"] == 1
    assert recognition["completion_state"] == "completed"
    assert recognition["normalized_answer"] == "x=±12"

    grade = client.post(
        "/check_answer",
        json={"answer": recognition["normalized_answer"], "question_uid": uid, "skill_id": SKILL},
    ).get_json()
    assert grade["correct"] is True


def test_endpoint_blank_canvas_skips_vision(runtime_app, monkeypatch):
    import core.routes.adaptive_api as adaptive_api

    app, user_id = runtime_app
    client = app.test_client()
    uid = "canvas-blank"
    blank = _png_data_url(with_stroke=False)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
        sess["current_data"] = {
            "skill": SKILL,
            "skill_id": SKILL,
            "question_uid": uid,
            "question_text": "|x| = 12",
            "correct_answer": "-12, 12",
        }
        sess["current_question_uid"] = uid
        sess["current_skill_id"] = SKILL

    vision_calls = {"n": 0}
    monkeypatch.setattr(
        adaptive_api,
        "_call_ai_handwriting_checker",
        lambda *_a, **_k: vision_calls.__setitem__("n", vision_calls["n"] + 1) or {},
    )

    recognition = client.post(
        "/api/practice/ai-check-handwriting",
        json={"image_data_url": blank, "image_base64": blank, "question_uid": uid},
    ).get_json()
    assert recognition["completion_state"] == "blank"
    assert recognition["is_blank"] is True
    assert recognition["vision_invoked"] is False
    assert vision_calls["n"] == 0
    assert "請先在白板作答" in recognition["feedback"]


@pytest.mark.parametrize(
    ("template_name", "markers"),
    [
        (
            "index.html",
            (
                "function captureHandwritingImageForRecognition",
                "function isInkCanvasBlank",
                "getElementById('handwriting-canvas')",
                "fillStyle = '#ffffff'",
                "await captureHandwritingImageForRecognition()",
                "請先在白板作答",
            ),
        ),
        (
            "adaptive_practice_v2.html",
            (
                "function captureHandwritingImageForRecognition",
                "function isCanvasBlank",
                'getElementById("handwriting-canvas")',
                'fillStyle = "#ffffff"',
                "await captureHandwritingImageForRecognition()",
                "請先在白板作答",
            ),
        ),
    ],
)
def test_practice_templates_capture_ink_on_white_background(template_name, markers):
    source = (ROOT / "templates" / template_name).read_text(encoding="utf-8")
    for marker in markers:
        assert marker in source
