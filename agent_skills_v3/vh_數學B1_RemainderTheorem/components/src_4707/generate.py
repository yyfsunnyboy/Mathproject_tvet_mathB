from __future__ import annotations

from typing import Any

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "remainder_theorem_evaluate"
TEXTBOOK_EXAMPLE_ID = 4707
DEFAULT_COMPONENT_ID = "src_4707" if TEXTBOOK_EXAMPLE_ID else ""

SOURCE_PROBLEM_TEXT = "設$f\\left( x \\right)={{x}^{5}}-6{{x}^{4}}-4{{x}^{3}}-25{{x}^{2}}+30x-7$，則$f\\left( 7 \\right)=$ (A) 9 (B) 8 (C) 7 (D) 6。"




def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_RemainderTheorem",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "algebra.polynomial",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_RemainderTheorem', 'source_example_id': 4707, 'textbook_example_id': 4707, 'source_hash': 'a196abda5aa8c2d3f3c6160813ac9255', 'problem_type_id': 'remainder_theorem_evaluate', 'required_capabilities': ['remainder_theorem_evaluate'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_RemainderTheorem', 'source_example_id': 4707, 'textbook_example_id': 4707, 'source_hash': 'a196abda5aa8c2d3f3c6160813ac9255', 'problem_type_id': 'remainder_theorem_evaluate', 'required_capabilities': ['remainder_theorem_evaluate'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'remainder_theorem_evaluate', 'required_capabilities': ['remainder_theorem_evaluate'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'a196abda5aa8c2d3f3c6160813ac9255', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 4707, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '9'}, {'key': 'B', 'label': 'B', 'text': '8'}, {'key': 'C', 'label': 'C', 'text': '7'}, {'key': 'D', 'label': 'D', 'text': '6'}], 'source_answer_label': 'C', 'domain_resolution': {'skill_id': 'vh_數學B1_RemainderTheorem', 'fixed_domain_key': 'algebra.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['remainder_theorem_evaluate'], 'matched_capabilities': ['remainder_theorem_evaluate'], 'selected_operation': 'remainder_theorem_evaluate', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.polynomial_domain', 'entrypoint': 'build_polynomial_matrix', 'allowed_operations': ['remainder_theorem_evaluate'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_RemainderTheorem'})

    constraints["source_problem_text"] = SOURCE_PROBLEM_TEXT
    constraints["source_question_text"] = SOURCE_PROBLEM_TEXT
    constraints["presentation_mode"] = PRESENTATION_MODE
    constraints["skill_id"] = "vh_數學B1_RemainderTheorem"

    matrix = _v3_invoke_domain_entrypoint(
        build_polynomial_matrix,
        entrypoint_name="build_polynomial_matrix",
        domain_operation="remainder_theorem_evaluate",
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
        domain_operation="remainder_theorem_evaluate",
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
