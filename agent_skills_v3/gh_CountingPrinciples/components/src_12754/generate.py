from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "three_set_counting"
TEXTBOOK_EXAMPLE_ID = 12754
DEFAULT_COMPONENT_ID = "src_12754" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CountingPrinciples"
FIXED_DOMAIN_KEY = "discrete.sets_counting"
DOMAIN_OPERATION = "three_set_counting"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.sets_counting', 'required_capabilities': ['three_set_counting'], 'domain_operation': 'three_set_counting', 'problem_type_id': 'three_set_counting', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'kind': 'union_and_none', 'U': 40, 'A': 15, 'B': 19, 'C': 20, 'AB': 10, 'BC': 12, 'CA': 8, 'ABC': 3}, {'kind': 'union_and_none', 'A': 12, 'B': 13, 'C': 15, 'AB': 3, 'BC': 9, 'CA': 2, 'ABC': 2, 'U': 29}, {'kind': 'union_and_none', 'A': 23, 'B': 19, 'C': 26, 'AB': 9, 'BC': 12, 'CA': 11, 'ABC': 4, 'U': 45}, {'kind': 'union_and_none', 'A': 21, 'B': 23, 'C': 14, 'AB': 13, 'BC': 9, 'CA': 5, 'ABC': 5, 'U': 44}, {'kind': 'union_and_none', 'A': 17, 'B': 16, 'C': 23, 'AB': 4, 'BC': 11, 'CA': 12, 'ABC': 3, 'U': 37}, {'kind': 'union_and_none', 'A': 17, 'B': 19, 'C': 30, 'AB': 7, 'BC': 14, 'CA': 12, 'ABC': 5, 'U': 46}, {'kind': 'union_and_none', 'A': 19, 'B': 24, 'C': 19, 'AB': 12, 'BC': 10, 'CA': 13, 'ABC': 6, 'U': 35}, {'kind': 'union_and_none', 'A': 21, 'B': 22, 'C': 24, 'AB': 15, 'BC': 11, 'CA': 11, 'ABC': 6, 'U': 45}, {'kind': 'union_and_none', 'A': 18, 'B': 9, 'C': 14, 'AB': 2, 'BC': 5, 'CA': 11, 'ABC': 2, 'U': 34}, {'kind': 'union_and_none', 'A': 29, 'B': 22, 'C': 20, 'AB': 15, 'BC': 13, 'CA': 12, 'ABC': 6, 'U': 49}, {'kind': 'union_and_none', 'A': 21, 'B': 21, 'C': 14, 'AB': 14, 'BC': 6, 'CA': 9, 'ABC': 5, 'U': 34}, {'kind': 'union_and_none', 'A': 23, 'B': 12, 'C': 15, 'AB': 10, 'BC': 2, 'CA': 11, 'ABC': 2, 'U': 40}, {'kind': 'union_and_none', 'A': 17, 'B': 11, 'C': 16, 'AB': 3, 'BC': 9, 'CA': 8, 'ABC': 1, 'U': 29}, {'kind': 'union_and_none', 'A': 15, 'B': 21, 'C': 13, 'AB': 12, 'BC': 8, 'CA': 8, 'ABC': 6, 'U': 31}, {'kind': 'union_and_none', 'A': 18, 'B': 19, 'C': 18, 'AB': 7, 'BC': 7, 'CA': 9, 'ABC': 4, 'U': 44}, {'kind': 'union_and_none', 'A': 14, 'B': 6, 'C': 15, 'AB': 6, 'BC': 6, 'CA': 7, 'ABC': 6, 'U': 24}, {'kind': 'union_and_none', 'A': 13, 'B': 17, 'C': 15, 'AB': 7, 'BC': 11, 'CA': 5, 'ABC': 4, 'U': 31}, {'kind': 'union_and_none', 'A': 22, 'B': 15, 'C': 12, 'AB': 9, 'BC': 6, 'CA': 8, 'ABC': 4, 'U': 39}, {'kind': 'union_and_none', 'A': 18, 'B': 10, 'C': 17, 'AB': 5, 'BC': 5, 'CA': 10, 'ABC': 1, 'U': 34}, {'kind': 'union_and_none', 'A': 17, 'B': 21, 'C': 26, 'AB': 6, 'BC': 10, 'CA': 11, 'ABC': 4, 'U': 44}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.sets_counting', 'required_capabilities': ['three_set_counting'], 'domain_operation': 'three_set_counting', 'problem_type_id': 'three_set_counting', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'kind': 'union_and_none', 'U': 40, 'A': 15, 'B': 19, 'C': 20, 'AB': 10, 'BC': 12, 'CA': 8, 'ABC': 3}, {'kind': 'union_and_none', 'A': 12, 'B': 13, 'C': 15, 'AB': 3, 'BC': 9, 'CA': 2, 'ABC': 2, 'U': 29}, {'kind': 'union_and_none', 'A': 23, 'B': 19, 'C': 26, 'AB': 9, 'BC': 12, 'CA': 11, 'ABC': 4, 'U': 45}, {'kind': 'union_and_none', 'A': 21, 'B': 23, 'C': 14, 'AB': 13, 'BC': 9, 'CA': 5, 'ABC': 5, 'U': 44}, {'kind': 'union_and_none', 'A': 17, 'B': 16, 'C': 23, 'AB': 4, 'BC': 11, 'CA': 12, 'ABC': 3, 'U': 37}, {'kind': 'union_and_none', 'A': 17, 'B': 19, 'C': 30, 'AB': 7, 'BC': 14, 'CA': 12, 'ABC': 5, 'U': 46}, {'kind': 'union_and_none', 'A': 19, 'B': 24, 'C': 19, 'AB': 12, 'BC': 10, 'CA': 13, 'ABC': 6, 'U': 35}, {'kind': 'union_and_none', 'A': 21, 'B': 22, 'C': 24, 'AB': 15, 'BC': 11, 'CA': 11, 'ABC': 6, 'U': 45}, {'kind': 'union_and_none', 'A': 18, 'B': 9, 'C': 14, 'AB': 2, 'BC': 5, 'CA': 11, 'ABC': 2, 'U': 34}, {'kind': 'union_and_none', 'A': 29, 'B': 22, 'C': 20, 'AB': 15, 'BC': 13, 'CA': 12, 'ABC': 6, 'U': 49}, {'kind': 'union_and_none', 'A': 21, 'B': 21, 'C': 14, 'AB': 14, 'BC': 6, 'CA': 9, 'ABC': 5, 'U': 34}, {'kind': 'union_and_none', 'A': 23, 'B': 12, 'C': 15, 'AB': 10, 'BC': 2, 'CA': 11, 'ABC': 2, 'U': 40}, {'kind': 'union_and_none', 'A': 17, 'B': 11, 'C': 16, 'AB': 3, 'BC': 9, 'CA': 8, 'ABC': 1, 'U': 29}, {'kind': 'union_and_none', 'A': 15, 'B': 21, 'C': 13, 'AB': 12, 'BC': 8, 'CA': 8, 'ABC': 6, 'U': 31}, {'kind': 'union_and_none', 'A': 18, 'B': 19, 'C': 18, 'AB': 7, 'BC': 7, 'CA': 9, 'ABC': 4, 'U': 44}, {'kind': 'union_and_none', 'A': 14, 'B': 6, 'C': 15, 'AB': 6, 'BC': 6, 'CA': 7, 'ABC': 6, 'U': 24}, {'kind': 'union_and_none', 'A': 13, 'B': 17, 'C': 15, 'AB': 7, 'BC': 11, 'CA': 5, 'ABC': 4, 'U': 31}, {'kind': 'union_and_none', 'A': 22, 'B': 15, 'C': 12, 'AB': 9, 'BC': 6, 'CA': 8, 'ABC': 4, 'U': 39}, {'kind': 'union_and_none', 'A': 18, 'B': 10, 'C': 17, 'AB': 5, 'BC': 5, 'CA': 10, 'ABC': 1, 'U': 34}, {'kind': 'union_and_none', 'A': 17, 'B': 21, 'C': 26, 'AB': 6, 'BC': 10, 'CA': 11, 'ABC': 4, 'U': 44}]}}, 'problem_type_id': 'three_set_counting', 'required_capabilities': ['three_set_counting'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'kind': 'union_and_none', 'U': 40, 'A': 15, 'B': 19, 'C': 20, 'AB': 10, 'BC': 12, 'CA': 8, 'ABC': 3}, {'kind': 'union_and_none', 'A': 12, 'B': 13, 'C': 15, 'AB': 3, 'BC': 9, 'CA': 2, 'ABC': 2, 'U': 29}, {'kind': 'union_and_none', 'A': 23, 'B': 19, 'C': 26, 'AB': 9, 'BC': 12, 'CA': 11, 'ABC': 4, 'U': 45}, {'kind': 'union_and_none', 'A': 21, 'B': 23, 'C': 14, 'AB': 13, 'BC': 9, 'CA': 5, 'ABC': 5, 'U': 44}, {'kind': 'union_and_none', 'A': 17, 'B': 16, 'C': 23, 'AB': 4, 'BC': 11, 'CA': 12, 'ABC': 3, 'U': 37}, {'kind': 'union_and_none', 'A': 17, 'B': 19, 'C': 30, 'AB': 7, 'BC': 14, 'CA': 12, 'ABC': 5, 'U': 46}, {'kind': 'union_and_none', 'A': 19, 'B': 24, 'C': 19, 'AB': 12, 'BC': 10, 'CA': 13, 'ABC': 6, 'U': 35}, {'kind': 'union_and_none', 'A': 21, 'B': 22, 'C': 24, 'AB': 15, 'BC': 11, 'CA': 11, 'ABC': 6, 'U': 45}, {'kind': 'union_and_none', 'A': 18, 'B': 9, 'C': 14, 'AB': 2, 'BC': 5, 'CA': 11, 'ABC': 2, 'U': 34}, {'kind': 'union_and_none', 'A': 29, 'B': 22, 'C': 20, 'AB': 15, 'BC': 13, 'CA': 12, 'ABC': 6, 'U': 49}, {'kind': 'union_and_none', 'A': 21, 'B': 21, 'C': 14, 'AB': 14, 'BC': 6, 'CA': 9, 'ABC': 5, 'U': 34}, {'kind': 'union_and_none', 'A': 23, 'B': 12, 'C': 15, 'AB': 10, 'BC': 2, 'CA': 11, 'ABC': 2, 'U': 40}, {'kind': 'union_and_none', 'A': 17, 'B': 11, 'C': 16, 'AB': 3, 'BC': 9, 'CA': 8, 'ABC': 1, 'U': 29}, {'kind': 'union_and_none', 'A': 15, 'B': 21, 'C': 13, 'AB': 12, 'BC': 8, 'CA': 8, 'ABC': 6, 'U': 31}, {'kind': 'union_and_none', 'A': 18, 'B': 19, 'C': 18, 'AB': 7, 'BC': 7, 'CA': 9, 'ABC': 4, 'U': 44}, {'kind': 'union_and_none', 'A': 14, 'B': 6, 'C': 15, 'AB': 6, 'BC': 6, 'CA': 7, 'ABC': 6, 'U': 24}, {'kind': 'union_and_none', 'A': 13, 'B': 17, 'C': 15, 'AB': 7, 'BC': 11, 'CA': 5, 'ABC': 4, 'U': 31}, {'kind': 'union_and_none', 'A': 22, 'B': 15, 'C': 12, 'AB': 9, 'BC': 6, 'CA': 8, 'ABC': 4, 'U': 39}, {'kind': 'union_and_none', 'A': 18, 'B': 10, 'C': 17, 'AB': 5, 'BC': 5, 'CA': 10, 'ABC': 1, 'U': 34}, {'kind': 'union_and_none', 'A': 17, 'B': 21, 'C': 26, 'AB': 6, 'BC': 10, 'CA': 11, 'ABC': 4, 'U': 44}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_CountingPrinciples', 'fixed_domain_key': 'discrete.sets_counting', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['three_set_counting'], 'matched_capabilities': ['three_set_counting'], 'selected_operation': 'three_set_counting', 'registry_revision': 'promoted-61f56dc42350', 'domain_module': 'core.domain.promoted.counting_sets.counting_sets_domain', 'entrypoint': 'build_counting_sets_matrix', 'allowed_operations': ['at_least_one_pairing', 'choice_product', 'coin_payment', 'coin_toss_sequences', 'dice_sum_multiples', 'divisor_counting', 'grade_selection', 'graph_paths', 'multiples_counting', 'ordered_at_least_one', 'race_outcomes', 'region_pairs_claim', 'three_set_counting', 'tiling_count', 'two_set_counting'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_CountingPrinciples'}), seed)
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
