"""cubic_graph drawing grader: deterministic evaluator on synthetic analyzer features (no AI call)."""

from __future__ import annotations

import base64
import io
import json
from unittest import mock

import pytest

from core.services import drawing_answer_analysis_service as svc

AXIS = {"x_min": -5, "x_max": 5, "y_min": -6, "y_max": 8}


def cubic_spec(a, p, h, k, *, turning=(), zeros=()):
    return {
        "drawing_type": "cubic_graph", "graph_kind": "cubic_graph", "required_elements": ["x_axis", "y_axis", "cubic_curve"], "axis_range": AXIS,
        "expected_cubics": [{"a": a, "p": p, "center": [h, k], "turning_points": [list(t) for t in turning], "x_intercepts": list(zeros)}],
    }


def f(a, p, h, k, x):
    return a * (x - h) ** 3 + p * (x - h) + k


def curve(a, p, h, k, *, xs=None, shift=(0.0, 0.0), jitter=0.0, shape="cubic", right_end=None, center=True, turning=(), zeros=()):
    xs = xs or [h - 1.6 + 3.2 * i / 6 for i in range(7)]
    pts = [[x + shift[0] + (jitter if i % 2 else -jitter), f(a, p, h, k, x) + shift[1]] for i, x in enumerate(xs)]
    return {"detected": True, "shape": shape, "right_end": right_end or ("up" if a > 0 else "down"),
            "center": [h + shift[0], k + shift[1]] if center else None, "turning_points": [list(t) for t in turning],
            "x_intercepts": list(zeros), "points_on_curve": pts, "label_text": ""}


def features(*curves, confidence=0.9):
    return {"drawing_detected": bool(curves), "recognized_type": "cubic_graph", "required_elements": {"x_axis": True, "y_axis": True, "curve": bool(curves)},
            "curve_count": len(curves), "curves": list(curves), "missing_features": [], "incorrect_features": [], "confidence": confidence}


def verdict(spec, feats):
    return svc.evaluate_cubic_graph(feats, spec)["is_correct"]


@pytest.mark.parametrize("a,p,h,k", [(1, 0, 0, 0), (-1, 0, 0, 0), (1, 2, 0, 0), (1, 2, 3, 1), (2, 3, -1, 2)])
def test_correct_monotone_cubics_pass(a, p, h, k):
    assert verdict(cubic_spec(a, p, h, k), features(curve(a, p, h, k))) is True


def test_correct_wavy_cubic_with_turning_points_and_zeros_passes():
    spec = cubic_spec(1, -1, 0, 0, turning=[(-0.58, 0.38), (0.58, -0.38)], zeros=[-1, 0, 1])
    assert verdict(spec, features(curve(1, -1, 0, 0, xs=[-1.6, -1.0, -0.58, 0.0, 0.58, 1.0, 1.6], turning=[(-0.6, 0.4), (0.6, -0.4)], zeros=[-1, 0, 1]))) is True
    assert verdict(spec, features(curve(1, -1, 0, 0, xs=[-1.6, -1.0, -0.58, 0.0, 0.58, 1.0, 1.6], turning=[], zeros=[]))) is None  # features not read -> uncertain, not a guess


def test_reasonable_hand_drawn_error_is_accepted():
    assert verdict(cubic_spec(1, 2, 0, 0), features(curve(1, 2, 0, 0, jitter=0.12, shift=(0.1, -0.1)))) is True


@pytest.mark.parametrize("shift", [(2.0, 0.0), (0.0, 2.5), (-2.0, 2.0), (3.0, -3.0)])
def test_wrong_centre_or_position_is_rejected(shift):
    assert verdict(cubic_spec(1, 0, 0, 0), features(curve(1, 0, 0, 0, shift=shift))) is False


def test_reversed_orientation_and_wrong_steepness_are_rejected():
    spec = cubic_spec(1, 0, 0, 0)
    assert verdict(spec, features(curve(-1, 0, 0, 0))) is False
    assert verdict(spec, features(curve(1, 0, 0, 0, right_end="down"))) is False
    assert verdict(cubic_spec(3, 0, 0, 0), features(curve(0.4, 0, 0, 0))) is not True  # far too flat: never accepted (at most uncertain)
    assert verdict(cubic_spec(1, 0, 0, 0), features(curve(0.4, 0, 0, 0, xs=[-4.0, -3.0, -2.0, 0.0, 2.0, 3.0, 4.0]))) is False


@pytest.mark.parametrize("shape", ["line", "parabola", "other"])
def test_line_parabola_and_other_shapes_are_not_cubics(shape):
    assert verdict(cubic_spec(1, 0, 0, 0), features(curve(1, 0, 0, 0, shape=shape))) is False


def test_wavy_curve_drawn_where_a_monotone_one_is_expected_is_rejected():
    spec = cubic_spec(1, 2, 0, 0)
    assert verdict(spec, features(curve(1, -3, 0, 0, xs=[-2.0, -1.2, -0.6, 0.0, 0.6, 1.2, 2.0], turning=[(-1.0, 2.0), (1.0, -2.0)]))) is False


def test_blank_low_confidence_and_unreadable_input_never_pass():
    spec = cubic_spec(1, 0, 0, 0)
    assert verdict(spec, features()) is False
    assert verdict(spec, features(curve(1, 0, 0, 0), confidence=0.3)) is None
    assert verdict(spec, features(curve(1, 0, 0, 0, xs=[-1.0, 0.0, 1.0]))) is None  # too few readable points
    assert svc.evaluate_cubic_graph(features(curve(1, 0, 0, 0)), {"drawing_type": "cubic_graph"})["system_error"] is True  # spec incomplete


def test_an_extra_curve_and_a_retraced_axis():
    spec = cubic_spec(1, 0, 0, 0)
    axis = {"detected": True, "shape": "line", "right_end": "unknown", "center": None, "points_on_curve": [[-4, 0], [-2, 0], [-1, 0], [0, 0], [1, 0], [2, 0], [4, 0]]}
    assert verdict(spec, features(curve(1, 0, 0, 0), axis)) is True
    assert verdict(spec, features(axis)) is False
    assert verdict(spec, features(curve(1, 0, 0, 0), curve(-1, 0, 2, 2))) is False


def test_prompt_never_leaks_the_expected_answer():
    prompt = svc.build_drawing_analysis_prompt(question_text="描繪", expected_drawing_spec=cubic_spec(7.25, 3.5, -8.75, 4.5, turning=[(1.5, 2.5)]))
    for secret in ("7.25", "3.5", "-8.75", "expected_cubics"):
        assert secret not in prompt
    assert "turning_points" in prompt and "center" in prompt


def test_cubic_graph_is_a_registered_type_in_service_and_checker():
    from core.checkers import free_response_drawing_checker as checker

    assert "cubic_graph" in svc.SUPPORTED_DRAWING_TYPES and "cubic_graph" in checker.SUPPORTED_DRAWING_TYPES
    assert svc.DRAWING_EVALUATOR_REGISTRY["cubic_graph"] is svc.evaluate_cubic_graph


def _png_data_url() -> str:
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (200, 120), (255, 255, 255, 255))
    ImageDraw.Draw(img).line([(10, 10), (190, 110)], fill=(0, 0, 0, 255), width=4)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def _analyze(model_json: dict, spec_: dict) -> dict:
    with mock.patch.object(svc, "_resolve_analyzer_role", return_value={"available": True, "analyzer": "mock"}), \
            mock.patch.object(svc, "_call_vision_analyzer", return_value=json.dumps(model_json)):
        return svc.analyze_drawing(image_data_url=_png_data_url(), question_text="描繪", expected_drawing_spec=spec_)


def test_end_to_end_with_a_mocked_vision_model():
    s = cubic_spec(1, 0, 0, 0)
    assert _analyze(features(curve(1, 0, 0, 0)), s)["is_correct"] is True
    assert _analyze(features(curve(1, 0, 0, 0, shape="parabola")), s)["is_correct"] is False
    alias = {**features(curve(1, 0, 0, 0)), "recognized_type": "cubic"}
    assert _analyze(alias, s)["is_correct"] is True
    named_line = {**features(curve(1, 0, 0, 0, shape="line")), "recognized_type": "line_graph"}
    result = _analyze(named_line, s)
    assert result["is_correct"] is False and not result.get("system_error")
