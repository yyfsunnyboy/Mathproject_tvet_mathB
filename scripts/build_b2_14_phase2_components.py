"""Mechanically materialize the audited B2 1-4 one-example components."""
from pathlib import Path
from core.gencode.b2_14_component_specs import SPECS

ROOT=Path(__file__).resolve().parents[1]
GENERATE='''from __future__ import annotations
from typing import Any
from core.gencode.b2_14_component_payload import generate_b2_14_component_payload
from core.gencode.b2_14_component_specs import get_b2_14_component_spec

TEXTBOOK_EXAMPLE_ID = {id}
DEFAULT_COMPONENT_ID = "src_{id}"
SPEC = get_b2_14_component_spec(TEXTBOOK_EXAMPLE_ID)
DOMAIN_OPERATION = str(SPEC["operation"])
ANSWER_TYPE = str(SPEC["answer_type"])
PROBLEM_TYPE_ID = DOMAIN_OPERATION

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return generate_b2_14_component_payload(spec=SPEC, textbook_example_id=TEXTBOOK_EXAMPLE_ID, seed=seed, component_id=str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID))
'''
METADATA='''from __future__ import annotations
from typing import Final
from core.gencode.b2_14_component_specs import get_b2_14_component_spec

TEXTBOOK_EXAMPLE_ID: Final[int] = {id}
COMPONENT_ID: Final[str] = "src_{id}"
SPEC = get_b2_14_component_spec(TEXTBOOK_EXAMPLE_ID)
SKILL_ID: Final[str] = str(SPEC["skill_id"])
SOURCE_REF: Final[str] = COMPONENT_ID
SOURCE_KIND: Final[str] = "example" if SPEC["oracle_source"] == "source_provided" else "exercise"
DOMAIN_OPERATION: Final[str] = str(SPEC["operation"])
LINE_TYPE: Final[str] = DOMAIN_OPERATION
PROBLEM_TYPE_ID: Final[str] = DOMAIN_OPERATION
ANSWER_TYPE: Final[str] = str(SPEC["answer_type"])
PRESENTATION_MODE: Final[str] = "single_choice" if ANSWER_TYPE == "single_choice" else ("multiple_inputs" if ANSWER_TYPE == "multi_part" else "short_answer")
RESPONSE_MODE: Final[str] = ANSWER_TYPE
INTERACTION_TYPE: Final[str] = ANSWER_TYPE
ANSWER_VALUE_TYPE: Final[str] = ANSWER_TYPE
GENERATOR_READINESS: Final[str] = "verified"
SOURCE_FIDELITY: Final[str] = "pass"
ORACLE_SOURCE: Final[str] = str(SPEC["oracle_source"])
EXACT_CAPABILITY_READINESS: Final[str] = "pass"
DOMAIN_LIBRARY: Final[tuple[str, ...]] = ("core.registry.domain_operation_registry",)
VISUAL_REQUIRED: Final[bool] = bool(SPEC.get("visual_asset"))
'''
HINT='''from __future__ import annotations
from typing import Any
from core.gencode.b2_14_component_payload import get_b2_14_hint

def get_hint(payload: dict[str, Any] | None = None, *, stage: int = 1, **kwargs: Any) -> str:
    return get_b2_14_hint(payload, stage=stage, **kwargs)
'''

for example_id,spec in SPECS.items():
    directory=ROOT/'agent_skills_v3'/str(spec['skill_id'])/'components'/f'src_{example_id}'
    directory.mkdir(parents=True,exist_ok=True)
    (directory/'generate.py').write_text(GENERATE.format(id=example_id),encoding='utf-8')
    (directory/'metadata.py').write_text(METADATA.format(id=example_id),encoding='utf-8')
    (directory/'get_hint.py').write_text(HINT,encoding='utf-8')
print(f"created={len(SPECS)}")
