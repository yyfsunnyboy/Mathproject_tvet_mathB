from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11616"
SKILL_ID: Final[str] = "vh_數學B2_AngleMeasurementAndConversion"
SOURCE_REF: Final[str] = "src_11616"
SOURCE_KIND: Final[str] = "textbook_exercise"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11616
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "fill_in_angle_conversion_table"
ANSWER_SCHEMA_KEY: Final[str] = "table_fill_in"
LINE_TYPE: Final[str] = "angle_conversion_table"

TARGET_TASK: Final[str] = "fill_in_angle_conversion_table"
TEMPLATE_SLOT: Final[str] = "fill_in_angle_conversion_table"
PROBLEM_TYPE_ID: Final[str] = "angle_measurement_and_conversion"
PRESENTATION_MODE: Final[str] = "table_fill_in"
RESPONSE_MODE: Final[str] = "table"
INTERACTION_TYPE: Final[str] = "table"
ANSWER_VALUE_TYPE: Final[str] = "table"
ANSWER_TYPE: Final[str] = "table"
LEGACY_ANSWER_TYPE: Final[str] = "table"

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "table_fill_in_checker",
    "equivalence_type": "table_exact",
}

GENERATOR_READINESS: Final[str] = "blocked"
BLOCK_REASON: Final[str] = "source_incomplete"
BLOCK_DETAILS: Final[str] = "Textbook table has 7 unfilled blanks without official answer key in DB; interactive table schema not supported."

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "常用特別角的度度量與弧度量對照表",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "table", "angle", "radian",
)
TAXONOMY_PATH: Final[str] = "trigonometry:angle_measurement"
