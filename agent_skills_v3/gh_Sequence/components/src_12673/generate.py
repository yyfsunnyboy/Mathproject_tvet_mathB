from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "finger_counting_cycle"
TEXTBOOK_EXAMPLE_ID = 12673
DEFAULT_COMPONENT_ID = "src_12673" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Sequence"
FIXED_DOMAIN_KEY = "sequence.progression"
DOMAIN_OPERATION = "finger_counting_cycle"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'sequence.progression', 'required_capabilities': ['finger_counting_cycle'], 'domain_operation': 'finger_counting_cycle', 'problem_type_id': 'finger_counting_cycle', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'ks': [1, 2, 3, 4], 'N': 999}, {'ks': [4, 5, 6, 7], 'N': 308}, {'ks': [3, 4, 5, 6], 'N': 1501}, {'ks': [4, 5, 6, 7], 'N': 400}, {'ks': [2, 3, 4, 5], 'N': 1318}, {'ks': [1, 2, 3, 4], 'N': 1258}, {'ks': [5, 6, 7, 8], 'N': 1722}, {'ks': [3, 7, 11, 12], 'N': 1214}, {'ks': [2, 3, 4, 5], 'N': 1638}, {'ks': [5, 6, 7, 8], 'N': 1737}, {'ks': [1, 2, 3, 4], 'N': 1348}, {'ks': [1, 2, 3, 4], 'N': 852}, {'ks': [1, 2, 3, 4], 'N': 329}, {'ks': [3, 5, 9, 11], 'N': 829}, {'ks': [1, 2, 3, 4], 'N': 1547}, {'ks': [1, 2, 3, 4], 'N': 665}, {'ks': [1, 2, 3, 4], 'N': 512}, {'ks': [2, 3, 4, 5], 'N': 315}, {'ks': [3, 4, 6, 7], 'N': 1155}, {'ks': [5, 6, 11, 12], 'N': 1499}]}}, 'phase1_classification': {'fixed_domain_key': 'sequence.progression', 'required_capabilities': ['finger_counting_cycle'], 'domain_operation': 'finger_counting_cycle', 'problem_type_id': 'finger_counting_cycle', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'ks': [1, 2, 3, 4], 'N': 999}, {'ks': [4, 5, 6, 7], 'N': 308}, {'ks': [3, 4, 5, 6], 'N': 1501}, {'ks': [4, 5, 6, 7], 'N': 400}, {'ks': [2, 3, 4, 5], 'N': 1318}, {'ks': [1, 2, 3, 4], 'N': 1258}, {'ks': [5, 6, 7, 8], 'N': 1722}, {'ks': [3, 7, 11, 12], 'N': 1214}, {'ks': [2, 3, 4, 5], 'N': 1638}, {'ks': [5, 6, 7, 8], 'N': 1737}, {'ks': [1, 2, 3, 4], 'N': 1348}, {'ks': [1, 2, 3, 4], 'N': 852}, {'ks': [1, 2, 3, 4], 'N': 329}, {'ks': [3, 5, 9, 11], 'N': 829}, {'ks': [1, 2, 3, 4], 'N': 1547}, {'ks': [1, 2, 3, 4], 'N': 665}, {'ks': [1, 2, 3, 4], 'N': 512}, {'ks': [2, 3, 4, 5], 'N': 315}, {'ks': [3, 4, 6, 7], 'N': 1155}, {'ks': [5, 6, 11, 12], 'N': 1499}]}}, 'problem_type_id': 'finger_counting_cycle', 'required_capabilities': ['finger_counting_cycle'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'ks': [1, 2, 3, 4], 'N': 999}, {'ks': [4, 5, 6, 7], 'N': 308}, {'ks': [3, 4, 5, 6], 'N': 1501}, {'ks': [4, 5, 6, 7], 'N': 400}, {'ks': [2, 3, 4, 5], 'N': 1318}, {'ks': [1, 2, 3, 4], 'N': 1258}, {'ks': [5, 6, 7, 8], 'N': 1722}, {'ks': [3, 7, 11, 12], 'N': 1214}, {'ks': [2, 3, 4, 5], 'N': 1638}, {'ks': [5, 6, 7, 8], 'N': 1737}, {'ks': [1, 2, 3, 4], 'N': 1348}, {'ks': [1, 2, 3, 4], 'N': 852}, {'ks': [1, 2, 3, 4], 'N': 329}, {'ks': [3, 5, 9, 11], 'N': 829}, {'ks': [1, 2, 3, 4], 'N': 1547}, {'ks': [1, 2, 3, 4], 'N': 665}, {'ks': [1, 2, 3, 4], 'N': 512}, {'ks': [2, 3, 4, 5], 'N': 315}, {'ks': [3, 4, 6, 7], 'N': 1155}, {'ks': [5, 6, 11, 12], 'N': 1499}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Sequence', 'fixed_domain_key': 'sequence.progression', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['finger_counting_cycle'], 'matched_capabilities': ['finger_counting_cycle'], 'selected_operation': 'finger_counting_cycle', 'registry_revision': 'promoted-123c5741bbd3', 'domain_module': 'core.domain.promoted.sequence_progression.sequence_progression_domain', 'entrypoint': 'build_sequence_progression_matrix', 'allowed_operations': ['arithmetic_from_terms', 'figure_path_pattern', 'finger_counting_cycle', 'geometric_from_relations', 'geometric_from_terms', 'progression_three_numbers', 'sequence_statements', 'sequence_terms_from_formula'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Sequence'}), seed)
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
