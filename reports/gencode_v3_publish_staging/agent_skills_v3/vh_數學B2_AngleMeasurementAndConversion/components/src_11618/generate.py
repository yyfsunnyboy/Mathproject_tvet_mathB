from __future__ import annotations

from typing import Any

from core.gencode.trigonometry_angle_payload import generate_trigonometry_angle_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "convert_angle_measure"
TEXTBOOK_EXAMPLE_ID = 11618
DEFAULT_COMPONENT_ID = "src_11618"
DOMAIN_OPERATION = "convert_angle_measure"
CONSTRAINTS = {
    "variant": "rad_to_deg_list",
}


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return generate_trigonometry_angle_payload(
        skill_id="vh_數學B2_AngleMeasurementAndConversion",
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
