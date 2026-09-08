from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11615"
SKILL_ID: Final[str] = "vh_數學B2_CoterminalAngles"
SOURCE_REF: Final[str] = "src_11615"
SOURCE_KIND: Final[str] = "exam"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11615
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "medium"
DOMAIN_OPERATION: Final[str] = "clock_minute_hand_rotation"
ANSWER_SCHEMA_KEY: Final[str] = "single_choice"
LINE_TYPE: Final[str] = "clock_coterminal_rotation"

TARGET_TASK: Final[str] = "clock_minute_hand_rotation"
TEMPLATE_SLOT: Final[str] = "clock_minute_hand_rotation"
PROBLEM_TYPE_ID: Final[str] = "coterminal_angles"
PRESENTATION_MODE: Final[str] = "multiple_choice"
RESPONSE_MODE: Final[str] = "selection"
INTERACTION_TYPE: Final[str] = "selection"
ANSWER_VALUE_TYPE: Final[str] = "single_choice"
ANSWER_TYPE: Final[str] = "single_choice"
LEGACY_ANSWER_TYPE: Final[str] = "single_choice"

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "single_choice_checker",
    "equivalence_type": "exact_string",
    "response_mode": "selection",
    "interaction_type": "selection",
    "answer_value_type": "single_choice",
    "answer_type": "single_choice",
}

GENERATOR_READINESS: Final[str] = "blocked"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "時鐘", "分針", "順時針", "同界角", "圓心角",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "clock", "minute_hand", "rotation", "coterminal",
)
TAXONOMY_PATH: Final[str] = "trigonometry:coterminal:application"

BLOCK_REASON: Final[str] = "missing_ground_truth"
