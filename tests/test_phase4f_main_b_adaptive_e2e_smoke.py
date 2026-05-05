# -*- coding: utf-8 -*-
"""Phase 4F-Main-B: B4 Chapter 1 adaptive E2E smoke (single/multiple/review + check_answer)."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app import create_app
from core.vocational_math_b4.services.question_router import generate_for_skill
from models import SkillCurriculum, User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _make_user() -> User:
    user = User(
        username=f"pf4f_main_b_{uuid.uuid4().hex[:10]}",
        password_hash="test-hash",
        role="student",
    )
    db.session.add(user)
    db.session.commit()
    return user


def _patch_skill_curriculum_query(monkeypatch, skill_ids: list[str]) -> None:
    """Stub chapter→skills resolution for mode=single/multiple."""

    import core.routes.practice as pm

    orig_query = pm.db.session.query

    class _Row:
        __slots__ = ("skill_id",)

        def __init__(self, sid: str) -> None:
            self.skill_id = sid

    rows = [_Row(sid) for sid in skill_ids]

    def _is_skill_curriculum_query(first_arg: object) -> bool:
        if first_arg is SkillCurriculum:
            return True
        cls = getattr(first_arg, "class_", None)
        return cls is SkillCurriculum

    def _query(first_arg, *args, **kwargs):
        if _is_skill_curriculum_query(first_arg):
            q = MagicMock()
            q.filter.return_value.distinct.return_value.all.return_value = rows
            return q
        return orig_query(first_arg, *args, **kwargs)

    monkeypatch.setattr(pm.db.session, "query", _query)


def test_e2e_single_allowlisted_b4_audit_and_check_answer(monkeypatch) -> None:
    monkeypatch.setattr("core.routes.practice.recommend_question", lambda _u, _s: None)
    _patch_skill_curriculum_query(
        monkeypatch,
        ["vh_數學B4_CombinationDefinition"],
    )

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)

    resp = client.get(
        "/get_adaptive_question?mode=single&skill_ids=B4_Ch1_Smoke_Single"
        "&gen_seed=101&adaptive_audit=1"
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["skill_id"] == "vh_數學B4_CombinationDefinition"
    assert body["new_question_text"]
    assert body.get("correct_answer") is not None
    audit = body["adaptive_audit"]
    assert audit["source_type"] == "generator_first"
    for key in ("skill_id", "problem_type_id", "generator_key", "router_trace", "source_type"):
        assert key in audit
    assert isinstance(audit.get("router_trace"), dict)

    chk = client.post(
        "/check_answer",
        json={
            "answer": str(body["correct_answer"]),
            "mode": "adaptive",
            "question_id": body["question_id"],
        },
    )
    assert chk.status_code == 200
    chk_body = chk.get_json()
    assert chk_body.get("correct") is True


def test_e2e_multiple_b4_only_empty_db_generator_first(monkeypatch) -> None:
    monkeypatch.setattr("core.routes.practice.recommend_question", lambda _u, _s: None)
    _patch_skill_curriculum_query(
        monkeypatch,
        [
            "vh_數學B4_CombinationDefinition",
            "vh_數學B4_AdditionPrinciple",
        ],
    )

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)

    resp = client.get(
        "/get_adaptive_question?mode=multiple&skill_ids=ChA,ChB"
        "&gen_seed=202&adaptive_audit=1"
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["skill_id"] in (
        "vh_數學B4_CombinationDefinition",
        "vh_數學B4_AdditionPrinciple",
    )
    assert body["adaptive_audit"]["source_type"] == "generator_first"


def test_e2e_review_b4_only_multi_skill_pool_generator_first(monkeypatch) -> None:
    calls = {"recommend": 0}

    def _no_db(_uid, _sids):
        calls["recommend"] += 1
        return None

    monkeypatch.setattr("core.routes.practice.recommend_question", _no_db)

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    with client.session_transaction() as sess:
        sess["review_skill_pool"] = [
            "vh_數學B4_MultiplicationPrinciple",
            "vh_數學B4_FactorialNotation",
        ]

    resp = client.get(
        "/get_adaptive_question?mode=review&curriculum=vocational"
        "&gen_seed=303&adaptive_audit=1"
    )
    assert resp.status_code == 200
    assert calls["recommend"] == 0
    body = resp.get_json()
    assert body["adaptive_audit"]["source_type"] == "generator_first"
    assert body["skill_id"] in (
        "vh_數學B4_MultiplicationPrinciple",
        "vh_數學B4_FactorialNotation",
    )


def test_e2e_review_mixed_jh_b4_empty_db_generator_fallback(monkeypatch) -> None:
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
        "/get_adaptive_question?mode=review&curriculum=vocational"
        "&gen_seed=404&adaptive_audit=1"
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["skill_id"] == "vh_數學B4_CombinationDefinition"
    audit = body["adaptive_audit"]
    assert audit["source_type"] == "generator_fallback"
    assert audit["skill_id"] == body["skill_id"]
    assert audit.get("problem_type_id")
    assert audit.get("generator_key")


def test_e2e_non_b4_only_empty_db_still_404(monkeypatch) -> None:
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


@pytest.mark.parametrize(
    "inject_problem_type_id,base_skill_id",
    [
        ("binomial_expansion_basic", "vh_數學B4_BinomialTheorem"),
        ("tree_diagram_listing", "vh_數學B4_AdditionPrinciple"),
        ("pascal_triangle_derivation", "vh_數學B4_BinomialCoefficientIdentities"),
    ],
)
def test_e2e_excluded_problem_type_not_returned_to_student(
    monkeypatch,
    inject_problem_type_id: str,
    base_skill_id: str,
) -> None:
    """Force excluded problem_type_id post-generation; expect 422 and no playable payload."""

    class _FakeMod:
        @staticmethod
        def generate(level=1, **kwargs):
            payload = generate_for_skill(
                skill_id=base_skill_id,
                level=level,
                seed=kwargs.get("seed") or 1,
            )
            payload["problem_type_id"] = inject_problem_type_id
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
        sess["review_skill_pool"] = [base_skill_id]

    resp = client.get(
        "/get_adaptive_question?mode=review&curriculum=vocational&adaptive_audit=1"
    )
    assert resp.status_code == 422
    body = resp.get_json()
    assert body.get("adaptive_audit", {}).get("source_type") == "rejected_excluded_problem_type"
    assert body.get("new_question_text") is None
    assert body.get("correct_answer") is None


def test_e2e_single_mixed_pool_jh_and_b4_prefers_db_then_generator_fallback(monkeypatch) -> None:
    """single/multiple: DB empty but pool lists JH+B4 → generator_fallback from allowlisted B4."""

    monkeypatch.setattr("core.routes.practice.recommend_question", lambda _u, _s: None)
    _patch_skill_curriculum_query(
        monkeypatch,
        [
            "jh_數學1上_FourArithmeticOperationsOfIntegers",
            "vh_數學B4_CombinationDefinition",
        ],
    )

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)

    resp = client.get(
        "/get_adaptive_question?mode=single&skill_ids=MixedSmoke"
        "&gen_seed=505&adaptive_audit=1"
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["skill_id"] == "vh_數學B4_CombinationDefinition"
    assert body["adaptive_audit"]["source_type"] == "generator_fallback"
