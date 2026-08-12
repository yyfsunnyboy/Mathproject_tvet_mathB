from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = 'src_4463'
SKILL_ID: Final[str] = 'vh_數學B1_QuadraticFunctionExtremum'
SOURCE_REF: Final[str] = 'src_4463'
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4463
IS_REQUIRED_CORE: Final[bool] = False
ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = 'quadratic_vertex_or_parameter_computation'
TARGET_TASK: Final[str] = 'quadratic_vertex_or_parameter_computation'
TEMPLATE_SLOT: Final[str] = 'quadratic_vertex_or_parameter_computation'
PROBLEM_TYPE_ID: Final[str] = 'integer_quadratic_vertex_or_parameter_computation'
PRESENTATION_MODE: Final[str] = 'short_answer'
RESPONSE_MODE: Final[str] = 'short_answer'
INTERACTION_TYPE: Final[str] = 'short_answer'
ANSWER_VALUE_TYPE: Final[str] = 'integer'
ANSWER_TYPE: Final[str] = 'integer'
LEGACY_ANSWER_TYPE: Final[str] = 'integer'
DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.gencode.slot_generators.generate_from_problem_type_spec",
)
ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": 'integer_checker',
    "equivalence_type": 'numeric_exact',
    "response_mode": 'short_answer',
    "interaction_type": 'short_answer',
    "answer_value_type": 'integer',
    "answer_type": 'integer',
    "module": "core.gencode.runtime_skill_wrapper",
}
GENERATOR_READINESS: Final[str] = "runtime_ready"
