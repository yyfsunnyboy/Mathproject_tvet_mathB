from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12456"
SKILL_ID: Final[str] = "gh_GeneralFormOfACircle"
SOURCE_REF: Final[str] = "src_12456"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12456
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "solve_distance_ratio_locus"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "solve_distance_ratio_locus"

TARGET_TASK: Final[str] = "solve_distance_ratio_locus"
TEMPLATE_SLOT: Final[str] = "solve_distance_ratio_locus"
PROBLEM_TYPE_ID: Final[str] = "solve_distance_ratio_locus"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "equation"
ANSWER_TYPE: Final[str] = "equation"
LEGACY_ANSWER_TYPE: Final[str] = "equation"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.analytic_geometry_circles.circle_equations_domain.build_circle_equations_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "equation_checker",
    "equivalence_type": "equation_equivalent",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "equation",
    "answer_type": "equation",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
