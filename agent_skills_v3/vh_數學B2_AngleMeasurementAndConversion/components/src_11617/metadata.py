from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11617"
SKILL_ID: Final[str] = "vh_數學B2_AngleMeasurementAndConversion"
SOURCE_REF: Final[str] = "src_11617"
SOURCE_KIND: Final[str] = "textbook_exercise"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11617
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "convert_degree_to_radian"
ANSWER_SCHEMA_KEY: Final[str] = "multi_part"
LINE_TYPE: Final[str] = "angle_conversion"

TARGET_TASK: Final[str] = "convert_degree_to_radian_multi"
TEMPLATE_SLOT: Final[str] = "convert_degree_to_radian_multi"
PROBLEM_TYPE_ID: Final[str] = "angle_measurement_and_conversion"
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
    "角的度量與換算", "度度量轉弧度量",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "angle", "radian", "degree",
)
TAXONOMY_PATH: Final[str] = "trigonometry:angle_measurement"

BLOCK_REASON: Final[str] = "missing_ground_truth"
