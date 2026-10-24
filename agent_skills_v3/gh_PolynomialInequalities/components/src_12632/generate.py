from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "solve_polynomial_inequality"
TEXTBOOK_EXAMPLE_ID = 12632
DEFAULT_COMPONENT_ID = "src_12632" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PolynomialInequalities"
FIXED_DOMAIN_KEY = "inequality.polynomial"
DOMAIN_OPERATION = "solve_polynomial_inequality"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'inequality.polynomial', 'required_capabilities': ['solve_polynomial_inequality'], 'domain_operation': 'solve_polynomial_inequality', 'problem_type_id': 'solve_polynomial_inequality', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'left': {'poly': [1, -4, 3]}, 'rel': '<='}, {'left': {'poly': [-1, 1, 3]}, 'rel': '<'}]}, {'items': [{'left': {'poly': [3, 3, -60]}, 'rel': '<='}, {'left': {'poly': [-2, -5, -7]}, 'rel': '<='}]}, {'items': [{'left': {'poly': [-1, 0, 9]}, 'rel': '<'}, {'left': {'poly': [1, 0, 0]}, 'rel': '>=', 'right': {'poly': [-3, -2]}}]}, {'items': [{'left': {'poly': [2, 18, 40]}, 'rel': '<'}, {'left': {'poly': [1, 6, 5]}, 'rel': '<'}]}, {'items': [{'left': {'poly': [2, -4, -48]}, 'rel': '>'}, {'left': {'poly': [-2, -14, -20]}, 'rel': '>='}]}, {'items': [{'left': {'poly': [-1, -3, -2]}, 'rel': '>'}, {'left': {'poly': [2, 1, 5]}, 'rel': '<='}]}, {'items': [{'left': {'poly': [-2, -10, 0]}, 'rel': '<='}, {'left': {'poly': [1, 4, 6]}, 'rel': '>'}]}, {'items': [{'left': {'poly': [2, 18, 36]}, 'rel': '<='}, {'left': {'poly': [-1, 0, 0]}, 'rel': '>=', 'right': {'poly': [0, 0]}}]}, {'items': [{'left': {'poly': [3, 12, -36]}, 'rel': '<'}, {'left': {'poly': [1, 0, 0]}, 'rel': '>', 'right': {'poly': [4, -5]}}]}, {'items': [{'left': {'poly': [2, -6, -20]}, 'rel': '>='}, {'left': {'poly': [-2, 0, 8]}, 'rel': '<'}]}, {'items': [{'left': {'poly': [-2, -2, 40]}, 'rel': '<='}, {'left': {'poly': [-2, 0, 0]}, 'rel': '>=', 'right': {'poly': [0, -50]}}]}, {'items': [{'left': {'poly': [2, -22, 60]}, 'rel': '>='}, {'left': {'poly': [3, 18, 27]}, 'rel': '>'}]}, {'items': [{'left': {'poly': [2, -8, 6]}, 'rel': '<'}, {'left': {'poly': [1, 11, 30]}, 'rel': '<'}]}, {'items': [{'left': {'poly': [1, 2, -24]}, 'rel': '<='}, {'left': {'poly': [1, 0, 0]}, 'rel': '>=', 'right': {'poly': [8, -16]}}]}, {'items': [{'left': {'poly': [1, 2, 0]}, 'rel': '<'}, {'left': {'poly': [1, 0, 0]}, 'rel': '<', 'right': {'poly': [-10, -25]}}]}, {'items': [{'left': {'poly': [-1, -5, -6]}, 'rel': '>='}, {'left': {'poly': [2, 0, 0]}, 'rel': '>=', 'right': {'poly': [10, 12]}}]}, {'items': [{'left': {'poly': [1, -1, -2]}, 'rel': '>='}, {'left': {'poly': [-1, 0, 0]}, 'rel': '>', 'right': {'poly': [8, 16]}}]}, {'items': [{'left': {'poly': [1, 3, -10]}, 'rel': '>='}, {'left': {'poly': [1, 0, 0]}, 'rel': '<=', 'right': {'poly': [10, -25]}}]}, {'items': [{'left': {'poly': [1, -1, 0]}, 'rel': '<='}, {'left': {'poly': [-1, 10, -24]}, 'rel': '>='}]}, {'items': [{'left': {'poly': [3, 15, 18]}, 'rel': '>'}, {'left': {'poly': [3, 0, 0]}, 'rel': '<', 'right': {'poly': [3, 6]}}]}]}}, 'phase1_classification': {'fixed_domain_key': 'inequality.polynomial', 'required_capabilities': ['solve_polynomial_inequality'], 'domain_operation': 'solve_polynomial_inequality', 'problem_type_id': 'solve_polynomial_inequality', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'left': {'poly': [1, -4, 3]}, 'rel': '<='}, {'left': {'poly': [-1, 1, 3]}, 'rel': '<'}]}, {'items': [{'left': {'poly': [3, 3, -60]}, 'rel': '<='}, {'left': {'poly': [-2, -5, -7]}, 'rel': '<='}]}, {'items': [{'left': {'poly': [-1, 0, 9]}, 'rel': '<'}, {'left': {'poly': [1, 0, 0]}, 'rel': '>=', 'right': {'poly': [-3, -2]}}]}, {'items': [{'left': {'poly': [2, 18, 40]}, 'rel': '<'}, {'left': {'poly': [1, 6, 5]}, 'rel': '<'}]}, {'items': [{'left': {'poly': [2, -4, -48]}, 'rel': '>'}, {'left': {'poly': [-2, -14, -20]}, 'rel': '>='}]}, {'items': [{'left': {'poly': [-1, -3, -2]}, 'rel': '>'}, {'left': {'poly': [2, 1, 5]}, 'rel': '<='}]}, {'items': [{'left': {'poly': [-2, -10, 0]}, 'rel': '<='}, {'left': {'poly': [1, 4, 6]}, 'rel': '>'}]}, {'items': [{'left': {'poly': [2, 18, 36]}, 'rel': '<='}, {'left': {'poly': [-1, 0, 0]}, 'rel': '>=', 'right': {'poly': [0, 0]}}]}, {'items': [{'left': {'poly': [3, 12, -36]}, 'rel': '<'}, {'left': {'poly': [1, 0, 0]}, 'rel': '>', 'right': {'poly': [4, -5]}}]}, {'items': [{'left': {'poly': [2, -6, -20]}, 'rel': '>='}, {'left': {'poly': [-2, 0, 8]}, 'rel': '<'}]}, {'items': [{'left': {'poly': [-2, -2, 40]}, 'rel': '<='}, {'left': {'poly': [-2, 0, 0]}, 'rel': '>=', 'right': {'poly': [0, -50]}}]}, {'items': [{'left': {'poly': [2, -22, 60]}, 'rel': '>='}, {'left': {'poly': [3, 18, 27]}, 'rel': '>'}]}, {'items': [{'left': {'poly': [2, -8, 6]}, 'rel': '<'}, {'left': {'poly': [1, 11, 30]}, 'rel': '<'}]}, {'items': [{'left': {'poly': [1, 2, -24]}, 'rel': '<='}, {'left': {'poly': [1, 0, 0]}, 'rel': '>=', 'right': {'poly': [8, -16]}}]}, {'items': [{'left': {'poly': [1, 2, 0]}, 'rel': '<'}, {'left': {'poly': [1, 0, 0]}, 'rel': '<', 'right': {'poly': [-10, -25]}}]}, {'items': [{'left': {'poly': [-1, -5, -6]}, 'rel': '>='}, {'left': {'poly': [2, 0, 0]}, 'rel': '>=', 'right': {'poly': [10, 12]}}]}, {'items': [{'left': {'poly': [1, -1, -2]}, 'rel': '>='}, {'left': {'poly': [-1, 0, 0]}, 'rel': '>', 'right': {'poly': [8, 16]}}]}, {'items': [{'left': {'poly': [1, 3, -10]}, 'rel': '>='}, {'left': {'poly': [1, 0, 0]}, 'rel': '<=', 'right': {'poly': [10, -25]}}]}, {'items': [{'left': {'poly': [1, -1, 0]}, 'rel': '<='}, {'left': {'poly': [-1, 10, -24]}, 'rel': '>='}]}, {'items': [{'left': {'poly': [3, 15, 18]}, 'rel': '>'}, {'left': {'poly': [3, 0, 0]}, 'rel': '<', 'right': {'poly': [3, 6]}}]}]}}, 'problem_type_id': 'solve_polynomial_inequality', 'required_capabilities': ['solve_polynomial_inequality'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'left': {'poly': [1, -4, 3]}, 'rel': '<='}, {'left': {'poly': [-1, 1, 3]}, 'rel': '<'}]}, {'items': [{'left': {'poly': [3, 3, -60]}, 'rel': '<='}, {'left': {'poly': [-2, -5, -7]}, 'rel': '<='}]}, {'items': [{'left': {'poly': [-1, 0, 9]}, 'rel': '<'}, {'left': {'poly': [1, 0, 0]}, 'rel': '>=', 'right': {'poly': [-3, -2]}}]}, {'items': [{'left': {'poly': [2, 18, 40]}, 'rel': '<'}, {'left': {'poly': [1, 6, 5]}, 'rel': '<'}]}, {'items': [{'left': {'poly': [2, -4, -48]}, 'rel': '>'}, {'left': {'poly': [-2, -14, -20]}, 'rel': '>='}]}, {'items': [{'left': {'poly': [-1, -3, -2]}, 'rel': '>'}, {'left': {'poly': [2, 1, 5]}, 'rel': '<='}]}, {'items': [{'left': {'poly': [-2, -10, 0]}, 'rel': '<='}, {'left': {'poly': [1, 4, 6]}, 'rel': '>'}]}, {'items': [{'left': {'poly': [2, 18, 36]}, 'rel': '<='}, {'left': {'poly': [-1, 0, 0]}, 'rel': '>=', 'right': {'poly': [0, 0]}}]}, {'items': [{'left': {'poly': [3, 12, -36]}, 'rel': '<'}, {'left': {'poly': [1, 0, 0]}, 'rel': '>', 'right': {'poly': [4, -5]}}]}, {'items': [{'left': {'poly': [2, -6, -20]}, 'rel': '>='}, {'left': {'poly': [-2, 0, 8]}, 'rel': '<'}]}, {'items': [{'left': {'poly': [-2, -2, 40]}, 'rel': '<='}, {'left': {'poly': [-2, 0, 0]}, 'rel': '>=', 'right': {'poly': [0, -50]}}]}, {'items': [{'left': {'poly': [2, -22, 60]}, 'rel': '>='}, {'left': {'poly': [3, 18, 27]}, 'rel': '>'}]}, {'items': [{'left': {'poly': [2, -8, 6]}, 'rel': '<'}, {'left': {'poly': [1, 11, 30]}, 'rel': '<'}]}, {'items': [{'left': {'poly': [1, 2, -24]}, 'rel': '<='}, {'left': {'poly': [1, 0, 0]}, 'rel': '>=', 'right': {'poly': [8, -16]}}]}, {'items': [{'left': {'poly': [1, 2, 0]}, 'rel': '<'}, {'left': {'poly': [1, 0, 0]}, 'rel': '<', 'right': {'poly': [-10, -25]}}]}, {'items': [{'left': {'poly': [-1, -5, -6]}, 'rel': '>='}, {'left': {'poly': [2, 0, 0]}, 'rel': '>=', 'right': {'poly': [10, 12]}}]}, {'items': [{'left': {'poly': [1, -1, -2]}, 'rel': '>='}, {'left': {'poly': [-1, 0, 0]}, 'rel': '>', 'right': {'poly': [8, 16]}}]}, {'items': [{'left': {'poly': [1, 3, -10]}, 'rel': '>='}, {'left': {'poly': [1, 0, 0]}, 'rel': '<=', 'right': {'poly': [10, -25]}}]}, {'items': [{'left': {'poly': [1, -1, 0]}, 'rel': '<='}, {'left': {'poly': [-1, 10, -24]}, 'rel': '>='}]}, {'items': [{'left': {'poly': [3, 15, 18]}, 'rel': '>'}, {'left': {'poly': [3, 0, 0]}, 'rel': '<', 'right': {'poly': [3, 6]}}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_PolynomialInequalities', 'fixed_domain_key': 'inequality.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_polynomial_inequality'], 'matched_capabilities': ['solve_polynomial_inequality'], 'selected_operation': 'solve_polynomial_inequality', 'registry_revision': 'promoted-ce51ac7b8c4c', 'domain_module': 'core.domain.promoted.polynomial_inequality.polynomial_inequality_domain', 'entrypoint': 'build_polynomial_inequality_matrix', 'allowed_operations': ['polynomial_applications', 'polynomial_inequality_parameters', 'polynomial_statements', 'solve_polynomial_inequality'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_PolynomialInequalities'}), seed)
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
