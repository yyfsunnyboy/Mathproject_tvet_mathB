from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = 'src_4504'
SKILL_ID: Final[str] = 'vh_數學B1_VertexFormOfQuadraticFunction'
SOURCE_REF: Final[str] = 'src_4504'
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4504
IS_REQUIRED_CORE: Final[bool] = False
ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = 'quadratic_vertex_or_parameter_computation'
TARGET_TASK: Final[str] = 'quadratic_vertex_or_parameter_computation'
TEMPLATE_SLOT: Final[str] = 'quadratic_vertex_or_parameter_computation'
PROBLEM_TYPE_ID: Final[str] = 'numeric_quadratic_vertex_or_parameter_computation_single_choice'
PRESENTATION_MODE: Final[str] = 'single_choice'
RESPONSE_MODE: Final[str] = 'single_choice'
INTERACTION_TYPE: Final[str] = 'single_choice'
ANSWER_VALUE_TYPE: Final[str] = 'single_choice'
ANSWER_TYPE: Final[str] = 'single_choice'
LEGACY_ANSWER_TYPE: Final[str] = 'single_choice'
DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.gencode.slot_generators.generate_from_problem_type_spec",
)
ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": 'choice_label_checker',
    "equivalence_type": 'choice_label',
    "response_mode": 'single_choice',
    "interaction_type": 'single_choice',
    "answer_value_type": 'single_choice',
    "answer_type": 'single_choice',
    "module": "core.gencode.runtime_skill_wrapper",
}
GENERATOR_READINESS: Final[str] = "runtime_ready"
