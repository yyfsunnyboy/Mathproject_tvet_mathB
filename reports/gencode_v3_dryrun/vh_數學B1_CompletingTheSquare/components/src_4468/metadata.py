from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = 'src_4468'
SKILL_ID: Final[str] = 'vh_數學B1_CompletingTheSquare'
SOURCE_REF: Final[str] = 'src_4468'
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4468
IS_REQUIRED_CORE: Final[bool] = False
ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = 'complete_square_to_vertex_expression'
TARGET_TASK: Final[str] = 'complete_square_to_vertex_expression'
TEMPLATE_SLOT: Final[str] = 'complete_square_to_vertex_expression'
PROBLEM_TYPE_ID: Final[str] = 'expression_complete_square_to_vertex'
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
