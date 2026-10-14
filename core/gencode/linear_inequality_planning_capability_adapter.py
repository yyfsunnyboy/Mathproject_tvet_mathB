# -*- coding: utf-8 -*-
"""Payload adapter for B3 Chapter 3 linear inequality planning."""

from __future__ import annotations

from typing import Any

from core.domain.linear_inequality_planning_domain import (
    OPS,
    validate_linear_inequality_planning_matrix,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

_FIXED = "linear.inequality.planning"
_CHECKERS = {
    "ordered_pair": ("coordinate_pair_checker", "coordinate_pair_equivalence"),
    "inequality": ("inequality_solution_checker", "ordered_inequality"),
    "short_answer": ("text_checker", "normalized_text_equivalence"),
    "expression": ("expression_checker", "algebraic_equivalent"),
    "multi_part": ("multi_part_answer_checker", "multi_part_answer"),
    "single_choice": ("single_choice_checker", "choice_value"),
}


def adapt_linear_inequality_planning_matrix(
    matrix: dict[str, Any],
    *,
    domain_operation: str,
    **kwargs: Any,
) -> dict[str, Any]:
    if domain_operation not in OPS:
        raise ValueError(f"unsupported_linear_inequality_operation:{domain_operation}")
    if not validate_linear_inequality_planning_matrix(matrix):
        raise ValueError(f"invalid_linear_inequality_matrix:{domain_operation}")
    answer_type = str(kwargs.pop("answer_type", None) or matrix.get("answer_type") or "expression")
    presentation_mode = str(kwargs.pop("presentation_mode", None) or matrix.get("presentation_mode") or "short_answer")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=presentation_mode,
        answer_type=answer_type,
        problem_type_id=domain_operation,
        domain_operation=domain_operation,
        **kwargs,
    )
    checker, equivalence = _CHECKERS.get(answer_type, ("expression_checker", "algebraic_equivalent"))
    if presentation_mode == "single_choice" or answer_type == "single_choice":
        checker, equivalence = _CHECKERS["single_choice"]
        choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
        values = [str(row.get("value") or "") for row in choices if isinstance(row, dict)]
        semantic = str(matrix.get("semantic_answer") or "")
        if semantic not in values:
            raise ValueError("mcq_identity_lost")
        label = str(matrix.get("correct_label") or "")
        matched = [row for row in choices if isinstance(row, dict) and str(row.get("label") or "") == label]
        if not matched or str(matched[0].get("value") or "") != semantic:
            raise ValueError("mcq_label_mismatch")
    contract = dict(payload.get("answer_contract") or {})
    contract["checker"] = checker
    contract["checker_key"] = checker
    contract["equivalence"] = equivalence
    contract["equivalence_type"] = equivalence
    contract["semantic_answer"] = matrix.get("semantic_answer")
    payload["answer_contract"] = contract
    payload["checker"] = checker
    payload["checker_key"] = checker
    payload["equivalence"] = equivalence
    payload["semantic_answer"] = matrix.get("semantic_answer")
    payload.setdefault("metadata", {})
    if isinstance(payload["metadata"], dict):
        payload["metadata"]["fixed_domain_key"] = _FIXED
        payload["metadata"]["multipart_count"] = int((matrix.get("validation_facts") or {}).get("multipart_count") or 1)
    return payload
