"""Validation helpers for vocational math B4 payloads and values."""

from __future__ import annotations

import re


_REQUIRED_PAYLOAD_KEYS = {
    "question_text",
    "choices",
    "answer",
    "explanation",
    "skill_id",
    "subskill_id",
    "problem_type_id",
    "generator_key",
    "difficulty",
    "diagnosis_tags",
    "remediation_candidates",
    "source_style_refs",
}

_PLACEHOLDER_TOKENS = [
    "[BLANK]",
    "[FORMULA_MISSING]",
    "[FORMULA_IMAGE",
    "[WORD_EQUATION_UNPARSED]",
    "□",
    "＿＿",
]


def validate_positive_integer(value: object, name: str = "value") -> bool:
    """Validate value is an integer > 0."""
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"validate_positive_integer: {name} must be a positive integer.")
    return True


def validate_nonnegative_integer(value: object, name: str = "value") -> bool:
    """Validate value is an integer >= 0."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"validate_nonnegative_integer: {name} must be a nonnegative integer.")
    return True


def validate_n_ge_r(n: int, r: int) -> bool:
    """Validate n and r are nonnegative integers with n >= r."""
    validate_nonnegative_integer(n, "n")
    validate_nonnegative_integer(r, "r")
    if n < r:
        raise ValueError("validate_n_ge_r: n must be >= r.")
    return True


def validate_choices_unique(choices: list) -> bool:
    """Validate choices is a list with unique entries."""
    if not isinstance(choices, list) or not choices:
        raise ValueError("validate_choices_unique: choices must be a non-empty list.")
    if len(set(choices)) != len(choices):
        raise ValueError("validate_choices_unique: choices must be unique.")
    return True


def validate_answer_in_choices(answer: object, choices: list) -> bool:
    """Validate answer appears in choices."""
    if not isinstance(choices, list) or not choices:
        raise ValueError("validate_answer_in_choices: choices must be a non-empty list.")
    if answer not in choices:
        raise ValueError("validate_answer_in_choices: answer must be included in choices.")
    return True


def validate_no_unfilled_placeholder(text: str) -> bool:
    """Validate text contains no unfilled placeholder markers."""
    if not isinstance(text, str):
        raise ValueError("validate_no_unfilled_placeholder: text must be a string.")
    for token in _PLACEHOLDER_TOKENS:
        if token in text:
            raise ValueError(f"validate_no_unfilled_placeholder: found placeholder token {token}.")
    return True


def validate_integer_answer(answer: object) -> bool:
    """Validate answer is int-like (int or integer string)."""
    if isinstance(answer, bool):
        raise ValueError("validate_integer_answer: bool is not an integer answer.")
    if isinstance(answer, int):
        return True
    if isinstance(answer, str) and re.fullmatch(r"[+-]?\d+", answer.strip()):
        return True
    raise ValueError("validate_integer_answer: answer must be an integer or integer-form string.")


def validate_expression_answer(answer: object) -> bool:
    """Validate answer is a non-empty expression-like string."""
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("validate_expression_answer: answer must be a non-empty string.")
    if not re.search(r"[0-9a-zA-ZxX+\-*/^() ]", answer):
        raise ValueError("validate_expression_answer: answer does not look like a math expression.")
    return True


def validate_polynomial_answer(answer: object) -> bool:
    """Validate answer is a polynomial-like expression string."""
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("validate_polynomial_answer: answer must be a non-empty string.")
    normalized = answer.replace(" ", "")
    if "x" not in normalized and "X" not in normalized:
        raise ValueError("validate_polynomial_answer: polynomial answer must include variable x.")
    if not re.fullmatch(r"[0-9xX+\-*/^()]+", normalized):
        raise ValueError("validate_polynomial_answer: contains invalid polynomial characters.")
    return True


def validate_parameter_tuple_not_seen(parameter_tuple: tuple, seen: set) -> bool:
    """Validate parameter tuple has not appeared in seen set."""
    if not isinstance(parameter_tuple, tuple):
        raise ValueError("validate_parameter_tuple_not_seen: parameter_tuple must be a tuple.")
    if not isinstance(seen, set):
        raise ValueError("validate_parameter_tuple_not_seen: seen must be a set.")
    if parameter_tuple in seen:
        raise ValueError("validate_parameter_tuple_not_seen: parameter tuple already seen.")
    return True


def validate_problem_payload_contract(payload: dict) -> bool:
    """Validate payload includes all required contract keys."""
    if not isinstance(payload, dict):
        raise ValueError("validate_problem_payload_contract: payload must be a dict.")
    missing = sorted(_REQUIRED_PAYLOAD_KEYS - set(payload.keys()))
    if missing:
        raise ValueError(f"validate_problem_payload_contract: missing keys: {', '.join(missing)}")
    return True
