from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "evaluate_common_logarithm_items"
TEXTBOOK_EXAMPLE_ID = 12385
DEFAULT_COMPONENT_ID = "src_12385" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CommonLogarithms"
FIXED_DOMAIN_KEY = "algebra.exponent_laws"
DOMAIN_OPERATION = "evaluate_common_logarithm_items"


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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '2.7'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '3.14']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '3.1'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '5.38']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '8.9'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '8.31']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '5.6'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '7.9']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '4.3'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '4.39']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '2.7'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '1.99']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '4.5'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '8.09']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '5.7'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '8.35']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '2.3'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '1.75']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '4.4'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '7.29']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '8.2'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '6.72']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '1.2'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '5.79']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '6.8'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '2.62']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '4.5'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '2.46']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '3.7'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '3.22']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '6.9'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '5.94']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '7.5'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '2.92']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '7.4'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '6.08']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '4.3'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '6.06']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '8.7'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '3.5']]]}]}]}}), seed)
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
