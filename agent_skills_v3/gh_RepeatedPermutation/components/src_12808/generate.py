from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "counting_claim"
TEXTBOOK_EXAMPLE_ID = 12808
DEFAULT_COMPONENT_ID = "src_12808" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RepeatedPermutation"
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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['counting_claim'], 'domain_operation': 'counting_claim', 'problem_type_id': 'counting_claim', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'setting': {'kind': 'repeated', 'boxes': 3, 'items': 4}, 'claim': {'form': 'power', 'base': 4, 'exp': 3}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 3}, 'claim': {'form': 'power', 'base': 3, 'exp': 4}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 6}, 'claim': {'form': 'power', 'base': 4, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 3}, 'claim': {'form': 'power', 'base': 2, 'exp': 2}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 4}, 'claim': {'form': 'power', 'base': 2, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 6}, 'claim': {'form': 'power', 'base': 3, 'exp': 6}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 4}, 'claim': {'form': 'power', 'base': 4, 'exp': 4}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 3}, 'claim': {'form': 'power', 'base': 2, 'exp': 3}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 5}, 'claim': {'form': 'power', 'base': 2, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 3}, 'claim': {'form': 'power', 'base': 4, 'exp': 2}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 6}, 'claim': {'form': 'power', 'base': 4, 'exp': 6}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 4}, 'claim': {'form': 'power', 'base': 3, 'exp': 4}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 6}, 'claim': {'form': 'power', 'base': 2, 'exp': 6}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 3}, 'claim': {'form': 'power', 'base': 4, 'exp': 3}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 5}, 'claim': {'form': 'power', 'base': 4, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 5}, 'claim': {'form': 'power', 'base': 3, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 4}, 'claim': {'form': 'power', 'base': 3, 'exp': 3}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 6}, 'claim': {'form': 'power', 'base': 6, 'exp': 6}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 3}, 'claim': {'form': 'power', 'base': 4, 'exp': 4}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 4}, 'claim': {'form': 'power', 'base': 3, 'exp': 5}}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.permutations', 'required_capabilities': ['counting_claim'], 'domain_operation': 'counting_claim', 'problem_type_id': 'counting_claim', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'setting': {'kind': 'repeated', 'boxes': 3, 'items': 4}, 'claim': {'form': 'power', 'base': 4, 'exp': 3}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 3}, 'claim': {'form': 'power', 'base': 3, 'exp': 4}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 6}, 'claim': {'form': 'power', 'base': 4, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 3}, 'claim': {'form': 'power', 'base': 2, 'exp': 2}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 4}, 'claim': {'form': 'power', 'base': 2, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 6}, 'claim': {'form': 'power', 'base': 3, 'exp': 6}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 4}, 'claim': {'form': 'power', 'base': 4, 'exp': 4}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 3}, 'claim': {'form': 'power', 'base': 2, 'exp': 3}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 5}, 'claim': {'form': 'power', 'base': 2, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 3}, 'claim': {'form': 'power', 'base': 4, 'exp': 2}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 6}, 'claim': {'form': 'power', 'base': 4, 'exp': 6}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 4}, 'claim': {'form': 'power', 'base': 3, 'exp': 4}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 6}, 'claim': {'form': 'power', 'base': 2, 'exp': 6}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 3}, 'claim': {'form': 'power', 'base': 4, 'exp': 3}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 5}, 'claim': {'form': 'power', 'base': 4, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 5}, 'claim': {'form': 'power', 'base': 3, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 4}, 'claim': {'form': 'power', 'base': 3, 'exp': 3}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 6}, 'claim': {'form': 'power', 'base': 6, 'exp': 6}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 3}, 'claim': {'form': 'power', 'base': 4, 'exp': 4}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 4}, 'claim': {'form': 'power', 'base': 3, 'exp': 5}}]}}, 'problem_type_id': 'counting_claim', 'required_capabilities': ['counting_claim'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'setting': {'kind': 'repeated', 'boxes': 3, 'items': 4}, 'claim': {'form': 'power', 'base': 4, 'exp': 3}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 3}, 'claim': {'form': 'power', 'base': 3, 'exp': 4}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 6}, 'claim': {'form': 'power', 'base': 4, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 3}, 'claim': {'form': 'power', 'base': 2, 'exp': 2}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 4}, 'claim': {'form': 'power', 'base': 2, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 6}, 'claim': {'form': 'power', 'base': 3, 'exp': 6}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 4}, 'claim': {'form': 'power', 'base': 4, 'exp': 4}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 3}, 'claim': {'form': 'power', 'base': 2, 'exp': 3}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 5}, 'claim': {'form': 'power', 'base': 2, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 3}, 'claim': {'form': 'power', 'base': 4, 'exp': 2}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 6}, 'claim': {'form': 'power', 'base': 4, 'exp': 6}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 4}, 'claim': {'form': 'power', 'base': 3, 'exp': 4}}, {'setting': {'kind': 'repeated', 'boxes': 2, 'items': 6}, 'claim': {'form': 'power', 'base': 2, 'exp': 6}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 3}, 'claim': {'form': 'power', 'base': 4, 'exp': 3}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 5}, 'claim': {'form': 'power', 'base': 4, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 5}, 'claim': {'form': 'power', 'base': 3, 'exp': 5}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 4}, 'claim': {'form': 'power', 'base': 3, 'exp': 3}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 6}, 'claim': {'form': 'power', 'base': 6, 'exp': 6}}, {'setting': {'kind': 'repeated', 'boxes': 4, 'items': 3}, 'claim': {'form': 'power', 'base': 4, 'exp': 4}}, {'setting': {'kind': 'repeated', 'boxes': 3, 'items': 4}, 'claim': {'form': 'power', 'base': 3, 'exp': 5}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_RepeatedPermutation', 'fixed_domain_key': 'discrete.permutations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['counting_claim'], 'matched_capabilities': ['counting_claim'], 'selected_operation': 'counting_claim', 'registry_revision': 'promoted-ebcd5e40b80e', 'domain_module': 'core.domain.promoted.permutations.permutations_domain', 'entrypoint': 'build_permutations_matrix', 'allowed_operations': ['counting_claim', 'distribute_distinct', 'identical_arrangement'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_RepeatedPermutation'}), seed)
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
