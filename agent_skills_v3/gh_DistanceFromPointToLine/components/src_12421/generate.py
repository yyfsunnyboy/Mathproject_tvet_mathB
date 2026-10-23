from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "solve_window_decorative_lines"
TEXTBOOK_EXAMPLE_ID = 12421
DEFAULT_COMPONENT_ID = "src_12421" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_DistanceFromPointToLine"
FIXED_DOMAIN_KEY = "analytic_geometry.line_equations"
DOMAIN_OPERATION = "solve_window_decorative_lines"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['solve_window_decorative_lines'], 'domain_operation': 'solve_window_decorative_lines', 'problem_type_id': 'solve_window_decorative_lines', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'width': 34, 'height': 44, 'edge_point': [34, 5], 'delta_c': 6, 'asks': ['l1_equation', 'l2_equation']}, {'width': 32, 'height': 38, 'edge_point': [32, 3], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 22, 'height': 30, 'edge_point': [22, 4], 'delta_c': 10, 'asks': ['l1_equation', 'l2_equation']}, {'width': 30, 'height': 48, 'edge_point': [30, 9], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 32, 'height': 40, 'edge_point': [32, 4], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 20, 'height': 28, 'edge_point': [20, 4], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 36, 'height': 40, 'edge_point': [36, 2], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 22, 'height': 34, 'edge_point': [22, 6], 'delta_c': 6, 'asks': ['l1_equation', 'l2_equation']}, {'width': 28, 'height': 36, 'edge_point': [28, 4], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 34, 'height': 48, 'edge_point': [34, 7], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 28, 'height': 48, 'edge_point': [28, 10], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 30, 'height': 36, 'edge_point': [30, 3], 'delta_c': 10, 'asks': ['l1_equation', 'l2_equation']}, {'width': 20, 'height': 28, 'edge_point': [20, 4], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 16, 'height': 20, 'edge_point': [16, 2], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 22, 'height': 26, 'edge_point': [22, 2], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 36, 'height': 56, 'edge_point': [36, 10], 'delta_c': 10, 'asks': ['l1_equation', 'l2_equation']}, {'width': 16, 'height': 36, 'edge_point': [16, 10], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 32, 'height': 42, 'edge_point': [32, 5], 'delta_c': 6, 'asks': ['l1_equation', 'l2_equation']}, {'width': 28, 'height': 42, 'edge_point': [28, 7], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 20, 'height': 24, 'edge_point': [20, 2], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['solve_window_decorative_lines'], 'domain_operation': 'solve_window_decorative_lines', 'problem_type_id': 'solve_window_decorative_lines', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'width': 34, 'height': 44, 'edge_point': [34, 5], 'delta_c': 6, 'asks': ['l1_equation', 'l2_equation']}, {'width': 32, 'height': 38, 'edge_point': [32, 3], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 22, 'height': 30, 'edge_point': [22, 4], 'delta_c': 10, 'asks': ['l1_equation', 'l2_equation']}, {'width': 30, 'height': 48, 'edge_point': [30, 9], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 32, 'height': 40, 'edge_point': [32, 4], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 20, 'height': 28, 'edge_point': [20, 4], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 36, 'height': 40, 'edge_point': [36, 2], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 22, 'height': 34, 'edge_point': [22, 6], 'delta_c': 6, 'asks': ['l1_equation', 'l2_equation']}, {'width': 28, 'height': 36, 'edge_point': [28, 4], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 34, 'height': 48, 'edge_point': [34, 7], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 28, 'height': 48, 'edge_point': [28, 10], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 30, 'height': 36, 'edge_point': [30, 3], 'delta_c': 10, 'asks': ['l1_equation', 'l2_equation']}, {'width': 20, 'height': 28, 'edge_point': [20, 4], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 16, 'height': 20, 'edge_point': [16, 2], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 22, 'height': 26, 'edge_point': [22, 2], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 36, 'height': 56, 'edge_point': [36, 10], 'delta_c': 10, 'asks': ['l1_equation', 'l2_equation']}, {'width': 16, 'height': 36, 'edge_point': [16, 10], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 32, 'height': 42, 'edge_point': [32, 5], 'delta_c': 6, 'asks': ['l1_equation', 'l2_equation']}, {'width': 28, 'height': 42, 'edge_point': [28, 7], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 20, 'height': 24, 'edge_point': [20, 2], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}]}}, 'problem_type_id': 'solve_window_decorative_lines', 'required_capabilities': ['solve_window_decorative_lines'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'width': 34, 'height': 44, 'edge_point': [34, 5], 'delta_c': 6, 'asks': ['l1_equation', 'l2_equation']}, {'width': 32, 'height': 38, 'edge_point': [32, 3], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 22, 'height': 30, 'edge_point': [22, 4], 'delta_c': 10, 'asks': ['l1_equation', 'l2_equation']}, {'width': 30, 'height': 48, 'edge_point': [30, 9], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 32, 'height': 40, 'edge_point': [32, 4], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 20, 'height': 28, 'edge_point': [20, 4], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 36, 'height': 40, 'edge_point': [36, 2], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 22, 'height': 34, 'edge_point': [22, 6], 'delta_c': 6, 'asks': ['l1_equation', 'l2_equation']}, {'width': 28, 'height': 36, 'edge_point': [28, 4], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 34, 'height': 48, 'edge_point': [34, 7], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 28, 'height': 48, 'edge_point': [28, 10], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 30, 'height': 36, 'edge_point': [30, 3], 'delta_c': 10, 'asks': ['l1_equation', 'l2_equation']}, {'width': 20, 'height': 28, 'edge_point': [20, 4], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 16, 'height': 20, 'edge_point': [16, 2], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 22, 'height': 26, 'edge_point': [22, 2], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 36, 'height': 56, 'edge_point': [36, 10], 'delta_c': 10, 'asks': ['l1_equation', 'l2_equation']}, {'width': 16, 'height': 36, 'edge_point': [16, 10], 'delta_c': 4, 'asks': ['l1_equation', 'l2_equation']}, {'width': 32, 'height': 42, 'edge_point': [32, 5], 'delta_c': 6, 'asks': ['l1_equation', 'l2_equation']}, {'width': 28, 'height': 42, 'edge_point': [28, 7], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}, {'width': 20, 'height': 24, 'edge_point': [20, 2], 'delta_c': 8, 'asks': ['l1_equation', 'l2_equation']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_DistanceFromPointToLine', 'fixed_domain_key': 'analytic_geometry.line_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_window_decorative_lines'], 'matched_capabilities': ['solve_window_decorative_lines'], 'selected_operation': 'solve_window_decorative_lines', 'registry_revision': 'promoted-ebaf64733fa3', 'domain_module': 'core.domain.promoted.analytic_geometry_lines.line_equations_domain', 'entrypoint': 'build_line_equations_matrix', 'allowed_operations': ['compute_line_distances', 'evaluate_line_statement_truth', 'solve_line_parameters', 'solve_parallel_line_family', 'solve_window_decorative_lines'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_DistanceFromPointToLine'}), seed)
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
