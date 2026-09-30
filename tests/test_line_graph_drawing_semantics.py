"""Regression: straight-line drawing answers (B1 LinearFunction canvas items).

The vision analyzer only extracts line features; evaluate_line_graph decides.
Case B: a student draws the horizontal line y=6 for "畫出常數函數 f(x)=6" and
must not be told the graph is missing `function_line`.
"""
from __future__ import annotations

import base64
import copy
import importlib
import io
import json

import pytest

from core.services import drawing_answer_analysis_service as service
from core.services.drawing_answer_analysis_service import (
    build_drawing_analysis_prompt,
    evaluate_line_graph,
    validate_analyzer_response,
)

LINEAR_SKILL = "vh_數學B1_LinearFunction"


def _spec(points, *, slope=None, intercept=None, extent=8):
    return {
        "drawing_type": "line_graph",
        "slope": slope,
        "y_intercept": intercept,
        "expected_line": {"points": points, "horizontal": slope == 0, "spans_graph_width": True},
        "required_elements": ["x_axis", "y_axis", "function_line"],
        "axis_range": {"x_min": -extent, "x_max": extent, "y_min": -extent, "y_max": extent},
        "tolerance": {"slope": 0.08, "y_intercept": 0.35},
    }


CONSTANT_6 = _spec([[-8, 6], [8, 6]], slope=0, intercept=6)
LINEAR_2X_PLUS_1 = _spec([[-6, -11], [6, 13]], slope=2, intercept=1, extent=15)
VERTICAL_3 = _spec([[3, -6], [3, 6]], extent=6)


def _features(points, *, detected=True, straight=True, confidence=0.95, **line_extra):
    line = {"detected": detected, "is_straight": straight, "points_on_line": points}
    line.update(line_extra)
    return {
        "recognized_type": "line_graph",
        "required_elements": {"x_axis": True, "y_axis": True, "function_line": detected},
        "line": line,
        "missing_features": [],
        "incorrect_features": [],
        "confidence": confidence,
    }


# --------------------------------------------------------------------------- evaluator


@pytest.mark.parametrize(
    ("spec", "points"),
    [
        (CONSTANT_6, [[-6, 6], [0, 6], [6, 6]]),
        (CONSTANT_6, [[-6, 6.2], [0, 6.0], [6, 5.8]]),  # slight hand tilt
        (LINEAR_2X_PLUS_1, [[-5, -9], [0, 1], [5, 11]]),
        (LINEAR_2X_PLUS_1, [[-5, -9.3], [0, 1.1], [5, 11.2]]),
        (VERTICAL_3, [[3, -5], [3, 0], [3, 5]]),
        (VERTICAL_3, [[2.8, -5], [3, 0], [3.2, 5]]),  # near-vertical stroke
    ],
)
def test_correct_lines_accepted(spec, points) -> None:
    res = evaluate_line_graph(_features(points), spec)
    assert res["is_correct"] is True, res
    assert res["missing_features"] == []


@pytest.mark.parametrize(
    ("spec", "points"),
    [
        (CONSTANT_6, [[-6, 8], [0, 8], [6, 8]]),  # y=8
        (CONSTANT_6, [[-6, 7], [0, 7], [6, 7]]),  # off by one grid unit
        (CONSTANT_6, [[6, -6], [6, 0], [6, 6]]),  # vertical x=6 instead of y=6
        (LINEAR_2X_PLUS_1, [[-4, 9], [0, 1], [4, -7]]),  # slope sign flipped
        (LINEAR_2X_PLUS_1, [[-4, -6], [0, 2], [4, 10]]),  # intercept off by one
        (VERTICAL_3, [[1, -5], [1, 0], [1, 5]]),
        (VERTICAL_3, [[4, -5], [4, 0], [4, 5]]),
        (VERTICAL_3, [[-5, 3], [0, 3], [5, 3]]),  # horizontal y=3 instead of x=3
    ],
)
def test_wrong_lines_rejected(spec, points) -> None:
    res = evaluate_line_graph(_features(points), spec)
    assert res["is_correct"] is False, res


def test_missing_line_rejected_with_readable_feedback() -> None:
    res = evaluate_line_graph(_features(None, detected=False, label_text="y=6"), CONSTANT_6)
    assert res["is_correct"] is False
    assert res["missing_features"] == ["function_line"]
    assert "函數圖形（直線）" in res["feedback"]
    assert "function_line" not in res["feedback"]


def test_curved_stroke_rejected() -> None:
    res = evaluate_line_graph(_features([[-6, 6], [0, 6], [6, 6]], straight=False), CONSTANT_6)
    assert res["is_correct"] is False
    assert "line_shape" in res["incorrect_features"]


def test_low_confidence_is_not_a_verdict() -> None:
    res = evaluate_line_graph(_features([[-6, 6], [0, 6], [6, 6]], confidence=0.3), CONSTANT_6)
    assert res["is_correct"] is None
    assert res["status"] == "low_confidence"


def test_unreadable_geometry_is_not_accepted() -> None:
    res = evaluate_line_graph(_features([]), CONSTANT_6)
    assert res["is_correct"] is None


def test_printed_canvas_axes_satisfy_axis_requirement() -> None:
    features = _features([[-6, 6], [0, 6], [6, 6]])
    features["required_elements"] = {"x_axis": False, "y_axis": False, "function_line": True}
    assert evaluate_line_graph(features, CONSTANT_6)["is_correct"] is True


def test_label_alone_never_substitutes_for_geometry() -> None:
    res = evaluate_line_graph(_features([[-6, 8], [0, 8], [6, 8]], label_text="y=6"), CONSTANT_6)
    assert res["is_correct"] is False


def test_recognized_type_alias_is_not_a_system_error() -> None:
    raw = _features([[-6, 6], [0, 6], [6, 6]])
    raw["recognized_type"] = "function_graph"
    ok, normalized = validate_analyzer_response(raw, drawing_type="line_graph")
    assert ok, normalized
    assert normalized["recognized_type"] == "line_graph"


def test_line_graph_prompt_requests_line_schema_without_answer() -> None:
    spec = dict(CONSTANT_6, equation="y=6")
    prompt = build_drawing_analysis_prompt(question_text="畫出常數函數 f(x)=6", expected_drawing_spec=spec)
    assert '"points_on_line"' in prompt
    assert "histogram" not in prompt
    assert "y=6" not in prompt
    assert "f(x)=6" not in prompt


# --------------------------------------------------------------------------- production path


def _png_with_line() -> str:
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (200, 200), (255, 255, 255, 255))
    ImageDraw.Draw(img).line([(10, 60), (190, 60)], fill=(20, 20, 90, 255), width=4)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def _stored_question(skill_id: str, component_id: str, seed: int) -> dict:
    from core.gencode.answer_payload import refresh_runtime_question_session
    from core.legacy_generator_adapter import normalize_runtime_value
    from core.practice_question_store import slim_payload_for_store

    wrapper = importlib.import_module(f"skills.{skill_id}")
    data = normalize_runtime_value(wrapper.generate(level=1, seed=seed, component_id=component_id))
    if "answer" in data and "correct_answer" not in data:
        data["correct_answer"] = data["answer"]
    session = refresh_runtime_question_session(dict(data), skill_id=skill_id)
    return slim_payload_for_store(session, skill_id=skill_id, question_uid="regression")


def _grade_drawing(stored: dict, analyzer_json: dict, monkeypatch) -> dict:
    from core.gencode.answer_grading import grade_answer_for_current_question
    from core.gencode.answer_payload import refresh_runtime_question_session

    monkeypatch.setattr(
        service,
        "_resolve_analyzer_role",
        lambda: {"available": True, "analyzer": "test:mock", "role": "vision_analyzer"},
    )
    monkeypatch.setattr(service, "_call_vision_analyzer", lambda *_args, **_kw: json.dumps(analyzer_json))
    image = _png_with_line()
    current = refresh_runtime_question_session(copy.deepcopy(stored), skill_id=LINEAR_SKILL)
    return grade_answer_for_current_question(
        {"composite_image_data_url": image, "image_data_url": image, "student_strokes_image_data_url": image},
        current,
        LINEAR_SKILL,
    )


@pytest.fixture(scope="module")
def constant_question() -> dict:
    return _stored_question(LINEAR_SKILL, "src_4433", 4433)


def _constant_value(stored: dict) -> float:
    spec = (stored.get("answer_contract") or {}).get("expected_drawing_spec") or {}
    assert spec.get("drawing_type") == "line_graph"
    return float(spec["y_intercept"])


def test_case_b_horizontal_line_passes_production_grader(constant_question, monkeypatch) -> None:
    c = _constant_value(constant_question)
    analyzer = _features([[-4, c], [0, c], [4, c]], orientation="horizontal", label_text=f"y={c:g}")
    analyzer["recognized_type"] = "constant_function"
    res = _grade_drawing(constant_question, analyzer, monkeypatch)
    assert res.get("correct") is True, res
    assert "function_line" not in (res.get("missing_features") or [])
    assert not res.get("system_error")


def test_case_b_wrong_horizontal_line_rejected(constant_question, monkeypatch) -> None:
    c = _constant_value(constant_question)
    wrong = c + 2
    res = _grade_drawing(constant_question, _features([[-4, wrong], [0, wrong], [4, wrong]]), monkeypatch)
    assert res.get("correct") is False, res


def test_case_b_label_without_line_rejected(constant_question, monkeypatch) -> None:
    c = _constant_value(constant_question)
    res = _grade_drawing(constant_question, _features(None, detected=False, label_text=f"y={c:g}"), monkeypatch)
    assert res.get("correct") is False
    assert "function_line" in (res.get("missing_features") or [])
