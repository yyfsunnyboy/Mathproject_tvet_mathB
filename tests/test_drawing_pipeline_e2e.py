# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib
import json
import uuid
from urllib.parse import quote

import pytest

from app import create_app
from core.gencode.runtime_skill_wrapper import check_answer as runtime_check_answer
from core.practice_question_store import _STORE
from models import User, db

SKILL_HIST = "vh_\u6578\u5b78B4_HistogramsAndFrequencyPolygons"
PT_CHART = "frequency_distribution_chart_construction"
PNG_1X1 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"drawing_{uuid.uuid4().hex[:10]}",
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


def _get_src_3827_question(client):
    question = {}
    for seed in range(7, 12):
        question = client.get(
            f"/get_next_question?skill={quote(SKILL_HIST)}&problem_type={PT_CHART}&gen_seed={seed}&level=1"
        ).get_json() or {}
        if question.get("component_id") == "src_3827":
            return question
    return question


def test_src_3827_generator_provides_expected_drawing_spec():
    mod = importlib.import_module(
        "agent_skills_v3.vh_\u6578\u5b78B4_HistogramsAndFrequencyPolygons.components.src_3827.generate"
    )

    payload = mod.generate(seed=7, component_id="src_3827")
    spec = payload.get("expected_drawing_spec")
    assert payload["answer_contract"]["checker"] == "free_response_drawing_checker"
    assert payload["answer_type"] == "drawing"
    assert isinstance(spec, dict)
    assert spec["drawing_type"] == "histogram_and_frequency_polygon"
    assert spec["expected_values"]
    assert spec["expected_values"] == payload["metadata"]["expected_drawing_spec"]["expected_values"]
    assert spec["expected_values"] == payload["answer_contract"]["expected_drawing_spec"]["expected_values"]


def test_src_3827_get_next_question_to_check_answer_dispatches_drawing(logged_client, monkeypatch):
    from core.services import drawing_answer_analysis_service as svc

    monkeypatch.setattr(svc, "_is_blank_png", lambda _b: False)
    monkeypatch.setattr(
        svc,
        "_resolve_analyzer_role",
        lambda: {"available": False, "analyzer": "vision_analyzer:unavailable"},
    )
    question = _get_src_3827_question(logged_client)

    assert question.get("question_uid")
    assert question.get("component_id") == "src_3827"
    assert question.get("answer_contract", {}).get("checker") == "free_response_drawing_checker"
    assert question.get("answer_contract", {}).get("expected_drawing_spec", {}).get("expected_values")
    assert question.get("answer_contract", {}).get("ui_contract", {}).get("response_mode") == "drawing"
    assert question.get("answer_contract", {}).get("ui_contract", {}).get("text_input_enabled") is False

    result = logged_client.post(
        "/check_answer",
        json={
            "skill_id": question["skill_id"],
            "question_uid": question["question_uid"],
            "problem_type_id": question["problem_type_id"],
            "answer": "[drawing]",
            "image_data_url": f"data:image/png;base64,{PNG_1X1}",
        },
    ).get_json() or {}

    assert result.get("checker") == "free_response_drawing_checker"
    assert result.get("correct") is None
    assert result.get("is_correct") is None
    assert result.get("status") == "analysis_unavailable"
    assert result.get("system_error") is True


def test_src_3827_missing_spec_returns_configuration_error(logged_client):
    question = _get_src_3827_question(logged_client)
    with logged_client.session_transaction() as sess:
        owner_key = f"user:{sess['_user_id']}"
        current = (_STORE.get(owner_key) or {}).get(question["question_uid"]) or {}
        current.pop("expected_drawing_spec", None)
        if isinstance(current.get("answer_contract"), dict):
            current["answer_contract"].pop("expected_drawing_spec", None)
        if isinstance(current.get("metadata"), dict):
            current["metadata"].pop("expected_drawing_spec", None)
        _STORE.setdefault(owner_key, {})[question["question_uid"]] = current

    result = logged_client.post(
        "/check_answer",
        json={
            "skill_id": question["skill_id"],
            "question_uid": question["question_uid"],
            "problem_type_id": question["problem_type_id"],
            "answer": "[drawing]",
            "image_data_url": f"data:image/png;base64,{PNG_1X1}",
        },
    ).get_json() or {}

    assert result.get("checker") == "free_response_drawing_checker"
    assert result.get("correct") is None
    assert result.get("status") == "missing_spec"
    assert result.get("system_error") is True


def test_src_3827_analyzer_success_returns_score_and_features(logged_client, monkeypatch):
    from core.services import drawing_answer_analysis_service as svc

    monkeypatch.setattr(svc, "_is_blank_png", lambda _b: False)
    monkeypatch.setattr(
        svc,
        "_resolve_analyzer_role",
        lambda: {"available": True, "role": "vision_analyzer", "analyzer": "mock"},
    )

    def fake_call(_prompt, _image_bytes, _status):
        return json.dumps(
            {
                "drawing_detected": True,
                "recognized_type": "histogram_and_frequency_polygon",
                "required_elements": {
                    "x_axis": True,
                    "y_axis": True,
                    "histogram_bars": True,
                    "frequency_polygon": True,
                },
                "histogram": {
                    "detected": True,
                    "bar_count": 4,
                    "estimated_values": expected_values,
                    "category_order_correct": True,
                    "baseline_correct": True,
                },
                "frequency_polygon": {
                    "detected": True,
                    "point_count": 4,
                    "estimated_values": expected_values,
                    "connected_in_order": True,
                    "points_near_category_centers": True,
                },
                "missing_features": [],
                "incorrect_features": [],
                "score": 0.95,
                "confidence": 0.92,
                "is_correct": True,
                "feedback": "ok",
            }
        )

    monkeypatch.setattr(svc, "_call_vision_analyzer", fake_call)
    question = _get_src_3827_question(logged_client)
    expected_values = question.get("answer_contract", {}).get("expected_drawing_spec", {}).get("expected_values", [])

    result = logged_client.post(
        "/check_answer",
        json={
            "skill_id": question["skill_id"],
            "question_uid": question["question_uid"],
            "problem_type_id": question["problem_type_id"],
            "answer": "[drawing]",
            "image_data_url": f"data:image/png;base64,{PNG_1X1}",
        },
    ).get_json() or {}

    assert result.get("checker") == "free_response_drawing_checker"
    assert result.get("correct") is True
    assert result.get("status") == "success"
    assert result.get("score") >= 0.8
    assert result.get("recognized_features", {}).get("histogram", {}).get("estimated_values")


def test_non_drawing_question_keeps_existing_behavior(logged_client):
    _ = logged_client
    payload = {
        "answer_contract": {
            "answer_type": "integer",
            "checker": "integer_checker",
            "answer_equivalence": "numeric_exact",
        }
    }
    assert runtime_check_answer("5", "5", payload=payload) is True
    assert runtime_check_answer("4", "5", payload=payload) is False


def test_answer_contract_consistency_validator():
    from core.gencode.answer_payload import validate_answer_contract_consistency

    # 1. string + drawing checker must fail
    errors = validate_answer_contract_consistency({
        "checker": "free_response_drawing_checker",
        "answer_type": "string",
        "expected_drawing_spec": {"some": "spec"}
    })
    assert any("answer_type=string must not use drawing checker" in e for e in errors)

    # 2. drawing checker without expected_drawing_spec must fail
    errors = validate_answer_contract_consistency({
        "checker": "free_response_drawing_checker",
        "answer_type": "drawing",
        "answer_shape": "drawing",
    })
    assert any("drawing checker must have expected_drawing_spec" in e for e in errors)

    # 3. drawing checker with incorrect answer_type must fail
    errors = validate_answer_contract_consistency({
        "checker": "free_response_drawing_checker",
        "answer_type": "integer",
        "expected_drawing_spec": {"some": "spec"}
    })
    assert any("drawing checker must use answer_type=drawing" in e for e in errors)

    # 4. answer_type=drawing without answer_shape=drawing must fail
    errors = validate_answer_contract_consistency({
        "checker": "free_response_drawing_checker",
        "answer_type": "drawing",
        "answer_shape": "integer",
        "expected_drawing_spec": {"some": "spec"}
    })
    assert any("answer_type=drawing must have answer_shape=drawing" in e for e in errors)

    # 5. drawing UI contract on non-drawing task must fail
    errors = validate_answer_contract_consistency({
        "checker": "integer_checker",
        "answer_type": "integer",
        "ui_contract": {
            "response_mode": "drawing"
        }
    })
    assert any("drawing UI contract must not be applied to non-drawing tasks" in e for e in errors)

    # 6. Valid drawing contract must pass
    errors = validate_answer_contract_consistency({
        "checker": "free_response_drawing_checker",
        "answer_type": "drawing",
        "answer_shape": "drawing",
        "expected_drawing_spec": {"some": "spec"}
    })
    assert not errors

    # 7. Valid string contract must pass
    errors = validate_answer_contract_consistency({
        "checker": "text_short_checker",
        "answer_type": "string",
        "answer_shape": "scalar",
    })
    assert not errors

