from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11609"
SKILL_ID: Final[str] = "vh_數學B2_ArcLengthAndAreaOfSector"
SOURCE_REF: Final[str] = "src_11609"
SOURCE_KIND: Final[str] = "practice"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11609
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 11
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "convert_deg_and_find_arc_and_area"
ANSWER_SCHEMA_KEY: Final[str] = "multi_part"
LINE_TYPE: Final[str] = "sector_arc_and_area"

TARGET_TASK: Final[str] = "convert_deg_and_find_arc_and_area"
TEMPLATE_SLOT: Final[str] = "convert_deg_and_find_arc_and_area"
PROBLEM_TYPE_ID: Final[str] = "arc_length_and_area_of_sector"
PRESENTATION_MODE: Final[str] = "multiple_inputs"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "multi_part"
ANSWER_TYPE: Final[str] = "multi_part"
LEGACY_ANSWER_TYPE: Final[str] = "multi_part"

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "multi_part_answer_checker",
    "equivalence_type": "multi_part_answer",
    "response_mode": "expression",
    "interaction_type": "expression",
    "answer_value_type": "multi_part",
    "answer_type": "multi_part",
}

GENERATOR_READINESS: Final[str] = "blocked"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "弧度", "弧長", "扇形面積", "圓心角",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "sector", "arc_length", "area", "radius", "radian",
)
TAXONOMY_PATH: Final[str] = "geometry:sector"

BLOCK_REASON: Final[str] = "missing_ground_truth"
