from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "three_set_counting"
TEXTBOOK_EXAMPLE_ID = 12771
DEFAULT_COMPONENT_ID = "src_12771" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.sets_counting', 'required_capabilities': ['three_set_counting'], 'domain_operation': 'three_set_counting', 'problem_type_id': 'three_set_counting', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'kind': 'union', 'A': 20, 'B': 10, 'C': 5, 'AB': 6, 'BC': 3, 'CA': 3, 'ABC': 1}, {'kind': 'union', 'A': 14, 'B': 14, 'C': 10, 'AB': 6, 'BC': 2, 'CA': 2, 'ABC': 2}, {'kind': 'union', 'A': 19, 'B': 15, 'C': 19, 'AB': 9, 'BC': 8, 'CA': 5, 'ABC': 2}, {'kind': 'union', 'A': 7, 'B': 14, 'C': 14, 'AB': 6, 'BC': 5, 'CA': 2, 'ABC': 2}, {'kind': 'union', 'A': 16, 'B': 14, 'C': 20, 'AB': 9, 'BC': 5, 'CA': 10, 'ABC': 4}, {'kind': 'union', 'A': 12, 'B': 16, 'C': 21, 'AB': 4, 'BC': 9, 'CA': 10, 'ABC': 3}, {'kind': 'union', 'A': 3, 'B': 16, 'C': 14, 'AB': 3, 'BC': 10, 'CA': 3, 'ABC': 3}, {'kind': 'union', 'A': 29, 'B': 21, 'C': 20, 'AB': 14, 'BC': 12, 'CA': 12, 'ABC': 6}, {'kind': 'union', 'A': 16, 'B': 22, 'C': 22, 'AB': 4, 'BC': 12, 'CA': 7, 'ABC': 3}, {'kind': 'union', 'A': 20, 'B': 30, 'C': 17, 'AB': 13, 'BC': 14, 'CA': 9, 'ABC': 6}, {'kind': 'union', 'A': 6, 'B': 14, 'C': 17, 'AB': 4, 'BC': 12, 'CA': 6, 'ABC': 4}, {'kind': 'union', 'A': 21, 'B': 17, 'C': 20, 'AB': 10, 'BC': 8, 'CA': 7, 'ABC': 4}, {'kind': 'union', 'A': 14, 'B': 14, 'C': 14, 'AB': 10, 'BC': 9, 'CA': 7, 'ABC': 6}, {'kind': 'union', 'A': 22, 'B': 19, 'C': 21, 'AB': 14, 'BC': 8, 'CA': 9, 'ABC': 5}, {'kind': 'union', 'A': 21, 'B': 8, 'C': 21, 'AB': 7, 'BC': 6, 'CA': 14, 'ABC': 6}, {'kind': 'union', 'A': 18, 'B': 20, 'C': 28, 'AB': 4, 'BC': 11, 'CA': 12, 'ABC': 4}, {'kind': 'union', 'A': 23, 'B': 26, 'C': 28, 'AB': 9, 'BC': 13, 'CA': 12, 'ABC': 5}, {'kind': 'union', 'A': 12, 'B': 25, 'C': 18, 'AB': 9, 'BC': 12, 'CA': 5, 'ABC': 3}, {'kind': 'union', 'A': 15, 'B': 27, 'C': 22, 'AB': 13, 'BC': 13, 'CA': 5, 'ABC': 4}, {'kind': 'union', 'A': 22, 'B': 19, 'C': 20, 'AB': 9, 'BC': 13, 'CA': 9, 'ABC': 5}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.sets_counting', 'required_capabilities': ['three_set_counting'], 'domain_operation': 'three_set_counting', 'problem_type_id': 'three_set_counting', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'kind': 'union', 'A': 20, 'B': 10, 'C': 5, 'AB': 6, 'BC': 3, 'CA': 3, 'ABC': 1}, {'kind': 'union', 'A': 14, 'B': 14, 'C': 10, 'AB': 6, 'BC': 2, 'CA': 2, 'ABC': 2}, {'kind': 'union', 'A': 19, 'B': 15, 'C': 19, 'AB': 9, 'BC': 8, 'CA': 5, 'ABC': 2}, {'kind': 'union', 'A': 7, 'B': 14, 'C': 14, 'AB': 6, 'BC': 5, 'CA': 2, 'ABC': 2}, {'kind': 'union', 'A': 16, 'B': 14, 'C': 20, 'AB': 9, 'BC': 5, 'CA': 10, 'ABC': 4}, {'kind': 'union', 'A': 12, 'B': 16, 'C': 21, 'AB': 4, 'BC': 9, 'CA': 10, 'ABC': 3}, {'kind': 'union', 'A': 3, 'B': 16, 'C': 14, 'AB': 3, 'BC': 10, 'CA': 3, 'ABC': 3}, {'kind': 'union', 'A': 29, 'B': 21, 'C': 20, 'AB': 14, 'BC': 12, 'CA': 12, 'ABC': 6}, {'kind': 'union', 'A': 16, 'B': 22, 'C': 22, 'AB': 4, 'BC': 12, 'CA': 7, 'ABC': 3}, {'kind': 'union', 'A': 20, 'B': 30, 'C': 17, 'AB': 13, 'BC': 14, 'CA': 9, 'ABC': 6}, {'kind': 'union', 'A': 6, 'B': 14, 'C': 17, 'AB': 4, 'BC': 12, 'CA': 6, 'ABC': 4}, {'kind': 'union', 'A': 21, 'B': 17, 'C': 20, 'AB': 10, 'BC': 8, 'CA': 7, 'ABC': 4}, {'kind': 'union', 'A': 14, 'B': 14, 'C': 14, 'AB': 10, 'BC': 9, 'CA': 7, 'ABC': 6}, {'kind': 'union', 'A': 22, 'B': 19, 'C': 21, 'AB': 14, 'BC': 8, 'CA': 9, 'ABC': 5}, {'kind': 'union', 'A': 21, 'B': 8, 'C': 21, 'AB': 7, 'BC': 6, 'CA': 14, 'ABC': 6}, {'kind': 'union', 'A': 18, 'B': 20, 'C': 28, 'AB': 4, 'BC': 11, 'CA': 12, 'ABC': 4}, {'kind': 'union', 'A': 23, 'B': 26, 'C': 28, 'AB': 9, 'BC': 13, 'CA': 12, 'ABC': 5}, {'kind': 'union', 'A': 12, 'B': 25, 'C': 18, 'AB': 9, 'BC': 12, 'CA': 5, 'ABC': 3}, {'kind': 'union', 'A': 15, 'B': 27, 'C': 22, 'AB': 13, 'BC': 13, 'CA': 5, 'ABC': 4}, {'kind': 'union', 'A': 22, 'B': 19, 'C': 20, 'AB': 9, 'BC': 13, 'CA': 9, 'ABC': 5}]}}, 'problem_type_id': 'three_set_counting', 'required_capabilities': ['three_set_counting'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'kind': 'union', 'A': 20, 'B': 10, 'C': 5, 'AB': 6, 'BC': 3, 'CA': 3, 'ABC': 1}, {'kind': 'union', 'A': 14, 'B': 14, 'C': 10, 'AB': 6, 'BC': 2, 'CA': 2, 'ABC': 2}, {'kind': 'union', 'A': 19, 'B': 15, 'C': 19, 'AB': 9, 'BC': 8, 'CA': 5, 'ABC': 2}, {'kind': 'union', 'A': 7, 'B': 14, 'C': 14, 'AB': 6, 'BC': 5, 'CA': 2, 'ABC': 2}, {'kind': 'union', 'A': 16, 'B': 14, 'C': 20, 'AB': 9, 'BC': 5, 'CA': 10, 'ABC': 4}, {'kind': 'union', 'A': 12, 'B': 16, 'C': 21, 'AB': 4, 'BC': 9, 'CA': 10, 'ABC': 3}, {'kind': 'union', 'A': 3, 'B': 16, 'C': 14, 'AB': 3, 'BC': 10, 'CA': 3, 'ABC': 3}, {'kind': 'union', 'A': 29, 'B': 21, 'C': 20, 'AB': 14, 'BC': 12, 'CA': 12, 'ABC': 6}, {'kind': 'union', 'A': 16, 'B': 22, 'C': 22, 'AB': 4, 'BC': 12, 'CA': 7, 'ABC': 3}, {'kind': 'union', 'A': 20, 'B': 30, 'C': 17, 'AB': 13, 'BC': 14, 'CA': 9, 'ABC': 6}, {'kind': 'union', 'A': 6, 'B': 14, 'C': 17, 'AB': 4, 'BC': 12, 'CA': 6, 'ABC': 4}, {'kind': 'union', 'A': 21, 'B': 17, 'C': 20, 'AB': 10, 'BC': 8, 'CA': 7, 'ABC': 4}, {'kind': 'union', 'A': 14, 'B': 14, 'C': 14, 'AB': 10, 'BC': 9, 'CA': 7, 'ABC': 6}, {'kind': 'union', 'A': 22, 'B': 19, 'C': 21, 'AB': 14, 'BC': 8, 'CA': 9, 'ABC': 5}, {'kind': 'union', 'A': 21, 'B': 8, 'C': 21, 'AB': 7, 'BC': 6, 'CA': 14, 'ABC': 6}, {'kind': 'union', 'A': 18, 'B': 20, 'C': 28, 'AB': 4, 'BC': 11, 'CA': 12, 'ABC': 4}, {'kind': 'union', 'A': 23, 'B': 26, 'C': 28, 'AB': 9, 'BC': 13, 'CA': 12, 'ABC': 5}, {'kind': 'union', 'A': 12, 'B': 25, 'C': 18, 'AB': 9, 'BC': 12, 'CA': 5, 'ABC': 3}, {'kind': 'union', 'A': 15, 'B': 27, 'C': 22, 'AB': 13, 'BC': 13, 'CA': 5, 'ABC': 4}, {'kind': 'union', 'A': 22, 'B': 19, 'C': 20, 'AB': 9, 'BC': 13, 'CA': 9, 'ABC': 5}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_CountingPrinciples', 'fixed_domain_key': 'discrete.sets_counting', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['three_set_counting'], 'matched_capabilities': ['three_set_counting'], 'selected_operation': 'three_set_counting', 'registry_revision': 'promoted-61f56dc42350', 'domain_module': 'core.domain.promoted.counting_sets.counting_sets_domain', 'entrypoint': 'build_counting_sets_matrix', 'allowed_operations': ['at_least_one_pairing', 'choice_product', 'coin_payment', 'coin_toss_sequences', 'dice_sum_multiples', 'divisor_counting', 'grade_selection', 'graph_paths', 'multiples_counting', 'ordered_at_least_one', 'race_outcomes', 'region_pairs_claim', 'three_set_counting', 'tiling_count', 'two_set_counting'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_CountingPrinciples'}), seed)
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
