from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12496"
SKILL_ID: Final[str] = "gh_JudgingTheRelationshipOfCircleAndLine"
SOURCE_REF: Final[str] = "src_12496"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12496
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "solve_circle_line_parameter"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "solve_circle_line_parameter"

TARGET_TASK: Final[str] = "solve_circle_line_parameter"
TEMPLATE_SLOT: Final[str] = "solve_circle_line_parameter"
PROBLEM_TYPE_ID: Final[str] = "solve_circle_line_parameter"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "inequality"
ANSWER_TYPE: Final[str] = "inequality"
LEGACY_ANSWER_TYPE: Final[str] = "inequality"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.analytic_geometry_circle_lines.circle_line_domain.build_circle_line_relations_matrix",
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
