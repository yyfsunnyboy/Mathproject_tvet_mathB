from __future__ import annotations

from typing import Any

from core.domain.statistics.table_chart_domain import build_statistical_chart_reading_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "integer"
PROBLEM_TYPE_ID = "compare_category_values"
TEXTBOOK_EXAMPLE_ID = 3885
DEFAULT_COMPONENT_ID = "src_3885" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_statistical_chart_reading_matrix(
        seed=seed,
        domain_operation="compare_category_values",
        curriculum_profile="vocational_high_b",
        difficulty_profile="hard",
        constraints={},
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="",
        domain_operation="compare_category_values",
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
