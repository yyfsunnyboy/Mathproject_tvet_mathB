from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "arithmetic_series_relation"
TEXTBOOK_EXAMPLE_ID = 12708
DEFAULT_COMPONENT_ID = "src_12708" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Series"
FIXED_DOMAIN_KEY = "sequence.series_sums"
DOMAIN_OPERATION = "arithmetic_series_relation"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'sequence.series_sums', 'required_capabilities': ['arithmetic_series_relation'], 'domain_operation': 'arithmetic_series_relation', 'problem_type_id': 'arithmetic_series_relation', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'kind': 'mid_term', 'm': 13, 'value': 11}, {'kind': 'mid_term', 'm': 9, 'value': 31}, {'kind': 'mid_term', 'm': 8, 'value': 21}, {'kind': 'mid_term', 'm': 16, 'value': 0}, {'kind': 'mid_term', 'm': 9, 'value': 34}, {'kind': 'mid_term', 'm': 8, 'value': 12}, {'kind': 'mid_term', 'm': 12, 'value': 41}, {'kind': 'mid_term', 'm': 9, 'value': 36}, {'kind': 'mid_term', 'm': 16, 'value': 18}, {'kind': 'mid_term', 'm': 12, 'value': -13}, {'kind': 'mid_term', 'm': 11, 'value': -8}, {'kind': 'mid_term', 'm': 16, 'value': 17}, {'kind': 'mid_term', 'm': 8, 'value': -11}, {'kind': 'mid_term', 'm': 15, 'value': 5}, {'kind': 'mid_term', 'm': 5, 'value': -9}, {'kind': 'mid_term', 'm': 7, 'value': 33}, {'kind': 'mid_term', 'm': 16, 'value': -8}, {'kind': 'mid_term', 'm': 15, 'value': 34}, {'kind': 'mid_term', 'm': 5, 'value': 41}, {'kind': 'mid_term', 'm': 10, 'value': 25}]}}, 'phase1_classification': {'fixed_domain_key': 'sequence.series_sums', 'required_capabilities': ['arithmetic_series_relation'], 'domain_operation': 'arithmetic_series_relation', 'problem_type_id': 'arithmetic_series_relation', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'kind': 'mid_term', 'm': 13, 'value': 11}, {'kind': 'mid_term', 'm': 9, 'value': 31}, {'kind': 'mid_term', 'm': 8, 'value': 21}, {'kind': 'mid_term', 'm': 16, 'value': 0}, {'kind': 'mid_term', 'm': 9, 'value': 34}, {'kind': 'mid_term', 'm': 8, 'value': 12}, {'kind': 'mid_term', 'm': 12, 'value': 41}, {'kind': 'mid_term', 'm': 9, 'value': 36}, {'kind': 'mid_term', 'm': 16, 'value': 18}, {'kind': 'mid_term', 'm': 12, 'value': -13}, {'kind': 'mid_term', 'm': 11, 'value': -8}, {'kind': 'mid_term', 'm': 16, 'value': 17}, {'kind': 'mid_term', 'm': 8, 'value': -11}, {'kind': 'mid_term', 'm': 15, 'value': 5}, {'kind': 'mid_term', 'm': 5, 'value': -9}, {'kind': 'mid_term', 'm': 7, 'value': 33}, {'kind': 'mid_term', 'm': 16, 'value': -8}, {'kind': 'mid_term', 'm': 15, 'value': 34}, {'kind': 'mid_term', 'm': 5, 'value': 41}, {'kind': 'mid_term', 'm': 10, 'value': 25}]}}, 'problem_type_id': 'arithmetic_series_relation', 'required_capabilities': ['arithmetic_series_relation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'kind': 'mid_term', 'm': 13, 'value': 11}, {'kind': 'mid_term', 'm': 9, 'value': 31}, {'kind': 'mid_term', 'm': 8, 'value': 21}, {'kind': 'mid_term', 'm': 16, 'value': 0}, {'kind': 'mid_term', 'm': 9, 'value': 34}, {'kind': 'mid_term', 'm': 8, 'value': 12}, {'kind': 'mid_term', 'm': 12, 'value': 41}, {'kind': 'mid_term', 'm': 9, 'value': 36}, {'kind': 'mid_term', 'm': 16, 'value': 18}, {'kind': 'mid_term', 'm': 12, 'value': -13}, {'kind': 'mid_term', 'm': 11, 'value': -8}, {'kind': 'mid_term', 'm': 16, 'value': 17}, {'kind': 'mid_term', 'm': 8, 'value': -11}, {'kind': 'mid_term', 'm': 15, 'value': 5}, {'kind': 'mid_term', 'm': 5, 'value': -9}, {'kind': 'mid_term', 'm': 7, 'value': 33}, {'kind': 'mid_term', 'm': 16, 'value': -8}, {'kind': 'mid_term', 'm': 15, 'value': 34}, {'kind': 'mid_term', 'm': 5, 'value': 41}, {'kind': 'mid_term', 'm': 10, 'value': 25}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Series', 'fixed_domain_key': 'sequence.series_sums', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['arithmetic_series_relation'], 'matched_capabilities': ['arithmetic_series_relation'], 'selected_operation': 'arithmetic_series_relation', 'registry_revision': 'promoted-b3fc93095b76', 'domain_module': 'core.domain.promoted.series_summation.series_summation_domain', 'entrypoint': 'build_series_summation_matrix', 'allowed_operations': ['arithmetic_series_items', 'arithmetic_series_relation', 'fish_rows', 'geometric_series_items', 'geometric_series_relation', 'partial_sum_terms', 'series_statements'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Series'}), seed)
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
