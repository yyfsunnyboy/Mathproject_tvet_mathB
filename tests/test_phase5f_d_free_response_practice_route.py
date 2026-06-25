# -*- coding: utf-8 -*-
"""Phase 5F-D: isolated free-response practice route tests."""

from __future__ import annotations

import uuid

from app import create_app
from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
    B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
    B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES,
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
            username=f"pf5f_d_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def test_get_tree_diagram_question_default_does_not_expose_expected_paths() -> None:
    client = _make_client()
    resp = client.get("/api/free_response/tree_diagram/question")
    print(resp.get_json())
    assert resp.status_code == 200
    body = resp.get_json()
    question = body["question"]
    assert body["ok"] is True
    assert question["problem_type_id"] == "tree_diagram_listing"
    assert question["grading_mode"] == "ai_judged_free_response"
    assert question["variant"] == "early_stopping_game"
    assert "expected_paths" not in question


def test_get_tree_diagram_question_fixed_stage_binary_tree() -> None:
    client = _make_client()
    resp = client.get("/api/free_response/tree_diagram/question?variant=fixed_stage_binary_tree")
    print(resp.get_json())
    assert resp.status_code == 200
    question = resp.get_json()["question"]
    assert question["expected_count"] == 8
    assert question["accept_text_listing"] is True
    assert question["accept_handwriting_tree"] is False


def test_submit_correct_early_stopping_game() -> None:
    client = _make_client()
    resp = client.post(
        "/api/free_response/tree_diagram/submit",
        json={
            "variant": "early_stopping_game",
            "answer_text": "甲甲、甲乙甲、甲乙乙、乙甲甲、乙甲乙、乙乙",
            "student_id": None,
            "session_id": None,
            "question_id": None,
        },
    )
    print(resp.get_json())
    assert resp.status_code == 200
    result = resp.get_json()["result"]
    assert result["status"] == "correct"
    assert result["score"] == 1.0


def test_submit_count_only_early_stopping_game_is_partial() -> None:
    client = _make_client()
    resp = client.post(
        "/api/free_response/tree_diagram/submit",
        json={"variant": "early_stopping_game", "answer_text": "6 種"},
    )
    print(resp.get_json())
    assert resp.status_code == 200
    result = resp.get_json()["result"]
    assert result["status"] == "partial"
    assert result["count_only_answer"] is True


def test_submit_fixed_three_round_wrong_is_not_correct() -> None:
    client = _make_client()
    resp = client.post(
        "/api/free_response/tree_diagram/submit",
        json={
            "variant": "early_stopping_game",
            "answer_text": "甲甲甲、甲甲乙、甲乙甲、甲乙乙、乙甲甲、乙甲乙、乙乙甲、乙乙乙",
        },
    )
    print(resp.get_json())
    assert resp.status_code == 200
    result = resp.get_json()["result"]
    assert result["status"] != "correct"
    assert "先贏兩場" in (result["feedback"] + result["main_issue"])


def test_submit_correct_fixed_stage_binary_tree() -> None:
    client = _make_client()
    resp = client.post(
        "/api/free_response/tree_diagram/submit",
        json={
            "variant": "fixed_stage_binary_tree",
            "answer_text": "正正正、正正反、正反正、正反反、反正正、反正反、反反正、反反反",
        },
    )
    print(resp.get_json())
    assert resp.status_code == 200
    assert resp.get_json()["result"]["status"] == "correct"


def test_invalid_variant_returns_400() -> None:
    client = _make_client()
    resp = client.get("/api/free_response/tree_diagram/question?variant=unknown_variant")
    assert resp.status_code == 400
    assert resp.get_json()["ok"] is False


def test_free_response_practice_page_smoke_does_not_expose_expected_paths() -> None:
    client = _make_client()
    resp = client.get(
        "/free_response_practice?curriculum=vocational&volume=數學B4&chapter_id=1&problem_type=tree_diagram_listing&variant=early_stopping_game"
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert '<textarea id="answerText"' in body
    assert "tree_diagram_listing" in body or "樹狀圖" in body
    assert "expected_paths" not in body
    assert "correct_answer" not in body


def test_dashboard_tree_diagram_skill_card_uses_practice_handwriting_entry() -> None:
    client = _make_client()
    resp = client.get(
        "/dashboard?view=curriculum&curriculum=vocational&volume=數學B4&chapter=1+排列組合"
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "樹狀圖" in body
    assert "加法原理" in body
    assert "/free_response_practice" not in body
    assert "/practice?skill=vh_" in body
    assert "TreeDiagramCounting" in body
    assert "problem_type=tree_diagram_listing" in body
    assert "answer_type=handwriting" in body
    assert "grading_mode=ai_judged_free_response" in body
    assert "variant=early_stopping_game" in body


def test_tree_diagram_practice_query_entry_uses_original_practice_page() -> None:
    client = _make_client()
    resp = client.get(
        "/practice?skill=vh_數學B4_TreeDiagramCounting&problem_type=tree_diagram_listing&answer_type=handwriting&grading_mode=ai_judged_free_response&variant=early_stopping_game"
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "scratchpad-container" in body
    assert "analyze_handwriting" in body
    assert "enableHandwritingNextQuestion" in body
    assert "window.currentProblemTypeId === 'tree_diagram_listing'" in body
    assert "event.preventDefault()" in body
    assert "params.set('problem_type', 'tree_diagram_listing')" in body
    assert "params.set('answer_type', currentParams.get('answer_type') || 'handwriting')" in body
    assert "params.set('grading_mode', currentParams.get('grading_mode') || 'ai_judged_free_response')" in body
    assert "let treeDiagramQuestionIndex = 0" in body
    assert "params.set('tree_diagram_index', treeDiagramQuestionIndex)" in body
    assert "treeDiagramQuestionIndex += 1" in body
    assert "nextBtn.dataset.readyForNext = 'true'" in body
    assert "free_response_practice" not in body


def test_tree_diagram_get_next_question_uses_handwriting_payload_without_skill_module() -> None:
    client = _make_client()
    resp = client.get(
        "/get_next_question?skill=vh_數學B4_TreeDiagramCounting&problem_type=tree_diagram_listing&variant=early_stopping_game"
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["answer_type"] == "handwriting"
    assert body["problem_type_id"] == "tree_diagram_listing"
    assert body["grading_mode"] == "ai_judged_free_response"
    assert body["variant"] == "early_stopping_game"
    assert body["expected_count"] == 6
    assert body["path_labels"] in (["甲", "乙"], ["A", "B"])
    assert body["requires_listing_or_tree"] is True
    assert "expected_paths" not in body
    assert "No module named" not in str(body)


def test_tree_diagram_get_next_question_rotates_variants_by_index() -> None:
    client = _make_client()
    resp0 = client.get(
        "/get_next_question?skill=vh_數學B4_TreeDiagramCounting&problem_type=tree_diagram_listing&tree_diagram_index=0"
    )
    resp1 = client.get(
        "/get_next_question?skill=vh_數學B4_TreeDiagramCounting&problem_type=tree_diagram_listing&tree_diagram_index=1"
    )
    assert resp0.status_code == 200
    assert resp1.status_code == 200
    body0 = resp0.get_json()
    body1 = resp1.get_json()
    assert body0["variant"] == "early_stopping_game"
    assert body1["variant"] == "fixed_stage_binary_tree"
    assert body0["new_question_text"] != body1["new_question_text"]
    for body in (body0, body1):
        assert body["problem_type_id"] == "tree_diagram_listing"
        assert body["answer_type"] == "handwriting"
        assert body["grading_mode"] == "ai_judged_free_response"
        assert "expected_paths" not in body


def test_tree_diagram_get_next_question_changes_within_same_variant_by_index() -> None:
    client = _make_client()
    resp0 = client.get(
        "/get_next_question?skill=vh_數學B4_TreeDiagramCounting&problem_type=tree_diagram_listing&tree_diagram_index=0"
    )
    resp2 = client.get(
        "/get_next_question?skill=vh_數學B4_TreeDiagramCounting&problem_type=tree_diagram_listing&tree_diagram_index=2"
    )
    assert resp0.status_code == 200
    assert resp2.status_code == 200
    body0 = resp0.get_json()
    body2 = resp2.get_json()
    assert body0["variant"] == "early_stopping_game"
    assert body2["variant"] == "early_stopping_game"
    assert body0["new_question_text"] != body2["new_question_text"]
    assert body0["path_labels"] != body2["path_labels"]
    assert body0["expected_count"] == 6
    assert body2["expected_count"] == 6


def test_tree_diagram_stays_out_of_deterministic_allowlist() -> None:
    assert "vh_數學B4_TreeDiagramCounting" not in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST
    assert "tree_diagram_listing" in B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES
