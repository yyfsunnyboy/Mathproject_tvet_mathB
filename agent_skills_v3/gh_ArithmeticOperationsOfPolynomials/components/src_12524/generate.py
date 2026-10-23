from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "taylor_shift_expansion"
TEXTBOOK_EXAMPLE_ID = 12524
DEFAULT_COMPONENT_ID = "src_12524" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_ArithmeticOperationsOfPolynomials"
FIXED_DOMAIN_KEY = "algebra.polynomial_division"
DOMAIN_OPERATION = "taylor_shift_expansion"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['taylor_shift_expansion'], 'domain_operation': 'taylor_shift_expansion', 'problem_type_id': 'taylor_shift_expansion', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'poly_coeffs': [1, -1, -1, 1], 'center': 2, 'approx_x': '1.99', 'style': 'numbered'}, {'poly_coeffs': [2, 2, -1, -5], 'center': -1, 'approx_x': '-1.01', 'style': 'numbered'}, {'poly_coeffs': [1, 5, 4, 3], 'center': -2, 'approx_x': '-2.01', 'style': 'numbered'}, {'poly_coeffs': [1, 1, -1, 4], 'center': 3, 'approx_x': '2.99', 'style': 'numbered'}, {'poly_coeffs': [1, -3, -5, 1], 'center': -2, 'approx_x': '-1.99', 'style': 'numbered'}, {'poly_coeffs': [-1, 2, -1, 1], 'center': 2, 'approx_x': '2.01', 'style': 'numbered'}, {'poly_coeffs': [2, 1, 5, 5], 'center': 3, 'approx_x': '3.01', 'style': 'numbered'}, {'poly_coeffs': [2, -2, -5, 2], 'center': -2, 'approx_x': '-1.99', 'style': 'numbered'}, {'poly_coeffs': [2, 4, -5, 5], 'center': 2, 'approx_x': '1.99', 'style': 'numbered'}, {'poly_coeffs': [-1, 5, 4, 2], 'center': 2, 'approx_x': '2.01', 'style': 'numbered'}, {'poly_coeffs': [-1, 3, -3, 1], 'center': 2, 'approx_x': '1.99', 'style': 'numbered'}, {'poly_coeffs': [-1, 4, 5, 6], 'center': 3, 'approx_x': '2.99', 'style': 'numbered'}, {'poly_coeffs': [1, 6, -4, 3], 'center': 1, 'approx_x': '0.99', 'style': 'numbered'}, {'poly_coeffs': [-1, 4, -1, -5], 'center': 3, 'approx_x': '2.99', 'style': 'numbered'}, {'poly_coeffs': [2, -6, 4, 4], 'center': 3, 'approx_x': '3.01', 'style': 'numbered'}, {'poly_coeffs': [1, -1, -3, 1], 'center': 3, 'approx_x': '3.01', 'style': 'numbered'}, {'poly_coeffs': [-1, 2, -4, -4], 'center': 1, 'approx_x': '1.01', 'style': 'numbered'}, {'poly_coeffs': [1, -2, -4, 3], 'center': 1, 'approx_x': '0.99', 'style': 'numbered'}, {'poly_coeffs': [-1, -3, 3, 3], 'center': -2, 'approx_x': '-2.01', 'style': 'numbered'}, {'poly_coeffs': [-1, 5, -2, 6], 'center': -2, 'approx_x': '-1.99', 'style': 'numbered'}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['taylor_shift_expansion'], 'domain_operation': 'taylor_shift_expansion', 'problem_type_id': 'taylor_shift_expansion', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'poly_coeffs': [1, -1, -1, 1], 'center': 2, 'approx_x': '1.99', 'style': 'numbered'}, {'poly_coeffs': [2, 2, -1, -5], 'center': -1, 'approx_x': '-1.01', 'style': 'numbered'}, {'poly_coeffs': [1, 5, 4, 3], 'center': -2, 'approx_x': '-2.01', 'style': 'numbered'}, {'poly_coeffs': [1, 1, -1, 4], 'center': 3, 'approx_x': '2.99', 'style': 'numbered'}, {'poly_coeffs': [1, -3, -5, 1], 'center': -2, 'approx_x': '-1.99', 'style': 'numbered'}, {'poly_coeffs': [-1, 2, -1, 1], 'center': 2, 'approx_x': '2.01', 'style': 'numbered'}, {'poly_coeffs': [2, 1, 5, 5], 'center': 3, 'approx_x': '3.01', 'style': 'numbered'}, {'poly_coeffs': [2, -2, -5, 2], 'center': -2, 'approx_x': '-1.99', 'style': 'numbered'}, {'poly_coeffs': [2, 4, -5, 5], 'center': 2, 'approx_x': '1.99', 'style': 'numbered'}, {'poly_coeffs': [-1, 5, 4, 2], 'center': 2, 'approx_x': '2.01', 'style': 'numbered'}, {'poly_coeffs': [-1, 3, -3, 1], 'center': 2, 'approx_x': '1.99', 'style': 'numbered'}, {'poly_coeffs': [-1, 4, 5, 6], 'center': 3, 'approx_x': '2.99', 'style': 'numbered'}, {'poly_coeffs': [1, 6, -4, 3], 'center': 1, 'approx_x': '0.99', 'style': 'numbered'}, {'poly_coeffs': [-1, 4, -1, -5], 'center': 3, 'approx_x': '2.99', 'style': 'numbered'}, {'poly_coeffs': [2, -6, 4, 4], 'center': 3, 'approx_x': '3.01', 'style': 'numbered'}, {'poly_coeffs': [1, -1, -3, 1], 'center': 3, 'approx_x': '3.01', 'style': 'numbered'}, {'poly_coeffs': [-1, 2, -4, -4], 'center': 1, 'approx_x': '1.01', 'style': 'numbered'}, {'poly_coeffs': [1, -2, -4, 3], 'center': 1, 'approx_x': '0.99', 'style': 'numbered'}, {'poly_coeffs': [-1, -3, 3, 3], 'center': -2, 'approx_x': '-2.01', 'style': 'numbered'}, {'poly_coeffs': [-1, 5, -2, 6], 'center': -2, 'approx_x': '-1.99', 'style': 'numbered'}]}}, 'problem_type_id': 'taylor_shift_expansion', 'required_capabilities': ['taylor_shift_expansion'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'poly_coeffs': [1, -1, -1, 1], 'center': 2, 'approx_x': '1.99', 'style': 'numbered'}, {'poly_coeffs': [2, 2, -1, -5], 'center': -1, 'approx_x': '-1.01', 'style': 'numbered'}, {'poly_coeffs': [1, 5, 4, 3], 'center': -2, 'approx_x': '-2.01', 'style': 'numbered'}, {'poly_coeffs': [1, 1, -1, 4], 'center': 3, 'approx_x': '2.99', 'style': 'numbered'}, {'poly_coeffs': [1, -3, -5, 1], 'center': -2, 'approx_x': '-1.99', 'style': 'numbered'}, {'poly_coeffs': [-1, 2, -1, 1], 'center': 2, 'approx_x': '2.01', 'style': 'numbered'}, {'poly_coeffs': [2, 1, 5, 5], 'center': 3, 'approx_x': '3.01', 'style': 'numbered'}, {'poly_coeffs': [2, -2, -5, 2], 'center': -2, 'approx_x': '-1.99', 'style': 'numbered'}, {'poly_coeffs': [2, 4, -5, 5], 'center': 2, 'approx_x': '1.99', 'style': 'numbered'}, {'poly_coeffs': [-1, 5, 4, 2], 'center': 2, 'approx_x': '2.01', 'style': 'numbered'}, {'poly_coeffs': [-1, 3, -3, 1], 'center': 2, 'approx_x': '1.99', 'style': 'numbered'}, {'poly_coeffs': [-1, 4, 5, 6], 'center': 3, 'approx_x': '2.99', 'style': 'numbered'}, {'poly_coeffs': [1, 6, -4, 3], 'center': 1, 'approx_x': '0.99', 'style': 'numbered'}, {'poly_coeffs': [-1, 4, -1, -5], 'center': 3, 'approx_x': '2.99', 'style': 'numbered'}, {'poly_coeffs': [2, -6, 4, 4], 'center': 3, 'approx_x': '3.01', 'style': 'numbered'}, {'poly_coeffs': [1, -1, -3, 1], 'center': 3, 'approx_x': '3.01', 'style': 'numbered'}, {'poly_coeffs': [-1, 2, -4, -4], 'center': 1, 'approx_x': '1.01', 'style': 'numbered'}, {'poly_coeffs': [1, -2, -4, 3], 'center': 1, 'approx_x': '0.99', 'style': 'numbered'}, {'poly_coeffs': [-1, -3, 3, 3], 'center': -2, 'approx_x': '-2.01', 'style': 'numbered'}, {'poly_coeffs': [-1, 5, -2, 6], 'center': -2, 'approx_x': '-1.99', 'style': 'numbered'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_ArithmeticOperationsOfPolynomials', 'fixed_domain_key': 'algebra.polynomial_division', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['taylor_shift_expansion'], 'matched_capabilities': ['taylor_shift_expansion'], 'selected_operation': 'taylor_shift_expansion', 'registry_revision': 'promoted-53d919cf7758', 'domain_module': 'core.domain.promoted.algebra_polynomial_division.polynomial_division_domain', 'entrypoint': 'build_polynomial_division_matrix', 'allowed_operations': ['evaluate_polynomial_statements', 'evaluate_polynomial_values', 'polynomial_arithmetic_items', 'solve_divisor_from_quotient_remainder', 'solve_polynomial_parameters', 'taylor_shift_expansion'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_ArithmeticOperationsOfPolynomials'}), seed)
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
