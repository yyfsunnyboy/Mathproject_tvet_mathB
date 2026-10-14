from __future__ import annotations

from typing import Any

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "polynomial_factoring"
TEXTBOOK_EXAMPLE_ID = 4713
DEFAULT_COMPONENT_ID = "src_4713" if TEXTBOOK_EXAMPLE_ID else ""

SOURCE_PROBLEM_TEXT = '已知一長方形的面積為$9{{x}^{2}}+6x+1-{{y}^{2}}$平方單位，若其長、寬均為x、y的一次式且x、y項的係數均為整數，則此長方形的周長為？ (A) $6x+4$ (B) $6x-4$ (C) $12x-4$ (D) $12x+4$'


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_PolynomialFactoring",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "algebra.polynomial",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_PolynomialFactoring', 'source_example_id': 4713, 'textbook_example_id': 4713, 'source_hash': '1e1d604b4d070320ae1efc595693d2e7', 'problem_type_id': 'polynomial_factoring', 'required_capabilities': ['polynomial_factoring'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_PolynomialFactoring', 'source_example_id': 4713, 'textbook_example_id': 4713, 'source_hash': '1e1d604b4d070320ae1efc595693d2e7', 'problem_type_id': 'polynomial_factoring', 'required_capabilities': ['polynomial_factoring'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'polynomial_factoring', 'required_capabilities': ['polynomial_factoring'], 'classification_source': 'phase1_rule_pack', 'source_hash': '1e1d604b4d070320ae1efc595693d2e7', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 4713, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '$6x+4$'}, {'key': 'B', 'label': 'B', 'text': '$6x-4$'}, {'key': 'C', 'label': 'C', 'text': '$12x-4$'}, {'key': 'D', 'label': 'D', 'text': '$12x+4$'}], 'source_answer_label': 'D', 'domain_resolution': {'skill_id': 'vh_數學B1_PolynomialFactoring', 'fixed_domain_key': 'algebra.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['polynomial_factoring'], 'matched_capabilities': ['polynomial_factoring'], 'selected_operation': 'polynomial_factoring', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.polynomial_domain', 'entrypoint': 'build_polynomial_matrix', 'allowed_operations': ['polynomial_factoring'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_PolynomialFactoring'})

    constraints["source_problem_text"] = SOURCE_PROBLEM_TEXT
    constraints["source_question_text"] = SOURCE_PROBLEM_TEXT
    constraints["presentation_mode"] = PRESENTATION_MODE
    constraints["skill_id"] = "vh_數學B1_PolynomialFactoring"

    matrix = _v3_invoke_domain_entrypoint(
        build_polynomial_matrix,
        entrypoint_name="build_polynomial_matrix",
        domain_operation="polynomial_factoring",
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
        domain_operation="polynomial_factoring",
        seed=seed,
    )

    # 3-3 force single_choice contract
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
