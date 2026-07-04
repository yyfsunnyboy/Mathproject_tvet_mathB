from __future__ import annotations

import random


def build_linear_graph_feasibility_choice_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    required_intercept = int(
        normalized.get(
            "required_intercept",
            rng.choice([value for value in range(-6, 7) if value]),
        )
    )
    feasible_slopes = rng.sample([-4, -3, -2, -1, 1, 2, 3, 4], 3)
    wrong_intercept = required_intercept + rng.choice([-2, -1, 1, 2])
    candidates = [
        {
            "equation": f"y={slope}x{required_intercept:+d}",
            "slope": slope,
            "y_intercept": required_intercept,
            "feasible": True,
        }
        for slope in feasible_slopes
    ]
    impossible_slope = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    impossible_equation = f"y={impossible_slope}x{wrong_intercept:+d}"
    candidates.append(
        {
            "equation": impossible_equation,
            "slope": impossible_slope,
            "y_intercept": wrong_intercept,
            "feasible": False,
        }
    )
    rng.shuffle(candidates)
    labels = ["A", "B", "C", "D"]
    choices = [
        {
            "label": label,
            "text": candidate["equation"],
            "value": candidate["equation"],
        }
        for label, candidate in zip(labels, candidates)
    ]
    correct_label = next(
        label
        for label, candidate in zip(labels, candidates)
        if not candidate["feasible"]
    )
    return {
        "question": (
            f"下列何者不可能是函數族 $f(x)=ax{required_intercept:+d}$"
            "（a≠0）的圖形？"
        ),
        "givens": {
            "graph_condition": {
                "required_y_intercept": required_intercept,
                "slope_must_be_nonzero": True,
            }
        },
        "answer": {"correct_label": correct_label},
        "semantic_answer": impossible_equation,
        "distractors": [
            candidate["equation"] for candidate in candidates if candidate["feasible"]
        ],
        "choices": choices,
        "explanation_steps": [
            f"此函數族所有圖形的 y 截距都必須是 {required_intercept}。",
            f"{impossible_equation} 的 y 截距不符，因此不可能。",
        ],
        "validation_facts": {
            "graph_condition": {
                "required_y_intercept": required_intercept,
                "slope_must_be_nonzero": True,
            },
            "candidate_lines": candidates,
            "feasibility_by_equation": {
                candidate["equation"]: candidate["feasible"]
                for candidate in candidates
            },
            "impossible_equation": impossible_equation,
            "correct_label": correct_label,
            "choice_value_to_label": {
                choice["value"]: choice["label"] for choice in choices
            },
            "unique_choices": True,
            "unique_correct_choice": True,
        },
        "visual_spec": {
            "kind": "line_graph_choices",
            "graph_condition": {
                "required_y_intercept": required_intercept,
                "slope_must_be_nonzero": True,
            },
            "candidates": candidates,
        },
        "answer_type": "single_choice",
        "presentation_mode": "graph_single_choice",
        "topology_tags": [
            "intercept_constraint",
            "graph_family",
            "feasibility",
            "single_choice",
        ],
    }
