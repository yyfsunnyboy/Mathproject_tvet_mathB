from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12332"
SKILL_ID: Final[str] = "gh_LinearInequalitiesWithAbsoluteValue"
SOURCE_REF: Final[str] = "src_12332"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12332
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "solve_absolute_value_inequalities"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "solve_absolute_value_inequalities"

TARGET_TASK: Final[str] = "solve_absolute_value_inequalities"
TEMPLATE_SLOT: Final[str] = "solve_absolute_value_inequalities"
PROBLEM_TYPE_ID: Final[str] = "solve_absolute_value_inequalities"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "inequality_solution"
ANSWER_TYPE: Final[str] = "inequality_solution"
LEGACY_ANSWER_TYPE: Final[str] = "inequality_solution"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.algebra_absolute_value_relations.absolute_value_relations_domain.build_absolute_value_relations_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "inequality_solution_checker",
    "equivalence_type": "interval_equivalence",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "inequality_solution",
    "answer_type": "inequality_solution",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
