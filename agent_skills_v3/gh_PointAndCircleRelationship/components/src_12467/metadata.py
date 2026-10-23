from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12467"
SKILL_ID: Final[str] = "gh_PointAndCircleRelationship"
SOURCE_REF: Final[str] = "src_12467"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12467
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "solve_point_position_parameter_range"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "solve_point_position_parameter_range"

TARGET_TASK: Final[str] = "solve_point_position_parameter_range"
TEMPLATE_SLOT: Final[str] = "solve_point_position_parameter_range"
PROBLEM_TYPE_ID: Final[str] = "solve_point_position_parameter_range"
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
