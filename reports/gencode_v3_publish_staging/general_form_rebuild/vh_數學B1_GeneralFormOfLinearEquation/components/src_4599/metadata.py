from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "ex_4599"
SKILL_ID: Final[str] = "vh_數學B1_GeneralFormOfLinearEquation"
SOURCE_REF: Final[str] = "ex_4599"
SOURCE_KIND: Final[str] = "ex_4599"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4599

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
LINE_TYPE: Final[str] = "perpendicular_bisector_application"

TARGET_TASK: Final[str] = "perpendicular_bisector_application"
TEMPLATE_SLOT: Final[str] = "line_equation_from_point_slope"
PROBLEM_TYPE_ID: Final[str] = "perpendicular_bisector_application"
PRESENTATION_MODE: Final[str] = "single_choice"
ANSWER_TYPE: Final[str] = "linear_equation"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "answer_type": "linear_equation",
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
