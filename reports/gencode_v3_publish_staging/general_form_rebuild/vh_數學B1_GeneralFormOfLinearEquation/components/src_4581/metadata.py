from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "ex_4581"
SKILL_ID: Final[str] = "vh_數學B1_GeneralFormOfLinearEquation"
SOURCE_REF: Final[str] = "ex_4581"
SOURCE_KIND: Final[str] = "ex_4581"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4581

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
LINE_TYPE: Final[str] = "slope_from_general_form"

TARGET_TASK: Final[str] = "slope_from_general_form"
TEMPLATE_SLOT: Final[str] = "line_equation_from_point_slope"
PROBLEM_TYPE_ID: Final[str] = "slope_from_general_form"
PRESENTATION_MODE: Final[str] = "short_answer"
ANSWER_TYPE: Final[str] = "numeric_or_undefined"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "rational_checker",
    "equivalence_type": "rational_equivalent",
    "answer_type": "numeric_or_undefined",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "斜率", "直線方程式",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_point", "linear_equation",
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:line_equation"
