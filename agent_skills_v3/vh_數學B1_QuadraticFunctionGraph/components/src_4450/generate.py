from __future__ import annotations

from typing import Any

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.slot_generators import generate_from_problem_type_spec

SKILL_ID = 'vh_數學B1_QuadraticFunctionGraph'
PROBLEM_TYPE_ID = 'integer_quadratic_graph_translation_fill_blank'
TEXTBOOK_EXAMPLE_ID = 4450
DEFAULT_COMPONENT_ID = 'src_4450'
PRESENTATION_MODE = 'short_answer'
ANSWER_TYPE = 'text_short'


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    spec = load_problem_type_spec(SKILL_ID, PROBLEM_TYPE_ID, prefer="auto")
    if not isinstance(spec, dict):
        raise RuntimeError(f"missing_problem_type_spec:{PROBLEM_TYPE_ID}")
    payload = generate_from_problem_type_spec(SKILL_ID, spec, seed=seed)
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    if component_id:
        payload["component_id"] = component_id
    payload["textbook_example_id"] = TEXTBOOK_EXAMPLE_ID
    payload["seed"] = seed
    payload.setdefault("problem_type_id", PROBLEM_TYPE_ID)
    payload.setdefault("presentation_mode", PRESENTATION_MODE)
    payload.setdefault("answer_type", ANSWER_TYPE)
    return payload
