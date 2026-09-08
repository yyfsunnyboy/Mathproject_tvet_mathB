from __future__ import annotations

from typing import Any

from core.gencode.trigonometry_angle_payload import generate_trigonometry_angle_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "solution_set"
PROBLEM_TYPE_ID = "coterminal_angles"
TEXTBOOK_EXAMPLE_ID = 11611
DEFAULT_COMPONENT_ID = "src_11611"
DOMAIN_OPERATION = "coterminal_angles"
CONSTRAINTS = {
    "variant": "identify_which",
    "unit": "deg",
}


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return generate_trigonometry_angle_payload(
        skill_id="vh_數學B2_CoterminalAngles",
        domain_operation=DOMAIN_OPERATION,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID,
        component_id=str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID),
        seed=seed,
        extra_constraints=CONSTRAINTS,
        kwargs=kwargs,
    )
