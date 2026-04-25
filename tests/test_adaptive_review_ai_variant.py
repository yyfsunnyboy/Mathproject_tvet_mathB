# -*- coding: utf-8 -*-

from flask import Flask

import adaptive_review_api as api


class _DummyResponse:
    def __init__(self, text: str):
        self.text = text


def _seed_question():
    return {
        "item_id": 42,
        "skill_id": 3,
        "skill_name": "jh_數學1上_FourArithmeticOperationsOfIntegers",
        "question_text": "計算 3 + 4",
        "correct_answer": "7",
        "predicted_difficulty": 0.35,
        "answer_format_hint": "請輸入整數",
        "family_id": "I1",
        "subskill_nodes": ["integer_addition"],
        "detailed_solution": "",
        "difficulty_level": 1,
        "problem_type": "calculation",
        "source_question_id": 1001,
        "source": "rl_fixed_question",
        "expected_answer": "7",
        "acceptable_answers": ["7"],
    }


def test_generate_ai_variant_success(monkeypatch):
    monkeypatch.setattr(api, "get_engine", lambda: object())
    monkeypatch.setattr(api, "_fetch_seed_question_by_item_id", lambda item_id, engine: _seed_question())
    monkeypatch.setattr(api, "get_ai_client", lambda role="tutor": object())
    monkeypatch.setattr(
        api,
        "call_ai_with_retry",
        lambda client, prompt, **kwargs: _DummyResponse(
            """{
                "question_text": "計算 5 + 2",
                "latex": "5+2",
                "answer_expression": "7",
                "answer_type": "integer",
                "variant_notes": "same structure"
            }"""
        ),
    )

    payload = api.generate_ai_variant_from_rl_selected_question(42)

    assert payload["question_text"] == "計算 5 + 2"
    assert payload["correct_answer"] == "7"
    assert payload["expected_answer"] == "7"
    assert payload["source"] == "ai_variant_from_rl_seed"
    assert payload["skill_catalog_id"] == "jh_數學1上_FourArithmeticOperationsOfIntegers"
    assert payload["runtime_log"]["ai_variant_success"] is True
    assert payload["runtime_log"]["fallback_used"] is False
    assert payload["runtime_log"]["sympy_validation_status"] == "parsed_ok"


def test_generate_ai_variant_success_without_latex(monkeypatch):
    monkeypatch.setattr(api, "get_engine", lambda: object())
    monkeypatch.setattr(api, "_fetch_seed_question_by_item_id", lambda item_id, engine: _seed_question())
    monkeypatch.setattr(api, "get_ai_client", lambda role="tutor": object())
    monkeypatch.setattr(
        api,
        "call_ai_with_retry",
        lambda client, prompt, **kwargs: _DummyResponse(
            """{
                "question_text": "計算 8 - 1",
                "answer_expression": "7",
                "answer_type": "integer",
                "variant_notes": "minimal payload"
            }"""
        ),
    )

    payload = api.generate_ai_variant_from_rl_selected_question(42)

    assert payload["question_text"] == "計算 8 - 1"
    assert payload["correct_answer"] == "7"
    assert payload["latex"]
    assert payload["source"] == "ai_variant_from_rl_seed"
    assert payload["runtime_log"]["ai_variant_success"] is True
    assert payload["runtime_log"]["fallback_used"] is False


def test_generate_ai_variant_fallback_on_invalid_json(monkeypatch):
    monkeypatch.setattr(api, "get_engine", lambda: object())
    monkeypatch.setattr(api, "_fetch_seed_question_by_item_id", lambda item_id, engine: _seed_question())
    monkeypatch.setattr(api, "get_ai_client", lambda role="tutor": object())
    monkeypatch.setattr(
        api,
        "call_ai_with_retry",
        lambda client, prompt, **kwargs: _DummyResponse("not-json"),
    )

    payload = api.generate_ai_variant_from_rl_selected_question(42)

    assert payload["question_text"] == "計算 3 + 4"
    assert payload["correct_answer"] == "7"
    assert payload["source"] == "rl_fixed_question_fallback"
    assert payload["runtime_log"]["ai_variant_success"] is False
    assert payload["runtime_log"]["fallback_used"] is True


def test_adaptive_review_question_route_preserves_frontend_shape(monkeypatch):
    app = Flask(__name__)
    app.register_blueprint(api.adaptive_review_bp)

    monkeypatch.setattr(
        api,
        "generate_ai_variant_from_rl_selected_question",
        lambda item_id, student_state=None: {
            "item_id": item_id,
            "skill_id": 3,
            "skill_name": "jh_數學1上_FourArithmeticOperationsOfIntegers",
            "question_text": "計算 9 - 2",
            "correct_answer": "7",
            "predicted_difficulty": 0.2,
            "answer_format_hint": "請輸入整數",
            "family_id": "I1",
            "subskill_nodes": ["integer_addition"],
            "expected_answer": "7",
            "acceptable_answers": ["7"],
            "difficulty_level": 1,
            "problem_type": "calculation",
            "source_question_id": 1001,
            "source": "ai_variant_from_rl_seed",
            "runtime_log": {
                "rl_selected_question_id": item_id,
                "ai_variant_success": True,
                "fallback_used": False,
                "sympy_validation_status": "parsed_ok",
                "generation_latency_ms": 12,
            },
            "latex": "9-2",
            "variant_notes": "same structure",
            "skill_catalog_id": "jh_數學1上_FourArithmeticOperationsOfIntegers",
            "rl_selected_question_id": item_id,
        },
    )

    client = app.test_client()
    response = client.get("/api/adaptive-review/question/42")

    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["item_id"] == 42
    assert payload["question_text"] == "計算 9 - 2"
    assert payload["correct_answer"] == "7"
    assert payload["acceptable_answers"] == ["7"]
    assert payload["source"] == "ai_variant_from_rl_seed"
    assert payload["runtime_log"]["ai_variant_success"] is True
