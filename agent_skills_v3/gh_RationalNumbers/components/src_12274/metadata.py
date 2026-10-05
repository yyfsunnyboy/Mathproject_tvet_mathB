from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12274"
SKILL_ID: Final[str] = "gh_RationalNumbers"
SOURCE_REF: Final[str] = "src_12274"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12274
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "decimal_to_simplest_fraction"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "decimal_to_simplest_fraction"

TARGET_TASK: Final[str] = "decimal_to_simplest_fraction"
TEMPLATE_SLOT: Final[str] = "decimal_to_simplest_fraction"
PROBLEM_TYPE_ID: Final[str] = "decimal_to_simplest_fraction"
PRESENTATION_MODE: Final[str] = "multiple_inputs"
RESPONSE_MODE: Final[str] = "multiple_inputs"
INTERACTION_TYPE: Final[str] = "multiple_inputs"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.number_system_rational_numbers.rational_numbers_domain.build_rational_numbers_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "multi_part_answer_checker",
    "equivalence_type": "multi_part_answer",
    "response_mode": "multiple_inputs",
    "interaction_type": "multiple_inputs",
    "answer_value_type": "expression",
    "answer_type": "expression",
    "module": "core.checkers.multi_part_answer_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
