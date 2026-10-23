from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice_label"
PROBLEM_TYPE_ID = "evaluate_number_property_statements"
TEXTBOOK_EXAMPLE_ID = 12397
DEFAULT_COMPONENT_ID = "src_12397" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CommonLogarithms"
FIXED_DOMAIN_KEY = "algebra.exponent_laws"
DOMAIN_OPERATION = "evaluate_number_property_statements"


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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'number': {'ten_power': '19.1'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 19}]}, {'number': {'ten_power': '16.1'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 16}]}, {'number': {'ten_power': '14.4'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 14}]}, {'number': {'ten_power': '14.7'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 15}]}, {'number': {'ten_power': '39.7'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 39}]}, {'number': {'ten_power': '27.5'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 27}]}, {'number': {'ten_power': '9.7'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 9}]}, {'number': {'ten_power': '8.6'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 8}]}, {'number': {'ten_power': '27.6'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 27}]}, {'number': {'ten_power': '16.5'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 17}]}, {'number': {'ten_power': '29.6'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 30}]}, {'number': {'ten_power': '26.2'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 26}]}, {'number': {'ten_power': '14.8'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 14}]}, {'number': {'ten_power': '39.6'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 39}]}, {'number': {'ten_power': '26.1'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 26}]}, {'number': {'ten_power': '34.7'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 35}]}, {'number': {'ten_power': '10.1'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 10}]}, {'number': {'ten_power': '9.5'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 10}]}, {'number': {'ten_power': '12.5'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 12}]}, {'number': {'ten_power': '40.4'}, 'statements': [{'kind': 'integer_part_digits', 'claim': 41}]}]}}), seed)
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
