from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11623"
SKILL_ID: Final[str] = "vh_數學B2_CoterminalAngles"
SOURCE_REF: Final[str] = "src_11623"
SOURCE_KIND: Final[str] = "exercise"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11623
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 21
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "find_min_positive_max_negative_coterminal_radians"
ANSWER_SCHEMA_KEY: Final[str] = "multi_part"
LINE_TYPE: Final[str] = "coterminal_angles"

TARGET_TASK: Final[str] = "find_min_positive_max_negative_coterminal_radians"
TEMPLATE_SLOT: Final[str] = "find_min_positive_max_negative_coterminal_radians"
PROBLEM_TYPE_ID: Final[str] = "coterminal_angles"
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
    "最小正同界角", "最大負同界角", "2pi", "弧度",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "angle", "coterminal", "radian",
)
TAXONOMY_PATH: Final[str] = "trigonometry:coterminal"

BLOCK_REASON: Final[str] = "missing_ground_truth"
