from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "unknown_given_sd"
TEXTBOOK_EXAMPLE_ID = 12940
DEFAULT_COMPONENT_ID = "src_12940" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_VarianceAndStandardDeviation"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "unknown_given_sd"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['unknown_given_sd'], 'domain_operation': 'unknown_given_sd', 'problem_type_id': 'unknown_given_sd', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'prefix': [2, 6, 14], 'suffix': [18], 'sd': 6}, {'prefix': [22, 25, 31], 'suffix': [39], 'sd': 6}, {'prefix': [8, 22, 26], 'suffix': [30], 'sd': 8}, {'prefix': [1, 5, 7], 'suffix': [29], 'sd': 12}, {'prefix': [13, 24, 25], 'suffix': [37], 'sd': 8}, {'prefix': [16, 22, 24], 'suffix': [40], 'sd': 8}, {'prefix': [17, 19, 23], 'suffix': [36], 'sd': 8}, {'prefix': [4, 8, 12], 'suffix': [26], 'sd': 8}, {'prefix': [11, 12, 13], 'suffix': [35], 'sd': 10}, {'prefix': [6, 12, 14], 'suffix': [30], 'sd': 8}, {'prefix': [16, 19, 22], 'suffix': [38], 'sd': 8}, {'prefix': [12, 14, 20], 'suffix': [38], 'sd': 10}, {'prefix': [4, 8, 16], 'suffix': [25], 'sd': 8}, {'prefix': [3, 15, 24], 'suffix': [31], 'sd': 10}, {'prefix': [13, 31, 37], 'suffix': [40], 'sd': 10}, {'prefix': [7, 11, 20], 'suffix': [29], 'sd': 8}, {'prefix': [14, 16, 32], 'suffix': [38], 'sd': 10}, {'prefix': [11, 12, 24], 'suffix': [30], 'sd': 8}, {'prefix': [2, 5, 11], 'suffix': [23], 'sd': 8}, {'prefix': [14, 17, 23], 'suffix': [35], 'sd': 8}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['unknown_given_sd'], 'domain_operation': 'unknown_given_sd', 'problem_type_id': 'unknown_given_sd', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'prefix': [2, 6, 14], 'suffix': [18], 'sd': 6}, {'prefix': [22, 25, 31], 'suffix': [39], 'sd': 6}, {'prefix': [8, 22, 26], 'suffix': [30], 'sd': 8}, {'prefix': [1, 5, 7], 'suffix': [29], 'sd': 12}, {'prefix': [13, 24, 25], 'suffix': [37], 'sd': 8}, {'prefix': [16, 22, 24], 'suffix': [40], 'sd': 8}, {'prefix': [17, 19, 23], 'suffix': [36], 'sd': 8}, {'prefix': [4, 8, 12], 'suffix': [26], 'sd': 8}, {'prefix': [11, 12, 13], 'suffix': [35], 'sd': 10}, {'prefix': [6, 12, 14], 'suffix': [30], 'sd': 8}, {'prefix': [16, 19, 22], 'suffix': [38], 'sd': 8}, {'prefix': [12, 14, 20], 'suffix': [38], 'sd': 10}, {'prefix': [4, 8, 16], 'suffix': [25], 'sd': 8}, {'prefix': [3, 15, 24], 'suffix': [31], 'sd': 10}, {'prefix': [13, 31, 37], 'suffix': [40], 'sd': 10}, {'prefix': [7, 11, 20], 'suffix': [29], 'sd': 8}, {'prefix': [14, 16, 32], 'suffix': [38], 'sd': 10}, {'prefix': [11, 12, 24], 'suffix': [30], 'sd': 8}, {'prefix': [2, 5, 11], 'suffix': [23], 'sd': 8}, {'prefix': [14, 17, 23], 'suffix': [35], 'sd': 8}]}}, 'problem_type_id': 'unknown_given_sd', 'required_capabilities': ['unknown_given_sd'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'prefix': [2, 6, 14], 'suffix': [18], 'sd': 6}, {'prefix': [22, 25, 31], 'suffix': [39], 'sd': 6}, {'prefix': [8, 22, 26], 'suffix': [30], 'sd': 8}, {'prefix': [1, 5, 7], 'suffix': [29], 'sd': 12}, {'prefix': [13, 24, 25], 'suffix': [37], 'sd': 8}, {'prefix': [16, 22, 24], 'suffix': [40], 'sd': 8}, {'prefix': [17, 19, 23], 'suffix': [36], 'sd': 8}, {'prefix': [4, 8, 12], 'suffix': [26], 'sd': 8}, {'prefix': [11, 12, 13], 'suffix': [35], 'sd': 10}, {'prefix': [6, 12, 14], 'suffix': [30], 'sd': 8}, {'prefix': [16, 19, 22], 'suffix': [38], 'sd': 8}, {'prefix': [12, 14, 20], 'suffix': [38], 'sd': 10}, {'prefix': [4, 8, 16], 'suffix': [25], 'sd': 8}, {'prefix': [3, 15, 24], 'suffix': [31], 'sd': 10}, {'prefix': [13, 31, 37], 'suffix': [40], 'sd': 10}, {'prefix': [7, 11, 20], 'suffix': [29], 'sd': 8}, {'prefix': [14, 16, 32], 'suffix': [38], 'sd': 10}, {'prefix': [11, 12, 24], 'suffix': [30], 'sd': 8}, {'prefix': [2, 5, 11], 'suffix': [23], 'sd': 8}, {'prefix': [14, 17, 23], 'suffix': [35], 'sd': 8}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_VarianceAndStandardDeviation', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['unknown_given_sd'], 'matched_capabilities': ['unknown_given_sd'], 'selected_operation': 'unknown_given_sd', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['compare_standard_deviation', 'grade_distribution_read', 'mean_variance_sd', 'standard_deviation', 'true_false_stat', 'unknown_given_sd'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_VarianceAndStandardDeviation'}), seed)
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
