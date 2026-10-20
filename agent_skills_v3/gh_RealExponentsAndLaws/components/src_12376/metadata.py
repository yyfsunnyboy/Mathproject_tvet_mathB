from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12376"
SKILL_ID: Final[str] = "gh_RealExponentsAndLaws"
SOURCE_REF: Final[str] = "src_12376"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12376
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "evaluate_conditional_exponent_values"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "evaluate_conditional_exponent_values"

TARGET_TASK: Final[str] = "evaluate_conditional_exponent_values"
TEMPLATE_SLOT: Final[str] = "evaluate_conditional_exponent_values"
PROBLEM_TYPE_ID: Final[str] = "evaluate_conditional_exponent_values"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "numeric_or_radical"
ANSWER_TYPE: Final[str] = "numeric_or_radical"
LEGACY_ANSWER_TYPE: Final[str] = "numeric_or_radical"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.algebra_exponent_laws.exponent_laws_domain.build_exponent_laws_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "expression_equivalence_checker",
    "equivalence_type": "radical_equivalence",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "numeric_or_radical",
    "answer_type": "numeric_or_radical",
    "module": "core.gencode.runtime_skill_wrapper",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
