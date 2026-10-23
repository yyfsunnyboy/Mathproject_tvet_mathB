from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12410"
SKILL_ID: Final[str] = "gh_EquationOfALine"
SOURCE_REF: Final[str] = "src_12410"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12410
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "fill_line_property_table"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "fill_line_property_table"

TARGET_TASK: Final[str] = "fill_line_property_table"
TEMPLATE_SLOT: Final[str] = "fill_line_property_table"
PROBLEM_TYPE_ID: Final[str] = "fill_line_property_table"
PRESENTATION_MODE: Final[str] = "table_fill"
RESPONSE_MODE: Final[str] = "table_fill"
INTERACTION_TYPE: Final[str] = "table_fill"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.analytic_geometry_lines.line_equations_domain.build_line_equations_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "table_fill_checker",
    "equivalence_type": "multi_part_answer",
    "response_mode": "table_fill",
    "interaction_type": "table_fill",
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
