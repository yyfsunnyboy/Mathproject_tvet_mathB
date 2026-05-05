# -*- coding: utf-8 -*-
"""Phase 4F-Main-C: adaptive v2 / session_engine B4 Chapter 1 allowlist unification."""

from __future__ import annotations

import uuid

import pytest

from app import create_app
from core.adaptive.schema import CatalogEntry
from core.adaptive.session_engine import (
    _b4_session_engine_payload_gate,
    submit_and_get_next,
)
from core.vocational_math_b4.adaptive import b4_chapter1_deterministic_allowlist as allow
from models import User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _make_user() -> User:
    user = User(
        username=f"pf4f_main_c_{uuid.uuid4().hex[:10]}",
        password_hash="test-hash",
        role="student",
    )
    db.session.add(user)
    db.session.commit()
    return user


def _sample_b4_catalog_combo() -> list[CatalogEntry]:
    return [
        CatalogEntry(
            skill_id="vh_數學B4_CombinationDefinition",
            skill_name="組合",
            family_id="B4_MC_Test",
            family_name="組合定義",
            theme="counting",
            subskill_nodes=["b4_ch1_comb_def_01"],
            notes="",
        )
    ]


def test_filter_catalog_entries_skips_disallowed_b4() -> None:
    mixed = [
        CatalogEntry(
            skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers",
            skill_name="整數",
            family_id="I1",
            family_name="整數",
            theme="arith",
            subskill_nodes=["sign_handling"],
            notes="",
        ),
        CatalogEntry(
            skill_id="vh_數學B4_NotOnChapter1AllowlistFake",
            skill_name="假技能",
            family_id="X1",
            family_name="假",
            theme="counting",
            subskill_nodes=["x"],
            notes="",
        ),
        *_sample_b4_catalog_combo(),
    ]
    out, audits = allow.filter_catalog_entries_for_b4_chapter1_deterministic_adaptive(mixed)
    skill_ids = {e.skill_id for e in out}
    assert "jh_數學1上_FourArithmeticOperationsOfIntegers" in skill_ids
    assert "vh_數學B4_CombinationDefinition" in skill_ids
    assert "vh_數學B4_NotOnChapter1AllowlistFake" not in skill_ids
    assert any(a["skill_id"] == "vh_數學B4_NotOnChapter1AllowlistFake" for a in audits)


def test_session_engine_gate_non_b4_always_passes() -> None:
    entry = CatalogEntry(
        skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers",
        skill_name="整數",
        family_id="I1",
        family_name="整數",
        theme="arith",
        subskill_nodes=["sign_handling"],
        notes="",
    )
    cand = {
        "question_text": "Q",
        "correct_answer": "1",
        "source": "skill_module",
    }
    ok, _reason = _b4_session_engine_payload_gate(entry, cand)
    assert ok is True


def test_session_engine_gate_blocks_excluded_problem_type() -> None:
    entry = _sample_b4_catalog_combo()[0]
    cand = {
        "question_text": "Q",
        "correct_answer": "1",
        "problem_type_id": "binomial_expansion_basic",
        "source": "skill_module",
    }
    ok, reason = _b4_session_engine_payload_gate(entry, cand)
    assert ok is False
    assert reason is not None


@pytest.fixture()
def combo_catalog(monkeypatch) -> None:
    monkeypatch.setattr(
        "core.adaptive.session_engine.load_catalog",
        lambda path=None: _sample_b4_catalog_combo(),
    )


def test_submit_and_get_next_b4_allowlisted_returns_deterministic_payload(monkeypatch, combo_catalog) -> None:
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

        out = submit_and_get_next(
            {"student_id": uid, "step_number": 0, "skill_id": "vh_數學B4_CombinationDefinition"}
        )
        q = out["new_question_data"]
        assert q.get("skill_id") == "vh_數學B4_CombinationDefinition"
        assert q.get("problem_type_id") == "combination_definition_basic"
        audit = q.get("adaptive_audit")
        assert isinstance(audit, dict)
        assert audit.get("source_type", "").startswith("session_engine_")
        assert audit.get("generator_key")
        assert out.get("b4_deterministic_catalog_audit") == []


def test_submit_and_get_next_rejects_excluded_problem_type_via_fallback(monkeypatch, combo_catalog) -> None:
    import skills.vh_數學B4_CombinationDefinition as combo_mod

    real = combo_mod.generate

    def evil_generate(level=1, **kwargs):
        p = real(level=level, **kwargs)
        p["problem_type_id"] = "tree_diagram_listing"
        return p

    monkeypatch.setattr(combo_mod, "generate", evil_generate)

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

        out = submit_and_get_next(
            {"student_id": uid, "step_number": 0, "skill_id": "vh_數學B4_CombinationDefinition"}
        )
        q = out["new_question_data"]
        pid = q.get("problem_type_id")
        assert pid not in allow.B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES
        assert pid is None or pid != "tree_diagram_listing"
        assert q.get("source") == "catalog_fallback"


def test_submit_and_get_next_empty_catalog_when_only_disallowed_b4(monkeypatch) -> None:
    bad_only = [
        CatalogEntry(
            skill_id="vh_數學B4_NotOnChapter1AllowlistFake",
            skill_name="假",
            family_id="X1",
            family_name="假",
            theme="counting",
            subskill_nodes=["x"],
            notes="",
        ),
    ]
    monkeypatch.setattr("core.adaptive.session_engine.load_catalog", lambda path=None: bad_only)

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    with pytest.raises(ValueError, match="No catalog entries"):
        submit_and_get_next(
            {"student_id": uid, "step_number": 0, "skill_id": "vh_數學B4_NotOnChapter1AllowlistFake"}
        )


def test_api_submit_bootstrap_non_b4_unchanged(monkeypatch) -> None:
    """Regression: default catalog integer skill path still returns 200."""
    monkeypatch.delenv("ADAPTIVE_USE_FULL_CATALOG", raising=False)

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    resp = client.post(
        "/api/adaptive/submit_and_get_next",
        json={"step_number": 0, "skill_id": "jh_數學1上_FourArithmeticOperationsOfIntegers"},
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["new_question_data"]["skill_id"] == "jh_數學1上_FourArithmeticOperationsOfIntegers"
