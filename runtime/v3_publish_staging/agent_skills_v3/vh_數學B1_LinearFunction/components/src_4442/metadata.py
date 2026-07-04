from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4442"
SKILL_ID: Final[str] = "vh_數學B1_LinearFunction"
SOURCE_REF: Final[str] = "src_4442"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4442
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "graph_based_linear_application_inverse"
ANSWER_SCHEMA_KEY: Final[str] = "numeric_scalar"
LINE_TYPE: Final[str] = "graph_based_linear_application_inverse"

TARGET_TASK: Final[str] = "graph_based_linear_application_inverse"
TEMPLATE_SLOT: Final[str] = "graph_based_linear_application_inverse"
PROBLEM_TYPE_ID: Final[str] = "graph_based_linear_application_inverse"
PRESENTATION_MODE: Final[str] = "graph_short_answer"
RESPONSE_MODE: Final[str] = "graph_short_answer"
INTERACTION_TYPE: Final[str] = "graph_short_answer"
ANSWER_VALUE_TYPE: Final[str] = "numeric"
ANSWER_TYPE: Final[str] = "numeric"
LEGACY_ANSWER_TYPE: Final[str] = "numeric"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "numeric_checker",
    "equivalence_type": "numeric_equivalence",
    "response_mode": "graph_short_answer",
    "interaction_type": "graph_short_answer",
    "answer_value_type": "numeric",
    "answer_type": "numeric",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
