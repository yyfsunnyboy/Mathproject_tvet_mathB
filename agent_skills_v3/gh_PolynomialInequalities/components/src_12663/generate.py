from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "inequality"
PROBLEM_TYPE_ID = "polynomial_applications"
TEXTBOOK_EXAMPLE_ID = 12663
DEFAULT_COMPONENT_ID = "src_12663" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PolynomialInequalities"
FIXED_DOMAIN_KEY = "inequality.polynomial"
DOMAIN_OPERATION = "polynomial_applications"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'inequality.polynomial', 'required_capabilities': ['polynomial_applications'], 'domain_operation': 'polynomial_applications', 'problem_type_id': 'polynomial_applications', 'presentation_mode': 'short_answer', 'answer_type': 'inequality', 'generation_constraints': {'variants': [{'items': [{'kind': 'path_around_plot', 'W': 10, 'L': 12, 'P0': 20, 'A0': 48}]}, {'items': [{'kind': 'path_around_plot', 'W': 9, 'L': 14, 'P0': 14, 'A0': 24}]}, {'items': [{'kind': 'path_around_plot', 'W': 16, 'L': 16, 'P0': 24, 'A0': 64}]}, {'items': [{'kind': 'path_around_plot', 'W': 8, 'L': 18, 'P0': 28, 'A0': 56}]}, {'items': [{'kind': 'path_around_plot', 'W': 10, 'L': 10, 'P0': 8, 'A0': 36}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 20, 'P0': 24, 'A0': 48}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 12, 'P0': 8, 'A0': 100}]}, {'items': [{'kind': 'path_around_plot', 'W': 11, 'L': 17, 'P0': 16, 'A0': 55}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 17, 'P0': 34, 'A0': 104}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 18, 'P0': 36, 'A0': 112}]}, {'items': [{'kind': 'path_around_plot', 'W': 16, 'L': 16, 'P0': 16, 'A0': 196}]}, {'items': [{'kind': 'path_around_plot', 'W': 16, 'L': 17, 'P0': 10, 'A0': 110}]}, {'items': [{'kind': 'path_around_plot', 'W': 8, 'L': 17, 'P0': 26, 'A0': 90}]}, {'items': [{'kind': 'path_around_plot', 'W': 15, 'L': 17, 'P0': 8, 'A0': 63}]}, {'items': [{'kind': 'path_around_plot', 'W': 14, 'L': 17, 'P0': 22, 'A0': 54}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 17, 'P0': 34, 'A0': 150}]}, {'items': [{'kind': 'path_around_plot', 'W': 14, 'L': 19, 'P0': 18, 'A0': 36}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 18, 'P0': 28, 'A0': 72}]}, {'items': [{'kind': 'path_around_plot', 'W': 8, 'L': 18, 'P0': 36, 'A0': 96}]}, {'items': [{'kind': 'path_around_plot', 'W': 13, 'L': 20, 'P0': 26, 'A0': 98}]}]}}, 'phase1_classification': {'fixed_domain_key': 'inequality.polynomial', 'required_capabilities': ['polynomial_applications'], 'domain_operation': 'polynomial_applications', 'problem_type_id': 'polynomial_applications', 'presentation_mode': 'short_answer', 'answer_type': 'inequality', 'generation_constraints': {'variants': [{'items': [{'kind': 'path_around_plot', 'W': 10, 'L': 12, 'P0': 20, 'A0': 48}]}, {'items': [{'kind': 'path_around_plot', 'W': 9, 'L': 14, 'P0': 14, 'A0': 24}]}, {'items': [{'kind': 'path_around_plot', 'W': 16, 'L': 16, 'P0': 24, 'A0': 64}]}, {'items': [{'kind': 'path_around_plot', 'W': 8, 'L': 18, 'P0': 28, 'A0': 56}]}, {'items': [{'kind': 'path_around_plot', 'W': 10, 'L': 10, 'P0': 8, 'A0': 36}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 20, 'P0': 24, 'A0': 48}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 12, 'P0': 8, 'A0': 100}]}, {'items': [{'kind': 'path_around_plot', 'W': 11, 'L': 17, 'P0': 16, 'A0': 55}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 17, 'P0': 34, 'A0': 104}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 18, 'P0': 36, 'A0': 112}]}, {'items': [{'kind': 'path_around_plot', 'W': 16, 'L': 16, 'P0': 16, 'A0': 196}]}, {'items': [{'kind': 'path_around_plot', 'W': 16, 'L': 17, 'P0': 10, 'A0': 110}]}, {'items': [{'kind': 'path_around_plot', 'W': 8, 'L': 17, 'P0': 26, 'A0': 90}]}, {'items': [{'kind': 'path_around_plot', 'W': 15, 'L': 17, 'P0': 8, 'A0': 63}]}, {'items': [{'kind': 'path_around_plot', 'W': 14, 'L': 17, 'P0': 22, 'A0': 54}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 17, 'P0': 34, 'A0': 150}]}, {'items': [{'kind': 'path_around_plot', 'W': 14, 'L': 19, 'P0': 18, 'A0': 36}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 18, 'P0': 28, 'A0': 72}]}, {'items': [{'kind': 'path_around_plot', 'W': 8, 'L': 18, 'P0': 36, 'A0': 96}]}, {'items': [{'kind': 'path_around_plot', 'W': 13, 'L': 20, 'P0': 26, 'A0': 98}]}]}}, 'problem_type_id': 'polynomial_applications', 'required_capabilities': ['polynomial_applications'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'kind': 'path_around_plot', 'W': 10, 'L': 12, 'P0': 20, 'A0': 48}]}, {'items': [{'kind': 'path_around_plot', 'W': 9, 'L': 14, 'P0': 14, 'A0': 24}]}, {'items': [{'kind': 'path_around_plot', 'W': 16, 'L': 16, 'P0': 24, 'A0': 64}]}, {'items': [{'kind': 'path_around_plot', 'W': 8, 'L': 18, 'P0': 28, 'A0': 56}]}, {'items': [{'kind': 'path_around_plot', 'W': 10, 'L': 10, 'P0': 8, 'A0': 36}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 20, 'P0': 24, 'A0': 48}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 12, 'P0': 8, 'A0': 100}]}, {'items': [{'kind': 'path_around_plot', 'W': 11, 'L': 17, 'P0': 16, 'A0': 55}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 17, 'P0': 34, 'A0': 104}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 18, 'P0': 36, 'A0': 112}]}, {'items': [{'kind': 'path_around_plot', 'W': 16, 'L': 16, 'P0': 16, 'A0': 196}]}, {'items': [{'kind': 'path_around_plot', 'W': 16, 'L': 17, 'P0': 10, 'A0': 110}]}, {'items': [{'kind': 'path_around_plot', 'W': 8, 'L': 17, 'P0': 26, 'A0': 90}]}, {'items': [{'kind': 'path_around_plot', 'W': 15, 'L': 17, 'P0': 8, 'A0': 63}]}, {'items': [{'kind': 'path_around_plot', 'W': 14, 'L': 17, 'P0': 22, 'A0': 54}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 17, 'P0': 34, 'A0': 150}]}, {'items': [{'kind': 'path_around_plot', 'W': 14, 'L': 19, 'P0': 18, 'A0': 36}]}, {'items': [{'kind': 'path_around_plot', 'W': 12, 'L': 18, 'P0': 28, 'A0': 72}]}, {'items': [{'kind': 'path_around_plot', 'W': 8, 'L': 18, 'P0': 36, 'A0': 96}]}, {'items': [{'kind': 'path_around_plot', 'W': 13, 'L': 20, 'P0': 26, 'A0': 98}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_PolynomialInequalities', 'fixed_domain_key': 'inequality.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['polynomial_applications'], 'matched_capabilities': ['polynomial_applications'], 'selected_operation': 'polynomial_applications', 'registry_revision': 'promoted-ce51ac7b8c4c', 'domain_module': 'core.domain.promoted.polynomial_inequality.polynomial_inequality_domain', 'entrypoint': 'build_polynomial_inequality_matrix', 'allowed_operations': ['polynomial_applications', 'polynomial_inequality_parameters', 'polynomial_statements', 'solve_polynomial_inequality'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_PolynomialInequalities'}), seed)
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
