from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = 'src_4493'
SKILL_ID: Final[str] = 'vh_數學B1_QuadraticInequalitySolution'
SOURCE_REF: Final[str] = 'src_4493'
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4493
IS_REQUIRED_CORE: Final[bool] = False
ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = 'reverse_quadratic_inequality_coefficients'
TARGET_TASK: Final[str] = 'reverse_quadratic_inequality_coefficients'
TEMPLATE_SLOT: Final[str] = 'reverse_quadratic_inequality_coefficients'
PROBLEM_TYPE_ID: Final[str] = 'integer_reverse_quadratic_inequality_coefficients'
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
