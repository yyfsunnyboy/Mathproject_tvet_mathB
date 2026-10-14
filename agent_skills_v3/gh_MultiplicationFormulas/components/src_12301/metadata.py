from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12301"
SKILL_ID: Final[str] = "gh_MultiplicationFormulas"
SOURCE_REF: Final[str] = "src_12301"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12301
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "evaluate_product_under_power_relation"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "evaluate_product_under_power_relation"

TARGET_TASK: Final[str] = "evaluate_product_under_power_relation"
TEMPLATE_SLOT: Final[str] = "evaluate_product_under_power_relation"
PROBLEM_TYPE_ID: Final[str] = "evaluate_product_under_power_relation"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "rational"
ANSWER_TYPE: Final[str] = "rational"
LEGACY_ANSWER_TYPE: Final[str] = "rational"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.algebra_multiplication_formulas.multiplication_formulas_domain.build_multiplication_formulas_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "rational_checker",
    "equivalence_type": "rational_equivalent",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "rational",
    "answer_type": "rational",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
