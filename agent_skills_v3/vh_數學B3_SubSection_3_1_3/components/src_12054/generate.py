from __future__ import annotations

from typing import Any

from core.domain.linear_inequality_planning_domain import build_linear_inequality_planning_matrix
from core.gencode.linear_inequality_planning_capability_adapter import adapt_linear_inequality_planning_matrix

PRESENTATION_MODE = 'single_choice'
ANSWER_TYPE = 'single_choice'
PROBLEM_TYPE_ID = 'system_dependent_value'
TEXTBOOK_EXAMPLE_ID = 12054
DEFAULT_COMPONENT_ID = "src_12054"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_linear_inequality_planning_matrix(
        seed,
        {
            "skill_id": 'vh_數學B3_SubSection_3_1_3',
            "problem_type_id": PROBLEM_TYPE_ID,
            "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
            "presentation": PRESENTATION_MODE,
        },
    )
    payload = adapt_linear_inequality_planning_matrix(
        matrix,
        domain_operation=PROBLEM_TYPE_ID,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        component_id=str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID),
        textbook_example_id=TEXTBOOK_EXAMPLE_ID,
        seed=seed,
    )
    payload["component_id"] = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID)
    payload["seed"] = seed
    payload["domain_matrix"] = matrix
    payload["skill_id"] = 'vh_數學B3_SubSection_3_1_3'
    return payload
