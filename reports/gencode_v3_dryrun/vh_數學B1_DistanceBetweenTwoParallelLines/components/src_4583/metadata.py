from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4583"
SKILL_ID: Final[str] = "vh_數學B1_DistanceBetweenTwoParallelLines"
SOURCE_REF: Final[str] = "src_4583"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4583
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "area_using_parallel_distance"
ANSWER_SCHEMA_KEY: Final[str] = "numeric_scalar"
LINE_TYPE: Final[str] = "area_using_parallel_distance"

TARGET_TASK: Final[str] = "area_using_parallel_distance"
TEMPLATE_SLOT: Final[str] = "area_using_parallel_distance"
PROBLEM_TYPE_ID: Final[str] = "area_using_parallel_distance"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "rational"
ANSWER_TYPE: Final[str] = "rational"
LEGACY_ANSWER_TYPE: Final[str] = "rational"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.parallel_lines_distance_domain.build_parallel_lines_distance_matrix",
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
