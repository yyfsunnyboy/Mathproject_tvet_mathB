from __future__ import annotations

from typing import Any

from core.gencode.b2_12_component_payload import generate_b2_12_component_payload
from core.gencode.b2_12_component_specs import get_b2_12_component_spec

TEXTBOOK_EXAMPLE_ID = 11571
DEFAULT_COMPONENT_ID = "src_11571"
SPEC = get_b2_12_component_spec(TEXTBOOK_EXAMPLE_ID)
DOMAIN_OPERATION = str(SPEC["operation"])
ANSWER_TYPE = str(SPEC["answer_type"])
PRESENTATION_MODE = "single_choice" if ANSWER_TYPE == "single_choice" else ("multiple_inputs" if ANSWER_TYPE == "multi_part" else "short_answer")
PROBLEM_TYPE_ID = DOMAIN_OPERATION


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return generate_b2_12_component_payload(
        skill_id=str(SPEC["skill_id"]),
        textbook_example_id=TEXTBOOK_EXAMPLE_ID,
        domain_operation=DOMAIN_OPERATION,
        answer_type=ANSWER_TYPE,
        question_text=str(SPEC["question"]),
        calls=list(SPEC["calls"]),
        seed=seed,
        component_id=str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID),
        oracle_source=str(SPEC["oracle_source"]),
        visual_asset=str(SPEC.get("visual_asset") or ""),
    )

