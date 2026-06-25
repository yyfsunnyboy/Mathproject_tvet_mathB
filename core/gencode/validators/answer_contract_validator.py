from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

from core.gencode.answer_payload import (
    VALID_ANSWER_TYPES,
    answer_type_family,
    canonical_answer_type,
    format_invalid_answer_type_error,
    is_linear_equation_contract,
    validate_generated_answer_shape,
)
from core.gencode.answer_contract_gate import (
    _INCOMPATIBLE_ANSWER_TYPES_FOR_CHOICE_LABEL_CHECKER,
    coerce_single_choice_contract,
)
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


def validate_answer_type_presentation_consistency(payload: dict[str, Any]) -> list[str]:
    """Hard contract rules that apply universally regardless of problem_type_spec.

    Error codes returned (never raise):
        ANSWER_CONTRACT_INCONSISTENT   – checker=choice_label_checker + incompatible answer_type
        ANSWER_TYPE_INTEGER_LABEL_MISMATCH – answer_type=integer but answer is a choice label
        CHOICE_LABEL_NOT_IN_CHOICES    – single_choice + answer not in choice labels
        CHOICES_EMPTY_FOR_SINGLE_CHOICE – single_choice + no choices
        SEMANTIC_ANSWER_MISMATCH       – correct choice value != semantic_answer
    """
    errors: list[str] = []
    mode = str(payload.get("presentation_mode") or "").strip()
    answer_type = str(payload.get("answer_type") or "").strip()
    checker = str(payload.get("checker_key") or payload.get("checker") or "").strip()
    answer = payload.get("answer") or payload.get("correct_answer")
    choices = payload.get("choices") or []
    semantic = payload.get("semantic_answer")

    answer_str = str(answer or "").strip()
    is_label = bool(LABEL_ONLY_PATTERN.match(answer_str))

    # Rule B: choice_label_checker forbids numeric/expression answer_type
    if checker == "choice_label_checker" and answer_type in _INCOMPATIBLE_ANSWER_TYPES_FOR_CHOICE_LABEL_CHECKER:
        errors.append(
            f"ANSWER_CONTRACT_INCONSISTENT:checker=choice_label_checker+answer_type={answer_type}"
        )

    # answer_type=integer but answer is a choice label A/B/C/D
    if answer_type in {"integer", "numeric", "number"} and is_label:
        errors.append(
            f"ANSWER_TYPE_INTEGER_LABEL_MISMATCH:answer_type={answer_type}+answer={answer_str}"
        )

    if mode == "single_choice":
        if not isinstance(choices, list) or not choices:
            errors.append("CHOICES_EMPTY_FOR_SINGLE_CHOICE")
        else:
            choice_labels = {
                str(c.get("label", "")).strip()
                for c in choices
                if isinstance(c, dict)
            }
            normalized_choice_labels = {lb.strip("()[] .").upper() for lb in choice_labels}
            if answer_str and answer_str.strip("()[] .").upper() not in normalized_choice_labels:
                errors.append(f"CHOICE_LABEL_NOT_IN_CHOICES:answer={answer_str}")

            # semantic_answer must equal the correct choice's value
            if semantic is not None and is_label:
                correct_label_upper = answer_str.strip("()[] .").upper()
                for c in choices:
                    if not isinstance(c, dict):
                        continue
                    lbl = str(c.get("label", "")).strip("()[] .").upper()
                    if lbl == correct_label_upper:
                        val = c.get("value")
                        if val is not None and str(val) != str(semantic):
                            errors.append(
                                f"SEMANTIC_ANSWER_MISMATCH:"
                                f"choice[{correct_label_upper}].value={val}"
                                f"!=semantic_answer={semantic}"
                            )
                        break

    return errors


def validate_answer_contract(payload: dict[str, Any], problem_type_spec: dict[str, Any]) -> list[str]:
    errors: list[str] = list(validate_answer_type_presentation_consistency(payload))
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
        if is_linear_equation_contract(answer_contract):
            pass
        else:
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

    if family == "short_answer" or answer_type == "short_answer" or is_linear_equation_contract(answer_contract):
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
    if is_linear_equation_contract(answer_contract) or equivalence == "linear_equation_equivalent":
        from core.checkers.linear_equation_equivalent_checker import (
            canonicalize_linear_equation,
            check_linear_equation_equivalent_answer,
        )

        answer_str = str(answer).strip()
        if not answer_str:
            errors.append("linear_equation_equivalence_invalid")
        elif canonicalize_linear_equation(answer_str) is None:
            errors.append("linear_equation_equivalence_invalid")
        elif not check_linear_equation_equivalent_answer(answer_str, answer_str):
            errors.append("linear_equation_equivalence_invalid")

    if CHOICE_EMBEDDED_PATTERN.search(question_text) and len(choices_text) > 0:
        errors.append("choices_embedded_in_question_text")

    return sorted(set(errors))
