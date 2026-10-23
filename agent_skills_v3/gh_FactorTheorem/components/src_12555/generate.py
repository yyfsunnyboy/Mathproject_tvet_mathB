from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "solve_masked_synthetic_coefficient"
TEXTBOOK_EXAMPLE_ID = 12555
DEFAULT_COMPONENT_ID = "src_12555" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_FactorTheorem"
FIXED_DOMAIN_KEY = "algebra.polynomial_division"
DOMAIN_OPERATION = "solve_masked_synthetic_coefficient"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['solve_masked_synthetic_coefficient'], 'domain_operation': 'solve_masked_synthetic_coefficient', 'problem_type_id': 'solve_masked_synthetic_coefficient', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'coefficients': [None, 0, 0, 0, 1, 0, 0, 3, -5], 'mask_index': 0, 'root': -2, 'remainder': 8}, {'coefficients': [None, 0, 0, 0, 1, 4, 1], 'mask_index': 0, 'root': -1, 'remainder': 1}, {'coefficients': [None, 2, 4, 0, 0, 0, -5], 'mask_index': 0, 'root': 3, 'remainder': 1534}, {'coefficients': [None, 0, -3, 2, 0, -1], 'mask_index': 0, 'root': -1, 'remainder': 6}, {'coefficients': [None, 0, -1, 3, -5, 0, 5], 'mask_index': 0, 'root': -1, 'remainder': -3}, {'coefficients': [None, 4, 0, 0, 4, 0, 0, 0, -3], 'mask_index': 0, 'root': -3, 'remainder': -14988}, {'coefficients': [None, 3, 1, 4, 0, 5], 'mask_index': 0, 'root': -1, 'remainder': 10}, {'coefficients': [None, -1, -2, 0, 0, 3], 'mask_index': 0, 'root': 1, 'remainder': 2}, {'coefficients': [None, -4, 0, 0, -2, 0, -4, 0, -3], 'mask_index': 0, 'root': -2, 'remainder': -51}, {'coefficients': [None, 1, 0, -5, 0, 0, 0, 0, -4], 'mask_index': 0, 'root': 1, 'remainder': -7}, {'coefficients': [None, 0, -4, 0, 1, 0, -2], 'mask_index': 0, 'root': -2, 'remainder': 130}, {'coefficients': [None, 0, -5, 0, 0, -3, 0, 5, 1], 'mask_index': 0, 'root': 2, 'remainder': -589}, {'coefficients': [None, 0, -4, 0, 0, 3, 1, 0, 5], 'mask_index': 0, 'root': -1, 'remainder': -2}, {'coefficients': [None, 0, 0, 0, -2, 2, 0, -2], 'mask_index': 0, 'root': 2, 'remainder': 118}, {'coefficients': [None, -4, 0, 0, -1, -4], 'mask_index': 0, 'root': -3, 'remainder': -568}, {'coefficients': [None, 5, -3, 0, 4, 0, 5], 'mask_index': 0, 'root': -3, 'remainder': -2146}, {'coefficients': [None, 0, 0, -4, 3, 0, -5], 'mask_index': 0, 'root': -3, 'remainder': -1328}, {'coefficients': [None, 0, 0, -1, 0, 0, -2, -2, 3], 'mask_index': 0, 'root': 1, 'remainder': -3}, {'coefficients': [None, 0, -1, 0, 0, -1, 2], 'mask_index': 0, 'root': -2, 'remainder': 180}, {'coefficients': [None, 0, -1, -3, 0, 0, 5], 'mask_index': 0, 'root': -1, 'remainder': 9}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['solve_masked_synthetic_coefficient'], 'domain_operation': 'solve_masked_synthetic_coefficient', 'problem_type_id': 'solve_masked_synthetic_coefficient', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'coefficients': [None, 0, 0, 0, 1, 0, 0, 3, -5], 'mask_index': 0, 'root': -2, 'remainder': 8}, {'coefficients': [None, 0, 0, 0, 1, 4, 1], 'mask_index': 0, 'root': -1, 'remainder': 1}, {'coefficients': [None, 2, 4, 0, 0, 0, -5], 'mask_index': 0, 'root': 3, 'remainder': 1534}, {'coefficients': [None, 0, -3, 2, 0, -1], 'mask_index': 0, 'root': -1, 'remainder': 6}, {'coefficients': [None, 0, -1, 3, -5, 0, 5], 'mask_index': 0, 'root': -1, 'remainder': -3}, {'coefficients': [None, 4, 0, 0, 4, 0, 0, 0, -3], 'mask_index': 0, 'root': -3, 'remainder': -14988}, {'coefficients': [None, 3, 1, 4, 0, 5], 'mask_index': 0, 'root': -1, 'remainder': 10}, {'coefficients': [None, -1, -2, 0, 0, 3], 'mask_index': 0, 'root': 1, 'remainder': 2}, {'coefficients': [None, -4, 0, 0, -2, 0, -4, 0, -3], 'mask_index': 0, 'root': -2, 'remainder': -51}, {'coefficients': [None, 1, 0, -5, 0, 0, 0, 0, -4], 'mask_index': 0, 'root': 1, 'remainder': -7}, {'coefficients': [None, 0, -4, 0, 1, 0, -2], 'mask_index': 0, 'root': -2, 'remainder': 130}, {'coefficients': [None, 0, -5, 0, 0, -3, 0, 5, 1], 'mask_index': 0, 'root': 2, 'remainder': -589}, {'coefficients': [None, 0, -4, 0, 0, 3, 1, 0, 5], 'mask_index': 0, 'root': -1, 'remainder': -2}, {'coefficients': [None, 0, 0, 0, -2, 2, 0, -2], 'mask_index': 0, 'root': 2, 'remainder': 118}, {'coefficients': [None, -4, 0, 0, -1, -4], 'mask_index': 0, 'root': -3, 'remainder': -568}, {'coefficients': [None, 5, -3, 0, 4, 0, 5], 'mask_index': 0, 'root': -3, 'remainder': -2146}, {'coefficients': [None, 0, 0, -4, 3, 0, -5], 'mask_index': 0, 'root': -3, 'remainder': -1328}, {'coefficients': [None, 0, 0, -1, 0, 0, -2, -2, 3], 'mask_index': 0, 'root': 1, 'remainder': -3}, {'coefficients': [None, 0, -1, 0, 0, -1, 2], 'mask_index': 0, 'root': -2, 'remainder': 180}, {'coefficients': [None, 0, -1, -3, 0, 0, 5], 'mask_index': 0, 'root': -1, 'remainder': 9}]}}, 'problem_type_id': 'solve_masked_synthetic_coefficient', 'required_capabilities': ['solve_masked_synthetic_coefficient'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'coefficients': [None, 0, 0, 0, 1, 0, 0, 3, -5], 'mask_index': 0, 'root': -2, 'remainder': 8}, {'coefficients': [None, 0, 0, 0, 1, 4, 1], 'mask_index': 0, 'root': -1, 'remainder': 1}, {'coefficients': [None, 2, 4, 0, 0, 0, -5], 'mask_index': 0, 'root': 3, 'remainder': 1534}, {'coefficients': [None, 0, -3, 2, 0, -1], 'mask_index': 0, 'root': -1, 'remainder': 6}, {'coefficients': [None, 0, -1, 3, -5, 0, 5], 'mask_index': 0, 'root': -1, 'remainder': -3}, {'coefficients': [None, 4, 0, 0, 4, 0, 0, 0, -3], 'mask_index': 0, 'root': -3, 'remainder': -14988}, {'coefficients': [None, 3, 1, 4, 0, 5], 'mask_index': 0, 'root': -1, 'remainder': 10}, {'coefficients': [None, -1, -2, 0, 0, 3], 'mask_index': 0, 'root': 1, 'remainder': 2}, {'coefficients': [None, -4, 0, 0, -2, 0, -4, 0, -3], 'mask_index': 0, 'root': -2, 'remainder': -51}, {'coefficients': [None, 1, 0, -5, 0, 0, 0, 0, -4], 'mask_index': 0, 'root': 1, 'remainder': -7}, {'coefficients': [None, 0, -4, 0, 1, 0, -2], 'mask_index': 0, 'root': -2, 'remainder': 130}, {'coefficients': [None, 0, -5, 0, 0, -3, 0, 5, 1], 'mask_index': 0, 'root': 2, 'remainder': -589}, {'coefficients': [None, 0, -4, 0, 0, 3, 1, 0, 5], 'mask_index': 0, 'root': -1, 'remainder': -2}, {'coefficients': [None, 0, 0, 0, -2, 2, 0, -2], 'mask_index': 0, 'root': 2, 'remainder': 118}, {'coefficients': [None, -4, 0, 0, -1, -4], 'mask_index': 0, 'root': -3, 'remainder': -568}, {'coefficients': [None, 5, -3, 0, 4, 0, 5], 'mask_index': 0, 'root': -3, 'remainder': -2146}, {'coefficients': [None, 0, 0, -4, 3, 0, -5], 'mask_index': 0, 'root': -3, 'remainder': -1328}, {'coefficients': [None, 0, 0, -1, 0, 0, -2, -2, 3], 'mask_index': 0, 'root': 1, 'remainder': -3}, {'coefficients': [None, 0, -1, 0, 0, -1, 2], 'mask_index': 0, 'root': -2, 'remainder': 180}, {'coefficients': [None, 0, -1, -3, 0, 0, 5], 'mask_index': 0, 'root': -1, 'remainder': 9}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_FactorTheorem', 'fixed_domain_key': 'algebra.polynomial_division', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_masked_synthetic_coefficient'], 'matched_capabilities': ['solve_masked_synthetic_coefficient'], 'selected_operation': 'solve_masked_synthetic_coefficient', 'registry_revision': 'promoted-53d919cf7758', 'domain_module': 'core.domain.promoted.algebra_polynomial_division.polynomial_division_domain', 'entrypoint': 'build_polynomial_division_matrix', 'allowed_operations': ['evaluate_polynomial_statements', 'interpolate_polynomials', 'select_linear_factors', 'solve_erased_cubic', 'solve_masked_synthetic_coefficient', 'solve_polynomial_parameters'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_FactorTheorem'}), seed)
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
