from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "coordinate_pair"
PROBLEM_TYPE_ID = "solve_line_constructions"
TEXTBOOK_EXAMPLE_ID = 12415
DEFAULT_COMPONENT_ID = "src_12415" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_ParallelAndPerpendicularLines"
FIXED_DOMAIN_KEY = "analytic_geometry.line_equations"
DOMAIN_OPERATION = "solve_line_constructions"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['solve_line_constructions'], 'domain_operation': 'solve_line_constructions', 'problem_type_id': 'solve_line_constructions', 'presentation_mode': 'short_answer', 'answer_type': 'coordinate_pair', 'generation_constraints': {'variants': [{'stem': '', 'items': [{'kind': 'reflect_point', 'p': [3, 1], 'line': [1, -1, 0], 'line_display': 'x-y=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-4, 2], 'line': [1, 1, -1], 'line_display': 'x+y-1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [3, 3], 'line': [1, 1, -4], 'line_display': 'x+y-4=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [5, 1], 'line': [1, 1, -2], 'line_display': 'x+y-2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-1, 6], 'line': [1, 1, 4], 'line_display': 'x+y+4=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-5, 0], 'line': [1, -1, -3], 'line_display': 'x-y-3=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [0, -3], 'line': [1, -1, -3], 'line_display': 'x-y-3=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-5, 1], 'line': [1, -1, 2], 'line_display': 'x-y+2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-1, 1], 'line': [1, -1, -2], 'line_display': 'x-y-2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [4, 6], 'line': [1, -1, -3], 'line_display': 'x-y-3=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-2, 2], 'line': [1, 1, 1], 'line_display': 'x+y+1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [0, 3], 'line': [1, 1, -2], 'line_display': 'x+y-2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [4, -4], 'line': [1, -1, -1], 'line_display': 'x-y-1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-5, -4], 'line': [1, -1, 2], 'line_display': 'x-y+2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [5, -5], 'line': [1, -1, 3], 'line_display': 'x-y+3=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-2, -2], 'line': [1, -1, 4], 'line_display': 'x-y+4=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [4, -2], 'line': [1, -1, 1], 'line_display': 'x-y+1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [2, -5], 'line': [1, 1, 2], 'line_display': 'x+y+2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [6, 1], 'line': [1, -1, 1], 'line_display': 'x-y+1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-5, -1], 'line': [1, 1, 0], 'line_display': 'x+y=0', 'names': {'p': 'A'}}]}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['solve_line_constructions'], 'domain_operation': 'solve_line_constructions', 'problem_type_id': 'solve_line_constructions', 'presentation_mode': 'short_answer', 'answer_type': 'coordinate_pair', 'generation_constraints': {'variants': [{'stem': '', 'items': [{'kind': 'reflect_point', 'p': [3, 1], 'line': [1, -1, 0], 'line_display': 'x-y=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-4, 2], 'line': [1, 1, -1], 'line_display': 'x+y-1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [3, 3], 'line': [1, 1, -4], 'line_display': 'x+y-4=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [5, 1], 'line': [1, 1, -2], 'line_display': 'x+y-2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-1, 6], 'line': [1, 1, 4], 'line_display': 'x+y+4=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-5, 0], 'line': [1, -1, -3], 'line_display': 'x-y-3=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [0, -3], 'line': [1, -1, -3], 'line_display': 'x-y-3=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-5, 1], 'line': [1, -1, 2], 'line_display': 'x-y+2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-1, 1], 'line': [1, -1, -2], 'line_display': 'x-y-2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [4, 6], 'line': [1, -1, -3], 'line_display': 'x-y-3=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-2, 2], 'line': [1, 1, 1], 'line_display': 'x+y+1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [0, 3], 'line': [1, 1, -2], 'line_display': 'x+y-2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [4, -4], 'line': [1, -1, -1], 'line_display': 'x-y-1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-5, -4], 'line': [1, -1, 2], 'line_display': 'x-y+2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [5, -5], 'line': [1, -1, 3], 'line_display': 'x-y+3=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-2, -2], 'line': [1, -1, 4], 'line_display': 'x-y+4=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [4, -2], 'line': [1, -1, 1], 'line_display': 'x-y+1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [2, -5], 'line': [1, 1, 2], 'line_display': 'x+y+2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [6, 1], 'line': [1, -1, 1], 'line_display': 'x-y+1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-5, -1], 'line': [1, 1, 0], 'line_display': 'x+y=0', 'names': {'p': 'A'}}]}]}}, 'problem_type_id': 'solve_line_constructions', 'required_capabilities': ['solve_line_constructions'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'stem': '', 'items': [{'kind': 'reflect_point', 'p': [3, 1], 'line': [1, -1, 0], 'line_display': 'x-y=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-4, 2], 'line': [1, 1, -1], 'line_display': 'x+y-1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [3, 3], 'line': [1, 1, -4], 'line_display': 'x+y-4=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [5, 1], 'line': [1, 1, -2], 'line_display': 'x+y-2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-1, 6], 'line': [1, 1, 4], 'line_display': 'x+y+4=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-5, 0], 'line': [1, -1, -3], 'line_display': 'x-y-3=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [0, -3], 'line': [1, -1, -3], 'line_display': 'x-y-3=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-5, 1], 'line': [1, -1, 2], 'line_display': 'x-y+2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-1, 1], 'line': [1, -1, -2], 'line_display': 'x-y-2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [4, 6], 'line': [1, -1, -3], 'line_display': 'x-y-3=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-2, 2], 'line': [1, 1, 1], 'line_display': 'x+y+1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [0, 3], 'line': [1, 1, -2], 'line_display': 'x+y-2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [4, -4], 'line': [1, -1, -1], 'line_display': 'x-y-1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-5, -4], 'line': [1, -1, 2], 'line_display': 'x-y+2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [5, -5], 'line': [1, -1, 3], 'line_display': 'x-y+3=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-2, -2], 'line': [1, -1, 4], 'line_display': 'x-y+4=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [4, -2], 'line': [1, -1, 1], 'line_display': 'x-y+1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [2, -5], 'line': [1, 1, 2], 'line_display': 'x+y+2=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [6, 1], 'line': [1, -1, 1], 'line_display': 'x-y+1=0', 'names': {'p': 'A'}}]}, {'stem': '', 'items': [{'kind': 'reflect_point', 'p': [-5, -1], 'line': [1, 1, 0], 'line_display': 'x+y=0', 'names': {'p': 'A'}}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_ParallelAndPerpendicularLines', 'fixed_domain_key': 'analytic_geometry.line_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_line_constructions'], 'matched_capabilities': ['solve_line_constructions'], 'selected_operation': 'solve_line_constructions', 'registry_revision': 'promoted-ebaf64733fa3', 'domain_module': 'core.domain.promoted.analytic_geometry_lines.line_equations_domain', 'entrypoint': 'build_line_equations_matrix', 'allowed_operations': ['evaluate_line_statement_truth', 'solve_line_constructions', 'solve_line_equations', 'solve_line_parameters', 'solve_rectangle_perpendicular_diagonals'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_ParallelAndPerpendicularLines'}), seed)
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
