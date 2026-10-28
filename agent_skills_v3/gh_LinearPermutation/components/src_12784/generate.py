from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "counting_claim"
TEXTBOOK_EXAMPLE_ID = 12784
DEFAULT_COMPONENT_ID = "src_12784" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_LinearPermutation"
FIXED_DOMAIN_KEY = "discrete.permutations"
DOMAIN_OPERATION = "counting_claim"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['counting_claim'], 'domain_operation': 'counting_claim', 'problem_type_id': 'counting_claim', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['讀', '書', '好']}, 'claim': {'form': 'number', 'value': 6}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['讀', '書', '理', '學', '樂']}, 'claim': {'form': 'number', 'value': 120}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['習', '好', '學', '讀', '書']}, 'claim': {'form': 'number', 'value': 25}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['理', '讀', '學', '樂']}, 'claim': {'form': 'number', 'value': 24}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['數', '讀', '樂']}, 'claim': {'form': 'number', 'value': 6}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['學', '數', '習', '理', '好']}, 'claim': {'form': 'number', 'value': 120}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['習', '樂', '數', '好', '理']}, 'claim': {'form': 'number', 'value': 120}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['書', '樂', '數', '理']}, 'claim': {'form': 'number', 'value': 24}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['書', '學', '樂', '數']}, 'claim': {'form': 'number', 'value': 48}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['好', '學', '書']}, 'claim': {'form': 'number', 'value': 12}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['學', '讀', '數']}, 'claim': {'form': 'number', 'value': 9}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['好', '學', '數']}, 'claim': {'form': 'number', 'value': 27}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['樂', '書', '學']}, 'claim': {'form': 'number', 'value': 9}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['理', '學', '數', '樂']}, 'claim': {'form': 'number', 'value': 24}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['習', '書', '理', '樂', '學']}, 'claim': {'form': 'number', 'value': 120}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['理', '書', '習', '數']}, 'claim': {'form': 'number', 'value': 24}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['習', '學', '理', '書']}, 'claim': {'form': 'number', 'value': 28}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['好', '習', '書']}, 'claim': {'form': 'number', 'value': 6}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['數', '讀', '學', '理']}, 'claim': {'form': 'number', 'value': 8}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['書', '數', '樂', '學']}, 'claim': {'form': 'number', 'value': 24}}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['counting_claim'], 'domain_operation': 'counting_claim', 'problem_type_id': 'counting_claim', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['讀', '書', '好']}, 'claim': {'form': 'number', 'value': 6}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['讀', '書', '理', '學', '樂']}, 'claim': {'form': 'number', 'value': 120}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['習', '好', '學', '讀', '書']}, 'claim': {'form': 'number', 'value': 25}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['理', '讀', '學', '樂']}, 'claim': {'form': 'number', 'value': 24}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['數', '讀', '樂']}, 'claim': {'form': 'number', 'value': 6}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['學', '數', '習', '理', '好']}, 'claim': {'form': 'number', 'value': 120}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['習', '樂', '數', '好', '理']}, 'claim': {'form': 'number', 'value': 120}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['書', '樂', '數', '理']}, 'claim': {'form': 'number', 'value': 24}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['書', '學', '樂', '數']}, 'claim': {'form': 'number', 'value': 48}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['好', '學', '書']}, 'claim': {'form': 'number', 'value': 12}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['學', '讀', '數']}, 'claim': {'form': 'number', 'value': 9}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['好', '學', '數']}, 'claim': {'form': 'number', 'value': 27}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['樂', '書', '學']}, 'claim': {'form': 'number', 'value': 9}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['理', '學', '數', '樂']}, 'claim': {'form': 'number', 'value': 24}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['習', '書', '理', '樂', '學']}, 'claim': {'form': 'number', 'value': 120}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['理', '書', '習', '數']}, 'claim': {'form': 'number', 'value': 24}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['習', '學', '理', '書']}, 'claim': {'form': 'number', 'value': 28}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['好', '習', '書']}, 'claim': {'form': 'number', 'value': 6}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['數', '讀', '學', '理']}, 'claim': {'form': 'number', 'value': 8}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['書', '數', '樂', '學']}, 'claim': {'form': 'number', 'value': 24}}]}}, 'problem_type_id': 'counting_claim', 'required_capabilities': ['counting_claim'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['讀', '書', '好']}, 'claim': {'form': 'number', 'value': 6}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['讀', '書', '理', '學', '樂']}, 'claim': {'form': 'number', 'value': 120}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['習', '好', '學', '讀', '書']}, 'claim': {'form': 'number', 'value': 25}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['理', '讀', '學', '樂']}, 'claim': {'form': 'number', 'value': 24}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['數', '讀', '樂']}, 'claim': {'form': 'number', 'value': 6}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['學', '數', '習', '理', '好']}, 'claim': {'form': 'number', 'value': 120}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['習', '樂', '數', '好', '理']}, 'claim': {'form': 'number', 'value': 120}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['書', '樂', '數', '理']}, 'claim': {'form': 'number', 'value': 24}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['書', '學', '樂', '數']}, 'claim': {'form': 'number', 'value': 48}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['好', '學', '書']}, 'claim': {'form': 'number', 'value': 12}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['學', '讀', '數']}, 'claim': {'form': 'number', 'value': 9}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['好', '學', '數']}, 'claim': {'form': 'number', 'value': 27}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['樂', '書', '學']}, 'claim': {'form': 'number', 'value': 9}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['理', '學', '數', '樂']}, 'claim': {'form': 'number', 'value': 24}}, {'setting': {'kind': 'arrangement', 'n': 5, 'chars': ['習', '書', '理', '樂', '學']}, 'claim': {'form': 'number', 'value': 120}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['理', '書', '習', '數']}, 'claim': {'form': 'number', 'value': 24}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['習', '學', '理', '書']}, 'claim': {'form': 'number', 'value': 28}}, {'setting': {'kind': 'arrangement', 'n': 3, 'chars': ['好', '習', '書']}, 'claim': {'form': 'number', 'value': 6}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['數', '讀', '學', '理']}, 'claim': {'form': 'number', 'value': 8}}, {'setting': {'kind': 'arrangement', 'n': 4, 'chars': ['書', '數', '樂', '學']}, 'claim': {'form': 'number', 'value': 24}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_LinearPermutation', 'fixed_domain_key': 'discrete.permutations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['counting_claim'], 'matched_capabilities': ['counting_claim'], 'selected_operation': 'counting_claim', 'registry_revision': 'promoted-ebcd5e40b80e', 'domain_module': 'core.domain.promoted.permutations.permutations_domain', 'entrypoint': 'build_permutations_matrix', 'allowed_operations': ['adjacent_separated', 'counting_claim', 'distinct_digit_numbers', 'ends_and_block', 'ends_from_group', 'fixed_order_insertion', 'relative_order_three', 'restricted_assignment', 'selected_arrangement', 'two_group_line'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_LinearPermutation'}), seed)
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
