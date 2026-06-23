from __future__ import annotations

from typing import Any

from core.domain.statistics.frequency_distribution_domain import build_frequency_distribution_table_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "frequency_table_construction_review"
TEXTBOOK_EXAMPLE_ID = 3822


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_frequency_distribution_table_matrix(
        seed=seed,
        domain_operation="frequency_table_construction_review",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={},
    )
    component_id = str(kwargs.get("component_id") or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="",
        domain_operation="frequency_table_construction_review",
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
