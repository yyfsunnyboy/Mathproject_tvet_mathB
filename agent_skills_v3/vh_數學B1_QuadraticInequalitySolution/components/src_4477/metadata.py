from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = 'src_4477'
SKILL_ID: Final[str] = 'vh_數學B1_QuadraticInequalitySolution'
SOURCE_REF: Final[str] = 'src_4477'
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4477
IS_REQUIRED_CORE: Final[bool] = False
ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = 'solve_quadratic_inequality'
TARGET_TASK: Final[str] = 'solve_quadratic_inequality'
TEMPLATE_SLOT: Final[str] = 'solve_quadratic_inequality'
PROBLEM_TYPE_ID: Final[str] = 'integer_solve_quadratic_inequality'
PRESENTATION_MODE: Final[str] = 'short_answer'
RESPONSE_MODE: Final[str] = 'short_answer'
INTERACTION_TYPE: Final[str] = 'short_answer'
ANSWER_VALUE_TYPE: Final[str] = 'interval'
ANSWER_TYPE: Final[str] = 'interval'
LEGACY_ANSWER_TYPE: Final[str] = 'interval'
DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.gencode.slot_generators.generate_from_problem_type_spec",
)
ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": 'interval_checker',
    "equivalence_type": 'interval_equivalence',
    "response_mode": 'short_answer',
    "interaction_type": 'short_answer',
    "answer_value_type": 'interval',
    "answer_type": 'interval',
    "module": "core.gencode.runtime_skill_wrapper",
}
GENERATOR_READINESS: Final[str] = "runtime_ready"
