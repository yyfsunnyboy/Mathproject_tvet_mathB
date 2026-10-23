from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "analyze_general_circle"
TEXTBOOK_EXAMPLE_ID = 12460
DEFAULT_COMPONENT_ID = "src_12460" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_GeneralFormOfACircle"
FIXED_DOMAIN_KEY = "analytic_geometry.circle_equations"
DOMAIN_OPERATION = "analyze_general_circle"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['analyze_general_circle'], 'domain_operation': 'analyze_general_circle', 'problem_type_id': 'analyze_general_circle', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': -2, 'f1': 2, 'r2': 9}]}, {'items': [{'kind': 'param_radius_center', 'd': 4, 'e1': 2, 'f1': 0, 'r2': 5}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': 2, 'f1': 3, 'r2': 7}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': 2, 'f1': -3, 'r2': 19}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': -2, 'f1': 3, 'r2': 7}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': -2, 'f1': 5, 'r2': 15}]}, {'items': [{'kind': 'param_radius_center', 'd': -4, 'e1': 2, 'f1': 1, 'r2': 16}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': 2, 'f1': 0, 'r2': 13}]}, {'items': [{'kind': 'param_radius_center', 'd': 4, 'e1': 2, 'f1': 3, 'r2': 8}]}, {'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': 2, 'f1': -3, 'r2': 11}]}, {'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': -2, 'f1': 2, 'r2': 25}]}, {'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': 2, 'f1': 0, 'r2': 5}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': -2, 'f1': 1, 'r2': 21}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': -2, 'f1': 4, 'r2': 21}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': 2, 'f1': 3, 'r2': 13}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': 2, 'f1': -6, 'r2': 4}]}, {'items': [{'kind': 'param_radius_center', 'd': -4, 'e1': 2, 'f1': -1, 'r2': 6}]}, {'items': [{'kind': 'param_radius_center', 'd': 4, 'e1': 2, 'f1': -2, 'r2': 12}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': -2, 'f1': 2, 'r2': 9}]}, {'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': 2, 'f1': 3, 'r2': 11}]}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['analyze_general_circle'], 'domain_operation': 'analyze_general_circle', 'problem_type_id': 'analyze_general_circle', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': -2, 'f1': 2, 'r2': 9}]}, {'items': [{'kind': 'param_radius_center', 'd': 4, 'e1': 2, 'f1': 0, 'r2': 5}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': 2, 'f1': 3, 'r2': 7}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': 2, 'f1': -3, 'r2': 19}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': -2, 'f1': 3, 'r2': 7}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': -2, 'f1': 5, 'r2': 15}]}, {'items': [{'kind': 'param_radius_center', 'd': -4, 'e1': 2, 'f1': 1, 'r2': 16}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': 2, 'f1': 0, 'r2': 13}]}, {'items': [{'kind': 'param_radius_center', 'd': 4, 'e1': 2, 'f1': 3, 'r2': 8}]}, {'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': 2, 'f1': -3, 'r2': 11}]}, {'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': -2, 'f1': 2, 'r2': 25}]}, {'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': 2, 'f1': 0, 'r2': 5}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': -2, 'f1': 1, 'r2': 21}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': -2, 'f1': 4, 'r2': 21}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': 2, 'f1': 3, 'r2': 13}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': 2, 'f1': -6, 'r2': 4}]}, {'items': [{'kind': 'param_radius_center', 'd': -4, 'e1': 2, 'f1': -1, 'r2': 6}]}, {'items': [{'kind': 'param_radius_center', 'd': 4, 'e1': 2, 'f1': -2, 'r2': 12}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': -2, 'f1': 2, 'r2': 9}]}, {'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': 2, 'f1': 3, 'r2': 11}]}]}}, 'problem_type_id': 'analyze_general_circle', 'required_capabilities': ['analyze_general_circle'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': -2, 'f1': 2, 'r2': 9}]}, {'items': [{'kind': 'param_radius_center', 'd': 4, 'e1': 2, 'f1': 0, 'r2': 5}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': 2, 'f1': 3, 'r2': 7}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': 2, 'f1': -3, 'r2': 19}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': -2, 'f1': 3, 'r2': 7}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': -2, 'f1': 5, 'r2': 15}]}, {'items': [{'kind': 'param_radius_center', 'd': -4, 'e1': 2, 'f1': 1, 'r2': 16}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': 2, 'f1': 0, 'r2': 13}]}, {'items': [{'kind': 'param_radius_center', 'd': 4, 'e1': 2, 'f1': 3, 'r2': 8}]}, {'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': 2, 'f1': -3, 'r2': 11}]}, {'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': -2, 'f1': 2, 'r2': 25}]}, {'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': 2, 'f1': 0, 'r2': 5}]}, {'items': [{'kind': 'param_radius_center', 'd': -6, 'e1': -2, 'f1': 1, 'r2': 21}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': -2, 'f1': 4, 'r2': 21}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': 2, 'f1': 3, 'r2': 13}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': 2, 'f1': -6, 'r2': 4}]}, {'items': [{'kind': 'param_radius_center', 'd': -4, 'e1': 2, 'f1': -1, 'r2': 6}]}, {'items': [{'kind': 'param_radius_center', 'd': 4, 'e1': 2, 'f1': -2, 'r2': 12}]}, {'items': [{'kind': 'param_radius_center', 'd': 6, 'e1': -2, 'f1': 2, 'r2': 9}]}, {'items': [{'kind': 'param_radius_center', 'd': 2, 'e1': 2, 'f1': 3, 'r2': 11}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_GeneralFormOfACircle', 'fixed_domain_key': 'analytic_geometry.circle_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['analyze_general_circle'], 'matched_capabilities': ['analyze_general_circle'], 'selected_operation': 'analyze_general_circle', 'registry_revision': 'promoted-c27fac060f71', 'domain_module': 'core.domain.promoted.analytic_geometry_circles.circle_equations_domain', 'entrypoint': 'build_circle_equations_matrix', 'allowed_operations': ['analyze_general_circle', 'evaluate_circle_statement_truth', 'solve_distance_ratio_locus'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_GeneralFormOfACircle'}), seed)
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
