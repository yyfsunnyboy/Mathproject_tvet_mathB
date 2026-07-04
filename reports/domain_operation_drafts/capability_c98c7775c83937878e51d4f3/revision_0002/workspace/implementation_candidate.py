from __future__ import annotations

import random


def build_draw_linear_function_graph_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    slope = int(normalized.get("slope", rng.choice([-3, -2, -1, 1, 2, 3])))
    intercept = int(normalized.get("intercept", rng.randint(-4, 4)))
    if slope == 0:
        raise ValueError("linear_function_slope_must_be_nonzero")
    x_extent = 6
    endpoint_values = [
        slope * -x_extent + intercept,
        slope * x_extent + intercept,
    ]
    y_extent = max(6, *(abs(value) + 2 for value in endpoint_values))
    expression = f"{slope}x"
    if intercept > 0:
        expression += f"+{intercept}"
    elif intercept < 0:
        expression += str(intercept)
    equation = f"y={expression}"
    points = [[-x_extent, endpoint_values[0]], [x_extent, endpoint_values[1]]]
    expected_spec = {
        "drawing_type": "line_graph",
        "graph_kind": "linear_function",
        "equation": equation,
        "slope": slope,
        "y_intercept": intercept,
        "expected_line": {
            "points": points,
            "horizontal": False,
            "spans_graph_width": True,
        },
        "required_elements": ["x_axis", "y_axis", "function_line"],
        "axis_range": {
            "x_min": -x_extent,
            "x_max": x_extent,
            "y_min": -y_extent,
            "y_max": y_extent,
        },
        "tolerance": {"slope": 0.08, "y_intercept": 0.35},
    }
    return {
        "question": f"請在坐標平面上畫出一次函數 $f(x)={expression}$ 的圖形。",
        "givens": {
            "slope": slope,
            "y_intercept": intercept,
            "linear_function_equation": equation,
        },
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
            f"圖形斜率為 {slope}，y 截距為 {intercept}。",
            "取兩個符合函數式的點並連成直線。",
        ],
        "validation_facts": {
            "slope": slope,
            "y_intercept": intercept,
            "points": points,
            "collinear": True,
        },
        "topology_tags": [
            "graph_construction",
            "linear_function",
            "two_point_plotting",
        ],
    }
