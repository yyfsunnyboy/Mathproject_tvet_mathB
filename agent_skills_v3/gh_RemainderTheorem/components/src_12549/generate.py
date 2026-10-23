from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "solve_remainder_with_linear_part"
TEXTBOOK_EXAMPLE_ID = 12549
DEFAULT_COMPONENT_ID = "src_12549" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RemainderTheorem"
FIXED_DOMAIN_KEY = "algebra.polynomial_division"
DOMAIN_OPERATION = "solve_remainder_with_linear_part"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['solve_remainder_with_linear_part'], 'domain_operation': 'solve_remainder_with_linear_part', 'problem_type_id': 'solve_remainder_with_linear_part', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'roots': [1, 2, 3], 'k': 3, 'first_value': -3, 'last_value': 7}, {'roots': [-1, 0, 1], 'k': 2, 'first_value': -7, 'last_value': 1}, {'roots': [-3, -1, 4], 'k': 2, 'first_value': -2, 'last_value': 82}, {'roots': [-3, 3, 4], 'k': -4, 'first_value': 0, 'last_value': -21}, {'roots': [-1, 0, 3], 'k': 4, 'first_value': -5, 'last_value': 55}, {'roots': [-3, 2, 4], 'k': 3, 'first_value': 10, 'last_value': 38}, {'roots': [-3, -1, 1], 'k': -4, 'first_value': -9, 'last_value': -37}, {'roots': [1, 2, 3], 'k': -4, 'first_value': 1, 'last_value': -13}, {'roots': [1, 2, 3], 'k': -2, 'first_value': -4, 'last_value': -4}, {'roots': [-3, -1, 4], 'k': -1, 'first_value': 7, 'last_value': -49}, {'roots': [0, 1, 2], 'k': -3, 'first_value': 2, 'last_value': 2}, {'roots': [1, 2, 3], 'k': -4, 'first_value': -4, 'last_value': -10}, {'roots': [-1, 0, 2], 'k': -3, 'first_value': 0, 'last_value': -21}, {'roots': [-3, -2, 0], 'k': -1, 'first_value': 0, 'last_value': -9}, {'roots': [0, 1, 3], 'k': 2, 'first_value': 3, 'last_value': 18}, {'roots': [-2, -1, 1], 'k': 3, 'first_value': -1, 'last_value': 26}, {'roots': [-1, 0, 1], 'k': 3, 'first_value': -2, 'last_value': 6}, {'roots': [0, 1, 2], 'k': 1, 'first_value': 3, 'last_value': -1}, {'roots': [-2, 2, 3], 'k': 2, 'first_value': -12, 'last_value': 13}, {'roots': [-2, -1, 3], 'k': -1, 'first_value': 0, 'last_value': -30}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['solve_remainder_with_linear_part'], 'domain_operation': 'solve_remainder_with_linear_part', 'problem_type_id': 'solve_remainder_with_linear_part', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'roots': [1, 2, 3], 'k': 3, 'first_value': -3, 'last_value': 7}, {'roots': [-1, 0, 1], 'k': 2, 'first_value': -7, 'last_value': 1}, {'roots': [-3, -1, 4], 'k': 2, 'first_value': -2, 'last_value': 82}, {'roots': [-3, 3, 4], 'k': -4, 'first_value': 0, 'last_value': -21}, {'roots': [-1, 0, 3], 'k': 4, 'first_value': -5, 'last_value': 55}, {'roots': [-3, 2, 4], 'k': 3, 'first_value': 10, 'last_value': 38}, {'roots': [-3, -1, 1], 'k': -4, 'first_value': -9, 'last_value': -37}, {'roots': [1, 2, 3], 'k': -4, 'first_value': 1, 'last_value': -13}, {'roots': [1, 2, 3], 'k': -2, 'first_value': -4, 'last_value': -4}, {'roots': [-3, -1, 4], 'k': -1, 'first_value': 7, 'last_value': -49}, {'roots': [0, 1, 2], 'k': -3, 'first_value': 2, 'last_value': 2}, {'roots': [1, 2, 3], 'k': -4, 'first_value': -4, 'last_value': -10}, {'roots': [-1, 0, 2], 'k': -3, 'first_value': 0, 'last_value': -21}, {'roots': [-3, -2, 0], 'k': -1, 'first_value': 0, 'last_value': -9}, {'roots': [0, 1, 3], 'k': 2, 'first_value': 3, 'last_value': 18}, {'roots': [-2, -1, 1], 'k': 3, 'first_value': -1, 'last_value': 26}, {'roots': [-1, 0, 1], 'k': 3, 'first_value': -2, 'last_value': 6}, {'roots': [0, 1, 2], 'k': 1, 'first_value': 3, 'last_value': -1}, {'roots': [-2, 2, 3], 'k': 2, 'first_value': -12, 'last_value': 13}, {'roots': [-2, -1, 3], 'k': -1, 'first_value': 0, 'last_value': -30}]}}, 'problem_type_id': 'solve_remainder_with_linear_part', 'required_capabilities': ['solve_remainder_with_linear_part'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'roots': [1, 2, 3], 'k': 3, 'first_value': -3, 'last_value': 7}, {'roots': [-1, 0, 1], 'k': 2, 'first_value': -7, 'last_value': 1}, {'roots': [-3, -1, 4], 'k': 2, 'first_value': -2, 'last_value': 82}, {'roots': [-3, 3, 4], 'k': -4, 'first_value': 0, 'last_value': -21}, {'roots': [-1, 0, 3], 'k': 4, 'first_value': -5, 'last_value': 55}, {'roots': [-3, 2, 4], 'k': 3, 'first_value': 10, 'last_value': 38}, {'roots': [-3, -1, 1], 'k': -4, 'first_value': -9, 'last_value': -37}, {'roots': [1, 2, 3], 'k': -4, 'first_value': 1, 'last_value': -13}, {'roots': [1, 2, 3], 'k': -2, 'first_value': -4, 'last_value': -4}, {'roots': [-3, -1, 4], 'k': -1, 'first_value': 7, 'last_value': -49}, {'roots': [0, 1, 2], 'k': -3, 'first_value': 2, 'last_value': 2}, {'roots': [1, 2, 3], 'k': -4, 'first_value': -4, 'last_value': -10}, {'roots': [-1, 0, 2], 'k': -3, 'first_value': 0, 'last_value': -21}, {'roots': [-3, -2, 0], 'k': -1, 'first_value': 0, 'last_value': -9}, {'roots': [0, 1, 3], 'k': 2, 'first_value': 3, 'last_value': 18}, {'roots': [-2, -1, 1], 'k': 3, 'first_value': -1, 'last_value': 26}, {'roots': [-1, 0, 1], 'k': 3, 'first_value': -2, 'last_value': 6}, {'roots': [0, 1, 2], 'k': 1, 'first_value': 3, 'last_value': -1}, {'roots': [-2, 2, 3], 'k': 2, 'first_value': -12, 'last_value': 13}, {'roots': [-2, -1, 3], 'k': -1, 'first_value': 0, 'last_value': -30}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_RemainderTheorem', 'fixed_domain_key': 'algebra.polynomial_division', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_remainder_with_linear_part'], 'matched_capabilities': ['solve_remainder_with_linear_part'], 'selected_operation': 'solve_remainder_with_linear_part', 'registry_revision': 'promoted-53d919cf7758', 'domain_module': 'core.domain.promoted.algebra_polynomial_division.polynomial_division_domain', 'entrypoint': 'build_polynomial_division_matrix', 'allowed_operations': ['evaluate_polynomial_statements', 'evaluate_polynomial_values', 'solve_polynomial_from_remainder_congruences', 'solve_remainder_from_conditions', 'solve_remainder_with_linear_part'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_RemainderTheorem'}), seed)
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
