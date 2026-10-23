from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12546"
SKILL_ID: Final[str] = "gh_RemainderTheorem"
SOURCE_REF: Final[str] = "src_12546"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12546
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "evaluate_polynomial_statements"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "evaluate_polynomial_statements"

TARGET_TASK: Final[str] = "evaluate_polynomial_statements"
TEMPLATE_SLOT: Final[str] = "evaluate_polynomial_statements"
PROBLEM_TYPE_ID: Final[str] = "evaluate_polynomial_statements"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "solution_set"
ANSWER_TYPE: Final[str] = "solution_set"
LEGACY_ANSWER_TYPE: Final[str] = "solution_set"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.algebra_polynomial_division.polynomial_division_domain.build_polynomial_division_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "solution_set_checker",
    "equivalence_type": "unordered_solution_set",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "solution_set",
    "answer_type": "solution_set",
    "module": "core.checkers.solution_set_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
