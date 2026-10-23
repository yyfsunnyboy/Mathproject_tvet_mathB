from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "solution_set"
PROBLEM_TYPE_ID = "select_points_same_side"
TEXTBOOK_EXAMPLE_ID = 12441
DEFAULT_COMPONENT_ID = "src_12441" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_LinearInequalityInTwoVariables"
FIXED_DOMAIN_KEY = "analytic_geometry.line_equations"
DOMAIN_OPERATION = "select_points_same_side"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['select_points_same_side'], 'domain_operation': 'select_points_same_side', 'problem_type_id': 'select_points_same_side', 'presentation_mode': 'short_answer', 'answer_type': 'solution_set', 'generation_constraints': {'variants': [{'line': [2, -3, 4], 'line_display': '2x-3y=-4', 'reference': [0, 0], 'reference_name': '原點', 'points': [[1, 2], [2, 3], [3, 4], [4, 3], [3, 2]]}, {'line': [1, 1, -1], 'line_display': 'x+y=1', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, 3], [1, 5], [2, 4], [-2, -1], [3, 3]]}, {'line': [3, -2, 2], 'line_display': '3x-2y=-2', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, 4], [1, -1], [-2, 3], [-2, 5], [-1, -1]]}, {'line': [3, -2, -4], 'line_display': '3x-2y=4', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, -1], [-1, 2], [3, 0], [4, 2], [5, 0]]}, {'line': [-1, -3, 3], 'line_display': '-x-3y=-3', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-2, 1], [1, 5], [-1, -2], [-1, 4], [-2, 3]]}, {'line': [-1, 3, 3], 'line_display': '-x+3y=-3', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-1, 1], [3, -1], [-1, 5], [1, 4], [-2, 2]]}, {'line': [-3, 3, 4], 'line_display': '-3x+3y=-4', 'reference': [0, 0], 'reference_name': '原點', 'points': [[2, 5], [4, 3], [2, -1], [-2, 2], [0, 1]]}, {'line': [-3, 2, -4], 'line_display': '-3x+2y=4', 'reference': [0, 0], 'reference_name': '原點', 'points': [[2, 4], [1, 4], [3, -2], [2, 3], [4, 2]]}, {'line': [1, -3, 2], 'line_display': 'x-3y=-2', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-1, 3], [4, 0], [5, 3], [-1, 2], [0, 2]]}, {'line': [-1, -3, 1], 'line_display': '-x-3y=-1', 'reference': [0, 0], 'reference_name': '原點', 'points': [[3, -1], [3, 4], [2, 1], [4, 0], [4, 2]]}, {'line': [2, -1, -5], 'line_display': '2x-y=5', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-1, -2], [4, 1], [1, 3], [3, 4], [3, 5]]}, {'line': [-3, 2, -6], 'line_display': '-3x+2y=6', 'reference': [0, 0], 'reference_name': '原點', 'points': [[5, 2], [-2, 1], [0, -2], [-2, 4], [3, 2]]}, {'line': [-2, 3, -6], 'line_display': '-2x+3y=6', 'reference': [0, 0], 'reference_name': '原點', 'points': [[2, 3], [-2, 2], [-2, 5], [4, 0], [4, 4]]}, {'line': [-1, 2, -5], 'line_display': '-x+2y=5', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-2, 5], [3, -1], [-2, 4], [-1, -2], [-1, 0]]}, {'line': [-1, 1, -2], 'line_display': '-x+y=2', 'reference': [0, 0], 'reference_name': '原點', 'points': [[1, 2], [0, -2], [-1, -1], [-2, 2], [2, 2]]}, {'line': [3, 2, -1], 'line_display': '3x+2y=1', 'reference': [0, 0], 'reference_name': '原點', 'points': [[3, 4], [-1, 4], [5, 2], [-1, 0], [2, 5]]}, {'line': [-1, 2, -5], 'line_display': '-x+2y=5', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, 4], [4, 2], [3, 5], [5, -1], [0, 5]]}, {'line': [-2, 2, 2], 'line_display': '-2x+2y=-2', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-2, 1], [2, 2], [2, 5], [5, -2], [2, 1]]}, {'line': [1, -2, 3], 'line_display': 'x-2y=-3', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, 1], [5, 5], [3, 1], [-1, 5], [3, 5]]}, {'line': [-1, 2, -5], 'line_display': '-x+2y=5', 'reference': [0, 0], 'reference_name': '原點', 'points': [[5, -1], [1, 5], [-2, 4], [-2, -2], [1, 1]]}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['select_points_same_side'], 'domain_operation': 'select_points_same_side', 'problem_type_id': 'select_points_same_side', 'presentation_mode': 'short_answer', 'answer_type': 'solution_set', 'generation_constraints': {'variants': [{'line': [2, -3, 4], 'line_display': '2x-3y=-4', 'reference': [0, 0], 'reference_name': '原點', 'points': [[1, 2], [2, 3], [3, 4], [4, 3], [3, 2]]}, {'line': [1, 1, -1], 'line_display': 'x+y=1', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, 3], [1, 5], [2, 4], [-2, -1], [3, 3]]}, {'line': [3, -2, 2], 'line_display': '3x-2y=-2', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, 4], [1, -1], [-2, 3], [-2, 5], [-1, -1]]}, {'line': [3, -2, -4], 'line_display': '3x-2y=4', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, -1], [-1, 2], [3, 0], [4, 2], [5, 0]]}, {'line': [-1, -3, 3], 'line_display': '-x-3y=-3', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-2, 1], [1, 5], [-1, -2], [-1, 4], [-2, 3]]}, {'line': [-1, 3, 3], 'line_display': '-x+3y=-3', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-1, 1], [3, -1], [-1, 5], [1, 4], [-2, 2]]}, {'line': [-3, 3, 4], 'line_display': '-3x+3y=-4', 'reference': [0, 0], 'reference_name': '原點', 'points': [[2, 5], [4, 3], [2, -1], [-2, 2], [0, 1]]}, {'line': [-3, 2, -4], 'line_display': '-3x+2y=4', 'reference': [0, 0], 'reference_name': '原點', 'points': [[2, 4], [1, 4], [3, -2], [2, 3], [4, 2]]}, {'line': [1, -3, 2], 'line_display': 'x-3y=-2', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-1, 3], [4, 0], [5, 3], [-1, 2], [0, 2]]}, {'line': [-1, -3, 1], 'line_display': '-x-3y=-1', 'reference': [0, 0], 'reference_name': '原點', 'points': [[3, -1], [3, 4], [2, 1], [4, 0], [4, 2]]}, {'line': [2, -1, -5], 'line_display': '2x-y=5', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-1, -2], [4, 1], [1, 3], [3, 4], [3, 5]]}, {'line': [-3, 2, -6], 'line_display': '-3x+2y=6', 'reference': [0, 0], 'reference_name': '原點', 'points': [[5, 2], [-2, 1], [0, -2], [-2, 4], [3, 2]]}, {'line': [-2, 3, -6], 'line_display': '-2x+3y=6', 'reference': [0, 0], 'reference_name': '原點', 'points': [[2, 3], [-2, 2], [-2, 5], [4, 0], [4, 4]]}, {'line': [-1, 2, -5], 'line_display': '-x+2y=5', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-2, 5], [3, -1], [-2, 4], [-1, -2], [-1, 0]]}, {'line': [-1, 1, -2], 'line_display': '-x+y=2', 'reference': [0, 0], 'reference_name': '原點', 'points': [[1, 2], [0, -2], [-1, -1], [-2, 2], [2, 2]]}, {'line': [3, 2, -1], 'line_display': '3x+2y=1', 'reference': [0, 0], 'reference_name': '原點', 'points': [[3, 4], [-1, 4], [5, 2], [-1, 0], [2, 5]]}, {'line': [-1, 2, -5], 'line_display': '-x+2y=5', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, 4], [4, 2], [3, 5], [5, -1], [0, 5]]}, {'line': [-2, 2, 2], 'line_display': '-2x+2y=-2', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-2, 1], [2, 2], [2, 5], [5, -2], [2, 1]]}, {'line': [1, -2, 3], 'line_display': 'x-2y=-3', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, 1], [5, 5], [3, 1], [-1, 5], [3, 5]]}, {'line': [-1, 2, -5], 'line_display': '-x+2y=5', 'reference': [0, 0], 'reference_name': '原點', 'points': [[5, -1], [1, 5], [-2, 4], [-2, -2], [1, 1]]}]}}, 'problem_type_id': 'select_points_same_side', 'required_capabilities': ['select_points_same_side'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'line': [2, -3, 4], 'line_display': '2x-3y=-4', 'reference': [0, 0], 'reference_name': '原點', 'points': [[1, 2], [2, 3], [3, 4], [4, 3], [3, 2]]}, {'line': [1, 1, -1], 'line_display': 'x+y=1', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, 3], [1, 5], [2, 4], [-2, -1], [3, 3]]}, {'line': [3, -2, 2], 'line_display': '3x-2y=-2', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, 4], [1, -1], [-2, 3], [-2, 5], [-1, -1]]}, {'line': [3, -2, -4], 'line_display': '3x-2y=4', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, -1], [-1, 2], [3, 0], [4, 2], [5, 0]]}, {'line': [-1, -3, 3], 'line_display': '-x-3y=-3', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-2, 1], [1, 5], [-1, -2], [-1, 4], [-2, 3]]}, {'line': [-1, 3, 3], 'line_display': '-x+3y=-3', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-1, 1], [3, -1], [-1, 5], [1, 4], [-2, 2]]}, {'line': [-3, 3, 4], 'line_display': '-3x+3y=-4', 'reference': [0, 0], 'reference_name': '原點', 'points': [[2, 5], [4, 3], [2, -1], [-2, 2], [0, 1]]}, {'line': [-3, 2, -4], 'line_display': '-3x+2y=4', 'reference': [0, 0], 'reference_name': '原點', 'points': [[2, 4], [1, 4], [3, -2], [2, 3], [4, 2]]}, {'line': [1, -3, 2], 'line_display': 'x-3y=-2', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-1, 3], [4, 0], [5, 3], [-1, 2], [0, 2]]}, {'line': [-1, -3, 1], 'line_display': '-x-3y=-1', 'reference': [0, 0], 'reference_name': '原點', 'points': [[3, -1], [3, 4], [2, 1], [4, 0], [4, 2]]}, {'line': [2, -1, -5], 'line_display': '2x-y=5', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-1, -2], [4, 1], [1, 3], [3, 4], [3, 5]]}, {'line': [-3, 2, -6], 'line_display': '-3x+2y=6', 'reference': [0, 0], 'reference_name': '原點', 'points': [[5, 2], [-2, 1], [0, -2], [-2, 4], [3, 2]]}, {'line': [-2, 3, -6], 'line_display': '-2x+3y=6', 'reference': [0, 0], 'reference_name': '原點', 'points': [[2, 3], [-2, 2], [-2, 5], [4, 0], [4, 4]]}, {'line': [-1, 2, -5], 'line_display': '-x+2y=5', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-2, 5], [3, -1], [-2, 4], [-1, -2], [-1, 0]]}, {'line': [-1, 1, -2], 'line_display': '-x+y=2', 'reference': [0, 0], 'reference_name': '原點', 'points': [[1, 2], [0, -2], [-1, -1], [-2, 2], [2, 2]]}, {'line': [3, 2, -1], 'line_display': '3x+2y=1', 'reference': [0, 0], 'reference_name': '原點', 'points': [[3, 4], [-1, 4], [5, 2], [-1, 0], [2, 5]]}, {'line': [-1, 2, -5], 'line_display': '-x+2y=5', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, 4], [4, 2], [3, 5], [5, -1], [0, 5]]}, {'line': [-2, 2, 2], 'line_display': '-2x+2y=-2', 'reference': [0, 0], 'reference_name': '原點', 'points': [[-2, 1], [2, 2], [2, 5], [5, -2], [2, 1]]}, {'line': [1, -2, 3], 'line_display': 'x-2y=-3', 'reference': [0, 0], 'reference_name': '原點', 'points': [[4, 1], [5, 5], [3, 1], [-1, 5], [3, 5]]}, {'line': [-1, 2, -5], 'line_display': '-x+2y=5', 'reference': [0, 0], 'reference_name': '原點', 'points': [[5, -1], [1, 5], [-2, 4], [-2, -2], [1, 1]]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_LinearInequalityInTwoVariables', 'fixed_domain_key': 'analytic_geometry.line_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['select_points_same_side'], 'matched_capabilities': ['select_points_same_side'], 'selected_operation': 'select_points_same_side', 'registry_revision': 'promoted-ebaf64733fa3', 'domain_module': 'core.domain.promoted.analytic_geometry_lines.line_equations_domain', 'entrypoint': 'build_line_equations_matrix', 'allowed_operations': ['evaluate_line_statement_truth', 'graph_inequality_system', 'read_region_signs_from_figure', 'select_points_same_side', 'solve_region_coefficients_from_figure', 'solve_triangle_region_system'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_LinearInequalityInTwoVariables'}), seed)
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
