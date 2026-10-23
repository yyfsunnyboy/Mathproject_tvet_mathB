from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "evaluate_conditional_exponent_values"
TEXTBOOK_EXAMPLE_ID = 12399
DEFAULT_COMPONENT_ID = "src_12399" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CommonLogarithms"
FIXED_DOMAIN_KEY = "algebra.exponent_laws"
DOMAIN_OPERATION = "evaluate_conditional_exponent_values"


def _materialize_generation_constraints(raw_constraints: dict[str, Any], seed: int | None) -> dict[str, Any]:
    constraints = deepcopy(raw_constraints)
    generation_constraints = constraints.pop("generation_constraints", None)
    if generation_constraints is None:
        return constraints
    if not isinstance(generation_constraints, dict):
        raise ValueError("generation_constraints must be a dict")
    variants = generation_constraints.get("variants")
    if not isinstance(variants, list) or not variants:
        raise ValueError("generation_constraints.variants must be a non-empty list")
    index = 0 if seed is None else int(seed) % len(variants)
    selected = variants[index]
    if not isinstance(selected, dict):
        raise ValueError("generation_constraints variant must be a dict")
    selected_constraints = selected.get("constraints", selected)
    if not isinstance(selected_constraints, dict):
        raise ValueError("generation_constraints variant constraints must be a dict")
    forbidden = {"answer", "correct_answer", "canonical_answer", "answer_contract", "checker", "checker_key"}
    if forbidden & set(selected_constraints):
        raise ValueError("generation_constraints must not define answer or checker authority")
    constraints.update(deepcopy(selected_constraints))
    return constraints


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    resolution = resolve_domain_authority(SKILL_ID, selected_operation=DOMAIN_OPERATION)
    if (
        resolution.binding_status != "confirmed"
        or resolution.fixed_domain_key != FIXED_DOMAIN_KEY
        or resolution.selected_operation != DOMAIN_OPERATION
    ):
        raise RuntimeError(
            "domain_binding_mismatch:"
            f"{resolution.binding_status}:{resolution.fixed_domain_key}:{resolution.selected_operation}"
        )

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '7']]}, 'roots': ['log(7)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '29']]}, 'roots': ['log(29)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '19']]}, 'roots': ['log(19)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '23']]}, 'roots': ['log(23)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '43']]}, 'roots': ['log(43)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '31']]}, 'roots': ['log(31)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '59']]}, 'roots': ['log(59)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '37']]}, 'roots': ['log(37)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '61']]}, 'roots': ['log(61)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '3']]}, 'roots': ['log(3)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '2']]}, 'roots': ['log(2)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '11']]}, 'roots': ['log(11)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '41']]}, 'roots': ['log(41)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '47']]}, 'roots': ['log(47)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '53']]}, 'roots': ['log(53)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '5']]}, 'roots': ['log(5)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '13']]}, 'roots': ['log(13)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 't', 'condition': {'lhs': ['sym', 't'], 'rhs': ['log', ['n', '17']]}, 'roots': ['log(17)/log(10)'], 'targets': [['pow', ['n', '10'], ['sym', 't']], ['add', ['pow', ['n', '100'], ['sym', 't']], ['pow', ['n', '10'], ['neg', ['sym', 't']]]]], 'assume_positive': False}]}}), seed)
    constraints["skill_id"] = SKILL_ID
    _matrix, payload = dispatch_registered_operation(
        resolution.fixed_domain_key,
        DOMAIN_OPERATION,
        seed=seed,
        constraints=constraints,
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    if component_id:
        payload["component_id"] = component_id
    payload["skill_id"] = SKILL_ID
    payload["textbook_example_id"] = TEXTBOOK_EXAMPLE_ID
    payload["domain_resolution"] = {
        "fixed_domain_key": resolution.fixed_domain_key,
        "resolution_source": resolution.resolution_source,
        "binding_status": resolution.binding_status,
        "selected_operation": resolution.selected_operation,
        "registry_revision": resolution.registry_revision,
    }
    payload["seed"] = seed
    return payload
