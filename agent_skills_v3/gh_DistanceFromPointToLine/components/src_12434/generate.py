from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "evaluate_line_statement_truth"
TEXTBOOK_EXAMPLE_ID = 12434
DEFAULT_COMPONENT_ID = "src_12434" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_DistanceFromPointToLine"
FIXED_DOMAIN_KEY = "analytic_geometry.line_equations"
DOMAIN_OPERATION = "evaluate_line_statement_truth"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['evaluate_line_statement_truth'], 'domain_operation': 'evaluate_line_statement_truth', 'problem_type_id': 'evaluate_line_statement_truth', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'statement': {'kind': 'parallel_at_distance_count', 'line': [1, 2, -5], 'distance': 5, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, 1, -7], 'distance': 8, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-1, -4, 5], 'distance': 2, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-1, -4, -4], 'distance': 1, 'claimed_count': 4}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-4, 2, -5], 'distance': 8, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-3, -4, -1], 'distance': 5, 'claimed_count': 3}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [1, 1, -3], 'distance': 4, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, 4, 8], 'distance': 6, 'claimed_count': 4}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-4, -1, -6], 'distance': 7, 'claimed_count': 4}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [4, 1, -4], 'distance': 1, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-4, -3, -4], 'distance': 2, 'claimed_count': 3}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, 2, -1], 'distance': 3, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [2, -1, -7], 'distance': 6, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-4, -4, -1], 'distance': 6, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-2, -3, -1], 'distance': 3, 'claimed_count': 3}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-2, -4, -3], 'distance': 1, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, 1, 0], 'distance': 7, 'claimed_count': 3}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, -3, 7], 'distance': 2, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-3, 2, 7], 'distance': 2, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-2, -2, 8], 'distance': 1, 'claimed_count': 2}}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['evaluate_line_statement_truth'], 'domain_operation': 'evaluate_line_statement_truth', 'problem_type_id': 'evaluate_line_statement_truth', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'statement': {'kind': 'parallel_at_distance_count', 'line': [1, 2, -5], 'distance': 5, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, 1, -7], 'distance': 8, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-1, -4, 5], 'distance': 2, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-1, -4, -4], 'distance': 1, 'claimed_count': 4}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-4, 2, -5], 'distance': 8, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-3, -4, -1], 'distance': 5, 'claimed_count': 3}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [1, 1, -3], 'distance': 4, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, 4, 8], 'distance': 6, 'claimed_count': 4}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-4, -1, -6], 'distance': 7, 'claimed_count': 4}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [4, 1, -4], 'distance': 1, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-4, -3, -4], 'distance': 2, 'claimed_count': 3}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, 2, -1], 'distance': 3, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [2, -1, -7], 'distance': 6, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-4, -4, -1], 'distance': 6, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-2, -3, -1], 'distance': 3, 'claimed_count': 3}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-2, -4, -3], 'distance': 1, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, 1, 0], 'distance': 7, 'claimed_count': 3}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, -3, 7], 'distance': 2, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-3, 2, 7], 'distance': 2, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-2, -2, 8], 'distance': 1, 'claimed_count': 2}}]}}, 'problem_type_id': 'evaluate_line_statement_truth', 'required_capabilities': ['evaluate_line_statement_truth'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'statement': {'kind': 'parallel_at_distance_count', 'line': [1, 2, -5], 'distance': 5, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, 1, -7], 'distance': 8, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-1, -4, 5], 'distance': 2, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-1, -4, -4], 'distance': 1, 'claimed_count': 4}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-4, 2, -5], 'distance': 8, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-3, -4, -1], 'distance': 5, 'claimed_count': 3}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [1, 1, -3], 'distance': 4, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, 4, 8], 'distance': 6, 'claimed_count': 4}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-4, -1, -6], 'distance': 7, 'claimed_count': 4}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [4, 1, -4], 'distance': 1, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-4, -3, -4], 'distance': 2, 'claimed_count': 3}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, 2, -1], 'distance': 3, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [2, -1, -7], 'distance': 6, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-4, -4, -1], 'distance': 6, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-2, -3, -1], 'distance': 3, 'claimed_count': 3}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-2, -4, -3], 'distance': 1, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, 1, 0], 'distance': 7, 'claimed_count': 3}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [3, -3, 7], 'distance': 2, 'claimed_count': 2}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-3, 2, 7], 'distance': 2, 'claimed_count': 1}}, {'statement': {'kind': 'parallel_at_distance_count', 'line': [-2, -2, 8], 'distance': 1, 'claimed_count': 2}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_DistanceFromPointToLine', 'fixed_domain_key': 'analytic_geometry.line_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['evaluate_line_statement_truth'], 'matched_capabilities': ['evaluate_line_statement_truth'], 'selected_operation': 'evaluate_line_statement_truth', 'registry_revision': 'promoted-ebaf64733fa3', 'domain_module': 'core.domain.promoted.analytic_geometry_lines.line_equations_domain', 'entrypoint': 'build_line_equations_matrix', 'allowed_operations': ['compute_line_distances', 'evaluate_line_statement_truth', 'solve_line_parameters', 'solve_parallel_line_family', 'solve_window_decorative_lines'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_DistanceFromPointToLine'}), seed)
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
