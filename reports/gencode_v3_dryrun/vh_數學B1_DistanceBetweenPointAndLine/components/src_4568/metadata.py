from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4568"
SKILL_ID: Final[str] = "vh_數學B1_DistanceBetweenPointAndLine"
SOURCE_REF: Final[str] = "src_4568"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4568
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "compare_point_to_line_distances"
ANSWER_SCHEMA_KEY: Final[str] = "comparison_label"
LINE_TYPE: Final[str] = "compare_point_to_line_distances"

TARGET_TASK: Final[str] = "compare_point_to_line_distances"
TEMPLATE_SLOT: Final[str] = "compare_point_to_line_distances"
PROBLEM_TYPE_ID: Final[str] = "compare_point_to_line_distances"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "text_short"
ANSWER_TYPE: Final[str] = "text_short"
LEGACY_ANSWER_TYPE: Final[str] = "text_short"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "text_short_checker",
    "equivalence_type": "exact_string",
    "response_mode": "expression",
    "interaction_type": "expression",
    "answer_value_type": "text_short",
    "answer_type": "text_short",
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
