from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "percentile_frequency"
TEXTBOOK_EXAMPLE_ID = 12922
DEFAULT_COMPONENT_ID = "src_12922" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['percentile_frequency'], 'domain_operation': 'percentile_frequency', 'problem_type_id': 'percentile_frequency', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'values': [15, 16, 17, 18, 19, 20, 21], 'counts': [16, 31, 48, 71, 67, 34, 3], 'percentiles': [15, 80], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [41, 73, 67, 29, 25, 16, 44], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [41, 72, 31, 70, 12, 63, 54], 'percentiles': [15, 80], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [65, 19, 28, 26, 39, 58, 61], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [8, 5, 47, 57, 13, 72, 40], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [16, 17, 18, 19, 20, 21, 22], 'counts': [5, 40, 63, 56, 67, 9, 40], 'percentiles': [25, 75], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [16, 47, 8, 74, 47, 10, 37], 'percentiles': [25, 75], 'scene': 'breaths'}, {'values': [14, 15, 16, 17, 18, 19, 20], 'counts': [36, 4, 75, 23, 6, 61, 32], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [13, 14, 15, 16, 17, 18, 19], 'counts': [20, 52, 49, 4, 12, 26, 51], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [16, 17, 18, 19, 20, 21, 22], 'counts': [26, 50, 25, 25, 9, 48, 30], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [16, 17, 18, 19, 20, 21, 22], 'counts': [55, 40, 37, 48, 50, 75, 66], 'percentiles': [25, 75], 'scene': 'breaths'}, {'values': [15, 16, 17, 18, 19, 20, 21], 'counts': [47, 21, 24, 23, 36, 16, 68], 'percentiles': [25, 75], 'scene': 'breaths'}, {'values': [14, 15, 16, 17, 18, 19, 20], 'counts': [63, 44, 17, 71, 54, 75, 56], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [14, 15, 16, 17, 18, 19, 20], 'counts': [70, 4, 49, 35, 21, 26, 27], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [15, 16, 17, 18, 19, 20, 21], 'counts': [47, 3, 65, 20, 16, 58, 57], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [14, 15, 16, 17, 18, 19, 20], 'counts': [43, 69, 9, 56, 16, 37, 16], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [13, 14, 15, 16, 17, 18, 19], 'counts': [20, 18, 17, 58, 32, 26, 26], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [16, 17, 18, 19, 20, 21, 22], 'counts': [26, 64, 34, 54, 55, 26, 51], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [13, 14, 15, 16, 17, 18, 19], 'counts': [24, 43, 60, 18, 67, 50, 28], 'percentiles': [15, 80], 'scene': 'breaths'}, {'values': [13, 14, 15, 16, 17, 18, 19], 'counts': [45, 4, 51, 52, 59, 21, 31], 'percentiles': [15, 80], 'scene': 'breaths'}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['percentile_frequency'], 'domain_operation': 'percentile_frequency', 'problem_type_id': 'percentile_frequency', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'values': [15, 16, 17, 18, 19, 20, 21], 'counts': [16, 31, 48, 71, 67, 34, 3], 'percentiles': [15, 80], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [41, 73, 67, 29, 25, 16, 44], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [41, 72, 31, 70, 12, 63, 54], 'percentiles': [15, 80], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [65, 19, 28, 26, 39, 58, 61], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [8, 5, 47, 57, 13, 72, 40], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [16, 17, 18, 19, 20, 21, 22], 'counts': [5, 40, 63, 56, 67, 9, 40], 'percentiles': [25, 75], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [16, 47, 8, 74, 47, 10, 37], 'percentiles': [25, 75], 'scene': 'breaths'}, {'values': [14, 15, 16, 17, 18, 19, 20], 'counts': [36, 4, 75, 23, 6, 61, 32], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [13, 14, 15, 16, 17, 18, 19], 'counts': [20, 52, 49, 4, 12, 26, 51], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [16, 17, 18, 19, 20, 21, 22], 'counts': [26, 50, 25, 25, 9, 48, 30], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [16, 17, 18, 19, 20, 21, 22], 'counts': [55, 40, 37, 48, 50, 75, 66], 'percentiles': [25, 75], 'scene': 'breaths'}, {'values': [15, 16, 17, 18, 19, 20, 21], 'counts': [47, 21, 24, 23, 36, 16, 68], 'percentiles': [25, 75], 'scene': 'breaths'}, {'values': [14, 15, 16, 17, 18, 19, 20], 'counts': [63, 44, 17, 71, 54, 75, 56], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [14, 15, 16, 17, 18, 19, 20], 'counts': [70, 4, 49, 35, 21, 26, 27], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [15, 16, 17, 18, 19, 20, 21], 'counts': [47, 3, 65, 20, 16, 58, 57], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [14, 15, 16, 17, 18, 19, 20], 'counts': [43, 69, 9, 56, 16, 37, 16], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [13, 14, 15, 16, 17, 18, 19], 'counts': [20, 18, 17, 58, 32, 26, 26], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [16, 17, 18, 19, 20, 21, 22], 'counts': [26, 64, 34, 54, 55, 26, 51], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [13, 14, 15, 16, 17, 18, 19], 'counts': [24, 43, 60, 18, 67, 50, 28], 'percentiles': [15, 80], 'scene': 'breaths'}, {'values': [13, 14, 15, 16, 17, 18, 19], 'counts': [45, 4, 51, 52, 59, 21, 31], 'percentiles': [15, 80], 'scene': 'breaths'}]}}, 'problem_type_id': 'percentile_frequency', 'required_capabilities': ['percentile_frequency'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'values': [15, 16, 17, 18, 19, 20, 21], 'counts': [16, 31, 48, 71, 67, 34, 3], 'percentiles': [15, 80], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [41, 73, 67, 29, 25, 16, 44], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [41, 72, 31, 70, 12, 63, 54], 'percentiles': [15, 80], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [65, 19, 28, 26, 39, 58, 61], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [8, 5, 47, 57, 13, 72, 40], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [16, 17, 18, 19, 20, 21, 22], 'counts': [5, 40, 63, 56, 67, 9, 40], 'percentiles': [25, 75], 'scene': 'breaths'}, {'values': [12, 13, 14, 15, 16, 17, 18], 'counts': [16, 47, 8, 74, 47, 10, 37], 'percentiles': [25, 75], 'scene': 'breaths'}, {'values': [14, 15, 16, 17, 18, 19, 20], 'counts': [36, 4, 75, 23, 6, 61, 32], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [13, 14, 15, 16, 17, 18, 19], 'counts': [20, 52, 49, 4, 12, 26, 51], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [16, 17, 18, 19, 20, 21, 22], 'counts': [26, 50, 25, 25, 9, 48, 30], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [16, 17, 18, 19, 20, 21, 22], 'counts': [55, 40, 37, 48, 50, 75, 66], 'percentiles': [25, 75], 'scene': 'breaths'}, {'values': [15, 16, 17, 18, 19, 20, 21], 'counts': [47, 21, 24, 23, 36, 16, 68], 'percentiles': [25, 75], 'scene': 'breaths'}, {'values': [14, 15, 16, 17, 18, 19, 20], 'counts': [63, 44, 17, 71, 54, 75, 56], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [14, 15, 16, 17, 18, 19, 20], 'counts': [70, 4, 49, 35, 21, 26, 27], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [15, 16, 17, 18, 19, 20, 21], 'counts': [47, 3, 65, 20, 16, 58, 57], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [14, 15, 16, 17, 18, 19, 20], 'counts': [43, 69, 9, 56, 16, 37, 16], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [13, 14, 15, 16, 17, 18, 19], 'counts': [20, 18, 17, 58, 32, 26, 26], 'percentiles': [35, 60], 'scene': 'breaths'}, {'values': [16, 17, 18, 19, 20, 21, 22], 'counts': [26, 64, 34, 54, 55, 26, 51], 'percentiles': [20, 70], 'scene': 'breaths'}, {'values': [13, 14, 15, 16, 17, 18, 19], 'counts': [24, 43, 60, 18, 67, 50, 28], 'percentiles': [15, 80], 'scene': 'breaths'}, {'values': [13, 14, 15, 16, 17, 18, 19], 'counts': [45, 4, 51, 52, 59, 21, 31], 'percentiles': [15, 80], 'scene': 'breaths'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MedianAndPercentiles', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['percentile_frequency'], 'matched_capabilities': ['percentile_frequency'], 'selected_operation': 'percentile_frequency', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['list_summary_stats', 'median_consecutive', 'median_lists', 'percentile_frequency', 'quartile_frequency', 'statement_selection', 'true_false_stat'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MedianAndPercentiles'}), seed)
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
