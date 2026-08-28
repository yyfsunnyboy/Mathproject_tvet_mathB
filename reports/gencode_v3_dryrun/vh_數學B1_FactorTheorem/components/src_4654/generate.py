from __future__ import annotations

from typing import Any

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "factor_theorem_root_factor"
TEXTBOOK_EXAMPLE_ID = 4654
DEFAULT_COMPONENT_ID = "src_4654" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_FactorTheorem",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "algebra.polynomial",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_FactorTheorem', 'source_example_id': 4654, 'textbook_example_id': 4654, 'source_hash': '1226bafb8915269e3d427469b7b4f47e', 'problem_type_id': 'factor_theorem_root_factor', 'required_capabilities': ['factor_theorem_root_factor'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_FactorTheorem', 'source_example_id': 4654, 'textbook_example_id': 4654, 'source_hash': '1226bafb8915269e3d427469b7b4f47e', 'problem_type_id': 'factor_theorem_root_factor', 'required_capabilities': ['factor_theorem_root_factor'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'factor_theorem_root_factor', 'required_capabilities': ['factor_theorem_root_factor'], 'classification_source': 'phase1_rule_pack', 'source_hash': '1226bafb8915269e3d427469b7b4f47e', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 4654, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_FactorTheorem', 'fixed_domain_key': 'algebra.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['factor_theorem_root_factor'], 'matched_capabilities': ['factor_theorem_root_factor'], 'selected_operation': '', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.polynomial_domain', 'entrypoint': 'build_polynomial_matrix', 'allowed_operations': ['factor_theorem_root_factor'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_FactorTheorem'})
    constraints["skill_id"] = "vh_數學B1_FactorTheorem"

    matrix = _v3_invoke_domain_entrypoint(
        build_polynomial_matrix,
        entrypoint_name="build_polynomial_matrix",
        domain_operation="factor_theorem_root_factor",
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
        domain_operation="factor_theorem_root_factor",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
