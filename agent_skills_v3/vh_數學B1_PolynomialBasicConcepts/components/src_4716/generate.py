from __future__ import annotations

from typing import Any

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "polynomial_degree_product_sum"
TEXTBOOK_EXAMPLE_ID = 4716
DEFAULT_COMPONENT_ID = "src_4716" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_PolynomialBasicConcepts",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "algebra.polynomial",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_PolynomialBasicConcepts', 'source_example_id': 4716, 'textbook_example_id': 4716, 'source_hash': '40c98a7608c692d96e2e9f010f5f6286', 'problem_type_id': 'polynomial_degree_product_sum', 'required_capabilities': ['polynomial_degree_product_sum'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_PolynomialBasicConcepts', 'source_example_id': 4716, 'textbook_example_id': 4716, 'source_hash': '40c98a7608c692d96e2e9f010f5f6286', 'problem_type_id': 'polynomial_degree_product_sum', 'required_capabilities': ['polynomial_degree_product_sum'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'polynomial_degree_product_sum', 'required_capabilities': ['polynomial_degree_product_sum'], 'classification_source': 'phase1_rule_pack', 'source_hash': '40c98a7608c692d96e2e9f010f5f6286', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 4716, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '4'}, {'key': 'B', 'label': 'B', 'text': '14'}, {'key': 'C', 'label': 'C', 'text': '9'}, {'key': 'D', 'label': 'D', 'text': '6'}], 'source_answer_label': 'A', 'domain_resolution': {'skill_id': 'vh_數學B1_PolynomialBasicConcepts', 'fixed_domain_key': 'algebra.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['polynomial_degree_product_sum'], 'matched_capabilities': ['polynomial_degree_product_sum'], 'selected_operation': 'polynomial_degree_product_sum', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.polynomial_domain', 'entrypoint': 'build_polynomial_matrix', 'allowed_operations': ['polynomial_descending_power_properties', 'polynomial_param_degree_constraint', 'polynomial_descending_power_table', 'zero_polynomial_find_coeffs', 'polynomial_degree_product_sum'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_PolynomialBasicConcepts'})
    constraints["skill_id"] = "vh_數學B1_PolynomialBasicConcepts"

    matrix = _v3_invoke_domain_entrypoint(
        build_polynomial_matrix,
        entrypoint_name="build_polynomial_matrix",
        domain_operation="polynomial_degree_product_sum",
        seed=seed,
        curriculum_profile="vocational_high_b",
        difficulty_profile="hard",
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
        answer_schema_key="choice_label",
        domain_operation="polynomial_degree_product_sum",
        seed=seed,
    )

    # recovered self-assessment: force single_choice contract
    payload["presentation_mode"] = "single_choice"
    payload["answer_type"] = "single_choice"
    payload["interaction_type"] = "single_choice"
    payload["checker"] = "choice_label_checker"
    payload["checker_key"] = "choice_label_checker"
    _ac = dict(payload.get("answer_contract") or {})
    _ac.update({
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "answer_equivalence": "choice_label",
        "equivalence": "choice_label",
        "equivalence_type": "choice_label",
    })
    payload["answer_contract"] = _ac
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
