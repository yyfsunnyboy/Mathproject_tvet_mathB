from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11606"
SKILL_ID: Final[str] = "vh_數學B2_AngleMeasurementAndConversion"
SOURCE_REF: Final[str] = "src_11606"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11606
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "degree_radian_mutual_conversion"
ANSWER_SCHEMA_KEY: Final[str] = "multi_part"
LINE_TYPE: Final[str] = "degree_radian_conversion"

TARGET_TASK: Final[str] = "degree_radian_mutual_conversion"
TEMPLATE_SLOT: Final[str] = "degree_radian_mutual_conversion"
PROBLEM_TYPE_ID: Final[str] = "angle_measurement_and_conversion"
PRESENTATION_MODE: Final[str] = "multiple_inputs"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "multi_part"
ANSWER_TYPE: Final[str] = "multi_part"
LEGACY_ANSWER_TYPE: Final[str] = "multi_part"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.trigonometry_angle_domain",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "multi_part_answer_checker",
    "equivalence_type": "multi_part_answer",
    "response_mode": "expression",
    "interaction_type": "expression",
    "answer_value_type": "multi_part",
    "answer_type": "multi_part",
    "module": "core.checkers.multi_part_answer_checker",
}

GENERATOR_READINESS: Final[str] = "verified"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "度度量", "弧度制", "徑度", "圓心角",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "angle", "degree", "radian",
)
TAXONOMY_PATH: Final[str] = "trigonometry:angle"
