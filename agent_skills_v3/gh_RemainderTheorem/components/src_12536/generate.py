from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "evaluate_polynomial_values"
TEXTBOOK_EXAMPLE_ID = 12536
DEFAULT_COMPONENT_ID = "src_12536" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['evaluate_polynomial_values'], 'domain_operation': 'evaluate_polynomial_values', 'problem_type_id': 'evaluate_polynomial_values', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'items': [{'kind': 'expression', 'poly': [1, -7, -58, 16, -465, 100], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -23, 20, -48, -51, -192], 'x': 13}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -60, -33, 15, 21, 286], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 27, -38, -5, -51, -117], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -57, -19, -42, -46, 153], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 33, -26, -51, 11, -6], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -39, 45, -27, 21, 85], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -44, -48, 27, -47, -152], 'x': 13}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -52, -39, -29, -15, 112], 'x': 20}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 11, -20, -6, 20, -40], 'x': 15}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 6, -33, 8, -57, 296], 'x': 11}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 44, -23, -50, -17, -68], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 17, 19, -28, -33, -173], 'x': 11}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -2, -43, 12, 56, 91], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 24, 40, 12, -34, -188], 'x': 13}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 32, 45, -49, 29, 168], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 11, 46, -28, -10, 289], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -39, 48, 14, -36, -142], 'x': 13}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 22, 42, -15, -39, 137], 'x': 11}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -46, -25, 8, -53, -214], 'x': 10}], 'style': 'expression'}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['evaluate_polynomial_values'], 'domain_operation': 'evaluate_polynomial_values', 'problem_type_id': 'evaluate_polynomial_values', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'items': [{'kind': 'expression', 'poly': [1, -7, -58, 16, -465, 100], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -23, 20, -48, -51, -192], 'x': 13}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -60, -33, 15, 21, 286], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 27, -38, -5, -51, -117], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -57, -19, -42, -46, 153], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 33, -26, -51, 11, -6], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -39, 45, -27, 21, 85], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -44, -48, 27, -47, -152], 'x': 13}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -52, -39, -29, -15, 112], 'x': 20}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 11, -20, -6, 20, -40], 'x': 15}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 6, -33, 8, -57, 296], 'x': 11}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 44, -23, -50, -17, -68], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 17, 19, -28, -33, -173], 'x': 11}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -2, -43, 12, 56, 91], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 24, 40, 12, -34, -188], 'x': 13}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 32, 45, -49, 29, 168], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 11, 46, -28, -10, 289], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -39, 48, 14, -36, -142], 'x': 13}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 22, 42, -15, -39, 137], 'x': 11}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -46, -25, 8, -53, -214], 'x': 10}], 'style': 'expression'}]}}, 'problem_type_id': 'evaluate_polynomial_values', 'required_capabilities': ['evaluate_polynomial_values'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'kind': 'expression', 'poly': [1, -7, -58, 16, -465, 100], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -23, 20, -48, -51, -192], 'x': 13}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -60, -33, 15, 21, 286], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 27, -38, -5, -51, -117], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -57, -19, -42, -46, 153], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 33, -26, -51, 11, -6], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -39, 45, -27, 21, 85], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -44, -48, 27, -47, -152], 'x': 13}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -52, -39, -29, -15, 112], 'x': 20}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 11, -20, -6, 20, -40], 'x': 15}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 6, -33, 8, -57, 296], 'x': 11}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 44, -23, -50, -17, -68], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 17, 19, -28, -33, -173], 'x': 11}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -2, -43, 12, 56, 91], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 24, 40, 12, -34, -188], 'x': 13}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 32, 45, -49, 29, 168], 'x': 12}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 11, 46, -28, -10, 289], 'x': 10}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -39, 48, 14, -36, -142], 'x': 13}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, 22, 42, -15, -39, 137], 'x': 11}], 'style': 'expression'}, {'items': [{'kind': 'expression', 'poly': [1, -46, -25, 8, -53, -214], 'x': 10}], 'style': 'expression'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_RemainderTheorem', 'fixed_domain_key': 'algebra.polynomial_division', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['evaluate_polynomial_values'], 'matched_capabilities': ['evaluate_polynomial_values'], 'selected_operation': 'evaluate_polynomial_values', 'registry_revision': 'promoted-53d919cf7758', 'domain_module': 'core.domain.promoted.algebra_polynomial_division.polynomial_division_domain', 'entrypoint': 'build_polynomial_division_matrix', 'allowed_operations': ['evaluate_polynomial_statements', 'evaluate_polynomial_values', 'solve_polynomial_from_remainder_congruences', 'solve_remainder_from_conditions', 'solve_remainder_with_linear_part'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_RemainderTheorem'}), seed)
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
