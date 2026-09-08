from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11612"
SKILL_ID: Final[str] = "vh_數學B2_CoterminalAngles"
SOURCE_REF: Final[str] = "src_11612"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11612
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "coterminal_angles"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "coterminal_angles"

TARGET_TASK: Final[str] = "coterminal_angles"
TEMPLATE_SLOT: Final[str] = "coterminal_angles"
PROBLEM_TYPE_ID: Final[str] = "coterminal_angles"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "short_answer"
ANSWER_TYPE: Final[str] = "short_answer"
LEGACY_ANSWER_TYPE: Final[str] = "solution_set"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.trigonometry_angle_domain.build_trigonometry_angle_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "solution_set_checker",
    "equivalence_type": "unordered_solution_set",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "short_answer",
    "answer_type": "short_answer",
    "module": "core.checkers",
}

GENERATOR_READINESS: Final[str] = "blocked"
BLOCK_REASON: Final[str] = "missing_ground_truth"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "angle", "radian",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "angle", "radian",
)
TAXONOMY_PATH: Final[str] = "trigonometry"
