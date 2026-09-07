from __future__ import annotations

from typing import Any

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "polynomial_equality_identity"
TEXTBOOK_EXAMPLE_ID = 4611
DEFAULT_COMPONENT_ID = "src_4611" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_PolynomialEquality",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "algebra.polynomial",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_PolynomialEquality', 'source_example_id': 4611, 'textbook_example_id': 4611, 'source_hash': '043f8bd9c136e5173f434dff507aaacd', 'problem_type_id': 'polynomial_equality_identity', 'required_capabilities': ['polynomial_equality_identity'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_PolynomialEquality', 'source_example_id': 4611, 'textbook_example_id': 4611, 'source_hash': '043f8bd9c136e5173f434dff507aaacd', 'problem_type_id': 'polynomial_equality_identity', 'required_capabilities': ['polynomial_equality_identity'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'polynomial_equality_identity', 'required_capabilities': ['polynomial_equality_identity'], 'classification_source': 'phase1_rule_pack', 'source_hash': '043f8bd9c136e5173f434dff507aaacd', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 4611, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_PolynomialEquality', 'fixed_domain_key': 'algebra.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['polynomial_equality_identity'], 'matched_capabilities': ['polynomial_equality_identity'], 'selected_operation': 'polynomial_equality_identity', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.polynomial_domain', 'entrypoint': 'build_polynomial_matrix', 'allowed_operations': ['polynomial_equality_identity'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_PolynomialEquality'})
    constraints["skill_id"] = "vh_數學B1_PolynomialEquality"

    matrix = _v3_invoke_domain_entrypoint(
        build_polynomial_matrix,
        entrypoint_name="build_polynomial_matrix",
        domain_operation="polynomial_equality_identity",
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
        domain_operation="polynomial_equality_identity",
        seed=seed,
    )

    # v1.12 topology alignment: ensure multi_part answer_contract.parts
    if isinstance(payload.get("answer"), dict):
        _ans = payload["answer"]
        _parts = []
        for _k, _v in sorted(_ans.items(), key=lambda kv: str(kv[0])):
            _chk = "integer_checker" if str(_v).strip().lstrip("+-").isdigit() else "expression_checker"
            _parts.append({
                "key": str(_k),
                "label": str(_k),
                "checker": _chk,
                "checker_key": _chk,
                "equivalence_type": "numeric_exact" if _chk == "integer_checker" else "algebraic_equivalent",
                "expected_answer": _v,
            })
        _ac = dict(payload.get("answer_contract") or {})
        _ac.update({
            "answer_type": "multi_part",
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "equivalence_type": "multi_part_answer",
            "parts": _parts,
        })
        payload["answer_type"] = "multi_part"
        payload["answer_contract"] = _ac
        payload["checker"] = "multi_part_answer_checker"
        payload["checker_key"] = "multi_part_answer_checker"

    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
