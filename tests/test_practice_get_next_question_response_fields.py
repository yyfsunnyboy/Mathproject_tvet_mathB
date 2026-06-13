# -*- coding: utf-8 -*-
"""Regression: /get_next_question must expose canonical question_text for frontend render."""

from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from core.routes.practice import (
    _canonicalize_answer_contract_for_api,
    _extract_canonical_question_stem,
    _finalize_practice_question_api_fields,
)
from models import User, db

SKILL_VERTEX = "vh_數學B1_VertexFormOfQuadraticFunction"
SKILL_DIVISION = "vh_數學B1_DivisionPointCoordinates"
PT_DIVISION = "ordered_pair_compute_internal_division_point_coordinates_short_answer"


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"pract_qtxt_{uuid.uuid4().hex[:10]}",
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


class TestPracticeQuestionStemHelpers:
    def test_extract_prefers_question_text(self) -> None:
        stem = _extract_canonical_question_stem(
            {"question_text": "canonical", "new_question_text": "legacy"}
        )
        assert stem == "canonical"

    def test_extract_falls_back_to_new_question_text(self) -> None:
        stem = _extract_canonical_question_stem({"new_question_text": "legacy only"})
        assert stem == "legacy only"

    def test_finalize_sets_both_fields_equal(self) -> None:
        out = _finalize_practice_question_api_fields(
            {"new_question_text": "stem body", "skill_id": SKILL_VERTEX},
            skill_id=SKILL_VERTEX,
        )
        assert out["question_text"] == "stem body"
        assert out["new_question_text"] == "stem body"

    def test_canonicalize_answer_contract_renames_nested_shape(self) -> None:
        ac = _canonicalize_answer_contract_for_api(
            {
                "answer_type": "text_short",
                "checker": "text_short_checker",
                "answer_contract": {
                    "answer_shape": "text_short",
                    "checker_key": "text_short_checker",
                    "generator_contract": {"answer_shape": "numeric"},
                },
            }
        )
        assert ac["answer_shape"] == "text_short"
        gc = ac.get("generator_contract") or {}
        assert gc.get("answer_shape") == "text_short"
        assert gc.get("raw_generator_answer_shape") == "numeric"


class TestGetNextQuestionResponseFields:
    def test_vertex_skill_response_has_question_text(self, logged_client) -> None:
        resp = logged_client.get(
            f"/get_next_question?skill={quote(SKILL_VERTEX)}&level=1&gen_seed=7"
        )
        data = resp.get_json() or {}
        assert not data.get("error"), data.get("error")
        assert data.get("question_text"), "question_text must be present"
        assert data.get("new_question_text"), "new_question_text must be present"
        assert data["question_text"] == data["new_question_text"]
        assert data.get("question_uid")
        assert data.get("skill_id") == SKILL_VERTEX
        assert isinstance(data.get("answer_contract"), dict)

    def test_division_skill_response_has_question_text(self, logged_client) -> None:
        resp = logged_client.get(
            f"/get_next_question?skill={quote(SKILL_DIVISION)}"
            f"&problem_type={PT_DIVISION}&gen_seed=31&level=1"
        )
        data = resp.get_json() or {}
        assert not data.get("error"), data.get("error")
        assert data.get("question_text")
        assert data["question_text"] == data["new_question_text"]
        assert data.get("question_uid")
        assert data.get("skill_id") == SKILL_DIVISION

    def test_finalize_helper_matches_frontend_fallback_contract(self) -> None:
        """Frontend reads question_text || new_question_text || question."""
        payload = _finalize_practice_question_api_fields(
            {"new_question_text": "平移題幹", "question": "ignored when new_question_text set"},
            skill_id=SKILL_VERTEX,
        )
        frontend_stem = (
            payload.get("question_text")
            or payload.get("new_question_text")
            or payload.get("question")
            or ""
        )
        assert frontend_stem == "平移題幹"
