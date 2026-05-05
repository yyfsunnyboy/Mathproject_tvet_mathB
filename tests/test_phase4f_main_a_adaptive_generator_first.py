# -*- coding: utf-8 -*-
"""Phase 4F-Main-A: B4 adaptive generator-first alignment (practice.get_adaptive_question)."""

from __future__ import annotations

import uuid

from app import create_app
from core.vocational_math_b4.services.question_router import generate_for_skill
from models import User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _make_user() -> User:
    user = User(
        username=f"pf4f_main_a_{uuid.uuid4().hex[:10]}",
        password_hash="test-hash",
        role="student",
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_pure_b4_pool_skips_db_recommend_and_returns_generator_first(monkeypatch) -> None:
    calls = {"recommend": 0}

    def _fake_recommend(_uid, _sids):
        calls["recommend"] += 1
        return None

    monkeypatch.setattr("core.routes.practice.recommend_question", _fake_recommend)

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
        "/get_adaptive_question?mode=review&curriculum=vocational&gen_seed=11&adaptive_audit=1"
    )
    assert resp.status_code == 200
    assert calls["recommend"] == 0
    body = resp.get_json()
    assert body["skill_id"] == "vh_數學B4_CombinationDefinition"
    assert body["question_id"] == 0
    assert body["adaptive_audit"]["source_type"] == "generator_first"
    assert body["adaptive_audit"]["problem_type_id"] == "combination_definition_basic"


def test_mixed_pool_empty_db_uses_generator_fallback(monkeypatch) -> None:
    monkeypatch.setattr("core.routes.practice.recommend_question", lambda _u, _s: None)
    monkeypatch.setattr(
        "core.adaptive_engine.select_review_skill",
        lambda pool, stats, last_skill: "jh_數學1上_FourArithmeticOperationsOfIntegers",
    )

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    with client.session_transaction() as sess:
        sess["review_skill_pool"] = [
            "jh_數學1上_FourArithmeticOperationsOfIntegers",
            "vh_數學B4_CombinationDefinition",
        ]

    resp = client.get(
        "/get_adaptive_question?mode=review&curriculum=vocational&gen_seed=3&adaptive_audit=1"
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["skill_id"] == "vh_數學B4_CombinationDefinition"
    assert body["question_id"] == 0
    assert body["adaptive_audit"]["source_type"] == "generator_fallback"


def test_non_b4_only_empty_db_still_404(monkeypatch) -> None:
    monkeypatch.setattr("core.routes.practice.recommend_question", lambda _u, _s: None)

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    with client.session_transaction() as sess:
        sess["review_skill_pool"] = ["jh_數學1上_FourArithmeticOperationsOfIntegers"]

    resp = client.get("/get_adaptive_question?mode=review&curriculum=vocational")
    assert resp.status_code == 404


def test_rejected_excluded_problem_type_returns_422_with_audit(monkeypatch) -> None:
    class _FakeMod:
        @staticmethod
        def generate(level=1, **kwargs):
            payload = generate_for_skill(
                skill_id="vh_數學B4_BinomialTheorem",
                level=level,
                seed=kwargs.get("seed") or 1,
                problem_type_id="binomial_specific_term_coefficient",
            )
            payload["problem_type_id"] = "binomial_expansion_basic"
            return payload

    monkeypatch.setattr("core.routes.practice.recommend_question", lambda _u, _s: None)
    monkeypatch.setattr("core.routes.practice.get_skill", lambda _sid: _FakeMod())

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    with client.session_transaction() as sess:
        sess["review_skill_pool"] = ["vh_數學B4_BinomialTheorem"]

    resp = client.get(
        "/get_adaptive_question?mode=review&curriculum=vocational&adaptive_audit=1"
    )
    assert resp.status_code == 422
    body = resp.get_json()
    assert body["adaptive_audit"]["source_type"] == "rejected_excluded_problem_type"
    assert "excluded_problem_type" in (body.get("detail") or "")


def test_db_path_marks_db_textbook_example(monkeypatch) -> None:
    class _TQ:
        id = 4242
        skill_id = "jh_數學1上_FourArithmeticOperationsOfIntegers"
        difficulty_level = 2

    monkeypatch.setattr(
        "core.routes.practice.recommend_question",
        lambda _u, _s: _TQ(),
    )
    monkeypatch.setattr(
        "core.adaptive_engine.select_review_skill",
        lambda pool, stats, last_skill: "jh_數學1上_FourArithmeticOperationsOfIntegers",
    )

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    with client.session_transaction() as sess:
        sess["review_skill_pool"] = [
            "jh_數學1上_FourArithmeticOperationsOfIntegers",
            "vh_數學B4_CombinationDefinition",
        ]

    resp = client.get(
        "/get_adaptive_question?mode=review&curriculum=vocational&adaptive_audit=1"
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["question_id"] == 4242
    assert body["skill_id"] == "jh_數學1上_FourArithmeticOperationsOfIntegers"
    assert body["adaptive_audit"]["source_type"] == "db_textbook_example"
    assert body["new_question_text"] is not None
