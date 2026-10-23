from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "evaluate_polynomial_values"
TEXTBOOK_EXAMPLE_ID = 12541
DEFAULT_COMPONENT_ID = "src_12541" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RemainderTheorem"
FIXED_DOMAIN_KEY = "algebra.polynomial_division"
DOMAIN_OPERATION = "evaluate_polynomial_values"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['evaluate_polynomial_values'], 'domain_operation': 'evaluate_polynomial_values', 'problem_type_id': 'evaluate_polynomial_values', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'items': [{'kind': 'value', 'poly': [3, -22, -12, -33, 10, 5], 'x': 8}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -37, -10, -19, 10, 7], 'x': 9}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -25, -19, -26, 27, 3], 'x': -5}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [3, -24, -7, -20, 17, 7], 'x': 5}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -24, -15, -13, 24, 9], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [3, -32, -10, -44, 16, 5], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -27, -20, -32, 19, 6], 'x': 6}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [3, -13, -16, -37, 21, 6], 'x': 9}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -29, -17, -38, 14, 9], 'x': 8}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -15, -18, -28, 9, 3], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -19, -5, -46, 17, 8], 'x': 6}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -27, -20, -22, 10, 5], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [2, -12, -15, -45, 28, 3], 'x': 6}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -19, -11, -40, 29, 9], 'x': 5}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [2, -27, -7, -43, 21, 6], 'x': 9}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [3, -20, -9, -14, 5, 5], 'x': -5}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -30, -17, -14, 13, 8], 'x': 6}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [2, -38, -18, -16, 8, 6], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -38, -6, -23, 28, 4], 'x': 9}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -11, -16, -15, 21, 3], 'x': 5}], 'style': 'value'}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['evaluate_polynomial_values'], 'domain_operation': 'evaluate_polynomial_values', 'problem_type_id': 'evaluate_polynomial_values', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'items': [{'kind': 'value', 'poly': [3, -22, -12, -33, 10, 5], 'x': 8}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -37, -10, -19, 10, 7], 'x': 9}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -25, -19, -26, 27, 3], 'x': -5}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [3, -24, -7, -20, 17, 7], 'x': 5}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -24, -15, -13, 24, 9], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [3, -32, -10, -44, 16, 5], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -27, -20, -32, 19, 6], 'x': 6}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [3, -13, -16, -37, 21, 6], 'x': 9}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -29, -17, -38, 14, 9], 'x': 8}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -15, -18, -28, 9, 3], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -19, -5, -46, 17, 8], 'x': 6}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -27, -20, -22, 10, 5], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [2, -12, -15, -45, 28, 3], 'x': 6}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -19, -11, -40, 29, 9], 'x': 5}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [2, -27, -7, -43, 21, 6], 'x': 9}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [3, -20, -9, -14, 5, 5], 'x': -5}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -30, -17, -14, 13, 8], 'x': 6}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [2, -38, -18, -16, 8, 6], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -38, -6, -23, 28, 4], 'x': 9}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -11, -16, -15, 21, 3], 'x': 5}], 'style': 'value'}]}}, 'problem_type_id': 'evaluate_polynomial_values', 'required_capabilities': ['evaluate_polynomial_values'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'kind': 'value', 'poly': [3, -22, -12, -33, 10, 5], 'x': 8}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -37, -10, -19, 10, 7], 'x': 9}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -25, -19, -26, 27, 3], 'x': -5}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [3, -24, -7, -20, 17, 7], 'x': 5}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -24, -15, -13, 24, 9], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [3, -32, -10, -44, 16, 5], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -27, -20, -32, 19, 6], 'x': 6}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [3, -13, -16, -37, 21, 6], 'x': 9}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -29, -17, -38, 14, 9], 'x': 8}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -15, -18, -28, 9, 3], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -19, -5, -46, 17, 8], 'x': 6}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -27, -20, -22, 10, 5], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [2, -12, -15, -45, 28, 3], 'x': 6}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -19, -11, -40, 29, 9], 'x': 5}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [2, -27, -7, -43, 21, 6], 'x': 9}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [3, -20, -9, -14, 5, 5], 'x': -5}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -30, -17, -14, 13, 8], 'x': 6}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [2, -38, -18, -16, 8, 6], 'x': 7}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [5, -38, -6, -23, 28, 4], 'x': 9}], 'style': 'value'}, {'items': [{'kind': 'value', 'poly': [4, -11, -16, -15, 21, 3], 'x': 5}], 'style': 'value'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_RemainderTheorem', 'fixed_domain_key': 'algebra.polynomial_division', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['evaluate_polynomial_values'], 'matched_capabilities': ['evaluate_polynomial_values'], 'selected_operation': 'evaluate_polynomial_values', 'registry_revision': 'promoted-53d919cf7758', 'domain_module': 'core.domain.promoted.algebra_polynomial_division.polynomial_division_domain', 'entrypoint': 'build_polynomial_division_matrix', 'allowed_operations': ['evaluate_polynomial_statements', 'evaluate_polynomial_values', 'solve_polynomial_from_remainder_congruences', 'solve_remainder_from_conditions', 'solve_remainder_with_linear_part'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_RemainderTheorem'}), seed)
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
