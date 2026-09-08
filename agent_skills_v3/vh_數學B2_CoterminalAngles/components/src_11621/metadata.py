from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11621"
SKILL_ID: Final[str] = "vh_數學B2_CoterminalAngles"
SOURCE_REF: Final[str] = "src_11621"
SOURCE_KIND: Final[str] = "exercise"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11621
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 19
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "identify_degree_coterminal_angles"
ANSWER_SCHEMA_KEY: Final[str] = "solution_set"
LINE_TYPE: Final[str] = "coterminal_angles"

TARGET_TASK: Final[str] = "identify_degree_coterminal_angles"
TEMPLATE_SLOT: Final[str] = "identify_degree_coterminal_angles"
PROBLEM_TYPE_ID: Final[str] = "coterminal_angles"
PRESENTATION_MODE: Final[str] = "multiple_inputs"
RESPONSE_MODE: Final[str] = "selection"
INTERACTION_TYPE: Final[str] = "selection"
ANSWER_VALUE_TYPE: Final[str] = "solution_set"
ANSWER_TYPE: Final[str] = "solution_set"
LEGACY_ANSWER_TYPE: Final[str] = "solution_set"

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "solution_set_checker",
    "equivalence_type": "set_equivalence",
    "response_mode": "selection",
    "interaction_type": "selection",
    "answer_value_type": "solution_set",
    "answer_type": "solution_set",
}

GENERATOR_READINESS: Final[str] = "blocked"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "同界角", "度數", "360k度",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "angle", "coterminal", "degree",
)
TAXONOMY_PATH: Final[str] = "trigonometry:coterminal"

BLOCK_REASON: Final[str] = "missing_ground_truth"
