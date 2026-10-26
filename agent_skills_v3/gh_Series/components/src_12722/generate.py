from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "arithmetic_series_items"
TEXTBOOK_EXAMPLE_ID = 12722
DEFAULT_COMPONENT_ID = "src_12722" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Series"
FIXED_DOMAIN_KEY = "sequence.series_sums"
DOMAIN_OPERATION = "arithmetic_series_items"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'sequence.series_sums', 'required_capabilities': ['arithmetic_series_items'], 'domain_operation': 'arithmetic_series_items', 'problem_type_id': 'arithmetic_series_items', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'd_from_sum', 'a1': 36, 'n': 9, 'S': 144}, {'kind': 'sum_terms', 'first': -3, 'd': 2, 'last': 23, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 30, 'n': 9, 'S': 378}, {'kind': 'sum_terms', 'first': 2, 'd': 2, 'last': 14, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 1, 'n': 7, 'S': 70}, {'kind': 'sum_terms', 'first': -7, 'd': -4, 'last': -55, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 29, 'n': 11, 'S': 484}, {'kind': 'sum_terms', 'first': 2, 'd': -4, 'last': -50, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 21, 'n': 11, 'S': 11}, {'kind': 'sum_terms', 'first': -5, 'd': 2, 'last': 7, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 6, 'n': 9, 'S': -18}, {'kind': 'sum_terms', 'first': 8, 'd': 3, 'last': 26, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 9, 'n': 5, 'S': 85}, {'kind': 'sum_terms', 'first': 10, 'd': -4, 'last': -10, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 25, 'n': 11, 'S': 0}, {'kind': 'sum_terms', 'first': 11, 'd': 5, 'last': 46, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 26, 'n': 8, 'S': 124}, {'kind': 'sum_terms', 'first': 3, 'd': -3, 'last': -36, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 23, 'n': 10, 'S': 365}, {'kind': 'sum_terms', 'first': -8, 'd': 2, 'last': 2, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 27, 'n': 6, 'S': 252}, {'kind': 'sum_terms', 'first': -6, 'd': 2, 'last': 8, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 5, 'n': 8, 'S': 124}, {'kind': 'sum_terms', 'first': 0, 'd': 2, 'last': 12, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': -9, 'n': 12, 'S': 288}, {'kind': 'sum_terms', 'first': 0, 'd': -3, 'last': -24, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': -2, 'n': 11, 'S': -297}, {'kind': 'sum_terms', 'first': -5, 'd': 3, 'last': 31, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 15, 'n': 11, 'S': 385}, {'kind': 'sum_terms', 'first': 1, 'd': -4, 'last': -43, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 23, 'n': 9, 'S': 423}, {'kind': 'sum_terms', 'first': -3, 'd': 2, 'last': 13, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 18, 'n': 10, 'S': -45}, {'kind': 'sum_terms', 'first': 8, 'd': -3, 'last': -25, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 25, 'n': 12, 'S': 630}, {'kind': 'sum_terms', 'first': 6, 'd': -4, 'last': -38, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 8, 'n': 9, 'S': 0}, {'kind': 'sum_terms', 'first': 12, 'd': 4, 'last': 40, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 29, 'n': 6, 'S': 249}, {'kind': 'sum_terms', 'first': 11, 'd': 2, 'last': 27, 'show': 3}]}]}}, 'phase1_classification': {'fixed_domain_key': 'sequence.series_sums', 'required_capabilities': ['arithmetic_series_items'], 'domain_operation': 'arithmetic_series_items', 'problem_type_id': 'arithmetic_series_items', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'd_from_sum', 'a1': 36, 'n': 9, 'S': 144}, {'kind': 'sum_terms', 'first': -3, 'd': 2, 'last': 23, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 30, 'n': 9, 'S': 378}, {'kind': 'sum_terms', 'first': 2, 'd': 2, 'last': 14, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 1, 'n': 7, 'S': 70}, {'kind': 'sum_terms', 'first': -7, 'd': -4, 'last': -55, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 29, 'n': 11, 'S': 484}, {'kind': 'sum_terms', 'first': 2, 'd': -4, 'last': -50, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 21, 'n': 11, 'S': 11}, {'kind': 'sum_terms', 'first': -5, 'd': 2, 'last': 7, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 6, 'n': 9, 'S': -18}, {'kind': 'sum_terms', 'first': 8, 'd': 3, 'last': 26, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 9, 'n': 5, 'S': 85}, {'kind': 'sum_terms', 'first': 10, 'd': -4, 'last': -10, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 25, 'n': 11, 'S': 0}, {'kind': 'sum_terms', 'first': 11, 'd': 5, 'last': 46, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 26, 'n': 8, 'S': 124}, {'kind': 'sum_terms', 'first': 3, 'd': -3, 'last': -36, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 23, 'n': 10, 'S': 365}, {'kind': 'sum_terms', 'first': -8, 'd': 2, 'last': 2, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 27, 'n': 6, 'S': 252}, {'kind': 'sum_terms', 'first': -6, 'd': 2, 'last': 8, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 5, 'n': 8, 'S': 124}, {'kind': 'sum_terms', 'first': 0, 'd': 2, 'last': 12, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': -9, 'n': 12, 'S': 288}, {'kind': 'sum_terms', 'first': 0, 'd': -3, 'last': -24, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': -2, 'n': 11, 'S': -297}, {'kind': 'sum_terms', 'first': -5, 'd': 3, 'last': 31, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 15, 'n': 11, 'S': 385}, {'kind': 'sum_terms', 'first': 1, 'd': -4, 'last': -43, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 23, 'n': 9, 'S': 423}, {'kind': 'sum_terms', 'first': -3, 'd': 2, 'last': 13, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 18, 'n': 10, 'S': -45}, {'kind': 'sum_terms', 'first': 8, 'd': -3, 'last': -25, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 25, 'n': 12, 'S': 630}, {'kind': 'sum_terms', 'first': 6, 'd': -4, 'last': -38, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 8, 'n': 9, 'S': 0}, {'kind': 'sum_terms', 'first': 12, 'd': 4, 'last': 40, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 29, 'n': 6, 'S': 249}, {'kind': 'sum_terms', 'first': 11, 'd': 2, 'last': 27, 'show': 3}]}]}}, 'problem_type_id': 'arithmetic_series_items', 'required_capabilities': ['arithmetic_series_items'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'kind': 'd_from_sum', 'a1': 36, 'n': 9, 'S': 144}, {'kind': 'sum_terms', 'first': -3, 'd': 2, 'last': 23, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 30, 'n': 9, 'S': 378}, {'kind': 'sum_terms', 'first': 2, 'd': 2, 'last': 14, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 1, 'n': 7, 'S': 70}, {'kind': 'sum_terms', 'first': -7, 'd': -4, 'last': -55, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 29, 'n': 11, 'S': 484}, {'kind': 'sum_terms', 'first': 2, 'd': -4, 'last': -50, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 21, 'n': 11, 'S': 11}, {'kind': 'sum_terms', 'first': -5, 'd': 2, 'last': 7, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 6, 'n': 9, 'S': -18}, {'kind': 'sum_terms', 'first': 8, 'd': 3, 'last': 26, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 9, 'n': 5, 'S': 85}, {'kind': 'sum_terms', 'first': 10, 'd': -4, 'last': -10, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 25, 'n': 11, 'S': 0}, {'kind': 'sum_terms', 'first': 11, 'd': 5, 'last': 46, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 26, 'n': 8, 'S': 124}, {'kind': 'sum_terms', 'first': 3, 'd': -3, 'last': -36, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 23, 'n': 10, 'S': 365}, {'kind': 'sum_terms', 'first': -8, 'd': 2, 'last': 2, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 27, 'n': 6, 'S': 252}, {'kind': 'sum_terms', 'first': -6, 'd': 2, 'last': 8, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 5, 'n': 8, 'S': 124}, {'kind': 'sum_terms', 'first': 0, 'd': 2, 'last': 12, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': -9, 'n': 12, 'S': 288}, {'kind': 'sum_terms', 'first': 0, 'd': -3, 'last': -24, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': -2, 'n': 11, 'S': -297}, {'kind': 'sum_terms', 'first': -5, 'd': 3, 'last': 31, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 15, 'n': 11, 'S': 385}, {'kind': 'sum_terms', 'first': 1, 'd': -4, 'last': -43, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 23, 'n': 9, 'S': 423}, {'kind': 'sum_terms', 'first': -3, 'd': 2, 'last': 13, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 18, 'n': 10, 'S': -45}, {'kind': 'sum_terms', 'first': 8, 'd': -3, 'last': -25, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 25, 'n': 12, 'S': 630}, {'kind': 'sum_terms', 'first': 6, 'd': -4, 'last': -38, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 8, 'n': 9, 'S': 0}, {'kind': 'sum_terms', 'first': 12, 'd': 4, 'last': 40, 'show': 3}]}, {'items': [{'kind': 'd_from_sum', 'a1': 29, 'n': 6, 'S': 249}, {'kind': 'sum_terms', 'first': 11, 'd': 2, 'last': 27, 'show': 3}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Series', 'fixed_domain_key': 'sequence.series_sums', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['arithmetic_series_items'], 'matched_capabilities': ['arithmetic_series_items'], 'selected_operation': 'arithmetic_series_items', 'registry_revision': 'promoted-b3fc93095b76', 'domain_module': 'core.domain.promoted.series_summation.series_summation_domain', 'entrypoint': 'build_series_summation_matrix', 'allowed_operations': ['arithmetic_series_items', 'arithmetic_series_relation', 'fish_rows', 'geometric_series_items', 'geometric_series_relation', 'partial_sum_terms', 'series_statements'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Series'}), seed)
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
