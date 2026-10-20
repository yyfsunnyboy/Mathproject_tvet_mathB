from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "solve_cooling_initial_temperature"
TEXTBOOK_EXAMPLE_ID = 12372
DEFAULT_COMPONENT_ID = "src_12372" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RealExponentsAndLaws"
FIXED_DOMAIN_KEY = "algebra.exponent_laws"
DOMAIN_OPERATION = "solve_cooling_initial_temperature"


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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'ambient': '30', 'measured': '55.6', 'minutes': 3, 'decay_base': '1.25'}, {'ambient': '25', 'measured': '43', 'minutes': 3, 'decay_base': '2'}, {'ambient': '25', 'measured': '62', 'minutes': 2, 'decay_base': '2'}, {'ambient': '25', 'measured': '44.6', 'minutes': 4, 'decay_base': '1.5'}, {'ambient': '20', 'measured': '42.9', 'minutes': 5, 'decay_base': '1.25'}, {'ambient': '30', 'measured': '41.1', 'minutes': 5, 'decay_base': '1.25'}, {'ambient': '20', 'measured': '47.9', 'minutes': 4, 'decay_base': '1.25'}, {'ambient': '25', 'measured': '60.9', 'minutes': 3, 'decay_base': '1.2'}, {'ambient': '30', 'measured': '94', 'minutes': 2, 'decay_base': '1.25'}, {'ambient': '20', 'measured': '115.4', 'minutes': 2, 'decay_base': '1.25'}, {'ambient': '25', 'measured': '29.8', 'minutes': 5, 'decay_base': '2'}, {'ambient': '30', 'measured': '31.3', 'minutes': 5, 'decay_base': '2'}, {'ambient': '35', 'measured': '115.6', 'minutes': 2, 'decay_base': '1.2'}, {'ambient': '35', 'measured': '72.3', 'minutes': 3, 'decay_base': '1.5'}, {'ambient': '25', 'measured': '95.4', 'minutes': 2, 'decay_base': '1.25'}, {'ambient': '20', 'measured': '124.2', 'minutes': 2, 'decay_base': '1.2'}, {'ambient': '25', 'measured': '93.5', 'minutes': 4, 'decay_base': '1.2'}, {'ambient': '35', 'measured': '81.5', 'minutes': 2, 'decay_base': '1.2'}, {'ambient': '30', 'measured': '37.4', 'minutes': 4, 'decay_base': '2'}, {'ambient': '30', 'measured': '60.1', 'minutes': 5, 'decay_base': '1.2'}]}}), seed)
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
