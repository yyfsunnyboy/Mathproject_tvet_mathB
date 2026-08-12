from __future__ import annotations
from typing import Any
from core.domain.function_concept_domain import generate_function_concept_payload

SKILL_ID = 'vh_數學B1_FunctionConcept'
PROBLEM_TYPE_ID = 'free_fall_function_value_choice'
TEXTBOOK_EXAMPLE_ID = 4430
DEFAULT_COMPONENT_ID = 'src_4430'
PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID)
    return generate_function_concept_payload(
        skill_id=SKILL_ID,
        problem_type_id=PROBLEM_TYPE_ID,
        seed=seed,
        component_id=component_id,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID,
    )
