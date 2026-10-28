from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "finite_set_operations"
TEXTBOOK_EXAMPLE_ID = 12748
DEFAULT_COMPONENT_ID = "src_12748" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_LogicAndSets"
FIXED_DOMAIN_KEY = "discrete.sets_counting"
DOMAIN_OPERATION = "finite_set_operations"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.sets_counting', 'required_capabilities': ['finite_set_operations'], 'domain_operation': 'finite_set_operations', 'problem_type_id': 'finite_set_operations', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'universe': [1, 2, 3, 4, 5], 'A': [1, 2, 3], 'B': [2, 3, 4], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [1, 2, 6, 8], 'B': [1, 3, 4, 6], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [5, 6, 7, 8], 'B': [2, 3, 4, 7, 8], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6], 'A': [1, 2, 4, 5, 6], 'B': [1, 3, 4, 5, 6], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'A': [4, 5, 8, 9], 'B': [2, 4, 6, 7], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'A': [3, 4, 7], 'B': [2, 3, 6, 7, 8], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [2, 3, 4], 'B': [4, 5, 6], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 3, 4], 'B': [1, 2, 4, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [1, 5, 8], 'B': [3, 4, 5, 7], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 2, 4, 5], 'B': [1, 4, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6], 'A': [1, 4, 5, 6], 'B': [1, 3, 4], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [1, 2, 3, 4, 6], 'B': [1, 2, 4], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6], 'A': [1, 2, 3, 6], 'B': [1, 2, 3, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'A': [1, 7, 8], 'B': [1, 2, 4, 8], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6], 'A': [1, 3, 4, 5, 6], 'B': [2, 3, 4, 5, 6], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 2, 4, 5], 'B': [1, 3, 4], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 2, 3], 'B': [2, 4, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 3, 4], 'B': [2, 3, 4, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [1, 2, 8], 'B': [2, 4, 7], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7], 'A': [3, 4, 5, 6], 'B': [2, 3, 5, 7], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.sets_counting', 'required_capabilities': ['finite_set_operations'], 'domain_operation': 'finite_set_operations', 'problem_type_id': 'finite_set_operations', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'universe': [1, 2, 3, 4, 5], 'A': [1, 2, 3], 'B': [2, 3, 4], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [1, 2, 6, 8], 'B': [1, 3, 4, 6], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [5, 6, 7, 8], 'B': [2, 3, 4, 7, 8], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6], 'A': [1, 2, 4, 5, 6], 'B': [1, 3, 4, 5, 6], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'A': [4, 5, 8, 9], 'B': [2, 4, 6, 7], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'A': [3, 4, 7], 'B': [2, 3, 6, 7, 8], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [2, 3, 4], 'B': [4, 5, 6], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 3, 4], 'B': [1, 2, 4, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [1, 5, 8], 'B': [3, 4, 5, 7], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 2, 4, 5], 'B': [1, 4, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6], 'A': [1, 4, 5, 6], 'B': [1, 3, 4], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [1, 2, 3, 4, 6], 'B': [1, 2, 4], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6], 'A': [1, 2, 3, 6], 'B': [1, 2, 3, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'A': [1, 7, 8], 'B': [1, 2, 4, 8], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6], 'A': [1, 3, 4, 5, 6], 'B': [2, 3, 4, 5, 6], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 2, 4, 5], 'B': [1, 3, 4], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 2, 3], 'B': [2, 4, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 3, 4], 'B': [2, 3, 4, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [1, 2, 8], 'B': [2, 4, 7], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7], 'A': [3, 4, 5, 6], 'B': [2, 3, 5, 7], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}]}}, 'problem_type_id': 'finite_set_operations', 'required_capabilities': ['finite_set_operations'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'universe': [1, 2, 3, 4, 5], 'A': [1, 2, 3], 'B': [2, 3, 4], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [1, 2, 6, 8], 'B': [1, 3, 4, 6], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [5, 6, 7, 8], 'B': [2, 3, 4, 7, 8], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6], 'A': [1, 2, 4, 5, 6], 'B': [1, 3, 4, 5, 6], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'A': [4, 5, 8, 9], 'B': [2, 4, 6, 7], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'A': [3, 4, 7], 'B': [2, 3, 6, 7, 8], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [2, 3, 4], 'B': [4, 5, 6], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 3, 4], 'B': [1, 2, 4, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [1, 5, 8], 'B': [3, 4, 5, 7], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 2, 4, 5], 'B': [1, 4, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6], 'A': [1, 4, 5, 6], 'B': [1, 3, 4], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [1, 2, 3, 4, 6], 'B': [1, 2, 4], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6], 'A': [1, 2, 3, 6], 'B': [1, 2, 3, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'A': [1, 7, 8], 'B': [1, 2, 4, 8], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6], 'A': [1, 3, 4, 5, 6], 'B': [2, 3, 4, 5, 6], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 2, 4, 5], 'B': [1, 3, 4], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 2, 3], 'B': [2, 4, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5], 'A': [1, 3, 4], 'B': [2, 3, 4, 5], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7, 8], 'A': [1, 2, 8], 'B': [2, 4, 7], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}, {'universe': [1, 2, 3, 4, 5, 6, 7], 'A': [3, 4, 5, 6], 'B': [2, 3, 5, 7], 'items': ['intersection', 'union', 'a_minus_b', 'a_complement']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_LogicAndSets', 'fixed_domain_key': 'discrete.sets_counting', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['finite_set_operations'], 'matched_capabilities': ['finite_set_operations'], 'selected_operation': 'finite_set_operations', 'registry_revision': 'promoted-61f56dc42350', 'domain_module': 'core.domain.promoted.counting_sets.counting_sets_domain', 'entrypoint': 'build_counting_sets_matrix', 'allowed_operations': ['condition_relation', 'equation_root_sets', 'finite_set_operations', 'implication_truth', 'interval_set_operations', 'proposition_truth'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_LogicAndSets'}), seed)
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
