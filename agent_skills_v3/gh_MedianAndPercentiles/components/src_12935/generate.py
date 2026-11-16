from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "list_summary_stats"
TEXTBOOK_EXAMPLE_ID = 12935
DEFAULT_COMPONENT_ID = "src_12935" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MedianAndPercentiles"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "list_summary_stats"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['list_summary_stats'], 'domain_operation': 'list_summary_stats', 'problem_type_id': 'list_summary_stats', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'values': [55, 56, 59, 59, 59, 60, 60, 63, 68, 71], 'stats': ['mean', 'median', 'q3']}, {'values': [46, 47, 54, 56, 64, 69, 70, 80, 81, 88], 'stats': ['mean', 'median', 'q3']}, {'values': [45, 46, 48, 54, 59, 65, 75, 84, 87, 87], 'stats': ['mean', 'median', 'q3']}, {'values': [42, 43, 44, 47, 53, 61, 61, 71, 85, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [54, 56, 62, 64, 70, 72, 79, 82, 86, 90], 'stats': ['mean', 'median', 'q3']}, {'values': [45, 51, 52, 60, 73, 77, 83, 86, 86, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [45, 53, 55, 60, 64, 78, 79, 80, 83, 90], 'stats': ['mean', 'median', 'q3']}, {'values': [49, 52, 57, 61, 62, 66, 68, 74, 76, 77], 'stats': ['mean', 'median', 'q3']}, {'values': [44, 47, 58, 64, 71, 71, 80, 80, 80, 81], 'stats': ['mean', 'median', 'q3']}, {'values': [41, 47, 47, 50, 56, 63, 74, 79, 79, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [40, 42, 43, 45, 69, 69, 76, 77, 79, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [42, 44, 48, 48, 49, 64, 65, 80, 82, 88], 'stats': ['mean', 'median', 'q3']}, {'values': [44, 47, 48, 59, 63, 64, 74, 74, 84, 84], 'stats': ['mean', 'median', 'q3']}, {'values': [50, 54, 66, 66, 78, 82, 82, 84, 85, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [43, 46, 56, 57, 61, 65, 65, 66, 83, 90], 'stats': ['mean', 'median', 'q3']}, {'values': [54, 59, 61, 66, 67, 72, 72, 77, 78, 84], 'stats': ['mean', 'median', 'q3']}, {'values': [43, 49, 61, 61, 67, 72, 76, 78, 81, 88], 'stats': ['mean', 'median', 'q3']}, {'values': [41, 53, 61, 62, 77, 78, 78, 80, 83, 84], 'stats': ['mean', 'median', 'q3']}, {'values': [42, 54, 55, 56, 59, 64, 67, 68, 82, 88], 'stats': ['mean', 'median', 'q3']}, {'values': [41, 50, 57, 58, 59, 65, 68, 68, 79, 82], 'stats': ['mean', 'median', 'q3']}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['list_summary_stats'], 'domain_operation': 'list_summary_stats', 'problem_type_id': 'list_summary_stats', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'values': [55, 56, 59, 59, 59, 60, 60, 63, 68, 71], 'stats': ['mean', 'median', 'q3']}, {'values': [46, 47, 54, 56, 64, 69, 70, 80, 81, 88], 'stats': ['mean', 'median', 'q3']}, {'values': [45, 46, 48, 54, 59, 65, 75, 84, 87, 87], 'stats': ['mean', 'median', 'q3']}, {'values': [42, 43, 44, 47, 53, 61, 61, 71, 85, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [54, 56, 62, 64, 70, 72, 79, 82, 86, 90], 'stats': ['mean', 'median', 'q3']}, {'values': [45, 51, 52, 60, 73, 77, 83, 86, 86, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [45, 53, 55, 60, 64, 78, 79, 80, 83, 90], 'stats': ['mean', 'median', 'q3']}, {'values': [49, 52, 57, 61, 62, 66, 68, 74, 76, 77], 'stats': ['mean', 'median', 'q3']}, {'values': [44, 47, 58, 64, 71, 71, 80, 80, 80, 81], 'stats': ['mean', 'median', 'q3']}, {'values': [41, 47, 47, 50, 56, 63, 74, 79, 79, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [40, 42, 43, 45, 69, 69, 76, 77, 79, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [42, 44, 48, 48, 49, 64, 65, 80, 82, 88], 'stats': ['mean', 'median', 'q3']}, {'values': [44, 47, 48, 59, 63, 64, 74, 74, 84, 84], 'stats': ['mean', 'median', 'q3']}, {'values': [50, 54, 66, 66, 78, 82, 82, 84, 85, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [43, 46, 56, 57, 61, 65, 65, 66, 83, 90], 'stats': ['mean', 'median', 'q3']}, {'values': [54, 59, 61, 66, 67, 72, 72, 77, 78, 84], 'stats': ['mean', 'median', 'q3']}, {'values': [43, 49, 61, 61, 67, 72, 76, 78, 81, 88], 'stats': ['mean', 'median', 'q3']}, {'values': [41, 53, 61, 62, 77, 78, 78, 80, 83, 84], 'stats': ['mean', 'median', 'q3']}, {'values': [42, 54, 55, 56, 59, 64, 67, 68, 82, 88], 'stats': ['mean', 'median', 'q3']}, {'values': [41, 50, 57, 58, 59, 65, 68, 68, 79, 82], 'stats': ['mean', 'median', 'q3']}]}}, 'problem_type_id': 'list_summary_stats', 'required_capabilities': ['list_summary_stats'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'values': [55, 56, 59, 59, 59, 60, 60, 63, 68, 71], 'stats': ['mean', 'median', 'q3']}, {'values': [46, 47, 54, 56, 64, 69, 70, 80, 81, 88], 'stats': ['mean', 'median', 'q3']}, {'values': [45, 46, 48, 54, 59, 65, 75, 84, 87, 87], 'stats': ['mean', 'median', 'q3']}, {'values': [42, 43, 44, 47, 53, 61, 61, 71, 85, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [54, 56, 62, 64, 70, 72, 79, 82, 86, 90], 'stats': ['mean', 'median', 'q3']}, {'values': [45, 51, 52, 60, 73, 77, 83, 86, 86, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [45, 53, 55, 60, 64, 78, 79, 80, 83, 90], 'stats': ['mean', 'median', 'q3']}, {'values': [49, 52, 57, 61, 62, 66, 68, 74, 76, 77], 'stats': ['mean', 'median', 'q3']}, {'values': [44, 47, 58, 64, 71, 71, 80, 80, 80, 81], 'stats': ['mean', 'median', 'q3']}, {'values': [41, 47, 47, 50, 56, 63, 74, 79, 79, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [40, 42, 43, 45, 69, 69, 76, 77, 79, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [42, 44, 48, 48, 49, 64, 65, 80, 82, 88], 'stats': ['mean', 'median', 'q3']}, {'values': [44, 47, 48, 59, 63, 64, 74, 74, 84, 84], 'stats': ['mean', 'median', 'q3']}, {'values': [50, 54, 66, 66, 78, 82, 82, 84, 85, 86], 'stats': ['mean', 'median', 'q3']}, {'values': [43, 46, 56, 57, 61, 65, 65, 66, 83, 90], 'stats': ['mean', 'median', 'q3']}, {'values': [54, 59, 61, 66, 67, 72, 72, 77, 78, 84], 'stats': ['mean', 'median', 'q3']}, {'values': [43, 49, 61, 61, 67, 72, 76, 78, 81, 88], 'stats': ['mean', 'median', 'q3']}, {'values': [41, 53, 61, 62, 77, 78, 78, 80, 83, 84], 'stats': ['mean', 'median', 'q3']}, {'values': [42, 54, 55, 56, 59, 64, 67, 68, 82, 88], 'stats': ['mean', 'median', 'q3']}, {'values': [41, 50, 57, 58, 59, 65, 68, 68, 79, 82], 'stats': ['mean', 'median', 'q3']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MedianAndPercentiles', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['list_summary_stats'], 'matched_capabilities': ['list_summary_stats'], 'selected_operation': 'list_summary_stats', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['list_summary_stats', 'median_consecutive', 'median_lists', 'percentile_frequency', 'quartile_frequency', 'statement_selection', 'true_false_stat'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MedianAndPercentiles'}), seed)
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
