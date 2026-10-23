from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12442"
SKILL_ID: Final[str] = "gh_LinearInequalityInTwoVariables"
SOURCE_REF: Final[str] = "src_12442"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12442
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "graph_inequality_system"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "graph_inequality_system"

TARGET_TASK: Final[str] = "graph_inequality_system"
TEMPLATE_SLOT: Final[str] = "graph_inequality_system"
PROBLEM_TYPE_ID: Final[str] = "graph_inequality_system"
PRESENTATION_MODE: Final[str] = "canvas"
RESPONSE_MODE: Final[str] = "canvas"
INTERACTION_TYPE: Final[str] = "canvas"
ANSWER_VALUE_TYPE: Final[str] = "drawing"
ANSWER_TYPE: Final[str] = "drawing"
LEGACY_ANSWER_TYPE: Final[str] = "drawing"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.analytic_geometry_lines.line_equations_domain.build_line_equations_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "free_response_drawing_checker",
    "equivalence_type": "drawing_equivalence",
    "response_mode": "canvas",
    "interaction_type": "canvas",
    "answer_value_type": "drawing",
    "answer_type": "drawing",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
