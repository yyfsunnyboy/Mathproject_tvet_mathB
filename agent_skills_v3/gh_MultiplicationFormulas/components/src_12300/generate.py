from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "evaluate_reciprocal_power_expressions"
TEXTBOOK_EXAMPLE_ID = 12300
DEFAULT_COMPONENT_ID = "src_12300" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MultiplicationFormulas"
FIXED_DOMAIN_KEY = "algebra.multiplication_formulas"
DOMAIN_OPERATION = "evaluate_reciprocal_power_expressions"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.multiplication_formulas', 'required_capabilities': ['multiplication_formulas'], 'domain_operation': 'evaluate_reciprocal_power_expressions', 'problem_type_id': 'evaluate_reciprocal_power_expressions', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'base': {'kind': 'radical', 'rational': 2, 'radical': -1, 'radicand': 3}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 8, 'radical': -3, 'radicand': 7}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 11, 'radical': -2, 'radicand': 30}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 5, 'radical': 2, 'radicand': 6}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 3, 'radical': 2, 'radicand': 2}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 10, 'radical': -3, 'radicand': 11}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 6, 'radical': -1, 'radicand': 35}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 11, 'radical': 2, 'radicand': 30}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 2, 'radical': 1, 'radicand': 3}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 4, 'radical': -1, 'radicand': 15}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 7, 'radical': 4, 'radicand': 3}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 6, 'radical': 1, 'radicand': 35}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 4, 'radical': 1, 'radicand': 15}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 9, 'radical': 4, 'radicand': 5}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 8, 'radical': 3, 'radicand': 7}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 3, 'radical': -2, 'radicand': 2}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 10, 'radical': 3, 'radicand': 11}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 7, 'radical': -4, 'radicand': 3}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 5, 'radical': -2, 'radicand': 6}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 9, 'radical': -4, 'radicand': 5}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.multiplication_formulas', 'required_capabilities': ['multiplication_formulas'], 'domain_operation': 'evaluate_reciprocal_power_expressions', 'problem_type_id': 'evaluate_reciprocal_power_expressions', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'base': {'kind': 'radical', 'rational': 2, 'radical': -1, 'radicand': 3}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 8, 'radical': -3, 'radicand': 7}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 11, 'radical': -2, 'radicand': 30}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 5, 'radical': 2, 'radicand': 6}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 3, 'radical': 2, 'radicand': 2}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 10, 'radical': -3, 'radicand': 11}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 6, 'radical': -1, 'radicand': 35}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 11, 'radical': 2, 'radicand': 30}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 2, 'radical': 1, 'radicand': 3}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 4, 'radical': -1, 'radicand': 15}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 7, 'radical': 4, 'radicand': 3}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 6, 'radical': 1, 'radicand': 35}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 4, 'radical': 1, 'radicand': 15}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 9, 'radical': 4, 'radicand': 5}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 8, 'radical': 3, 'radicand': 7}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 3, 'radical': -2, 'radicand': 2}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 10, 'radical': 3, 'radicand': 11}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 7, 'radical': -4, 'radicand': 3}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 5, 'radical': -2, 'radicand': 6}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 9, 'radical': -4, 'radicand': 5}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}]}}, 'problem_type_id': 'evaluate_reciprocal_power_expressions', 'required_capabilities': ['multiplication_formulas'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'base': {'kind': 'radical', 'rational': 2, 'radical': -1, 'radicand': 3}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 8, 'radical': -3, 'radicand': 7}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 11, 'radical': -2, 'radicand': 30}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 5, 'radical': 2, 'radicand': 6}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 3, 'radical': 2, 'radicand': 2}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 10, 'radical': -3, 'radicand': 11}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 6, 'radical': -1, 'radicand': 35}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 11, 'radical': 2, 'radicand': 30}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 2, 'radical': 1, 'radicand': 3}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 4, 'radical': -1, 'radicand': 15}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 7, 'radical': 4, 'radicand': 3}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 6, 'radical': 1, 'radicand': 35}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 4, 'radical': 1, 'radicand': 15}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 9, 'radical': 4, 'radicand': 5}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 8, 'radical': 3, 'radicand': 7}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 3, 'radical': -2, 'radicand': 2}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 10, 'radical': 3, 'radicand': 11}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 7, 'radical': -4, 'radicand': 3}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 5, 'radical': -2, 'radicand': 6}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}, {'base': {'kind': 'radical', 'rational': 9, 'radical': -4, 'radicand': 5}, 'targets': [{'power': 1, 'sign': 1}, {'power': 2, 'sign': 1}, {'power': 3, 'sign': 1}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MultiplicationFormulas', 'fixed_domain_key': 'algebra.multiplication_formulas', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': [], 'matched_capabilities': [], 'selected_operation': 'evaluate_reciprocal_power_expressions', 'registry_revision': 'promoted-39c0ccae9af0', 'domain_module': 'core.domain.promoted.algebra_multiplication_formulas.multiplication_formulas_domain', 'entrypoint': 'build_multiplication_formulas_matrix', 'allowed_operations': ['expand_polynomial_expressions', 'factor_by_cube_formulas', 'evaluate_reciprocal_power_expressions', 'simplify_radical_expressions', 'solve_rational_unknowns_from_squared_radical_identity', 'evaluate_product_under_power_relation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MultiplicationFormulas'}), seed)
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
