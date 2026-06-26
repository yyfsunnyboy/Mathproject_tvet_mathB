from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4553"
SKILL_ID: Final[str] = "vh_數學B1_HorizontalAndVerticalLineEquations"
SOURCE_REF: Final[str] = "src_4553"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4553
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "horizontal_line"
ANSWER_SCHEMA_KEY: Final[str] = "line_equation"
LINE_TYPE: Final[str] = "horizontal_line"

TARGET_TASK: Final[str] = "horizontal_line"
TEMPLATE_SLOT: Final[str] = "horizontal_line"
PROBLEM_TYPE_ID: Final[str] = "write_line_equation_from_point_slope"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence_type": "linear_equation_equivalent",
    "response_mode": "expression",
    "interaction_type": "expression",
    "answer_value_type": "expression",
    "answer_type": "expression",
    "module": "core.checkers.linear_equation_equivalent_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "斜率", "直線方程式",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_point", "linear_equation",
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:line_equation"
