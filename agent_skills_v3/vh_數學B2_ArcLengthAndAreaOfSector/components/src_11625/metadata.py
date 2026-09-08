from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11625"
SKILL_ID: Final[str] = "vh_數學B2_ArcLengthAndAreaOfSector"
SOURCE_REF: Final[str] = "src_11625"
SOURCE_KIND: Final[str] = "advanced_exercise"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11625
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 23
DIFFICULTY_LEVEL: Final[str] = "medium"
DOMAIN_OPERATION: Final[str] = "calculate_bridge_sector_area"
ANSWER_SCHEMA_KEY: Final[str] = "single_value"
LINE_TYPE: Final[str] = "bridge_sector_area"

TARGET_TASK: Final[str] = "calculate_bridge_sector_area"
TEMPLATE_SLOT: Final[str] = "calculate_bridge_sector_area"
PROBLEM_TYPE_ID: Final[str] = "arc_length_and_area_of_sector"
PRESENTATION_MODE: Final[str] = "single_input"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "expression_equivalence_checker",
    "equivalence_type": "expression",
    "response_mode": "expression",
    "interaction_type": "expression",
    "answer_value_type": "expression",
    "answer_type": "expression",
}

GENERATOR_READINESS: Final[str] = "blocked"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "摺扇橋", "扇形面積", "圓心角", "展開角",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "sector", "bridge", "area", "radius", "angle",
)
TAXONOMY_PATH: Final[str] = "geometry:sector:application"

BLOCK_REASON: Final[str] = "missing_ground_truth"
