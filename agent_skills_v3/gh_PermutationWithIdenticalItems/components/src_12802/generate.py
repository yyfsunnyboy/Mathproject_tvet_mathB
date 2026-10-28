from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "line_walk"
TEXTBOOK_EXAMPLE_ID = 12802
DEFAULT_COMPONENT_ID = "src_12802" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PermutationWithIdenticalItems"
FIXED_DOMAIN_KEY = "discrete.permutations"
DOMAIN_OPERATION = "line_walk"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['line_walk'], 'domain_operation': 'line_walk', 'problem_type_id': 'line_walk', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'steps': 6, 'target': 4}, {'steps': 7, 'target': 1}, {'steps': 9, 'target': 7}, {'steps': 10, 'target': 2}, {'steps': 5, 'target': -1}, {'steps': 6, 'target': 2}, {'steps': 6, 'target': -2}, {'steps': 4, 'target': 2}, {'steps': 4, 'target': -2}, {'steps': 10, 'target': -2}, {'steps': 11, 'target': 3}, {'steps': 7, 'target': -3}, {'steps': 7, 'target': 3}, {'steps': 9, 'target': -5}, {'steps': 7, 'target': -5}, {'steps': 10, 'target': 4}, {'steps': 9, 'target': 1}, {'steps': 11, 'target': -3}, {'steps': 8, 'target': 4}, {'steps': 8, 'target': -4}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['line_walk'], 'domain_operation': 'line_walk', 'problem_type_id': 'line_walk', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'steps': 6, 'target': 4}, {'steps': 7, 'target': 1}, {'steps': 9, 'target': 7}, {'steps': 10, 'target': 2}, {'steps': 5, 'target': -1}, {'steps': 6, 'target': 2}, {'steps': 6, 'target': -2}, {'steps': 4, 'target': 2}, {'steps': 4, 'target': -2}, {'steps': 10, 'target': -2}, {'steps': 11, 'target': 3}, {'steps': 7, 'target': -3}, {'steps': 7, 'target': 3}, {'steps': 9, 'target': -5}, {'steps': 7, 'target': -5}, {'steps': 10, 'target': 4}, {'steps': 9, 'target': 1}, {'steps': 11, 'target': -3}, {'steps': 8, 'target': 4}, {'steps': 8, 'target': -4}]}}, 'problem_type_id': 'line_walk', 'required_capabilities': ['line_walk'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'steps': 6, 'target': 4}, {'steps': 7, 'target': 1}, {'steps': 9, 'target': 7}, {'steps': 10, 'target': 2}, {'steps': 5, 'target': -1}, {'steps': 6, 'target': 2}, {'steps': 6, 'target': -2}, {'steps': 4, 'target': 2}, {'steps': 4, 'target': -2}, {'steps': 10, 'target': -2}, {'steps': 11, 'target': 3}, {'steps': 7, 'target': -3}, {'steps': 7, 'target': 3}, {'steps': 9, 'target': -5}, {'steps': 7, 'target': -5}, {'steps': 10, 'target': 4}, {'steps': 9, 'target': 1}, {'steps': 11, 'target': -3}, {'steps': 8, 'target': 4}, {'steps': 8, 'target': -4}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_PermutationWithIdenticalItems', 'fixed_domain_key': 'discrete.permutations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['line_walk'], 'matched_capabilities': ['line_walk'], 'selected_operation': 'line_walk', 'registry_revision': 'promoted-ebcd5e40b80e', 'domain_module': 'core.domain.promoted.permutations.permutations_domain', 'entrypoint': 'build_permutations_matrix', 'allowed_operations': ['colored_distinct_items', 'column_shooting_order', 'counting_claim', 'grid_paths', 'identical_arrangement', 'line_walk', 'multiset_digit_numbers'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_PermutationWithIdenticalItems'}), seed)
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
