from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12393"
SKILL_ID: Final[str] = "gh_CommonLogarithms"
SOURCE_REF: Final[str] = "src_12393"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12393
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "count_digits_of_integer_power"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "count_digits_of_integer_power"

TARGET_TASK: Final[str] = "count_digits_of_integer_power"
TEMPLATE_SLOT: Final[str] = "count_digits_of_integer_power"
PROBLEM_TYPE_ID: Final[str] = "count_digits_of_integer_power"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "rational"
ANSWER_TYPE: Final[str] = "rational"
LEGACY_ANSWER_TYPE: Final[str] = "rational"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.algebra_exponent_laws.exponent_laws_domain.build_exponent_laws_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "rational_checker",
    "equivalence_type": "rational_equivalent",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "rational",
    "answer_type": "rational",
    "module": "core.gencode.runtime_skill_wrapper",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
