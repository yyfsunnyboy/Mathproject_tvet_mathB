from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11615"
SKILL_ID: Final[str] = "vh_數學B2_CoterminalAngles"
SOURCE_REF: Final[str] = "src_11615"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 11615
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "coterminal_angles"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "coterminal_angles"

TARGET_TASK: Final[str] = "coterminal_angles"
TEMPLATE_SLOT: Final[str] = "coterminal_angles"
PROBLEM_TYPE_ID: Final[str] = "coterminal_angles"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "single_choice"
ANSWER_TYPE: Final[str] = "single_choice"
LEGACY_ANSWER_TYPE: Final[str] = "single_choice"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.trigonometry_angle_domain.build_trigonometry_angle_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "single_choice",
    "interaction_type": "single_choice",
    "answer_value_type": "single_choice",
    "answer_type": "single_choice",
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
