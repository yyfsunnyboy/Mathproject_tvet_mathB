from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = 'src_4451'
SKILL_ID: Final[str] = 'vh_數學B1_VertexFormOfQuadraticFunction'
SOURCE_REF: Final[str] = 'src_4451'
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4451
IS_REQUIRED_CORE: Final[bool] = False
ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = 'quadratic_graph_translation_fill_blank'
TARGET_TASK: Final[str] = 'quadratic_graph_translation_fill_blank'
TEMPLATE_SLOT: Final[str] = 'quadratic_graph_translation_fill_blank'
PROBLEM_TYPE_ID: Final[str] = 'text_quadratic_graph_translation_fill_blank_short_answer'
PRESENTATION_MODE: Final[str] = 'short_answer'
RESPONSE_MODE: Final[str] = 'short_answer'
INTERACTION_TYPE: Final[str] = 'short_answer'
ANSWER_VALUE_TYPE: Final[str] = 'text_short'
ANSWER_TYPE: Final[str] = 'text_short'
LEGACY_ANSWER_TYPE: Final[str] = 'text_short'
DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.gencode.slot_generators.generate_from_problem_type_spec",
)
ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": 'text_short_checker',
    "equivalence_type": 'exact_string',
    "response_mode": 'short_answer',
    "interaction_type": 'short_answer',
    "answer_value_type": 'text_short',
    "answer_type": 'text_short',
    "module": "core.gencode.runtime_skill_wrapper",
}
GENERATOR_READINESS: Final[str] = "runtime_ready"
