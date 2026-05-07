# -*- coding: utf-8 -*-
"""Phase 5H-C: expose AI-judged free-response checkpoints in B4 adaptive audit."""

from __future__ import annotations

import uuid

from app import create_app
from core.adaptive.session_engine import CatalogEntry
from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
    B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
    build_b4_chapter1_ai_judged_free_response_audit,
)
from models import User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _make_user() -> User:
    user = User(
        username=f"pf5h_c_{uuid.uuid4().hex[:10]}",
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
        theme="phase5h_c",
        subskill_nodes=["phase5h_c_node"],
        notes="phase5h_c test entry",
    )


def test_build_b4_chapter1_ai_judged_free_response_audit_schema_and_policies() -> None:
    audit = build_b4_chapter1_ai_judged_free_response_audit()
    assert audit["enabled"] is True
    assert audit["scoring_policy"] == "visibility_only_not_mastery_scored"
    assert audit["adaptive_insertion_policy"] == "registered_checkpoint_not_auto_scored"
    assert audit["scope"] == {
        "curriculum": "vocational",
        "volume": "數學B4",
        "chapter_id": "1",
        "chapter_name": "1 排列組合",
    }


def test_build_b4_chapter1_ai_judged_free_response_audit_checkpoints_exact_and_safe() -> None:
    checkpoints = build_b4_chapter1_ai_judged_free_response_audit()["checkpoints"]
    skill_ids = [item["skill_id"] for item in checkpoints]
    assert skill_ids == [
        "vh_數學B4_TreeDiagramCounting",
        "vh_數學B4_PascalTriangle",
    ]

    tree = checkpoints[0]
    assert tree["problem_type_id"] == "tree_diagram_listing"
    assert tree["answer_type"] == "handwriting"
    assert tree["grading_mode"] == "ai_judged_free_response"
    assert tree["index_param"] == "tree_diagram_index"
    assert "/practice?" in str(tree["practice_url"])
    assert "/free_response_practice" not in str(tree["practice_url"])

    pascal = checkpoints[1]
    assert pascal["problem_type_id"] == "pascal_triangle_handwriting"
    assert pascal["answer_type"] == "handwriting"
    assert pascal["grading_mode"] == "ai_judged_free_response"
    assert pascal["index_param"] == "pascal_triangle_index"
    assert "/practice?" in str(pascal["practice_url"])
    assert "/free_response_practice" not in str(pascal["practice_url"])

    blob = str(checkpoints)
    assert "expected_paths" not in blob
    assert "expected_row" not in blob
    assert "expected_terms" not in blob
    assert "expected_expansion" not in blob


def test_b4_chapter_bootstrap_response_contains_ai_judged_free_response_checkpoints(monkeypatch) -> None:
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
            "mode": "chapter",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_name": "1 排列組合（測試）",
            "learning_mode": "teaching",
            "practice_kind": "unit_practice",
            "skill_id": "vh_數學B4_AdditionPrinciple",
            "target_skill_ids": ["vh_數學B4_AdditionPrinciple", "vh_數學B4_MultiplicationPrinciple"],
            "skill_ids": ["vh_數學B4_AdditionPrinciple", "vh_數學B4_MultiplicationPrinciple"],
            "unit_skill_ids": ["vh_數學B4_AdditionPrinciple", "vh_數學B4_MultiplicationPrinciple"],
        },
    )
    assert resp.status_code == 200
    body = resp.get_json()
    adaptive_audit = body.get("adaptive_audit") or {}
    checkpoints_audit = adaptive_audit.get("ai_judged_free_response_checkpoints") or {}
    assert checkpoints_audit.get("enabled") is True
    assert checkpoints_audit.get("scoring_policy") == "visibility_only_not_mastery_scored"
    assert checkpoints_audit.get("adaptive_insertion_policy") == "registered_checkpoint_not_auto_scored"
    assert adaptive_audit.get("free_response_candidate_count") == 2
    assert adaptive_audit.get("free_response_scoring_policy") == "deferred_teacher_review"


def test_non_b4_response_does_not_include_b4_ai_judged_checkpoints(monkeypatch) -> None:
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
            _entry("jh_數學1上_FourArithmeticOperationsOfIntegers", "I1", "整數四則"),
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
            "entry_mode": "single",
            "skill_id": "jh_數學1上_FourArithmeticOperationsOfIntegers",
            "unit_skill_ids": ["jh_數學1上_FourArithmeticOperationsOfIntegers"],
        },
    )
    assert resp.status_code == 200
    body = resp.get_json()
    adaptive_audit = body.get("adaptive_audit") or {}
    assert "ai_judged_free_response_checkpoints" not in adaptive_audit


def test_tree_and_pascal_not_in_deterministic_allowlist() -> None:
    assert "vh_數學B4_TreeDiagramCounting" not in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST
    assert "vh_數學B4_PascalTriangle" not in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST
