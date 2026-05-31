from __future__ import annotations

import re
from typing import Any

from core.gencode.problem_type_spec import get_dependency_contract, get_semantic_contract
from core.gencode.validators.answer_contract_validator import LABEL_ONLY_PATTERN, _choices_to_texts
from core.gencode.validators.condition_target_dependency import validate_condition_target_dependency


def validate_dependency_contract(payload: dict[str, Any], problem_type_spec: dict[str, Any]) -> list[str]:
    return validate_condition_target_dependency(payload, problem_type_spec)


def validate_semantic_contract(payload: dict[str, Any], problem_type_spec: dict[str, Any]) -> list[str]:
    errors = list(validate_condition_target_dependency(payload, problem_type_spec))
    semantic_contract = get_semantic_contract(problem_type_spec)
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    derivation = metadata.get("derivation") if isinstance(metadata.get("derivation"), list) else []
    reject_if = semantic_contract.get("reject_if", []) if isinstance(semantic_contract.get("reject_if"), list) else []

    if "ambiguous_answer" in reject_if and len(derivation) < 1:
        errors.append("ambiguous_answer")

    if "multiple_correct_choices_when_single_choice" in reject_if or "no_correct_choice" in reject_if:
        choices = _choices_to_texts(payload.get("choices"))
        answer = str(payload.get("answer", "")).strip()
        if choices:
            if LABEL_ONLY_PATTERN.match(answer):
                idx = ord(answer.strip("()[] .").upper()) - ord("A")
                correct_count = 1 if 0 <= idx < len(choices) else 0
            else:
                correct_count = sum(1 for c in choices if c == answer)
            if "multiple_correct_choices_when_single_choice" in reject_if and correct_count > 1:
                errors.append("multiple_correct_choices_when_single_choice")
            if "no_correct_choice" in reject_if and correct_count != 1:
                errors.append("no_correct_choice")

    return sorted(set(errors))


def validate_semantic_and_dependency(payload: dict[str, Any], problem_type_spec: dict[str, Any]) -> list[str]:
    dependency_contract = get_dependency_contract(problem_type_spec)
    errors = validate_condition_target_dependency(payload, problem_type_spec)
    errors.extend(validate_semantic_contract(payload, problem_type_spec))

    if bool(dependency_contract.get("target_answer_must_depend_on_givens", False)):
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        givens = metadata.get("givens")
        target = metadata.get("target")
        if (
            isinstance(givens, list)
            and givens
            and target
            and re.search(r"[a-zA-Z]", " ".join(str(x) for x in givens if not isinstance(x, dict)))
            and re.fullmatch(r"\s*-?\d+(\.\d+)?\s*", str(target))
        ):
            errors.append("condition_unused_by_target")

    return sorted(set(errors))
