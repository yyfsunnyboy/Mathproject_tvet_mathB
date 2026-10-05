from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12314"
SKILL_ID: Final[str] = "gh_OperationsOfRadicalsAndFractions"
SOURCE_REF: Final[str] = "src_12314"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12314
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "optimize_by_am_gm"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "optimize_by_am_gm"

TARGET_TASK: Final[str] = "optimize_by_am_gm"
TEMPLATE_SLOT: Final[str] = "optimize_by_am_gm"
PROBLEM_TYPE_ID: Final[str] = "optimize_by_am_gm"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "rational"
ANSWER_TYPE: Final[str] = "rational"
LEGACY_ANSWER_TYPE: Final[str] = "rational"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.algebra_radical_operations.radical_operations_domain.build_radical_operations_matrix",
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
