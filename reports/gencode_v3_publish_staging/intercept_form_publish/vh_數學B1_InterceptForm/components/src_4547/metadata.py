from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "ex_4547"
SKILL_ID: Final[str] = "vh_數學B1_InterceptForm"
SOURCE_REF: Final[str] = "ex_4547"
SOURCE_KIND: Final[str] = "ex_4547"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4547

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
LINE_TYPE: Final[str] = "intercept_form_equation_and_triangle_area"

TARGET_TASK: Final[str] = "intercept_form_equation_and_triangle_area"
TEMPLATE_SLOT: Final[str] = "intercept_form_equation_and_triangle_area"
PROBLEM_TYPE_ID: Final[str] = "intercept_form_equation_and_triangle_area"
PRESENTATION_MODE: Final[str] = "short_answer"
ANSWER_TYPE: Final[str] = "multi_part"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "multi_part_answer_checker",
    "equivalence_type": "multi_part_answer",
    "answer_type": "multi_part",
    "module": "core.checkers.multi_part_answer_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "斜率", "直線方程式",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_point", "linear_equation",
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:line_equation"
