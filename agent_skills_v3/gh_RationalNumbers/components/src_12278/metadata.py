from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12278"
SKILL_ID: Final[str] = "gh_RationalNumbers"
SOURCE_REF: Final[str] = "src_12278"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12278
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "construct_rational_between_bounds"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "construct_rational_between_bounds"

TARGET_TASK: Final[str] = "construct_rational_between_bounds"
TEMPLATE_SLOT: Final[str] = "construct_rational_between_bounds"
PROBLEM_TYPE_ID: Final[str] = "construct_rational_between_bounds"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.number_system_rational_numbers.rational_numbers_domain.build_rational_numbers_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "rational_between_bounds_checker",
    "equivalence_type": "strict_between_bounds",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "expression",
    "answer_type": "expression",
    "module": "core.checkers.rational_between_bounds_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
