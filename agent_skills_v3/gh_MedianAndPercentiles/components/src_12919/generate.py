from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "percentile_frequency"
TEXTBOOK_EXAMPLE_ID = 12919
DEFAULT_COMPONENT_ID = "src_12919" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MedianAndPercentiles"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "percentile_frequency"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['percentile_frequency'], 'domain_operation': 'percentile_frequency', 'problem_type_id': 'percentile_frequency', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [13, 29, 42, 66, 38, 35, 27], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [32, 62, 70, 12, 16, 68, 25], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [15, 64, 56, 56, 29, 47, 23], 'percentiles': [15, 80], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [57, 45, 18, 43, 70, 39, 8, 11, 26], 'percentiles': [25, 75], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [42, 39, 59, 13, 65, 25, 58, 41, 44], 'percentiles': [15, 80], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [20, 30, 18, 31, 19, 20, 21], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [30, 17, 62, 9, 36, 39, 64], 'percentiles': [25, 75], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [23, 33, 21, 50, 32, 26, 14, 48, 11], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [30, 23, 35, 43, 53, 44, 9], 'percentiles': [15, 80], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [18, 14, 25, 50, 60, 10], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [18, 54, 55, 44, 28, 41, 39, 60, 40], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [26, 25, 27, 42, 44, 16], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [21, 69, 40, 66, 25, 49, 70, 26, 31], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [23, 10, 40, 68, 38, 34, 39, 9, 42], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [57, 38, 45, 49, 45, 53], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [12, 66, 49, 22, 17, 44], 'percentiles': [15, 80], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [36, 70, 52, 51, 32, 22, 12], 'percentiles': [25, 75], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [10, 14, 22, 49, 63, 50], 'percentiles': [25, 75], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [45, 28, 25, 65, 46, 60], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [64, 25, 41, 15, 60, 53, 12, 17, 12], 'percentiles': [25, 75], 'scene': 'shots'}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['percentile_frequency'], 'domain_operation': 'percentile_frequency', 'problem_type_id': 'percentile_frequency', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [13, 29, 42, 66, 38, 35, 27], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [32, 62, 70, 12, 16, 68, 25], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [15, 64, 56, 56, 29, 47, 23], 'percentiles': [15, 80], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [57, 45, 18, 43, 70, 39, 8, 11, 26], 'percentiles': [25, 75], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [42, 39, 59, 13, 65, 25, 58, 41, 44], 'percentiles': [15, 80], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [20, 30, 18, 31, 19, 20, 21], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [30, 17, 62, 9, 36, 39, 64], 'percentiles': [25, 75], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [23, 33, 21, 50, 32, 26, 14, 48, 11], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [30, 23, 35, 43, 53, 44, 9], 'percentiles': [15, 80], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [18, 14, 25, 50, 60, 10], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [18, 54, 55, 44, 28, 41, 39, 60, 40], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [26, 25, 27, 42, 44, 16], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [21, 69, 40, 66, 25, 49, 70, 26, 31], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [23, 10, 40, 68, 38, 34, 39, 9, 42], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [57, 38, 45, 49, 45, 53], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [12, 66, 49, 22, 17, 44], 'percentiles': [15, 80], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [36, 70, 52, 51, 32, 22, 12], 'percentiles': [25, 75], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [10, 14, 22, 49, 63, 50], 'percentiles': [25, 75], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [45, 28, 25, 65, 46, 60], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [64, 25, 41, 15, 60, 53, 12, 17, 12], 'percentiles': [25, 75], 'scene': 'shots'}]}}, 'problem_type_id': 'percentile_frequency', 'required_capabilities': ['percentile_frequency'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [13, 29, 42, 66, 38, 35, 27], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [32, 62, 70, 12, 16, 68, 25], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [15, 64, 56, 56, 29, 47, 23], 'percentiles': [15, 80], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [57, 45, 18, 43, 70, 39, 8, 11, 26], 'percentiles': [25, 75], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [42, 39, 59, 13, 65, 25, 58, 41, 44], 'percentiles': [15, 80], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [20, 30, 18, 31, 19, 20, 21], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [30, 17, 62, 9, 36, 39, 64], 'percentiles': [25, 75], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [23, 33, 21, 50, 32, 26, 14, 48, 11], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [30, 23, 35, 43, 53, 44, 9], 'percentiles': [15, 80], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [18, 14, 25, 50, 60, 10], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [18, 54, 55, 44, 28, 41, 39, 60, 40], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [26, 25, 27, 42, 44, 16], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [21, 69, 40, 66, 25, 49, 70, 26, 31], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [23, 10, 40, 68, 38, 34, 39, 9, 42], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [57, 38, 45, 49, 45, 53], 'percentiles': [35, 60], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [12, 66, 49, 22, 17, 44], 'percentiles': [15, 80], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6], 'counts': [36, 70, 52, 51, 32, 22, 12], 'percentiles': [25, 75], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [10, 14, 22, 49, 63, 50], 'percentiles': [25, 75], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5], 'counts': [45, 28, 25, 65, 46, 60], 'percentiles': [20, 70], 'scene': 'shots'}, {'values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'counts': [64, 25, 41, 15, 60, 53, 12, 17, 12], 'percentiles': [25, 75], 'scene': 'shots'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MedianAndPercentiles', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['percentile_frequency'], 'matched_capabilities': ['percentile_frequency'], 'selected_operation': 'percentile_frequency', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['list_summary_stats', 'median_consecutive', 'median_lists', 'percentile_frequency', 'quartile_frequency', 'statement_selection', 'true_false_stat'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MedianAndPercentiles'}), seed)
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
