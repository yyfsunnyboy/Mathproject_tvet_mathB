from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "recurrence_from_process"
TEXTBOOK_EXAMPLE_ID = 12687
DEFAULT_COMPONENT_ID = "src_12687" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RecursiveRelation"
FIXED_DOMAIN_KEY = "sequence.progression"
DOMAIN_OPERATION = "recurrence_from_process"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'sequence.progression', 'required_capabilities': ['recurrence_from_process'], 'domain_operation': 'recurrence_from_process', 'problem_type_id': 'recurrence_from_process', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 1, 'where': '中間', 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 12, 'ask': 'value', 'k': 4}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 2, 'ask': 'value', 'k': 7}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 14, 'ask': 'value', 'k': 9}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 3, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 2, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 7, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 3, 'ask': 'value', 'k': 7}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 2, 'ask': 'value', 'k': 8}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 3, 'ask': 'value', 'k': 5}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 9, 'ask': 'value', 'k': 7}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 1, 'ask': 'value', 'k': 9}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 1, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 8, 'ask': 'value', 'k': 9}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 6, 'ask': 'value', 'k': 8}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 8, 'ask': 'value', 'k': 4}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 4, 'ask': 'value', 'k': 9}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 14, 'ask': 'value', 'k': 7}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 6, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 1, 'ask': 'value', 'where': '中間', 'k': 4}]}}, 'phase1_classification': {'fixed_domain_key': 'sequence.progression', 'required_capabilities': ['recurrence_from_process'], 'domain_operation': 'recurrence_from_process', 'problem_type_id': 'recurrence_from_process', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 1, 'where': '中間', 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 12, 'ask': 'value', 'k': 4}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 2, 'ask': 'value', 'k': 7}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 14, 'ask': 'value', 'k': 9}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 3, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 2, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 7, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 3, 'ask': 'value', 'k': 7}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 2, 'ask': 'value', 'k': 8}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 3, 'ask': 'value', 'k': 5}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 9, 'ask': 'value', 'k': 7}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 1, 'ask': 'value', 'k': 9}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 1, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 8, 'ask': 'value', 'k': 9}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 6, 'ask': 'value', 'k': 8}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 8, 'ask': 'value', 'k': 4}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 4, 'ask': 'value', 'k': 9}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 14, 'ask': 'value', 'k': 7}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 6, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 1, 'ask': 'value', 'where': '中間', 'k': 4}]}}, 'problem_type_id': 'recurrence_from_process', 'required_capabilities': ['recurrence_from_process'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 1, 'where': '中間', 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 12, 'ask': 'value', 'k': 4}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 2, 'ask': 'value', 'k': 7}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 14, 'ask': 'value', 'k': 9}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 3, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 2, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 7, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 3, 'ask': 'value', 'k': 7}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 2, 'ask': 'value', 'k': 8}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 3, 'ask': 'value', 'k': 5}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 9, 'ask': 'value', 'k': 7}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 1, 'ask': 'value', 'k': 9}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 1, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 8, 'ask': 'value', 'k': 9}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 6, 'ask': 'value', 'k': 8}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 8, 'ask': 'value', 'k': 4}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 9, 'removed': 4, 'ask': 'value', 'k': 9}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 14, 'ask': 'value', 'k': 7}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 16, 'removed': 6, 'ask': 'value', 'k': 6}, {'kind': 'subdivision', 'shape': 'triangle', 'parts': 4, 'removed': 1, 'ask': 'value', 'where': '中間', 'k': 4}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_RecursiveRelation', 'fixed_domain_key': 'sequence.progression', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['recurrence_from_process'], 'matched_capabilities': ['recurrence_from_process'], 'selected_operation': 'recurrence_from_process', 'registry_revision': 'promoted-9863553f3bfd', 'domain_module': 'core.domain.promoted.sequence_progression.sequence_progression_domain', 'entrypoint': 'build_sequence_progression_matrix', 'allowed_operations': ['progression_three_numbers', 'recurrence_from_process', 'sequence_statements'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_RecursiveRelation'}), seed)
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
