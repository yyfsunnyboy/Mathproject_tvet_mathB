# -*- coding: utf-8 -*-
"""Phase 4F-Main-D: real smoke + session_engine B4 retry alignment."""

from __future__ import annotations

import uuid

from app import create_app
from core.adaptive.schema import CatalogEntry
from core.adaptive.session_engine import submit_and_get_next
from models import User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _make_user() -> User:
    user = User(
        username=f"pf4f_main_d_{uuid.uuid4().hex[:10]}",
        password_hash="test-hash",
        role="student",
    )
    db.session.add(user)
    db.session.commit()
    return user


def _entry(skill_id: str, family_id: str, family_name: str, node: str) -> CatalogEntry:
    return CatalogEntry(
        skill_id=skill_id,
        skill_name=skill_id,
        family_id=family_id,
        family_name=family_name,
        theme="counting",
        subskill_nodes=[node],
        notes="",
    )


def test_main_d_real_app_smoke_b4_route_not_blocked_by_empty_db_and_submit_answer(monkeypatch) -> None:
    monkeypatch.setattr("core.routes.practice.recommend_question", lambda _u, _s: None)

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    with client.session_transaction() as sess:
        sess["review_skill_pool"] = ["vh_數學B4_CombinationDefinition"]

    resp = client.get(
        "/get_adaptive_question?mode=review&curriculum=vocational&gen_seed=808&adaptive_audit=1"
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["skill_id"] == "vh_數學B4_CombinationDefinition"
    assert body["adaptive_audit"]["source_type"] == "generator_first"
    assert body["new_question_text"]
    assert body.get("correct_answer") is not None

    chk = client.post(
        "/check_answer",
        json={
            "answer": str(body["correct_answer"]),
            "mode": "adaptive",
            "question_id": body["question_id"],
        },
    )
    assert chk.status_code == 200
    assert chk.get_json().get("correct") is True


def test_main_d_frontend_route_smoke_pages_and_adaptive_endpoint(monkeypatch) -> None:
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)

    page_resp = client.get(
        "/adaptive_practice?mode=review&curriculum=vocational&skill_id=vh_數學B4_CombinationDefinition"
    )
    assert page_resp.status_code == 200

    api_resp = client.post(
        "/api/adaptive/submit_and_get_next",
        json={"step_number": 0, "skill_id": "jh_數學1上_FourArithmeticOperationsOfIntegers"},
    )
    assert api_resp.status_code == 200
    payload = api_resp.get_json()
    assert payload.get("new_question_data", {}).get("skill_id") == "jh_數學1上_FourArithmeticOperationsOfIntegers"


def test_main_d_retry_first_b4_rejected_second_b4_succeeds(monkeypatch) -> None:
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine.choose_next_family",
        lambda **kwargs: kwargs["entries"][0],
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine.load_catalog",
        lambda path=None: [
            _entry("vh_數學B4_CombinationDefinition", "B4_F1", "組合定義", "comb_definition"),
            _entry("vh_數學B4_AdditionPrinciple", "B4_F2", "加法原理", "addition_principle"),
        ],
    )

    import skills.vh_數學B4_CombinationDefinition as first_mod

    real_first = first_mod.generate

    def _reject_first(level=1, **kwargs):
        payload = real_first(level=level, **kwargs)
        payload["problem_type_id"] = "tree_diagram_listing"
        return payload

    monkeypatch.setattr(first_mod, "generate", _reject_first)

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        out = submit_and_get_next(
                {"student_id": user.id, "step_number": 0}
        )

    q = out["new_question_data"]
    assert q.get("source") != "catalog_fallback"
    assert q.get("skill_id") == "vh_數學B4_AdditionPrinciple"
    retry_audit = (q.get("adaptive_audit") or {}).get("b4_retry_attempts") or []
    assert len(retry_audit) >= 2
    assert retry_audit[0]["result"] == "rejected"
    assert retry_audit[-1]["result"] == "accepted"


def test_main_d_retry_all_b4_fail_then_catalog_fallback(monkeypatch) -> None:
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine.choose_next_family",
        lambda **kwargs: kwargs["entries"][0],
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine.load_catalog",
        lambda path=None: [
            _entry("vh_數學B4_CombinationDefinition", "B4_F1", "組合定義", "comb_definition"),
            _entry("vh_數學B4_AdditionPrinciple", "B4_F2", "加法原理", "addition_principle"),
        ],
    )

    import skills.vh_數學B4_CombinationDefinition as first_mod
    import skills.vh_數學B4_AdditionPrinciple as second_mod

    real_first = first_mod.generate
    real_second = second_mod.generate

    def _reject_first(level=1, **kwargs):
        payload = real_first(level=level, **kwargs)
        payload["problem_type_id"] = "binomial_expansion_basic"
        return payload

    def _reject_second(level=1, **kwargs):
        payload = real_second(level=level, **kwargs)
        payload["problem_type_id"] = "binomial_expansion_basic"
        return payload

    monkeypatch.setattr(first_mod, "generate", _reject_first)
    monkeypatch.setattr(second_mod, "generate", _reject_second)

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        out = submit_and_get_next(
                {"student_id": user.id, "step_number": 0}
        )

    q = out["new_question_data"]
    assert q.get("source") == "catalog_fallback"
    retry_audit = (q.get("adaptive_audit") or {}).get("b4_retry_attempts") or []
    assert len(retry_audit) >= 2
    assert all(item.get("result") == "rejected" for item in retry_audit)


def test_main_d_non_b4_behavior_unchanged_without_retry_marker() -> None:
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        out = submit_and_get_next(
            {
                "student_id": user.id,
                "step_number": 0,
                "skill_id": "jh_數學1上_FourArithmeticOperationsOfIntegers",
            }
        )

    q = out["new_question_data"]
    audit = q.get("adaptive_audit") or {}
    assert q.get("skill_id") == "jh_數學1上_FourArithmeticOperationsOfIntegers"
    assert "b4_retry_attempts" not in audit
