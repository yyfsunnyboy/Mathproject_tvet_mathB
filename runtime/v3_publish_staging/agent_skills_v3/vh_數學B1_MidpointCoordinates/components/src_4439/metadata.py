from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4439"
SKILL_ID: Final[str] = "vh_數學B1_MidpointCoordinates"
SOURCE_REF: Final[str] = "src_4439"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4439
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "compute_midpoint_coordinates"
ANSWER_SCHEMA_KEY: Final[str] = "coordinate_pair"
LINE_TYPE: Final[str] = "compute_midpoint_coordinates"

TARGET_TASK: Final[str] = "compute_midpoint_coordinates"
TEMPLATE_SLOT: Final[str] = "compute_midpoint_coordinates"
PROBLEM_TYPE_ID: Final[str] = "compute_midpoint_coordinates"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "coordinate_pair"
ANSWER_TYPE: Final[str] = "coordinate_pair"
LEGACY_ANSWER_TYPE: Final[str] = "coordinate_pair"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.gencode.division_point_slot_engine.generate_division_point_payload",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "coordinate_pair_checker",
    "equivalence_type": "coordinate_pair_equivalence",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "coordinate_pair",
    "answer_type": "coordinate_pair",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
