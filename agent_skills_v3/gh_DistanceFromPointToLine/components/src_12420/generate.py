from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "compute_line_distances"
TEXTBOOK_EXAMPLE_ID = 12420
DEFAULT_COMPONENT_ID = "src_12420" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_DistanceFromPointToLine"
FIXED_DOMAIN_KEY = "analytic_geometry.line_equations"
DOMAIN_OPERATION = "compute_line_distances"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['compute_line_distances'], 'domain_operation': 'compute_line_distances', 'problem_type_id': 'compute_line_distances', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [3, 4, 11], 'l2': [6, 8, -9]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [12, 5, 0], 'l2': [-36, -15, -11]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [15, 8, 6], 'l2': [30, 16, 17]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 15, -6], 'l2': [-24, -45, -18]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [6, 8, -8], 'l2': [-18, -24, 5]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 6, 0], 'l2': [-16, -12, -5]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [5, 12, -5], 'l2': [-10, -24, -8]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 15, 1], 'l2': [-24, -45, 0]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [6, 8, 10], 'l2': [-12, -16, 13]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [6, 8, 3], 'l2': [18, 24, -12]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [4, 3, -4], 'l2': [-8, -6, 17]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [5, 12, -10], 'l2': [-10, -24, -14]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 6, 2], 'l2': [16, 12, -15]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [4, 3, 7], 'l2': [8, 6, -10]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [15, 8, -5], 'l2': [45, 24, -16]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [15, 8, 1], 'l2': [45, 24, 7]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [15, 8, 6], 'l2': [30, 16, 0]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [12, 5, 3], 'l2': [-24, -10, -8]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 15, 5], 'l2': [-16, -30, -20]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 15, 1], 'l2': [-16, -30, -9]}]}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['compute_line_distances'], 'domain_operation': 'compute_line_distances', 'problem_type_id': 'compute_line_distances', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [3, 4, 11], 'l2': [6, 8, -9]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [12, 5, 0], 'l2': [-36, -15, -11]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [15, 8, 6], 'l2': [30, 16, 17]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 15, -6], 'l2': [-24, -45, -18]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [6, 8, -8], 'l2': [-18, -24, 5]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 6, 0], 'l2': [-16, -12, -5]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [5, 12, -5], 'l2': [-10, -24, -8]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 15, 1], 'l2': [-24, -45, 0]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [6, 8, 10], 'l2': [-12, -16, 13]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [6, 8, 3], 'l2': [18, 24, -12]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [4, 3, -4], 'l2': [-8, -6, 17]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [5, 12, -10], 'l2': [-10, -24, -14]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 6, 2], 'l2': [16, 12, -15]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [4, 3, 7], 'l2': [8, 6, -10]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [15, 8, -5], 'l2': [45, 24, -16]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [15, 8, 1], 'l2': [45, 24, 7]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [15, 8, 6], 'l2': [30, 16, 0]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [12, 5, 3], 'l2': [-24, -10, -8]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 15, 5], 'l2': [-16, -30, -20]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 15, 1], 'l2': [-16, -30, -9]}]}]}}, 'problem_type_id': 'compute_line_distances', 'required_capabilities': ['compute_line_distances'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [3, 4, 11], 'l2': [6, 8, -9]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [12, 5, 0], 'l2': [-36, -15, -11]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [15, 8, 6], 'l2': [30, 16, 17]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 15, -6], 'l2': [-24, -45, -18]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [6, 8, -8], 'l2': [-18, -24, 5]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 6, 0], 'l2': [-16, -12, -5]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [5, 12, -5], 'l2': [-10, -24, -8]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 15, 1], 'l2': [-24, -45, 0]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [6, 8, 10], 'l2': [-12, -16, 13]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [6, 8, 3], 'l2': [18, 24, -12]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [4, 3, -4], 'l2': [-8, -6, 17]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [5, 12, -10], 'l2': [-10, -24, -14]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 6, 2], 'l2': [16, 12, -15]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [4, 3, 7], 'l2': [8, 6, -10]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [15, 8, -5], 'l2': [45, 24, -16]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [15, 8, 1], 'l2': [45, 24, 7]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [15, 8, 6], 'l2': [30, 16, 0]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [12, 5, 3], 'l2': [-24, -10, -8]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 15, 5], 'l2': [-16, -30, -20]}]}, {'stem': '', 'items': [{'kind': 'parallel_lines', 'l1': [8, 15, 1], 'l2': [-16, -30, -9]}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_DistanceFromPointToLine', 'fixed_domain_key': 'analytic_geometry.line_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['compute_line_distances'], 'matched_capabilities': ['compute_line_distances'], 'selected_operation': 'compute_line_distances', 'registry_revision': 'promoted-ebaf64733fa3', 'domain_module': 'core.domain.promoted.analytic_geometry_lines.line_equations_domain', 'entrypoint': 'build_line_equations_matrix', 'allowed_operations': ['compute_line_distances', 'evaluate_line_statement_truth', 'solve_line_parameters', 'solve_parallel_line_family', 'solve_window_decorative_lines'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_DistanceFromPointToLine'}), seed)
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
