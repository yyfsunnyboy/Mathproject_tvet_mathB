from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "short_answer"
PROBLEM_TYPE_ID = "solve_axis_triangle_area_line"
TEXTBOOK_EXAMPLE_ID = 12445
DEFAULT_COMPONENT_ID = "src_12445" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_EquationOfALine"
FIXED_DOMAIN_KEY = "analytic_geometry.line_equations"
DOMAIN_OPERATION = "solve_axis_triangle_area_line"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['solve_axis_triangle_area_line'], 'domain_operation': 'solve_axis_triangle_area_line', 'problem_type_id': 'solve_axis_triangle_area_line', 'presentation_mode': 'short_answer', 'answer_type': 'short_answer', 'generation_constraints': {'variants': [{'point': [4, 1], 'area': 1}, {'point': [6, -6], 'area': '3'}, {'point': [6, -16], 'area': '4'}, {'point': [-4, -8], 'area': '8'}, {'point': [5, -11], 'area': '18'}, {'point': [-8, 6], 'area': '2'}, {'point': [-6, -1], 'area': '3/2'}, {'point': [-5, 6], 'area': '15/2'}, {'point': [3, 12], 'area': '9'}, {'point': [-6, -3], 'area': '12'}, {'point': [-8, -3], 'area': '6'}, {'point': [8, 28], 'area': '2'}, {'point': [8, 36], 'area': '2'}, {'point': [-4, -2], 'area': '9'}, {'point': [2, 18], 'area': '3'}, {'point': [6, -20], 'area': '5'}, {'point': [3, -10], 'area': '15/2'}, {'point': [-7, -2], 'area': '25/2'}, {'point': [-4, 15], 'area': '5/2'}, {'point': [8, -11], 'area': '9/2'}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['solve_axis_triangle_area_line'], 'domain_operation': 'solve_axis_triangle_area_line', 'problem_type_id': 'solve_axis_triangle_area_line', 'presentation_mode': 'short_answer', 'answer_type': 'short_answer', 'generation_constraints': {'variants': [{'point': [4, 1], 'area': 1}, {'point': [6, -6], 'area': '3'}, {'point': [6, -16], 'area': '4'}, {'point': [-4, -8], 'area': '8'}, {'point': [5, -11], 'area': '18'}, {'point': [-8, 6], 'area': '2'}, {'point': [-6, -1], 'area': '3/2'}, {'point': [-5, 6], 'area': '15/2'}, {'point': [3, 12], 'area': '9'}, {'point': [-6, -3], 'area': '12'}, {'point': [-8, -3], 'area': '6'}, {'point': [8, 28], 'area': '2'}, {'point': [8, 36], 'area': '2'}, {'point': [-4, -2], 'area': '9'}, {'point': [2, 18], 'area': '3'}, {'point': [6, -20], 'area': '5'}, {'point': [3, -10], 'area': '15/2'}, {'point': [-7, -2], 'area': '25/2'}, {'point': [-4, 15], 'area': '5/2'}, {'point': [8, -11], 'area': '9/2'}]}}, 'problem_type_id': 'solve_axis_triangle_area_line', 'required_capabilities': ['solve_axis_triangle_area_line'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'point': [4, 1], 'area': 1}, {'point': [6, -6], 'area': '3'}, {'point': [6, -16], 'area': '4'}, {'point': [-4, -8], 'area': '8'}, {'point': [5, -11], 'area': '18'}, {'point': [-8, 6], 'area': '2'}, {'point': [-6, -1], 'area': '3/2'}, {'point': [-5, 6], 'area': '15/2'}, {'point': [3, 12], 'area': '9'}, {'point': [-6, -3], 'area': '12'}, {'point': [-8, -3], 'area': '6'}, {'point': [8, 28], 'area': '2'}, {'point': [8, 36], 'area': '2'}, {'point': [-4, -2], 'area': '9'}, {'point': [2, 18], 'area': '3'}, {'point': [6, -20], 'area': '5'}, {'point': [3, -10], 'area': '15/2'}, {'point': [-7, -2], 'area': '25/2'}, {'point': [-4, 15], 'area': '5/2'}, {'point': [8, -11], 'area': '9/2'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_EquationOfALine', 'fixed_domain_key': 'analytic_geometry.line_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_axis_triangle_area_line'], 'matched_capabilities': ['solve_axis_triangle_area_line'], 'selected_operation': 'solve_axis_triangle_area_line', 'registry_revision': 'promoted-ebaf64733fa3', 'domain_module': 'core.domain.promoted.analytic_geometry_lines.line_equations_domain', 'entrypoint': 'build_line_equations_matrix', 'allowed_operations': ['evaluate_line_statement_truth', 'fill_line_property_table', 'slope_of_line_from_equation', 'solve_axis_triangle_area_line', 'solve_line_equations'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_EquationOfALine'}), seed)
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
