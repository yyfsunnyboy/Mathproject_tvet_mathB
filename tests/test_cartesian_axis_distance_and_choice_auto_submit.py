from __future__ import annotations

import re
import uuid
from urllib.parse import quote

import pytest

from app import create_app
from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.slot_generators import generate_from_problem_type_spec
from models import User, db

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
PT = "single_choice_choose_correct_statement_axis_distance_coordinate_point"

_POINT_RE = re.compile(
    r"P\s*\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)",
    re.UNICODE,
)


def _parse_axis_distance_question(question_text: str) -> tuple[int, int, str]:
    match = _POINT_RE.search(question_text)
    assert match is not None, f"missing coordinate point in stem: {question_text!r}"
    x, y = int(match.group(1)), int(match.group(2))
    assert x != 0 and y != 0
    if "到 x 軸" in question_text:
        return x, y, "x"
    if "到 y 軸" in question_text:
        return x, y, "y"
    raise AssertionError(f"axis not recognized in stem: {question_text!r}")


def _expected_distance(x: int, y: int, axis: str) -> int:
    return abs(y) if axis == "x" else abs(x)


def _choice_texts(payload: dict) -> list[str]:
    choices = payload.get("choices") or []
    return [
        str(c.get("text", c) if isinstance(c, dict) else c).strip()
        for c in choices
    ]


def _correct_choice_text(payload: dict) -> str:
    answer_label = str(payload.get("answer", "")).strip().upper()
    for idx, choice in enumerate(payload.get("choices") or []):
        if isinstance(choice, dict):
            label = str(choice.get("label", "")).strip().upper() or chr(ord("A") + idx)
            if label == answer_label:
                return str(choice.get("text", "")).strip()
    raise AssertionError(f"correct choice not found for label={answer_label!r}")


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"cartesian_axis_distance_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client


def test_axis_distance_generator_supports_x_and_y_axes_over_50_samples():
    spec = load_problem_type_spec(SKILL_ID, PT, prefer="auto")
    assert spec is not None

    saw_x = False
    saw_y = False
    for seed in range(50):
        payload = generate_from_problem_type_spec(SKILL_ID, spec, seed=seed)
        qt = str(payload.get("question_text", ""))
        if "到 x 軸" not in qt and "到 y 軸" not in qt:
            continue

        x, y, axis = _parse_axis_distance_question(qt)
        expected = _expected_distance(x, y, axis)
        correct_text = _correct_choice_text(payload)
        assert correct_text == str(expected)

        texts = _choice_texts(payload)
        assert len(texts) == 4
        assert len(set(texts)) == 4
        assert correct_text in texts

        target = (payload.get("metadata") or {}).get("target") or {}
        distance_to = str(target.get("distance_to", ""))
        if axis == "x":
            saw_x = True
            assert "到 x 軸" in qt
            assert distance_to == "x_axis"
        else:
            saw_y = True
            assert "到 y 軸" in qt
            assert distance_to == "y_axis"

        explanation = str(payload.get("explanation", ""))
        if axis == "x":
            assert "|y|" in explanation or "y 座標" in explanation
        else:
            assert "|x|" in explanation or "x 座標" in explanation

    assert saw_x, "expected at least one x-axis distance question in 50 samples"
    assert saw_y, "expected at least one y-axis distance question in 50 samples"


def test_practice_page_choice_click_triggers_submit_handler(logged_client) -> None:
    resp = logged_client.get(f"/practice?skill={quote(SKILL_ID)}")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "setChoiceOptionsDisabled" in html
    assert "submitBtn.onclick()" in html
    assert "analyze-handwriting-button" in html
    assert "submitBtn.disabled = true" in html


def test_practice_choice_auto_check_answer_flow(logged_client) -> None:
    body = None
    for seed in range(50):
        q = logged_client.get(
            f"/get_next_question?skill={quote(SKILL_ID)}&level=1&gen_seed={seed}"
        )
        assert q.status_code == 200
        candidate = q.get_json() or {}
        qt = str(candidate.get("new_question_text") or candidate.get("question_text") or "")
        choices = candidate.get("choices") or []
        if choices and ("到 x 軸" in qt or "到 y 軸" in qt):
            body = candidate
            break
    assert body is not None, "expected an axis-distance choice question from route"

    choices = body.get("choices") or []
    qt = str(body.get("new_question_text") or body.get("question_text") or "")
    x, y, axis = _parse_axis_distance_question(qt)
    expected = str(_expected_distance(x, y, axis))

    answer_label = None
    for idx, choice in enumerate(choices):
        if isinstance(choice, dict):
            label = str(choice.get("label", "")).strip().upper() or chr(ord("A") + idx)
            text = str(choice.get("text", "")).strip()
        else:
            label = chr(ord("A") + idx)
            text = str(choice).strip()
        if text == expected:
            answer_label = label
            break
    assert answer_label in {"A", "B", "C", "D"}

    ok = logged_client.post("/check_answer", json={"answer": answer_label}).get_json() or {}
    assert ok.get("correct") is True

    bad = logged_client.post("/check_answer", json={"answer": "Z"}).get_json() or {}
    assert bad.get("correct") is False


def test_short_answer_still_uses_manual_submit_button(logged_client) -> None:
    spec = load_problem_type_spec(
        SKILL_ID,
        "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
        prefer="auto",
    )
    assert spec is not None
    payload = generate_from_problem_type_spec(SKILL_ID, spec, seed=3)
    assert not payload.get("choices")

    resp = logged_client.get(f"/practice?skill={quote(SKILL_ID)}")
    html = resp.get_data(as_text=True)
    assert 'id="submit-button"' in html or 'submitBtn' in html
    assert "submitBtn.onclick" in html
