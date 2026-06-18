from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "linear_equation"
PROBLEM_TYPE_ID = "triangle_area_bisector_line_equation"
TEXTBOOK_EXAMPLE_ID = 4558


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type="triangle_area_bisector_line_equation",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'vertex': {'label': 'B', 'x': '7', 'y': '-3'}, 'edge_p1': {'label': 'A', 'x': '4', 'y': '2'}, 'edge_p2': {'label': 'C', 'x': '2', 'y': '-2'}},
    )
    component_id = str(kwargs.get("component_id") or "")
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
