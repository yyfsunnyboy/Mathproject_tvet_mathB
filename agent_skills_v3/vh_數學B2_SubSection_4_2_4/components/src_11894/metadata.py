from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11894"
SKILL_ID: Final[str] = "vh_數學B2_SubSection_4_2_4"
SOURCE_REF: Final[str] = "src_11894"
SOURCE_KIND: Final[str] = "test"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11894
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 30
DIFFICULTY_LEVEL: Final[str] = "hard"
DOMAIN_OPERATION: Final[str] = "compute_tangent_segment_length_mcq"
ANSWER_SCHEMA_KEY: Final[str] = "choice_label"
LINE_TYPE: Final[str] = "compute_tangent_segment_length_mcq"

TARGET_TASK: Final[str] = "compute_tangent_segment_length_mcq"
TEMPLATE_SLOT: Final[str] = "compute_tangent_segment_length_mcq"
PROBLEM_TYPE_ID: Final[str] = "compute_tangent_segment_length_mcq"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice"
ANSWER_TYPE: Final[str] = "choice"
LEGACY_ANSWER_TYPE: Final[str] = "choice"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.circle_plane_domain.build_circle_plane_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "single_choice",
    "interaction_type": "single_choice",
    "answer_value_type": "choice",
    "answer_type": "choice",
    "module": "core.checkers.choice_label_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
