from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "solve_divisor_from_quotient_remainder"
TEXTBOOK_EXAMPLE_ID = 12535
DEFAULT_COMPONENT_ID = "src_12535" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_ArithmeticOperationsOfPolynomials"
FIXED_DOMAIN_KEY = "algebra.polynomial_division"
DOMAIN_OPERATION = "solve_divisor_from_quotient_remainder"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['solve_divisor_from_quotient_remainder'], 'domain_operation': 'solve_divisor_from_quotient_remainder', 'problem_type_id': 'solve_divisor_from_quotient_remainder', 'presentation_mode': 'short_answer', 'answer_type': 'expression', 'generation_constraints': {'variants': [{'dividend': [1, 4, 5, -3], 'quotient': [1, 2], 'remainder': [2, -1]}, {'dividend': [2, 4, 1, -3], 'quotient': [1, 1], 'remainder': [3, 1]}, {'dividend': [1, 1, -7, 1], 'quotient': [1, -2], 'remainder': [1, -3]}, {'dividend': [2, -3, -4, -5], 'quotient': [1, -3], 'remainder': [3, 1]}, {'dividend': [1, 5, 0, -12], 'quotient': [1, 3], 'remainder': [-3, -3]}, {'dividend': [1, -4, -1, 2], 'quotient': [1, -2], 'remainder': [-3, -2]}, {'dividend': [1, 1, -1, -5], 'quotient': [1, -2], 'remainder': [3, -1]}, {'dividend': [2, 0, 0, 5], 'quotient': [1, 1], 'remainder': [-1, 2]}, {'dividend': [2, 0, -9, -7], 'quotient': [1, 1], 'remainder': [-3, -3]}, {'dividend': [1, 0, -2, 15], 'quotient': [1, 3], 'remainder': [3, 3]}, {'dividend': [1, 0, -5, 3], 'quotient': [1, 2], 'remainder': [-2, 1]}, {'dividend': [1, -5, 7, 6], 'quotient': [1, -2], 'remainder': [3, 2]}, {'dividend': [2, -2, -1, -2], 'quotient': [1, -2], 'remainder': [1, 2]}, {'dividend': [1, 1, 2, -4], 'quotient': [1, -1], 'remainder': [2, -2]}, {'dividend': [2, -9, 11, -11], 'quotient': [1, -3], 'remainder': [-1, -2]}, {'dividend': [1, -1, -2, 1], 'quotient': [1, -2], 'remainder': [2, -3]}, {'dividend': [1, 2, -4, -6], 'quotient': [1, 1], 'remainder': [-3, -4]}, {'dividend': [1, 0, 2, -6], 'quotient': [1, -1], 'remainder': [-1, -2]}, {'dividend': [1, -6, 10, -12], 'quotient': [1, -3], 'remainder': [-2, -3]}, {'dividend': [1, 0, -4, -11], 'quotient': [1, -3], 'remainder': [2, -2]}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['solve_divisor_from_quotient_remainder'], 'domain_operation': 'solve_divisor_from_quotient_remainder', 'problem_type_id': 'solve_divisor_from_quotient_remainder', 'presentation_mode': 'short_answer', 'answer_type': 'expression', 'generation_constraints': {'variants': [{'dividend': [1, 4, 5, -3], 'quotient': [1, 2], 'remainder': [2, -1]}, {'dividend': [2, 4, 1, -3], 'quotient': [1, 1], 'remainder': [3, 1]}, {'dividend': [1, 1, -7, 1], 'quotient': [1, -2], 'remainder': [1, -3]}, {'dividend': [2, -3, -4, -5], 'quotient': [1, -3], 'remainder': [3, 1]}, {'dividend': [1, 5, 0, -12], 'quotient': [1, 3], 'remainder': [-3, -3]}, {'dividend': [1, -4, -1, 2], 'quotient': [1, -2], 'remainder': [-3, -2]}, {'dividend': [1, 1, -1, -5], 'quotient': [1, -2], 'remainder': [3, -1]}, {'dividend': [2, 0, 0, 5], 'quotient': [1, 1], 'remainder': [-1, 2]}, {'dividend': [2, 0, -9, -7], 'quotient': [1, 1], 'remainder': [-3, -3]}, {'dividend': [1, 0, -2, 15], 'quotient': [1, 3], 'remainder': [3, 3]}, {'dividend': [1, 0, -5, 3], 'quotient': [1, 2], 'remainder': [-2, 1]}, {'dividend': [1, -5, 7, 6], 'quotient': [1, -2], 'remainder': [3, 2]}, {'dividend': [2, -2, -1, -2], 'quotient': [1, -2], 'remainder': [1, 2]}, {'dividend': [1, 1, 2, -4], 'quotient': [1, -1], 'remainder': [2, -2]}, {'dividend': [2, -9, 11, -11], 'quotient': [1, -3], 'remainder': [-1, -2]}, {'dividend': [1, -1, -2, 1], 'quotient': [1, -2], 'remainder': [2, -3]}, {'dividend': [1, 2, -4, -6], 'quotient': [1, 1], 'remainder': [-3, -4]}, {'dividend': [1, 0, 2, -6], 'quotient': [1, -1], 'remainder': [-1, -2]}, {'dividend': [1, -6, 10, -12], 'quotient': [1, -3], 'remainder': [-2, -3]}, {'dividend': [1, 0, -4, -11], 'quotient': [1, -3], 'remainder': [2, -2]}]}}, 'problem_type_id': 'solve_divisor_from_quotient_remainder', 'required_capabilities': ['solve_divisor_from_quotient_remainder'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'dividend': [1, 4, 5, -3], 'quotient': [1, 2], 'remainder': [2, -1]}, {'dividend': [2, 4, 1, -3], 'quotient': [1, 1], 'remainder': [3, 1]}, {'dividend': [1, 1, -7, 1], 'quotient': [1, -2], 'remainder': [1, -3]}, {'dividend': [2, -3, -4, -5], 'quotient': [1, -3], 'remainder': [3, 1]}, {'dividend': [1, 5, 0, -12], 'quotient': [1, 3], 'remainder': [-3, -3]}, {'dividend': [1, -4, -1, 2], 'quotient': [1, -2], 'remainder': [-3, -2]}, {'dividend': [1, 1, -1, -5], 'quotient': [1, -2], 'remainder': [3, -1]}, {'dividend': [2, 0, 0, 5], 'quotient': [1, 1], 'remainder': [-1, 2]}, {'dividend': [2, 0, -9, -7], 'quotient': [1, 1], 'remainder': [-3, -3]}, {'dividend': [1, 0, -2, 15], 'quotient': [1, 3], 'remainder': [3, 3]}, {'dividend': [1, 0, -5, 3], 'quotient': [1, 2], 'remainder': [-2, 1]}, {'dividend': [1, -5, 7, 6], 'quotient': [1, -2], 'remainder': [3, 2]}, {'dividend': [2, -2, -1, -2], 'quotient': [1, -2], 'remainder': [1, 2]}, {'dividend': [1, 1, 2, -4], 'quotient': [1, -1], 'remainder': [2, -2]}, {'dividend': [2, -9, 11, -11], 'quotient': [1, -3], 'remainder': [-1, -2]}, {'dividend': [1, -1, -2, 1], 'quotient': [1, -2], 'remainder': [2, -3]}, {'dividend': [1, 2, -4, -6], 'quotient': [1, 1], 'remainder': [-3, -4]}, {'dividend': [1, 0, 2, -6], 'quotient': [1, -1], 'remainder': [-1, -2]}, {'dividend': [1, -6, 10, -12], 'quotient': [1, -3], 'remainder': [-2, -3]}, {'dividend': [1, 0, -4, -11], 'quotient': [1, -3], 'remainder': [2, -2]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_ArithmeticOperationsOfPolynomials', 'fixed_domain_key': 'algebra.polynomial_division', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_divisor_from_quotient_remainder'], 'matched_capabilities': ['solve_divisor_from_quotient_remainder'], 'selected_operation': 'solve_divisor_from_quotient_remainder', 'registry_revision': 'promoted-53d919cf7758', 'domain_module': 'core.domain.promoted.algebra_polynomial_division.polynomial_division_domain', 'entrypoint': 'build_polynomial_division_matrix', 'allowed_operations': ['evaluate_polynomial_statements', 'evaluate_polynomial_values', 'polynomial_arithmetic_items', 'solve_divisor_from_quotient_remainder', 'solve_polynomial_parameters', 'taylor_shift_expansion'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_ArithmeticOperationsOfPolynomials'}), seed)
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
