from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4607"
SKILL_ID: Final[str] = "vh_數學B1_DistanceBetweenPointAndLine"
SOURCE_REF: Final[str] = "src_4607"
SOURCE_KIND: Final[str] = "test"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4607
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 30
DIFFICULTY_LEVEL: Final[str] = "hard"
DOMAIN_OPERATION: Final[str] = "distance_from_point_to_line_parameter_single_choice_scalar"
ANSWER_SCHEMA_KEY: Final[str] = "parameter_scalar"
LINE_TYPE: Final[str] = "distance_from_point_to_line_parameter_single_choice_scalar"

TARGET_TASK: Final[str] = "distance_from_point_to_line_parameter_single_choice_scalar"
TEMPLATE_SLOT: Final[str] = "distance_from_point_to_line_parameter_single_choice_scalar"
PROBLEM_TYPE_ID: Final[str] = "distance_from_point_to_line_parameter_single_choice_scalar"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice_label"
ANSWER_TYPE: Final[str] = "choice_label"
LEGACY_ANSWER_TYPE: Final[str] = "single_choice"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "single_choice",
    "interaction_type": "single_choice",
    "answer_value_type": "choice_label",
    "answer_type": "choice_label",
    "module": "core.checkers.choice_label_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "斜率", "直線方程式",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_point", "linear_equation",
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:line_equation"
