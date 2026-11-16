from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "quartile_frequency"
TEXTBOOK_EXAMPLE_ID = 12920
DEFAULT_COMPONENT_ID = "src_12920" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MedianAndPercentiles"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "quartile_frequency"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['quartile_frequency'], 'domain_operation': 'quartile_frequency', 'problem_type_id': 'quartile_frequency', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'values': [22, 25, 32, 36, 43, 48, 52], 'counts': [10, 15, 26, 35, 16, 11, 5], 'scene': 'salary'}, {'values': [35, 37, 38, 43, 46, 47, 53], 'counts': [16, 23, 9, 20, 34, 16, 25], 'scene': 'salary'}, {'values': [25, 26, 36, 42, 44, 55, 58], 'counts': [26, 11, 30, 33, 25, 9, 9], 'scene': 'salary'}, {'values': [29, 38, 44, 49, 50, 51, 52], 'counts': [29, 17, 12, 16, 19, 22, 10], 'scene': 'salary'}, {'values': [32, 44, 45, 46, 48, 51, 57], 'counts': [34, 10, 34, 19, 20, 12, 18], 'scene': 'salary'}, {'values': [21, 22, 31, 32, 36, 40, 52], 'counts': [24, 30, 6, 28, 11, 12, 5], 'scene': 'salary'}, {'values': [20, 21, 24, 38, 44, 54, 60], 'counts': [12, 25, 6, 15, 13, 10, 25], 'scene': 'salary'}, {'values': [22, 23, 28, 30, 31, 48, 52], 'counts': [18, 10, 33, 24, 9, 11, 17], 'scene': 'salary'}, {'values': [22, 26, 27, 39, 45, 52, 55], 'counts': [32, 25, 5, 20, 22, 5, 7], 'scene': 'salary'}, {'values': [20, 21, 30, 37, 51, 53, 54], 'counts': [21, 21, 21, 17, 30, 22, 18], 'scene': 'salary'}, {'values': [27, 28, 37, 43, 54, 57, 59], 'counts': [17, 7, 30, 23, 23, 30, 21], 'scene': 'salary'}, {'values': [27, 28, 29, 33, 43, 53, 57], 'counts': [35, 12, 17, 31, 22, 12, 9], 'scene': 'salary'}, {'values': [21, 27, 42, 47, 49, 56, 58], 'counts': [28, 18, 33, 27, 13, 35, 25], 'scene': 'salary'}, {'values': [24, 29, 42, 43, 46, 49, 51], 'counts': [29, 33, 16, 13, 8, 6, 18], 'scene': 'salary'}, {'values': [26, 38, 39, 46, 53, 54, 58], 'counts': [34, 11, 7, 21, 18, 31, 31], 'scene': 'salary'}, {'values': [31, 35, 37, 39, 43, 51, 58], 'counts': [34, 21, 27, 30, 32, 30, 16], 'scene': 'salary'}, {'values': [22, 23, 25, 47, 53, 56, 60], 'counts': [26, 8, 14, 35, 6, 26, 9], 'scene': 'salary'}, {'values': [20, 25, 32, 43, 50, 53, 57], 'counts': [22, 10, 14, 16, 15, 26, 25], 'scene': 'salary'}, {'values': [26, 32, 37, 41, 42, 54, 60], 'counts': [28, 7, 9, 15, 26, 21, 26], 'scene': 'salary'}, {'values': [29, 34, 39, 42, 52, 59, 60], 'counts': [32, 14, 20, 31, 31, 32, 31], 'scene': 'salary'}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['quartile_frequency'], 'domain_operation': 'quartile_frequency', 'problem_type_id': 'quartile_frequency', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'values': [22, 25, 32, 36, 43, 48, 52], 'counts': [10, 15, 26, 35, 16, 11, 5], 'scene': 'salary'}, {'values': [35, 37, 38, 43, 46, 47, 53], 'counts': [16, 23, 9, 20, 34, 16, 25], 'scene': 'salary'}, {'values': [25, 26, 36, 42, 44, 55, 58], 'counts': [26, 11, 30, 33, 25, 9, 9], 'scene': 'salary'}, {'values': [29, 38, 44, 49, 50, 51, 52], 'counts': [29, 17, 12, 16, 19, 22, 10], 'scene': 'salary'}, {'values': [32, 44, 45, 46, 48, 51, 57], 'counts': [34, 10, 34, 19, 20, 12, 18], 'scene': 'salary'}, {'values': [21, 22, 31, 32, 36, 40, 52], 'counts': [24, 30, 6, 28, 11, 12, 5], 'scene': 'salary'}, {'values': [20, 21, 24, 38, 44, 54, 60], 'counts': [12, 25, 6, 15, 13, 10, 25], 'scene': 'salary'}, {'values': [22, 23, 28, 30, 31, 48, 52], 'counts': [18, 10, 33, 24, 9, 11, 17], 'scene': 'salary'}, {'values': [22, 26, 27, 39, 45, 52, 55], 'counts': [32, 25, 5, 20, 22, 5, 7], 'scene': 'salary'}, {'values': [20, 21, 30, 37, 51, 53, 54], 'counts': [21, 21, 21, 17, 30, 22, 18], 'scene': 'salary'}, {'values': [27, 28, 37, 43, 54, 57, 59], 'counts': [17, 7, 30, 23, 23, 30, 21], 'scene': 'salary'}, {'values': [27, 28, 29, 33, 43, 53, 57], 'counts': [35, 12, 17, 31, 22, 12, 9], 'scene': 'salary'}, {'values': [21, 27, 42, 47, 49, 56, 58], 'counts': [28, 18, 33, 27, 13, 35, 25], 'scene': 'salary'}, {'values': [24, 29, 42, 43, 46, 49, 51], 'counts': [29, 33, 16, 13, 8, 6, 18], 'scene': 'salary'}, {'values': [26, 38, 39, 46, 53, 54, 58], 'counts': [34, 11, 7, 21, 18, 31, 31], 'scene': 'salary'}, {'values': [31, 35, 37, 39, 43, 51, 58], 'counts': [34, 21, 27, 30, 32, 30, 16], 'scene': 'salary'}, {'values': [22, 23, 25, 47, 53, 56, 60], 'counts': [26, 8, 14, 35, 6, 26, 9], 'scene': 'salary'}, {'values': [20, 25, 32, 43, 50, 53, 57], 'counts': [22, 10, 14, 16, 15, 26, 25], 'scene': 'salary'}, {'values': [26, 32, 37, 41, 42, 54, 60], 'counts': [28, 7, 9, 15, 26, 21, 26], 'scene': 'salary'}, {'values': [29, 34, 39, 42, 52, 59, 60], 'counts': [32, 14, 20, 31, 31, 32, 31], 'scene': 'salary'}]}}, 'problem_type_id': 'quartile_frequency', 'required_capabilities': ['quartile_frequency'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'values': [22, 25, 32, 36, 43, 48, 52], 'counts': [10, 15, 26, 35, 16, 11, 5], 'scene': 'salary'}, {'values': [35, 37, 38, 43, 46, 47, 53], 'counts': [16, 23, 9, 20, 34, 16, 25], 'scene': 'salary'}, {'values': [25, 26, 36, 42, 44, 55, 58], 'counts': [26, 11, 30, 33, 25, 9, 9], 'scene': 'salary'}, {'values': [29, 38, 44, 49, 50, 51, 52], 'counts': [29, 17, 12, 16, 19, 22, 10], 'scene': 'salary'}, {'values': [32, 44, 45, 46, 48, 51, 57], 'counts': [34, 10, 34, 19, 20, 12, 18], 'scene': 'salary'}, {'values': [21, 22, 31, 32, 36, 40, 52], 'counts': [24, 30, 6, 28, 11, 12, 5], 'scene': 'salary'}, {'values': [20, 21, 24, 38, 44, 54, 60], 'counts': [12, 25, 6, 15, 13, 10, 25], 'scene': 'salary'}, {'values': [22, 23, 28, 30, 31, 48, 52], 'counts': [18, 10, 33, 24, 9, 11, 17], 'scene': 'salary'}, {'values': [22, 26, 27, 39, 45, 52, 55], 'counts': [32, 25, 5, 20, 22, 5, 7], 'scene': 'salary'}, {'values': [20, 21, 30, 37, 51, 53, 54], 'counts': [21, 21, 21, 17, 30, 22, 18], 'scene': 'salary'}, {'values': [27, 28, 37, 43, 54, 57, 59], 'counts': [17, 7, 30, 23, 23, 30, 21], 'scene': 'salary'}, {'values': [27, 28, 29, 33, 43, 53, 57], 'counts': [35, 12, 17, 31, 22, 12, 9], 'scene': 'salary'}, {'values': [21, 27, 42, 47, 49, 56, 58], 'counts': [28, 18, 33, 27, 13, 35, 25], 'scene': 'salary'}, {'values': [24, 29, 42, 43, 46, 49, 51], 'counts': [29, 33, 16, 13, 8, 6, 18], 'scene': 'salary'}, {'values': [26, 38, 39, 46, 53, 54, 58], 'counts': [34, 11, 7, 21, 18, 31, 31], 'scene': 'salary'}, {'values': [31, 35, 37, 39, 43, 51, 58], 'counts': [34, 21, 27, 30, 32, 30, 16], 'scene': 'salary'}, {'values': [22, 23, 25, 47, 53, 56, 60], 'counts': [26, 8, 14, 35, 6, 26, 9], 'scene': 'salary'}, {'values': [20, 25, 32, 43, 50, 53, 57], 'counts': [22, 10, 14, 16, 15, 26, 25], 'scene': 'salary'}, {'values': [26, 32, 37, 41, 42, 54, 60], 'counts': [28, 7, 9, 15, 26, 21, 26], 'scene': 'salary'}, {'values': [29, 34, 39, 42, 52, 59, 60], 'counts': [32, 14, 20, 31, 31, 32, 31], 'scene': 'salary'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MedianAndPercentiles', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['quartile_frequency'], 'matched_capabilities': ['quartile_frequency'], 'selected_operation': 'quartile_frequency', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['list_summary_stats', 'median_consecutive', 'median_lists', 'percentile_frequency', 'quartile_frequency', 'statement_selection', 'true_false_stat'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MedianAndPercentiles'}), seed)
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
