from __future__ import annotations

import random


def build_linear_equation_from_two_points_choice_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    line_kind = str(normalized.get("line_kind", rng.choice(["vertical", "horizontal", "oblique"])))
    offset = int(normalized.get("offset", rng.choice([value for value in range(-6, 7) if value])))
    if line_kind == "vertical":
        point_1, point_2 = (offset, -2), (offset, 3)
        slope = None
        equation = f"x={offset}"
        option_values = [equation, f"y={offset}", f"x={offset + 1}", f"y={offset + 1}"]
    elif line_kind == "horizontal":
        point_1, point_2 = (-2, offset), (3, offset)
        slope = 0
        equation = f"y={offset}"
        option_values = [equation, f"x={offset}", f"y={offset + 1}", f"x={offset + 1}"]
    elif line_kind == "oblique":
        slope = int(normalized.get("slope", rng.choice([-3, -2, -1, 1, 2, 3])))
        point_1 = (-2, slope * -2 + offset)
        point_2 = (3, slope * 3 + offset)
        expression = f"{slope}x"
        if offset > 0:
            expression += f"+{offset}"
        elif offset < 0:
            expression += str(offset)
        equation = f"y={expression}"
        option_values = [
            equation,
            f"y={slope + 1}x{offset:+d}",
            f"y={slope}x{offset + 1:+d}",
            f"y={-slope}x{offset:+d}",
        ]
    else:
        raise ValueError("unsupported_line_kind")
    if len(set(option_values)) != 4:
        raise ValueError("choice_generation_not_unique")
    rng.shuffle(option_values)
    labels = ["A", "B", "C", "D"]
    choices = [
        {"label": label, "text": value, "value": value}
        for label, value in zip(labels, option_values)
    ]
    correct_label = labels[option_values.index(equation)]
    return {
        "question": f"通過點 {point_1}、{point_2} 的直線方程式為何？",
        "givens": {"point_1": point_1, "point_2": point_2},
        "answer": {"correct_label": correct_label},
        "semantic_answer": equation,
        "distractors": [value for value in option_values if value != equation],
        "choices": choices,
        "explanation_steps": ["由兩點判斷直線型態與斜率，再代入其中一點求方程式。"],
        "validation_facts": {
            "point_1": point_1,
            "point_2": point_2,
            "line_kind": line_kind,
            "slope": slope,
            "equation": equation,
            "correct_label": correct_label,
            "choice_value_to_label": {
                choice["value"]: choice["label"] for choice in choices
            },
            "unique_choices": True,
            "unique_correct_choice": True,
        },
        "visual_spec": {"kind": "no_visual"},
        "answer_type": "single_choice",
        "presentation_mode": "single_choice",
        "topology_tags": ["two_points", "slope_then_intercept", "single_choice"],
    }
