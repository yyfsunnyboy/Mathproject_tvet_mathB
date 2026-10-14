# -*- coding: utf-8 -*-
"""Chapter review save/resume (本章總複習存檔) and teacher first-attempt stats.

Runs only against the pytest isolated DB (tests/conftest.py); every test signs in
as its own freshly created student so runs never mix.
"""
import importlib
import json
import re
import uuid
from types import SimpleNamespace
from urllib.parse import quote

import pytest

from core import chapter_review_run as crr
from core import practice_type_rotation as ptr

SECTION_A = "vh_數學B3_SubSection_4_1_1"  # 3 practice types
SECTION_B = "vh_數學B3_SubSection_4_5_1"  # 2 practice types
B4_DET = "vh_數學B4_ProbabilityDefinition"
CHAPTER = "第4章 指數與對數"
WRONG_ANSWER = "987654321"


def _row(skill_id, section, order=1, chapter=CHAPTER, volume="數學B3"):
    return SimpleNamespace(
        skill_id=skill_id, curriculum="vocational", volume=volume,
        chapter=chapter, section=section, display_order=order,
    )


@pytest.fixture()
def app(monkeypatch):
    """Isolated-DB app whose checker verdict is pinned per submission.

    Grading is out of scope here; everything from ``_emit_check_result`` on (attempt
    persistence, run state) runs unchanged.
    """
    from app import create_app
    from core.routes import practice as practice_routes

    original = practice_routes._emit_check_result

    def _pinned(question_uid, skill_id, result, **kwargs):
        verdict = _VERDICT.get("next")
        if verdict is not None:
            result = {k: v for k, v in dict(result).items() if k not in {"invalid_input", "system_error"}}
            result.update(correct=verdict, status="correct" if verdict else "incorrect")
        return original(question_uid, skill_id, result, **kwargs)

    monkeypatch.setattr(practice_routes, "_emit_check_result", _pinned)
    application = create_app()
    application.config["TESTING"] = True
    return application


_VERDICT: dict = {}


@pytest.fixture()
def chapter_scope(monkeypatch):
    from core.routes import practice as practice_routes

    rows = [_row(SECTION_A, "4-1 指數"), _row(SECTION_B, "4-5 常用對數")]
    by_skill = {r.skill_id: r for r in rows}

    def _scope(skill_id):
        anchor = by_skill.get(skill_id)
        return (anchor, rows) if anchor is not None else (None, [])

    monkeypatch.setattr(practice_routes, "_practice_chapter_scope", _scope)
    return rows


def _new_student(app):
    from models import User, db

    with app.app_context():
        user = User(username=f"cr_{uuid.uuid4().hex[:12]}", password_hash="x", role="student")
        db.session.add(user)
        db.session.commit()
        return int(user.id)


def _client(app, user_id):
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
    return client


def _attempts(app, user_id):
    from models import PracticeAttempt, db

    with app.app_context():
        rows = (
            db.session.query(PracticeAttempt)
            .filter(PracticeAttempt.student_id == user_id)
            .order_by(PracticeAttempt.id.asc())
            .all()
        )
        return [
            SimpleNamespace(
                skill_id=r.skill_id, source=r.source, session_id=r.session_id,
                problem_type_id=r.problem_type_id, question_uid=r.question_uid, is_correct=r.is_correct,
            )
            for r in rows
        ]


def _next(client, skill, *, chapter_review=True):
    url = f"/get_next_question?skill={quote(skill)}&level=1&mode=type_rotation"
    if chapter_review:
        url += "&chapter_review=1"
    payload = client.get(url).get_json()
    assert payload is not None
    return payload


def _answer(client, payload, correct):
    _VERDICT["next"] = correct
    try:
        out = client.post(
            "/check_answer",
            json={"answer": WRONG_ANSWER, "skill_id": payload["skill_id"], "question_uid": payload["question_uid"]},
        ).get_json()
    finally:
        _VERDICT.clear()
    assert out["correct"] is correct, out
    return out


def _start(client, skill):
    return client.get(f"/practice/{quote(skill)}?chapter_review=start")


def _page_context(body):
    match = re.search(r"const CHAPTER_REVIEW = (.*?);\n", body)
    assert match, "CHAPTER_REVIEW context missing"
    return json.loads(match.group(1))


def test_chapter_review_attempt_is_saved_with_run_id(app, chapter_scope):
    uid = _new_student(app)
    client = _client(app, uid)
    assert _start(client, SECTION_A).status_code == 200
    payload = _next(client, SECTION_A)
    snap = payload["practice_type_rotation"]["chapter_review"]
    run_id = snap["run_id"]
    assert run_id.startswith("cr_")
    assert (snap["types_passed"], snap["types_total"], snap["answered"]) == (0, 5, 0)

    out = _answer(client, payload, True)
    rows = _attempts(app, uid)
    assert len(rows) == 1
    assert rows[0].source == "chapter_review"
    assert rows[0].session_id == run_id
    assert rows[0].problem_type_id == payload["practice_type_rotation"]["type_key"]
    saved = out["practice_type_rotation"]["chapter_review"]
    assert (saved["answered"], saved["correct"], saved["accuracy"], saved["streak"]) == (1, 1, 100, 1)
    assert saved["types_passed"] == 1


def test_general_practice_attempts_stay_general(app, chapter_scope):
    uid = _new_student(app)
    client = _client(app, uid)
    payload = _next(client, SECTION_A, chapter_review=False)
    assert "chapter_review" not in (payload.get("practice_type_rotation") or {})
    _answer(client, payload, True)
    rows = _attempts(app, uid)
    assert [(r.source, r.session_id) for r in rows] == [("general_practice", None)]


def test_accuracy_counts_first_verdict_per_question_and_streak_rebuilds(app, chapter_scope):
    uid = _new_student(app)
    client = _client(app, uid)
    _start(client, SECTION_A)
    first = _next(client, SECTION_A)
    _answer(client, first, False)
    out = _answer(client, first, True)  # re-submit of the same question
    snap = out["practice_type_rotation"]["chapter_review"]
    assert (snap["answered"], snap["correct"], snap["streak"]) == (1, 0, 0)
    assert out["practice_type_rotation"]["type_status"] == ptr.STATUS_WEAK
    assert len(_attempts(app, uid)) == 2

    second = _next(client, SECTION_A)
    _answer(client, second, True)
    third = _next(client, SECTION_A)
    out = _answer(client, third, True)
    snap = out["practice_type_rotation"]["chapter_review"]
    assert (snap["answered"], snap["correct"], snap["accuracy"], snap["streak"]) == (3, 2, 67, 2)

    page = _client(app, uid).get(f"/practice/{quote(SECTION_A)}?chapter_review=1").get_data(as_text=True)
    ctx = _page_context(page)
    summary = ctx["chapter_summary"]
    assert (summary["total_answered"], summary["correct"], ctx["streak"]) == (3, 2, 2)
    assert "67%（2/3）" in page
    assert 'id="chapter-review-streak">2<' in page


def test_resume_after_cookie_loss_serves_unseen_then_retry_never_passed(app, chapter_scope):
    uid = _new_student(app)
    client = _client(app, uid)
    _start(client, SECTION_A)
    p1 = _next(client, SECTION_A)
    _answer(client, p1, True)
    p2 = _next(client, SECTION_A)
    _answer(client, p2, False)
    passed_type = p1["practice_type_rotation"]["type_key"]
    weak_type = p2["practice_type_rotation"]["type_key"]
    run_id = p1["practice_type_rotation"]["chapter_review"]["run_id"]

    fresh = _client(app, uid)  # browser closed / cookie lost / other device
    body = _start(fresh, SECTION_A).get_data(as_text=True)
    ctx = _page_context(body)
    assert ctx["resume"]["run_id"] == run_id
    assert (ctx["resume"]["types_passed"], ctx["resume"]["answered"], ctx["resume"]["correct"]) == (1, 2, 1)
    assert "chapter_review=resume" in ctx["resume_url"]
    assert "chapter_review=restart" in ctx["restart_url"]

    resp = fresh.get(ctx["resume_url"])
    assert resp.status_code == 302
    assert quote(SECTION_A) in resp.headers["Location"] and "chapter_review=1" in resp.headers["Location"]

    unseen = sorted(set(ptr.get_practice_type_pool(SECTION_A, module=importlib.import_module(f"skills.{SECTION_A}")))
                    - {passed_type, weak_type})
    p3 = _next(fresh, SECTION_A)
    assert p3["practice_type_rotation"]["chapter_review"]["run_id"] == run_id
    assert [p3["practice_type_rotation"]["type_key"]] == unseen
    _answer(fresh, p3, True)
    p4 = _next(fresh, SECTION_A)
    assert p4["practice_type_rotation"]["type_key"] == weak_type
    assert {r.session_id for r in _attempts(app, uid)} == {run_id}


def test_restart_opens_new_run_and_keeps_old_attempts(app, chapter_scope):
    uid = _new_student(app)
    client = _client(app, uid)
    _start(client, SECTION_A)
    p1 = _next(client, SECTION_A)
    _answer(client, p1, False)
    old_run = p1["practice_type_rotation"]["chapter_review"]["run_id"]
    before = _attempts(app, uid)

    fresh = _client(app, uid)
    resp = fresh.get(f"/practice/{quote(SECTION_B)}?chapter_review=restart")
    assert resp.status_code == 302
    assert quote(SECTION_A) in resp.headers["Location"]  # a new run starts at the first section
    p = _next(fresh, SECTION_A)
    snap = p["practice_type_rotation"]["chapter_review"]
    assert snap["run_id"] != old_run
    assert (snap["answered"], snap["types_passed"]) == (0, 0)
    assert _attempts(app, uid) == before


def test_retry_type_returns_then_section_and_chapter_complete(app, chapter_scope):
    uid = _new_student(app)
    client = _client(app, uid)
    _start(client, SECTION_A)
    served = []
    for correct in (False, True, True):
        p = _next(client, SECTION_A)
        out = _answer(client, p, correct)
        served.append(p["practice_type_rotation"]["type_key"])
    assert out["practice_type_rotation"]["section_completed"] is False
    retry = _next(client, SECTION_A)
    assert retry["practice_type_rotation"]["type_key"] == served[0]
    out = _answer(client, retry, True)
    rotation = out["practice_type_rotation"]
    assert rotation["section_completed"] is True
    assert rotation["next_section_skill_id"] == SECTION_B
    assert _next(client, SECTION_A)["chapter_review_next_section"] == SECTION_B

    for _ in range(2):
        p = _next(client, SECTION_B)
        out = _answer(client, p, True)
    assert out["practice_type_rotation"]["chapter_completed"] is True
    done = _next(client, SECTION_B)
    assert done["chapter_completed"] is True
    assert done["chapter_summary"] == {
        "total_answered": 6, "correct": 5, "wrong": 1, "accuracy": 83.3,
        "types_completed": 5, "sections_completed": 2, "chapter_completed": True,
    }
    assert "question_text" not in done


def test_b4_deterministic_chapter_review_persists_and_resumes(app, monkeypatch):
    from core.routes import practice as practice_routes
    from models import B4Chap2VisibilityAuditLog, db

    anchor = _row(B4_DET, "2-2 機率的運算", chapter="2 機率", volume="數學B4")
    monkeypatch.setattr(practice_routes, "_practice_chapter_scope", lambda sid: (anchor, [anchor]))
    uid = _new_student(app)

    general = _client(app, uid)
    _answer(general, _next(general, B4_DET, chapter_review=False), True)
    assert _attempts(app, uid) == []  # general B4 practice keeps writing only the audit log

    client = _client(app, uid)
    _start(client, B4_DET)
    p1 = _next(client, B4_DET)
    rotation = p1["practice_type_rotation"]
    assert rotation["type_key"] in {"classical_probability_fraction", "dice_coin_probability_count"}
    assert p1["problem_type_id"] == rotation["type_key"]
    _answer(client, p1, True)
    rows = _attempts(app, uid)
    assert [(r.source, r.session_id, r.problem_type_id) for r in rows] == [
        ("chapter_review", rotation["chapter_review"]["run_id"], rotation["type_key"])
    ]
    with app.app_context():
        audit = db.session.query(B4Chap2VisibilityAuditLog).filter_by(student_id=uid).count()
    assert audit == 1  # only the general practice answer

    resumed = _client(app, uid)
    p2 = _next(resumed, B4_DET)
    assert p2["practice_type_rotation"]["chapter_review"]["run_id"] == rotation["chapter_review"]["run_id"]
    assert p2["practice_type_rotation"]["type_key"] != rotation["type_key"]


def test_run_summary_first_verdict_streak_and_progress():
    verdicts = [
        {"skill_id": "s1", "type_key": "a", "correct": False},
        {"skill_id": "s1", "type_key": "b", "correct": True},
        {"skill_id": "s1", "type_key": "a", "correct": True},
        {"skill_id": "s2", "type_key": "c", "correct": True},
    ]
    sections = [("s1", ["a", "b"]), ("s2", ["c", "d"])]
    snap = crr.summarize_run(verdicts, sections)
    assert (snap["answered"], snap["correct"], snap["accuracy"], snap["streak"]) == (4, 3, 75, 3)
    assert (snap["types_passed"], snap["types_total"], snap["sections_completed"]) == (3, 4, 1)
    assert snap["current_section"] == "s2" and snap["completed"] is False
    statuses = crr.type_statuses(verdicts)
    assert crr.section_statuses(statuses, "s2", ["c", "d"]) == {"c": ptr.STATUS_PASSED, "d": ptr.STATUS_UNSEEN}


def test_teacher_stats_include_chapter_review_and_count_first_verdict(app):
    from datetime import datetime, timedelta

    from core.teacher_analysis_service import (
        TimeRange,
        _aggregate_practice_by_skill,
        _aggregate_practice_by_student,
    )
    from models import PracticeAttempt, db

    uid = _new_student(app)
    t0 = datetime(2026, 9, 1, 8, 0, 0)
    rows = [
        ("g1", "general_practice", None, False),
        ("g1", "general_practice", None, True),
        ("c1", "chapter_review", "cr_x", True),
        ("c2", "chapter_review", "cr_x", False),
        ("c2", "chapter_review", "cr_x", False),
        (None, "general_practice", None, True),
    ]
    with app.app_context():
        for i, (qid, source, run, ok) in enumerate(rows):
            db.session.add(PracticeAttempt(
                student_id=uid, skill_id=SECTION_A, question_uid=qid, is_correct=ok,
                source=source, session_id=run, created_at=t0 + timedelta(minutes=i),
            ))
        db.session.commit()
        everything = TimeRange(key="all", start=None, end=None)
        by_student = _aggregate_practice_by_student([uid], everything)[uid]
        by_skill = _aggregate_practice_by_skill(uid, everything)[SECTION_A]
    for stats in (by_student, by_skill):
        assert (stats.total, stats.correct) == (4, 2)
        assert stats.last_activity == t0 + timedelta(minutes=5)
