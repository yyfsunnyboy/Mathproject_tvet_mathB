"""Backward-compatible facade for ProblemTypeSpec + validators."""

from __future__ import annotations

from core.gencode.problem_type_spec import (
    build_generator_code_prompt,
    build_generator_plan_prompt,
    get_answer_contract,
    get_dependency_contract,
    get_generator_contract,
    get_semantic_contract,
    get_stem_contract,
    get_template_slot,
    list_problem_types_for_skill,
    load_problem_type_spec,
)
from core.gencode.validators import (
    validate_answer_contract,
    validate_generator_payload,
    validate_semantic_and_dependency,
)

# legacy alias
validate_dependency_and_semantic = validate_semantic_and_dependency

__all__ = [
    "load_problem_type_spec",
    "list_problem_types_for_skill",
    "validate_answer_contract",
    "validate_semantic_and_dependency",
    "validate_dependency_and_semantic",
    "validate_generator_payload",
    "build_generator_plan_prompt",
    "build_generator_code_prompt",
]
