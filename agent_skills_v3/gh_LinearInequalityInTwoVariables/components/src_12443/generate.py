from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "solve_region_coefficients_from_figure"
TEXTBOOK_EXAMPLE_ID = 12443
DEFAULT_COMPONENT_ID = "src_12443" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_LinearInequalityInTwoVariables"
FIXED_DOMAIN_KEY = "analytic_geometry.line_equations"
DOMAIN_OPERATION = "solve_region_coefficients_from_figure"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['solve_region_coefficients_from_figure'], 'domain_operation': 'solve_region_coefficients_from_figure', 'problem_type_id': 'solve_region_coefficients_from_figure', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'a_point': [2, 6], 'b_point': [5, 0], 'bound': 5}, {'a_point': [2, 4], 'b_point': [8, 0], 'bound': 5}, {'a_point': [1, 4], 'b_point': [8, 0], 'bound': 5}, {'a_point': [1, 3], 'b_point': [3, 0], 'bound': 5}, {'a_point': [2, 5], 'b_point': [8, 0], 'bound': 5}, {'a_point': [3, 4], 'b_point': [8, 0], 'bound': 5}, {'a_point': [2, 2], 'b_point': [4, 0], 'bound': 5}, {'a_point': [1, 2], 'b_point': [5, 0], 'bound': 5}, {'a_point': [1, 4], 'b_point': [3, 0], 'bound': 5}, {'a_point': [1, 4], 'b_point': [5, 0], 'bound': 5}, {'a_point': [4, 2], 'b_point': [7, 0], 'bound': 5}, {'a_point': [1, 7], 'b_point': [7, 0], 'bound': 5}, {'a_point': [2, 6], 'b_point': [7, 0], 'bound': 5}, {'a_point': [3, 2], 'b_point': [6, 0], 'bound': 5}, {'a_point': [2, 4], 'b_point': [5, 0], 'bound': 5}, {'a_point': [2, 5], 'b_point': [6, 0], 'bound': 5}, {'a_point': [1, 3], 'b_point': [7, 0], 'bound': 5}, {'a_point': [2, 5], 'b_point': [3, 0], 'bound': 5}, {'a_point': [3, 2], 'b_point': [5, 0], 'bound': 5}, {'a_point': [4, 3], 'b_point': [8, 0], 'bound': 5}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['solve_region_coefficients_from_figure'], 'domain_operation': 'solve_region_coefficients_from_figure', 'problem_type_id': 'solve_region_coefficients_from_figure', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'a_point': [2, 6], 'b_point': [5, 0], 'bound': 5}, {'a_point': [2, 4], 'b_point': [8, 0], 'bound': 5}, {'a_point': [1, 4], 'b_point': [8, 0], 'bound': 5}, {'a_point': [1, 3], 'b_point': [3, 0], 'bound': 5}, {'a_point': [2, 5], 'b_point': [8, 0], 'bound': 5}, {'a_point': [3, 4], 'b_point': [8, 0], 'bound': 5}, {'a_point': [2, 2], 'b_point': [4, 0], 'bound': 5}, {'a_point': [1, 2], 'b_point': [5, 0], 'bound': 5}, {'a_point': [1, 4], 'b_point': [3, 0], 'bound': 5}, {'a_point': [1, 4], 'b_point': [5, 0], 'bound': 5}, {'a_point': [4, 2], 'b_point': [7, 0], 'bound': 5}, {'a_point': [1, 7], 'b_point': [7, 0], 'bound': 5}, {'a_point': [2, 6], 'b_point': [7, 0], 'bound': 5}, {'a_point': [3, 2], 'b_point': [6, 0], 'bound': 5}, {'a_point': [2, 4], 'b_point': [5, 0], 'bound': 5}, {'a_point': [2, 5], 'b_point': [6, 0], 'bound': 5}, {'a_point': [1, 3], 'b_point': [7, 0], 'bound': 5}, {'a_point': [2, 5], 'b_point': [3, 0], 'bound': 5}, {'a_point': [3, 2], 'b_point': [5, 0], 'bound': 5}, {'a_point': [4, 3], 'b_point': [8, 0], 'bound': 5}]}}, 'problem_type_id': 'solve_region_coefficients_from_figure', 'required_capabilities': ['solve_region_coefficients_from_figure'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'a_point': [2, 6], 'b_point': [5, 0], 'bound': 5}, {'a_point': [2, 4], 'b_point': [8, 0], 'bound': 5}, {'a_point': [1, 4], 'b_point': [8, 0], 'bound': 5}, {'a_point': [1, 3], 'b_point': [3, 0], 'bound': 5}, {'a_point': [2, 5], 'b_point': [8, 0], 'bound': 5}, {'a_point': [3, 4], 'b_point': [8, 0], 'bound': 5}, {'a_point': [2, 2], 'b_point': [4, 0], 'bound': 5}, {'a_point': [1, 2], 'b_point': [5, 0], 'bound': 5}, {'a_point': [1, 4], 'b_point': [3, 0], 'bound': 5}, {'a_point': [1, 4], 'b_point': [5, 0], 'bound': 5}, {'a_point': [4, 2], 'b_point': [7, 0], 'bound': 5}, {'a_point': [1, 7], 'b_point': [7, 0], 'bound': 5}, {'a_point': [2, 6], 'b_point': [7, 0], 'bound': 5}, {'a_point': [3, 2], 'b_point': [6, 0], 'bound': 5}, {'a_point': [2, 4], 'b_point': [5, 0], 'bound': 5}, {'a_point': [2, 5], 'b_point': [6, 0], 'bound': 5}, {'a_point': [1, 3], 'b_point': [7, 0], 'bound': 5}, {'a_point': [2, 5], 'b_point': [3, 0], 'bound': 5}, {'a_point': [3, 2], 'b_point': [5, 0], 'bound': 5}, {'a_point': [4, 3], 'b_point': [8, 0], 'bound': 5}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_LinearInequalityInTwoVariables', 'fixed_domain_key': 'analytic_geometry.line_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_region_coefficients_from_figure'], 'matched_capabilities': ['solve_region_coefficients_from_figure'], 'selected_operation': 'solve_region_coefficients_from_figure', 'registry_revision': 'promoted-ebaf64733fa3', 'domain_module': 'core.domain.promoted.analytic_geometry_lines.line_equations_domain', 'entrypoint': 'build_line_equations_matrix', 'allowed_operations': ['evaluate_line_statement_truth', 'graph_inequality_system', 'read_region_signs_from_figure', 'select_points_same_side', 'solve_region_coefficients_from_figure', 'solve_triangle_region_system'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_LinearInequalityInTwoVariables'}), seed)
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
