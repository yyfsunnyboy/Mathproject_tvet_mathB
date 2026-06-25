from __future__ import annotations

from typing import Any

from core.domain.statistics.frequency_distribution_domain import build_frequency_distribution_table_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "integer"
PROBLEM_TYPE_ID = "cumulative_frequency_graph_reading"
TEXTBOOK_EXAMPLE_ID = 3832
DEFAULT_COMPONENT_ID = "src_3832" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_frequency_distribution_table_matrix(
        seed=seed,
        domain_operation="cumulative_frequency_graph_reading",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'exact_task_operation': ''},
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
        domain_operation="cumulative_frequency_graph_reading",
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
