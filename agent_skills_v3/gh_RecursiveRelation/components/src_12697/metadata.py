from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12697"
SKILL_ID: Final[str] = "gh_RecursiveRelation"
SOURCE_REF: Final[str] = "src_12697"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12697
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "progression_three_numbers"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "progression_three_numbers"

TARGET_TASK: Final[str] = "progression_three_numbers"
TEMPLATE_SLOT: Final[str] = "progression_three_numbers"
PROBLEM_TYPE_ID: Final[str] = "progression_three_numbers"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "numeric_or_radical"
ANSWER_TYPE: Final[str] = "numeric_or_radical"
LEGACY_ANSWER_TYPE: Final[str] = "numeric_or_radical"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.sequence_progression.sequence_progression_domain.build_sequence_progression_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "expression_checker",
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
