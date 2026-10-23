from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "solve_storm_entry_time"
TEXTBOOK_EXAMPLE_ID = 12478
DEFAULT_COMPONENT_ID = "src_12478" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PointAndCircleRelationship"
FIXED_DOMAIN_KEY = "analytic_geometry.circle_equations"
DOMAIN_OPERATION = "solve_storm_entry_time"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['solve_storm_entry_time'], 'domain_operation': 'solve_storm_entry_time', 'problem_type_id': 'solve_storm_entry_time', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'start_hour': 15, 'distance': 460, 'radius': 80, 'speed': 25, 'options': [18, 23, 30, 35]}, {'start_hour': 13, 'distance': 362, 'radius': 60, 'speed': 25, 'options': [13, 22, 25, 30]}, {'start_hour': 18, 'distance': 616, 'radius': 120, 'speed': 40, 'options': [21, 30, 35, 38]}, {'start_hour': 13, 'distance': 756, 'radius': 100, 'speed': 40, 'options': [15, 29, 33, 37]}, {'start_hour': 16, 'distance': 505, 'radius': 100, 'speed': 25, 'options': [18, 23, 32, 38]}, {'start_hour': 14, 'distance': 355, 'radius': 120, 'speed': 25, 'options': [14, 20, 23, 26]}, {'start_hour': 14, 'distance': 268, 'radius': 100, 'speed': 20, 'options': [13, 22, 25, 30]}, {'start_hour': 17, 'distance': 300, 'radius': 60, 'speed': 40, 'options': [9, 14, 23, 28]}, {'start_hour': 16, 'distance': 217, 'radius': 60, 'speed': 25, 'options': [10, 22, 26, 28]}, {'start_hour': 20, 'distance': 202, 'radius': 60, 'speed': 20, 'options': [18, 27, 30, 37]}, {'start_hour': 17, 'distance': 483, 'radius': 120, 'speed': 30, 'options': [22, 25, 29, 32]}, {'start_hour': 16, 'distance': 427, 'radius': 100, 'speed': 25, 'options': [17, 20, 29, 37]}, {'start_hour': 13, 'distance': 522, 'radius': 120, 'speed': 25, 'options': [29, 34, 35, 37]}, {'start_hour': 17, 'distance': 525, 'radius': 100, 'speed': 25, 'options': [22, 30, 31, 34]}, {'start_hour': 14, 'distance': 744, 'radius': 60, 'speed': 40, 'options': [17, 19, 26, 31]}, {'start_hour': 17, 'distance': 362, 'radius': 120, 'speed': 20, 'options': [22, 29, 32, 39]}, {'start_hour': 14, 'distance': 484, 'radius': 120, 'speed': 40, 'options': [18, 19, 23, 26]}, {'start_hour': 16, 'distance': 612, 'radius': 60, 'speed': 30, 'options': [22, 34, 37, 42]}, {'start_hour': 17, 'distance': 384, 'radius': 80, 'speed': 20, 'options': [18, 27, 28, 32]}, {'start_hour': 14, 'distance': 349, 'radius': 100, 'speed': 30, 'options': [13, 19, 22, 30]}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['solve_storm_entry_time'], 'domain_operation': 'solve_storm_entry_time', 'problem_type_id': 'solve_storm_entry_time', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'start_hour': 15, 'distance': 460, 'radius': 80, 'speed': 25, 'options': [18, 23, 30, 35]}, {'start_hour': 13, 'distance': 362, 'radius': 60, 'speed': 25, 'options': [13, 22, 25, 30]}, {'start_hour': 18, 'distance': 616, 'radius': 120, 'speed': 40, 'options': [21, 30, 35, 38]}, {'start_hour': 13, 'distance': 756, 'radius': 100, 'speed': 40, 'options': [15, 29, 33, 37]}, {'start_hour': 16, 'distance': 505, 'radius': 100, 'speed': 25, 'options': [18, 23, 32, 38]}, {'start_hour': 14, 'distance': 355, 'radius': 120, 'speed': 25, 'options': [14, 20, 23, 26]}, {'start_hour': 14, 'distance': 268, 'radius': 100, 'speed': 20, 'options': [13, 22, 25, 30]}, {'start_hour': 17, 'distance': 300, 'radius': 60, 'speed': 40, 'options': [9, 14, 23, 28]}, {'start_hour': 16, 'distance': 217, 'radius': 60, 'speed': 25, 'options': [10, 22, 26, 28]}, {'start_hour': 20, 'distance': 202, 'radius': 60, 'speed': 20, 'options': [18, 27, 30, 37]}, {'start_hour': 17, 'distance': 483, 'radius': 120, 'speed': 30, 'options': [22, 25, 29, 32]}, {'start_hour': 16, 'distance': 427, 'radius': 100, 'speed': 25, 'options': [17, 20, 29, 37]}, {'start_hour': 13, 'distance': 522, 'radius': 120, 'speed': 25, 'options': [29, 34, 35, 37]}, {'start_hour': 17, 'distance': 525, 'radius': 100, 'speed': 25, 'options': [22, 30, 31, 34]}, {'start_hour': 14, 'distance': 744, 'radius': 60, 'speed': 40, 'options': [17, 19, 26, 31]}, {'start_hour': 17, 'distance': 362, 'radius': 120, 'speed': 20, 'options': [22, 29, 32, 39]}, {'start_hour': 14, 'distance': 484, 'radius': 120, 'speed': 40, 'options': [18, 19, 23, 26]}, {'start_hour': 16, 'distance': 612, 'radius': 60, 'speed': 30, 'options': [22, 34, 37, 42]}, {'start_hour': 17, 'distance': 384, 'radius': 80, 'speed': 20, 'options': [18, 27, 28, 32]}, {'start_hour': 14, 'distance': 349, 'radius': 100, 'speed': 30, 'options': [13, 19, 22, 30]}]}}, 'problem_type_id': 'solve_storm_entry_time', 'required_capabilities': ['solve_storm_entry_time'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'start_hour': 15, 'distance': 460, 'radius': 80, 'speed': 25, 'options': [18, 23, 30, 35]}, {'start_hour': 13, 'distance': 362, 'radius': 60, 'speed': 25, 'options': [13, 22, 25, 30]}, {'start_hour': 18, 'distance': 616, 'radius': 120, 'speed': 40, 'options': [21, 30, 35, 38]}, {'start_hour': 13, 'distance': 756, 'radius': 100, 'speed': 40, 'options': [15, 29, 33, 37]}, {'start_hour': 16, 'distance': 505, 'radius': 100, 'speed': 25, 'options': [18, 23, 32, 38]}, {'start_hour': 14, 'distance': 355, 'radius': 120, 'speed': 25, 'options': [14, 20, 23, 26]}, {'start_hour': 14, 'distance': 268, 'radius': 100, 'speed': 20, 'options': [13, 22, 25, 30]}, {'start_hour': 17, 'distance': 300, 'radius': 60, 'speed': 40, 'options': [9, 14, 23, 28]}, {'start_hour': 16, 'distance': 217, 'radius': 60, 'speed': 25, 'options': [10, 22, 26, 28]}, {'start_hour': 20, 'distance': 202, 'radius': 60, 'speed': 20, 'options': [18, 27, 30, 37]}, {'start_hour': 17, 'distance': 483, 'radius': 120, 'speed': 30, 'options': [22, 25, 29, 32]}, {'start_hour': 16, 'distance': 427, 'radius': 100, 'speed': 25, 'options': [17, 20, 29, 37]}, {'start_hour': 13, 'distance': 522, 'radius': 120, 'speed': 25, 'options': [29, 34, 35, 37]}, {'start_hour': 17, 'distance': 525, 'radius': 100, 'speed': 25, 'options': [22, 30, 31, 34]}, {'start_hour': 14, 'distance': 744, 'radius': 60, 'speed': 40, 'options': [17, 19, 26, 31]}, {'start_hour': 17, 'distance': 362, 'radius': 120, 'speed': 20, 'options': [22, 29, 32, 39]}, {'start_hour': 14, 'distance': 484, 'radius': 120, 'speed': 40, 'options': [18, 19, 23, 26]}, {'start_hour': 16, 'distance': 612, 'radius': 60, 'speed': 30, 'options': [22, 34, 37, 42]}, {'start_hour': 17, 'distance': 384, 'radius': 80, 'speed': 20, 'options': [18, 27, 28, 32]}, {'start_hour': 14, 'distance': 349, 'radius': 100, 'speed': 30, 'options': [13, 19, 22, 30]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_PointAndCircleRelationship', 'fixed_domain_key': 'analytic_geometry.circle_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_storm_entry_time'], 'matched_capabilities': ['solve_storm_entry_time'], 'selected_operation': 'solve_storm_entry_time', 'registry_revision': 'promoted-c27fac060f71', 'domain_module': 'core.domain.promoted.analytic_geometry_circles.circle_equations_domain', 'entrypoint': 'build_circle_equations_matrix', 'allowed_operations': ['classify_points_against_circle', 'evaluate_circle_statement_truth', 'solve_circle_point_distances', 'solve_mohr_circles', 'solve_point_position_parameter_range', 'solve_storm_entry_time', 'write_circle_equations'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_PointAndCircleRelationship'}), seed)
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
