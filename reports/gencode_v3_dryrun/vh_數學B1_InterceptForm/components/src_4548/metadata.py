from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "ex_4548"
SKILL_ID: Final[str] = "vh_數學B1_InterceptForm"
SOURCE_REF: Final[str] = "ex_4548"
SOURCE_KIND: Final[str] = "ex_4548"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4548

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
LINE_TYPE: Final[str] = "intercept_form_from_intercept_sum_and_slope"

TARGET_TASK: Final[str] = "intercept_form_from_intercept_sum_and_slope"
TEMPLATE_SLOT: Final[str] = "intercept_form_from_intercept_sum_and_slope"
PROBLEM_TYPE_ID: Final[str] = "intercept_form_from_intercept_sum_and_slope"
PRESENTATION_MODE: Final[str] = "short_answer"
ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence_type": "linear_equation_equivalent",
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
