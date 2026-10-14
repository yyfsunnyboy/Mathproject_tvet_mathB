from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12275"
SKILL_ID: Final[str] = "gh_RationalNumbers"
SOURCE_REF: Final[str] = "src_12275"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12275
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "fraction_to_decimal_expansion"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "fraction_to_decimal_expansion"

TARGET_TASK: Final[str] = "fraction_to_decimal_expansion"
TEMPLATE_SLOT: Final[str] = "fraction_to_decimal_expansion"
PROBLEM_TYPE_ID: Final[str] = "fraction_to_decimal_expansion"
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
