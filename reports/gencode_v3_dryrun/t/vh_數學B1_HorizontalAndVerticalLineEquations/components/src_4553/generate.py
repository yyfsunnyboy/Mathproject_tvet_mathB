from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "write_line_equation_from_point_slope"
TEXTBOOK_EXAMPLE_ID = 4553
DEFAULT_COMPONENT_ID = "src_4553" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type="horizontal_line",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_HorizontalAndVerticalLineEquations', 'source_example_id': 4553, 'textbook_example_id': 4553, 'source_hash': '0449d0851471886274b014e2f668ce9b', 'problem_type_id': 'horizontal_line', 'required_capabilities': ['horizontal_line'], 'classification_source': 'deterministic', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_HorizontalAndVerticalLineEquations', 'source_example_id': 4553, 'textbook_example_id': 4553, 'source_hash': '0449d0851471886274b014e2f668ce9b', 'problem_type_id': 'horizontal_line', 'required_capabilities': ['horizontal_line'], 'classification_source': 'deterministic', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'classification_source': 'deterministic', 'source_example_id': 4553, 'source_hash': '0449d0851471886274b014e2f668ce9b', 'problem_type_id': 'horizontal_line', 'required_capabilities': ['horizontal_line'], 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression', 'exact_task_operation': ''},
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="line_equation",
        domain_operation="horizontal_line",
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
