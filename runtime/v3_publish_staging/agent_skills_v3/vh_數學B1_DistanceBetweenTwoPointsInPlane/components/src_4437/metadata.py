from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4437"
SKILL_ID: Final[str] = "vh_數學B1_DistanceBetweenTwoPointsInPlane"
SOURCE_REF: Final[str] = "src_4437"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4437
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "solve_unknown_coordinate_from_two_point_distance"
ANSWER_SCHEMA_KEY: Final[str] = "parameter_solution_set"
LINE_TYPE: Final[str] = "solve_unknown_coordinate_from_two_point_distance"

TARGET_TASK: Final[str] = "solve_unknown_coordinate_from_two_point_distance"
TEMPLATE_SLOT: Final[str] = "solve_unknown_coordinate_from_two_point_distance"
PROBLEM_TYPE_ID: Final[str] = "solve_unknown_coordinate_from_two_point_distance"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.distance_between_two_points_domain.build_distance_between_two_points_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "expression_checker",
    "equivalence_type": "algebraic_equivalent",
    "response_mode": "expression",
    "interaction_type": "expression",
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
