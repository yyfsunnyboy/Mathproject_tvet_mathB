# -*- coding: utf-8 -*-
"""Phase 5B-Fix-A: B4 chapter adaptive entry bridge smoke tests."""

from __future__ import annotations

import uuid

from app import create_app
from core.adaptive.session_engine import CatalogEntry, submit_and_get_next
from core.routes.practice import _resolve_b4_chapter_adaptive_entry
from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
    B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
    B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES,
    starter_b4_candidates,
)
from models import User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _make_user() -> User:
    user = User(
        username=f"pf5b_fix_a_{uuid.uuid4().hex[:10]}",
        password_hash="test-hash",
        role="student",
    )
    db.session.add(user)
    db.session.commit()
    return user


def _entry(skill_id: str, family_id: str, family_name: str) -> CatalogEntry:
    return CatalogEntry(
        skill_id=skill_id,
        skill_name=skill_id,
        family_id=family_id,
        family_name=family_name,
        theme="phase5b_fix_a",
        subskill_nodes=["starter_node"],
        notes="phase5b_fix_a test entry",
    )


def test_dashboard_b4_chapter_card_uses_chapter_mode_link() -> None:
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    resp = client.get("/dashboard?view=curriculum&curriculum=vocational&volume=數學B4")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "/adaptive_practice?mode=chapter&amp;curriculum=vocational&amp;volume=%E6%95%B8%E5%AD%B8B4&amp;chapter_id=1" in body


def test_chapter_resolver_returns_allowlist_pool() -> None:
    resolved, hit = _resolve_b4_chapter_adaptive_entry(
        mode="chapter",
        curriculum="vocational",
        volume="數學B4",
        chapter_id="1",
        skill_ids="",
    )
    assert hit is True
    unit_skill_ids = resolved.get("unit_skill_ids") or []
    assert set(unit_skill_ids) == set(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST)
    assert (resolved.get("starter_skill_id") or "") in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST


def test_chapter_mode_payload_can_bootstrap_without_400_and_returns_allowlisted_skill(monkeypatch) -> None:
    starter_pool = starter_b4_candidates(sorted(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST))
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
            _entry("vh_數學B4_AdditionPrinciple", "B4_F1", "加法原理"),
            _entry("vh_數學B4_MultiplicationPrinciple", "B4_F2", "乘法原理"),
            _entry("vh_數學B4_FactorialNotation", "B4_F3", "階乘記號"),
        ],
    )
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    resp = client.post(
        "/api/adaptive/submit_and_get_next",
        json={
            "step_number": 0,
            "mode": "teaching",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "1",
            "skill_id": starter_pool[0],
            "starter_skill_id": starter_pool[0],
            "target_skill_ids": starter_pool,
            "skill_ids": starter_pool,
            "unit_skill_ids": sorted(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST),
            "learning_mode": "main",
        },
    )
    assert resp.status_code == 200
    body = resp.get_json()
    sid = body.get("new_question_data", {}).get("skill_id")
    assert sid in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST


def test_excluded_problem_type_remains_blocked_in_chapter_bridge_bootstrap(monkeypatch) -> None:
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
            _entry("vh_數學B4_AdditionPrinciple", "B4_F1", "加法原理"),
        ],
    )
    import skills.vh_數學B4_AdditionPrinciple as add_mod

    real = add_mod.generate

    def _bad(level=1, **kwargs):
        payload = real(level=level, **kwargs)
        payload["problem_type_id"] = "tree_diagram_listing"
        return payload

    monkeypatch.setattr(add_mod, "generate", _bad)
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    with app.app_context():
        body = submit_and_get_next(
            {
                "student_id": uid,
                "step_number": 0,
                "mode": "chapter",
                "curriculum": "vocational",
                "volume": "數學B4",
                "chapter_id": "1",
                "skill_id": "vh_數學B4_AdditionPrinciple",
                "unit_skill_ids": ["vh_數學B4_AdditionPrinciple"],
            }
        )
    pid = body.get("new_question_data", {}).get("problem_type_id")
    assert pid not in B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES


def test_legacy_single_skill_ids_chapter_label_is_bridged() -> None:
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    resp = client.get("/adaptive_practice?mode=single&skill_ids=1+排列組合")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'const adaptiveEntryMode = "chapter";' in body
    assert 'const chapterBridgeCompatUsed = true;' in body
    assert "const bootstrapUnitSkillIds = " in body
    assert "const starterSkillId = " in body


def test_non_b4_entry_behavior_unchanged() -> None:
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    page = client.get("/adaptive_practice?mode=single&skill_ids=整數四則運算")
    assert page.status_code == 200
    body = page.get_data(as_text=True)
    assert 'const adaptiveEntryMode = "single";' in body
    assert "const unitSkillIds = [];" in body


def test_fix_c_b4_chapter_bootstrap_with_empty_catalog_uses_synthetic_entries(monkeypatch) -> None:
    monkeypatch.setattr("core.adaptive.session_engine.load_catalog", lambda path=None: [])
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    starter_pool = starter_b4_candidates(sorted(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST))
    resp = client.post(
        "/api/adaptive/submit_and_get_next",
        json={
            "step_number": 0,
            "mode": "teaching",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "1",
            "skill_id": starter_pool[0],
            "starter_skill_id": starter_pool[0],
            "target_skill_ids": starter_pool,
            "skill_ids": starter_pool,
            "unit_skill_ids": sorted(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST),
            "learning_mode": "main",
        },
    )
    assert resp.status_code == 200
    body = resp.get_json()
    q = body.get("new_question_data", {})
    assert q.get("skill_id") in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST
    assert str(q.get("source") or "") != "catalog_fallback"


def test_fix_c_synthetic_catalog_only_uses_allowlisted_b4_skills(monkeypatch) -> None:
    monkeypatch.setattr("core.adaptive.session_engine.load_catalog", lambda path=None: [])
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id
        body = submit_and_get_next(
            {
                "student_id": uid,
                "step_number": 0,
                "mode": "teaching",
                "entry_mode": "chapter",
                "curriculum": "vocational",
                "volume": "數學B4",
                "chapter_id": "1",
                "skill_id": "vh_數學B4_AdditionPrinciple",
                "target_skill_ids": [
                    "vh_數學B4_AdditionPrinciple",
                    "vh_數學B4_TreeDiagramCounting",
                    "not_existing_skill",
                ],
                "skill_ids": [
                    "vh_數學B4_AdditionPrinciple",
                    "vh_數學B4_TreeDiagramCounting",
                    "not_existing_skill",
                ],
                "unit_skill_ids": [
                    "vh_數學B4_AdditionPrinciple",
                    "vh_數學B4_TreeDiagramCounting",
                    "not_existing_skill",
                ],
            }
        )
    q = body.get("new_question_data", {})
    assert q.get("skill_id") == "vh_數學B4_AdditionPrinciple"


def test_fix_c_non_b4_empty_catalog_keeps_existing_error(monkeypatch) -> None:
    monkeypatch.setattr("core.adaptive.session_engine.load_catalog", lambda path=None: [])
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    resp = client.post(
        "/api/adaptive/submit_and_get_next",
        json={
            "step_number": 0,
            "mode": "teaching",
            "skill_id": "jh_數學1上_FourArithmeticOperationsOfIntegers",
            "unit_skill_ids": ["jh_數學1上_FourArithmeticOperationsOfIntegers"],
        },
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert "No catalog entries available for the requested adaptive scope" in str(body.get("error") or "")
