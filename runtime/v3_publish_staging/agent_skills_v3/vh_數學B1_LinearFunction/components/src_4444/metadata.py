from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4444"
SKILL_ID: Final[str] = "vh_數學B1_LinearFunction"
SOURCE_REF: Final[str] = "src_4444"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4444
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "graph_intercepts_and_linear_equation"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "graph_intercepts_and_linear_equation"

TARGET_TASK: Final[str] = "graph_intercepts_and_linear_equation"
TEMPLATE_SLOT: Final[str] = "graph_intercepts_and_linear_equation"
PROBLEM_TYPE_ID: Final[str] = "graph_intercepts_and_linear_equation"
PRESENTATION_MODE: Final[str] = "graph_multi_part"
RESPONSE_MODE: Final[str] = "graph_multi_part"
INTERACTION_TYPE: Final[str] = "graph_multi_part"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "multi_part_answer_checker",
    "equivalence_type": "multi_part_answer",
    "response_mode": "graph_multi_part",
    "interaction_type": "graph_multi_part",
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
