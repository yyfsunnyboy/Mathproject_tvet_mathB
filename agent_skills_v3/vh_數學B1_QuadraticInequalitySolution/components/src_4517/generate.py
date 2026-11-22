from __future__ import annotations

from typing import Any

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.slot_generators import generate_from_problem_type_spec

SKILL_ID = "vh_數學B1_QuadraticInequalitySolution"
PROBLEM_TYPE_ID = "integer_applied_quadratic_inequality_problem"
TEXTBOOK_EXAMPLE_ID = 4517
DEFAULT_COMPONENT_ID = "src_4517"
PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice_label"
PRESENTATION_VARIANT = "right_triangle_area_mcq"


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
            "answer_type": "choice_label",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "equivalence_type": "choice_label",
            "answer_equivalence": "choice_label",
            "presentation_mode": "single_choice",
            "answer_format_example": "A",
            "accepted_formats": ["A", "B", "C", "D"],
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
    spec["answer_format_hint"] = ANSWER_TYPE
    payload = generate_from_problem_type_spec(SKILL_ID, spec, seed=seed)
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    if component_id:
        payload["component_id"] = component_id
    payload["textbook_example_id"] = TEXTBOOK_EXAMPLE_ID
    payload["seed"] = seed
    payload["problem_type_id"] = PROBLEM_TYPE_ID
    payload["presentation_mode"] = PRESENTATION_MODE
    payload["answer_type"] = ANSWER_TYPE
    return payload
