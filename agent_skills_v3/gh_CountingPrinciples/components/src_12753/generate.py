from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "two_set_counting"
TEXTBOOK_EXAMPLE_ID = 12753
DEFAULT_COMPONENT_ID = "src_12753" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CountingPrinciples"
FIXED_DOMAIN_KEY = "discrete.sets_counting"
DOMAIN_OPERATION = "two_set_counting"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.sets_counting', 'required_capabilities': ['two_set_counting'], 'domain_operation': 'two_set_counting', 'problem_type_id': 'two_set_counting', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'kind': 'union_and_none', 'U': 40, 'A': 35, 'B': 15, 'AB': 12}, {'kind': 'union_and_none', 'U': 34, 'A': 14, 'B': 29, 'AB': 12}, {'kind': 'union_and_none', 'U': 36, 'A': 25, 'B': 16, 'AB': 8}, {'kind': 'union_and_none', 'U': 35, 'A': 20, 'B': 26, 'AB': 15}, {'kind': 'union_and_none', 'U': 55, 'A': 35, 'B': 26, 'AB': 13}, {'kind': 'union_and_none', 'U': 41, 'A': 34, 'B': 19, 'AB': 16}, {'kind': 'union_and_none', 'U': 34, 'A': 27, 'B': 16, 'AB': 13}, {'kind': 'union_and_none', 'U': 51, 'A': 31, 'B': 25, 'AB': 12}, {'kind': 'union_and_none', 'U': 45, 'A': 32, 'B': 15, 'AB': 9}, {'kind': 'union_and_none', 'U': 31, 'A': 21, 'B': 12, 'AB': 9}, {'kind': 'union_and_none', 'U': 25, 'A': 12, 'B': 17, 'AB': 6}, {'kind': 'union_and_none', 'U': 37, 'A': 17, 'B': 27, 'AB': 15}, {'kind': 'union_and_none', 'U': 23, 'A': 16, 'B': 14, 'AB': 8}, {'kind': 'union_and_none', 'U': 34, 'A': 28, 'B': 7, 'AB': 6}, {'kind': 'union_and_none', 'U': 38, 'A': 30, 'B': 10, 'AB': 6}, {'kind': 'union_and_none', 'U': 54, 'A': 40, 'B': 27, 'AB': 15}, {'kind': 'union_and_none', 'U': 19, 'A': 8, 'B': 12, 'AB': 4}, {'kind': 'union_and_none', 'U': 35, 'A': 25, 'B': 18, 'AB': 15}, {'kind': 'union_and_none', 'U': 41, 'A': 24, 'B': 17, 'AB': 6}, {'kind': 'union_and_none', 'U': 54, 'A': 31, 'B': 22, 'AB': 6}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.sets_counting', 'required_capabilities': ['two_set_counting'], 'domain_operation': 'two_set_counting', 'problem_type_id': 'two_set_counting', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'kind': 'union_and_none', 'U': 40, 'A': 35, 'B': 15, 'AB': 12}, {'kind': 'union_and_none', 'U': 34, 'A': 14, 'B': 29, 'AB': 12}, {'kind': 'union_and_none', 'U': 36, 'A': 25, 'B': 16, 'AB': 8}, {'kind': 'union_and_none', 'U': 35, 'A': 20, 'B': 26, 'AB': 15}, {'kind': 'union_and_none', 'U': 55, 'A': 35, 'B': 26, 'AB': 13}, {'kind': 'union_and_none', 'U': 41, 'A': 34, 'B': 19, 'AB': 16}, {'kind': 'union_and_none', 'U': 34, 'A': 27, 'B': 16, 'AB': 13}, {'kind': 'union_and_none', 'U': 51, 'A': 31, 'B': 25, 'AB': 12}, {'kind': 'union_and_none', 'U': 45, 'A': 32, 'B': 15, 'AB': 9}, {'kind': 'union_and_none', 'U': 31, 'A': 21, 'B': 12, 'AB': 9}, {'kind': 'union_and_none', 'U': 25, 'A': 12, 'B': 17, 'AB': 6}, {'kind': 'union_and_none', 'U': 37, 'A': 17, 'B': 27, 'AB': 15}, {'kind': 'union_and_none', 'U': 23, 'A': 16, 'B': 14, 'AB': 8}, {'kind': 'union_and_none', 'U': 34, 'A': 28, 'B': 7, 'AB': 6}, {'kind': 'union_and_none', 'U': 38, 'A': 30, 'B': 10, 'AB': 6}, {'kind': 'union_and_none', 'U': 54, 'A': 40, 'B': 27, 'AB': 15}, {'kind': 'union_and_none', 'U': 19, 'A': 8, 'B': 12, 'AB': 4}, {'kind': 'union_and_none', 'U': 35, 'A': 25, 'B': 18, 'AB': 15}, {'kind': 'union_and_none', 'U': 41, 'A': 24, 'B': 17, 'AB': 6}, {'kind': 'union_and_none', 'U': 54, 'A': 31, 'B': 22, 'AB': 6}]}}, 'problem_type_id': 'two_set_counting', 'required_capabilities': ['two_set_counting'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'kind': 'union_and_none', 'U': 40, 'A': 35, 'B': 15, 'AB': 12}, {'kind': 'union_and_none', 'U': 34, 'A': 14, 'B': 29, 'AB': 12}, {'kind': 'union_and_none', 'U': 36, 'A': 25, 'B': 16, 'AB': 8}, {'kind': 'union_and_none', 'U': 35, 'A': 20, 'B': 26, 'AB': 15}, {'kind': 'union_and_none', 'U': 55, 'A': 35, 'B': 26, 'AB': 13}, {'kind': 'union_and_none', 'U': 41, 'A': 34, 'B': 19, 'AB': 16}, {'kind': 'union_and_none', 'U': 34, 'A': 27, 'B': 16, 'AB': 13}, {'kind': 'union_and_none', 'U': 51, 'A': 31, 'B': 25, 'AB': 12}, {'kind': 'union_and_none', 'U': 45, 'A': 32, 'B': 15, 'AB': 9}, {'kind': 'union_and_none', 'U': 31, 'A': 21, 'B': 12, 'AB': 9}, {'kind': 'union_and_none', 'U': 25, 'A': 12, 'B': 17, 'AB': 6}, {'kind': 'union_and_none', 'U': 37, 'A': 17, 'B': 27, 'AB': 15}, {'kind': 'union_and_none', 'U': 23, 'A': 16, 'B': 14, 'AB': 8}, {'kind': 'union_and_none', 'U': 34, 'A': 28, 'B': 7, 'AB': 6}, {'kind': 'union_and_none', 'U': 38, 'A': 30, 'B': 10, 'AB': 6}, {'kind': 'union_and_none', 'U': 54, 'A': 40, 'B': 27, 'AB': 15}, {'kind': 'union_and_none', 'U': 19, 'A': 8, 'B': 12, 'AB': 4}, {'kind': 'union_and_none', 'U': 35, 'A': 25, 'B': 18, 'AB': 15}, {'kind': 'union_and_none', 'U': 41, 'A': 24, 'B': 17, 'AB': 6}, {'kind': 'union_and_none', 'U': 54, 'A': 31, 'B': 22, 'AB': 6}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_CountingPrinciples', 'fixed_domain_key': 'discrete.sets_counting', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['two_set_counting'], 'matched_capabilities': ['two_set_counting'], 'selected_operation': 'two_set_counting', 'registry_revision': 'promoted-61f56dc42350', 'domain_module': 'core.domain.promoted.counting_sets.counting_sets_domain', 'entrypoint': 'build_counting_sets_matrix', 'allowed_operations': ['at_least_one_pairing', 'choice_product', 'coin_payment', 'coin_toss_sequences', 'dice_sum_multiples', 'divisor_counting', 'grade_selection', 'graph_paths', 'multiples_counting', 'ordered_at_least_one', 'race_outcomes', 'region_pairs_claim', 'three_set_counting', 'tiling_count', 'two_set_counting'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_CountingPrinciples'}), seed)
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
