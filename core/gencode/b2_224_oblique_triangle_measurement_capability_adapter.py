# -*- coding: utf-8 -*-
"""Composition adapter for B2 §2-2-4 — reuses sine/cosine payload adapters."""

from __future__ import annotations

from typing import Any

from core.domain.trigonometry_oblique_triangle_measurement_domain import (
    OPS,
    validate_trigonometry_oblique_triangle_measurement_matrix,
)
from core.gencode.b2_21_law_of_cosines_capability_adapter import adapt_b2_21_law_of_cosines_matrix
from core.gencode.b2_21_law_of_sines_capability_adapter import adapt_b2_21_law_of_sines_matrix

_FIXED = "trigonometry.oblique_triangle_measurement"
_SINE_OPS = {"solve_side_by_law_of_sines"}
_COSINE_OPS = {"solve_side_by_law_of_cosines"}

OPERATION_PAYLOAD_CONTRACTS = {
    "solve_side_by_law_of_sines": {
        "fixed_domain_key": _FIXED,
        "canonical_answer_contract": "deterministic_exact_trigonometry_oracle",
        "checker": "single_choice_checker",
        "cross_domain_delegate": "trigonometry.law_of_sines",
    },
    "solve_side_by_law_of_cosines": {
        "fixed_domain_key": _FIXED,
        "canonical_answer_contract": "deterministic_exact_trigonometry_oracle",
        "checker": "expression_checker",
        "cross_domain_delegate": "trigonometry.law_of_cosines",
    },
}


def adapt_b2_224_oblique_triangle_measurement_matrix(
    matrix: dict[str, Any],
    *,
    domain_operation: str,
    **kwargs: Any,
) -> dict[str, Any]:
    op = str(domain_operation or "").strip()
    if op not in OPS:
        raise ValueError(f"unsupported_b2_224_oblique_operation:{op}")
    if not validate_trigonometry_oblique_triangle_measurement_matrix(matrix):
        raise ValueError(f"invalid_b2_224_oblique_domain_matrix:{op}")

    if op in _SINE_OPS:
        payload = adapt_b2_21_law_of_sines_matrix(matrix, domain_operation=op, **kwargs)
    elif op in _COSINE_OPS:
        payload = adapt_b2_21_law_of_cosines_matrix(matrix, domain_operation=op, **kwargs)
    else:
        raise ValueError(f"unsupported_b2_224_oblique_operation:{op}")

    contract = OPERATION_PAYLOAD_CONTRACTS[op]
    answer_contract = dict(payload.get("answer_contract") or {})
    answer_contract["fixed_domain_key"] = contract["fixed_domain_key"]
    answer_contract["cross_domain_delegate"] = contract["cross_domain_delegate"]
    answer_contract["canonical_answer_contract"] = contract["canonical_answer_contract"]
    payload["answer_contract"] = answer_contract
    payload["fixed_domain_key"] = _FIXED
    if payload.get("choices"):
        payload["choice_contract_valid"] = True
    return payload
