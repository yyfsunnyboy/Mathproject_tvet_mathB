from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4449"
SKILL_ID: Final[str] = "vh_數學B1_LinearFunction"
SOURCE_REF: Final[str] = "src_4449"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4449
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "draw_linear_function_graph"
ANSWER_SCHEMA_KEY: Final[str] = "drawing_spec"
LINE_TYPE: Final[str] = "draw_linear_function_graph"

TARGET_TASK: Final[str] = "draw_linear_function_graph"
TEMPLATE_SLOT: Final[str] = "draw_linear_function_graph"
PROBLEM_TYPE_ID: Final[str] = "draw_linear_function_graph"
PRESENTATION_MODE: Final[str] = "canvas"
RESPONSE_MODE: Final[str] = "canvas"
INTERACTION_TYPE: Final[str] = "canvas"
ANSWER_VALUE_TYPE: Final[str] = "drawing"
ANSWER_TYPE: Final[str] = "drawing"
LEGACY_ANSWER_TYPE: Final[str] = "drawing"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
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
