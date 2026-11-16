from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "true_false_stat"
TEXTBOOK_EXAMPLE_ID = 12934
DEFAULT_COMPONENT_ID = "src_12934" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MedianAndPercentiles"
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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['true_false_stat'], 'domain_operation': 'true_false_stat', 'problem_type_id': 'true_false_stat', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'claim': {'kind': 'median_ge_mean_always'}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [17, 40, 13, 6, 18, 16]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [36, 35, 23, 38, 1, 40, 30]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [28, 27, 25, 31, 36, 0]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [28, 36, 39, 39, 34, 0, 34]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [16, 8, 16, 17, 40]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [2, 36, 35, 33, 28, 36]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [51, 10, 14, 11, 2, 6]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [12, 12, 12, 17, 10, 1, 44]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [0, 23, 40, 28, 29, 25, 24]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [2, 23, 32, 24, 29, 27]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [10, 43, 8, 15, 3]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [29, 6, 29, 28, 30]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [46, 3, 9, 5, 13]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [32, 39, 39, 0, 34, 38, 29]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [13, 10, 44, 10, 4]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [39, 26, 2, 40, 30]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [2, 43, 2, 8, 6]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [14, 13, 46, 13, 14, 8]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [27, 27, 29, 30, 2]}}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['true_false_stat'], 'domain_operation': 'true_false_stat', 'problem_type_id': 'true_false_stat', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'claim': {'kind': 'median_ge_mean_always'}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [17, 40, 13, 6, 18, 16]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [36, 35, 23, 38, 1, 40, 30]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [28, 27, 25, 31, 36, 0]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [28, 36, 39, 39, 34, 0, 34]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [16, 8, 16, 17, 40]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [2, 36, 35, 33, 28, 36]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [51, 10, 14, 11, 2, 6]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [12, 12, 12, 17, 10, 1, 44]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [0, 23, 40, 28, 29, 25, 24]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [2, 23, 32, 24, 29, 27]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [10, 43, 8, 15, 3]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [29, 6, 29, 28, 30]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [46, 3, 9, 5, 13]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [32, 39, 39, 0, 34, 38, 29]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [13, 10, 44, 10, 4]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [39, 26, 2, 40, 30]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [2, 43, 2, 8, 6]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [14, 13, 46, 13, 14, 8]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [27, 27, 29, 30, 2]}}]}}, 'problem_type_id': 'true_false_stat', 'required_capabilities': ['true_false_stat'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'claim': {'kind': 'median_ge_mean_always'}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [17, 40, 13, 6, 18, 16]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [36, 35, 23, 38, 1, 40, 30]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [28, 27, 25, 31, 36, 0]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [28, 36, 39, 39, 34, 0, 34]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [16, 8, 16, 17, 40]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [2, 36, 35, 33, 28, 36]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [51, 10, 14, 11, 2, 6]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [12, 12, 12, 17, 10, 1, 44]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [0, 23, 40, 28, 29, 25, 24]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [2, 23, 32, 24, 29, 27]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [10, 43, 8, 15, 3]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [29, 6, 29, 28, 30]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [46, 3, 9, 5, 13]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [32, 39, 39, 0, 34, 38, 29]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [13, 10, 44, 10, 4]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [39, 26, 2, 40, 30]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [2, 43, 2, 8, 6]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [14, 13, 46, 13, 14, 8]}}, {'claim': {'kind': 'median_ge_mean_data', 'values': [27, 27, 29, 30, 2]}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MedianAndPercentiles', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['true_false_stat'], 'matched_capabilities': ['true_false_stat'], 'selected_operation': 'true_false_stat', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['list_summary_stats', 'median_consecutive', 'median_lists', 'percentile_frequency', 'quartile_frequency', 'statement_selection', 'true_false_stat'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MedianAndPercentiles'}), seed)
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
