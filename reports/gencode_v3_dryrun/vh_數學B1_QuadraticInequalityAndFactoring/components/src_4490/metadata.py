from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = 'src_4490'
SKILL_ID: Final[str] = 'vh_數學B1_QuadraticInequalityAndFactoring'
SOURCE_REF: Final[str] = 'src_4490'
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4490
IS_REQUIRED_CORE: Final[bool] = False
ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = 'factor_quadratic_by_cross_multiplication'
TARGET_TASK: Final[str] = 'factor_quadratic_by_cross_multiplication'
TEMPLATE_SLOT: Final[str] = 'factor_quadratic_by_cross_multiplication'
PROBLEM_TYPE_ID: Final[str] = 'integer_factor_quadratic_by_cross_multiplication'
PRESENTATION_MODE: Final[str] = 'short_answer'
RESPONSE_MODE: Final[str] = 'short_answer'
INTERACTION_TYPE: Final[str] = 'short_answer'
ANSWER_VALUE_TYPE: Final[str] = 'expression'
ANSWER_TYPE: Final[str] = 'expression'
LEGACY_ANSWER_TYPE: Final[str] = 'expression'
DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.gencode.slot_generators.generate_from_problem_type_spec",
)
ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": 'expression_checker',
    "equivalence_type": 'algebraic_equivalent',
    "response_mode": 'short_answer',
    "interaction_type": 'short_answer',
    "answer_value_type": 'expression',
    "answer_type": 'expression',
    "module": "core.gencode.runtime_skill_wrapper",
}
GENERATOR_READINESS: Final[str] = "runtime_ready"
