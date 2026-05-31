from __future__ import annotations

from typing import Any

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.validators.answer_contract_validator import validate_answer_contract
from core.gencode.validators.condition_target_dependency import validate_condition_target_dependency
from core.gencode.validators.semantic_validator import (
    validate_dependency_contract,
    validate_semantic_and_dependency,
    validate_semantic_contract,
)


def validate_generator_payload(
    payload: dict[str, Any],
    *,
    skill_id: str | None = None,
    problem_type_spec: dict[str, Any] | None = None,
) -> list[str]:
    spec = problem_type_spec
    if spec is None:
        sid = str(skill_id or payload.get("skill_id", "")).strip()
        pt = str(payload.get("problem_type_id", "")).strip()
        spec = load_problem_type_spec(sid, pt, prefer="auto")
    if not spec:
        return ["problem_type_spec_missing"]
    errors = validate_answer_contract(payload, spec)
    errors.extend(validate_dependency_contract(payload, spec))
    errors.extend(validate_semantic_contract(payload, spec))
    return sorted(set(errors))


__all__ = [
    "validate_answer_contract",
    "validate_condition_target_dependency",
    "validate_dependency_contract",
    "validate_semantic_and_dependency",
    "validate_semantic_contract",
    "validate_generator_payload",
]
