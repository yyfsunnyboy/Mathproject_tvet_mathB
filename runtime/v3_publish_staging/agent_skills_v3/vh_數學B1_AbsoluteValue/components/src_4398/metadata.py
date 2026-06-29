from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4398"
SKILL_ID: Final[str] = "vh_數學B1_AbsoluteValue"
SOURCE_REF: Final[str] = "src_4398"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4398
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "solve_basic_absolute_value_equation"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "solve_basic_absolute_value_equation"

TARGET_TASK: Final[str] = "solve_basic_absolute_value_equation"
TEMPLATE_SLOT: Final[str] = "solve_basic_absolute_value_equation"
PROBLEM_TYPE_ID: Final[str] = "solve_basic_absolute_value_equation"
PRESENTATION_MODE: Final[str] = "multiple_inputs"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "solution_set"
ANSWER_TYPE: Final[str] = "solution_set"
LEGACY_ANSWER_TYPE: Final[str] = "solution_set"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.absolute_value_domain.build_absolute_value_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence_type": "linear_equation_equivalent",
    "response_mode": "expression",
    "interaction_type": "expression",
    "answer_value_type": "solution_set",
    "answer_type": "solution_set",
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
