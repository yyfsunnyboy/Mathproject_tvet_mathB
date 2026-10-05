from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12280"
SKILL_ID: Final[str] = "gh_RationalNumbers"
SOURCE_REF: Final[str] = "src_12280"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12280
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "identify_rational_numbers"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "identify_rational_numbers"

TARGET_TASK: Final[str] = "identify_rational_numbers"
TEMPLATE_SLOT: Final[str] = "identify_rational_numbers"
PROBLEM_TYPE_ID: Final[str] = "identify_rational_numbers"
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
    "checker_key": "solution_set_checker",
    "equivalence_type": "unordered_solution_set",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "expression",
    "answer_type": "expression",
    "module": "core.checkers.solution_set_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
