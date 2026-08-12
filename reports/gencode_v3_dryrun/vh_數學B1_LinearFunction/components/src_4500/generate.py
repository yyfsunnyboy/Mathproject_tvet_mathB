from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "graph_single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "graph_based_linear_model_equation"
TEXTBOOK_EXAMPLE_ID = 4500
DEFAULT_COMPONENT_ID = "src_4500" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_LinearFunction",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "coordinate_geometry.line_equation",
    }

    constraints = {
        "v3_induced_spec": {
            "classification_status": "resolved",
            "skill_id": "vh_數學B1_LinearFunction",
            "source_example_id": 4500,
            "textbook_example_id": 4500,
            "problem_type_id": PROBLEM_TYPE_ID,
            "required_capabilities": [PROBLEM_TYPE_ID],
            "classification_source": "phase1_rule_pack",
            "presentation_mode": PRESENTATION_MODE,
            "answer_contract": {
                "answer_type": ANSWER_TYPE,
                "checker_key": "choice_label_checker",
                "equivalence_type": "choice_label",
            },
            "answer_type": ANSWER_TYPE,
            "source_topology": {
                "problem_type_id": PROBLEM_TYPE_ID,
                "exact_task_operation": PROBLEM_TYPE_ID,
                "required_givens": ["context_variables", "linear_relation_graph"],
                "requested_quantity": ["linear_model_equation"],
                "topology_tags": [
                    "contextual_application",
                    "graph_reading",
                    "equation_from_graph",
                    "single_choice",
                ],
                "answer_schema": "choice_label",
                "presentation_mode": PRESENTATION_MODE,
            },
        },
        "problem_type_id": PROBLEM_TYPE_ID,
        "required_capabilities": [PROBLEM_TYPE_ID],
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "skill_id": "vh_數學B1_LinearFunction",
    }

    matrix = _v3_invoke_domain_entrypoint(
        build_line_equation_matrix,
        entrypoint_name="build_line_equation_matrix",
        domain_operation=PROBLEM_TYPE_ID,
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
        domain_operation=PROBLEM_TYPE_ID,
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
