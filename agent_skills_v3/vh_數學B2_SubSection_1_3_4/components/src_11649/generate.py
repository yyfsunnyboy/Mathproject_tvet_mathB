from __future__ import annotations
from typing import Any
from core.gencode.b2_13_component_payload import generate_b2_13_component_payload
from core.gencode.b2_13_component_specs import get_b2_13_component_spec

TEXTBOOK_EXAMPLE_ID = 11649
DEFAULT_COMPONENT_ID = "src_11649"
SPEC = get_b2_13_component_spec(TEXTBOOK_EXAMPLE_ID)
DOMAIN_OPERATION = str(SPEC["operation"])
ANSWER_TYPE = str(SPEC["answer_type"])
PROBLEM_TYPE_ID = DOMAIN_OPERATION

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return generate_b2_13_component_payload(spec=SPEC, textbook_example_id=TEXTBOOK_EXAMPLE_ID, seed=seed, component_id=str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID))

