from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "cubic_center_form"
TEXTBOOK_EXAMPLE_ID = 12622
DEFAULT_COMPONENT_ID = "src_12622" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_GraphsOfCubicFunctions"
FIXED_DOMAIN_KEY = "function.cubic_graph"
DOMAIN_OPERATION = "cubic_center_form"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'function.cubic_graph', 'required_capabilities': ['cubic_center_form'], 'domain_operation': 'cubic_center_form', 'problem_type_id': 'cubic_center_form', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'to_form', 'coeffs': [-1, -6, 2, -3]}, {'kind': 'to_form', 'coeffs': [1, 1, -1, 1]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, -3, 0, -7]}, {'kind': 'to_form', 'coeffs': [1, 3, 4, 2]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-1, -6, 7, 9]}, {'kind': 'to_form', 'coeffs': [2, -18, -5, 3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-1, -3, -9, -3]}, {'kind': 'to_form', 'coeffs': [1, 2, -2, 4]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 9, 7, -1]}, {'kind': 'to_form', 'coeffs': [-2, 12, 2, -5]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-1, 9, -5, 8]}, {'kind': 'to_form', 'coeffs': [3, 0, -9, -2]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 0, 1, -1]}, {'kind': 'to_form', 'coeffs': [1, 9, 5, 3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 0, -7, -9]}, {'kind': 'to_form', 'coeffs': [1, 0, -7, 3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [2, 18, 1, 5]}, {'kind': 'to_form', 'coeffs': [1, -2, -2, -3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [2, -6, 5, -5]}, {'kind': 'to_form', 'coeffs': [1, -2, 1, -4]}]}, {'items': [{'kind': 'to_form', 'coeffs': [2, 6, -8, 5]}, {'kind': 'to_form', 'coeffs': [-2, -6, 4, -4]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-2, 18, -9, 9]}, {'kind': 'to_form', 'coeffs': [-1, -9, -7, 3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-2, 18, 8, -3]}, {'kind': 'to_form', 'coeffs': [-1, -3, -3, 6]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 6, -7, 9]}, {'kind': 'to_form', 'coeffs': [-1, -3, 7, 7]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-1, 6, -8, -9]}, {'kind': 'to_form', 'coeffs': [1, -6, 2, -8]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, -2, 1, 3]}, {'kind': 'to_form', 'coeffs': [3, -27, 9, -4]}]}, {'items': [{'kind': 'to_form', 'coeffs': [2, 18, 4, 5]}, {'kind': 'to_form', 'coeffs': [-1, -9, -3, -3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, -9, -4, 3]}, {'kind': 'to_form', 'coeffs': [1, -6, -2, -2]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 1, -2, -2]}, {'kind': 'to_form', 'coeffs': [1, -3, 6, 8]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 3, -1, 7]}, {'kind': 'to_form', 'coeffs': [3, -18, 0, -1]}]}]}}, 'phase1_classification': {'fixed_domain_key': 'function.cubic_graph', 'required_capabilities': ['cubic_center_form'], 'domain_operation': 'cubic_center_form', 'problem_type_id': 'cubic_center_form', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'to_form', 'coeffs': [-1, -6, 2, -3]}, {'kind': 'to_form', 'coeffs': [1, 1, -1, 1]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, -3, 0, -7]}, {'kind': 'to_form', 'coeffs': [1, 3, 4, 2]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-1, -6, 7, 9]}, {'kind': 'to_form', 'coeffs': [2, -18, -5, 3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-1, -3, -9, -3]}, {'kind': 'to_form', 'coeffs': [1, 2, -2, 4]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 9, 7, -1]}, {'kind': 'to_form', 'coeffs': [-2, 12, 2, -5]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-1, 9, -5, 8]}, {'kind': 'to_form', 'coeffs': [3, 0, -9, -2]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 0, 1, -1]}, {'kind': 'to_form', 'coeffs': [1, 9, 5, 3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 0, -7, -9]}, {'kind': 'to_form', 'coeffs': [1, 0, -7, 3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [2, 18, 1, 5]}, {'kind': 'to_form', 'coeffs': [1, -2, -2, -3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [2, -6, 5, -5]}, {'kind': 'to_form', 'coeffs': [1, -2, 1, -4]}]}, {'items': [{'kind': 'to_form', 'coeffs': [2, 6, -8, 5]}, {'kind': 'to_form', 'coeffs': [-2, -6, 4, -4]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-2, 18, -9, 9]}, {'kind': 'to_form', 'coeffs': [-1, -9, -7, 3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-2, 18, 8, -3]}, {'kind': 'to_form', 'coeffs': [-1, -3, -3, 6]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 6, -7, 9]}, {'kind': 'to_form', 'coeffs': [-1, -3, 7, 7]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-1, 6, -8, -9]}, {'kind': 'to_form', 'coeffs': [1, -6, 2, -8]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, -2, 1, 3]}, {'kind': 'to_form', 'coeffs': [3, -27, 9, -4]}]}, {'items': [{'kind': 'to_form', 'coeffs': [2, 18, 4, 5]}, {'kind': 'to_form', 'coeffs': [-1, -9, -3, -3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, -9, -4, 3]}, {'kind': 'to_form', 'coeffs': [1, -6, -2, -2]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 1, -2, -2]}, {'kind': 'to_form', 'coeffs': [1, -3, 6, 8]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 3, -1, 7]}, {'kind': 'to_form', 'coeffs': [3, -18, 0, -1]}]}]}}, 'problem_type_id': 'cubic_center_form', 'required_capabilities': ['cubic_center_form'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'kind': 'to_form', 'coeffs': [-1, -6, 2, -3]}, {'kind': 'to_form', 'coeffs': [1, 1, -1, 1]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, -3, 0, -7]}, {'kind': 'to_form', 'coeffs': [1, 3, 4, 2]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-1, -6, 7, 9]}, {'kind': 'to_form', 'coeffs': [2, -18, -5, 3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-1, -3, -9, -3]}, {'kind': 'to_form', 'coeffs': [1, 2, -2, 4]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 9, 7, -1]}, {'kind': 'to_form', 'coeffs': [-2, 12, 2, -5]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-1, 9, -5, 8]}, {'kind': 'to_form', 'coeffs': [3, 0, -9, -2]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 0, 1, -1]}, {'kind': 'to_form', 'coeffs': [1, 9, 5, 3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 0, -7, -9]}, {'kind': 'to_form', 'coeffs': [1, 0, -7, 3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [2, 18, 1, 5]}, {'kind': 'to_form', 'coeffs': [1, -2, -2, -3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [2, -6, 5, -5]}, {'kind': 'to_form', 'coeffs': [1, -2, 1, -4]}]}, {'items': [{'kind': 'to_form', 'coeffs': [2, 6, -8, 5]}, {'kind': 'to_form', 'coeffs': [-2, -6, 4, -4]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-2, 18, -9, 9]}, {'kind': 'to_form', 'coeffs': [-1, -9, -7, 3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-2, 18, 8, -3]}, {'kind': 'to_form', 'coeffs': [-1, -3, -3, 6]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 6, -7, 9]}, {'kind': 'to_form', 'coeffs': [-1, -3, 7, 7]}]}, {'items': [{'kind': 'to_form', 'coeffs': [-1, 6, -8, -9]}, {'kind': 'to_form', 'coeffs': [1, -6, 2, -8]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, -2, 1, 3]}, {'kind': 'to_form', 'coeffs': [3, -27, 9, -4]}]}, {'items': [{'kind': 'to_form', 'coeffs': [2, 18, 4, 5]}, {'kind': 'to_form', 'coeffs': [-1, -9, -3, -3]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, -9, -4, 3]}, {'kind': 'to_form', 'coeffs': [1, -6, -2, -2]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 1, -2, -2]}, {'kind': 'to_form', 'coeffs': [1, -3, 6, 8]}]}, {'items': [{'kind': 'to_form', 'coeffs': [1, 3, -1, 7]}, {'kind': 'to_form', 'coeffs': [3, -18, 0, -1]}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_GraphsOfCubicFunctions', 'fixed_domain_key': 'function.cubic_graph', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['cubic_center_form'], 'matched_capabilities': ['cubic_center_form'], 'selected_operation': 'cubic_center_form', 'registry_revision': 'promoted-870e318c51b6', 'domain_module': 'core.domain.promoted.function_cubic.cubic_domain', 'entrypoint': 'build_cubic_graph_matrix', 'allowed_operations': ['cubic_center_form', 'cubic_curve_matching', 'cubic_from_conditions', 'cubic_statements'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_GraphsOfCubicFunctions'}), seed)
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
