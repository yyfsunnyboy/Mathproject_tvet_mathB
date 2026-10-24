from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "polynomial_inequality_parameters"
TEXTBOOK_EXAMPLE_ID = 12658
DEFAULT_COMPONENT_ID = "src_12658" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PolynomialInequalities"
FIXED_DOMAIN_KEY = "inequality.polynomial"
DOMAIN_OPERATION = "polynomial_inequality_parameters"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'inequality.polynomial', 'required_capabilities': ['polynomial_inequality_parameters'], 'domain_operation': 'polynomial_inequality_parameters', 'problem_type_id': 'polynomial_inequality_parameters', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'quad_from_solution', 'p': -3, 'roots': ['-3', '1/2'], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -27, 'roots': [-4, '-1/2'], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -12, 'roots': [1, 3], 'rel': '<=', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 10, 'roots': ['-3/2', -1], 'rel': '<=', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -6, 'roots': ['-3/2', '1/2'], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 21, 'roots': [3, 4], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -2, 'roots': ['-1/2', 1], 'rel': '<=', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 12, 'roots': [1, 3], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 15, 'roots': [-3, -2], 'rel': '>', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 3, 'roots': [-2, -1], 'rel': '>', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -4, 'roots': ['1/2', '3/2'], 'rel': '>=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 2, 'roots': [-3, 4], 'rel': '<', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 7, 'roots': [-4, '1/2'], 'rel': '>=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 2, 'roots': [-1, '1/2'], 'rel': '>', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 10, 'roots': [1, 4], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 3, 'roots': [-1, '3/2'], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 9, 'roots': ['-3/2', 3], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 20, 'roots': [2, 3], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 1, 'roots': [-1, '3/2'], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 27, 'roots': [-3, '-3/2'], 'rel': '<=', 'shape': 'between'}]}]}}, 'phase1_classification': {'fixed_domain_key': 'inequality.polynomial', 'required_capabilities': ['polynomial_inequality_parameters'], 'domain_operation': 'polynomial_inequality_parameters', 'problem_type_id': 'polynomial_inequality_parameters', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'quad_from_solution', 'p': -3, 'roots': ['-3', '1/2'], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -27, 'roots': [-4, '-1/2'], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -12, 'roots': [1, 3], 'rel': '<=', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 10, 'roots': ['-3/2', -1], 'rel': '<=', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -6, 'roots': ['-3/2', '1/2'], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 21, 'roots': [3, 4], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -2, 'roots': ['-1/2', 1], 'rel': '<=', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 12, 'roots': [1, 3], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 15, 'roots': [-3, -2], 'rel': '>', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 3, 'roots': [-2, -1], 'rel': '>', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -4, 'roots': ['1/2', '3/2'], 'rel': '>=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 2, 'roots': [-3, 4], 'rel': '<', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 7, 'roots': [-4, '1/2'], 'rel': '>=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 2, 'roots': [-1, '1/2'], 'rel': '>', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 10, 'roots': [1, 4], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 3, 'roots': [-1, '3/2'], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 9, 'roots': ['-3/2', 3], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 20, 'roots': [2, 3], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 1, 'roots': [-1, '3/2'], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 27, 'roots': [-3, '-3/2'], 'rel': '<=', 'shape': 'between'}]}]}}, 'problem_type_id': 'polynomial_inequality_parameters', 'required_capabilities': ['polynomial_inequality_parameters'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'kind': 'quad_from_solution', 'p': -3, 'roots': ['-3', '1/2'], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -27, 'roots': [-4, '-1/2'], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -12, 'roots': [1, 3], 'rel': '<=', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 10, 'roots': ['-3/2', -1], 'rel': '<=', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -6, 'roots': ['-3/2', '1/2'], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 21, 'roots': [3, 4], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -2, 'roots': ['-1/2', 1], 'rel': '<=', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 12, 'roots': [1, 3], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 15, 'roots': [-3, -2], 'rel': '>', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 3, 'roots': [-2, -1], 'rel': '>', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': -4, 'roots': ['1/2', '3/2'], 'rel': '>=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 2, 'roots': [-3, 4], 'rel': '<', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 7, 'roots': [-4, '1/2'], 'rel': '>=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 2, 'roots': [-1, '1/2'], 'rel': '>', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 10, 'roots': [1, 4], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 3, 'roots': [-1, '3/2'], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 9, 'roots': ['-3/2', 3], 'rel': '>', 'shape': 'between'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 20, 'roots': [2, 3], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 1, 'roots': [-1, '3/2'], 'rel': '<=', 'shape': 'outside'}]}, {'items': [{'kind': 'quad_from_solution', 'p': 27, 'roots': [-3, '-3/2'], 'rel': '<=', 'shape': 'between'}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_PolynomialInequalities', 'fixed_domain_key': 'inequality.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['polynomial_inequality_parameters'], 'matched_capabilities': ['polynomial_inequality_parameters'], 'selected_operation': 'polynomial_inequality_parameters', 'registry_revision': 'promoted-ce51ac7b8c4c', 'domain_module': 'core.domain.promoted.polynomial_inequality.polynomial_inequality_domain', 'entrypoint': 'build_polynomial_inequality_matrix', 'allowed_operations': ['polynomial_applications', 'polynomial_inequality_parameters', 'polynomial_statements', 'solve_polynomial_inequality'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_PolynomialInequalities'}), seed)
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
