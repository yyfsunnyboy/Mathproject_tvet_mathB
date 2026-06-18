from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "ex_4558"
SKILL_ID: Final[str] = "vh_數學B1_InterceptForm"
SOURCE_REF: Final[str] = "ex_4558"
SOURCE_KIND: Final[str] = "ex_4558"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4558

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
LINE_TYPE: Final[str] = "triangle_area_bisector_line_equation"

TARGET_TASK: Final[str] = "triangle_area_bisector_line_equation"
TEMPLATE_SLOT: Final[str] = "triangle_area_bisector_line_equation"
PROBLEM_TYPE_ID: Final[str] = "triangle_area_bisector_line_equation"
PRESENTATION_MODE: Final[str] = "short_answer"
ANSWER_TYPE: Final[str] = "linear_equation"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence_type": "linear_equation_equivalent",
    "answer_type": "linear_equation",
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
