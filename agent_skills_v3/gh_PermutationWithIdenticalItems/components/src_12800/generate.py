from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "colored_distinct_items"
TEXTBOOK_EXAMPLE_ID = 12800
DEFAULT_COMPONENT_ID = "src_12800" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PermutationWithIdenticalItems"
FIXED_DOMAIN_KEY = "discrete.permutations"
DOMAIN_OPERATION = "colored_distinct_items"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['colored_distinct_items'], 'domain_operation': 'colored_distinct_items', 'problem_type_id': 'colored_distinct_items', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'counts': [2, 3, 4], 'colors': ['黃', '白', '黑'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 3, 3], 'colors': ['黃', '棕', '灰'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [3, 2, 3], 'colors': ['黃', '灰', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 3, 3], 'colors': ['黑', '橘', '黃'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 2, 3], 'colors': ['棕', '灰', '白'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 3, 2], 'colors': ['黃', '棕', '白'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 2, 3], 'colors': ['黑', '灰', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 4, 2], 'colors': ['灰', '橘', '黃'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 3, 3], 'colors': ['黑', '橘', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 2, 4], 'colors': ['黃', '白', '灰'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 2, 5], 'colors': ['白', '橘', '黃'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 4, 3], 'colors': ['黃', '黑', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [3, 2, 5], 'colors': ['白', '黑', '灰'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [3, 4, 3], 'colors': ['橘', '棕', '黃'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 4, 3], 'colors': ['白', '灰', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [3, 2, 5], 'colors': ['黑', '白', '灰'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 2, 4], 'colors': ['灰', '棕', '橘'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 4, 3], 'colors': ['橘', '灰', '黑'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 2, 3], 'colors': ['黑', '白', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 3, 2], 'colors': ['黃', '灰', '橘'], 'asks': ['each_color_together', 'last_color_apart']}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['colored_distinct_items'], 'domain_operation': 'colored_distinct_items', 'problem_type_id': 'colored_distinct_items', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'counts': [2, 3, 4], 'colors': ['黃', '白', '黑'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 3, 3], 'colors': ['黃', '棕', '灰'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [3, 2, 3], 'colors': ['黃', '灰', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 3, 3], 'colors': ['黑', '橘', '黃'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 2, 3], 'colors': ['棕', '灰', '白'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 3, 2], 'colors': ['黃', '棕', '白'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 2, 3], 'colors': ['黑', '灰', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 4, 2], 'colors': ['灰', '橘', '黃'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 3, 3], 'colors': ['黑', '橘', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 2, 4], 'colors': ['黃', '白', '灰'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 2, 5], 'colors': ['白', '橘', '黃'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 4, 3], 'colors': ['黃', '黑', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [3, 2, 5], 'colors': ['白', '黑', '灰'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [3, 4, 3], 'colors': ['橘', '棕', '黃'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 4, 3], 'colors': ['白', '灰', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [3, 2, 5], 'colors': ['黑', '白', '灰'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 2, 4], 'colors': ['灰', '棕', '橘'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 4, 3], 'colors': ['橘', '灰', '黑'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 2, 3], 'colors': ['黑', '白', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 3, 2], 'colors': ['黃', '灰', '橘'], 'asks': ['each_color_together', 'last_color_apart']}]}}, 'problem_type_id': 'colored_distinct_items', 'required_capabilities': ['colored_distinct_items'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'counts': [2, 3, 4], 'colors': ['黃', '白', '黑'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 3, 3], 'colors': ['黃', '棕', '灰'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [3, 2, 3], 'colors': ['黃', '灰', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 3, 3], 'colors': ['黑', '橘', '黃'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 2, 3], 'colors': ['棕', '灰', '白'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 3, 2], 'colors': ['黃', '棕', '白'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 2, 3], 'colors': ['黑', '灰', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 4, 2], 'colors': ['灰', '橘', '黃'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 3, 3], 'colors': ['黑', '橘', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 2, 4], 'colors': ['黃', '白', '灰'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 2, 5], 'colors': ['白', '橘', '黃'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 4, 3], 'colors': ['黃', '黑', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [3, 2, 5], 'colors': ['白', '黑', '灰'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [3, 4, 3], 'colors': ['橘', '棕', '黃'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 4, 3], 'colors': ['白', '灰', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [3, 2, 5], 'colors': ['黑', '白', '灰'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 2, 4], 'colors': ['灰', '棕', '橘'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 4, 3], 'colors': ['橘', '灰', '黑'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [4, 2, 3], 'colors': ['黑', '白', '棕'], 'asks': ['each_color_together', 'last_color_apart']}, {'counts': [2, 3, 2], 'colors': ['黃', '灰', '橘'], 'asks': ['each_color_together', 'last_color_apart']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_PermutationWithIdenticalItems', 'fixed_domain_key': 'discrete.permutations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['colored_distinct_items'], 'matched_capabilities': ['colored_distinct_items'], 'selected_operation': 'colored_distinct_items', 'registry_revision': 'promoted-ebcd5e40b80e', 'domain_module': 'core.domain.promoted.permutations.permutations_domain', 'entrypoint': 'build_permutations_matrix', 'allowed_operations': ['colored_distinct_items', 'column_shooting_order', 'counting_claim', 'grid_paths', 'identical_arrangement', 'line_walk', 'multiset_digit_numbers'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_PermutationWithIdenticalItems'}), seed)
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
