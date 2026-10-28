from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "column_shooting_order"
TEXTBOOK_EXAMPLE_ID = 12803
DEFAULT_COMPONENT_ID = "src_12803" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PermutationWithIdenticalItems"
FIXED_DOMAIN_KEY = "discrete.permutations"
DOMAIN_OPERATION = "column_shooting_order"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['column_shooting_order'], 'domain_operation': 'column_shooting_order', 'problem_type_id': 'column_shooting_order', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'counts': [2, 3, 3], 'colors': ['紅', '黃', '藍'], 'figure': 'balloons'}, {'counts': [1, 1, 2], 'colors': ['紅', '黃', '藍']}, {'counts': [1, 2, 4], 'colors': ['紅', '黃', '藍']}, {'counts': [1, 3, 1], 'colors': ['紅', '黃', '藍']}, {'counts': [3, 2, 3], 'colors': ['紅', '黃', '藍']}, {'counts': [4, 5], 'colors': ['紅', '黃']}, {'counts': [3, 1], 'colors': ['紅', '黃']}, {'counts': [1, 3, 4], 'colors': ['紅', '黃', '藍']}, {'counts': [4, 1, 2], 'colors': ['紅', '黃', '藍']}, {'counts': [5, 1, 1], 'colors': ['紅', '黃', '藍']}, {'counts': [3, 4], 'colors': ['紅', '黃']}, {'counts': [5, 1, 3], 'colors': ['紅', '黃', '藍']}, {'counts': [3, 1, 3], 'colors': ['紅', '黃', '藍']}, {'counts': [2, 3], 'colors': ['紅', '黃']}, {'counts': [2, 2, 5], 'colors': ['紅', '黃', '藍']}, {'counts': [3, 3, 4], 'colors': ['紅', '黃', '藍']}, {'counts': [1, 1], 'colors': ['紅', '黃']}, {'counts': [4, 5, 2], 'colors': ['紅', '黃', '藍']}, {'counts': [1, 3], 'colors': ['紅', '黃']}, {'counts': [1, 4], 'colors': ['紅', '黃']}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['column_shooting_order'], 'domain_operation': 'column_shooting_order', 'problem_type_id': 'column_shooting_order', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'counts': [2, 3, 3], 'colors': ['紅', '黃', '藍'], 'figure': 'balloons'}, {'counts': [1, 1, 2], 'colors': ['紅', '黃', '藍']}, {'counts': [1, 2, 4], 'colors': ['紅', '黃', '藍']}, {'counts': [1, 3, 1], 'colors': ['紅', '黃', '藍']}, {'counts': [3, 2, 3], 'colors': ['紅', '黃', '藍']}, {'counts': [4, 5], 'colors': ['紅', '黃']}, {'counts': [3, 1], 'colors': ['紅', '黃']}, {'counts': [1, 3, 4], 'colors': ['紅', '黃', '藍']}, {'counts': [4, 1, 2], 'colors': ['紅', '黃', '藍']}, {'counts': [5, 1, 1], 'colors': ['紅', '黃', '藍']}, {'counts': [3, 4], 'colors': ['紅', '黃']}, {'counts': [5, 1, 3], 'colors': ['紅', '黃', '藍']}, {'counts': [3, 1, 3], 'colors': ['紅', '黃', '藍']}, {'counts': [2, 3], 'colors': ['紅', '黃']}, {'counts': [2, 2, 5], 'colors': ['紅', '黃', '藍']}, {'counts': [3, 3, 4], 'colors': ['紅', '黃', '藍']}, {'counts': [1, 1], 'colors': ['紅', '黃']}, {'counts': [4, 5, 2], 'colors': ['紅', '黃', '藍']}, {'counts': [1, 3], 'colors': ['紅', '黃']}, {'counts': [1, 4], 'colors': ['紅', '黃']}]}}, 'problem_type_id': 'column_shooting_order', 'required_capabilities': ['column_shooting_order'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'counts': [2, 3, 3], 'colors': ['紅', '黃', '藍'], 'figure': 'balloons'}, {'counts': [1, 1, 2], 'colors': ['紅', '黃', '藍']}, {'counts': [1, 2, 4], 'colors': ['紅', '黃', '藍']}, {'counts': [1, 3, 1], 'colors': ['紅', '黃', '藍']}, {'counts': [3, 2, 3], 'colors': ['紅', '黃', '藍']}, {'counts': [4, 5], 'colors': ['紅', '黃']}, {'counts': [3, 1], 'colors': ['紅', '黃']}, {'counts': [1, 3, 4], 'colors': ['紅', '黃', '藍']}, {'counts': [4, 1, 2], 'colors': ['紅', '黃', '藍']}, {'counts': [5, 1, 1], 'colors': ['紅', '黃', '藍']}, {'counts': [3, 4], 'colors': ['紅', '黃']}, {'counts': [5, 1, 3], 'colors': ['紅', '黃', '藍']}, {'counts': [3, 1, 3], 'colors': ['紅', '黃', '藍']}, {'counts': [2, 3], 'colors': ['紅', '黃']}, {'counts': [2, 2, 5], 'colors': ['紅', '黃', '藍']}, {'counts': [3, 3, 4], 'colors': ['紅', '黃', '藍']}, {'counts': [1, 1], 'colors': ['紅', '黃']}, {'counts': [4, 5, 2], 'colors': ['紅', '黃', '藍']}, {'counts': [1, 3], 'colors': ['紅', '黃']}, {'counts': [1, 4], 'colors': ['紅', '黃']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_PermutationWithIdenticalItems', 'fixed_domain_key': 'discrete.permutations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['column_shooting_order'], 'matched_capabilities': ['column_shooting_order'], 'selected_operation': 'column_shooting_order', 'registry_revision': 'promoted-ebcd5e40b80e', 'domain_module': 'core.domain.promoted.permutations.permutations_domain', 'entrypoint': 'build_permutations_matrix', 'allowed_operations': ['colored_distinct_items', 'column_shooting_order', 'counting_claim', 'grid_paths', 'identical_arrangement', 'line_walk', 'multiset_digit_numbers'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_PermutationWithIdenticalItems'}), seed)
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
