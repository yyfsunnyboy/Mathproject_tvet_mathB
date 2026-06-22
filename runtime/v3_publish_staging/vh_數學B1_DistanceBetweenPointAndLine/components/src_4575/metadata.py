from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4575"
SKILL_ID: Final[str] = "vh_數學B1_DistanceBetweenPointAndLine"
SOURCE_REF: Final[str] = "src_4575"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4575
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "distance_from_point_to_line"
ANSWER_SCHEMA_KEY: Final[str] = "distance_scalar"
LINE_TYPE: Final[str] = "distance_from_point_to_line"

TARGET_TASK: Final[str] = "distance_from_point_to_line"
TEMPLATE_SLOT: Final[str] = "distance_from_point_to_line"
PROBLEM_TYPE_ID: Final[str] = "distance_from_point_to_line"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "rational"
ANSWER_TYPE: Final[str] = "rational"
LEGACY_ANSWER_TYPE: Final[str] = "rational"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "rational_checker",
    "equivalence_type": "rational_equivalent",
    "response_mode": "expression",
    "interaction_type": "expression",
    "answer_value_type": "rational",
    "answer_type": "rational",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "斜率", "直線方程式",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_point", "linear_equation",
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:line_equation"
