from __future__ import annotations

import uuid

import pytest

from app import create_app
from models import User, db
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"b4_graph1_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


@pytest.mark.parametrize(
    "skill_id,problem_type_id",
    [
        ("vh_數學B4_CentralTendencyMeasures", "chart_mode_bar_reading"),
        ("vh_數學B4_DispersionMeasures", "chart_range_line_reading"),
    ],
)
def test_visual_first_batch_generator_metadata(skill_id: str, problem_type_id: str) -> None:
    payload = generate_for_chap3_skill(
        skill_id=skill_id,
        problem_type_id=problem_type_id,
        seed=11,
        level=1,
    )
    assert payload["problem_type_id"] == problem_type_id
    assert payload["visual_backed"] is True
    assert payload["visual_asset_type"] == "chart"
    assert payload["runtime_mode"] == "visual_backed"
    assert payload["check_mode"] == "deterministic_auto_checked"
    assert payload["grading_mode"] == "deterministic_auto_checked"
    assert payload["image_base64"]
    assert payload["answer_type"] == "integer"
    assert payload["parameters"].get("scenario") in {"bar_mode", "line_range"}


def test_visual_first_batch_scenario_diversity() -> None:
    seen_bar = set()
    seen_line = set()
    for seed in range(1, 30):
        p_bar = generate_for_chap3_skill(
            skill_id="vh_數學B4_CentralTendencyMeasures",
            problem_type_id="chart_mode_bar_reading",
            seed=seed,
            level=1,
        )
        p_line = generate_for_chap3_skill(
            skill_id="vh_數學B4_DispersionMeasures",
            problem_type_id="chart_range_line_reading",
            seed=seed,
            level=1,
        )
        seen_bar.add(tuple(p_bar["parameters"]["values"]))
        seen_line.add(tuple(p_line["parameters"]["values"]))
    assert len(seen_bar) >= 2
    assert len(seen_line) >= 2


def test_get_next_question_visual_payload_and_check_answer(logged_client) -> None:
    q = logged_client.get(
        "/get_next_question?skill=vh_數學B4_CentralTendencyMeasures"
        "&problem_type=chart_mode_bar_reading&gen_seed=5&level=1"
    )
    assert q.status_code == 200, q.get_data(as_text=True)
    body = q.get_json() or {}
    assert body["problem_type_id"] == "chart_mode_bar_reading"
    assert body["visual_backed"] is True
    assert body["runtime_mode"] == "visual_backed"
    assert body["check_mode"] == "deterministic_auto_checked"
    assert body["grading_mode"] == "deterministic_auto_checked"
    assert body["answer_type"] == "integer"
    assert body["image_base64"]

    expected = generate_for_chap3_skill(
        skill_id="vh_數學B4_CentralTendencyMeasures",
        problem_type_id="chart_mode_bar_reading",
        seed=5,
        level=1,
    )
    ans = str(expected["correct_answer"])
    ck = logged_client.post("/check_answer", json={"answer": ans})
    assert ck.status_code == 200
    assert (ck.get_json() or {}).get("correct") is True


def test_practice_template_keeps_existing_numberline_style_hooks(logged_client) -> None:
    resp = logged_client.get("/practice?skill=vh_數學B4_CentralTendencyMeasures")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'id="question-text"' in html
    assert 'id="answer-input"' in html
    assert 'id="handwriting-canvas"' in html
    assert 'id="question-image-uploader"' in html
    assert 'id="analyze-handwriting-button"' in html
    assert "instant-question-image" in html


def test_ai_checked_review_mode_does_not_fall_into_deterministic_checker(logged_client) -> None:
    q = logged_client.get(
        "/get_next_question?skill=vh_數學B4_TreeDiagramCounting"
        "&problem_type=tree_diagram_listing&tree_diagram_index=0"
    )
    assert q.status_code == 200
    body = q.get_json() or {}
    assert body.get("grading_mode") == "ai_judged_free_response"

    ck = logged_client.post("/check_answer", json={"answer": "任意答案"})
    assert ck.status_code == 200
    ck_body = ck.get_json() or {}
    assert ck_body.get("correct") is False
    assert "AI" in str(ck_body.get("result", ""))


def test_existing_chap3_deterministic_mainline_not_broken(logged_client) -> None:
    q = logged_client.get(
        "/get_next_question?skill=vh_數學B4_CentralTendencyMeasures"
        "&problem_type=mean_basic_numeric&gen_seed=3&level=1"
    )
    assert q.status_code == 200
    body = q.get_json() or {}
    assert body["problem_type_id"] == "mean_basic_numeric"
    assert body["answer_type"] == "integer"


def test_not_enabled_reserved_ux_not_regressed(logged_client) -> None:
    q = logged_client.get("/get_next_question?skill=vh_數學B4_StatisticalChartReading")
    assert q.status_code == 422
    body = q.get_json() or {}
    assert "error" in body
    assert "not enabled" in body["error"].lower()
