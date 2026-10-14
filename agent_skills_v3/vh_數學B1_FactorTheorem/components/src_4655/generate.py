from __future__ import annotations

from typing import Any

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "factor_theorem_root_factor"
TEXTBOOK_EXAMPLE_ID = 4655
DEFAULT_COMPONENT_ID = "src_4655" if TEXTBOOK_EXAMPLE_ID else ""

SOURCE_PROBLEM_TEXT = "已知多項式$f\\left( x \\right)$除以$\\left( x+2 \\right)\\left( x-7 \\right)$的餘式為$ax+3$。若$\\left( x-7 \\right)$為$f\\left( x \\right)$的因式，則$f\\left( -2 \\right)=$？ (A) $\\frac{27}{7}$ (B) $\\frac{29}{7}$ (C) $\\frac{31}{7}$ (D) $\\frac{33}{7}$。"




def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_FactorTheorem",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "algebra.polynomial",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_FactorTheorem', 'source_example_id': 4655, 'textbook_example_id': 4655, 'source_hash': '5aed18eeef4499374f5a404da4ca1e31', 'problem_type_id': 'factor_theorem_root_factor', 'required_capabilities': ['factor_theorem_root_factor'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_FactorTheorem', 'source_example_id': 4655, 'textbook_example_id': 4655, 'source_hash': '5aed18eeef4499374f5a404da4ca1e31', 'problem_type_id': 'factor_theorem_root_factor', 'required_capabilities': ['factor_theorem_root_factor'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'factor_theorem_root_factor', 'required_capabilities': ['factor_theorem_root_factor'], 'classification_source': 'phase1_rule_pack', 'source_hash': '5aed18eeef4499374f5a404da4ca1e31', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 4655, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '$\\frac{27}{7}$'}, {'key': 'B', 'label': 'B', 'text': '$\\frac{29}{7}$'}, {'key': 'C', 'label': 'C', 'text': '$\\frac{31}{7}$'}, {'key': 'D', 'label': 'D', 'text': '$\\frac{33}{7}$'}], 'source_answer_label': 'A', 'domain_resolution': {'skill_id': 'vh_數學B1_FactorTheorem', 'fixed_domain_key': 'algebra.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['factor_theorem_root_factor'], 'matched_capabilities': ['factor_theorem_root_factor'], 'selected_operation': 'factor_theorem_root_factor', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.polynomial_domain', 'entrypoint': 'build_polynomial_matrix', 'allowed_operations': ['factor_theorem_root_factor'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_FactorTheorem'})

    constraints["source_problem_text"] = SOURCE_PROBLEM_TEXT
    constraints["source_question_text"] = SOURCE_PROBLEM_TEXT
    constraints["presentation_mode"] = PRESENTATION_MODE
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
        answer_schema_key="choice_label",
        domain_operation="factor_theorem_root_factor",
        seed=seed,
    )

    # 3-2 force single_choice contract
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
