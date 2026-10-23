from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "interpolate_polynomials"
TEXTBOOK_EXAMPLE_ID = 12554
DEFAULT_COMPONENT_ID = "src_12554" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_FactorTheorem"
FIXED_DOMAIN_KEY = "algebra.polynomial_division"
DOMAIN_OPERATION = "interpolate_polynomials"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['interpolate_polynomials'], 'domain_operation': 'interpolate_polynomials', 'problem_type_id': 'interpolate_polynomials', 'presentation_mode': 'short_answer', 'answer_type': 'expression', 'generation_constraints': {'variants': [{'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [3, 24]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [4, -60]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-2, 0], [-1, 0], [0, 0], [3, -60]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [6, 480]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [-2, -24]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [-1, -72]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [-3, -72]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-2, 0], [-1, 0], [0, 0], [-4, 48]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [4, 48]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-2, 0], [-1, 0], [0, 0], [1, 12]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [-2, -48]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [0, -6]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [-2, 180]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [6, 240]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [6, 360]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [3, -12]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [-4, 60]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [-4, -630]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [3, 96]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [-2, 18]]}], 'style': 'is_cubic', 'last': '且'}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.polynomial_division', 'required_capabilities': ['interpolate_polynomials'], 'domain_operation': 'interpolate_polynomials', 'problem_type_id': 'interpolate_polynomials', 'presentation_mode': 'short_answer', 'answer_type': 'expression', 'generation_constraints': {'variants': [{'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [3, 24]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [4, -60]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-2, 0], [-1, 0], [0, 0], [3, -60]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [6, 480]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [-2, -24]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [-1, -72]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [-3, -72]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-2, 0], [-1, 0], [0, 0], [-4, 48]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [4, 48]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-2, 0], [-1, 0], [0, 0], [1, 12]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [-2, -48]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [0, -6]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [-2, 180]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [6, 240]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [6, 360]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [3, -12]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [-4, 60]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [-4, -630]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [3, 96]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [-2, 18]]}], 'style': 'is_cubic', 'last': '且'}]}}, 'problem_type_id': 'interpolate_polynomials', 'required_capabilities': ['interpolate_polynomials'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [3, 24]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [4, -60]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-2, 0], [-1, 0], [0, 0], [3, -60]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [6, 480]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [-2, -24]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [-1, -72]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [-3, -72]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-2, 0], [-1, 0], [0, 0], [-4, 48]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [4, 48]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-2, 0], [-1, 0], [0, 0], [1, 12]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [-2, -48]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [0, -6]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [-2, 180]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [6, 240]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [6, 360]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[0, 0], [1, 0], [2, 0], [3, -12]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [-4, 60]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[1, 0], [2, 0], [3, 0], [-4, -630]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [3, 96]]}], 'style': 'is_cubic', 'last': '且'}, {'items': [{'degree': 3, 'points': [[-1, 0], [0, 0], [1, 0], [-2, 18]]}], 'style': 'is_cubic', 'last': '且'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_FactorTheorem', 'fixed_domain_key': 'algebra.polynomial_division', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['interpolate_polynomials'], 'matched_capabilities': ['interpolate_polynomials'], 'selected_operation': 'interpolate_polynomials', 'registry_revision': 'promoted-53d919cf7758', 'domain_module': 'core.domain.promoted.algebra_polynomial_division.polynomial_division_domain', 'entrypoint': 'build_polynomial_division_matrix', 'allowed_operations': ['evaluate_polynomial_statements', 'interpolate_polynomials', 'select_linear_factors', 'solve_erased_cubic', 'solve_masked_synthetic_coefficient', 'solve_polynomial_parameters'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_FactorTheorem'}), seed)
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
