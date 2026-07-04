from __future__ import annotations

import random
from typing import Any


def build_draw_constant_function_graph_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    constant = int(normalized.get("constant", rng.choice([value for value in range(-6, 7) if value])))
    extent = max(5, abs(constant) + 2)
    equation = f"y={constant}"
    expected_spec = {
        "drawing_type": "line_graph",
        "graph_kind": "constant_function",
        "equation": equation,
        "slope": 0,
        "y_intercept": constant,
        "expected_line": {
            "points": [[-extent, constant], [extent, constant]],
            "horizontal": True,
            "spans_graph_width": True,
        },
        "required_elements": ["x_axis", "y_axis", "function_line"],
        "axis_range": {
            "x_min": -extent,
            "x_max": extent,
            "y_min": -extent,
            "y_max": extent,
        },
        "tolerance": {"slope": 0.08, "y_intercept": 0.35},
    }
    return {
        "question": f"請在坐標平面上畫出常數函數 $f(x)={constant}$ 的圖形。",
        "givens": {"constant": constant, "constant_function_equation": equation},
        "answer": expected_spec,
        "semantic_answer": expected_spec,
        "distractors": [],
        "answer_type": "drawing",
        "presentation_mode": "canvas",
        "expected_drawing_spec": expected_spec,
        "visual_spec": {
            "kind": "cartesian_canvas",
            "axis_range": dict(expected_spec["axis_range"]),
            "show_grid": True,
            "editable": True,
        },
        "explanation_steps": [
            f"常數函數對所有 x 都有相同函數值 {constant}。",
            f"圖形是通過 (0,{constant}) 且平行 x 軸的水平直線。",
        ],
        "validation_facts": {
            "constant": constant,
            "slope": 0,
            "y_intercept": constant,
            "horizontal": True,
        },
        "topology_tags": ["graph_construction", "horizontal_line", "constant_function"],
    }


def evaluate_constant_function_line_graph(
    recognized_features: dict[str, Any],
    expected_drawing_spec: dict[str, Any],
) -> dict[str, Any]:
    required = recognized_features.get("required_elements")
    required = required if isinstance(required, dict) else {}
    line = recognized_features.get("line")
    line = line if isinstance(line, dict) else {}
    tolerance = expected_drawing_spec.get("tolerance")
    tolerance = tolerance if isinstance(tolerance, dict) else {}
    missing = [
        element
        for element in expected_drawing_spec.get("required_elements", [])
        if not required.get(element)
    ]
    if not line.get("detected"):
        missing.append("function_line")
    incorrect: list[str] = []
    try:
        if abs(float(line.get("slope")) - float(expected_drawing_spec["slope"])) > float(tolerance.get("slope", 0.08)):
            incorrect.append("slope")
        if abs(float(line.get("y_intercept")) - float(expected_drawing_spec["y_intercept"])) > float(tolerance.get("y_intercept", 0.35)):
            incorrect.append("y_intercept")
    except (TypeError, ValueError, KeyError):
        incorrect.append("line_parameters")
    if line and not line.get("spans_graph_width", False):
        incorrect.append("line_extent")
    is_correct = not missing and not incorrect
    return {
        "status": "success",
        "is_correct": is_correct,
        "score": 1.0 if is_correct else 0.0,
        "confidence": float(recognized_features.get("confidence", 1.0)),
        "missing_features": sorted(set(missing)),
        "incorrect_features": sorted(set(incorrect)),
    }
