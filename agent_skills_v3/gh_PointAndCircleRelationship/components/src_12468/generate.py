from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "solve_circle_point_distances"
TEXTBOOK_EXAMPLE_ID = 12468
DEFAULT_COMPONENT_ID = "src_12468" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PointAndCircleRelationship"
FIXED_DOMAIN_KEY = "analytic_geometry.circle_equations"
DOMAIN_OPERATION = "solve_circle_point_distances"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['solve_circle_point_distances'], 'domain_operation': 'solve_circle_point_distances', 'problem_type_id': 'solve_circle_point_distances', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'circle': {'d': '-6', 'e': '-8', 'f': '-11'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '30', 'e': '16', 'f': '-195'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '16', 'e': '12', 'f': '-125'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '24', 'e': '18', 'f': '-136'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '10', 'e': '-24', 'f': '105'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '12', 'e': '16', 'f': '64'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-6', 'e': '-8', 'f': '-96'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '24', 'e': '18', 'f': '144'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-18', 'e': '-24', 'f': '-216'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-18', 'e': '-24', 'f': '216'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-12', 'e': '16', 'f': '75'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-12', 'e': '16', 'f': '-156'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '8', 'e': '6', 'f': '-96'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '8', 'e': '6', 'f': '21'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '24', 'e': '10', 'f': '165'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '24', 'e': '-18', 'f': '29'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '10', 'e': '24', 'f': '105'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '10', 'e': '24', 'f': '-27'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '10', 'e': '-24', 'f': '-27'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-18', 'e': '-24', 'f': '176'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['solve_circle_point_distances'], 'domain_operation': 'solve_circle_point_distances', 'problem_type_id': 'solve_circle_point_distances', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'circle': {'d': '-6', 'e': '-8', 'f': '-11'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '30', 'e': '16', 'f': '-195'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '16', 'e': '12', 'f': '-125'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '24', 'e': '18', 'f': '-136'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '10', 'e': '-24', 'f': '105'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '12', 'e': '16', 'f': '64'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-6', 'e': '-8', 'f': '-96'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '24', 'e': '18', 'f': '144'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-18', 'e': '-24', 'f': '-216'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-18', 'e': '-24', 'f': '216'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-12', 'e': '16', 'f': '75'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-12', 'e': '16', 'f': '-156'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '8', 'e': '6', 'f': '-96'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '8', 'e': '6', 'f': '21'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '24', 'e': '10', 'f': '165'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '24', 'e': '-18', 'f': '29'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '10', 'e': '24', 'f': '105'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '10', 'e': '24', 'f': '-27'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '10', 'e': '-24', 'f': '-27'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-18', 'e': '-24', 'f': '176'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}]}}, 'problem_type_id': 'solve_circle_point_distances', 'required_capabilities': ['solve_circle_point_distances'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'circle': {'d': '-6', 'e': '-8', 'f': '-11'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '30', 'e': '16', 'f': '-195'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '16', 'e': '12', 'f': '-125'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '24', 'e': '18', 'f': '-136'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '10', 'e': '-24', 'f': '105'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '12', 'e': '16', 'f': '64'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-6', 'e': '-8', 'f': '-96'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '24', 'e': '18', 'f': '144'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-18', 'e': '-24', 'f': '-216'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-18', 'e': '-24', 'f': '216'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-12', 'e': '16', 'f': '75'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-12', 'e': '16', 'f': '-156'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '8', 'e': '6', 'f': '-96'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '8', 'e': '6', 'f': '21'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '24', 'e': '10', 'f': '165'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '24', 'e': '-18', 'f': '29'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '10', 'e': '24', 'f': '105'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '10', 'e': '24', 'f': '-27'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '10', 'e': '-24', 'f': '-27'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}, {'circle': {'d': '-18', 'e': '-24', 'f': '176'}, 'point': [0, 0], 'asks': ['max', 'min'], 'point_name': '原點'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_PointAndCircleRelationship', 'fixed_domain_key': 'analytic_geometry.circle_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_circle_point_distances'], 'matched_capabilities': ['solve_circle_point_distances'], 'selected_operation': 'solve_circle_point_distances', 'registry_revision': 'promoted-c27fac060f71', 'domain_module': 'core.domain.promoted.analytic_geometry_circles.circle_equations_domain', 'entrypoint': 'build_circle_equations_matrix', 'allowed_operations': ['classify_points_against_circle', 'evaluate_circle_statement_truth', 'solve_circle_point_distances', 'solve_mohr_circles', 'solve_point_position_parameter_range', 'solve_storm_entry_time', 'write_circle_equations'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_PointAndCircleRelationship'}), seed)
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
