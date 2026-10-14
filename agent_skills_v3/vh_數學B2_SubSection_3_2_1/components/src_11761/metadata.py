from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11761"
SKILL_ID: Final[str] = "vh_數學B2_SubSection_3_2_1"
SOURCE_REF: Final[str] = "src_11761"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11761
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "solve_parallelogram_fourth_vertex"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "solve_parallelogram_fourth_vertex"

TARGET_TASK: Final[str] = "solve_parallelogram_fourth_vertex"
TEMPLATE_SLOT: Final[str] = "solve_parallelogram_fourth_vertex"
PROBLEM_TYPE_ID: Final[str] = "solve_parallelogram_fourth_vertex"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.vector_plane_domain.build_vector_plane_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "expression_checker",
    "equivalence_type": "algebraic_equivalent",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "expression",
    "answer_type": "expression",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (

)
MATH_OBJECTS: Final[tuple[str, ...]] = (

)
TAXONOMY_PATH: Final[str] = "algebra"
