from __future__ import annotations

from typing import Final

from core.gencode.b2_12_component_specs import get_b2_12_component_spec

TEXTBOOK_EXAMPLE_ID: Final[int] = 11560
COMPONENT_ID: Final[str] = "src_11560"
SPEC = get_b2_12_component_spec(TEXTBOOK_EXAMPLE_ID)
SKILL_ID: Final[str] = str(SPEC["skill_id"])
SOURCE_REF: Final[str] = COMPONENT_ID
SOURCE_KIND: Final[str] = "example" if TEXTBOOK_EXAMPLE_ID <= 11565 else "exercise"
DOMAIN_OPERATION: Final[str] = str(SPEC["operation"])
LINE_TYPE: Final[str] = DOMAIN_OPERATION
PROBLEM_TYPE_ID: Final[str] = DOMAIN_OPERATION
ANSWER_TYPE: Final[str] = str(SPEC["answer_type"])
PRESENTATION_MODE: Final[str] = "single_choice" if ANSWER_TYPE == "single_choice" else ("multiple_inputs" if ANSWER_TYPE == "multi_part" else "short_answer")
RESPONSE_MODE: Final[str] = ANSWER_TYPE
INTERACTION_TYPE: Final[str] = ANSWER_TYPE
ANSWER_VALUE_TYPE: Final[str] = ANSWER_TYPE
GENERATOR_READINESS: Final[str] = "verified"
SOURCE_FIDELITY: Final[str] = "pass"
ORACLE_SOURCE: Final[str] = str(SPEC["oracle_source"])
EXACT_CAPABILITY_READINESS: Final[str] = "pass"
DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.geometry_similarity_domain.build_geometry_similarity_matrix"
    if DOMAIN_OPERATION == "solve_similar_triangle_proportion"
    else "core.domain.trigonometry_acute_domain.build_trigonometry_acute_matrix",
)
ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker" if ANSWER_TYPE == "single_choice" else ("multi_part_answer_checker" if ANSWER_TYPE == "multi_part" else "expression_checker"),
    "equivalence_type": "choice_label" if ANSWER_TYPE == "single_choice" else ("multi_part_answer" if ANSWER_TYPE == "multi_part" else "algebraic_equivalent"),
    "answer_type": ANSWER_TYPE,
}

