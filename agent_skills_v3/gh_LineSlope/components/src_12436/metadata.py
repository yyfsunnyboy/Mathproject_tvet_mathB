from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12436"
SKILL_ID: Final[str] = "gh_LineSlope"
SOURCE_REF: Final[str] = "src_12436"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12436
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "rank_line_slopes"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "rank_line_slopes"

TARGET_TASK: Final[str] = "rank_line_slopes"
TEMPLATE_SLOT: Final[str] = "rank_line_slopes"
PROBLEM_TYPE_ID: Final[str] = "rank_line_slopes"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.analytic_geometry_lines.line_equations_domain.build_line_equations_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "ordered_inequality_checker",
    "equivalence_type": "ordered_inequality",
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
