from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "solution_set"
PROBLEM_TYPE_ID = "select_linear_factors"
TEXTBOOK_EXAMPLE_ID = 12550
DEFAULT_COMPONENT_ID = "src_12550" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_FactorTheorem"
FIXED_DOMAIN_KEY = "algebra.polynomial_division"
DOMAIN_OPERATION = "select_linear_factors"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['select_linear_factors'], 'domain_operation': 'select_linear_factors', 'problem_type_id': 'select_linear_factors', 'presentation_mode': 'short_answer', 'answer_type': 'solution_set', 'generation_constraints': {'variants': [{'poly_coeffs': [2, -1, 0, -2, 1], 'candidates': [[1, 1], [1, -1], [2, -1], [6, -3]]}, {'poly_coeffs': [3, -6, -15, 18], 'candidates': [[1, -3], [3, -9], [1, 1], [1, -3]]}, {'poly_coeffs': [2, 1, -2, -1], 'candidates': [[2, 2], [1, -3], [1, 1], [1, 1]]}, {'poly_coeffs': [2, -1, -2, 1], 'candidates': [[1, 1], [2, -1], [3, -1], [6, -3]]}, {'poly_coeffs': [2, -2, -8, 8], 'candidates': [[1, 2], [3, 6], [1, -1], [1, 3]]}, {'poly_coeffs': [2, 0, -14, -12], 'candidates': [[3, 3], [1, -2], [1, 1], [1, 1]]}, {'poly_coeffs': [3, -12, 3, 18], 'candidates': [[1, -3], [2, -4], [1, -5], [1, -2]]}, {'poly_coeffs': [6, 15, 3, -6], 'candidates': [[1, 1], [3, 3], [3, -1], [1, 1]]}, {'poly_coeffs': [2, 1, -8, -4], 'candidates': [[3, -1], [1, -2], [2, 1], [6, 3]]}, {'poly_coeffs': [2, 0, -14, -12], 'candidates': [[1, 2], [2, 4], [3, -1], [1, 2]]}, {'poly_coeffs': [6, -3, -15, -6], 'candidates': [[2, 1], [1, 1], [1, -5], [4, 2]]}, {'poly_coeffs': [4, -10, 2, 4], 'candidates': [[3, -6], [1, -2], [1, 1], [1, -2]]}, {'poly_coeffs': [3, -3, -12, 12], 'candidates': [[1, 1], [1, -2], [1, -2], [3, -6]]}, {'poly_coeffs': [4, -10, -8, 6], 'candidates': [[1, -5], [6, -3], [2, -1], [2, -1]]}, {'poly_coeffs': [6, -21, 6, 9], 'candidates': [[1, -1], [1, -2], [2, -2], [2, 1]]}, {'poly_coeffs': [2, -9, 10, -3], 'candidates': [[2, -6], [1, -3], [1, -3], [1, 1]]}, {'poly_coeffs': [6, 3, -15, 6], 'candidates': [[1, 2], [1, 1], [3, 6], [1, -1]]}, {'poly_coeffs': [6, -9, -33, 18], 'candidates': [[2, 4], [1, 2], [3, -1], [1, 2]]}, {'poly_coeffs': [4, -18, 14, 12], 'candidates': [[1, -3], [1, -5], [4, 2], [2, 1]]}, {'poly_coeffs': [8, 8, -2, -2], 'candidates': [[1, -3], [2, 1], [4, 2], [2, 1]]}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['select_linear_factors'], 'domain_operation': 'select_linear_factors', 'problem_type_id': 'select_linear_factors', 'presentation_mode': 'short_answer', 'answer_type': 'solution_set', 'generation_constraints': {'variants': [{'poly_coeffs': [2, -1, 0, -2, 1], 'candidates': [[1, 1], [1, -1], [2, -1], [6, -3]]}, {'poly_coeffs': [3, -6, -15, 18], 'candidates': [[1, -3], [3, -9], [1, 1], [1, -3]]}, {'poly_coeffs': [2, 1, -2, -1], 'candidates': [[2, 2], [1, -3], [1, 1], [1, 1]]}, {'poly_coeffs': [2, -1, -2, 1], 'candidates': [[1, 1], [2, -1], [3, -1], [6, -3]]}, {'poly_coeffs': [2, -2, -8, 8], 'candidates': [[1, 2], [3, 6], [1, -1], [1, 3]]}, {'poly_coeffs': [2, 0, -14, -12], 'candidates': [[3, 3], [1, -2], [1, 1], [1, 1]]}, {'poly_coeffs': [3, -12, 3, 18], 'candidates': [[1, -3], [2, -4], [1, -5], [1, -2]]}, {'poly_coeffs': [6, 15, 3, -6], 'candidates': [[1, 1], [3, 3], [3, -1], [1, 1]]}, {'poly_coeffs': [2, 1, -8, -4], 'candidates': [[3, -1], [1, -2], [2, 1], [6, 3]]}, {'poly_coeffs': [2, 0, -14, -12], 'candidates': [[1, 2], [2, 4], [3, -1], [1, 2]]}, {'poly_coeffs': [6, -3, -15, -6], 'candidates': [[2, 1], [1, 1], [1, -5], [4, 2]]}, {'poly_coeffs': [4, -10, 2, 4], 'candidates': [[3, -6], [1, -2], [1, 1], [1, -2]]}, {'poly_coeffs': [3, -3, -12, 12], 'candidates': [[1, 1], [1, -2], [1, -2], [3, -6]]}, {'poly_coeffs': [4, -10, -8, 6], 'candidates': [[1, -5], [6, -3], [2, -1], [2, -1]]}, {'poly_coeffs': [6, -21, 6, 9], 'candidates': [[1, -1], [1, -2], [2, -2], [2, 1]]}, {'poly_coeffs': [2, -9, 10, -3], 'candidates': [[2, -6], [1, -3], [1, -3], [1, 1]]}, {'poly_coeffs': [6, 3, -15, 6], 'candidates': [[1, 2], [1, 1], [3, 6], [1, -1]]}, {'poly_coeffs': [6, -9, -33, 18], 'candidates': [[2, 4], [1, 2], [3, -1], [1, 2]]}, {'poly_coeffs': [4, -18, 14, 12], 'candidates': [[1, -3], [1, -5], [4, 2], [2, 1]]}, {'poly_coeffs': [8, 8, -2, -2], 'candidates': [[1, -3], [2, 1], [4, 2], [2, 1]]}]}}, 'problem_type_id': 'select_linear_factors', 'required_capabilities': ['select_linear_factors'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'poly_coeffs': [2, -1, 0, -2, 1], 'candidates': [[1, 1], [1, -1], [2, -1], [6, -3]]}, {'poly_coeffs': [3, -6, -15, 18], 'candidates': [[1, -3], [3, -9], [1, 1], [1, -3]]}, {'poly_coeffs': [2, 1, -2, -1], 'candidates': [[2, 2], [1, -3], [1, 1], [1, 1]]}, {'poly_coeffs': [2, -1, -2, 1], 'candidates': [[1, 1], [2, -1], [3, -1], [6, -3]]}, {'poly_coeffs': [2, -2, -8, 8], 'candidates': [[1, 2], [3, 6], [1, -1], [1, 3]]}, {'poly_coeffs': [2, 0, -14, -12], 'candidates': [[3, 3], [1, -2], [1, 1], [1, 1]]}, {'poly_coeffs': [3, -12, 3, 18], 'candidates': [[1, -3], [2, -4], [1, -5], [1, -2]]}, {'poly_coeffs': [6, 15, 3, -6], 'candidates': [[1, 1], [3, 3], [3, -1], [1, 1]]}, {'poly_coeffs': [2, 1, -8, -4], 'candidates': [[3, -1], [1, -2], [2, 1], [6, 3]]}, {'poly_coeffs': [2, 0, -14, -12], 'candidates': [[1, 2], [2, 4], [3, -1], [1, 2]]}, {'poly_coeffs': [6, -3, -15, -6], 'candidates': [[2, 1], [1, 1], [1, -5], [4, 2]]}, {'poly_coeffs': [4, -10, 2, 4], 'candidates': [[3, -6], [1, -2], [1, 1], [1, -2]]}, {'poly_coeffs': [3, -3, -12, 12], 'candidates': [[1, 1], [1, -2], [1, -2], [3, -6]]}, {'poly_coeffs': [4, -10, -8, 6], 'candidates': [[1, -5], [6, -3], [2, -1], [2, -1]]}, {'poly_coeffs': [6, -21, 6, 9], 'candidates': [[1, -1], [1, -2], [2, -2], [2, 1]]}, {'poly_coeffs': [2, -9, 10, -3], 'candidates': [[2, -6], [1, -3], [1, -3], [1, 1]]}, {'poly_coeffs': [6, 3, -15, 6], 'candidates': [[1, 2], [1, 1], [3, 6], [1, -1]]}, {'poly_coeffs': [6, -9, -33, 18], 'candidates': [[2, 4], [1, 2], [3, -1], [1, 2]]}, {'poly_coeffs': [4, -18, 14, 12], 'candidates': [[1, -3], [1, -5], [4, 2], [2, 1]]}, {'poly_coeffs': [8, 8, -2, -2], 'candidates': [[1, -3], [2, 1], [4, 2], [2, 1]]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_FactorTheorem', 'fixed_domain_key': 'algebra.polynomial_division', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['select_linear_factors'], 'matched_capabilities': ['select_linear_factors'], 'selected_operation': 'select_linear_factors', 'registry_revision': 'promoted-53d919cf7758', 'domain_module': 'core.domain.promoted.algebra_polynomial_division.polynomial_division_domain', 'entrypoint': 'build_polynomial_division_matrix', 'allowed_operations': ['evaluate_polynomial_statements', 'interpolate_polynomials', 'select_linear_factors', 'solve_erased_cubic', 'solve_masked_synthetic_coefficient', 'solve_polynomial_parameters'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_FactorTheorem'}), seed)
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
