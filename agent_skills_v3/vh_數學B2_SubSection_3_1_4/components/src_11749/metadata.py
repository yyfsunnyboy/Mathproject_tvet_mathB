from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11749"
SKILL_ID: Final[str] = "vh_數學B2_SubSection_3_1_4"
SOURCE_REF: Final[str] = "src_11749"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11749
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "construct_linear_combination_choice"
ANSWER_SCHEMA_KEY: Final[str] = "choice_label"
LINE_TYPE: Final[str] = "construct_linear_combination_choice"

TARGET_TASK: Final[str] = "construct_linear_combination_choice"
TEMPLATE_SLOT: Final[str] = "construct_linear_combination_choice"
PROBLEM_TYPE_ID: Final[str] = "construct_linear_combination_choice"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice_label"
ANSWER_TYPE: Final[str] = "choice_label"
LEGACY_ANSWER_TYPE: Final[str] = "choice_label"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.vector_plane_domain.build_vector_plane_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "expression_checker",
    "equivalence_type": "algebraic_equivalent",
    "response_mode": "single_choice",
    "interaction_type": "single_choice",
    "answer_value_type": "choice_label",
    "answer_type": "choice_label",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (

)
MATH_OBJECTS: Final[tuple[str, ...]] = (

)
TAXONOMY_PATH: Final[str] = "algebra"
