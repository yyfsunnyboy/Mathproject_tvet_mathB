# -*- coding: utf-8 -*-
"""Payload adapter for B3 Chapter 4 exponential / logarithmic families."""

from __future__ import annotations

import re
from typing import Any

from core.domain.exponential_logarithmic_domain import (
    OPS,
    validate_exponential_logarithmic_matrix,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

_FIXED = "exponential.logarithmic"
_CHECKERS = {
    "expression": ("expression_checker", "algebraic_equivalent"),
    "multi_part": ("multi_part_answer_checker", "multi_part_answer"),
    "single_choice": ("single_choice_checker", "choice_value"),
}
_PART_EQUIVALENCE = {
    "ordered_inequality_checker": "ordered_inequality",
    "text_checker": "exact_string",
    "expression_checker": "algebraic_equivalent",
    "integer_checker": "numeric_exact",
}


def _apply_part_checkers(contract: dict[str, Any], overrides: dict[str, str]) -> None:
    parts = contract.get("parts") if isinstance(contract.get("parts"), list) else []
    seen = set()
    for row in parts:
        if not isinstance(row, dict):
            continue
        key = str(row.get("key") or "")
        checker = overrides.get(key)
        if not checker:
            continue
        seen.add(key)
        row["checker"] = checker
        row["checker_key"] = checker
        row["equivalence_type"] = _PART_EQUIVALENCE[checker]
        row["answer_equivalence"] = _PART_EQUIVALENCE[checker]
    missing = set(overrides) - seen
    if missing:
        raise ValueError(f"part_checker_key_not_found:{sorted(missing)}")


def _is_mixed_math_text(text: str) -> bool:
    if r"\(" not in text:
        return False
    return bool(re.sub(r"\\\(.*?\\\)", "", text).strip())


def _restore_mixed_choice_text(payload: dict[str, Any], matrix: dict[str, Any]) -> None:
    # The generic display formatter wraps the whole option in one $...$ span,
    # which breaks options that interleave text with several \(...\) spans.
    source = {
        str(row.get("value") or ""): str(row.get("text") or "")
        for row in matrix.get("choices") or []
        if isinstance(row, dict)
    }
    choices = payload.get("choices") or []
    for row in choices:
        text = source.get(str(row.get("value") or ""), "")
        if _is_mixed_math_text(text):
            row["text"] = text
            row["display"] = text
    if isinstance(payload.get("options"), list):
        payload["options"] = [str(row.get("text") or "") for row in choices]


def adapt_exponential_logarithmic_matrix(
    matrix: dict[str, Any],
    *,
    domain_operation: str,
    **kwargs: Any,
) -> dict[str, Any]:
    if domain_operation not in OPS:
        raise ValueError(f"unsupported_exponential_logarithmic_operation:{domain_operation}")
    if not validate_exponential_logarithmic_matrix(matrix):
        raise ValueError(f"invalid_exponential_logarithmic_matrix:{domain_operation}")
    kwargs.pop("answer_type", None)
    answer_type = str(matrix.get("answer_type") or "expression")
    presentation_mode = str(kwargs.pop("presentation_mode", None) or matrix.get("presentation_mode") or "short_answer")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=presentation_mode,
        answer_type=answer_type,
        problem_type_id=domain_operation,
        domain_operation=domain_operation,
        **kwargs,
    )
    checker, equivalence = _CHECKERS.get(answer_type, _CHECKERS["expression"])
    if presentation_mode == "single_choice" or answer_type == "single_choice":
        checker, equivalence = _CHECKERS["single_choice"]
        choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
        values = [str(row.get("value") or "") for row in choices if isinstance(row, dict)]
        semantic = str(matrix.get("semantic_answer") or "")
        if len(values) != 4 or len(set(values)) != 4 or semantic not in values:
            raise ValueError("mcq_identity_lost")
        label = str(matrix.get("correct_label") or "")
        matched = [row for row in choices if isinstance(row, dict) and str(row.get("label") or "") == label]
        if not matched or str(matched[0].get("value") or "") != semantic:
            raise ValueError("mcq_label_mismatch")
        _restore_mixed_choice_text(payload, matrix)
    contract = dict(payload.get("answer_contract") or {})
    if answer_type == "multi_part":
        _apply_part_checkers(contract, dict(matrix.get("part_checkers") or {}))
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
        facts = matrix.get("validation_facts") or {}
        payload["metadata"]["fixed_domain_key"] = _FIXED
        payload["metadata"]["multipart_count"] = int(facts.get("multipart_count") or 1)
        payload["metadata"]["log_notation"] = facts.get("log_notation")
        payload["metadata"]["given_approximations"] = dict(facts.get("given_approximations") or {})
        payload["metadata"]["visual_type"] = facts.get("visual_type")
    return payload
