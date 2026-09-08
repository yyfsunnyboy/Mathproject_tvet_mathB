from __future__ import annotations

from typing import Any

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "rational_equation_solve"
TEXTBOOK_EXAMPLE_ID = 4678
DEFAULT_COMPONENT_ID = "src_4678" if TEXTBOOK_EXAMPLE_ID else ""

SOURCE_PROBLEM_TEXT = '解下列分式方程式：(1)$\\frac{x+10}{x-2}=2$ (2)$\\frac{1}{x+1}=-\\frac{1}{{{x}^{2}}+x}$'


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

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_RationalEquation', 'source_example_id': 4678, 'textbook_example_id': 4678, 'source_hash': '2b029cb98437a2109dd4a578f77b77bb', 'problem_type_id': 'rational_equation_solve', 'required_capabilities': ['rational_equation_solve'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_RationalEquation', 'source_example_id': 4678, 'textbook_example_id': 4678, 'source_hash': '2b029cb98437a2109dd4a578f77b77bb', 'problem_type_id': 'rational_equation_solve', 'required_capabilities': ['rational_equation_solve'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'rational_equation_solve', 'required_capabilities': ['rational_equation_solve'], 'classification_source': 'phase1_rule_pack', 'source_hash': '2b029cb98437a2109dd4a578f77b77bb', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 4678, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_RationalEquation', 'fixed_domain_key': 'algebra.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['rational_equation_solve'], 'matched_capabilities': ['rational_equation_solve'], 'selected_operation': 'rational_equation_solve', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.polynomial_domain', 'entrypoint': 'build_polynomial_matrix', 'allowed_operations': ['rational_equation_solve'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_RationalEquation'})

    constraints["source_problem_text"] = SOURCE_PROBLEM_TEXT
    constraints["source_question_text"] = SOURCE_PROBLEM_TEXT
    constraints["presentation_mode"] = PRESENTATION_MODE
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
