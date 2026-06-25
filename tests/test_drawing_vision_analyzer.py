from __future__ import annotations

import json

from core.services import drawing_answer_analysis_service as svc

PNG_1X1 = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)

SPEC = {
    "drawing_type": "histogram_and_frequency_polygon",
    "expected_values": [8, 4, 4, 7],
    "required_elements": ["x_axis", "y_axis", "histogram_bars", "frequency_polygon"],
    "tolerance": {"value": 0.8, "position_ratio": 0.12},
}


def _analysis_json(**overrides):
    base = {
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
            "estimated_values": [8.0, 4.1, 3.9, 7.0],
            "category_order_correct": True,
            "baseline_correct": True,
        },
        "frequency_polygon": {
            "detected": True,
            "point_count": 4,
            "estimated_values": [8.0, 4.0, 4.0, 7.1],
            "connected_in_order": True,
            "points_near_category_centers": True,
        },
        "missing_features": [],
        "incorrect_features": [],
        "score": 0.94,
        "confidence": 0.91,
        "is_correct": True,
        "feedback": "ok",
    }
    base.update(overrides)
    return base


def test_parse_json_with_markdown_fence():
    raw = "```json\n" + json.dumps(_analysis_json()) + "\n```"
    parsed = svc.parse_analyzer_json(raw)
    assert parsed["recognized_type"] == "histogram_and_frequency_polygon"


def test_malformed_json_returns_none():
    assert svc.parse_analyzer_json("```json\n{bad\n```") is None


def test_schema_rejects_missing_or_bad_fields():
    ok, errors = svc.validate_analyzer_response(
        _analysis_json(score="bad"),
        drawing_type="histogram_and_frequency_polygon",
    )
    assert ok is False
    assert "score_invalid" in errors


def test_timeout_maps_to_analysis_timeout(monkeypatch):
    monkeypatch.setattr(svc, "_is_blank_png", lambda _b: False)
    monkeypatch.setattr(svc, "_resolve_analyzer_role", lambda: {"available": True, "role": "vision_analyzer", "analyzer": "mock"})
    monkeypatch.setattr(svc, "_call_vision_analyzer", lambda *_a, **_k: (_ for _ in ()).throw(TimeoutError()))
    result = svc.analyze_drawing(
        image_data_url=PNG_1X1,
        question_text="q",
        expected_drawing_spec=SPEC,
        context={},
    )
    assert result["status"] == "analysis_timeout"
    assert result["is_correct"] is None


def test_provider_error_maps_to_analysis_failed(monkeypatch):
    monkeypatch.setattr(svc, "_is_blank_png", lambda _b: False)
    monkeypatch.setattr(svc, "_resolve_analyzer_role", lambda: {"available": True, "role": "vision_analyzer", "analyzer": "mock"})
    monkeypatch.setattr(svc, "_call_vision_analyzer", lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")))
    result = svc.analyze_drawing(
        image_data_url=PNG_1X1,
        question_text="q",
        expected_drawing_spec=SPEC,
        context={},
    )
    assert result["status"] == "analysis_failed"
    assert result["is_correct"] is None


def test_analyzer_success_runs_local_evaluator(monkeypatch):
    monkeypatch.setattr(svc, "_is_blank_png", lambda _b: False)
    monkeypatch.setattr(svc, "_resolve_analyzer_role", lambda: {"available": True, "role": "vision_analyzer", "analyzer": "mock"})
    monkeypatch.setattr(svc, "_call_vision_analyzer", lambda *_a, **_k: json.dumps(_analysis_json()))
    result = svc.analyze_drawing(
        image_data_url=PNG_1X1,
        question_text="q",
        expected_drawing_spec=SPEC,
        context={},
    )
    assert result["status"] == "success"
    assert result["is_correct"] is True
    assert result["score"] >= 0.8
    assert result["recognized_features"]["histogram"]["estimated_values"] == [8.0, 4.1, 3.9, 7.0]


def test_low_confidence_returns_none(monkeypatch):
    monkeypatch.setattr(svc, "_is_blank_png", lambda _b: False)
    monkeypatch.setattr(svc, "_resolve_analyzer_role", lambda: {"available": True, "role": "vision_analyzer", "analyzer": "mock"})
    monkeypatch.setattr(svc, "_call_vision_analyzer", lambda *_a, **_k: json.dumps(_analysis_json(confidence=0.4)))
    result = svc.analyze_drawing(
        image_data_url=PNG_1X1,
        question_text="q",
        expected_drawing_spec=SPEC,
        context={},
    )
    assert result["status"] == "low_confidence"
    assert result["is_correct"] is None


def test_evaluator_missing_histogram_false():
    features = _analysis_json()
    features["histogram"] = {"detected": False}
    result = svc.evaluate_histogram_and_frequency_polygon(features, SPEC)
    assert result["is_correct"] is False
    assert "histogram" in result["missing_features"]


def test_evaluator_missing_polygon_false():
    features = _analysis_json()
    features["frequency_polygon"] = {"detected": False}
    result = svc.evaluate_histogram_and_frequency_polygon(features, SPEC)
    assert result["is_correct"] is False
    assert "frequency_polygon" in result["missing_features"]


def test_evaluator_wrong_values_false():
    features = _analysis_json()
    features["histogram"]["estimated_values"] = [1, 1, 1, 1]
    result = svc.evaluate_histogram_and_frequency_polygon(features, SPEC)
    assert result["is_correct"] is False
    assert "histogram_values" in result["incorrect_features"]


def test_evaluator_near_tolerance_true():
    features = _analysis_json()
    features["histogram"]["estimated_values"] = [8.7, 3.3, 4.6, 6.3]
    features["frequency_polygon"]["estimated_values"] = [7.3, 4.7, 3.4, 7.7]
    result = svc.evaluate_histogram_and_frequency_polygon(features, SPEC)
    assert result["is_correct"] is True
