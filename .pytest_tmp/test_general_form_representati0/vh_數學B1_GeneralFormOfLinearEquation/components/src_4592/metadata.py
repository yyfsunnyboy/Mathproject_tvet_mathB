from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4592"
SKILL_ID: Final[str] = "vh_數學B1_GeneralFormOfLinearEquation"
SOURCE_REF: Final[str] = "src_4592"
SOURCE_KIND: Final[str] = "ex_4592"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4592
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "general_form"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "general_form"

TARGET_TASK: Final[str] = "parallel_line_slope"
TEMPLATE_SLOT: Final[str] = "parallel_line_slope"
PROBLEM_TYPE_ID: Final[str] = "parallel_line_slope"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "numeric_or_undefined"
ANSWER_TYPE: Final[str] = "numeric_or_undefined"
LEGACY_ANSWER_TYPE: Final[str] = "numeric_or_undefined"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "single_choice",
    "interaction_type": "single_choice",
    "answer_value_type": "numeric_or_undefined",
    "answer_type": "numeric_or_undefined",
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
