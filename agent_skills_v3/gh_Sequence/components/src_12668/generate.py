from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "figure_path_pattern"
TEXTBOOK_EXAMPLE_ID = 12668
DEFAULT_COMPONENT_ID = "src_12668" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Sequence"
FIXED_DOMAIN_KEY = "sequence.progression"
DOMAIN_OPERATION = "figure_path_pattern"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'sequence.progression', 'required_capabilities': ['figure_path_pattern'], 'domain_operation': 'figure_path_pattern', 'problem_type_id': 'figure_path_pattern', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'start': 1, 't': 106, 'T': 107, 'order': [2, 3, 0, 1]}, {'start': 1, 't': 259, 'T': 260, 'order': [3, 2, 1, 0]}, {'start': 1, 't': 106, 'T': 126, 'order': [0, 2, 1, 3]}, {'start': 1, 't': 205, 'T': 206, 'order': [1, 2, 3, 0]}, {'start': 1, 't': 48, 'T': 15, 'order': [3, 2, 0, 1]}, {'start': 1, 't': 250, 'T': 251, 'order': [2, 1, 3, 0]}, {'start': 1, 't': 299, 'T': 300, 'order': [0, 1, 2, 3]}, {'start': 1, 't': 45, 'T': 245, 'order': [2, 3, 1, 0]}, {'start': 1, 't': 119, 'T': 120, 'order': [3, 1, 2, 0]}, {'start': 1, 't': 187, 'T': 188, 'order': [1, 3, 0, 2]}, {'start': 1, 't': 47, 'T': 140, 'order': [0, 1, 2, 3]}, {'start': 1, 't': 143, 'T': 479, 'order': [0, 3, 2, 1]}, {'start': 1, 't': 148, 'T': 71, 'order': [1, 3, 0, 2]}, {'start': 1, 't': 136, 'T': 137, 'order': [3, 1, 0, 2]}, {'start': 1, 't': 235, 'T': 236, 'order': [3, 1, 2, 0]}, {'start': 1, 't': 27, 'T': 28, 'order': [0, 3, 2, 1]}, {'start': 1, 't': 175, 'T': 240, 'order': [0, 1, 2, 3]}, {'start': 1, 't': 400, 'T': 401, 'order': [1, 0, 3, 2]}, {'start': 1, 't': 288, 'T': 324, 'order': [3, 0, 1, 2]}, {'start': 1, 't': 141, 'T': 429, 'order': [1, 0, 2, 3]}]}}, 'phase1_classification': {'fixed_domain_key': 'sequence.progression', 'required_capabilities': ['figure_path_pattern'], 'domain_operation': 'figure_path_pattern', 'problem_type_id': 'figure_path_pattern', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'start': 1, 't': 106, 'T': 107, 'order': [2, 3, 0, 1]}, {'start': 1, 't': 259, 'T': 260, 'order': [3, 2, 1, 0]}, {'start': 1, 't': 106, 'T': 126, 'order': [0, 2, 1, 3]}, {'start': 1, 't': 205, 'T': 206, 'order': [1, 2, 3, 0]}, {'start': 1, 't': 48, 'T': 15, 'order': [3, 2, 0, 1]}, {'start': 1, 't': 250, 'T': 251, 'order': [2, 1, 3, 0]}, {'start': 1, 't': 299, 'T': 300, 'order': [0, 1, 2, 3]}, {'start': 1, 't': 45, 'T': 245, 'order': [2, 3, 1, 0]}, {'start': 1, 't': 119, 'T': 120, 'order': [3, 1, 2, 0]}, {'start': 1, 't': 187, 'T': 188, 'order': [1, 3, 0, 2]}, {'start': 1, 't': 47, 'T': 140, 'order': [0, 1, 2, 3]}, {'start': 1, 't': 143, 'T': 479, 'order': [0, 3, 2, 1]}, {'start': 1, 't': 148, 'T': 71, 'order': [1, 3, 0, 2]}, {'start': 1, 't': 136, 'T': 137, 'order': [3, 1, 0, 2]}, {'start': 1, 't': 235, 'T': 236, 'order': [3, 1, 2, 0]}, {'start': 1, 't': 27, 'T': 28, 'order': [0, 3, 2, 1]}, {'start': 1, 't': 175, 'T': 240, 'order': [0, 1, 2, 3]}, {'start': 1, 't': 400, 'T': 401, 'order': [1, 0, 3, 2]}, {'start': 1, 't': 288, 'T': 324, 'order': [3, 0, 1, 2]}, {'start': 1, 't': 141, 'T': 429, 'order': [1, 0, 2, 3]}]}}, 'problem_type_id': 'figure_path_pattern', 'required_capabilities': ['figure_path_pattern'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'start': 1, 't': 106, 'T': 107, 'order': [2, 3, 0, 1]}, {'start': 1, 't': 259, 'T': 260, 'order': [3, 2, 1, 0]}, {'start': 1, 't': 106, 'T': 126, 'order': [0, 2, 1, 3]}, {'start': 1, 't': 205, 'T': 206, 'order': [1, 2, 3, 0]}, {'start': 1, 't': 48, 'T': 15, 'order': [3, 2, 0, 1]}, {'start': 1, 't': 250, 'T': 251, 'order': [2, 1, 3, 0]}, {'start': 1, 't': 299, 'T': 300, 'order': [0, 1, 2, 3]}, {'start': 1, 't': 45, 'T': 245, 'order': [2, 3, 1, 0]}, {'start': 1, 't': 119, 'T': 120, 'order': [3, 1, 2, 0]}, {'start': 1, 't': 187, 'T': 188, 'order': [1, 3, 0, 2]}, {'start': 1, 't': 47, 'T': 140, 'order': [0, 1, 2, 3]}, {'start': 1, 't': 143, 'T': 479, 'order': [0, 3, 2, 1]}, {'start': 1, 't': 148, 'T': 71, 'order': [1, 3, 0, 2]}, {'start': 1, 't': 136, 'T': 137, 'order': [3, 1, 0, 2]}, {'start': 1, 't': 235, 'T': 236, 'order': [3, 1, 2, 0]}, {'start': 1, 't': 27, 'T': 28, 'order': [0, 3, 2, 1]}, {'start': 1, 't': 175, 'T': 240, 'order': [0, 1, 2, 3]}, {'start': 1, 't': 400, 'T': 401, 'order': [1, 0, 3, 2]}, {'start': 1, 't': 288, 'T': 324, 'order': [3, 0, 1, 2]}, {'start': 1, 't': 141, 'T': 429, 'order': [1, 0, 2, 3]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Sequence', 'fixed_domain_key': 'sequence.progression', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['figure_path_pattern'], 'matched_capabilities': ['figure_path_pattern'], 'selected_operation': 'figure_path_pattern', 'registry_revision': 'promoted-123c5741bbd3', 'domain_module': 'core.domain.promoted.sequence_progression.sequence_progression_domain', 'entrypoint': 'build_sequence_progression_matrix', 'allowed_operations': ['arithmetic_from_terms', 'figure_path_pattern', 'finger_counting_cycle', 'geometric_from_relations', 'geometric_from_terms', 'progression_three_numbers', 'sequence_statements', 'sequence_terms_from_formula'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Sequence'}), seed)
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
