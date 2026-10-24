"""parabola_graph drawing grader: deterministic evaluator on synthetic analyzer features (no AI call)."""

from __future__ import annotations

import base64
import io
import json
from unittest import mock

import pytest

from core.services import drawing_answer_analysis_service as svc

AXIS = {"x_min": -6, "x_max": 6, "y_min": -6, "y_max": 10}


def spec(*parabolas, required=("x_axis", "y_axis", "parabola_curve")):
    return {
        "drawing_type": "parabola_graph", "graph_kind": "parabola_graph", "required_elements": list(required), "axis_range": AXIS,
        "expected_parabolas": [{"a": a, "vertex": [h, k]} for a, h, k in parabolas],
    }


def curve(a, h, k, *, shift=(0.0, 0.0), jitter=0.0, shape="parabola", opens=None, points=5):
    xs = [h - 2.0 + 4.0 * i / (points - 1) for i in range(points)]
    pts = [[x + shift[0] + (jitter if i % 2 else -jitter), a * (x - h) ** 2 + k + shift[1]] for i, x in enumerate(xs)]
    return {"detected": True, "shape": shape, "opens": opens or ("up" if a > 0 else "down"), "vertex": [h + shift[0], k + shift[1]],
            "points_on_curve": pts, "label_text": ""}


def features(*curves, confidence=0.9, x_axis=True, y_axis=True):
    return {"drawing_detected": bool(curves), "recognized_type": "parabola_graph",
            "required_elements": {"x_axis": x_axis, "y_axis": y_axis, "curve": bool(curves)}, "curve_count": len(curves), "curves": list(curves),
            "missing_features": [], "incorrect_features": [], "confidence": confidence}


def verdict(spec_, feats):
    return svc.evaluate_parabola_graph(feats, spec_)["is_correct"]


@pytest.mark.parametrize("a,h,k", [(1, 0, 0), (-1, 0, 0), (2, 0, 0), (-2, 1, 5), (1, 1, -4), ("1/2", -2, 3)])
def test_correct_curves_open_up_and_down_pass(a, h, k):
    a = float(__import__("fractions").Fraction(str(a)))
    assert verdict(spec((a, h, k)), features(curve(a, h, k))) is True


def test_reasonable_hand_drawn_error_is_accepted():
    assert verdict(spec((2, 0, 0)), features(curve(2, 0, 0, jitter=0.15, shift=(0.1, -0.1)))) is True


@pytest.mark.parametrize("shift", [(2.0, 0.0), (0.0, 2.5), (-2.0, 2.0), (3.0, -3.0)])
def test_wrong_vertex_or_position_is_rejected(shift):
    assert verdict(spec((1, 0, 0)), features(curve(1, 0, 0, shift=shift))) is False


def test_reversed_opening_and_wrong_width_are_rejected():
    assert verdict(spec((1, 0, 0)), features(curve(-1, 0, 0))) is False
    assert verdict(spec((1, 0, 0)), features(curve(1, 0, 0, opens="down"))) is False
    assert verdict(spec((3, 0, 0)), features(curve(0.5, 0, 0))) is False  # far too flat


@pytest.mark.parametrize("shape", ["line", "v_shape", "other"])
def test_line_and_v_shape_are_not_parabolas(shape):
    assert verdict(spec((1, 0, 0)), features(curve(1, 0, 0, shape=shape))) is False


def test_blank_low_confidence_and_unreadable_input_never_pass():
    assert verdict(spec((1, 0, 0)), features()) is False
    assert verdict(spec((1, 0, 0)), features(curve(1, 0, 0), confidence=0.3)) is None
    assert verdict(spec((1, 0, 0)), features(curve(1, 0, 0, points=2))) is None      # too few readable points
    assert verdict(spec((1, 0, 0)), features(curve(1, 0, 0), x_axis=False, y_axis=False)) is True  # axes are printed on the canvas
    assert svc.evaluate_parabola_graph(features(curve(1, 0, 0)), {"drawing_type": "parabola_graph"})["system_error"] is True  # spec incomplete


THREE = [(3, 0, 0), (3, 2, 0), (3, 2, 4)]


def test_three_curves_on_one_canvas_are_matched_one_to_one():
    s = spec(*THREE)
    drawn = [curve(*p) for p in THREE]
    assert verdict(s, features(*drawn)) is True
    assert verdict(s, features(*reversed(drawn))) is True                       # order of drawing does not matter
    assert verdict(s, features(*drawn[:2])) is False                            # one curve missing
    assert verdict(s, features(drawn[0], drawn[0], drawn[0])) is False         # one student curve cannot satisfy three answers
    assert verdict(s, features(drawn[0], drawn[1], curve(3, 2, 4, shift=(3.0, 3.0)))) is False  # third curve misplaced
    assert verdict(s, features(*drawn, curve(3, -3, 5))) is False               # an extra curve
    assert svc.evaluate_parabola_graph(features(*drawn[:2]), s)["missing_features"] == ["parabola_curve"]


def test_a_retraced_axis_is_not_counted_as_a_curve():
    axis = {"detected": True, "shape": "line", "opens": "unknown", "vertex": None, "points_on_curve": [[-4, 0], [-2, 0], [0, 0], [2, 0], [4, 0]]}
    assert verdict(spec((1, 0, 0)), features(curve(1, 0, 0), axis)) is True
    assert verdict(spec((1, 0, 0)), features(axis)) is False                    # only an axis: nothing drawn


def test_independent_canvases_are_graded_independently():
    first, second = spec((2, 0, 0)), spec((-1, 0, 0))
    good_first, good_second = features(curve(2, 0, 0)), features(curve(-1, 0, 0))
    assert [verdict(first, good_first), verdict(second, good_second)] == [True, True]
    assert [verdict(first, good_second), verdict(second, good_first)] == [False, False]  # swapped canvases fail both


# --- prompt, validation and the end-to-end path with a mocked vision model -----------------------------------------

def test_prompt_never_leaks_the_expected_answer():
    prompt = svc.build_drawing_analysis_prompt(question_text="描繪", expected_drawing_spec=spec((7.25, 3.5, -8.75)))
    for secret in ("7.25", "3.5", "-8.75", "expected_parabolas"):
        assert secret not in prompt
    assert "points_on_curve" in prompt and "curve_count" in prompt


def test_parabola_graph_is_a_registered_type_in_service_and_checker():
    from core.checkers import free_response_drawing_checker as checker

    assert "parabola_graph" in svc.SUPPORTED_DRAWING_TYPES and "parabola_graph" in checker.SUPPORTED_DRAWING_TYPES
    assert svc.DRAWING_EVALUATOR_REGISTRY["parabola_graph"] is svc.evaluate_parabola_graph


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
    s = spec((1, 0, 0))
    assert _analyze(features(curve(1, 0, 0)), s)["is_correct"] is True
    assert _analyze(features(curve(1, 0, 0, shape="line")), s)["is_correct"] is False
    alias = {**features(curve(1, 0, 0)), "recognized_type": "parabola"}
    assert _analyze(alias, s)["is_correct"] is True
    # the model naming a drawn straight line "line_graph" is graded as a wrong shape, not as an unreadable response
    named_line = {**features(curve(1, 0, 0, shape="line")), "recognized_type": "line_graph"}
    result = _analyze(named_line, s)
    assert result["is_correct"] is False and not result.get("system_error")
