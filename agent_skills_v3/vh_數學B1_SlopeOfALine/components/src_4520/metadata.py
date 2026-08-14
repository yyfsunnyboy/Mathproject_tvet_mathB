from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4520"
SKILL_ID: Final[str] = "vh_數學B1_SlopeOfALine"
SOURCE_REF: Final[str] = "src_4520"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4520
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "classify_and_compare_figure_slopes"
ANSWER_SCHEMA_KEY: Final[str] = "multi_part_scalar"
LINE_TYPE: Final[str] = "classify_and_compare_figure_slopes"

TARGET_TASK: Final[str] = "classify_and_compare_figure_slopes"
TEMPLATE_SLOT: Final[str] = "classify_and_compare_figure_slopes"
PROBLEM_TYPE_ID: Final[str] = "classify_and_compare_figure_slopes"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "expression_checker",
    "equivalence_type": "algebraic_equivalent",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "expression",
    "answer_type": "expression",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
