from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "divisor_counting"
TEXTBOOK_EXAMPLE_ID = 12759
DEFAULT_COMPONENT_ID = "src_12759" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CountingPrinciples"
FIXED_DOMAIN_KEY = "discrete.sets_counting"
DOMAIN_OPERATION = "divisor_counting"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.sets_counting', 'required_capabilities': ['divisor_counting'], 'domain_operation': 'divisor_counting', 'problem_type_id': 'divisor_counting', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'n': 240, 'multiple_of': 4, 'exclude_multiple_of': 5}, {'n': 180, 'multiple_of': 3, 'exclude_multiple_of': 5}, {'n': 252, 'multiple_of': 2, 'exclude_multiple_of': 3}, {'n': 504, 'multiple_of': 12, 'exclude_multiple_of': 7}, {'n': 480, 'multiple_of': 15, 'exclude_multiple_of': 2}, {'n': 180, 'multiple_of': 18, 'exclude_multiple_of': 5}, {'n': 360, 'multiple_of': 5, 'exclude_multiple_of': 2}, {'n': 1008, 'multiple_of': 18, 'exclude_multiple_of': 7}, {'n': 540, 'multiple_of': 20, 'exclude_multiple_of': 3}, {'n': 720, 'multiple_of': 3, 'exclude_multiple_of': 5}, {'n': 900, 'multiple_of': 9, 'exclude_multiple_of': 2}, {'n': 420, 'multiple_of': 2, 'exclude_multiple_of': 3}, {'n': 480, 'multiple_of': 6, 'exclude_multiple_of': 5}, {'n': 720, 'multiple_of': 10, 'exclude_multiple_of': 3}, {'n': 1008, 'multiple_of': 24, 'exclude_multiple_of': 7}, {'n': 504, 'multiple_of': 24, 'exclude_multiple_of': 7}, {'n': 300, 'multiple_of': 10, 'exclude_multiple_of': 3}, {'n': 600, 'multiple_of': 20, 'exclude_multiple_of': 3}, {'n': 1008, 'multiple_of': 6, 'exclude_multiple_of': 7}, {'n': 600, 'multiple_of': 3, 'exclude_multiple_of': 2}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.sets_counting', 'required_capabilities': ['divisor_counting'], 'domain_operation': 'divisor_counting', 'problem_type_id': 'divisor_counting', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'n': 240, 'multiple_of': 4, 'exclude_multiple_of': 5}, {'n': 180, 'multiple_of': 3, 'exclude_multiple_of': 5}, {'n': 252, 'multiple_of': 2, 'exclude_multiple_of': 3}, {'n': 504, 'multiple_of': 12, 'exclude_multiple_of': 7}, {'n': 480, 'multiple_of': 15, 'exclude_multiple_of': 2}, {'n': 180, 'multiple_of': 18, 'exclude_multiple_of': 5}, {'n': 360, 'multiple_of': 5, 'exclude_multiple_of': 2}, {'n': 1008, 'multiple_of': 18, 'exclude_multiple_of': 7}, {'n': 540, 'multiple_of': 20, 'exclude_multiple_of': 3}, {'n': 720, 'multiple_of': 3, 'exclude_multiple_of': 5}, {'n': 900, 'multiple_of': 9, 'exclude_multiple_of': 2}, {'n': 420, 'multiple_of': 2, 'exclude_multiple_of': 3}, {'n': 480, 'multiple_of': 6, 'exclude_multiple_of': 5}, {'n': 720, 'multiple_of': 10, 'exclude_multiple_of': 3}, {'n': 1008, 'multiple_of': 24, 'exclude_multiple_of': 7}, {'n': 504, 'multiple_of': 24, 'exclude_multiple_of': 7}, {'n': 300, 'multiple_of': 10, 'exclude_multiple_of': 3}, {'n': 600, 'multiple_of': 20, 'exclude_multiple_of': 3}, {'n': 1008, 'multiple_of': 6, 'exclude_multiple_of': 7}, {'n': 600, 'multiple_of': 3, 'exclude_multiple_of': 2}]}}, 'problem_type_id': 'divisor_counting', 'required_capabilities': ['divisor_counting'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'n': 240, 'multiple_of': 4, 'exclude_multiple_of': 5}, {'n': 180, 'multiple_of': 3, 'exclude_multiple_of': 5}, {'n': 252, 'multiple_of': 2, 'exclude_multiple_of': 3}, {'n': 504, 'multiple_of': 12, 'exclude_multiple_of': 7}, {'n': 480, 'multiple_of': 15, 'exclude_multiple_of': 2}, {'n': 180, 'multiple_of': 18, 'exclude_multiple_of': 5}, {'n': 360, 'multiple_of': 5, 'exclude_multiple_of': 2}, {'n': 1008, 'multiple_of': 18, 'exclude_multiple_of': 7}, {'n': 540, 'multiple_of': 20, 'exclude_multiple_of': 3}, {'n': 720, 'multiple_of': 3, 'exclude_multiple_of': 5}, {'n': 900, 'multiple_of': 9, 'exclude_multiple_of': 2}, {'n': 420, 'multiple_of': 2, 'exclude_multiple_of': 3}, {'n': 480, 'multiple_of': 6, 'exclude_multiple_of': 5}, {'n': 720, 'multiple_of': 10, 'exclude_multiple_of': 3}, {'n': 1008, 'multiple_of': 24, 'exclude_multiple_of': 7}, {'n': 504, 'multiple_of': 24, 'exclude_multiple_of': 7}, {'n': 300, 'multiple_of': 10, 'exclude_multiple_of': 3}, {'n': 600, 'multiple_of': 20, 'exclude_multiple_of': 3}, {'n': 1008, 'multiple_of': 6, 'exclude_multiple_of': 7}, {'n': 600, 'multiple_of': 3, 'exclude_multiple_of': 2}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_CountingPrinciples', 'fixed_domain_key': 'discrete.sets_counting', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['divisor_counting'], 'matched_capabilities': ['divisor_counting'], 'selected_operation': 'divisor_counting', 'registry_revision': 'promoted-61f56dc42350', 'domain_module': 'core.domain.promoted.counting_sets.counting_sets_domain', 'entrypoint': 'build_counting_sets_matrix', 'allowed_operations': ['at_least_one_pairing', 'choice_product', 'coin_payment', 'coin_toss_sequences', 'dice_sum_multiples', 'divisor_counting', 'grade_selection', 'graph_paths', 'multiples_counting', 'ordered_at_least_one', 'race_outcomes', 'region_pairs_claim', 'three_set_counting', 'tiling_count', 'two_set_counting'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_CountingPrinciples'}), seed)
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
