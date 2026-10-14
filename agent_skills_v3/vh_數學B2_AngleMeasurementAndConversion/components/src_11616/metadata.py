from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11616"
SKILL_ID: Final[str] = "vh_數學B2_AngleMeasurementAndConversion"
SOURCE_REF: Final[str] = "src_11616"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11616
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "convert_angle_measure"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "convert_angle_measure"

TARGET_TASK: Final[str] = "convert_angle_measure"
TEMPLATE_SLOT: Final[str] = "convert_angle_measure"
PROBLEM_TYPE_ID: Final[str] = "convert_angle_measure"
PRESENTATION_MODE: Final[str] = "inline_table_input"
RESPONSE_MODE: Final[str] = "table_fill"
INTERACTION_TYPE: Final[str] = "table_fill"
ANSWER_VALUE_TYPE: Final[str] = "table_fill"
ANSWER_TYPE: Final[str] = "table_fill"
LEGACY_ANSWER_TYPE: Final[str] = "table_fill"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.trigonometry_angle_domain.build_trigonometry_angle_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "table_fill_checker",
    "equivalence_type": "multi_part_answer",
    "response_mode": "table_fill",
    "interaction_type": "table_fill",
    "answer_value_type": "table_fill",
    "answer_type": "table_fill",
    "module": "core.checkers",
}

GENERATOR_READINESS: Final[str] = "verified"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "angle", "radian",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "angle", "radian",
)
TAXONOMY_PATH: Final[str] = "trigonometry"
