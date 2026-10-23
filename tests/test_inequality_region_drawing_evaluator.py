"""linear_inequality_region drawing type: the vision analyzer only reports features; the local
evaluator decides.  Truth for the shaded side is recomputed here from the relations themselves
(independent of the evaluator's probe-point helper)."""
from __future__ import annotations

import copy
import json

import pytest

from core.services import drawing_answer_analysis_service as svc

PNG_1X1 = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


def _spec(relations, extent=6):
    return {
        "drawing_type": "linear_inequality_region",
        "relations": relations,
        "required_elements": ["x_axis", "y_axis", "boundary_lines", "shaded_region"],
        "axis_range": {"x_min": -extent, "x_max": extent, "y_min": -extent, "y_max": extent},
    }


# x - y - 3 <= 0 (solid) and 2x + y - 2 > 0 (dashed), as ``a x + b y + c >= 0`` oriented relations
SYSTEM = _spec([
    {"line": [-1, 1, 3], "boundary": "solid", "shaded_side": "positive_normal"},
    {"line": [2, 1, -2], "boundary": "dashed", "shaded_side": "positive_normal"},
])
SINGLE = _spec([{"line": [2, -1, 4], "boundary": "dashed", "shaded_side": "positive_normal"}])


def _truth(spec, x, y):
    return all(r["line"][0] * x + r["line"][1] * y + r["line"][2] > 0 for r in spec["relations"])


def _line_points(rel):
    a, b, c = rel["line"]
    if b != 0:
        return [[x, (-a * x - c) / b] for x in (-3.0, 0.0, 3.0)]
    return [[-c / a, y] for y in (-3.0, 0.0, 3.0)]


def _features(spec, *, shade=None, lines=None, styles=None, confidence=0.95, detected=True):
    shade = shade or (lambda x, y: _truth(spec, x, y))
    styles = styles or [r["boundary"] for r in spec["relations"]]
    lines = lines if lines is not None else [
        {"points_on_line": _line_points(r), "style": styles[i]} for i, r in enumerate(spec["relations"])
    ]
    probes = svc.inequality_region_probe_points(spec)
    return {
        "recognized_type": "linear_inequality_region",
        "required_elements": {"x_axis": True, "y_axis": True},
        "lines": lines,
        "shaded_region_detected": detected,
        "probe_points": [{"x": p["x"], "y": p["y"], "shaded": bool(shade(p["x"], p["y"]))} for p in probes],
        "missing_features": [],
        "incorrect_features": [],
        "confidence": confidence,
    }


@pytest.mark.parametrize("spec", [SINGLE, SYSTEM])
def test_probe_points_cover_inside_and_outside_and_match_independent_truth(spec):
    probes = svc.inequality_region_probe_points(spec)
    assert any(p["expected"] for p in probes) and any(not p["expected"] for p in probes)
    for p in probes:
        assert p["expected"] == _truth(spec, p["x"], p["y"])


@pytest.mark.parametrize("spec", [SINGLE, SYSTEM])
def test_correct_drawing_accepted(spec):
    result = svc.evaluate_linear_inequality_region(_features(spec), spec)
    assert result["is_correct"] is True, result
    assert result["missing_features"] == [] and result["incorrect_features"] == []


@pytest.mark.parametrize("spec", [SINGLE, SYSTEM])
def test_shading_the_wrong_side_is_rejected(spec):
    result = svc.evaluate_linear_inequality_region(_features(spec, shade=lambda x, y: not _truth(spec, x, y)), spec)
    assert result["is_correct"] is False
    assert "shaded_region" in result["incorrect_features"]


def test_one_inequality_of_the_system_shaded_alone_is_rejected():
    only_first = lambda x, y: SYSTEM["relations"][0]["line"][0] * x + SYSTEM["relations"][0]["line"][1] * y + SYSTEM["relations"][0]["line"][2] > 0  # noqa: E731
    result = svc.evaluate_linear_inequality_region(_features(SYSTEM, shade=only_first), SYSTEM)
    assert result["is_correct"] is False


def test_no_shading_is_missing_shaded_region():
    result = svc.evaluate_linear_inequality_region(_features(SINGLE, shade=lambda x, y: False, detected=False), SINGLE)
    assert result["is_correct"] is False
    assert "shaded_region" in result["missing_features"]


def test_wrong_style_is_rejected_and_unknown_style_is_not():
    wrong = svc.evaluate_linear_inequality_region(_features(SINGLE, styles=["solid"]), SINGLE)
    assert wrong["is_correct"] is False and "boundary_style" in wrong["incorrect_features"]
    unknown = svc.evaluate_linear_inequality_region(_features(SINGLE, styles=["unknown"]), SINGLE)
    assert unknown["is_correct"] is True


def test_misplaced_boundary_line_is_rejected():
    shifted = [{"points_on_line": [[-3.0, 1.0], [0.0, 7.0], [1.0, 9.0]], "style": "dashed"}]
    result = svc.evaluate_linear_inequality_region(_features(SINGLE, lines=shifted), SINGLE)
    assert result["is_correct"] is False
    assert "boundary_line_position" in result["incorrect_features"]


def test_missing_second_line_and_extra_line():
    one_line = [{"points_on_line": _line_points(SYSTEM["relations"][0]), "style": "solid"}]
    result = svc.evaluate_linear_inequality_region(_features(SYSTEM, lines=one_line), SYSTEM)
    assert result["is_correct"] is False and "boundary_lines" in result["missing_features"]
    extra = [{"points_on_line": _line_points(r), "style": r["boundary"]} for r in SYSTEM["relations"]]
    extra.append({"points_on_line": [[-3.0, 0.5], [0.0, 0.5], [3.0, 0.5]], "style": "solid"})
    result = svc.evaluate_linear_inequality_region(_features(SYSTEM, lines=extra), SYSTEM)
    assert result["is_correct"] is False and "extra_boundary_line" in result["incorrect_features"]


def test_low_confidence_is_not_a_verdict():
    result = svc.evaluate_linear_inequality_region(_features(SINGLE, confidence=0.3), SINGLE)
    assert result["is_correct"] is None and result["status"] == "low_confidence"


def test_unanswered_probe_points_are_not_guessed_correct():
    features = _features(SINGLE)
    features["probe_points"] = features["probe_points"][:2]
    assert svc.evaluate_linear_inequality_region(features, SINGLE)["is_correct"] is None


def test_prompt_withholds_expected_answer():
    prompt = svc.build_drawing_analysis_prompt(question_text="q", expected_drawing_spec=SYSTEM)
    assert "Probe points" in prompt
    assert "dashed" in prompt  # only as a style vocabulary
    for leak in ('"relations"', "positive_normal", "boundary_intersection", "[2, 1, -2]"):
        assert leak not in prompt


def _patch_vision(monkeypatch, features):
    monkeypatch.setattr(svc, "_is_blank_png", lambda _b: False)
    monkeypatch.setattr(svc, "_resolve_analyzer_role", lambda: {"available": True, "role": "vision_analyzer", "analyzer": "mock"})
    monkeypatch.setattr(svc, "_call_vision_analyzer", lambda *_a, **_k: json.dumps(features))


def test_analyze_drawing_end_to_end_with_mock_vision(monkeypatch):
    _patch_vision(monkeypatch, _features(SYSTEM))
    ok = svc.analyze_drawing(image_data_url=PNG_1X1, question_text="q", expected_drawing_spec=copy.deepcopy(SYSTEM), context={})
    assert ok["status"] == "success" and ok["is_correct"] is True
    _patch_vision(monkeypatch, _features(SYSTEM, shade=lambda x, y: not _truth(SYSTEM, x, y)))
    bad = svc.analyze_drawing(image_data_url=PNG_1X1, question_text="q", expected_drawing_spec=copy.deepcopy(SYSTEM), context={})
    assert bad["is_correct"] is False and bad["system_error"] is False


def test_checker_accepts_the_new_type_and_missing_image_is_a_system_error():
    from core.checkers.free_response_drawing_checker import SUPPORTED_DRAWING_TYPES, check_drawing_answer

    assert "linear_inequality_region" in SUPPORTED_DRAWING_TYPES
    result = check_drawing_answer(image_data_url=None, question_text="q", expected_drawing_spec=SYSTEM)
    assert result["system_error"] is True and result["is_correct"] is None
