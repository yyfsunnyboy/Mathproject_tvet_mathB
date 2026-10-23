from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12455"
SKILL_ID: Final[str] = "gh_GeneralFormOfACircle"
SOURCE_REF: Final[str] = "src_12455"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12455
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "analyze_general_circle"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "analyze_general_circle"

TARGET_TASK: Final[str] = "analyze_general_circle"
TEMPLATE_SLOT: Final[str] = "analyze_general_circle"
PROBLEM_TYPE_ID: Final[str] = "analyze_general_circle"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "inequality"
ANSWER_TYPE: Final[str] = "inequality"
LEGACY_ANSWER_TYPE: Final[str] = "inequality"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.analytic_geometry_circles.circle_equations_domain.build_circle_equations_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "inequality_solution_checker",
    "equivalence_type": "inequality_solution_equivalence",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "inequality",
    "answer_type": "inequality",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
