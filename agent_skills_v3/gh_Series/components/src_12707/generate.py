from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "arithmetic_series_items"
TEXTBOOK_EXAMPLE_ID = 12707
DEFAULT_COMPONENT_ID = "src_12707" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'sequence.series_sums', 'required_capabilities': ['arithmetic_series_items'], 'domain_operation': 'arithmetic_series_items', 'problem_type_id': 'arithmetic_series_items', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'd_from_sum', 'a1': 24, 'n': 7, 'S': 105}, {'kind': 'sum_terms', 'first': 3, 'd': 4, 'last': 47, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 33, 'n': 8, 'S': 432}, {'kind': 'sum_terms', 'first': -1, 'd': 2, 'last': 11, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 30, 'n': 9, 'S': 162}, {'kind': 'sum_terms', 'first': -7, 'd': -4, 'last': -35, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 19, 'n': 9, 'S': -9}, {'kind': 'sum_terms', 'first': 12, 'd': 2, 'last': 28, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 29, 'n': 5, 'S': 175}, {'kind': 'sum_terms', 'first': 4, 'd': 2, 'last': 18, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 9, 'n': 6, 'S': 9}, {'kind': 'sum_terms', 'first': -3, 'd': 2, 'last': 11, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 26, 'n': 10, 'S': 125}, {'kind': 'sum_terms', 'first': -4, 'd': -4, 'last': -40, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 40, 'n': 8, 'S': 460}, {'kind': 'sum_terms', 'first': 12, 'd': 3, 'last': 39, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 5, 'n': 11, 'S': 385}, {'kind': 'sum_terms', 'first': -1, 'd': -3, 'last': -40, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 12, 'n': 12, 'S': -186}, {'kind': 'sum_terms', 'first': 8, 'd': 3, 'last': 29, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 36, 'n': 12, 'S': 234}, {'kind': 'sum_terms', 'first': 11, 'd': 5, 'last': 56, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 17, 'n': 6, 'S': 147}, {'kind': 'sum_terms', 'first': -3, 'd': 3, 'last': 12, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 31, 'n': 9, 'S': 171}, {'kind': 'sum_terms', 'first': -7, 'd': -3, 'last': -37, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': -4, 'n': 8, 'S': 108}, {'kind': 'sum_terms', 'first': -4, 'd': 3, 'last': 26, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 17, 'n': 6, 'S': 57}, {'kind': 'sum_terms', 'first': 2, 'd': 4, 'last': 22, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 1, 'n': 8, 'S': 64}, {'kind': 'sum_terms', 'first': -1, 'd': 2, 'last': 17, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 15, 'n': 5, 'S': 25}, {'kind': 'sum_terms', 'first': 4, 'd': 2, 'last': 22, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 19, 'n': 12, 'S': 96}, {'kind': 'sum_terms', 'first': 8, 'd': -4, 'last': -40, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 30, 'n': 5, 'S': 190}, {'kind': 'sum_terms', 'first': 2, 'd': 3, 'last': 38, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 4, 'n': 11, 'S': 209}, {'kind': 'sum_terms', 'first': 11, 'd': -4, 'last': -17, 'show': 2}]}]}}, 'phase1_classification': {'fixed_domain_key': 'sequence.series_sums', 'required_capabilities': ['arithmetic_series_items'], 'domain_operation': 'arithmetic_series_items', 'problem_type_id': 'arithmetic_series_items', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'd_from_sum', 'a1': 24, 'n': 7, 'S': 105}, {'kind': 'sum_terms', 'first': 3, 'd': 4, 'last': 47, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 33, 'n': 8, 'S': 432}, {'kind': 'sum_terms', 'first': -1, 'd': 2, 'last': 11, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 30, 'n': 9, 'S': 162}, {'kind': 'sum_terms', 'first': -7, 'd': -4, 'last': -35, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 19, 'n': 9, 'S': -9}, {'kind': 'sum_terms', 'first': 12, 'd': 2, 'last': 28, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 29, 'n': 5, 'S': 175}, {'kind': 'sum_terms', 'first': 4, 'd': 2, 'last': 18, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 9, 'n': 6, 'S': 9}, {'kind': 'sum_terms', 'first': -3, 'd': 2, 'last': 11, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 26, 'n': 10, 'S': 125}, {'kind': 'sum_terms', 'first': -4, 'd': -4, 'last': -40, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 40, 'n': 8, 'S': 460}, {'kind': 'sum_terms', 'first': 12, 'd': 3, 'last': 39, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 5, 'n': 11, 'S': 385}, {'kind': 'sum_terms', 'first': -1, 'd': -3, 'last': -40, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 12, 'n': 12, 'S': -186}, {'kind': 'sum_terms', 'first': 8, 'd': 3, 'last': 29, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 36, 'n': 12, 'S': 234}, {'kind': 'sum_terms', 'first': 11, 'd': 5, 'last': 56, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 17, 'n': 6, 'S': 147}, {'kind': 'sum_terms', 'first': -3, 'd': 3, 'last': 12, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 31, 'n': 9, 'S': 171}, {'kind': 'sum_terms', 'first': -7, 'd': -3, 'last': -37, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': -4, 'n': 8, 'S': 108}, {'kind': 'sum_terms', 'first': -4, 'd': 3, 'last': 26, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 17, 'n': 6, 'S': 57}, {'kind': 'sum_terms', 'first': 2, 'd': 4, 'last': 22, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 1, 'n': 8, 'S': 64}, {'kind': 'sum_terms', 'first': -1, 'd': 2, 'last': 17, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 15, 'n': 5, 'S': 25}, {'kind': 'sum_terms', 'first': 4, 'd': 2, 'last': 22, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 19, 'n': 12, 'S': 96}, {'kind': 'sum_terms', 'first': 8, 'd': -4, 'last': -40, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 30, 'n': 5, 'S': 190}, {'kind': 'sum_terms', 'first': 2, 'd': 3, 'last': 38, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 4, 'n': 11, 'S': 209}, {'kind': 'sum_terms', 'first': 11, 'd': -4, 'last': -17, 'show': 2}]}]}}, 'problem_type_id': 'arithmetic_series_items', 'required_capabilities': ['arithmetic_series_items'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'kind': 'd_from_sum', 'a1': 24, 'n': 7, 'S': 105}, {'kind': 'sum_terms', 'first': 3, 'd': 4, 'last': 47, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 33, 'n': 8, 'S': 432}, {'kind': 'sum_terms', 'first': -1, 'd': 2, 'last': 11, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 30, 'n': 9, 'S': 162}, {'kind': 'sum_terms', 'first': -7, 'd': -4, 'last': -35, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 19, 'n': 9, 'S': -9}, {'kind': 'sum_terms', 'first': 12, 'd': 2, 'last': 28, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 29, 'n': 5, 'S': 175}, {'kind': 'sum_terms', 'first': 4, 'd': 2, 'last': 18, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 9, 'n': 6, 'S': 9}, {'kind': 'sum_terms', 'first': -3, 'd': 2, 'last': 11, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 26, 'n': 10, 'S': 125}, {'kind': 'sum_terms', 'first': -4, 'd': -4, 'last': -40, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 40, 'n': 8, 'S': 460}, {'kind': 'sum_terms', 'first': 12, 'd': 3, 'last': 39, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 5, 'n': 11, 'S': 385}, {'kind': 'sum_terms', 'first': -1, 'd': -3, 'last': -40, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 12, 'n': 12, 'S': -186}, {'kind': 'sum_terms', 'first': 8, 'd': 3, 'last': 29, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 36, 'n': 12, 'S': 234}, {'kind': 'sum_terms', 'first': 11, 'd': 5, 'last': 56, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 17, 'n': 6, 'S': 147}, {'kind': 'sum_terms', 'first': -3, 'd': 3, 'last': 12, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 31, 'n': 9, 'S': 171}, {'kind': 'sum_terms', 'first': -7, 'd': -3, 'last': -37, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': -4, 'n': 8, 'S': 108}, {'kind': 'sum_terms', 'first': -4, 'd': 3, 'last': 26, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 17, 'n': 6, 'S': 57}, {'kind': 'sum_terms', 'first': 2, 'd': 4, 'last': 22, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 1, 'n': 8, 'S': 64}, {'kind': 'sum_terms', 'first': -1, 'd': 2, 'last': 17, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 15, 'n': 5, 'S': 25}, {'kind': 'sum_terms', 'first': 4, 'd': 2, 'last': 22, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 19, 'n': 12, 'S': 96}, {'kind': 'sum_terms', 'first': 8, 'd': -4, 'last': -40, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 30, 'n': 5, 'S': 190}, {'kind': 'sum_terms', 'first': 2, 'd': 3, 'last': 38, 'show': 2}]}, {'items': [{'kind': 'd_from_sum', 'a1': 4, 'n': 11, 'S': 209}, {'kind': 'sum_terms', 'first': 11, 'd': -4, 'last': -17, 'show': 2}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Series', 'fixed_domain_key': 'sequence.series_sums', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['arithmetic_series_items'], 'matched_capabilities': ['arithmetic_series_items'], 'selected_operation': 'arithmetic_series_items', 'registry_revision': 'promoted-b3fc93095b76', 'domain_module': 'core.domain.promoted.series_summation.series_summation_domain', 'entrypoint': 'build_series_summation_matrix', 'allowed_operations': ['arithmetic_series_items', 'arithmetic_series_relation', 'fish_rows', 'geometric_series_items', 'geometric_series_relation', 'partial_sum_terms', 'series_statements'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Series'}), seed)
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
