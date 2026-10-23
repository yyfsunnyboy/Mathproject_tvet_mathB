from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice_label"
PROBLEM_TYPE_ID = "select_nearest_model_value"
TEXTBOOK_EXAMPLE_ID = 12402
DEFAULT_COMPONENT_ID = "src_12402" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CommonLogarithms"
FIXED_DOMAIN_KEY = "algebra.exponent_laws"
DOMAIN_OPERATION = "select_nearest_model_value"


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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'model': 'benford', 'leading_digit': 1, 'options': [{'name': '10%', 'value': 10, 'text': '10%'}, {'name': '20%', 'value': 20, 'text': '20%'}, {'name': '30%', 'value': 30, 'text': '30%'}, {'name': '40%', 'value': 40, 'text': '40%'}, {'name': '50%', 'value': 50, 'text': '50%'}]}, {'model': 'benford', 'leading_digit': 9, 'options': [{'name': '10%', 'value': 10, 'text': '10%'}, {'name': '20%', 'value': 20, 'text': '20%'}, {'name': '30%', 'value': 30, 'text': '30%'}, {'name': '40%', 'value': 40, 'text': '40%'}, {'name': '50%', 'value': 50, 'text': '50%'}]}, {'model': 'benford', 'leading_digit': 3, 'options': [{'name': '10%', 'value': 10, 'text': '10%'}, {'name': '20%', 'value': 20, 'text': '20%'}, {'name': '30%', 'value': 30, 'text': '30%'}, {'name': '40%', 'value': 40, 'text': '40%'}, {'name': '50%', 'value': 50, 'text': '50%'}]}, {'model': 'benford', 'leading_digit': 4, 'options': [{'name': '10%', 'value': 10, 'text': '10%'}, {'name': '20%', 'value': 20, 'text': '20%'}, {'name': '30%', 'value': 30, 'text': '30%'}, {'name': '40%', 'value': 40, 'text': '40%'}, {'name': '50%', 'value': 50, 'text': '50%'}]}, {'model': 'benford', 'leading_digit': 2, 'options': [{'name': '10%', 'value': 10, 'text': '10%'}, {'name': '20%', 'value': 20, 'text': '20%'}, {'name': '30%', 'value': 30, 'text': '30%'}, {'name': '40%', 'value': 40, 'text': '40%'}, {'name': '50%', 'value': 50, 'text': '50%'}]}, {'model': 'benford', 'leading_digit': 8, 'options': [{'name': '10%', 'value': 10, 'text': '10%'}, {'name': '20%', 'value': 20, 'text': '20%'}, {'name': '30%', 'value': 30, 'text': '30%'}, {'name': '40%', 'value': 40, 'text': '40%'}, {'name': '50%', 'value': 50, 'text': '50%'}]}, {'model': 'benford', 'leading_digit': 7, 'options': [{'name': '10%', 'value': 10, 'text': '10%'}, {'name': '20%', 'value': 20, 'text': '20%'}, {'name': '30%', 'value': 30, 'text': '30%'}, {'name': '40%', 'value': 40, 'text': '40%'}, {'name': '50%', 'value': 50, 'text': '50%'}]}, {'model': 'benford', 'leading_digit': 6, 'options': [{'name': '10%', 'value': 10, 'text': '10%'}, {'name': '20%', 'value': 20, 'text': '20%'}, {'name': '30%', 'value': 30, 'text': '30%'}, {'name': '40%', 'value': 40, 'text': '40%'}, {'name': '50%', 'value': 50, 'text': '50%'}]}, {'model': 'benford', 'leading_digit': 5, 'options': [{'name': '10%', 'value': 10, 'text': '10%'}, {'name': '20%', 'value': 20, 'text': '20%'}, {'name': '30%', 'value': 30, 'text': '30%'}, {'name': '40%', 'value': 40, 'text': '40%'}, {'name': '50%', 'value': 50, 'text': '50%'}]}]}}), seed)
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
