from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "grid_paths"
TEXTBOOK_EXAMPLE_ID = 12794
DEFAULT_COMPONENT_ID = "src_12794" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PermutationWithIdenticalItems"
FIXED_DOMAIN_KEY = "discrete.permutations"
DOMAIN_OPERATION = "grid_paths"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['grid_paths'], 'domain_operation': 'grid_paths', 'problem_type_id': 'grid_paths', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'width': 7, 'height': 3, 'points': {'C': [2, 1], 'D': [4, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both'], 'figure': 'example7'}, {'width': 6, 'height': 2, 'points': {'C': [3, 1], 'D': [1, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 8, 'height': 3, 'points': {'C': [1, 2], 'D': [6, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 3, 'points': {'C': [3, 1], 'D': [3, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 8, 'height': 4, 'points': {'C': [4, 3], 'D': [7, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 5, 'height': 2, 'points': {'C': [1, 1], 'D': [4, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 8, 'height': 2, 'points': {'C': [6, 1], 'D': [1, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 7, 'height': 4, 'points': {'C': [2, 1], 'D': [6, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 4, 'points': {'C': [2, 3], 'D': [1, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 3, 'points': {'C': [2, 2], 'D': [3, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 6, 'height': 4, 'points': {'C': [4, 1], 'D': [1, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 7, 'height': 3, 'points': {'C': [6, 2], 'D': [2, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 4, 'points': {'C': [2, 1], 'D': [1, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 5, 'height': 3, 'points': {'C': [3, 2], 'D': [4, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 2, 'points': {'C': [1, 1], 'D': [2, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 7, 'height': 4, 'points': {'C': [2, 2], 'D': [5, 3]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 6, 'height': 4, 'points': {'C': [4, 3], 'D': [5, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 8, 'height': 4, 'points': {'C': [3, 3], 'D': [1, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 7, 'height': 4, 'points': {'C': [4, 3], 'D': [3, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 4, 'points': {'C': [1, 2], 'D': [2, 3]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['grid_paths'], 'domain_operation': 'grid_paths', 'problem_type_id': 'grid_paths', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'width': 7, 'height': 3, 'points': {'C': [2, 1], 'D': [4, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both'], 'figure': 'example7'}, {'width': 6, 'height': 2, 'points': {'C': [3, 1], 'D': [1, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 8, 'height': 3, 'points': {'C': [1, 2], 'D': [6, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 3, 'points': {'C': [3, 1], 'D': [3, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 8, 'height': 4, 'points': {'C': [4, 3], 'D': [7, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 5, 'height': 2, 'points': {'C': [1, 1], 'D': [4, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 8, 'height': 2, 'points': {'C': [6, 1], 'D': [1, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 7, 'height': 4, 'points': {'C': [2, 1], 'D': [6, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 4, 'points': {'C': [2, 3], 'D': [1, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 3, 'points': {'C': [2, 2], 'D': [3, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 6, 'height': 4, 'points': {'C': [4, 1], 'D': [1, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 7, 'height': 3, 'points': {'C': [6, 2], 'D': [2, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 4, 'points': {'C': [2, 1], 'D': [1, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 5, 'height': 3, 'points': {'C': [3, 2], 'D': [4, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 2, 'points': {'C': [1, 1], 'D': [2, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 7, 'height': 4, 'points': {'C': [2, 2], 'D': [5, 3]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 6, 'height': 4, 'points': {'C': [4, 3], 'D': [5, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 8, 'height': 4, 'points': {'C': [3, 3], 'D': [1, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 7, 'height': 4, 'points': {'C': [4, 3], 'D': [3, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 4, 'points': {'C': [1, 2], 'D': [2, 3]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}]}}, 'problem_type_id': 'grid_paths', 'required_capabilities': ['grid_paths'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'width': 7, 'height': 3, 'points': {'C': [2, 1], 'D': [4, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both'], 'figure': 'example7'}, {'width': 6, 'height': 2, 'points': {'C': [3, 1], 'D': [1, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 8, 'height': 3, 'points': {'C': [1, 2], 'D': [6, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 3, 'points': {'C': [3, 1], 'D': [3, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 8, 'height': 4, 'points': {'C': [4, 3], 'D': [7, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 5, 'height': 2, 'points': {'C': [1, 1], 'D': [4, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 8, 'height': 2, 'points': {'C': [6, 1], 'D': [1, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 7, 'height': 4, 'points': {'C': [2, 1], 'D': [6, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 4, 'points': {'C': [2, 3], 'D': [1, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 3, 'points': {'C': [2, 2], 'D': [3, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 6, 'height': 4, 'points': {'C': [4, 1], 'D': [1, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 7, 'height': 3, 'points': {'C': [6, 2], 'D': [2, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 4, 'points': {'C': [2, 1], 'D': [1, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 5, 'height': 3, 'points': {'C': [3, 2], 'D': [4, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 2, 'points': {'C': [1, 1], 'D': [2, 1]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 7, 'height': 4, 'points': {'C': [2, 2], 'D': [5, 3]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 6, 'height': 4, 'points': {'C': [4, 3], 'D': [5, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 8, 'height': 4, 'points': {'C': [3, 3], 'D': [1, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 7, 'height': 4, 'points': {'C': [4, 3], 'D': [3, 2]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}, {'width': 4, 'height': 4, 'points': {'C': [1, 2], 'D': [2, 3]}, 'asks': ['any', 'via_C', 'via_C_or_D', 'avoid_both']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_PermutationWithIdenticalItems', 'fixed_domain_key': 'discrete.permutations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['grid_paths'], 'matched_capabilities': ['grid_paths'], 'selected_operation': 'grid_paths', 'registry_revision': 'promoted-ebcd5e40b80e', 'domain_module': 'core.domain.promoted.permutations.permutations_domain', 'entrypoint': 'build_permutations_matrix', 'allowed_operations': ['colored_distinct_items', 'column_shooting_order', 'counting_claim', 'grid_paths', 'identical_arrangement', 'line_walk', 'multiset_digit_numbers'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_PermutationWithIdenticalItems'}), seed)
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
