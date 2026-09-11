"""Formal payload contracts for B2 1-3 arbitrary-angle operations."""
from __future__ import annotations
from typing import Any

from core.domain.trigonometry_arbitrary_domain import validate_trigonometry_arbitrary_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

OPERATION_PAYLOAD_CONTRACTS = {
    "classify_standard_position_angle": ("classification", "exact_angle_location_enum", "quadrant_checker", "normalized_label"),
    "compute_terminal_ray_trig_ratios": ("multi_part", "exact_signed_trig_ratio_parts", "multi_part_answer_checker", "multi_part_answer"),
    "solve_signed_trig_constraints": ("multi_part", "unique_signed_branch_exact_targets", "multi_part_answer_checker", "multi_part_answer"),
    "evaluate_exact_arbitrary_angle_trig_expression": ("expression", "exact_reduced_symbolic_expression", "expression_checker", "algebraic_equivalent"),
    "complete_reference_angle_conversion": ("multi_part", "reference_angle_and_sign_structured_parts", "multi_part_answer_checker", "multi_part_answer"),
    "classify_trig_derived_point_quadrant": ("classification", "exact_derived_point_location_enum", "quadrant_checker", "normalized_label"),
    "solve_arbitrary_angle_vertical_projection": ("expression", "exact_signed_projection_with_elevation", "expression_checker", "algebraic_equivalent"),
}

# Administrative source-to-capability audit map.  It selects shared operations
# only; no answer data or per-example mathematics lives here.
B2_13_SOURCE_OPERATION_MAP: dict[str, str] = {
    **{label: "classify_standard_position_angle" for label in ("例1", "隨堂練習1", "1-3習題 基礎題1")},
    **{label: "compute_terminal_ray_trig_ratios" for label in ("例2", "隨堂練習2", "1-3習題 基礎題2")},
    **{label: "solve_signed_trig_constraints" for label in ("例3", "隨堂練習3", "例4", "隨堂練習4", "1-3習題 基礎題3", "1-3習題 基礎題5")},
    **{label: "evaluate_exact_arbitrary_angle_trig_expression" for label in ("例5", "隨堂練習5", "例6", "隨堂練習6", "例7", "隨堂練習7", "例8", "隨堂練習8", "1-3習題 基礎題4", "1-3習題 基礎題6", "1-3習題 基礎題8")},
    **{label: "complete_reference_angle_conversion" for label in ("例9", "隨堂練習9", "1-3習題 基礎題7")},
    **{label: "classify_trig_derived_point_quadrant" for label in ("111統測B", "1-3習題 進階題9")},
    "1-3習題 進階題10": "solve_arbitrary_angle_vertical_projection",
}


def audit_b2_13_example_mapping() -> dict[str, Any]:
    mapped = B2_13_SOURCE_OPERATION_MAP
    unavailable = sorted(label for label, operation in mapped.items() if operation not in OPERATION_PAYLOAD_CONTRACTS)
    return {
        "expected_examples": 29,
        "mapped_examples": len(mapped),
        "oracle_unavailable": unavailable,
        "example_mapping_complete": len(mapped) == 29 and not unavailable,
    }

def adapt_b2_13_arbitrary_matrix(matrix: dict[str, Any], *, domain_operation: str, **kwargs: Any) -> dict[str, Any]:
    if domain_operation == "simplify_fundamental_trig_expression":
        from core.gencode.b2_12_capability_adapter import adapt_b2_12_batch1_matrix

        payload = adapt_b2_12_batch1_matrix(matrix, domain_operation=domain_operation, **kwargs)
        answer_contract = dict(payload.get("answer_contract") or {})
        answer_contract["fixed_domain_key"] = "trigonometry.arbitrary_angle"
        payload["answer_contract"] = answer_contract
        return payload
    contract = OPERATION_PAYLOAD_CONTRACTS.get(domain_operation)
    if contract is None: raise ValueError(f"unsupported_b2_13_operation:{domain_operation}")
    if not validate_trigonometry_arbitrary_matrix(matrix): raise ValueError(f"invalid_b2_13_matrix:{domain_operation}")
    answer_type, canonical_contract, checker, equivalence = contract
    payload = convert_domain_matrix_to_question_payload(matrix,
        presentation_mode=kwargs.pop("presentation_mode", "multiple_inputs" if answer_type=="multi_part" else "short_answer"),
        answer_type=kwargs.pop("answer_type", answer_type), problem_type_id=domain_operation,
        domain_operation=domain_operation, **kwargs)
    ac=dict(payload.get("answer_contract") or {})
    ac.update({
        "fixed_domain_key":"trigonometry.arbitrary_angle",
        "canonical_answer_contract":canonical_contract,
        "checker": checker,
        "checker_key": checker,
        "answer_equivalence": equivalence,
        "equivalence_type": equivalence,
    })
    if domain_operation=="complete_reference_angle_conversion":
        ac["required_form_validator"]="reference_angle_conversion_ast"
        ac["required_form"]="reference_angle_and_sign"
    payload["answer_contract"]=ac
    return payload
