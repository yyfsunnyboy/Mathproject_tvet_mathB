from __future__ import annotations

import random


def build_graph_based_linear_application_inverse_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    slope = int(normalized.get("slope", rng.choice([2, 3, 4, 5])))
    intercept = int(normalized.get("intercept", rng.randint(5, 30)))
    input_min = int(normalized.get("input_min", 1))
    input_max = int(normalized.get("input_max", 12))
    if slope == 0 or input_min >= input_max:
        raise ValueError("invalid_inverse_linear_model_constraints")
    target_input = int(
        normalized.get("target_input", rng.randint(input_min, input_max))
    )
    if not input_min <= target_input <= input_max:
        raise ValueError("target_input_out_of_range")
    known_output = slope * target_input + intercept
    return {
        "question": (
            f"某方案的輸入量 x 與總費用 y 關係為 $y={slope}x+{intercept}$，"
            f"其圖形如下。若總費用為 {known_output}，求輸入量 x。"
        ),
        "givens": {
            "slope": slope,
            "intercept": intercept,
            "input_min": input_min,
            "input_max": input_max,
            "known_output": known_output,
        },
        "answer": {"canonical_form": target_input},
        "semantic_answer": target_input,
        "distractors": [],
        "explanation_steps": [
            f"由 {known_output}={slope}x+{intercept} 反解 x。",
            f"x=({known_output}-{intercept})/{slope}={target_input}。",
        ],
        "validation_facts": {
            "slope": slope,
            "intercept": intercept,
            "input_min": input_min,
            "input_max": input_max,
            "target_input": target_input,
            "known_output": known_output,
            "forward_output": slope * target_input + intercept,
            "inverse_solution": (known_output - intercept) // slope,
            "unique_solution": True,
        },
        "visual_spec": {
            "kind": "linear_application_graph",
            "x_range": [input_min, input_max],
            "line": {
                "slope": slope,
                "intercept": intercept,
                "points": [
                    [input_min, slope * input_min + intercept],
                    [input_max, slope * input_max + intercept],
                ],
            },
            "known_output": known_output,
        },
        "answer_type": "numeric",
        "presentation_mode": "graph_short_answer",
        "topology_tags": [
            "contextual_application",
            "graph_reading",
            "inverse_evaluation",
        ],
    }
