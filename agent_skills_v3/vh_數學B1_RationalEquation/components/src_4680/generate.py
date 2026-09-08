from __future__ import annotations

from typing import Any

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "rational_equation_solve"
TEXTBOOK_EXAMPLE_ID = 4680
DEFAULT_COMPONENT_ID = "src_4680" if TEXTBOOK_EXAMPLE_ID else ""

SOURCE_PROBLEM_TEXT = '已知多項式$Q\\left( x \\right)=ax+b$，$f\\left( x \\right)=\\left( 2a-b \\right){{x}^{2}}+ax-1$，$g\\left( x \\right)=3{{x}^{2}}+x-1$，且$f\\left( x \\right)=g\\left( x \\right)$。若分式方程式$\\frac{x}{Q\\left( x \\right)}+\\frac{5}{x-2}=\\frac{-1}{\\left( x-2 \\right)Q\\left( x \\right)}$的解為$x=c$，則${{a}^{2}}+{{b}^{2}}+{{c}^{2}}=$？ (A) 4 (B) 10 (C) 18 (D) 27 〔112統測B〕'


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_RationalEquation",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "algebra.polynomial",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_RationalEquation', 'source_example_id': 4680, 'textbook_example_id': 4680, 'source_hash': 'cbead959ecd0d868968cb22ea161ce9b', 'problem_type_id': 'rational_equation_solve', 'required_capabilities': ['rational_equation_solve'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_RationalEquation', 'source_example_id': 4680, 'textbook_example_id': 4680, 'source_hash': 'cbead959ecd0d868968cb22ea161ce9b', 'problem_type_id': 'rational_equation_solve', 'required_capabilities': ['rational_equation_solve'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'rational_equation_solve', 'required_capabilities': ['rational_equation_solve'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'cbead959ecd0d868968cb22ea161ce9b', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 4680, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '4'}, {'key': 'B', 'label': 'B', 'text': '10'}, {'key': 'C', 'label': 'C', 'text': '18'}, {'key': 'D', 'label': 'D', 'text': '27 〔112統測B〕'}], 'source_answer_label': 'C', 'domain_resolution': {'skill_id': 'vh_數學B1_RationalEquation', 'fixed_domain_key': 'algebra.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['rational_equation_solve'], 'matched_capabilities': ['rational_equation_solve'], 'selected_operation': 'rational_equation_solve', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.polynomial_domain', 'entrypoint': 'build_polynomial_matrix', 'allowed_operations': ['rational_equation_solve'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_RationalEquation'})

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
        answer_schema_key="choice_label",
        domain_operation="rational_equation_solve",
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
