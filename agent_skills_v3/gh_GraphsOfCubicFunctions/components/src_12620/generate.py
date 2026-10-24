from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "cubic_statements"
TEXTBOOK_EXAMPLE_ID = 12620
DEFAULT_COMPONENT_ID = "src_12620" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_GraphsOfCubicFunctions"
FIXED_DOMAIN_KEY = "function.cubic_graph"
DOMAIN_OPERATION = "cubic_statements"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'function.cubic_graph', 'required_capabilities': ['cubic_statements'], 'domain_operation': 'cubic_statements', 'problem_type_id': 'cubic_statements', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'subject': {'type': 'form', 'a': 2, 'p': 3, 'h': 4, 'k': 5}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': 3, 'n': -7}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -1, 'p': -3, 'h': 1, 'k': 4}, 'statements': [{'kind': 'local_line', 'x0': 1, 'm': -1, 'n': 7}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 2, 'p': 5, 'h': 4, 'k': -6}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': 4, 'n': -26}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 1, 'p': -1, 'h': 5, 'k': -4}, 'statements': [{'kind': 'local_line', 'x0': 5, 'm': -1, 'n': 2}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -3, 'p': 2, 'h': 3, 'k': -3}, 'statements': [{'kind': 'local_line', 'x0': 3, 'm': 2, 'n': -9}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': -3, 'h': -4, 'k': 4}, 'statements': [{'kind': 'local_line', 'x0': -4, 'm': -3, 'n': -6}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -3, 'p': -2, 'h': -4, 'k': -5}, 'statements': [{'kind': 'local_line', 'x0': -4, 'm': -3, 'n': -13}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': 1, 'h': -5, 'k': 0}, 'statements': [{'kind': 'local_line', 'x0': -5, 'm': 1, 'n': 5}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 2, 'p': 5, 'h': 4, 'k': -3}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': 4, 'n': -23}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 1, 'p': 5, 'h': -2, 'k': 3}, 'statements': [{'kind': 'local_line', 'x0': -2, 'm': 7, 'n': 13}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 2, 'p': -1, 'h': 0, 'k': 1}, 'statements': [{'kind': 'local_line', 'x0': 0, 'm': -1, 'n': 1}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 3, 'p': -3, 'h': 4, 'k': 1}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': -3, 'n': 13}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 1, 'p': 4, 'h': -3, 'k': 1}, 'statements': [{'kind': 'local_line', 'x0': -3, 'm': 4, 'n': 11}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -3, 'p': 6, 'h': 1, 'k': -1}, 'statements': [{'kind': 'local_line', 'x0': 1, 'm': 6, 'n': -7}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': 4, 'h': 2, 'k': 5}, 'statements': [{'kind': 'local_line', 'x0': 2, 'm': 4, 'n': 0}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 3, 'p': -5, 'h': 4, 'k': 3}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': -5, 'n': 23}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': 3, 'h': -1, 'k': -1}, 'statements': [{'kind': 'local_line', 'x0': -1, 'm': 2, 'n': 2}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 3, 'p': 1, 'h': 5, 'k': 2}, 'statements': [{'kind': 'local_line', 'x0': 5, 'm': 1, 'n': -2}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 1, 'p': -2, 'h': -1, 'k': -1}, 'statements': [{'kind': 'local_line', 'x0': -1, 'm': 0, 'n': -3}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': 3, 'h': -1, 'k': -6}, 'statements': [{'kind': 'local_line', 'x0': -1, 'm': 3, 'n': -1}], 'mode': 'truth'}]}}, 'phase1_classification': {'fixed_domain_key': 'function.cubic_graph', 'required_capabilities': ['cubic_statements'], 'domain_operation': 'cubic_statements', 'problem_type_id': 'cubic_statements', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'subject': {'type': 'form', 'a': 2, 'p': 3, 'h': 4, 'k': 5}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': 3, 'n': -7}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -1, 'p': -3, 'h': 1, 'k': 4}, 'statements': [{'kind': 'local_line', 'x0': 1, 'm': -1, 'n': 7}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 2, 'p': 5, 'h': 4, 'k': -6}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': 4, 'n': -26}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 1, 'p': -1, 'h': 5, 'k': -4}, 'statements': [{'kind': 'local_line', 'x0': 5, 'm': -1, 'n': 2}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -3, 'p': 2, 'h': 3, 'k': -3}, 'statements': [{'kind': 'local_line', 'x0': 3, 'm': 2, 'n': -9}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': -3, 'h': -4, 'k': 4}, 'statements': [{'kind': 'local_line', 'x0': -4, 'm': -3, 'n': -6}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -3, 'p': -2, 'h': -4, 'k': -5}, 'statements': [{'kind': 'local_line', 'x0': -4, 'm': -3, 'n': -13}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': 1, 'h': -5, 'k': 0}, 'statements': [{'kind': 'local_line', 'x0': -5, 'm': 1, 'n': 5}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 2, 'p': 5, 'h': 4, 'k': -3}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': 4, 'n': -23}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 1, 'p': 5, 'h': -2, 'k': 3}, 'statements': [{'kind': 'local_line', 'x0': -2, 'm': 7, 'n': 13}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 2, 'p': -1, 'h': 0, 'k': 1}, 'statements': [{'kind': 'local_line', 'x0': 0, 'm': -1, 'n': 1}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 3, 'p': -3, 'h': 4, 'k': 1}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': -3, 'n': 13}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 1, 'p': 4, 'h': -3, 'k': 1}, 'statements': [{'kind': 'local_line', 'x0': -3, 'm': 4, 'n': 11}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -3, 'p': 6, 'h': 1, 'k': -1}, 'statements': [{'kind': 'local_line', 'x0': 1, 'm': 6, 'n': -7}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': 4, 'h': 2, 'k': 5}, 'statements': [{'kind': 'local_line', 'x0': 2, 'm': 4, 'n': 0}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 3, 'p': -5, 'h': 4, 'k': 3}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': -5, 'n': 23}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': 3, 'h': -1, 'k': -1}, 'statements': [{'kind': 'local_line', 'x0': -1, 'm': 2, 'n': 2}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 3, 'p': 1, 'h': 5, 'k': 2}, 'statements': [{'kind': 'local_line', 'x0': 5, 'm': 1, 'n': -2}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 1, 'p': -2, 'h': -1, 'k': -1}, 'statements': [{'kind': 'local_line', 'x0': -1, 'm': 0, 'n': -3}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': 3, 'h': -1, 'k': -6}, 'statements': [{'kind': 'local_line', 'x0': -1, 'm': 3, 'n': -1}], 'mode': 'truth'}]}}, 'problem_type_id': 'cubic_statements', 'required_capabilities': ['cubic_statements'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'subject': {'type': 'form', 'a': 2, 'p': 3, 'h': 4, 'k': 5}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': 3, 'n': -7}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -1, 'p': -3, 'h': 1, 'k': 4}, 'statements': [{'kind': 'local_line', 'x0': 1, 'm': -1, 'n': 7}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 2, 'p': 5, 'h': 4, 'k': -6}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': 4, 'n': -26}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 1, 'p': -1, 'h': 5, 'k': -4}, 'statements': [{'kind': 'local_line', 'x0': 5, 'm': -1, 'n': 2}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -3, 'p': 2, 'h': 3, 'k': -3}, 'statements': [{'kind': 'local_line', 'x0': 3, 'm': 2, 'n': -9}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': -3, 'h': -4, 'k': 4}, 'statements': [{'kind': 'local_line', 'x0': -4, 'm': -3, 'n': -6}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -3, 'p': -2, 'h': -4, 'k': -5}, 'statements': [{'kind': 'local_line', 'x0': -4, 'm': -3, 'n': -13}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': 1, 'h': -5, 'k': 0}, 'statements': [{'kind': 'local_line', 'x0': -5, 'm': 1, 'n': 5}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 2, 'p': 5, 'h': 4, 'k': -3}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': 4, 'n': -23}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 1, 'p': 5, 'h': -2, 'k': 3}, 'statements': [{'kind': 'local_line', 'x0': -2, 'm': 7, 'n': 13}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 2, 'p': -1, 'h': 0, 'k': 1}, 'statements': [{'kind': 'local_line', 'x0': 0, 'm': -1, 'n': 1}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 3, 'p': -3, 'h': 4, 'k': 1}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': -3, 'n': 13}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 1, 'p': 4, 'h': -3, 'k': 1}, 'statements': [{'kind': 'local_line', 'x0': -3, 'm': 4, 'n': 11}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -3, 'p': 6, 'h': 1, 'k': -1}, 'statements': [{'kind': 'local_line', 'x0': 1, 'm': 6, 'n': -7}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': 4, 'h': 2, 'k': 5}, 'statements': [{'kind': 'local_line', 'x0': 2, 'm': 4, 'n': 0}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 3, 'p': -5, 'h': 4, 'k': 3}, 'statements': [{'kind': 'local_line', 'x0': 4, 'm': -5, 'n': 23}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': 3, 'h': -1, 'k': -1}, 'statements': [{'kind': 'local_line', 'x0': -1, 'm': 2, 'n': 2}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 3, 'p': 1, 'h': 5, 'k': 2}, 'statements': [{'kind': 'local_line', 'x0': 5, 'm': 1, 'n': -2}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': 1, 'p': -2, 'h': -1, 'k': -1}, 'statements': [{'kind': 'local_line', 'x0': -1, 'm': 0, 'n': -3}], 'mode': 'truth'}, {'subject': {'type': 'form', 'a': -2, 'p': 3, 'h': -1, 'k': -6}, 'statements': [{'kind': 'local_line', 'x0': -1, 'm': 3, 'n': -1}], 'mode': 'truth'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_GraphsOfCubicFunctions', 'fixed_domain_key': 'function.cubic_graph', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['cubic_statements'], 'matched_capabilities': ['cubic_statements'], 'selected_operation': 'cubic_statements', 'registry_revision': 'promoted-870e318c51b6', 'domain_module': 'core.domain.promoted.function_cubic.cubic_domain', 'entrypoint': 'build_cubic_graph_matrix', 'allowed_operations': ['cubic_center_form', 'cubic_curve_matching', 'cubic_from_conditions', 'cubic_statements'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_GraphsOfCubicFunctions'}), seed)
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
