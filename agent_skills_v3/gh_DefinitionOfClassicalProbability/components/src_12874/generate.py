from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "classical_claim"
TEXTBOOK_EXAMPLE_ID = 12874
DEFAULT_COMPONENT_ID = "src_12874" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_DefinitionOfClassicalProbability"
FIXED_DOMAIN_KEY = "discrete.classical_probability"
DOMAIN_OPERATION = "classical_claim"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.classical_probability', 'required_capabilities': ['classical_claim'], 'domain_operation': 'classical_claim', 'problem_type_id': 'classical_claim', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'style': 'at_least_one_six', 'stated_miss': 25}, {'style': 'at_least_one_six', 'stated_miss': 32}, {'style': 'at_least_one_six', 'stated_miss': 26}, {'style': 'at_least_one_six', 'stated_miss': 15}, {'style': 'at_least_one_six', 'stated_miss': 34}, {'style': 'at_least_one_six', 'stated_miss': 14}, {'style': 'at_least_one_six', 'stated_miss': 29}, {'style': 'at_least_one_six', 'stated_miss': 19}, {'style': 'at_least_one_six', 'stated_miss': 22}, {'style': 'at_least_one_six', 'stated_miss': 16}, {'style': 'at_least_one_six', 'stated_miss': 21}, {'style': 'at_least_one_six', 'stated_miss': 24}, {'style': 'at_least_one_six', 'stated_miss': 30}, {'style': 'at_least_one_six', 'stated_miss': 18}, {'style': 'at_least_one_six', 'stated_miss': 11}, {'style': 'at_least_one_six', 'stated_miss': 1}, {'style': 'at_least_one_six', 'stated_miss': 7}, {'style': 'at_least_one_six', 'stated_miss': 35}, {'style': 'at_least_one_six', 'stated_miss': 2}, {'style': 'at_least_one_six', 'stated_miss': 12}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.classical_probability', 'required_capabilities': ['classical_claim'], 'domain_operation': 'classical_claim', 'problem_type_id': 'classical_claim', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'style': 'at_least_one_six', 'stated_miss': 25}, {'style': 'at_least_one_six', 'stated_miss': 32}, {'style': 'at_least_one_six', 'stated_miss': 26}, {'style': 'at_least_one_six', 'stated_miss': 15}, {'style': 'at_least_one_six', 'stated_miss': 34}, {'style': 'at_least_one_six', 'stated_miss': 14}, {'style': 'at_least_one_six', 'stated_miss': 29}, {'style': 'at_least_one_six', 'stated_miss': 19}, {'style': 'at_least_one_six', 'stated_miss': 22}, {'style': 'at_least_one_six', 'stated_miss': 16}, {'style': 'at_least_one_six', 'stated_miss': 21}, {'style': 'at_least_one_six', 'stated_miss': 24}, {'style': 'at_least_one_six', 'stated_miss': 30}, {'style': 'at_least_one_six', 'stated_miss': 18}, {'style': 'at_least_one_six', 'stated_miss': 11}, {'style': 'at_least_one_six', 'stated_miss': 1}, {'style': 'at_least_one_six', 'stated_miss': 7}, {'style': 'at_least_one_six', 'stated_miss': 35}, {'style': 'at_least_one_six', 'stated_miss': 2}, {'style': 'at_least_one_six', 'stated_miss': 12}]}}, 'problem_type_id': 'classical_claim', 'required_capabilities': ['classical_claim'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'style': 'at_least_one_six', 'stated_miss': 25}, {'style': 'at_least_one_six', 'stated_miss': 32}, {'style': 'at_least_one_six', 'stated_miss': 26}, {'style': 'at_least_one_six', 'stated_miss': 15}, {'style': 'at_least_one_six', 'stated_miss': 34}, {'style': 'at_least_one_six', 'stated_miss': 14}, {'style': 'at_least_one_six', 'stated_miss': 29}, {'style': 'at_least_one_six', 'stated_miss': 19}, {'style': 'at_least_one_six', 'stated_miss': 22}, {'style': 'at_least_one_six', 'stated_miss': 16}, {'style': 'at_least_one_six', 'stated_miss': 21}, {'style': 'at_least_one_six', 'stated_miss': 24}, {'style': 'at_least_one_six', 'stated_miss': 30}, {'style': 'at_least_one_six', 'stated_miss': 18}, {'style': 'at_least_one_six', 'stated_miss': 11}, {'style': 'at_least_one_six', 'stated_miss': 1}, {'style': 'at_least_one_six', 'stated_miss': 7}, {'style': 'at_least_one_six', 'stated_miss': 35}, {'style': 'at_least_one_six', 'stated_miss': 2}, {'style': 'at_least_one_six', 'stated_miss': 12}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_DefinitionOfClassicalProbability', 'fixed_domain_key': 'discrete.classical_probability', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['classical_claim'], 'matched_capabilities': ['classical_claim'], 'selected_operation': 'classical_claim', 'registry_revision': 'promoted-118ac6ac1753', 'domain_module': 'core.domain.promoted.classical_probability.classical_probability_domain', 'entrypoint': 'build_classical_probability_matrix', 'allowed_operations': ['classical_claim', 'coin_count_probability', 'dice_count_probability', 'password_guess', 'replacement_count_probability', 'solve_urn_count', 'uniform_draw_probability', 'urn_draw_probability'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_DefinitionOfClassicalProbability'}), seed)
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
