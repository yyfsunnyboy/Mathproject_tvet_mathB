from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "slope_of_line_from_equation"
TEXTBOOK_EXAMPLE_ID = 12407
DEFAULT_COMPONENT_ID = "src_12407" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_EquationOfALine"
FIXED_DOMAIN_KEY = "analytic_geometry.line_equations"
DOMAIN_OPERATION = "slope_of_line_from_equation"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['slope_of_line_from_equation'], 'domain_operation': 'slope_of_line_from_equation', 'problem_type_id': 'slope_of_line_from_equation', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'line': [3, -2, -5], 'name': 'L', 'line_display': '3x-2y-5=0'}, {'line': [-3, 5, -6], 'name': 'L', 'line_display': '-3x+5y-6=0'}, {'line': [-1, 3, 4], 'name': 'L', 'line_display': '-x+3y+4=0'}, {'line': [-5, 5, 5], 'name': 'L', 'line_display': '-5x+5y+5=0'}, {'line': [-2, -5, -2], 'name': 'L', 'line_display': '-2x-5y-2=0'}, {'line': [-1, 5, -7], 'name': 'L', 'line_display': '-x+5y-7=0'}, {'line': [4, 6, -6], 'name': 'L', 'line_display': '4x+6y-6=0'}, {'line': [-5, -6, -5], 'name': 'L', 'line_display': '-5x-6y-5=0'}, {'line': [-6, -3, 2], 'name': 'L', 'line_display': '-6x-3y+2=0'}, {'line': [-4, -6, 9], 'name': 'L', 'line_display': '-4x-6y+9=0'}, {'line': [1, -6, -2], 'name': 'L', 'line_display': 'x-6y-2=0'}, {'line': [-2, -1, -2], 'name': 'L', 'line_display': '-2x-y-2=0'}, {'line': [-6, 1, 9], 'name': 'L', 'line_display': '-6x+y+9=0'}, {'line': [4, -4, -3], 'name': 'L', 'line_display': '4x-4y-3=0'}, {'line': [-1, 4, 8], 'name': 'L', 'line_display': '-x+4y+8=0'}, {'line': [1, 2, -7], 'name': 'L', 'line_display': 'x+2y-7=0'}, {'line': [-3, -5, 5], 'name': 'L', 'line_display': '-3x-5y+5=0'}, {'line': [-5, 3, 8], 'name': 'L', 'line_display': '-5x+3y+8=0'}, {'line': [-5, -6, 8], 'name': 'L', 'line_display': '-5x-6y+8=0'}, {'line': [3, -4, 2], 'name': 'L', 'line_display': '3x-4y+2=0'}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['slope_of_line_from_equation'], 'domain_operation': 'slope_of_line_from_equation', 'problem_type_id': 'slope_of_line_from_equation', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'line': [3, -2, -5], 'name': 'L', 'line_display': '3x-2y-5=0'}, {'line': [-3, 5, -6], 'name': 'L', 'line_display': '-3x+5y-6=0'}, {'line': [-1, 3, 4], 'name': 'L', 'line_display': '-x+3y+4=0'}, {'line': [-5, 5, 5], 'name': 'L', 'line_display': '-5x+5y+5=0'}, {'line': [-2, -5, -2], 'name': 'L', 'line_display': '-2x-5y-2=0'}, {'line': [-1, 5, -7], 'name': 'L', 'line_display': '-x+5y-7=0'}, {'line': [4, 6, -6], 'name': 'L', 'line_display': '4x+6y-6=0'}, {'line': [-5, -6, -5], 'name': 'L', 'line_display': '-5x-6y-5=0'}, {'line': [-6, -3, 2], 'name': 'L', 'line_display': '-6x-3y+2=0'}, {'line': [-4, -6, 9], 'name': 'L', 'line_display': '-4x-6y+9=0'}, {'line': [1, -6, -2], 'name': 'L', 'line_display': 'x-6y-2=0'}, {'line': [-2, -1, -2], 'name': 'L', 'line_display': '-2x-y-2=0'}, {'line': [-6, 1, 9], 'name': 'L', 'line_display': '-6x+y+9=0'}, {'line': [4, -4, -3], 'name': 'L', 'line_display': '4x-4y-3=0'}, {'line': [-1, 4, 8], 'name': 'L', 'line_display': '-x+4y+8=0'}, {'line': [1, 2, -7], 'name': 'L', 'line_display': 'x+2y-7=0'}, {'line': [-3, -5, 5], 'name': 'L', 'line_display': '-3x-5y+5=0'}, {'line': [-5, 3, 8], 'name': 'L', 'line_display': '-5x+3y+8=0'}, {'line': [-5, -6, 8], 'name': 'L', 'line_display': '-5x-6y+8=0'}, {'line': [3, -4, 2], 'name': 'L', 'line_display': '3x-4y+2=0'}]}}, 'problem_type_id': 'slope_of_line_from_equation', 'required_capabilities': ['slope_of_line_from_equation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'line': [3, -2, -5], 'name': 'L', 'line_display': '3x-2y-5=0'}, {'line': [-3, 5, -6], 'name': 'L', 'line_display': '-3x+5y-6=0'}, {'line': [-1, 3, 4], 'name': 'L', 'line_display': '-x+3y+4=0'}, {'line': [-5, 5, 5], 'name': 'L', 'line_display': '-5x+5y+5=0'}, {'line': [-2, -5, -2], 'name': 'L', 'line_display': '-2x-5y-2=0'}, {'line': [-1, 5, -7], 'name': 'L', 'line_display': '-x+5y-7=0'}, {'line': [4, 6, -6], 'name': 'L', 'line_display': '4x+6y-6=0'}, {'line': [-5, -6, -5], 'name': 'L', 'line_display': '-5x-6y-5=0'}, {'line': [-6, -3, 2], 'name': 'L', 'line_display': '-6x-3y+2=0'}, {'line': [-4, -6, 9], 'name': 'L', 'line_display': '-4x-6y+9=0'}, {'line': [1, -6, -2], 'name': 'L', 'line_display': 'x-6y-2=0'}, {'line': [-2, -1, -2], 'name': 'L', 'line_display': '-2x-y-2=0'}, {'line': [-6, 1, 9], 'name': 'L', 'line_display': '-6x+y+9=0'}, {'line': [4, -4, -3], 'name': 'L', 'line_display': '4x-4y-3=0'}, {'line': [-1, 4, 8], 'name': 'L', 'line_display': '-x+4y+8=0'}, {'line': [1, 2, -7], 'name': 'L', 'line_display': 'x+2y-7=0'}, {'line': [-3, -5, 5], 'name': 'L', 'line_display': '-3x-5y+5=0'}, {'line': [-5, 3, 8], 'name': 'L', 'line_display': '-5x+3y+8=0'}, {'line': [-5, -6, 8], 'name': 'L', 'line_display': '-5x-6y+8=0'}, {'line': [3, -4, 2], 'name': 'L', 'line_display': '3x-4y+2=0'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_EquationOfALine', 'fixed_domain_key': 'analytic_geometry.line_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['slope_of_line_from_equation'], 'matched_capabilities': ['slope_of_line_from_equation'], 'selected_operation': 'slope_of_line_from_equation', 'registry_revision': 'promoted-ebaf64733fa3', 'domain_module': 'core.domain.promoted.analytic_geometry_lines.line_equations_domain', 'entrypoint': 'build_line_equations_matrix', 'allowed_operations': ['evaluate_line_statement_truth', 'fill_line_property_table', 'slope_of_line_from_equation', 'solve_axis_triangle_area_line', 'solve_line_equations'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_EquationOfALine'}), seed)
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
