from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "inequality"
PROBLEM_TYPE_ID = "solve_point_position_parameter_range"
TEXTBOOK_EXAMPLE_ID = 12467
DEFAULT_COMPONENT_ID = "src_12467" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PointAndCircleRelationship"
FIXED_DOMAIN_KEY = "analytic_geometry.circle_equations"
DOMAIN_OPERATION = "solve_point_position_parameter_range"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['solve_point_position_parameter_range'], 'domain_operation': 'solve_point_position_parameter_range', 'problem_type_id': 'solve_point_position_parameter_range', 'presentation_mode': 'short_answer', 'answer_type': 'inequality', 'generation_constraints': {'variants': [{'inside': [[1, -2]], 'outside': [[-3, 3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[0, -1]], 'outside': [[4, -2]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-2, 0]], 'outside': [[-3, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-2, 0]], 'outside': [[-1, -2]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-1, 3]], 'outside': [[-4, 3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-2, 3]], 'outside': [[-1, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[1, 2]], 'outside': [[4, -5]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[1, 3]], 'outside': [[0, 5]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[4, -1]], 'outside': [[-5, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-3, -1]], 'outside': [[5, 4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[1, 4]], 'outside': [[-5, 3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[3, 3]], 'outside': [[4, 4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-4, 0]], 'outside': [[-4, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[3, -3]], 'outside': [[5, 3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-4, -3]], 'outside': [[-5, 5]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-3, -3]], 'outside': [[-3, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-3, 0]], 'outside': [[-2, 5]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-3, -1]], 'outside': [[-4, 1]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-1, -3]], 'outside': [[4, -3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[0, -3]], 'outside': [[5, 1]], 'names': {'inside': ['P'], 'outside': ['Q']}}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['solve_point_position_parameter_range'], 'domain_operation': 'solve_point_position_parameter_range', 'problem_type_id': 'solve_point_position_parameter_range', 'presentation_mode': 'short_answer', 'answer_type': 'inequality', 'generation_constraints': {'variants': [{'inside': [[1, -2]], 'outside': [[-3, 3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[0, -1]], 'outside': [[4, -2]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-2, 0]], 'outside': [[-3, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-2, 0]], 'outside': [[-1, -2]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-1, 3]], 'outside': [[-4, 3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-2, 3]], 'outside': [[-1, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[1, 2]], 'outside': [[4, -5]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[1, 3]], 'outside': [[0, 5]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[4, -1]], 'outside': [[-5, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-3, -1]], 'outside': [[5, 4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[1, 4]], 'outside': [[-5, 3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[3, 3]], 'outside': [[4, 4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-4, 0]], 'outside': [[-4, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[3, -3]], 'outside': [[5, 3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-4, -3]], 'outside': [[-5, 5]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-3, -3]], 'outside': [[-3, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-3, 0]], 'outside': [[-2, 5]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-3, -1]], 'outside': [[-4, 1]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-1, -3]], 'outside': [[4, -3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[0, -3]], 'outside': [[5, 1]], 'names': {'inside': ['P'], 'outside': ['Q']}}]}}, 'problem_type_id': 'solve_point_position_parameter_range', 'required_capabilities': ['solve_point_position_parameter_range'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'inside': [[1, -2]], 'outside': [[-3, 3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[0, -1]], 'outside': [[4, -2]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-2, 0]], 'outside': [[-3, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-2, 0]], 'outside': [[-1, -2]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-1, 3]], 'outside': [[-4, 3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-2, 3]], 'outside': [[-1, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[1, 2]], 'outside': [[4, -5]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[1, 3]], 'outside': [[0, 5]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[4, -1]], 'outside': [[-5, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-3, -1]], 'outside': [[5, 4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[1, 4]], 'outside': [[-5, 3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[3, 3]], 'outside': [[4, 4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-4, 0]], 'outside': [[-4, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[3, -3]], 'outside': [[5, 3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-4, -3]], 'outside': [[-5, 5]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-3, -3]], 'outside': [[-3, -4]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-3, 0]], 'outside': [[-2, 5]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-3, -1]], 'outside': [[-4, 1]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[-1, -3]], 'outside': [[4, -3]], 'names': {'inside': ['P'], 'outside': ['Q']}}, {'inside': [[0, -3]], 'outside': [[5, 1]], 'names': {'inside': ['P'], 'outside': ['Q']}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_PointAndCircleRelationship', 'fixed_domain_key': 'analytic_geometry.circle_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_point_position_parameter_range'], 'matched_capabilities': ['solve_point_position_parameter_range'], 'selected_operation': 'solve_point_position_parameter_range', 'registry_revision': 'promoted-c27fac060f71', 'domain_module': 'core.domain.promoted.analytic_geometry_circles.circle_equations_domain', 'entrypoint': 'build_circle_equations_matrix', 'allowed_operations': ['classify_points_against_circle', 'evaluate_circle_statement_truth', 'solve_circle_point_distances', 'solve_mohr_circles', 'solve_point_position_parameter_range', 'solve_storm_entry_time', 'write_circle_equations'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_PointAndCircleRelationship'}), seed)
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
