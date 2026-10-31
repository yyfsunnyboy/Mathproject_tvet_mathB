from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "event_relation"
TEXTBOOK_EXAMPLE_ID = 12856
DEFAULT_COMPONENT_ID = "src_12856" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Event"
FIXED_DOMAIN_KEY = "discrete.classical_probability"
DOMAIN_OPERATION = "event_relation"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.classical_probability', 'required_capabilities': ['event_relation'], 'domain_operation': 'event_relation', 'problem_type_id': 'event_relation', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'model': 'coin', 'n': 2, 'a': {'kind': 'exactly_heads', 'k': 1}, 'b': {'kind': 'exactly_heads', 'k': 0}}, {'model': 'coin', 'n': 3, 'a': {'kind': 'at_least_heads', 'k': 1}, 'b': {'kind': 'exactly_heads', 'k': 1}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'at_least_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 3}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'at_least_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 1}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'at_least_heads', 'k': 4}, 'b': {'kind': 'at_least_heads', 'k': 2}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'exactly_heads', 'k': 4}, 'b': {'kind': 'at_least_heads', 'k': 1}}, {'model': 'coin', 'n': 2, 'a': {'kind': 'at_least_heads', 'k': 1}, 'b': {'kind': 'at_least_heads', 'k': 2}}, {'model': 'coin', 'n': 2, 'a': {'kind': 'exactly_heads', 'k': 1}, 'b': {'kind': 'at_least_heads', 'k': 1}}, {'model': 'coin', 'n': 2, 'a': {'kind': 'exactly_heads', 'k': 0}, 'b': {'kind': 'at_least_heads', 'k': 1}}, {'model': 'coin', 'n': 2, 'a': {'kind': 'exactly_heads', 'k': 2}, 'b': {'kind': 'at_least_heads', 'k': 2}}, {'model': 'coin', 'n': 3, 'a': {'kind': 'at_least_heads', 'k': 3}, 'b': {'kind': 'at_least_heads', 'k': 2}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'at_least_heads', 'k': 2}, 'b': {'kind': 'at_least_heads', 'k': 1}}, {'model': 'coin', 'n': 3, 'a': {'kind': 'exactly_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 2}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'at_least_heads', 'k': 4}, 'b': {'kind': 'exactly_heads', 'k': 2}}, {'model': 'coin', 'n': 3, 'a': {'kind': 'exactly_heads', 'k': 0}, 'b': {'kind': 'exactly_heads', 'k': 1}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'exactly_heads', 'k': 0}, 'b': {'kind': 'at_least_heads', 'k': 3}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'exactly_heads', 'k': 5}, 'b': {'kind': 'at_least_heads', 'k': 3}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'exactly_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 0}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'exactly_heads', 'k': 4}, 'b': {'kind': 'exactly_heads', 'k': 5}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'at_least_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 4}}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.classical_probability', 'required_capabilities': ['event_relation'], 'domain_operation': 'event_relation', 'problem_type_id': 'event_relation', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'model': 'coin', 'n': 2, 'a': {'kind': 'exactly_heads', 'k': 1}, 'b': {'kind': 'exactly_heads', 'k': 0}}, {'model': 'coin', 'n': 3, 'a': {'kind': 'at_least_heads', 'k': 1}, 'b': {'kind': 'exactly_heads', 'k': 1}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'at_least_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 3}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'at_least_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 1}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'at_least_heads', 'k': 4}, 'b': {'kind': 'at_least_heads', 'k': 2}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'exactly_heads', 'k': 4}, 'b': {'kind': 'at_least_heads', 'k': 1}}, {'model': 'coin', 'n': 2, 'a': {'kind': 'at_least_heads', 'k': 1}, 'b': {'kind': 'at_least_heads', 'k': 2}}, {'model': 'coin', 'n': 2, 'a': {'kind': 'exactly_heads', 'k': 1}, 'b': {'kind': 'at_least_heads', 'k': 1}}, {'model': 'coin', 'n': 2, 'a': {'kind': 'exactly_heads', 'k': 0}, 'b': {'kind': 'at_least_heads', 'k': 1}}, {'model': 'coin', 'n': 2, 'a': {'kind': 'exactly_heads', 'k': 2}, 'b': {'kind': 'at_least_heads', 'k': 2}}, {'model': 'coin', 'n': 3, 'a': {'kind': 'at_least_heads', 'k': 3}, 'b': {'kind': 'at_least_heads', 'k': 2}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'at_least_heads', 'k': 2}, 'b': {'kind': 'at_least_heads', 'k': 1}}, {'model': 'coin', 'n': 3, 'a': {'kind': 'exactly_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 2}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'at_least_heads', 'k': 4}, 'b': {'kind': 'exactly_heads', 'k': 2}}, {'model': 'coin', 'n': 3, 'a': {'kind': 'exactly_heads', 'k': 0}, 'b': {'kind': 'exactly_heads', 'k': 1}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'exactly_heads', 'k': 0}, 'b': {'kind': 'at_least_heads', 'k': 3}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'exactly_heads', 'k': 5}, 'b': {'kind': 'at_least_heads', 'k': 3}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'exactly_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 0}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'exactly_heads', 'k': 4}, 'b': {'kind': 'exactly_heads', 'k': 5}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'at_least_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 4}}]}}, 'problem_type_id': 'event_relation', 'required_capabilities': ['event_relation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'model': 'coin', 'n': 2, 'a': {'kind': 'exactly_heads', 'k': 1}, 'b': {'kind': 'exactly_heads', 'k': 0}}, {'model': 'coin', 'n': 3, 'a': {'kind': 'at_least_heads', 'k': 1}, 'b': {'kind': 'exactly_heads', 'k': 1}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'at_least_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 3}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'at_least_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 1}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'at_least_heads', 'k': 4}, 'b': {'kind': 'at_least_heads', 'k': 2}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'exactly_heads', 'k': 4}, 'b': {'kind': 'at_least_heads', 'k': 1}}, {'model': 'coin', 'n': 2, 'a': {'kind': 'at_least_heads', 'k': 1}, 'b': {'kind': 'at_least_heads', 'k': 2}}, {'model': 'coin', 'n': 2, 'a': {'kind': 'exactly_heads', 'k': 1}, 'b': {'kind': 'at_least_heads', 'k': 1}}, {'model': 'coin', 'n': 2, 'a': {'kind': 'exactly_heads', 'k': 0}, 'b': {'kind': 'at_least_heads', 'k': 1}}, {'model': 'coin', 'n': 2, 'a': {'kind': 'exactly_heads', 'k': 2}, 'b': {'kind': 'at_least_heads', 'k': 2}}, {'model': 'coin', 'n': 3, 'a': {'kind': 'at_least_heads', 'k': 3}, 'b': {'kind': 'at_least_heads', 'k': 2}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'at_least_heads', 'k': 2}, 'b': {'kind': 'at_least_heads', 'k': 1}}, {'model': 'coin', 'n': 3, 'a': {'kind': 'exactly_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 2}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'at_least_heads', 'k': 4}, 'b': {'kind': 'exactly_heads', 'k': 2}}, {'model': 'coin', 'n': 3, 'a': {'kind': 'exactly_heads', 'k': 0}, 'b': {'kind': 'exactly_heads', 'k': 1}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'exactly_heads', 'k': 0}, 'b': {'kind': 'at_least_heads', 'k': 3}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'exactly_heads', 'k': 5}, 'b': {'kind': 'at_least_heads', 'k': 3}}, {'model': 'coin', 'n': 4, 'a': {'kind': 'exactly_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 0}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'exactly_heads', 'k': 4}, 'b': {'kind': 'exactly_heads', 'k': 5}}, {'model': 'coin', 'n': 5, 'a': {'kind': 'at_least_heads', 'k': 3}, 'b': {'kind': 'exactly_heads', 'k': 4}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Event', 'fixed_domain_key': 'discrete.classical_probability', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['event_relation'], 'matched_capabilities': ['event_relation'], 'selected_operation': 'event_relation', 'registry_revision': 'promoted-118ac6ac1753', 'domain_module': 'core.domain.promoted.classical_probability.classical_probability_domain', 'entrypoint': 'build_classical_probability_matrix', 'allowed_operations': ['dice_event_sets', 'event_relation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Event'}), seed)
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
