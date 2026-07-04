from __future__ import annotations

import random


def build_collinear_trisection_coordinate_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    point_a = tuple(normalized.get("point_a", (rng.randint(-8, 8), rng.randint(-8, 8))))
    step = tuple(
        normalized.get(
            "step",
            rng.choice(
                [
                    (dx, dy)
                    for dx in range(-4, 5)
                    for dy in range(-4, 5)
                    if (dx, dy) != (0, 0)
                ]
            ),
        )
    )
    point_d = (point_a[0] + 3 * step[0], point_a[1] + 3 * step[1])
    point_b = (
        (2 * point_a[0] + point_d[0]) // 3,
        (2 * point_a[1] + point_d[1]) // 3,
    )
    point_c = (
        (point_a[0] + 2 * point_d[0]) // 3,
        (point_a[1] + 2 * point_d[1]) // 3,
    )
    answer = f"({point_c[0]}, {point_c[1]})"
    return {
        "question": (
            f"設 A{point_a}、B、C、D{point_d} 依序在同一直線上，"
            "且 B、C 將線段 AD 三等分，求點 C 的坐標。"
        ),
        "givens": {
            "point_a": point_a,
            "point_d": point_d,
            "trisection_point_b": point_b,
            "trisection_point_c": point_c,
        },
        "answer": {"point": answer},
        "semantic_answer": answer,
        "distractors": [],
        "explanation_steps": [
            "B 以 1:2 內分 AD，所以 B=(2A+D)/3。",
            "C 以 2:1 內分 AD，所以 C=(A+2D)/3。",
        ],
        "validation_facts": {
            "point_a": point_a,
            "point_b": point_b,
            "point_c": point_c,
            "point_d": point_d,
            "ratios": {"AB:BD": "1:2", "AC:CD": "2:1"},
            "collinear": True,
            "uses_midpoint_formula": False,
        },
        "visual_spec": {
            "kind": "collinear_points",
            "ordered_points": [point_a, point_b, point_c, point_d],
        },
        "answer_type": "coordinate_pair",
        "presentation_mode": "short_answer",
        "topology_tags": [
            "coordinate_geometry",
            "collinear",
            "equal_partition",
            "internal_division",
        ],
    }
