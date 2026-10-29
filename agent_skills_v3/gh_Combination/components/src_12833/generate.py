from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "multiset_select_arrange"
TEXTBOOK_EXAMPLE_ID = 12833
DEFAULT_COMPONENT_ID = "src_12833" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Combination"
FIXED_DOMAIN_KEY = "discrete.combinations"
DOMAIN_OPERATION = "multiset_select_arrange"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.combinations', 'required_capabilities': ['multiset_select_arrange'], 'domain_operation': 'multiset_select_arrange', 'problem_type_id': 'multiset_select_arrange', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'word': 'snoopy', 'pick': 3}, {'word': 'kitten', 'pick': 2}, {'word': 'yellow', 'pick': 2}, {'word': 'hello', 'pick': 2}, {'word': 'cookie', 'pick': 2}, {'word': 'cookie', 'pick': 4}, {'word': 'banana', 'pick': 3}, {'word': 'letter', 'pick': 4}, {'word': 'coffee', 'pick': 2}, {'word': 'letter', 'pick': 3}, {'word': 'bottle', 'pick': 2}, {'word': 'hello', 'pick': 3}, {'word': 'bottle', 'pick': 3}, {'word': 'puppy', 'pick': 2}, {'word': 'snoopy', 'pick': 4}, {'word': 'banana', 'pick': 4}, {'word': 'teeth', 'pick': 2}, {'word': 'cookie', 'pick': 3}, {'word': 'coffee', 'pick': 4}, {'word': 'google', 'pick': 4}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.combinations', 'required_capabilities': ['multiset_select_arrange'], 'domain_operation': 'multiset_select_arrange', 'problem_type_id': 'multiset_select_arrange', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'word': 'snoopy', 'pick': 3}, {'word': 'kitten', 'pick': 2}, {'word': 'yellow', 'pick': 2}, {'word': 'hello', 'pick': 2}, {'word': 'cookie', 'pick': 2}, {'word': 'cookie', 'pick': 4}, {'word': 'banana', 'pick': 3}, {'word': 'letter', 'pick': 4}, {'word': 'coffee', 'pick': 2}, {'word': 'letter', 'pick': 3}, {'word': 'bottle', 'pick': 2}, {'word': 'hello', 'pick': 3}, {'word': 'bottle', 'pick': 3}, {'word': 'puppy', 'pick': 2}, {'word': 'snoopy', 'pick': 4}, {'word': 'banana', 'pick': 4}, {'word': 'teeth', 'pick': 2}, {'word': 'cookie', 'pick': 3}, {'word': 'coffee', 'pick': 4}, {'word': 'google', 'pick': 4}]}}, 'problem_type_id': 'multiset_select_arrange', 'required_capabilities': ['multiset_select_arrange'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'word': 'snoopy', 'pick': 3}, {'word': 'kitten', 'pick': 2}, {'word': 'yellow', 'pick': 2}, {'word': 'hello', 'pick': 2}, {'word': 'cookie', 'pick': 2}, {'word': 'cookie', 'pick': 4}, {'word': 'banana', 'pick': 3}, {'word': 'letter', 'pick': 4}, {'word': 'coffee', 'pick': 2}, {'word': 'letter', 'pick': 3}, {'word': 'bottle', 'pick': 2}, {'word': 'hello', 'pick': 3}, {'word': 'bottle', 'pick': 3}, {'word': 'puppy', 'pick': 2}, {'word': 'snoopy', 'pick': 4}, {'word': 'banana', 'pick': 4}, {'word': 'teeth', 'pick': 2}, {'word': 'cookie', 'pick': 3}, {'word': 'coffee', 'pick': 4}, {'word': 'google', 'pick': 4}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Combination', 'fixed_domain_key': 'discrete.combinations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['multiset_select_arrange'], 'matched_capabilities': ['multiset_select_arrange'], 'selected_operation': 'multiset_select_arrange', 'registry_revision': 'promoted-848b2241bfec', 'domain_module': 'core.domain.promoted.combinations.combinations_domain', 'entrypoint': 'build_combinations_matrix', 'allowed_operations': ['combination_claim', 'combination_evaluate', 'combination_identity_select', 'gender_committee', 'group_partition', 'mixed_group_ordered', 'multiset_select_arrange', 'pair_count', 'paired_group_assignment', 'parity_sum_selection', 'select_with_members', 'sequential_selection', 'surjective_distribution'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Combination'}), seed)
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
