from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

from core.gencode.answer_payload import (
    VALID_ANSWER_TYPES,
    answer_type_family,
    canonical_answer_type,
    format_invalid_answer_type_error,
    validate_generated_answer_shape,
)
from core.gencode.answer_contract_gate import coerce_single_choice_contract
from core.gencode.problem_type_spec import get_answer_contract, get_stem_contract

CHOICE_EMBEDDED_PATTERN = re.compile(r"(\([A-D]\)|[A-D][\.\)]\s)")
LABEL_ONLY_PATTERN = re.compile(r"^[\(\[]?\s*[A-Da-d]\s*[\)\]\.]?\s*$")


def _choices_to_texts(choices: Any) -> list[str]:
    if not isinstance(choices, list):
        return []
    out: list[str] = []
    for ch in choices:
        if isinstance(ch, dict):
            out.append(str(ch.get("text", "")).strip())
        else:
            out.append(str(ch).strip())
    return [x for x in out if x]


def _normalize_numeric(v: Any) -> float | None:
    try:
        return float(str(v).strip())
    except Exception:
        return None


def _normalize_fraction(v: Any) -> Fraction | None:
    try:
        return Fraction(str(v).strip())
    except Exception:
        return None


def _answer_value(payload: dict[str, Any]) -> Any:
    if payload.get("answer") is not None:
        return payload.get("answer")
    return payload.get("correct_answer")


def validate_answer_contract(payload: dict[str, Any], problem_type_spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    answer_contract = get_answer_contract(problem_type_spec)
    coerce_single_choice_contract(answer_contract)
    stem_contract = get_stem_contract(problem_type_spec)
    raw_answer_type = str(answer_contract.get("answer_type", "")).strip()
    answer_type = canonical_answer_type(raw_answer_type)
    family = answer_type_family(raw_answer_type)
    problem_type_id = str(problem_type_spec.get("problem_type_id", "")).strip()
    checker = str(answer_contract.get("checker", "")).strip()
    equivalence = str(answer_contract.get("answer_equivalence", "")).strip()

    if raw_answer_type and raw_answer_type not in VALID_ANSWER_TYPES and answer_type not in VALID_ANSWER_TYPES:
        errors.append(
            format_invalid_answer_type_error(
                problem_type_id=problem_type_id,
                answer_contract=answer_contract,
                answer_value=_answer_value(payload),
                checker=checker,
                equivalence=equivalence,
            )
        )
        return errors

    question_text = str(payload.get("question_text", ""))
    choices = payload.get("choices")
    choices_text = _choices_to_texts(choices)
    answer = _answer_value(payload)

    if bool(stem_contract.get("stem_must_not_embed_choices", True)) and CHOICE_EMBEDDED_PATTERN.search(question_text):
        errors.append("choices_embedded_in_question_text")

    shape_ok, shape_errors, _shape_diag = validate_generated_answer_shape(
        payload,
        answer_contract=answer_contract,
        problem_type_id=problem_type_id,
    )
    if not shape_ok:
        errors.extend(shape_errors)

    if family == "single_choice" or answer_type == "single_choice":
        if not isinstance(choices, list) or not choices_text:
            errors.append("choices_missing")
        choice_count = int(answer_contract.get("choice_count", 4) or 4)
        if len(choices_text) != choice_count:
            errors.append("choice_count_mismatch")
        if len(set(choices_text)) != len(choices_text):
            errors.append("choices_duplicate")
        if int(answer_contract.get("correct_choice_count", 1) or 1) != 1:
            errors.append("correct_choice_count_invalid")
        answer_str = str(answer).strip()
        if LABEL_ONLY_PATTERN.match(answer_str):
            labels = {chr(ord("A") + i) for i in range(len(choices_text))}
            if answer_str.strip("()[] .").upper() not in labels:
                errors.append("answer_not_in_choices")
        elif answer_str not in choices_text:
            errors.append("answer_not_in_choices")

    if family == "short_answer" or answer_type == "short_answer":
        if choices not in (None, []) and len(choices_text) > 0:
            errors.append("choices_must_be_empty_for_short_answer")
        if LABEL_ONLY_PATTERN.match(str(answer).strip()):
            errors.append("short_answer_must_not_be_choice_label")

    if family == "numeric" and equivalence in {"numeric_equal", "numeric_equivalence"}:
        if _normalize_numeric(answer) is None:
            errors.append("numeric_equivalence_invalid")
    if answer_type == "fraction" and equivalence == "fraction_equal":
        if _normalize_fraction(answer) is None:
            errors.append("fraction_equivalence_invalid")
    if answer_type == "expression" and equivalence == "algebraic_equivalent":
        if not str(answer).strip():
            errors.append("algebraic_equivalence_invalid")

    if CHOICE_EMBEDDED_PATTERN.search(question_text) and len(choices_text) > 0:
        errors.append("choices_embedded_in_question_text")

    return sorted(set(errors))
