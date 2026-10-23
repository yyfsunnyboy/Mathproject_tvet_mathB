from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12402"
SKILL_ID: Final[str] = "gh_CommonLogarithms"
SOURCE_REF: Final[str] = "src_12402"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12402
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "select_nearest_model_value"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "select_nearest_model_value"

TARGET_TASK: Final[str] = "select_nearest_model_value"
TEMPLATE_SLOT: Final[str] = "select_nearest_model_value"
PROBLEM_TYPE_ID: Final[str] = "select_nearest_model_value"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice_label"
ANSWER_TYPE: Final[str] = "choice_label"
LEGACY_ANSWER_TYPE: Final[str] = "choice_label"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.algebra_exponent_laws.exponent_laws_domain.build_exponent_laws_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "single_choice",
    "interaction_type": "single_choice",
    "answer_value_type": "choice_label",
    "answer_type": "choice_label",
    "module": "core.checkers.choice_label_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
