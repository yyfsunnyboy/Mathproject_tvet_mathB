from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "true_false_stat"
TEXTBOOK_EXAMPLE_ID = 12933
DEFAULT_COMPONENT_ID = "src_12933" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_DataScalingAndShifting"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "true_false_stat"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['true_false_stat'], 'domain_operation': 'true_false_stat', 'problem_type_id': 'true_false_stat', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'claim': {'kind': 'scaled_sd_signed', 'a': -3, 'b': 2, 'stated_factor': '-3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 4, 'b': -8, 'stated_factor': '-4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -4, 'b': -4, 'stated_factor': '-4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 4, 'b': 1, 'stated_factor': '-4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 5, 'b': -1, 'stated_factor': '5'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -2, 'b': -7, 'stated_factor': '2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -2, 'b': 9, 'stated_factor': '-2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 3, 'b': 0, 'stated_factor': '-3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 2, 'b': 6, 'stated_factor': '-2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -4, 'b': 0, 'stated_factor': '4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 3, 'b': -2, 'stated_factor': '-3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 3, 'b': 9, 'stated_factor': '3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -3, 'b': -3, 'stated_factor': '3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 2, 'b': 4, 'stated_factor': '2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 3, 'b': -3, 'stated_factor': '-3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 5, 'b': 2, 'stated_factor': '5'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 2, 'b': 1, 'stated_factor': '-2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -4, 'b': 6, 'stated_factor': '4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -2, 'b': 4, 'stated_factor': '2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 2, 'b': 1, 'stated_factor': '2'}}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['true_false_stat'], 'domain_operation': 'true_false_stat', 'problem_type_id': 'true_false_stat', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'claim': {'kind': 'scaled_sd_signed', 'a': -3, 'b': 2, 'stated_factor': '-3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 4, 'b': -8, 'stated_factor': '-4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -4, 'b': -4, 'stated_factor': '-4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 4, 'b': 1, 'stated_factor': '-4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 5, 'b': -1, 'stated_factor': '5'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -2, 'b': -7, 'stated_factor': '2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -2, 'b': 9, 'stated_factor': '-2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 3, 'b': 0, 'stated_factor': '-3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 2, 'b': 6, 'stated_factor': '-2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -4, 'b': 0, 'stated_factor': '4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 3, 'b': -2, 'stated_factor': '-3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 3, 'b': 9, 'stated_factor': '3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -3, 'b': -3, 'stated_factor': '3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 2, 'b': 4, 'stated_factor': '2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 3, 'b': -3, 'stated_factor': '-3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 5, 'b': 2, 'stated_factor': '5'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 2, 'b': 1, 'stated_factor': '-2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -4, 'b': 6, 'stated_factor': '4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -2, 'b': 4, 'stated_factor': '2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 2, 'b': 1, 'stated_factor': '2'}}]}}, 'problem_type_id': 'true_false_stat', 'required_capabilities': ['true_false_stat'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'claim': {'kind': 'scaled_sd_signed', 'a': -3, 'b': 2, 'stated_factor': '-3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 4, 'b': -8, 'stated_factor': '-4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -4, 'b': -4, 'stated_factor': '-4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 4, 'b': 1, 'stated_factor': '-4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 5, 'b': -1, 'stated_factor': '5'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -2, 'b': -7, 'stated_factor': '2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -2, 'b': 9, 'stated_factor': '-2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 3, 'b': 0, 'stated_factor': '-3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 2, 'b': 6, 'stated_factor': '-2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -4, 'b': 0, 'stated_factor': '4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 3, 'b': -2, 'stated_factor': '-3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 3, 'b': 9, 'stated_factor': '3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -3, 'b': -3, 'stated_factor': '3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 2, 'b': 4, 'stated_factor': '2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 3, 'b': -3, 'stated_factor': '-3'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 5, 'b': 2, 'stated_factor': '5'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 2, 'b': 1, 'stated_factor': '-2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -4, 'b': 6, 'stated_factor': '4'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': -2, 'b': 4, 'stated_factor': '2'}}, {'claim': {'kind': 'scaled_sd_signed', 'a': 2, 'b': 1, 'stated_factor': '2'}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_DataScalingAndShifting', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['true_false_stat'], 'matched_capabilities': ['true_false_stat'], 'selected_operation': 'true_false_stat', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['linear_find_scale_sd', 'linear_mean_sd', 'monthly_mean_sd', 'standardize_scores', 'statement_selection', 'true_false_stat'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_DataScalingAndShifting'}), seed)
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
