from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.parallel_lines_distance_domain import build_parallel_lines_distance_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "solve_parameter_from_parallel_distance"
TEXTBOOK_EXAMPLE_ID = 4579


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_parallel_lines_distance_matrix(
        seed=seed,
        domain_operation="solve_parameter_from_parallel_distance",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'parameter_sign': 'negative'},
    )
    component_id = str(kwargs.get("component_id") or "")
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="parameter_scalar",
        domain_operation="solve_parameter_from_parallel_distance",
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
