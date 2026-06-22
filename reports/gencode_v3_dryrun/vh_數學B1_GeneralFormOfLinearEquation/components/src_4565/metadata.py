from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4565"
SKILL_ID: Final[str] = "vh_數學B1_GeneralFormOfLinearEquation"
SOURCE_REF: Final[str] = "src_4565"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4565
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "slope_from_general_or_intercept_form"
ANSWER_SCHEMA_KEY: Final[str] = "slope_intercept"
LINE_TYPE: Final[str] = "slope_from_general_or_intercept_form"

TARGET_TASK: Final[str] = "slope_from_general_or_intercept_form"
TEMPLATE_SLOT: Final[str] = "slope_from_general_or_intercept_form"
PROBLEM_TYPE_ID: Final[str] = "slope_from_general_or_intercept_form"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "numeric_or_undefined"
ANSWER_TYPE: Final[str] = "numeric_or_undefined"
LEGACY_ANSWER_TYPE: Final[str] = "numeric_or_undefined"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "rational_checker",
    "equivalence_type": "rational_equivalent",
    "response_mode": "expression",
    "interaction_type": "expression",
    "answer_value_type": "numeric_or_undefined",
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
