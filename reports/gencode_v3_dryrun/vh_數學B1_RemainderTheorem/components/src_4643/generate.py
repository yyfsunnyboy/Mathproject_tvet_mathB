from __future__ import annotations

from typing import Any

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "remainder_theorem_evaluate"
TEXTBOOK_EXAMPLE_ID = 4643
DEFAULT_COMPONENT_ID = "src_4643" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_RemainderTheorem",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "algebra.polynomial",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_RemainderTheorem', 'source_example_id': 4643, 'textbook_example_id': 4643, 'source_hash': 'c5f8a1bd8e0c5a11fcdf1aa764e8d899', 'problem_type_id': 'remainder_theorem_evaluate', 'required_capabilities': ['remainder_theorem_evaluate'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_RemainderTheorem', 'source_example_id': 4643, 'textbook_example_id': 4643, 'source_hash': 'c5f8a1bd8e0c5a11fcdf1aa764e8d899', 'problem_type_id': 'remainder_theorem_evaluate', 'required_capabilities': ['remainder_theorem_evaluate'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'remainder_theorem_evaluate', 'required_capabilities': ['remainder_theorem_evaluate'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'c5f8a1bd8e0c5a11fcdf1aa764e8d899', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 4643, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_RemainderTheorem', 'fixed_domain_key': 'algebra.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['remainder_theorem_evaluate'], 'matched_capabilities': ['remainder_theorem_evaluate'], 'selected_operation': '', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.polynomial_domain', 'entrypoint': 'build_polynomial_matrix', 'allowed_operations': ['remainder_theorem_evaluate'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_RemainderTheorem'})
    constraints["skill_id"] = "vh_數學B1_RemainderTheorem"

    matrix = _v3_invoke_domain_entrypoint(
        build_polynomial_matrix,
        entrypoint_name="build_polynomial_matrix",
        domain_operation="remainder_theorem_evaluate",
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
        domain_operation="remainder_theorem_evaluate",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
