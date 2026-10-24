from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12563"
SKILL_ID: Final[str] = "gh_LinearFunctions"
SOURCE_REF: Final[str] = "src_12563"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12563
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "solve_linear_functions"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "solve_linear_functions"

TARGET_TASK: Final[str] = "solve_linear_functions"
TEMPLATE_SLOT: Final[str] = "solve_linear_functions"
PROBLEM_TYPE_ID: Final[str] = "solve_linear_functions"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "numeric_or_radical"
ANSWER_TYPE: Final[str] = "numeric_or_radical"
LEGACY_ANSWER_TYPE: Final[str] = "numeric_or_radical"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.function_linear_quadratic.function_models_domain.build_function_models_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "expression_equivalence_checker",
    "equivalence_type": "radical_equivalence",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "numeric_or_radical",
    "answer_type": "numeric_or_radical",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
