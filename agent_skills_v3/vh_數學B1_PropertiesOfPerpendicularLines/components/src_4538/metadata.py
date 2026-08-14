from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4538"
SKILL_ID: Final[str] = "vh_數學B1_PropertiesOfPerpendicularLines"
SOURCE_REF: Final[str] = "src_4538"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4538
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "perpendicular_slope_quadrant_choice"
ANSWER_SCHEMA_KEY: Final[str] = "choice_label"
LINE_TYPE: Final[str] = "perpendicular_slope_quadrant_choice"

TARGET_TASK: Final[str] = "perpendicular_slope_quadrant_choice"
TEMPLATE_SLOT: Final[str] = "perpendicular_slope_quadrant_choice"
PROBLEM_TYPE_ID: Final[str] = "perpendicular_slope_quadrant_choice"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice"
ANSWER_TYPE: Final[str] = "choice"
LEGACY_ANSWER_TYPE: Final[str] = "choice"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "single_choice",
    "interaction_type": "single_choice",
    "answer_value_type": "choice",
    "answer_type": "choice",
    "module": "core.checkers.choice_label_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
