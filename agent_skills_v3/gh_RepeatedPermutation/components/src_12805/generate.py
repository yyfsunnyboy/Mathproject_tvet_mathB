from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "distribute_distinct"
TEXTBOOK_EXAMPLE_ID = 12805
DEFAULT_COMPONENT_ID = "src_12805" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RepeatedPermutation"
FIXED_DOMAIN_KEY = "discrete.permutations"
DOMAIN_OPERATION = "distribute_distinct"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['distribute_distinct'], 'domain_operation': 'distribute_distinct', 'problem_type_id': 'distribute_distinct', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 4}, {'kind': 'first_at_least', 'items': 4, 'k': 1}, {'kind': 'first_exactly', 'items': 4, 'k': 1}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 6}, {'kind': 'first_at_least', 'items': 6, 'k': 1}, {'kind': 'first_exactly', 'items': 6, 'k': 1}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 3}, {'kind': 'first_at_least', 'items': 3, 'k': 2}, {'kind': 'first_exactly', 'items': 3, 'k': 2}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 6}, {'kind': 'first_at_least', 'items': 6, 'k': 2}, {'kind': 'first_exactly', 'items': 6, 'k': 2}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 6}, {'kind': 'first_at_least', 'items': 6, 'k': 1}, {'kind': 'first_exactly', 'items': 6, 'k': 1}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 5}, {'kind': 'first_at_least', 'items': 5, 'k': 2}, {'kind': 'first_exactly', 'items': 5, 'k': 2}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 5}, {'kind': 'first_at_least', 'items': 5, 'k': 2}, {'kind': 'first_exactly', 'items': 5, 'k': 2}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 5}, {'kind': 'first_at_least', 'items': 5, 'k': 1}, {'kind': 'first_exactly', 'items': 5, 'k': 1}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 3}, {'kind': 'first_at_least', 'items': 3, 'k': 2}, {'kind': 'first_exactly', 'items': 3, 'k': 2}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 3}, {'kind': 'first_at_least', 'items': 3, 'k': 1}, {'kind': 'first_exactly', 'items': 3, 'k': 1}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 4}, {'kind': 'first_at_least', 'items': 4, 'k': 2}, {'kind': 'first_exactly', 'items': 4, 'k': 2}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 3}, {'kind': 'first_at_least', 'items': 3, 'k': 1}, {'kind': 'first_exactly', 'items': 3, 'k': 1}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 5}, {'kind': 'first_at_least', 'items': 5, 'k': 1}, {'kind': 'first_exactly', 'items': 5, 'k': 1}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 4}, {'kind': 'first_at_least', 'items': 4, 'k': 1}, {'kind': 'first_exactly', 'items': 4, 'k': 1}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 6}, {'kind': 'first_at_least', 'items': 6, 'k': 2}, {'kind': 'first_exactly', 'items': 6, 'k': 2}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 4}, {'kind': 'first_at_least', 'items': 4, 'k': 2}, {'kind': 'first_exactly', 'items': 4, 'k': 2}]}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['distribute_distinct'], 'domain_operation': 'distribute_distinct', 'problem_type_id': 'distribute_distinct', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 4}, {'kind': 'first_at_least', 'items': 4, 'k': 1}, {'kind': 'first_exactly', 'items': 4, 'k': 1}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 6}, {'kind': 'first_at_least', 'items': 6, 'k': 1}, {'kind': 'first_exactly', 'items': 6, 'k': 1}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 3}, {'kind': 'first_at_least', 'items': 3, 'k': 2}, {'kind': 'first_exactly', 'items': 3, 'k': 2}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 6}, {'kind': 'first_at_least', 'items': 6, 'k': 2}, {'kind': 'first_exactly', 'items': 6, 'k': 2}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 6}, {'kind': 'first_at_least', 'items': 6, 'k': 1}, {'kind': 'first_exactly', 'items': 6, 'k': 1}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 5}, {'kind': 'first_at_least', 'items': 5, 'k': 2}, {'kind': 'first_exactly', 'items': 5, 'k': 2}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 5}, {'kind': 'first_at_least', 'items': 5, 'k': 2}, {'kind': 'first_exactly', 'items': 5, 'k': 2}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 5}, {'kind': 'first_at_least', 'items': 5, 'k': 1}, {'kind': 'first_exactly', 'items': 5, 'k': 1}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 3}, {'kind': 'first_at_least', 'items': 3, 'k': 2}, {'kind': 'first_exactly', 'items': 3, 'k': 2}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 3}, {'kind': 'first_at_least', 'items': 3, 'k': 1}, {'kind': 'first_exactly', 'items': 3, 'k': 1}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 4}, {'kind': 'first_at_least', 'items': 4, 'k': 2}, {'kind': 'first_exactly', 'items': 4, 'k': 2}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 3}, {'kind': 'first_at_least', 'items': 3, 'k': 1}, {'kind': 'first_exactly', 'items': 3, 'k': 1}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 5}, {'kind': 'first_at_least', 'items': 5, 'k': 1}, {'kind': 'first_exactly', 'items': 5, 'k': 1}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 4}, {'kind': 'first_at_least', 'items': 4, 'k': 1}, {'kind': 'first_exactly', 'items': 4, 'k': 1}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 6}, {'kind': 'first_at_least', 'items': 6, 'k': 2}, {'kind': 'first_exactly', 'items': 6, 'k': 2}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 4}, {'kind': 'first_at_least', 'items': 4, 'k': 2}, {'kind': 'first_exactly', 'items': 4, 'k': 2}]}]}}, 'problem_type_id': 'distribute_distinct', 'required_capabilities': ['distribute_distinct'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 4}, {'kind': 'first_at_least', 'items': 4, 'k': 1}, {'kind': 'first_exactly', 'items': 4, 'k': 1}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 6}, {'kind': 'first_at_least', 'items': 6, 'k': 1}, {'kind': 'first_exactly', 'items': 6, 'k': 1}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 3}, {'kind': 'first_at_least', 'items': 3, 'k': 2}, {'kind': 'first_exactly', 'items': 3, 'k': 2}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 6}, {'kind': 'first_at_least', 'items': 6, 'k': 2}, {'kind': 'first_exactly', 'items': 6, 'k': 2}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 6}, {'kind': 'first_at_least', 'items': 6, 'k': 1}, {'kind': 'first_exactly', 'items': 6, 'k': 1}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 5}, {'kind': 'first_at_least', 'items': 5, 'k': 2}, {'kind': 'first_exactly', 'items': 5, 'k': 2}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 5}, {'kind': 'first_at_least', 'items': 5, 'k': 2}, {'kind': 'first_exactly', 'items': 5, 'k': 2}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 5}, {'kind': 'first_at_least', 'items': 5, 'k': 1}, {'kind': 'first_exactly', 'items': 5, 'k': 1}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 3}, {'kind': 'first_at_least', 'items': 3, 'k': 2}, {'kind': 'first_exactly', 'items': 3, 'k': 2}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 3}, {'kind': 'first_at_least', 'items': 3, 'k': 1}, {'kind': 'first_exactly', 'items': 3, 'k': 1}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 4}, {'kind': 'first_at_least', 'items': 4, 'k': 2}, {'kind': 'first_exactly', 'items': 4, 'k': 2}]}, {'style': 'books', 'boxes': 3, 'asks': [{'kind': 'any', 'items': 3}, {'kind': 'first_at_least', 'items': 3, 'k': 1}, {'kind': 'first_exactly', 'items': 3, 'k': 1}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 5}, {'kind': 'first_at_least', 'items': 5, 'k': 1}, {'kind': 'first_exactly', 'items': 5, 'k': 1}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 4}, {'kind': 'first_at_least', 'items': 4, 'k': 1}, {'kind': 'first_exactly', 'items': 4, 'k': 1}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 6}, {'kind': 'first_at_least', 'items': 6, 'k': 2}, {'kind': 'first_exactly', 'items': 6, 'k': 2}]}, {'style': 'books', 'boxes': 4, 'asks': [{'kind': 'any', 'items': 4}, {'kind': 'first_at_least', 'items': 4, 'k': 2}, {'kind': 'first_exactly', 'items': 4, 'k': 2}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_RepeatedPermutation', 'fixed_domain_key': 'discrete.permutations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['distribute_distinct'], 'matched_capabilities': ['distribute_distinct'], 'selected_operation': 'distribute_distinct', 'registry_revision': 'promoted-ebcd5e40b80e', 'domain_module': 'core.domain.promoted.permutations.permutations_domain', 'entrypoint': 'build_permutations_matrix', 'allowed_operations': ['counting_claim', 'distribute_distinct', 'identical_arrangement'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_RepeatedPermutation'}), seed)
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
