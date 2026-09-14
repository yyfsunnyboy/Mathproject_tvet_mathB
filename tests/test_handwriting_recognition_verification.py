from __future__ import annotations

import json

from flask import Flask

import core.ai_analyzer as analyzer
from core.handwriting_ai_check import HandwritingCheckContext, build_handwriting_check_response


class _Response:
    def __init__(self, payload):
        self.text = json.dumps(payload)


class _VisionClient:
    def __init__(self, payloads):
        self.payloads = iter(payloads)
        self.calls = []

    def generate_content(self, prompt, image_path=None):
        self.calls.append((prompt, image_path))
        return _Response(next(self.payloads))


def _run_analyze(monkeypatch, payloads, *, expected="3"):
    client = _VisionClient(payloads)
    monkeypatch.setattr(analyzer, "get_ai_client", lambda role: client)
    monkeypatch.setattr(analyzer, "get_ai_prompt_with_source", lambda: ("Read {context} {prereq_text}", "test"))
    monkeypatch.setattr(
        "core.database_runtime.release_db_session_before_external_call",
        lambda *_args, **_kwargs: None,
    )
    app = Flask(__name__)
    with app.app_context():
        result = analyzer.analyze(
            "data:image/png;base64,Mw==",
            "A(-17), B(-20)",
            None,
            prerequisite_skills=[],
            correct_answer=expected,
        )
    return result, client


def test_single_digit_misread_as_37_becomes_uncertain_and_skips_checker(monkeypatch):
    result, client = _run_analyze(
        monkeypatch,
        [
            {"mode": "final_answer_only", "recognized_expression": "37", "confidence": 0.99},
            {"recognized_answer": "3"},
        ],
    )
    checker_calls = []
    response = build_handwriting_check_response(
        image_base64="ink",
        ctx=HandwritingCheckContext(correct_answer="3"),
        ai_result=result,
        checker=lambda *_args, **_kwargs: checker_calls.append(True) or False,
    )

    assert len(client.calls) == 2
    assert result["recognition_uncertain"] is True
    assert response["recognized_answer"] == "37"
    assert response["completion_state"] == "recognition_uncertain"
    assert response["should_record_attempt"] is False
    assert response["final_answer_correct"] is None
    assert checker_calls == []


def test_verification_is_image_only_and_never_receives_expected_answer(monkeypatch):
    _result, client = _run_analyze(
        monkeypatch,
        [
            {"mode": "final_answer_only", "recognized_answer": "3", "confidence": 0.99},
            {"recognized_answer": "3"},
        ],
        expected="DO_NOT_USE_EXPECTED_999",
    )
    verification_prompt, image_path = client.calls[1]
    assert image_path
    assert "DO_NOT_USE_EXPECTED_999" not in verification_prompt
    assert "A(-17)" not in verification_prompt


def test_consistent_single_digit_reaches_shared_checker(monkeypatch):
    result, _client = _run_analyze(
        monkeypatch,
        [
            {"mode": "final_answer_only", "recognized_answer": "3", "confidence": 0.99},
            {"recognized_answer": "3"},
        ],
    )
    checker_calls = []
    response = build_handwriting_check_response(
        image_base64="ink",
        ctx=HandwritingCheckContext(correct_answer="3"),
        ai_result=result,
        checker=lambda recognized, expected, **_kwargs: checker_calls.append((recognized, expected)) or True,
    )
    assert checker_calls == [("3", "3")]
    assert response["is_correct"] is True
    assert response["should_record_attempt"] is True
