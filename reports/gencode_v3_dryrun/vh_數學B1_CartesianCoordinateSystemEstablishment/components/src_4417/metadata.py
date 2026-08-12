from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4417"
SKILL_ID: Final[str] = "vh_數學B1_CartesianCoordinateSystemEstablishment"
SOURCE_REF: Final[str] = "src_4417"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4417
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "cartesian_coordinate_quadrant_symbol_reasoning"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "cartesian_coordinate_quadrant_symbol_reasoning"

TARGET_TASK: Final[str] = "cartesian_coordinate_quadrant_symbol_reasoning"
TEMPLATE_SLOT: Final[str] = "cartesian_coordinate_quadrant_symbol_reasoning"
PROBLEM_TYPE_ID: Final[str] = "cartesian_coordinate_quadrant_symbol_reasoning"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "choice"
INTERACTION_TYPE: Final[str] = "choice"
ANSWER_VALUE_TYPE: Final[str] = "choice_label"
ANSWER_TYPE: Final[str] = "choice"
LEGACY_ANSWER_TYPE: Final[str] = "choice"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.cartesian_coordinate_domain.build_cartesian_coordinate_matrix",
)

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
