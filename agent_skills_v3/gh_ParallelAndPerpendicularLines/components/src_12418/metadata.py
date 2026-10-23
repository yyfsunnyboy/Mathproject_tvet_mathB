from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12418"
SKILL_ID: Final[str] = "gh_ParallelAndPerpendicularLines"
SOURCE_REF: Final[str] = "src_12418"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12418
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "solve_line_constructions"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "solve_line_constructions"

TARGET_TASK: Final[str] = "solve_line_constructions"
TEMPLATE_SLOT: Final[str] = "solve_line_constructions"
PROBLEM_TYPE_ID: Final[str] = "solve_line_constructions"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "coordinate_pair"
ANSWER_TYPE: Final[str] = "coordinate_pair"
LEGACY_ANSWER_TYPE: Final[str] = "coordinate_pair"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.analytic_geometry_lines.line_equations_domain.build_line_equations_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "coordinate_pair_checker",
    "equivalence_type": "coordinate_pair_equivalence",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "coordinate_pair",
    "answer_type": "coordinate_pair",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
