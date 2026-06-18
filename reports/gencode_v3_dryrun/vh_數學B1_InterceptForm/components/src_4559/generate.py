from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "parabola_secant_parallel_line_choice"
TEXTBOOK_EXAMPLE_ID = 4559


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type="parabola_secant_parallel_line_choice",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'p': '-3', 'q': '1', 'choices': [{'label': 'A', 'text': 'y=-2x'}, {'label': 'B', 'text': 'y=\\frac{-1}{2}x'}, {'label': 'C', 'text': 'y=\\frac{1}{2}x'}, {'label': 'D', 'text': 'y=2x'}]},
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
