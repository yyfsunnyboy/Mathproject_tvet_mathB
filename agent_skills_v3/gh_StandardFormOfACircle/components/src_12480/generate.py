from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "solve_circular_arch_height"
TEXTBOOK_EXAMPLE_ID = 12480
DEFAULT_COMPONENT_ID = "src_12480" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_StandardFormOfACircle"
FIXED_DOMAIN_KEY = "analytic_geometry.circle_equations"
DOMAIN_OPERATION = "solve_circular_arch_height"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['solve_circular_arch_height'], 'domain_operation': 'solve_circular_arch_height', 'problem_type_id': 'solve_circular_arch_height', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'width': 3, 'height': '9/2', 'post_offset': '3/2'}, {'width': '7', 'height': '49/2', 'post_offset': '7/2'}, {'width': '5', 'height': '25/4', 'post_offset': '5/2'}, {'width': '3', 'height': '9/4', 'post_offset': '3/2'}, {'width': '6', 'height': '18/5', 'post_offset': '3'}, {'width': '12', 'height': '18', 'post_offset': '6'}, {'width': '5', 'height': '25/6', 'post_offset': '5/2'}, {'width': '12', 'height': '12', 'post_offset': '6'}, {'width': '8', 'height': '32/3', 'post_offset': '4'}, {'width': '12', 'height': '24', 'post_offset': '6'}, {'width': '7', 'height': '49/4', 'post_offset': '7/2'}, {'width': '6', 'height': '18', 'post_offset': '3'}, {'width': '6', 'height': '9', 'post_offset': '3'}, {'width': '8', 'height': '8', 'post_offset': '4'}, {'width': '4', 'height': '4', 'post_offset': '2'}, {'width': '5', 'height': '25/8', 'post_offset': '5/2'}, {'width': '5', 'height': '25/2', 'post_offset': '5/2'}, {'width': '6', 'height': '6', 'post_offset': '3'}, {'width': '10', 'height': '25/3', 'post_offset': '5'}, {'width': '10', 'height': '25/2', 'post_offset': '5'}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['solve_circular_arch_height'], 'domain_operation': 'solve_circular_arch_height', 'problem_type_id': 'solve_circular_arch_height', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'width': 3, 'height': '9/2', 'post_offset': '3/2'}, {'width': '7', 'height': '49/2', 'post_offset': '7/2'}, {'width': '5', 'height': '25/4', 'post_offset': '5/2'}, {'width': '3', 'height': '9/4', 'post_offset': '3/2'}, {'width': '6', 'height': '18/5', 'post_offset': '3'}, {'width': '12', 'height': '18', 'post_offset': '6'}, {'width': '5', 'height': '25/6', 'post_offset': '5/2'}, {'width': '12', 'height': '12', 'post_offset': '6'}, {'width': '8', 'height': '32/3', 'post_offset': '4'}, {'width': '12', 'height': '24', 'post_offset': '6'}, {'width': '7', 'height': '49/4', 'post_offset': '7/2'}, {'width': '6', 'height': '18', 'post_offset': '3'}, {'width': '6', 'height': '9', 'post_offset': '3'}, {'width': '8', 'height': '8', 'post_offset': '4'}, {'width': '4', 'height': '4', 'post_offset': '2'}, {'width': '5', 'height': '25/8', 'post_offset': '5/2'}, {'width': '5', 'height': '25/2', 'post_offset': '5/2'}, {'width': '6', 'height': '6', 'post_offset': '3'}, {'width': '10', 'height': '25/3', 'post_offset': '5'}, {'width': '10', 'height': '25/2', 'post_offset': '5'}]}}, 'problem_type_id': 'solve_circular_arch_height', 'required_capabilities': ['solve_circular_arch_height'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'width': 3, 'height': '9/2', 'post_offset': '3/2'}, {'width': '7', 'height': '49/2', 'post_offset': '7/2'}, {'width': '5', 'height': '25/4', 'post_offset': '5/2'}, {'width': '3', 'height': '9/4', 'post_offset': '3/2'}, {'width': '6', 'height': '18/5', 'post_offset': '3'}, {'width': '12', 'height': '18', 'post_offset': '6'}, {'width': '5', 'height': '25/6', 'post_offset': '5/2'}, {'width': '12', 'height': '12', 'post_offset': '6'}, {'width': '8', 'height': '32/3', 'post_offset': '4'}, {'width': '12', 'height': '24', 'post_offset': '6'}, {'width': '7', 'height': '49/4', 'post_offset': '7/2'}, {'width': '6', 'height': '18', 'post_offset': '3'}, {'width': '6', 'height': '9', 'post_offset': '3'}, {'width': '8', 'height': '8', 'post_offset': '4'}, {'width': '4', 'height': '4', 'post_offset': '2'}, {'width': '5', 'height': '25/8', 'post_offset': '5/2'}, {'width': '5', 'height': '25/2', 'post_offset': '5/2'}, {'width': '6', 'height': '6', 'post_offset': '3'}, {'width': '10', 'height': '25/3', 'post_offset': '5'}, {'width': '10', 'height': '25/2', 'post_offset': '5'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_StandardFormOfACircle', 'fixed_domain_key': 'analytic_geometry.circle_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_circular_arch_height'], 'matched_capabilities': ['solve_circular_arch_height'], 'selected_operation': 'solve_circular_arch_height', 'registry_revision': 'promoted-c27fac060f71', 'domain_module': 'core.domain.promoted.analytic_geometry_circles.circle_equations_domain', 'entrypoint': 'build_circle_equations_matrix', 'allowed_operations': ['evaluate_circle_statement_truth', 'solve_circular_arch_height', 'write_circle_equations'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_StandardFormOfACircle'}), seed)
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
