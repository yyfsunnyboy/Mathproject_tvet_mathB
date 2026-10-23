from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "solve_parallel_line_family"
TEXTBOOK_EXAMPLE_ID = 12448
DEFAULT_COMPONENT_ID = "src_12448" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_DistanceFromPointToLine"
FIXED_DOMAIN_KEY = "analytic_geometry.line_equations"
DOMAIN_OPERATION = "solve_parallel_line_family"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['solve_parallel_line_family'], 'domain_operation': 'solve_parallel_line_family', 'problem_type_id': 'solve_parallel_line_family', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'a_point': [4, 0], 'b_point': [0, 3], 'p_point': [35, 43], 'spacing': 3}, {'a_point': [6, 0], 'b_point': [0, 8], 'p_point': [33, 41], 'spacing': 4}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [29, 16], 'spacing': 2}, {'a_point': [6, 0], 'b_point': [0, 8], 'p_point': [27, 44], 'spacing': 3}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [19, 45], 'spacing': 5}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [33, 17], 'spacing': 2}, {'a_point': [3, 0], 'b_point': [0, 4], 'p_point': [17, 11], 'spacing': 4}, {'a_point': [5, 0], 'b_point': [0, 12], 'p_point': [40, 31], 'spacing': 4}, {'a_point': [12, 0], 'b_point': [0, 5], 'p_point': [26, 15], 'spacing': 2}, {'a_point': [3, 0], 'b_point': [0, 4], 'p_point': [18, 21], 'spacing': 2}, {'a_point': [4, 0], 'b_point': [0, 3], 'p_point': [25, 19], 'spacing': 2}, {'a_point': [3, 0], 'b_point': [0, 4], 'p_point': [35, 23], 'spacing': 5}, {'a_point': [5, 0], 'b_point': [0, 12], 'p_point': [28, 18], 'spacing': 2}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [10, 20], 'spacing': 5}, {'a_point': [4, 0], 'b_point': [0, 3], 'p_point': [37, 33], 'spacing': 2}, {'a_point': [6, 0], 'b_point': [0, 8], 'p_point': [11, 14], 'spacing': 3}, {'a_point': [5, 0], 'b_point': [0, 12], 'p_point': [33, 16], 'spacing': 3}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [32, 34], 'spacing': 4}, {'a_point': [3, 0], 'b_point': [0, 4], 'p_point': [22, 12], 'spacing': 5}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [19, 16], 'spacing': 3}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['solve_parallel_line_family'], 'domain_operation': 'solve_parallel_line_family', 'problem_type_id': 'solve_parallel_line_family', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'a_point': [4, 0], 'b_point': [0, 3], 'p_point': [35, 43], 'spacing': 3}, {'a_point': [6, 0], 'b_point': [0, 8], 'p_point': [33, 41], 'spacing': 4}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [29, 16], 'spacing': 2}, {'a_point': [6, 0], 'b_point': [0, 8], 'p_point': [27, 44], 'spacing': 3}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [19, 45], 'spacing': 5}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [33, 17], 'spacing': 2}, {'a_point': [3, 0], 'b_point': [0, 4], 'p_point': [17, 11], 'spacing': 4}, {'a_point': [5, 0], 'b_point': [0, 12], 'p_point': [40, 31], 'spacing': 4}, {'a_point': [12, 0], 'b_point': [0, 5], 'p_point': [26, 15], 'spacing': 2}, {'a_point': [3, 0], 'b_point': [0, 4], 'p_point': [18, 21], 'spacing': 2}, {'a_point': [4, 0], 'b_point': [0, 3], 'p_point': [25, 19], 'spacing': 2}, {'a_point': [3, 0], 'b_point': [0, 4], 'p_point': [35, 23], 'spacing': 5}, {'a_point': [5, 0], 'b_point': [0, 12], 'p_point': [28, 18], 'spacing': 2}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [10, 20], 'spacing': 5}, {'a_point': [4, 0], 'b_point': [0, 3], 'p_point': [37, 33], 'spacing': 2}, {'a_point': [6, 0], 'b_point': [0, 8], 'p_point': [11, 14], 'spacing': 3}, {'a_point': [5, 0], 'b_point': [0, 12], 'p_point': [33, 16], 'spacing': 3}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [32, 34], 'spacing': 4}, {'a_point': [3, 0], 'b_point': [0, 4], 'p_point': [22, 12], 'spacing': 5}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [19, 16], 'spacing': 3}]}}, 'problem_type_id': 'solve_parallel_line_family', 'required_capabilities': ['solve_parallel_line_family'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'a_point': [4, 0], 'b_point': [0, 3], 'p_point': [35, 43], 'spacing': 3}, {'a_point': [6, 0], 'b_point': [0, 8], 'p_point': [33, 41], 'spacing': 4}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [29, 16], 'spacing': 2}, {'a_point': [6, 0], 'b_point': [0, 8], 'p_point': [27, 44], 'spacing': 3}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [19, 45], 'spacing': 5}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [33, 17], 'spacing': 2}, {'a_point': [3, 0], 'b_point': [0, 4], 'p_point': [17, 11], 'spacing': 4}, {'a_point': [5, 0], 'b_point': [0, 12], 'p_point': [40, 31], 'spacing': 4}, {'a_point': [12, 0], 'b_point': [0, 5], 'p_point': [26, 15], 'spacing': 2}, {'a_point': [3, 0], 'b_point': [0, 4], 'p_point': [18, 21], 'spacing': 2}, {'a_point': [4, 0], 'b_point': [0, 3], 'p_point': [25, 19], 'spacing': 2}, {'a_point': [3, 0], 'b_point': [0, 4], 'p_point': [35, 23], 'spacing': 5}, {'a_point': [5, 0], 'b_point': [0, 12], 'p_point': [28, 18], 'spacing': 2}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [10, 20], 'spacing': 5}, {'a_point': [4, 0], 'b_point': [0, 3], 'p_point': [37, 33], 'spacing': 2}, {'a_point': [6, 0], 'b_point': [0, 8], 'p_point': [11, 14], 'spacing': 3}, {'a_point': [5, 0], 'b_point': [0, 12], 'p_point': [33, 16], 'spacing': 3}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [32, 34], 'spacing': 4}, {'a_point': [3, 0], 'b_point': [0, 4], 'p_point': [22, 12], 'spacing': 5}, {'a_point': [8, 0], 'b_point': [0, 6], 'p_point': [19, 16], 'spacing': 3}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_DistanceFromPointToLine', 'fixed_domain_key': 'analytic_geometry.line_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_parallel_line_family'], 'matched_capabilities': ['solve_parallel_line_family'], 'selected_operation': 'solve_parallel_line_family', 'registry_revision': 'promoted-ebaf64733fa3', 'domain_module': 'core.domain.promoted.analytic_geometry_lines.line_equations_domain', 'entrypoint': 'build_line_equations_matrix', 'allowed_operations': ['compute_line_distances', 'evaluate_line_statement_truth', 'solve_line_parameters', 'solve_parallel_line_family', 'solve_window_decorative_lines'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_DistanceFromPointToLine'}), seed)
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
