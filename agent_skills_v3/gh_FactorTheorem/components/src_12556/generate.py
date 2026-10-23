from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "evaluate_polynomial_statements"
TEXTBOOK_EXAMPLE_ID = 12556
DEFAULT_COMPONENT_ID = "src_12556" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_FactorTheorem"
FIXED_DOMAIN_KEY = "algebra.polynomial_division"
DOMAIN_OPERATION = "evaluate_polynomial_statements"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['evaluate_polynomial_statements'], 'domain_operation': 'evaluate_polynomial_statements', 'problem_type_id': 'evaluate_polynomial_statements', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-1, '1/2'], 'factors': [[1, 1], [2, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/3', '3/2'], 'factors': [[3, -1], [2, -3]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [2, -1], 'factors': [[1, -2], [1, -2]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-1, 1], 'factors': [[1, 1], [1, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-1, 1], 'factors': [[1, 1], [1, -6]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [2, 1], 'factors': [[1, -2], [1, -6]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/3', '1/2'], 'factors': [[3, -1], [3, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/3', '-1/2'], 'factors': [[3, -1], [2, 1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-3, '-1/2'], 'factors': [[1, 3], [2, -9]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/2', 3], 'factors': [[2, -1], [1, -8]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-2, '1/2'], 'factors': [[1, 2], [1, 2]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['3/2', '1/2'], 'factors': [[2, -3], [2, -11]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-2, -3], 'factors': [[1, 2], [1, 3]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-3, '3/2'], 'factors': [[1, 3], [2, -3]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/2', -3], 'factors': [[2, -1], [1, 3]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/3', 1], 'factors': [[3, -1], [1, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [1, '1/3'], 'factors': [[1, -1], [3, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [2, 3], 'factors': [[1, -2], [1, -2]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['3/2', 2], 'factors': [[2, -3], [1, -7]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-3, '-1/2'], 'factors': [[1, 3], [1, 3]]}]}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['evaluate_polynomial_statements'], 'domain_operation': 'evaluate_polynomial_statements', 'problem_type_id': 'evaluate_polynomial_statements', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-1, '1/2'], 'factors': [[1, 1], [2, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/3', '3/2'], 'factors': [[3, -1], [2, -3]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [2, -1], 'factors': [[1, -2], [1, -2]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-1, 1], 'factors': [[1, 1], [1, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-1, 1], 'factors': [[1, 1], [1, -6]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [2, 1], 'factors': [[1, -2], [1, -6]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/3', '1/2'], 'factors': [[3, -1], [3, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/3', '-1/2'], 'factors': [[3, -1], [2, 1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-3, '-1/2'], 'factors': [[1, 3], [2, -9]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/2', 3], 'factors': [[2, -1], [1, -8]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-2, '1/2'], 'factors': [[1, 2], [1, 2]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['3/2', '1/2'], 'factors': [[2, -3], [2, -11]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-2, -3], 'factors': [[1, 2], [1, 3]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-3, '3/2'], 'factors': [[1, 3], [2, -3]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/2', -3], 'factors': [[2, -1], [1, 3]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/3', 1], 'factors': [[3, -1], [1, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [1, '1/3'], 'factors': [[1, -1], [3, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [2, 3], 'factors': [[1, -2], [1, -2]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['3/2', 2], 'factors': [[2, -3], [1, -7]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-3, '-1/2'], 'factors': [[1, 3], [1, 3]]}]}]}}, 'problem_type_id': 'evaluate_polynomial_statements', 'required_capabilities': ['evaluate_polynomial_statements'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-1, '1/2'], 'factors': [[1, 1], [2, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/3', '3/2'], 'factors': [[3, -1], [2, -3]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [2, -1], 'factors': [[1, -2], [1, -2]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-1, 1], 'factors': [[1, 1], [1, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-1, 1], 'factors': [[1, 1], [1, -6]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [2, 1], 'factors': [[1, -2], [1, -6]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/3', '1/2'], 'factors': [[3, -1], [3, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/3', '-1/2'], 'factors': [[3, -1], [2, 1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-3, '-1/2'], 'factors': [[1, 3], [2, -9]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/2', 3], 'factors': [[2, -1], [1, -8]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-2, '1/2'], 'factors': [[1, 2], [1, 2]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['3/2', '1/2'], 'factors': [[2, -3], [2, -11]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-2, -3], 'factors': [[1, 2], [1, 3]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-3, '3/2'], 'factors': [[1, 3], [2, -3]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/2', -3], 'factors': [[2, -1], [1, 3]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['1/3', 1], 'factors': [[3, -1], [1, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [1, '1/3'], 'factors': [[1, -1], [3, -1]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [2, 3], 'factors': [[1, -2], [1, -2]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': ['3/2', 2], 'factors': [[2, -3], [1, -7]]}]}, {'subject': {'type': 'generic'}, 'mode': 'truth', 'statements': [{'kind': 'factor_product_from_zeros', 'zeros': [-3, '-1/2'], 'factors': [[1, 3], [1, 3]]}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_FactorTheorem', 'fixed_domain_key': 'algebra.polynomial_division', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['evaluate_polynomial_statements'], 'matched_capabilities': ['evaluate_polynomial_statements'], 'selected_operation': 'evaluate_polynomial_statements', 'registry_revision': 'promoted-53d919cf7758', 'domain_module': 'core.domain.promoted.algebra_polynomial_division.polynomial_division_domain', 'entrypoint': 'build_polynomial_division_matrix', 'allowed_operations': ['evaluate_polynomial_statements', 'interpolate_polynomials', 'select_linear_factors', 'solve_erased_cubic', 'solve_masked_synthetic_coefficient', 'solve_polynomial_parameters'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_FactorTheorem'}), seed)
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
