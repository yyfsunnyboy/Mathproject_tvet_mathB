from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "text_short"
PROBLEM_TYPE_ID = "compare_point_to_line_distances"
TEXTBOOK_EXAMPLE_ID = 4568


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type="compare_point_to_line_distances",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'target_direction': 'closer'},
    )
    component_id = str(kwargs.get("component_id") or "")
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="comparison_label",
        domain_operation="compare_point_to_line_distances",
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
