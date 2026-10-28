from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "restricted_assignment"
TEXTBOOK_EXAMPLE_ID = 12778
DEFAULT_COMPONENT_ID = "src_12778" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_LinearPermutation"
FIXED_DOMAIN_KEY = "discrete.permutations"
DOMAIN_OPERATION = "restricted_assignment"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['restricted_assignment'], 'domain_operation': 'restricted_assignment', 'problem_type_id': 'restricted_assignment', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 0], [1, 3]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 0], [1, 2]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 1], [1, 3]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 6, 'k': 4, 'forbidden': [[0, 1], [1, 3]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 5, 'k': 3, 'forbidden': [[0, 2], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 8, 'k': 3, 'forbidden': [[0, 1], [1, 2]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 9, 'k': 4, 'forbidden': [[0, 1], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 8, 'k': 4, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 8, 'k': 3, 'forbidden': [[0, 2], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 0], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 8, 'k': 3, 'forbidden': [[0, 1], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 5, 'k': 3, 'forbidden': [[0, 1], [1, 2]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 9, 'k': 3, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 4, 'k': 3, 'forbidden': [[0, 2], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 5, 'k': 4, 'forbidden': [[0, 1], [1, 3]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 6, 'k': 3, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 9, 'k': 4, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 6, 'k': 4, 'forbidden': [[0, 3], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 9, 'k': 4, 'forbidden': [[0, 3], [1, 1]], 'names': ['甲', '乙']}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['restricted_assignment'], 'domain_operation': 'restricted_assignment', 'problem_type_id': 'restricted_assignment', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 0], [1, 3]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 0], [1, 2]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 1], [1, 3]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 6, 'k': 4, 'forbidden': [[0, 1], [1, 3]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 5, 'k': 3, 'forbidden': [[0, 2], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 8, 'k': 3, 'forbidden': [[0, 1], [1, 2]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 9, 'k': 4, 'forbidden': [[0, 1], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 8, 'k': 4, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 8, 'k': 3, 'forbidden': [[0, 2], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 0], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 8, 'k': 3, 'forbidden': [[0, 1], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 5, 'k': 3, 'forbidden': [[0, 1], [1, 2]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 9, 'k': 3, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 4, 'k': 3, 'forbidden': [[0, 2], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 5, 'k': 4, 'forbidden': [[0, 1], [1, 3]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 6, 'k': 3, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 9, 'k': 4, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 6, 'k': 4, 'forbidden': [[0, 3], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 9, 'k': 4, 'forbidden': [[0, 3], [1, 1]], 'names': ['甲', '乙']}]}}, 'problem_type_id': 'restricted_assignment', 'required_capabilities': ['restricted_assignment'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 0], [1, 3]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 0], [1, 2]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 1], [1, 3]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 6, 'k': 4, 'forbidden': [[0, 1], [1, 3]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 5, 'k': 3, 'forbidden': [[0, 2], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 8, 'k': 3, 'forbidden': [[0, 1], [1, 2]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 9, 'k': 4, 'forbidden': [[0, 1], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 8, 'k': 4, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 8, 'k': 3, 'forbidden': [[0, 2], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 0], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 7, 'k': 4, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 8, 'k': 3, 'forbidden': [[0, 1], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 5, 'k': 3, 'forbidden': [[0, 1], [1, 2]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 9, 'k': 3, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 4, 'k': 3, 'forbidden': [[0, 2], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 5, 'k': 4, 'forbidden': [[0, 1], [1, 3]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 6, 'k': 3, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 9, 'k': 4, 'forbidden': [[0, 2], [1, 1]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 6, 'k': 4, 'forbidden': [[0, 3], [1, 0]], 'names': ['甲', '乙']}, {'style': 'universities', 'n': 9, 'k': 4, 'forbidden': [[0, 3], [1, 1]], 'names': ['甲', '乙']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_LinearPermutation', 'fixed_domain_key': 'discrete.permutations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['restricted_assignment'], 'matched_capabilities': ['restricted_assignment'], 'selected_operation': 'restricted_assignment', 'registry_revision': 'promoted-ebcd5e40b80e', 'domain_module': 'core.domain.promoted.permutations.permutations_domain', 'entrypoint': 'build_permutations_matrix', 'allowed_operations': ['adjacent_separated', 'counting_claim', 'distinct_digit_numbers', 'ends_and_block', 'ends_from_group', 'fixed_order_insertion', 'relative_order_three', 'restricted_assignment', 'selected_arrangement', 'two_group_line'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_LinearPermutation'}), seed)
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
