from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4542"
SKILL_ID: Final[str] = "vh_數學B1_PointSlopeForm"
SOURCE_REF: Final[str] = "src_4542"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4542

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
LINE_TYPE: Final[str] = "perpendicular_bisector"

TARGET_TASK: Final[str] = "write_perpendicular_bisector_from_two_points"
TEMPLATE_SLOT: Final[str] = "perpendicular_bisector_from_two_points"
PROBLEM_TYPE_ID: Final[str] = "write_perpendicular_bisector_from_two_points"
PRESENTATION_MODE: Final[str] = "short_answer"
ANSWER_TYPE: Final[str] = "equation"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.gencode.slot_generators.generate_from_problem_type_spec",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence_type": "linear_equation_equivalent",
    "answer_type": "equation",
    "module": "core.gencode.runtime_skill_wrapper",
}

GENERATOR_READINESS: Final[str] = "runtime_ready"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "中點", "垂直斜率", "直線方程式",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_point", "linear_equation", "segment",
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:line_equation"
