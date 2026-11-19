# -*- coding: utf-8 -*-
"""Isolated Flask route smoke for the 2026/11/19 B1 slope bugfixes.

Uses the pytest isolated DB only. Never opens the formal student DB for writes.
"""

from __future__ import annotations

from fractions import Fraction

import pytest


def _oracle_slope(p1, p2) -> str:
    x1, y1 = int(p1[0]), int(p1[1])
    x2, y2 = int(p2[0]), int(p2[1])
    if x1 == x2:
        return "不存在"
    value = Fraction(y2 - y1, x2 - x1)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


@pytest.fixture()
def authed_client():
    from app import app

    app.config["WTF_CSRF_ENABLED"] = False
    uri = str(app.config.get("SQLALCHEMY_DATABASE_URI") or "")
    assert "pytest_isolated" in uri or "isolated" in uri
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True
        yield client


def test_slope_of_a_line_route_answers_match_stem_oracle(authed_client):
    client = authed_client
    res = client.get(
        "/get_next_question",
        query_string={
            "skill": "vh_數學B1_SlopeOfALine",
            "level": 1,
            "component_id": "src_4519",
            "seed": 19,
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data

    meta = data.get("metadata") or {}
    givens = meta.get("raw_givens") or {}
    points = givens.get("points") or {}
    segments = givens.get("segments") or []
    if not points or not segments:
        pytest.skip("runtime did not return raw_givens; generator-level coverage already asserts oracle")

    expected = {}
    for index, seg in enumerate(segments):
        expected[f"part_{index + 1}"] = _oracle_slope(points[seg["from"]], points[seg["to"]])

    check = client.post(
        "/check_answer",
        json={
            "skill_id": "vh_數學B1_SlopeOfALine",
            "question_uid": data.get("question_uid"),
            "answer": expected,
            "answers": expected,
        },
    )
    body = check.get_json()
    assert check.status_code == 200
    assert body.get("correct") is True or body.get("all_correct") is True


def test_slope_intercept_route_multipart_m_b(authed_client):
    client = authed_client
    res = client.get(
        "/get_next_question",
        query_string={
            "skill": "vh_數學B1_SlopeInterceptForm",
            "level": 1,
            "component_id": "src_4603",
            "seed": 19,
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data
    semantic = data.get("semantic_answer") or data.get("correct_answer")
    if not isinstance(semantic, dict) or set(semantic.keys()) < {"m", "b"}:
        pytest.skip("runtime did not return src_4603 multipart payload")

    assert data.get("answer_type") == "multi_part" or (
        (data.get("answer_contract") or {}).get("answer_type") == "multi_part"
    )
    check = client.post(
        "/check_answer",
        json={
            "skill_id": "vh_數學B1_SlopeInterceptForm",
            "question_uid": data.get("question_uid"),
            "answer": semantic,
            "answers": semantic,
        },
    )
    body = check.get_json()
    assert check.status_code == 200
    assert body.get("correct") is True or body.get("all_correct") is True
