from __future__ import annotations

from typing import Any

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "rational_equation_solve"
TEXTBOOK_EXAMPLE_ID = 4699
DEFAULT_COMPONENT_ID = "src_4699" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_RationalEquation",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "algebra.polynomial",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_RationalEquation', 'source_example_id': 4699, 'textbook_example_id': 4699, 'source_hash': '2d488c16378ac93297005d18b7d68d97', 'problem_type_id': 'rational_equation_solve', 'required_capabilities': ['rational_equation_solve'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_RationalEquation', 'source_example_id': 4699, 'textbook_example_id': 4699, 'source_hash': '2d488c16378ac93297005d18b7d68d97', 'problem_type_id': 'rational_equation_solve', 'required_capabilities': ['rational_equation_solve'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'rational_equation_solve', 'required_capabilities': ['rational_equation_solve'], 'classification_source': 'phase1_rule_pack', 'source_hash': '2d488c16378ac93297005d18b7d68d97', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 4699, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_RationalEquation', 'fixed_domain_key': 'algebra.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['rational_equation_solve'], 'matched_capabilities': ['rational_equation_solve'], 'selected_operation': '', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.polynomial_domain', 'entrypoint': 'build_polynomial_matrix', 'allowed_operations': ['rational_equation_solve'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_RationalEquation'})
    constraints["skill_id"] = "vh_數學B1_RationalEquation"

    matrix = _v3_invoke_domain_entrypoint(
        build_polynomial_matrix,
        entrypoint_name="build_polynomial_matrix",
        domain_operation="rational_equation_solve",
        seed=seed,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints=constraints,
    )
    matrix = normalize_domain_payload_to_v3_matrix(matrix, norm_context)

    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="",
        domain_operation="rational_equation_solve",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
