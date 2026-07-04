from __future__ import annotations

import random


def build_graph_based_linear_model_equation_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    consumption_rate = int(normalized.get("consumption_rate", rng.randint(1, 4)))
    intercept = int(normalized.get("intercept", rng.choice([40, 50, 60, 70, 80])))
    slope = -consumption_rate
    sample_x = int(normalized.get("sample_x", rng.randint(5, 10)))
    if intercept + slope * sample_x <= 0:
        raise ValueError("graph_sample_out_of_positive_range")
    points = [[0, intercept], [sample_x, slope * sample_x + intercept]]
    equation = f"y={slope}x+{intercept}"
    general_form = f"{consumption_rate}x+y-{intercept}=0"
    return {
        "question": (
            "汽車加滿油後開始行駛，圖中 x 表示行駛距離，y 表示剩餘油量。"
            "依圖求 x 與 y 的關係式。"
        ),
        "givens": {
            "context": "driving_distance_and_remaining_fuel",
            "x_quantity": "行駛距離",
            "y_quantity": "剩餘油量",
            "graph_points": points,
        },
        "answer": {
            "canonical_form": equation,
            "general_form": general_form,
        },
        "semantic_answer": equation,
        "distractors": [],
        "explanation_steps": [
            f"由兩圖點求得斜率 {slope}。",
            f"圖形通過 (0,{intercept})，故 y 截距為 {intercept}。",
            f"所以關係式為 {equation}。",
        ],
        "validation_facts": {
            "graph_points": points,
            "slope": slope,
            "intercept": intercept,
            "equation": equation,
            "general_form": general_form,
            "context": "driving_distance_and_remaining_fuel",
        },
        "visual_spec": {
            "kind": "linear_application_graph",
            "x_label": "行駛距離",
            "y_label": "剩餘油量",
            "points": points,
            "line": {"slope": slope, "intercept": intercept},
        },
        "answer_type": "linear_equation",
        "presentation_mode": "graph_short_answer",
        "topology_tags": [
            "contextual_application",
            "graph_reading",
            "equation_from_graph",
        ],
    }
