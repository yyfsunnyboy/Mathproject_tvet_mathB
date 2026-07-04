from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4428"
SKILL_ID: Final[str] = "vh_數學B1_MidpointCoordinates"
SOURCE_REF: Final[str] = "src_4428"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4428
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "midpoint_distance_from_origin"
ANSWER_SCHEMA_KEY: Final[str] = "distance_scalar"
LINE_TYPE: Final[str] = "midpoint_distance_from_origin"

TARGET_TASK: Final[str] = "midpoint_distance_from_origin"
TEMPLATE_SLOT: Final[str] = "midpoint_distance_from_origin"
PROBLEM_TYPE_ID: Final[str] = "midpoint_distance_from_origin"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "radical_scalar"
ANSWER_TYPE: Final[str] = "radical_scalar"
LEGACY_ANSWER_TYPE: Final[str] = "radical_scalar"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.gencode.division_point_slot_engine.generate_division_point_payload",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "coordinate_pair_checker",
    "equivalence_type": "coordinate_pair_equivalence",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "radical_scalar",
    "answer_type": "radical_scalar",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
