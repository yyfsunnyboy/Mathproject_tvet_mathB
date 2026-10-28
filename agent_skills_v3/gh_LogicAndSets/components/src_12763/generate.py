from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "proposition_truth"
TEXTBOOK_EXAMPLE_ID = 12763
DEFAULT_COMPONENT_ID = "src_12763" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_LogicAndSets"
FIXED_DOMAIN_KEY = "discrete.sets_counting"
DOMAIN_OPERATION = "proposition_truth"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.sets_counting', 'required_capabilities': ['proposition_truth'], 'domain_operation': 'proposition_truth', 'problem_type_id': 'proposition_truth', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'atoms': [{'kind': 'compare', 'a': 5, 'op': '>', 'b': 8}, {'kind': 'compare', 'a': 5, 'op': '<', 'b': 7}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 38, 'prop': 'multiple_of', 'k': 4}, {'kind': 'compare', 'a': 3, 'op': '<', 'b': 8}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 55, 'prop': 'multiple_of', 'k': 4}, {'kind': 'prop', 'n': 18, 'prop': 'multiple_of', 'k': 7}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 46, 'prop': 'multiple_of', 'k': 7}, {'kind': 'compare', 'a': 3, 'op': '>', 'b': 7}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 4, 'prop': 'odd'}, {'kind': 'compare', 'a': 5, 'op': '<', 'b': 1}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 39, 'prop': 'multiple_of', 'k': 6}, {'kind': 'prop', 'n': 7, 'prop': 'prime'}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 33, 'prop': 'odd'}, {'kind': 'prop', 'n': 37, 'prop': 'prime'}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 18, 'prop': 'even'}, {'kind': 'compare', 'a': 11, 'op': '>', 'b': 4}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 30, 'prop': 'odd'}, {'kind': 'compare', 'a': 3, 'op': '>', 'b': 4}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 15, 'prop': 'multiple_of', 'k': 4}, {'kind': 'compare', 'a': 3, 'op': '<', 'b': 6}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 33, 'prop': 'multiple_of', 'k': 6}, {'kind': 'compare', 'a': 5, 'op': '>', 'b': 9}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 20, 'prop': 'prime'}, {'kind': 'prop', 'n': 32, 'prop': 'odd'}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 46, 'prop': 'multiple_of', 'k': 4}, {'kind': 'compare', 'a': 8, 'op': '>', 'b': 11}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 15, 'prop': 'even'}, {'kind': 'prop', 'n': 26, 'prop': 'prime'}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 34, 'prop': 'odd'}, {'kind': 'prop', 'n': 31, 'prop': 'multiple_of', 'k': 4}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'compare', 'a': 5, 'op': '<', 'b': 8}, {'kind': 'compare', 'a': 2, 'op': '<', 'b': 11}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'compare', 'a': 1, 'op': '<', 'b': 11}, {'kind': 'prop', 'n': 16, 'prop': 'prime'}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'compare', 'a': 5, 'op': '<', 'b': 8}, {'kind': 'compare', 'a': 2, 'op': '>', 'b': 7}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 38, 'prop': 'prime'}, {'kind': 'prop', 'n': 27, 'prop': 'multiple_of', 'k': 4}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 36, 'prop': 'prime'}, {'kind': 'compare', 'a': 4, 'op': '<', 'b': 1}], 'options': [['or', 0, 1]], 'mode': 'truth'}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.sets_counting', 'required_capabilities': ['proposition_truth'], 'domain_operation': 'proposition_truth', 'problem_type_id': 'proposition_truth', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'atoms': [{'kind': 'compare', 'a': 5, 'op': '>', 'b': 8}, {'kind': 'compare', 'a': 5, 'op': '<', 'b': 7}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 38, 'prop': 'multiple_of', 'k': 4}, {'kind': 'compare', 'a': 3, 'op': '<', 'b': 8}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 55, 'prop': 'multiple_of', 'k': 4}, {'kind': 'prop', 'n': 18, 'prop': 'multiple_of', 'k': 7}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 46, 'prop': 'multiple_of', 'k': 7}, {'kind': 'compare', 'a': 3, 'op': '>', 'b': 7}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 4, 'prop': 'odd'}, {'kind': 'compare', 'a': 5, 'op': '<', 'b': 1}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 39, 'prop': 'multiple_of', 'k': 6}, {'kind': 'prop', 'n': 7, 'prop': 'prime'}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 33, 'prop': 'odd'}, {'kind': 'prop', 'n': 37, 'prop': 'prime'}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 18, 'prop': 'even'}, {'kind': 'compare', 'a': 11, 'op': '>', 'b': 4}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 30, 'prop': 'odd'}, {'kind': 'compare', 'a': 3, 'op': '>', 'b': 4}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 15, 'prop': 'multiple_of', 'k': 4}, {'kind': 'compare', 'a': 3, 'op': '<', 'b': 6}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 33, 'prop': 'multiple_of', 'k': 6}, {'kind': 'compare', 'a': 5, 'op': '>', 'b': 9}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 20, 'prop': 'prime'}, {'kind': 'prop', 'n': 32, 'prop': 'odd'}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 46, 'prop': 'multiple_of', 'k': 4}, {'kind': 'compare', 'a': 8, 'op': '>', 'b': 11}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 15, 'prop': 'even'}, {'kind': 'prop', 'n': 26, 'prop': 'prime'}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 34, 'prop': 'odd'}, {'kind': 'prop', 'n': 31, 'prop': 'multiple_of', 'k': 4}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'compare', 'a': 5, 'op': '<', 'b': 8}, {'kind': 'compare', 'a': 2, 'op': '<', 'b': 11}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'compare', 'a': 1, 'op': '<', 'b': 11}, {'kind': 'prop', 'n': 16, 'prop': 'prime'}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'compare', 'a': 5, 'op': '<', 'b': 8}, {'kind': 'compare', 'a': 2, 'op': '>', 'b': 7}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 38, 'prop': 'prime'}, {'kind': 'prop', 'n': 27, 'prop': 'multiple_of', 'k': 4}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 36, 'prop': 'prime'}, {'kind': 'compare', 'a': 4, 'op': '<', 'b': 1}], 'options': [['or', 0, 1]], 'mode': 'truth'}]}}, 'problem_type_id': 'proposition_truth', 'required_capabilities': ['proposition_truth'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'atoms': [{'kind': 'compare', 'a': 5, 'op': '>', 'b': 8}, {'kind': 'compare', 'a': 5, 'op': '<', 'b': 7}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 38, 'prop': 'multiple_of', 'k': 4}, {'kind': 'compare', 'a': 3, 'op': '<', 'b': 8}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 55, 'prop': 'multiple_of', 'k': 4}, {'kind': 'prop', 'n': 18, 'prop': 'multiple_of', 'k': 7}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 46, 'prop': 'multiple_of', 'k': 7}, {'kind': 'compare', 'a': 3, 'op': '>', 'b': 7}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 4, 'prop': 'odd'}, {'kind': 'compare', 'a': 5, 'op': '<', 'b': 1}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 39, 'prop': 'multiple_of', 'k': 6}, {'kind': 'prop', 'n': 7, 'prop': 'prime'}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 33, 'prop': 'odd'}, {'kind': 'prop', 'n': 37, 'prop': 'prime'}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 18, 'prop': 'even'}, {'kind': 'compare', 'a': 11, 'op': '>', 'b': 4}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 30, 'prop': 'odd'}, {'kind': 'compare', 'a': 3, 'op': '>', 'b': 4}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 15, 'prop': 'multiple_of', 'k': 4}, {'kind': 'compare', 'a': 3, 'op': '<', 'b': 6}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 33, 'prop': 'multiple_of', 'k': 6}, {'kind': 'compare', 'a': 5, 'op': '>', 'b': 9}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 20, 'prop': 'prime'}, {'kind': 'prop', 'n': 32, 'prop': 'odd'}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 46, 'prop': 'multiple_of', 'k': 4}, {'kind': 'compare', 'a': 8, 'op': '>', 'b': 11}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 15, 'prop': 'even'}, {'kind': 'prop', 'n': 26, 'prop': 'prime'}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 34, 'prop': 'odd'}, {'kind': 'prop', 'n': 31, 'prop': 'multiple_of', 'k': 4}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'compare', 'a': 5, 'op': '<', 'b': 8}, {'kind': 'compare', 'a': 2, 'op': '<', 'b': 11}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'compare', 'a': 1, 'op': '<', 'b': 11}, {'kind': 'prop', 'n': 16, 'prop': 'prime'}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'compare', 'a': 5, 'op': '<', 'b': 8}, {'kind': 'compare', 'a': 2, 'op': '>', 'b': 7}], 'options': [['or', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 38, 'prop': 'prime'}, {'kind': 'prop', 'n': 27, 'prop': 'multiple_of', 'k': 4}], 'options': [['and', 0, 1]], 'mode': 'truth'}, {'atoms': [{'kind': 'prop', 'n': 36, 'prop': 'prime'}, {'kind': 'compare', 'a': 4, 'op': '<', 'b': 1}], 'options': [['or', 0, 1]], 'mode': 'truth'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_LogicAndSets', 'fixed_domain_key': 'discrete.sets_counting', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['proposition_truth'], 'matched_capabilities': ['proposition_truth'], 'selected_operation': 'proposition_truth', 'registry_revision': 'promoted-61f56dc42350', 'domain_module': 'core.domain.promoted.counting_sets.counting_sets_domain', 'entrypoint': 'build_counting_sets_matrix', 'allowed_operations': ['condition_relation', 'equation_root_sets', 'finite_set_operations', 'implication_truth', 'interval_set_operations', 'proposition_truth'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_LogicAndSets'}), seed)
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
