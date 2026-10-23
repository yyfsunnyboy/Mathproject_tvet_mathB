from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "canvas"
ANSWER_TYPE = "drawing"
PROBLEM_TYPE_ID = "graph_inequality_system"
TEXTBOOK_EXAMPLE_ID = 12425
DEFAULT_COMPONENT_ID = "src_12425" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_LinearInequalityInTwoVariables"
FIXED_DOMAIN_KEY = "analytic_geometry.line_equations"
DOMAIN_OPERATION = "graph_inequality_system"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['graph_inequality_system'], 'domain_operation': 'graph_inequality_system', 'problem_type_id': 'graph_inequality_system', 'presentation_mode': 'canvas', 'answer_type': 'drawing', 'generation_constraints': {'variants': [{'relations': [{'coefficients': [2, -1, 4], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-2, 2, -2], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, -2, -4], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [2, -3, 6], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [3, -3, 1], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [2, 3, -6], 'op': '<='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [2, -2, -1], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [1, -2, -4], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-2, 2, 4], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-1, -3, 3], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [2, 3, -5], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-2, -1, 6], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-1, -1, -3], 'op': '<='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-1, 2, -5], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, 1, -3], 'op': '<='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, 2, -3], 'op': '<='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, -1, -1], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [1, -1, 4], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, -2, -5], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-1, 2, -6], 'op': '<='}], 'view': [-6, 6, -6, 6]}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['graph_inequality_system'], 'domain_operation': 'graph_inequality_system', 'problem_type_id': 'graph_inequality_system', 'presentation_mode': 'canvas', 'answer_type': 'drawing', 'generation_constraints': {'variants': [{'relations': [{'coefficients': [2, -1, 4], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-2, 2, -2], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, -2, -4], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [2, -3, 6], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [3, -3, 1], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [2, 3, -6], 'op': '<='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [2, -2, -1], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [1, -2, -4], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-2, 2, 4], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-1, -3, 3], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [2, 3, -5], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-2, -1, 6], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-1, -1, -3], 'op': '<='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-1, 2, -5], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, 1, -3], 'op': '<='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, 2, -3], 'op': '<='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, -1, -1], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [1, -1, 4], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, -2, -5], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-1, 2, -6], 'op': '<='}], 'view': [-6, 6, -6, 6]}]}}, 'problem_type_id': 'graph_inequality_system', 'required_capabilities': ['graph_inequality_system'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'canvas', 'answer_contract': {}, 'generation_constraints': {'variants': [{'relations': [{'coefficients': [2, -1, 4], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-2, 2, -2], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, -2, -4], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [2, -3, 6], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [3, -3, 1], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [2, 3, -6], 'op': '<='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [2, -2, -1], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [1, -2, -4], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-2, 2, 4], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-1, -3, 3], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [2, 3, -5], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-2, -1, 6], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-1, -1, -3], 'op': '<='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-1, 2, -5], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, 1, -3], 'op': '<='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, 2, -3], 'op': '<='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, -1, -1], 'op': '<'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [1, -1, 4], 'op': '>'}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-3, -2, -5], 'op': '>='}], 'view': [-6, 6, -6, 6]}, {'relations': [{'coefficients': [-1, 2, -6], 'op': '<='}], 'view': [-6, 6, -6, 6]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_LinearInequalityInTwoVariables', 'fixed_domain_key': 'analytic_geometry.line_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['graph_inequality_system'], 'matched_capabilities': ['graph_inequality_system'], 'selected_operation': 'graph_inequality_system', 'registry_revision': 'promoted-ebaf64733fa3', 'domain_module': 'core.domain.promoted.analytic_geometry_lines.line_equations_domain', 'entrypoint': 'build_line_equations_matrix', 'allowed_operations': ['evaluate_line_statement_truth', 'graph_inequality_system', 'read_region_signs_from_figure', 'select_points_same_side', 'solve_region_coefficients_from_figure', 'solve_triangle_region_system'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_LinearInequalityInTwoVariables'}), seed)
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
