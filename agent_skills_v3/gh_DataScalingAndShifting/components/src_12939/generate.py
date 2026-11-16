from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "linear_find_scale_sd"
TEXTBOOK_EXAMPLE_ID = 12939
DEFAULT_COMPONENT_ID = "src_12939" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_DataScalingAndShifting"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "linear_find_scale_sd"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['linear_find_scale_sd'], 'domain_operation': 'linear_find_scale_sd', 'problem_type_id': 'linear_find_scale_sd', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'old_mean': 42, 'old_sd': 12, 'old_max': 72, 'new_mean': 60, 'new_max': 95}, {'old_mean': 49, 'old_sd': 10, 'old_max': 79, 'new_mean': '265/4', 'new_max': '415/4'}, {'old_mean': 48, 'old_sd': 8, 'old_max': 85, 'new_mean': '79', 'new_max': '385/3'}, {'old_mean': 30, 'old_sd': 10, 'old_max': 50, 'new_mean': '61', 'new_max': '91'}, {'old_mean': 47, 'old_sd': 12, 'old_max': 86, 'new_mean': '171/2', 'new_max': '144'}, {'old_mean': 35, 'old_sd': 12, 'old_max': 72, 'new_mean': '215/4', 'new_max': '100'}, {'old_mean': 35, 'old_sd': 10, 'old_max': 75, 'new_mean': '173/3', 'new_max': '111'}, {'old_mean': 35, 'old_sd': 8, 'old_max': 63, 'new_mean': '121/2', 'new_max': '205/2'}, {'old_mean': 32, 'old_sd': 8, 'old_max': 59, 'new_mean': '62', 'new_max': '205/2'}, {'old_mean': 31, 'old_sd': 10, 'old_max': 64, 'new_mean': '129/2', 'new_max': '114'}, {'old_mean': 37, 'old_sd': 10, 'old_max': 74, 'new_mean': '172/3', 'new_max': '320/3'}, {'old_mean': 38, 'old_sd': 10, 'old_max': 71, 'new_mean': '127/2', 'new_max': '419/4'}, {'old_mean': 36, 'old_sd': 10, 'old_max': 70, 'new_mean': '66', 'new_max': '334/3'}, {'old_mean': 32, 'old_sd': 12, 'old_max': 57, 'new_mean': '176/3', 'new_max': '92'}, {'old_mean': 36, 'old_sd': 8, 'old_max': 75, 'new_mean': '68', 'new_max': '253/2'}, {'old_mean': 41, 'old_sd': 8, 'old_max': 74, 'new_mean': '157/2', 'new_max': '128'}, {'old_mean': 49, 'old_sd': 10, 'old_max': 81, 'new_mean': '247/3', 'new_max': '125'}, {'old_mean': 34, 'old_sd': 12, 'old_max': 63, 'new_mean': '163/3', 'new_max': '93'}, {'old_mean': 34, 'old_sd': 8, 'old_max': 65, 'new_mean': '121/2', 'new_max': '397/4'}, {'old_mean': 31, 'old_sd': 12, 'old_max': 53, 'new_mean': '157/3', 'new_max': '245/3'}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['linear_find_scale_sd'], 'domain_operation': 'linear_find_scale_sd', 'problem_type_id': 'linear_find_scale_sd', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'old_mean': 42, 'old_sd': 12, 'old_max': 72, 'new_mean': 60, 'new_max': 95}, {'old_mean': 49, 'old_sd': 10, 'old_max': 79, 'new_mean': '265/4', 'new_max': '415/4'}, {'old_mean': 48, 'old_sd': 8, 'old_max': 85, 'new_mean': '79', 'new_max': '385/3'}, {'old_mean': 30, 'old_sd': 10, 'old_max': 50, 'new_mean': '61', 'new_max': '91'}, {'old_mean': 47, 'old_sd': 12, 'old_max': 86, 'new_mean': '171/2', 'new_max': '144'}, {'old_mean': 35, 'old_sd': 12, 'old_max': 72, 'new_mean': '215/4', 'new_max': '100'}, {'old_mean': 35, 'old_sd': 10, 'old_max': 75, 'new_mean': '173/3', 'new_max': '111'}, {'old_mean': 35, 'old_sd': 8, 'old_max': 63, 'new_mean': '121/2', 'new_max': '205/2'}, {'old_mean': 32, 'old_sd': 8, 'old_max': 59, 'new_mean': '62', 'new_max': '205/2'}, {'old_mean': 31, 'old_sd': 10, 'old_max': 64, 'new_mean': '129/2', 'new_max': '114'}, {'old_mean': 37, 'old_sd': 10, 'old_max': 74, 'new_mean': '172/3', 'new_max': '320/3'}, {'old_mean': 38, 'old_sd': 10, 'old_max': 71, 'new_mean': '127/2', 'new_max': '419/4'}, {'old_mean': 36, 'old_sd': 10, 'old_max': 70, 'new_mean': '66', 'new_max': '334/3'}, {'old_mean': 32, 'old_sd': 12, 'old_max': 57, 'new_mean': '176/3', 'new_max': '92'}, {'old_mean': 36, 'old_sd': 8, 'old_max': 75, 'new_mean': '68', 'new_max': '253/2'}, {'old_mean': 41, 'old_sd': 8, 'old_max': 74, 'new_mean': '157/2', 'new_max': '128'}, {'old_mean': 49, 'old_sd': 10, 'old_max': 81, 'new_mean': '247/3', 'new_max': '125'}, {'old_mean': 34, 'old_sd': 12, 'old_max': 63, 'new_mean': '163/3', 'new_max': '93'}, {'old_mean': 34, 'old_sd': 8, 'old_max': 65, 'new_mean': '121/2', 'new_max': '397/4'}, {'old_mean': 31, 'old_sd': 12, 'old_max': 53, 'new_mean': '157/3', 'new_max': '245/3'}]}}, 'problem_type_id': 'linear_find_scale_sd', 'required_capabilities': ['linear_find_scale_sd'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'old_mean': 42, 'old_sd': 12, 'old_max': 72, 'new_mean': 60, 'new_max': 95}, {'old_mean': 49, 'old_sd': 10, 'old_max': 79, 'new_mean': '265/4', 'new_max': '415/4'}, {'old_mean': 48, 'old_sd': 8, 'old_max': 85, 'new_mean': '79', 'new_max': '385/3'}, {'old_mean': 30, 'old_sd': 10, 'old_max': 50, 'new_mean': '61', 'new_max': '91'}, {'old_mean': 47, 'old_sd': 12, 'old_max': 86, 'new_mean': '171/2', 'new_max': '144'}, {'old_mean': 35, 'old_sd': 12, 'old_max': 72, 'new_mean': '215/4', 'new_max': '100'}, {'old_mean': 35, 'old_sd': 10, 'old_max': 75, 'new_mean': '173/3', 'new_max': '111'}, {'old_mean': 35, 'old_sd': 8, 'old_max': 63, 'new_mean': '121/2', 'new_max': '205/2'}, {'old_mean': 32, 'old_sd': 8, 'old_max': 59, 'new_mean': '62', 'new_max': '205/2'}, {'old_mean': 31, 'old_sd': 10, 'old_max': 64, 'new_mean': '129/2', 'new_max': '114'}, {'old_mean': 37, 'old_sd': 10, 'old_max': 74, 'new_mean': '172/3', 'new_max': '320/3'}, {'old_mean': 38, 'old_sd': 10, 'old_max': 71, 'new_mean': '127/2', 'new_max': '419/4'}, {'old_mean': 36, 'old_sd': 10, 'old_max': 70, 'new_mean': '66', 'new_max': '334/3'}, {'old_mean': 32, 'old_sd': 12, 'old_max': 57, 'new_mean': '176/3', 'new_max': '92'}, {'old_mean': 36, 'old_sd': 8, 'old_max': 75, 'new_mean': '68', 'new_max': '253/2'}, {'old_mean': 41, 'old_sd': 8, 'old_max': 74, 'new_mean': '157/2', 'new_max': '128'}, {'old_mean': 49, 'old_sd': 10, 'old_max': 81, 'new_mean': '247/3', 'new_max': '125'}, {'old_mean': 34, 'old_sd': 12, 'old_max': 63, 'new_mean': '163/3', 'new_max': '93'}, {'old_mean': 34, 'old_sd': 8, 'old_max': 65, 'new_mean': '121/2', 'new_max': '397/4'}, {'old_mean': 31, 'old_sd': 12, 'old_max': 53, 'new_mean': '157/3', 'new_max': '245/3'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_DataScalingAndShifting', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['linear_find_scale_sd'], 'matched_capabilities': ['linear_find_scale_sd'], 'selected_operation': 'linear_find_scale_sd', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['linear_find_scale_sd', 'linear_mean_sd', 'monthly_mean_sd', 'standardize_scores', 'statement_selection', 'true_false_stat'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_DataScalingAndShifting'}), seed)
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
