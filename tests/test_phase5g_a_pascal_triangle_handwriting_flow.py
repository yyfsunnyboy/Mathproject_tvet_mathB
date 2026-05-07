# -*- coding: utf-8 -*-
"""Phase 5G-A: Pascal triangle handwriting integration tests."""

from __future__ import annotations

import base64
import uuid

from app import create_app
from core.vocational_math_b4.free_response.pascal_triangle_judge import (
    build_pascal_triangle_payload,
    pascal_row,
)
from models import User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _make_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"pf5g_a_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def test_pascal_row_helper() -> None:
    assert pascal_row(4) == [1, 4, 6, 4, 1]


def test_build_pascal_payload_index_0_row_listing() -> None:
    payload = build_pascal_triangle_payload("pascal_row_listing", index=0)
    assert payload["problem_type_id"] == "pascal_triangle_handwriting"
    assert payload["answer_type"] == "handwriting"
    assert payload["grading_mode"] == "ai_judged_free_response"
    assert payload["variant"] == "pascal_row_listing"
    assert payload["expected_row"] == [1, 3, 3, 1]


def test_build_pascal_payload_index_1_binomial() -> None:
    payload = build_pascal_triangle_payload("pascal_binomial_expansion", index=0)
    assert payload["variant"] == "pascal_binomial_expansion"
    assert "(x+y)^3" in payload["question_text"]
    assert payload["expected_terms"][1]["coefficient"] == 3
    assert payload["expected_terms"][1]["x_power"] == 2
    assert payload["expected_terms"][1]["y_power"] == 1


def test_pascal_get_next_question_index_0_is_handwriting() -> None:
    client = _make_client()
    resp = client.get(
        "/get_next_question?skill=vh_數學B4_PascalTriangle&problem_type=pascal_triangle_handwriting&pascal_triangle_index=0"
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["answer_type"] == "handwriting"
    assert body["grading_mode"] == "ai_judged_free_response"
    assert body["problem_type_id"] == "pascal_triangle_handwriting"
    assert "No module named" not in str(body)


def test_pascal_index_0_and_1_question_text_different() -> None:
    client = _make_client()
    resp0 = client.get(
        "/get_next_question?skill=vh_數學B4_PascalTriangle&problem_type=pascal_triangle_handwriting&pascal_triangle_index=0"
    )
    resp1 = client.get(
        "/get_next_question?skill=vh_數學B4_PascalTriangle&problem_type=pascal_triangle_handwriting&pascal_triangle_index=1"
    )
    assert resp0.status_code == 200
    assert resp1.status_code == 200
    assert resp0.get_json()["new_question_text"] != resp1.get_json()["new_question_text"]


def test_pascal_analyze_handwriting_branch_no_500(monkeypatch) -> None:
    client = _make_client()
    q_resp = client.get(
        "/get_next_question?skill=vh_數學B4_PascalTriangle&problem_type=pascal_triangle_handwriting&pascal_triangle_index=0"
    )
    assert q_resp.status_code == 200

    class _R:
        text = '{"status":"needs_review","feedback":"手寫不清楚，請重寫。"}'

    def _fake_call_ai(*args, **kwargs):
        return _R()

    monkeypatch.setattr("core.routes.analysis.call_ai", _fake_call_ai)
    monkeypatch.setattr("core.routes.analysis.call_google_model", _fake_call_ai)

    tiny_png = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9WlZ0x8AAAAASUVORK5CYII="
    )
    resp = client.post(
        "/analyze_handwriting",
        json={
            "problem_type": "pascal_triangle_handwriting",
            "image_data_url": f"data:image/png;base64,{tiny_png}",
            "question_text": q_resp.get_json()["new_question_text"],
        },
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["success"] is True
    assert body["handwriting_status"] in {"needs_review", "partial", "incorrect", "correct"}


def test_dashboard_pascal_card_links_to_practice_not_free_response() -> None:
    client = _make_client()
    resp = client.get("/dashboard?view=curriculum&curriculum=vocational&volume=數學B4&chapter=1+排列組合")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "巴斯卡三角形" in body
    assert "/free_response_practice" not in body
    assert "problem_type=pascal_triangle_handwriting" in body
    assert "answer_type=handwriting" in body
    assert "grading_mode=ai_judged_free_response" in body
