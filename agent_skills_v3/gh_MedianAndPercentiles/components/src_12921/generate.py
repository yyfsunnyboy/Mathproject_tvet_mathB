from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "median_consecutive"
TEXTBOOK_EXAMPLE_ID = 12921
DEFAULT_COMPONENT_ID = "src_12921" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MedianAndPercentiles"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "median_consecutive"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['median_consecutive'], 'domain_operation': 'median_consecutive', 'problem_type_id': 'median_consecutive', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'ends': [49, 50]}, {'ends': [30, 31]}, {'ends': [50, 51]}, {'ends': [46, 47]}, {'ends': [20, 21]}, {'ends': [44, 45]}, {'ends': [24, 25]}, {'ends': [48, 49]}, {'ends': [54, 55]}, {'ends': [40, 41]}, {'ends': [32, 33]}, {'ends': [42, 43]}, {'ends': [52, 53]}, {'ends': [38, 39]}, {'ends': [22, 23]}, {'ends': [28, 29]}, {'ends': [26, 27]}, {'ends': [58, 59]}, {'ends': [34, 35]}, {'ends': [56, 57]}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['median_consecutive'], 'domain_operation': 'median_consecutive', 'problem_type_id': 'median_consecutive', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'ends': [49, 50]}, {'ends': [30, 31]}, {'ends': [50, 51]}, {'ends': [46, 47]}, {'ends': [20, 21]}, {'ends': [44, 45]}, {'ends': [24, 25]}, {'ends': [48, 49]}, {'ends': [54, 55]}, {'ends': [40, 41]}, {'ends': [32, 33]}, {'ends': [42, 43]}, {'ends': [52, 53]}, {'ends': [38, 39]}, {'ends': [22, 23]}, {'ends': [28, 29]}, {'ends': [26, 27]}, {'ends': [58, 59]}, {'ends': [34, 35]}, {'ends': [56, 57]}]}}, 'problem_type_id': 'median_consecutive', 'required_capabilities': ['median_consecutive'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'ends': [49, 50]}, {'ends': [30, 31]}, {'ends': [50, 51]}, {'ends': [46, 47]}, {'ends': [20, 21]}, {'ends': [44, 45]}, {'ends': [24, 25]}, {'ends': [48, 49]}, {'ends': [54, 55]}, {'ends': [40, 41]}, {'ends': [32, 33]}, {'ends': [42, 43]}, {'ends': [52, 53]}, {'ends': [38, 39]}, {'ends': [22, 23]}, {'ends': [28, 29]}, {'ends': [26, 27]}, {'ends': [58, 59]}, {'ends': [34, 35]}, {'ends': [56, 57]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MedianAndPercentiles', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['median_consecutive'], 'matched_capabilities': ['median_consecutive'], 'selected_operation': 'median_consecutive', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['list_summary_stats', 'median_consecutive', 'median_lists', 'percentile_frequency', 'quartile_frequency', 'statement_selection', 'true_false_stat'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MedianAndPercentiles'}), seed)
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
