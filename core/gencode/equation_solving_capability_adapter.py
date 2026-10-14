# -*- coding: utf-8 -*-
"""Payload adapter for B3 Chapter 2 equation.solving."""

from __future__ import annotations

from typing import Any

from core.domain.equation_solving_domain import (
    INEQUALITY_SOLVE,
    OPS,
    QUADRATIC_PARAMETER_NO_REAL,
    QUADRATIC_PARAMETER_TWO_DISTINCT,
    validate_equation_solving_matrix,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

_FIXED = "equation.solving"
_INEQUALITY_OPS = frozenset({
    INEQUALITY_SOLVE,
    QUADRATIC_PARAMETER_NO_REAL,
    QUADRATIC_PARAMETER_TWO_DISTINCT,
})


def adapt_equation_solving_matrix(
    matrix: dict[str, Any],
    *,
    domain_operation: str,
    **kwargs: Any,
) -> dict[str, Any]:
    if domain_operation not in OPS:
        raise ValueError(f"unsupported_equation_operation:{domain_operation}")
    if not validate_equation_solving_matrix(matrix):
        raise ValueError(f"invalid_equation_solving_matrix:{domain_operation}")
    facts = matrix.get("validation_facts") if isinstance(matrix.get("validation_facts"), dict) else {}
    answer_type = str(kwargs.pop("answer_type", None) or facts.get("answer_type") or matrix.get("answer_type") or "expression")
    presentation_mode = str(
        kwargs.pop("presentation_mode", None) or facts.get("presentation_mode") or matrix.get("presentation_mode") or "short_answer"
    )
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=presentation_mode,
        answer_type=answer_type,
        problem_type_id=domain_operation,
        domain_operation=domain_operation,
        **kwargs,
    )
    if domain_operation in _INEQUALITY_OPS and answer_type != "single_choice":
        contract = dict(payload.get("answer_contract") or {})
        parts = contract.get("parts")
        if isinstance(parts, list):
            for part in parts:
                if isinstance(part, dict):
                    part["checker"] = "inequality_solution_checker"
                    part["checker_key"] = "inequality_solution_checker"
                    part["equivalence_type"] = "interval_equivalence"
        else:
            contract["checker"] = "inequality_solution_checker"
            contract["checker_key"] = "inequality_solution_checker"
            contract["equivalence_type"] = "interval_equivalence"
            payload["checker"] = "inequality_solution_checker"
            payload["checker_key"] = "inequality_solution_checker"
            payload["equivalence"] = "interval_equivalence"
        payload["answer_contract"] = contract
    payload.setdefault("metadata", {})
    if isinstance(payload["metadata"], dict):
        payload["metadata"]["fixed_domain_key"] = _FIXED
    return payload
