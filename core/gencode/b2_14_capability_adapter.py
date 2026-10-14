"""Payload contracts for B2 1-4 shared trigonometric graph capabilities."""

from __future__ import annotations
from typing import Any

from core.domain.trigonometry_function_graph_domain import OPS, validate_trigonometry_function_graph_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

OPERATION_PAYLOAD_CONTRACTS = {
    operation: {
        "fixed_domain_key": "trigonometry.function_graph",
        "input_schema": {"type": "object", "additionalProperties": False},
        "output_schema": {"type": "domain_matrix", "answer": "canonical_exact"},
        "canonical_answer_contract": "deterministic_exact_trigonometry_oracle",
        "checker": "multi_part_answer_checker",
    } for operation in OPS
}
_INPUT_FIELDS = {
    "compare_trig_values_by_monotonicity": ("terms", "unit"),
    "solve_trig_value_quadratic_constraint": ("function", "coefficients"),
    "analyze_affine_transformed_trig_graph": ("function", "A", "B", "C", "D"),
    "calculate_trig_period_from_argument_scale": ("function", "B", "C"),
    "classify_trig_expression_sign_change": ("function", "B", "C", "interval", "unit"),
    "classify_trig_equation_feasibility": ("options", "target"),
    "analyze_tangent_absolute_graph_period": ("A", "B", "C", "D"),
    "evaluate_trig_decimal": ("requests",),
    "count_sine_cosine_intersections": ("B", "C", "interval", "unit"),
}
for _operation, _fields in _INPUT_FIELDS.items():
    OPERATION_PAYLOAD_CONTRACTS[_operation]["input_schema"]["fields"] = _fields
OPERATION_PAYLOAD_CONTRACTS["classify_trig_equation_feasibility"].update({"checker":"single_choice_checker"})
OPERATION_PAYLOAD_CONTRACTS["evaluate_trig_decimal"].update({"canonical_answer_contract":"decimal_round_half_up_with_explicit_tolerance"})


def adapt_b2_14_function_graph_matrix(matrix: dict[str, Any], *, domain_operation: str, **kwargs: Any) -> dict[str, Any]:
    contract = OPERATION_PAYLOAD_CONTRACTS.get(str(domain_operation))
    if contract is None: raise ValueError(f"unsupported_b2_14_operation:{domain_operation}")
    if not validate_trigonometry_function_graph_matrix(matrix): raise ValueError(f"invalid_b2_14_domain_matrix:{domain_operation}")
    answer_type = kwargs.pop("answer_type", "single_choice" if domain_operation == "classify_trig_equation_feasibility" else "multi_part")
    presentation_mode = kwargs.pop("presentation_mode", "single_choice" if answer_type == "single_choice" else "multiple_inputs")
    payload = convert_domain_matrix_to_question_payload(matrix, presentation_mode=presentation_mode,
        answer_type=answer_type, problem_type_id=domain_operation, domain_operation=domain_operation, **kwargs)
    answer_contract = dict(payload.get("answer_contract") or {})
    answer_contract.update({"fixed_domain_key": contract["fixed_domain_key"],
        "canonical_answer_contract": contract["canonical_answer_contract"]})
    required_form = (matrix.get("givens") or {}).get("required_form")
    for part in answer_contract.get("parts") or []:
        if domain_operation == "evaluate_trig_decimal":
            part.update({"checker":"decimal_tolerance_checker", "checker_key":"decimal_tolerance_checker",
                         "equivalence_type":"decimal_tolerance", "rounding_policy":"ROUND_HALF_UP"})
        else:
            part.update({"checker":"expression_checker", "checker_key":"expression_checker",
                         "equivalence_type":"algebraic_equivalent"})
            if required_form: part["required_form"] = required_form
    if answer_type == "single_choice":
        answer_contract.update({"checker":"single_choice_checker", "semantic_choice": True})
    payload["answer_contract"] = answer_contract
    return payload
