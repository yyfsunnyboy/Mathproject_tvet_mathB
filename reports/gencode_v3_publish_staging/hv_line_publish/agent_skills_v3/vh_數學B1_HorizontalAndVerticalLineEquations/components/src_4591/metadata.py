from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "ex_4591"
SKILL_ID: Final[str] = "vh_數學B1_HorizontalAndVerticalLineEquations"
SOURCE_REF: Final[str] = "ex_4591"
SOURCE_KIND: Final[str] = "ex_4591"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4591

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
LINE_TYPE: Final[str] = "vertical_line"

TARGET_TASK: Final[str] = "write_line_equation_from_point_slope"
TEMPLATE_SLOT: Final[str] = "line_equation_from_point_slope"
PROBLEM_TYPE_ID: Final[str] = "write_line_equation_from_point_slope"
PRESENTATION_MODE: Final[str] = "single_choice"
ANSWER_TYPE: Final[str] = "single_choice"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "answer_type": "single_choice",
    "module": "core.checkers.choice_label_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "斜率", "直線方程式",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_point", "linear_equation",
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:line_equation"
