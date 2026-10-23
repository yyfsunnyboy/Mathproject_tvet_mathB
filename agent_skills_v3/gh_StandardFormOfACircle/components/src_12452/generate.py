from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "write_circle_equations"
TEXTBOOK_EXAMPLE_ID = 12452
DEFAULT_COMPONENT_ID = "src_12452" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_StandardFormOfACircle"
FIXED_DOMAIN_KEY = "analytic_geometry.circle_equations"
DOMAIN_OPERATION = "write_circle_equations"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['write_circle_equations'], 'domain_operation': 'write_circle_equations', 'problem_type_id': 'write_circle_equations', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'diameter_param_k', 'center': [4, 1], 'a': [2, 3]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [3, 3], 'a': [-1, 5]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-2, 1], 'a': [-5, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-4, -3], 'a': [-3, -1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [2, -1], 'a': [5, -2]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, -1], 'a': [-3, -4]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [1, -2], 'a': [5, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-2, -3], 'a': [-3, 0]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, 0], 'a': [3, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [3, -2], 'a': [4, -3]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-4, -1], 'a': [-6, -4]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [0, 0], 'a': [3, 3]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, -2], 'a': [0, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-3, 2], 'a': [-1, 5]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [4, -1], 'a': [7, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-4, 1], 'a': [-2, 5]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-3, 2], 'a': [-2, -2]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, 4], 'a': [-2, 4]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-4, -4], 'a': [-8, -3]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, -3], 'a': [1, -6]}]}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['write_circle_equations'], 'domain_operation': 'write_circle_equations', 'problem_type_id': 'write_circle_equations', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'diameter_param_k', 'center': [4, 1], 'a': [2, 3]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [3, 3], 'a': [-1, 5]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-2, 1], 'a': [-5, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-4, -3], 'a': [-3, -1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [2, -1], 'a': [5, -2]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, -1], 'a': [-3, -4]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [1, -2], 'a': [5, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-2, -3], 'a': [-3, 0]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, 0], 'a': [3, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [3, -2], 'a': [4, -3]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-4, -1], 'a': [-6, -4]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [0, 0], 'a': [3, 3]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, -2], 'a': [0, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-3, 2], 'a': [-1, 5]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [4, -1], 'a': [7, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-4, 1], 'a': [-2, 5]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-3, 2], 'a': [-2, -2]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, 4], 'a': [-2, 4]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-4, -4], 'a': [-8, -3]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, -3], 'a': [1, -6]}]}]}}, 'problem_type_id': 'write_circle_equations', 'required_capabilities': ['write_circle_equations'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'kind': 'diameter_param_k', 'center': [4, 1], 'a': [2, 3]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [3, 3], 'a': [-1, 5]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-2, 1], 'a': [-5, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-4, -3], 'a': [-3, -1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [2, -1], 'a': [5, -2]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, -1], 'a': [-3, -4]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [1, -2], 'a': [5, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-2, -3], 'a': [-3, 0]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, 0], 'a': [3, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [3, -2], 'a': [4, -3]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-4, -1], 'a': [-6, -4]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [0, 0], 'a': [3, 3]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, -2], 'a': [0, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-3, 2], 'a': [-1, 5]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [4, -1], 'a': [7, 1]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-4, 1], 'a': [-2, 5]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-3, 2], 'a': [-2, -2]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, 4], 'a': [-2, 4]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-4, -4], 'a': [-8, -3]}]}, {'items': [{'kind': 'diameter_param_k', 'center': [-1, -3], 'a': [1, -6]}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_StandardFormOfACircle', 'fixed_domain_key': 'analytic_geometry.circle_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['write_circle_equations'], 'matched_capabilities': ['write_circle_equations'], 'selected_operation': 'write_circle_equations', 'registry_revision': 'promoted-c27fac060f71', 'domain_module': 'core.domain.promoted.analytic_geometry_circles.circle_equations_domain', 'entrypoint': 'build_circle_equations_matrix', 'allowed_operations': ['evaluate_circle_statement_truth', 'solve_circular_arch_height', 'write_circle_equations'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_StandardFormOfACircle'}), seed)
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
