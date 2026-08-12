from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4510"
SKILL_ID: Final[str] = "vh_數學B1_CartesianCoordinateSystemEstablishment"
SOURCE_REF: Final[str] = "src_4510"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4510
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "quadrant_statement_reasoning_choice"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "quadrant_statement_reasoning_choice"

TARGET_TASK: Final[str] = "quadrant_statement_reasoning_choice"
TEMPLATE_SLOT: Final[str] = "quadrant_statement_reasoning_choice"
PROBLEM_TYPE_ID: Final[str] = "quadrant_statement_reasoning_choice"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "choice"
INTERACTION_TYPE: Final[str] = "choice"
ANSWER_VALUE_TYPE: Final[str] = "choice_label"
ANSWER_TYPE: Final[str] = "choice"
LEGACY_ANSWER_TYPE: Final[str] = "choice"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = ()

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "choice",
    "interaction_type": "choice",
    "answer_value_type": "choice_label",
    "answer_type": "choice",
    "module": "core.checkers.choice_label_checker",
}

GENERATOR_READINESS: Final[str] = "verified"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "直角坐標系", "象限與符號",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_plane", "quadrant",
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:cartesian_coordinate"
