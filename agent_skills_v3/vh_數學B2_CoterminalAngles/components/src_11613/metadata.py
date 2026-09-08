from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11613"
SKILL_ID: Final[str] = "vh_數學B2_CoterminalAngles"
SOURCE_REF: Final[str] = "src_11613"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11613
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
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
    "最小正同界角", "最大負同界角", "360度", "2pi",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "angle", "coterminal", "degree", "radian",
)
TAXONOMY_PATH: Final[str] = "trigonometry:coterminal"
