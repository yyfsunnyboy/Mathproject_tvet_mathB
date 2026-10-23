from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "evaluate_common_logarithm_items"
TEXTBOOK_EXAMPLE_ID = 12390
DEFAULT_COMPONENT_ID = "src_12390" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.02'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '120']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.86'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '497']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.96'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '281']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.37'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '127']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.68'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '971']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.08'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '384']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.68'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '347']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.17'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '225']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.12'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '456']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.21'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '726']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.76'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '429']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.49'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '594']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.55'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '927']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.3'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '437']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.26'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '865']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.16'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '263']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.28'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '541']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.89'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '268']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.67'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '731']]]}]}, {'stem': '', 'items': [{'kind': 'as_power_of_ten', 'value': '0.2'}, {'kind': 'expr', 'tree': ['pow', ['n', '10'], ['log', ['n', '882']]]}]}]}}), seed)
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
