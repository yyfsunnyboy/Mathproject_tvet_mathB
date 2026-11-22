from __future__ import annotations

from typing import Any

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.slot_generators import generate_from_problem_type_spec

SKILL_ID = "vh_數學B1_QuadraticFunctionExtremum"
PROBLEM_TYPE_ID = "integer_compute_quadratic_vertex"
TEXTBOOK_EXAMPLE_ID = 4471
DEFAULT_COMPONENT_ID = "src_4471"
PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "multi_part"
PRESENTATION_VARIANT = "tour_revenue_multi"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    _ = level
    spec = load_problem_type_spec(SKILL_ID, PROBLEM_TYPE_ID, prefer="auto")
    if not isinstance(spec, dict):
        raise RuntimeError(f"missing_problem_type_spec:{PROBLEM_TYPE_ID}")
    spec = dict(spec)
    spec["presentation_variant"] = PRESENTATION_VARIANT
    ac = dict(spec.get("answer_contract") or {})
    ac.update(
        {
            "answer_type": "multi_part",
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "equivalence_type": "multi_part_answer",
            "presentation_mode": "short_answer",
            "answer_format_example": "5；62500",
        }
    )
    for stale in (
        "checker_selection_reason",
        "answer_semantics",
        "answer_shape",
        "selected_checker",
    ):
        ac.pop(stale, None)
    spec["answer_contract"] = ac
    payload = generate_from_problem_type_spec(SKILL_ID, spec, seed=seed)
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    if component_id:
        payload["component_id"] = component_id
    payload["textbook_example_id"] = TEXTBOOK_EXAMPLE_ID
    payload["seed"] = seed
    payload.setdefault("problem_type_id", PROBLEM_TYPE_ID)
    payload.setdefault("presentation_mode", PRESENTATION_MODE)
    payload["answer_type"] = ANSWER_TYPE
    return payload
