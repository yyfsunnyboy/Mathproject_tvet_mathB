from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "quadratic_vertex_axis"
TEXTBOOK_EXAMPLE_ID = 12580
DEFAULT_COMPONENT_ID = "src_12580" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_QuadraticFunctions"
FIXED_DOMAIN_KEY = "function.linear_quadratic"
DOMAIN_OPERATION = "quadratic_vertex_axis"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'function.linear_quadratic', 'required_capabilities': ['quadratic_vertex_axis'], 'domain_operation': 'quadratic_vertex_axis', 'problem_type_id': 'quadratic_vertex_axis', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'coeffs': [3, 18, 29]}, {'coeffs': [1, 10, 22]}, {'coeffs': [2, 0, 3]}, {'coeffs': [-2, -12, -17]}, {'coeffs': [-1, 0, -6]}, {'coeffs': [-1, -10, -31]}, {'coeffs': [-2, -20, -55]}, {'coeffs': [-1, -4, -10]}, {'coeffs': [2, -4, -1]}, {'coeffs': [3, 18, 23]}, {'coeffs': [2, 12, 17]}, {'coeffs': [3, -12, 9]}, {'coeffs': [-1, 2, 2]}, {'coeffs': [-1, 8, -17]}, {'coeffs': [3, -12, 14]}, {'coeffs': [2, 4, -3]}, {'coeffs': [-1, 0, -3]}, {'coeffs': [1, 8, 11]}, {'coeffs': [1, -4, 5]}, {'coeffs': [1, 6, 12]}]}}, 'phase1_classification': {'fixed_domain_key': 'function.linear_quadratic', 'required_capabilities': ['quadratic_vertex_axis'], 'domain_operation': 'quadratic_vertex_axis', 'problem_type_id': 'quadratic_vertex_axis', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'coeffs': [3, 18, 29]}, {'coeffs': [1, 10, 22]}, {'coeffs': [2, 0, 3]}, {'coeffs': [-2, -12, -17]}, {'coeffs': [-1, 0, -6]}, {'coeffs': [-1, -10, -31]}, {'coeffs': [-2, -20, -55]}, {'coeffs': [-1, -4, -10]}, {'coeffs': [2, -4, -1]}, {'coeffs': [3, 18, 23]}, {'coeffs': [2, 12, 17]}, {'coeffs': [3, -12, 9]}, {'coeffs': [-1, 2, 2]}, {'coeffs': [-1, 8, -17]}, {'coeffs': [3, -12, 14]}, {'coeffs': [2, 4, -3]}, {'coeffs': [-1, 0, -3]}, {'coeffs': [1, 8, 11]}, {'coeffs': [1, -4, 5]}, {'coeffs': [1, 6, 12]}]}}, 'problem_type_id': 'quadratic_vertex_axis', 'required_capabilities': ['quadratic_vertex_axis'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'coeffs': [3, 18, 29]}, {'coeffs': [1, 10, 22]}, {'coeffs': [2, 0, 3]}, {'coeffs': [-2, -12, -17]}, {'coeffs': [-1, 0, -6]}, {'coeffs': [-1, -10, -31]}, {'coeffs': [-2, -20, -55]}, {'coeffs': [-1, -4, -10]}, {'coeffs': [2, -4, -1]}, {'coeffs': [3, 18, 23]}, {'coeffs': [2, 12, 17]}, {'coeffs': [3, -12, 9]}, {'coeffs': [-1, 2, 2]}, {'coeffs': [-1, 8, -17]}, {'coeffs': [3, -12, 14]}, {'coeffs': [2, 4, -3]}, {'coeffs': [-1, 0, -3]}, {'coeffs': [1, 8, 11]}, {'coeffs': [1, -4, 5]}, {'coeffs': [1, 6, 12]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_QuadraticFunctions', 'fixed_domain_key': 'function.linear_quadratic', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['quadratic_vertex_axis'], 'matched_capabilities': ['quadratic_vertex_axis'], 'selected_operation': 'quadratic_vertex_axis', 'registry_revision': 'promoted-3752585c4f0b', 'domain_module': 'core.domain.promoted.function_linear_quadratic.function_models_domain', 'entrypoint': 'build_function_models_matrix', 'allowed_operations': ['complete_square_items', 'evaluate_function_statements', 'quadratic_always_sign', 'quadratic_extrema', 'quadratic_graph_transformations', 'quadratic_vertex_axis', 'solve_quadratic_applications'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_QuadraticFunctions'}), seed)
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
