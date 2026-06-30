from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4400"
SKILL_ID: Final[str] = "vh_數學B1_AbsoluteValueInequality"
SOURCE_REF: Final[str] = "src_4400"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4400
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "absolute_value_inequality_zero_center_basic"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "absolute_value_inequality_zero_center_basic"

TARGET_TASK: Final[str] = "absolute_value_inequality_zero_center_basic"
TEMPLATE_SLOT: Final[str] = "absolute_value_inequality_zero_center_basic"
PROBLEM_TYPE_ID: Final[str] = "absolute_value_inequality_zero_center_basic"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.absolute_value_domain.build_absolute_value_matrix",
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
    "絕對值", "絕對值方程式",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "absolute_value", "equation",
)
TAXONOMY_PATH: Final[str] = "algebra:absolute_value"
