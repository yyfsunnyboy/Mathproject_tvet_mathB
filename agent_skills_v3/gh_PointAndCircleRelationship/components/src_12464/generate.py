from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "classify_points_against_circle"
TEXTBOOK_EXAMPLE_ID = 12464
DEFAULT_COMPONENT_ID = "src_12464" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PointAndCircleRelationship"
FIXED_DOMAIN_KEY = "analytic_geometry.circle_equations"
DOMAIN_OPERATION = "classify_points_against_circle"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['classify_points_against_circle'], 'domain_operation': 'classify_points_against_circle', 'problem_type_id': 'classify_points_against_circle', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'circle': {'center': ['2', '-3'], 'r2': '25'}, 'points': [[6, 0], [-2, -1], [0, 2]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['3', '4'], 'r2': '25'}, 'points': [[7, 2], [2, -4], [6, 8]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['2', '2'], 'r2': '25'}, 'points': [[5, 3], [6, 10], [6, 5]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-1', '1'], 'r2': '16'}, 'points': [[4, 7], [1, 3], [-5, 1]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['0', '-1'], 'r2': '36'}, 'points': [[-8, -4], [4, -5], [0, -7]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['3', '2'], 'r2': '16'}, 'points': [[-4, 2], [7, 2], [5, 0]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['3', '-3'], 'r2': '49'}, 'points': [[3, 4], [0, -7], [10, -4]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-1', '-3'], 'r2': '9'}, 'points': [[-6, -3], [-3, -5], [-1, -6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['3', '-3'], 'r2': '25'}, 'points': [[-1, 0], [2, -10], [3, -4]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-4', '-4'], 'r2': '16'}, 'points': [[-3, 1], [-4, 0], [-3, -4]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['0', '1'], 'r2': '16'}, 'points': [[0, 5], [4, 8], [3, -1]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['2', '4'], 'r2': '16'}, 'points': [[6, 4], [7, -3], [0, 1]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-2', '0'], 'r2': '9'}, 'points': [[-8, 3], [-2, 3], [-4, 0]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-3', '3'], 'r2': '9'}, 'points': [[-7, 5], [0, 3], [-5, 1]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-2', '0'], 'r2': '16'}, 'points': [[-2, -4], [-2, 2], [3, 6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['4', '0'], 'r2': '36'}, 'points': [[7, 3], [1, -8], [4, 6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-1', '3'], 'r2': '9'}, 'points': [[-1, 1], [-4, 3], [2, 6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-2', '-2'], 'r2': '16'}, 'points': [[-4, 4], [-2, -6], [0, -3]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-2', '-1'], 'r2': '25'}, 'points': [[-5, -5], [-4, -4], [6, 6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['0', '-2'], 'r2': '49'}, 'points': [[1, -12], [-7, -2], [-3, 3]], 'names': ['P', 'Q', 'R']}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.circle_equations', 'required_capabilities': ['classify_points_against_circle'], 'domain_operation': 'classify_points_against_circle', 'problem_type_id': 'classify_points_against_circle', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'circle': {'center': ['2', '-3'], 'r2': '25'}, 'points': [[6, 0], [-2, -1], [0, 2]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['3', '4'], 'r2': '25'}, 'points': [[7, 2], [2, -4], [6, 8]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['2', '2'], 'r2': '25'}, 'points': [[5, 3], [6, 10], [6, 5]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-1', '1'], 'r2': '16'}, 'points': [[4, 7], [1, 3], [-5, 1]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['0', '-1'], 'r2': '36'}, 'points': [[-8, -4], [4, -5], [0, -7]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['3', '2'], 'r2': '16'}, 'points': [[-4, 2], [7, 2], [5, 0]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['3', '-3'], 'r2': '49'}, 'points': [[3, 4], [0, -7], [10, -4]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-1', '-3'], 'r2': '9'}, 'points': [[-6, -3], [-3, -5], [-1, -6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['3', '-3'], 'r2': '25'}, 'points': [[-1, 0], [2, -10], [3, -4]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-4', '-4'], 'r2': '16'}, 'points': [[-3, 1], [-4, 0], [-3, -4]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['0', '1'], 'r2': '16'}, 'points': [[0, 5], [4, 8], [3, -1]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['2', '4'], 'r2': '16'}, 'points': [[6, 4], [7, -3], [0, 1]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-2', '0'], 'r2': '9'}, 'points': [[-8, 3], [-2, 3], [-4, 0]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-3', '3'], 'r2': '9'}, 'points': [[-7, 5], [0, 3], [-5, 1]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-2', '0'], 'r2': '16'}, 'points': [[-2, -4], [-2, 2], [3, 6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['4', '0'], 'r2': '36'}, 'points': [[7, 3], [1, -8], [4, 6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-1', '3'], 'r2': '9'}, 'points': [[-1, 1], [-4, 3], [2, 6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-2', '-2'], 'r2': '16'}, 'points': [[-4, 4], [-2, -6], [0, -3]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-2', '-1'], 'r2': '25'}, 'points': [[-5, -5], [-4, -4], [6, 6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['0', '-2'], 'r2': '49'}, 'points': [[1, -12], [-7, -2], [-3, 3]], 'names': ['P', 'Q', 'R']}]}}, 'problem_type_id': 'classify_points_against_circle', 'required_capabilities': ['classify_points_against_circle'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'circle': {'center': ['2', '-3'], 'r2': '25'}, 'points': [[6, 0], [-2, -1], [0, 2]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['3', '4'], 'r2': '25'}, 'points': [[7, 2], [2, -4], [6, 8]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['2', '2'], 'r2': '25'}, 'points': [[5, 3], [6, 10], [6, 5]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-1', '1'], 'r2': '16'}, 'points': [[4, 7], [1, 3], [-5, 1]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['0', '-1'], 'r2': '36'}, 'points': [[-8, -4], [4, -5], [0, -7]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['3', '2'], 'r2': '16'}, 'points': [[-4, 2], [7, 2], [5, 0]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['3', '-3'], 'r2': '49'}, 'points': [[3, 4], [0, -7], [10, -4]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-1', '-3'], 'r2': '9'}, 'points': [[-6, -3], [-3, -5], [-1, -6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['3', '-3'], 'r2': '25'}, 'points': [[-1, 0], [2, -10], [3, -4]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-4', '-4'], 'r2': '16'}, 'points': [[-3, 1], [-4, 0], [-3, -4]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['0', '1'], 'r2': '16'}, 'points': [[0, 5], [4, 8], [3, -1]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['2', '4'], 'r2': '16'}, 'points': [[6, 4], [7, -3], [0, 1]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-2', '0'], 'r2': '9'}, 'points': [[-8, 3], [-2, 3], [-4, 0]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-3', '3'], 'r2': '9'}, 'points': [[-7, 5], [0, 3], [-5, 1]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-2', '0'], 'r2': '16'}, 'points': [[-2, -4], [-2, 2], [3, 6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['4', '0'], 'r2': '36'}, 'points': [[7, 3], [1, -8], [4, 6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-1', '3'], 'r2': '9'}, 'points': [[-1, 1], [-4, 3], [2, 6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-2', '-2'], 'r2': '16'}, 'points': [[-4, 4], [-2, -6], [0, -3]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['-2', '-1'], 'r2': '25'}, 'points': [[-5, -5], [-4, -4], [6, 6]], 'names': ['P', 'Q', 'R']}, {'circle': {'center': ['0', '-2'], 'r2': '49'}, 'points': [[1, -12], [-7, -2], [-3, 3]], 'names': ['P', 'Q', 'R']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_PointAndCircleRelationship', 'fixed_domain_key': 'analytic_geometry.circle_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['classify_points_against_circle'], 'matched_capabilities': ['classify_points_against_circle'], 'selected_operation': 'classify_points_against_circle', 'registry_revision': 'promoted-c27fac060f71', 'domain_module': 'core.domain.promoted.analytic_geometry_circles.circle_equations_domain', 'entrypoint': 'build_circle_equations_matrix', 'allowed_operations': ['classify_points_against_circle', 'evaluate_circle_statement_truth', 'solve_circle_point_distances', 'solve_mohr_circles', 'solve_point_position_parameter_range', 'solve_storm_entry_time', 'write_circle_equations'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_PointAndCircleRelationship'}), seed)
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
