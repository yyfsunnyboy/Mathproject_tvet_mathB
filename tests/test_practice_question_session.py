# -*- coding: utf-8 -*-
"""Practice runtime question state: uid store, cross-skill, cookie, duplicate."""

from __future__ import annotations

import json
import uuid
from urllib.parse import quote

import pytest

from app import create_app
from core.practice_question_store import (
    estimate_session_cookie_bytes,
    get_question_by_uid,
    resolve_check_context,
)
from core.session import set_current
from models import User, db

SKILL_DISTANCE = "vh_數學B1_DistanceBetweenTwoPointsInPlane"
SKILL_DIVISION = "vh_數學B1_DivisionPointCoordinates"
PT_DISTANCE = "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
PT_DIVISION = "ordered_pair_compute_internal_division_point_coordinates_short_answer_two_coordi"


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"pract_{uuid.uuid4().hex[:10]}",
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


def _check_payload(question: dict, answer: str, *, skill_id: str = "") -> dict:
    return {
        "skill_id": skill_id or question.get("skill_id") or "",
        "question_uid": question.get("question_uid") or "",
        "problem_type_id": question.get("problem_type_id") or "",
        "answer": answer,
    }


def test_late_submit_after_next_question_race(logged_client) -> None:
    """Q1 submit after Q2 loaded must not grade against Q1 (simulates network delay)."""
    q1 = logged_client.get(
        f"/get_next_question?skill={quote(SKILL_DIVISION)}&problem_type={PT_DIVISION}&gen_seed=50&level=1"
    ).get_json() or {}
    q2 = logged_client.get(
        f"/get_next_question?skill={quote(SKILL_DIVISION)}&problem_type={PT_DIVISION}&gen_seed=51&level=1"
    ).get_json() or {}
    late = logged_client.post(
        "/check_answer",
        json=_check_payload(q1, "(0,0)"),
    ).get_json() or {}
    assert late.get("stale_question") is True
    current = logged_client.post(
        "/check_answer",
        json=_check_payload(q2, "__wrong__"),
    ).get_json() or {}
    assert current.get("stale_question") is not True


def test_cross_skill_stale_session(logged_client) -> None:
    dist_q = logged_client.get(
        f"/get_next_question?skill={quote(SKILL_DISTANCE)}&problem_type={PT_DISTANCE}&gen_seed=42&level=1"
    ).get_json() or {}
    assert dist_q.get("question_uid")

    div_q = logged_client.get(
        f"/get_next_question?skill={quote(SKILL_DIVISION)}&problem_type={PT_DIVISION}&gen_seed=7&level=1"
    ).get_json() or {}
    assert div_q.get("question_uid") != dist_q.get("question_uid")

    stale = logged_client.post(
        "/check_answer",
        json=_check_payload(dist_q, "4", skill_id=SKILL_DISTANCE),
    ).get_json() or {}
    assert stale.get("stale_question") is True

    ok = logged_client.post(
        "/check_answer",
        json=_check_payload(div_q, "__wrong__"),
    ).get_json() or {}
    assert ok.get("stale_question") is not True
    assert "4 或 10" not in str(ok.get("result", ""))


def test_skill_mismatch_returns_stale(logged_client) -> None:
    q = logged_client.get(
        f"/get_next_question?skill={quote(SKILL_DIVISION)}&problem_type={PT_DIVISION}&gen_seed=3&level=1"
    ).get_json() or {}
    resp = logged_client.post(
        "/check_answer",
        json={
            "skill_id": SKILL_DISTANCE,
            "question_uid": q.get("question_uid"),
            "answer": "(0,0)",
        },
    ).get_json() or {}
    assert resp.get("stale_question") is True


def test_question_uid_missing_in_store_returns_stale(logged_client) -> None:
    logged_client.get(
        f"/get_next_question?skill={quote(SKILL_DIVISION)}&problem_type={PT_DIVISION}&gen_seed=5&level=1"
    )
    resp = logged_client.post(
        "/check_answer",
        json={
            "skill_id": SKILL_DIVISION,
            "question_uid": str(uuid.uuid4()),
            "answer": "(0,0)",
        },
    ).get_json() or {}
    assert resp.get("stale_question") is True


def test_session_cookie_size_under_limit(logged_client) -> None:
    logged_client.get(
        f"/get_next_question?skill={quote(SKILL_DIVISION)}&problem_type={PT_DIVISION}&gen_seed=11&level=1"
    )
    with logged_client.session_transaction() as sess:
        size = len(json.dumps(dict(sess), ensure_ascii=False).encode("utf-8"))
        assert "current_data" not in sess or not sess.get("current_data")
        assert sess.get("current_question_uid")
        assert isinstance(sess.get("recent_question_uids"), list)
    assert size < 3500, f"session cookie too large: {size}"


def test_consecutive_100_questions_no_cookie_bloat(logged_client) -> None:
    last_uid = ""
    for seed in range(100):
        q = logged_client.get(
            f"/get_next_question?skill={quote(SKILL_DIVISION)}&problem_type={PT_DIVISION}&gen_seed={1000 + seed}&level=1"
        ).get_json() or {}
        uid = str(q.get("question_uid", ""))
        assert uid
        assert uid != last_uid
        last_uid = uid
        resp = logged_client.post(
            "/check_answer",
            json=_check_payload(q, "__wrong__"),
        ).get_json() or {}
        assert resp.get("stale_question") is not True
        assert "4 或 10" not in str(resp.get("result", ""))
    with logged_client.session_transaction() as sess:
        size = len(json.dumps(dict(sess), ensure_ascii=False).encode("utf-8"))
        recent = sess.get("recent_question_uids") or []
        assert len(recent) <= 20
    assert size < 3500


def test_duplicate_submission_no_double_grade(logged_client) -> None:
    q = logged_client.get(
        f"/get_next_question?skill={quote(SKILL_DIVISION)}&problem_type={PT_DIVISION}&gen_seed=88&level=1"
    ).get_json() or {}
    first = logged_client.post(
        "/check_answer",
        json=_check_payload(q, "__wrong__"),
    ).get_json() or {}
    assert first.get("duplicate_submission") is not True
    second = logged_client.post(
        "/check_answer",
        json=_check_payload(q, "__another_wrong__"),
    ).get_json() or {}
    assert second.get("duplicate_submission") is True
    assert second.get("result") == first.get("result")


def test_expired_question_after_window(logged_client) -> None:
    first_q = logged_client.get(
        f"/get_next_question?skill={quote(SKILL_DIVISION)}&problem_type={PT_DIVISION}&gen_seed=1&level=1"
    ).get_json() or {}
    first_uid = str(first_q.get("question_uid", ""))
    for seed in range(2, 24):
        logged_client.get(
            f"/get_next_question?skill={quote(SKILL_DIVISION)}&problem_type={PT_DIVISION}&gen_seed={seed}&level=1"
        )
    expired = logged_client.post(
        "/check_answer",
        json=_check_payload({"question_uid": first_uid, "skill_id": SKILL_DIVISION}, "1,2"),
    ).get_json() or {}
    assert expired.get("error") in {"question_expired", "stale_question_requires_reload"}
    assert expired.get("stale_question") is True


def test_division_coordinate_pair_not_or_join(logged_client) -> None:
    q = logged_client.get(
        f"/get_next_question?skill={quote(SKILL_DIVISION)}&problem_type={PT_DIVISION}&gen_seed=31&level=1"
    ).get_json() or {}
    bad = logged_client.post(
        "/check_answer",
        json=_check_payload(q, "9,9"),
    ).get_json() or {}
    result = str(bad.get("result", ""))
    assert "4 或 10" not in result
    if bad.get("correct") is False:
        assert "(" in result or "," in result


def test_distance_solution_set_still_or_join(logged_client) -> None:
    q = None
    for seed in range(1, 120):
        cand = logged_client.get(
            f"/get_next_question?skill={quote(SKILL_DISTANCE)}&problem_type={PT_DISTANCE}&gen_seed={seed}&level=1"
        ).get_json() or {}
        checker = str(cand.get("checker") or cand.get("checker_type") or "")
        ca = cand.get("correct_answer")
        if "solution_set" in checker or isinstance(ca, list):
            q = cand
            break
    assert q is not None
    wrong = logged_client.post(
        "/check_answer",
        json=_check_payload(q, "__wrong__"),
    ).get_json() or {}
    assert wrong.get("correct") is False
    assert " 或 " in str(wrong.get("result", ""))


def test_debug_clear_practice_state(logged_client) -> None:
    logged_client.get(
        f"/get_next_question?skill={quote(SKILL_DIVISION)}&problem_type={PT_DIVISION}&gen_seed=9&level=1"
    )
    resp = logged_client.post("/debug/clear_practice_state").get_json() or {}
    assert resp.get("ok") is True
    with logged_client.session_transaction() as sess:
        assert not sess.get("current_question_uid")


def test_resolve_check_context_unit() -> None:
    app = create_app()
    with app.test_request_context():
        from flask import session

        set_current(
            SKILL_DIVISION,
            {
                "question_text": "division point",
                "problem_type_id": PT_DIVISION,
                "correct_answer": "(1,2)",
                "checker": "coordinate_pair_checker",
            },
        )
        uid = session.get("current_question_uid")
        body = {"skill_id": SKILL_DIVISION, "question_uid": uid, "answer": "1,2"}
        payload, stale = resolve_check_context(body)
        assert stale is None
        assert payload is not None

        body_bad = {"skill_id": SKILL_DIVISION, "question_uid": str(uuid.uuid4()), "answer": "1,2"}
        _payload2, stale2 = resolve_check_context(body_bad)
        assert stale2 is not None


def test_estimate_session_cookie_bytes_small() -> None:
    app = create_app()
    with app.test_request_context():
        from flask import session

        set_current(
            SKILL_DIVISION,
            {
                "question_text": "x" * 500,
                "problem_type_id": PT_DIVISION,
                "correct_answer": "(1,2)",
                "metadata": {"big": "y" * 8000},
            },
        )
        assert estimate_session_cookie_bytes() < 3500
        assert "current_data" not in session or not session.get("current_data")
        uid = session.get("current_question_uid")
        assert uid and get_question_by_uid(uid)
