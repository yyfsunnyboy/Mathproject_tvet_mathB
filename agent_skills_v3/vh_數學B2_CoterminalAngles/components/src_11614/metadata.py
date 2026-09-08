from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11614"
SKILL_ID: Final[str] = "vh_數學B2_CoterminalAngles"
SOURCE_REF: Final[str] = "src_11614"
SOURCE_KIND: Final[str] = "practice"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11614
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 9
DIFFICULTY_LEVEL: Final[str] = "medium"
DOMAIN_OPERATION: Final[str] = "find_min_positive_max_negative_coterminal"
ANSWER_SCHEMA_KEY: Final[str] = "multi_part"
LINE_TYPE: Final[str] = "coterminal_angles"

TARGET_TASK: Final[str] = "find_min_positive_max_negative_coterminal"
TEMPLATE_SLOT: Final[str] = "find_min_positive_max_negative_coterminal"
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
    "最小正同界角", "最大負同界角", "360度", "2pi",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "angle", "coterminal", "degree", "radian",
)
TAXONOMY_PATH: Final[str] = "trigonometry:coterminal"

BLOCK_REASON: Final[str] = "missing_ground_truth"
