# -*- coding: utf-8 -*-
"""Phase 5H: AI-judged free-response adaptive candidate registration tests."""

from __future__ import annotations

import uuid

from app import create_app
from core.vocational_math_b4.adaptive import b4_chapter1_deterministic_allowlist as allow
from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
    B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
    B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILLS,
    B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER,
    B4_CHAPTER_1_CURRICULUM_PROGRESSION_WITH_FREE_RESPONSE,
    get_b4_chapter1_ai_judged_free_response_metadata,
    get_b4_chapter1_curriculum_progression,
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
            username=f"pf5h_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def test_ai_judged_candidate_list_contains_exact_two_skills() -> None:
    assert tuple(B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILLS) == (
        "vh_數學B4_TreeDiagramCounting",
        "vh_數學B4_PascalTriangle",
    )


def test_ai_judged_skills_are_not_in_deterministic_allowlist() -> None:
    for sid in B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILLS:
        assert sid not in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST


def test_ai_judged_metadata_correctness() -> None:
    tree = get_b4_chapter1_ai_judged_free_response_metadata("vh_數學B4_TreeDiagramCounting")
    pascal = get_b4_chapter1_ai_judged_free_response_metadata("vh_數學B4_PascalTriangle")

    assert tree is not None
    assert tree["problem_type_id"] == "tree_diagram_listing"
    assert tree["answer_type"] == "handwriting"
    assert tree["grading_mode"] == "ai_judged_free_response"
    assert tree["index_param"] == "tree_diagram_index"

    assert pascal is not None
    assert pascal["problem_type_id"] == "pascal_triangle_handwriting"
    assert pascal["answer_type"] == "handwriting"
    assert pascal["grading_mode"] == "ai_judged_free_response"
    assert pascal["index_param"] == "pascal_triangle_index"


def test_progression_with_free_response_has_expected_checkpoint_order() -> None:
    seq = list(B4_CHAPTER_1_CURRICULUM_PROGRESSION_WITH_FREE_RESPONSE)
    assert seq.index("vh_數學B4_MultiplicationPrinciple") < seq.index("vh_數學B4_TreeDiagramCounting")
    assert seq.index("vh_數學B4_BinomialCoefficientIdentities") < seq.index("vh_數學B4_PascalTriangle")
    assert seq.index("vh_數學B4_PascalTriangle") < seq.index("vh_數學B4_BinomialTheorem")


def test_default_progression_remains_deterministic_unchanged() -> None:
    assert get_b4_chapter1_curriculum_progression(include_free_response=False) == list(
        B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER
    )
    assert "vh_數學B4_TreeDiagramCounting" not in B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER
    assert "vh_數學B4_PascalTriangle" not in B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER


def test_progression_helper_prefers_db_order_when_available(monkeypatch) -> None:
    db_order = [
        "vh_數學B4_AdditionPrinciple",
        "vh_數學B4_MultiplicationPrinciple",
        "vh_數學B4_TreeDiagramCounting",
        "vh_數學B4_FactorialNotation",
        "vh_數學B4_BinomialCoefficientIdentities",
        "vh_數學B4_PascalTriangle",
        "vh_數學B4_BinomialTheorem",
    ]
    monkeypatch.setattr(allow, "_fetch_b4_chapter1_db_order_skill_ids", lambda: db_order)
    out = allow.get_b4_chapter1_curriculum_progression_from_db_or_fallback(include_free_response=True)
    assert out == db_order


def test_progression_helper_falls_back_when_db_order_missing(monkeypatch) -> None:
    monkeypatch.setattr(allow, "_fetch_b4_chapter1_db_order_skill_ids", lambda: [])
    out = allow.get_b4_chapter1_curriculum_progression_from_db_or_fallback(include_free_response=True)
    assert out[0] == "vh_數學B4_AdditionPrinciple"
    assert "vh_數學B4_TreeDiagramCounting" in out
    assert "vh_數學B4_PascalTriangle" in out


def test_progression_helper_include_flag_controls_free_response(monkeypatch) -> None:
    db_order = [
        "vh_數學B4_AdditionPrinciple",
        "vh_數學B4_TreeDiagramCounting",
        "vh_數學B4_MultiplicationPrinciple",
        "vh_數學B4_BinomialCoefficientIdentities",
        "vh_數學B4_PascalTriangle",
        "vh_數學B4_BinomialTheorem",
    ]
    monkeypatch.setattr(allow, "_fetch_b4_chapter1_db_order_skill_ids", lambda: db_order)
    no_fr = allow.get_b4_chapter1_curriculum_progression_from_db_or_fallback(include_free_response=False)
    with_fr = allow.get_b4_chapter1_curriculum_progression_from_db_or_fallback(include_free_response=True)
    assert "vh_數學B4_TreeDiagramCounting" not in no_fr
    assert "vh_數學B4_PascalTriangle" not in no_fr
    assert "vh_數學B4_TreeDiagramCounting" in with_fr
    assert "vh_數學B4_PascalTriangle" in with_fr


def test_dashboard_links_use_practice_handwriting_entries() -> None:
    client = _make_client()
    resp = client.get("/dashboard?view=curriculum&curriculum=vocational&volume=數學B4&chapter=1+排列組合")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "/practice?skill=vh_" in body
    assert "problem_type=tree_diagram_listing" in body
    assert "problem_type=pascal_triangle_handwriting" in body
    assert "grading_mode=ai_judged_free_response" in body
    assert "/free_response_practice" not in body


def test_practice_flow_smoke_tree_and_pascal_handwriting() -> None:
    client = _make_client()
    tree_resp = client.get(
        "/get_next_question?skill=vh_數學B4_TreeDiagramCounting&problem_type=tree_diagram_listing&tree_diagram_index=0"
    )
    pascal_resp = client.get(
        "/get_next_question?skill=vh_數學B4_PascalTriangle&problem_type=pascal_triangle_handwriting&pascal_triangle_index=0"
    )
    assert tree_resp.status_code == 200
    assert pascal_resp.status_code == 200
    tree_body = tree_resp.get_json()
    pascal_body = pascal_resp.get_json()
    assert tree_body["answer_type"] == "handwriting"
    assert tree_body["grading_mode"] == "ai_judged_free_response"
    assert pascal_body["answer_type"] == "handwriting"
    assert pascal_body["grading_mode"] == "ai_judged_free_response"
