from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "solve_polynomial_from_remainder_congruences"
TEXTBOOK_EXAMPLE_ID = 12548
DEFAULT_COMPONENT_ID = "src_12548" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RemainderTheorem"
FIXED_DOMAIN_KEY = "algebra.polynomial_division"
DOMAIN_OPERATION = "solve_polynomial_from_remainder_congruences"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['solve_polynomial_from_remainder_congruences'], 'domain_operation': 'solve_polynomial_from_remainder_congruences', 'problem_type_id': 'solve_polynomial_from_remainder_congruences', 'presentation_mode': 'short_answer', 'answer_type': 'expression', 'generation_constraints': {'variants': [{'degree': 3, 'conditions': [{'divisor': [1, 1, 2], 'remainder': [1, 2]}, {'divisor': [1, 1, -2], 'remainder': [5, -2]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, 2], 'remainder': [3]}, {'divisor': [1, 1, 3], 'remainder': [-4, 2]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, -1], 'remainder': [10, -8]}, {'divisor': [1, 1, -3], 'remainder': [6, -14]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, 2], 'remainder': [1, 11]}, {'divisor': [1, 2, -1], 'remainder': [7, -1]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, -3], 'remainder': [3, 0]}, {'divisor': [1, -1, -3], 'remainder': [3, 9]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, -3], 'remainder': [9, -5]}, {'divisor': [1, 2, 3], 'remainder': [7, 10]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -1, -2], 'remainder': [12, 13]}, {'divisor': [1, -1, -1], 'remainder': [10, 8]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, 2], 'remainder': [-1, 12]}, {'divisor': [1, 2, -2], 'remainder': [16, -12]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, 3], 'remainder': [-9, -1]}, {'divisor': [1, 1, 2], 'remainder': [-9, -5]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, -1], 'remainder': [18, -6]}, {'divisor': [1, -2, -1], 'remainder': [6, 2]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -2, -3], 'remainder': [11, 14]}, {'divisor': [1, -1, 2], 'remainder': [-1, -14]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, -1], 'remainder': [5, 0]}, {'divisor': [1, 2, -2], 'remainder': [6, -3]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, -1], 'remainder': [3, -1]}, {'divisor': [1, -1, 2], 'remainder': [1, -9]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -2, 1], 'remainder': [3]}, {'divisor': [1, 1, 3], 'remainder': [-2, 10]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, -1], 'remainder': [9, -9]}, {'divisor': [1, -1, 1], 'remainder': [-1, -3]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -1, -1], 'remainder': [11, 3]}, {'divisor': [1, -1, 1], 'remainder': [7, -9]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, -2], 'remainder': [3, 4]}, {'divisor': [1, 1, 1], 'remainder': [4]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -2, 2], 'remainder': [8, -12]}, {'divisor': [1, -2, -1], 'remainder': [11, 3]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -1, -3], 'remainder': [12, 16]}, {'divisor': [1, -2, 3], 'remainder': [13, -17]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -2, -1], 'remainder': [6, 0]}, {'divisor': [1, 1, -2], 'remainder': [2, -8]}]}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['solve_polynomial_from_remainder_congruences'], 'domain_operation': 'solve_polynomial_from_remainder_congruences', 'problem_type_id': 'solve_polynomial_from_remainder_congruences', 'presentation_mode': 'short_answer', 'answer_type': 'expression', 'generation_constraints': {'variants': [{'degree': 3, 'conditions': [{'divisor': [1, 1, 2], 'remainder': [1, 2]}, {'divisor': [1, 1, -2], 'remainder': [5, -2]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, 2], 'remainder': [3]}, {'divisor': [1, 1, 3], 'remainder': [-4, 2]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, -1], 'remainder': [10, -8]}, {'divisor': [1, 1, -3], 'remainder': [6, -14]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, 2], 'remainder': [1, 11]}, {'divisor': [1, 2, -1], 'remainder': [7, -1]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, -3], 'remainder': [3, 0]}, {'divisor': [1, -1, -3], 'remainder': [3, 9]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, -3], 'remainder': [9, -5]}, {'divisor': [1, 2, 3], 'remainder': [7, 10]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -1, -2], 'remainder': [12, 13]}, {'divisor': [1, -1, -1], 'remainder': [10, 8]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, 2], 'remainder': [-1, 12]}, {'divisor': [1, 2, -2], 'remainder': [16, -12]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, 3], 'remainder': [-9, -1]}, {'divisor': [1, 1, 2], 'remainder': [-9, -5]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, -1], 'remainder': [18, -6]}, {'divisor': [1, -2, -1], 'remainder': [6, 2]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -2, -3], 'remainder': [11, 14]}, {'divisor': [1, -1, 2], 'remainder': [-1, -14]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, -1], 'remainder': [5, 0]}, {'divisor': [1, 2, -2], 'remainder': [6, -3]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, -1], 'remainder': [3, -1]}, {'divisor': [1, -1, 2], 'remainder': [1, -9]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -2, 1], 'remainder': [3]}, {'divisor': [1, 1, 3], 'remainder': [-2, 10]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, -1], 'remainder': [9, -9]}, {'divisor': [1, -1, 1], 'remainder': [-1, -3]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -1, -1], 'remainder': [11, 3]}, {'divisor': [1, -1, 1], 'remainder': [7, -9]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, -2], 'remainder': [3, 4]}, {'divisor': [1, 1, 1], 'remainder': [4]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -2, 2], 'remainder': [8, -12]}, {'divisor': [1, -2, -1], 'remainder': [11, 3]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -1, -3], 'remainder': [12, 16]}, {'divisor': [1, -2, 3], 'remainder': [13, -17]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -2, -1], 'remainder': [6, 0]}, {'divisor': [1, 1, -2], 'remainder': [2, -8]}]}]}}, 'problem_type_id': 'solve_polynomial_from_remainder_congruences', 'required_capabilities': ['solve_polynomial_from_remainder_congruences'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'degree': 3, 'conditions': [{'divisor': [1, 1, 2], 'remainder': [1, 2]}, {'divisor': [1, 1, -2], 'remainder': [5, -2]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, 2], 'remainder': [3]}, {'divisor': [1, 1, 3], 'remainder': [-4, 2]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, -1], 'remainder': [10, -8]}, {'divisor': [1, 1, -3], 'remainder': [6, -14]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, 2], 'remainder': [1, 11]}, {'divisor': [1, 2, -1], 'remainder': [7, -1]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, -3], 'remainder': [3, 0]}, {'divisor': [1, -1, -3], 'remainder': [3, 9]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, -3], 'remainder': [9, -5]}, {'divisor': [1, 2, 3], 'remainder': [7, 10]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -1, -2], 'remainder': [12, 13]}, {'divisor': [1, -1, -1], 'remainder': [10, 8]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, 2], 'remainder': [-1, 12]}, {'divisor': [1, 2, -2], 'remainder': [16, -12]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, 3], 'remainder': [-9, -1]}, {'divisor': [1, 1, 2], 'remainder': [-9, -5]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, -1], 'remainder': [18, -6]}, {'divisor': [1, -2, -1], 'remainder': [6, 2]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -2, -3], 'remainder': [11, 14]}, {'divisor': [1, -1, 2], 'remainder': [-1, -14]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 2, -1], 'remainder': [5, 0]}, {'divisor': [1, 2, -2], 'remainder': [6, -3]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, -1], 'remainder': [3, -1]}, {'divisor': [1, -1, 2], 'remainder': [1, -9]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -2, 1], 'remainder': [3]}, {'divisor': [1, 1, 3], 'remainder': [-2, 10]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, -1], 'remainder': [9, -9]}, {'divisor': [1, -1, 1], 'remainder': [-1, -3]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -1, -1], 'remainder': [11, 3]}, {'divisor': [1, -1, 1], 'remainder': [7, -9]}]}, {'degree': 3, 'conditions': [{'divisor': [1, 1, -2], 'remainder': [3, 4]}, {'divisor': [1, 1, 1], 'remainder': [4]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -2, 2], 'remainder': [8, -12]}, {'divisor': [1, -2, -1], 'remainder': [11, 3]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -1, -3], 'remainder': [12, 16]}, {'divisor': [1, -2, 3], 'remainder': [13, -17]}]}, {'degree': 3, 'conditions': [{'divisor': [1, -2, -1], 'remainder': [6, 0]}, {'divisor': [1, 1, -2], 'remainder': [2, -8]}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_RemainderTheorem', 'fixed_domain_key': 'algebra.polynomial_division', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_polynomial_from_remainder_congruences'], 'matched_capabilities': ['solve_polynomial_from_remainder_congruences'], 'selected_operation': 'solve_polynomial_from_remainder_congruences', 'registry_revision': 'promoted-53d919cf7758', 'domain_module': 'core.domain.promoted.algebra_polynomial_division.polynomial_division_domain', 'entrypoint': 'build_polynomial_division_matrix', 'allowed_operations': ['evaluate_polynomial_statements', 'evaluate_polynomial_values', 'solve_polynomial_from_remainder_congruences', 'solve_remainder_from_conditions', 'solve_remainder_with_linear_part'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_RemainderTheorem'}), seed)
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
