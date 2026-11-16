from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "compare_standard_deviation"
TEXTBOOK_EXAMPLE_ID = 12928
DEFAULT_COMPONENT_ID = "src_12928" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_VarianceAndStandardDeviation"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "compare_standard_deviation"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['compare_standard_deviation'], 'domain_operation': 'compare_standard_deviation', 'problem_type_id': 'compare_standard_deviation', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'lists': [[5, 5, 5, 5, 5], [1, 3, 5, 7, 9], [3, 4, 5, 6, 7]]}, {'lists': [[6, 9, 12, 15, 18], [12, 12, 12, 12, 12], [10, 12, 12, 12, 14]]}, {'lists': [[8, 14, 14, 14, 20], [10, 14, 14, 14, 18], [14, 14, 14, 14, 14]]}, {'lists': [[10, 10, 10, 10, 10], [8, 10, 10, 10, 12], [4, 10, 10, 10, 16]]}, {'lists': [[15, 15, 15, 15, 15], [9, 15, 15, 15, 21], [13, 13, 15, 17, 17]]}, {'lists': [[7, 10, 13, 16, 19], [9, 13, 13, 13, 17], [13, 13, 13, 13, 13]]}, {'lists': [[9, 12, 15, 18, 21], [7, 11, 15, 19, 23], [15, 15, 15, 15, 15]]}, {'lists': [[9, 9, 9, 9, 9], [8, 8, 9, 10, 10], [3, 9, 9, 9, 15]]}, {'lists': [[6, 10, 10, 10, 14], [10, 10, 10, 10, 10], [2, 6, 10, 14, 18]]}, {'lists': [[4, 7, 10, 13, 16], [10, 10, 10, 10, 10], [6, 8, 10, 12, 14]]}, {'lists': [[14, 14, 14, 14, 14], [6, 14, 14, 14, 22], [8, 11, 14, 17, 20]]}, {'lists': [[9, 9, 9, 9, 9], [1, 9, 9, 9, 17], [7, 8, 9, 10, 11]]}, {'lists': [[15, 15, 15, 15, 15], [7, 11, 15, 19, 23], [11, 13, 15, 17, 19]]}, {'lists': [[1, 5, 9, 13, 17], [9, 9, 9, 9, 9], [7, 8, 9, 10, 11]]}, {'lists': [[9, 9, 9, 9, 9], [1, 9, 9, 9, 17], [5, 7, 9, 11, 13]]}, {'lists': [[12, 12, 12, 12, 12], [6, 12, 12, 12, 18], [8, 10, 12, 14, 16]]}, {'lists': [[6, 12, 12, 12, 18], [12, 12, 12, 12, 12], [4, 8, 12, 16, 20]]}, {'lists': [[8, 11, 14, 17, 20], [14, 14, 14, 14, 14], [13, 13, 14, 15, 15]]}, {'lists': [[15, 15, 15, 15, 15], [13, 14, 15, 16, 17], [9, 12, 15, 18, 21]]}, {'lists': [[13, 14, 15, 16, 17], [11, 13, 15, 17, 19], [15, 15, 15, 15, 15]]}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['compare_standard_deviation'], 'domain_operation': 'compare_standard_deviation', 'problem_type_id': 'compare_standard_deviation', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'lists': [[5, 5, 5, 5, 5], [1, 3, 5, 7, 9], [3, 4, 5, 6, 7]]}, {'lists': [[6, 9, 12, 15, 18], [12, 12, 12, 12, 12], [10, 12, 12, 12, 14]]}, {'lists': [[8, 14, 14, 14, 20], [10, 14, 14, 14, 18], [14, 14, 14, 14, 14]]}, {'lists': [[10, 10, 10, 10, 10], [8, 10, 10, 10, 12], [4, 10, 10, 10, 16]]}, {'lists': [[15, 15, 15, 15, 15], [9, 15, 15, 15, 21], [13, 13, 15, 17, 17]]}, {'lists': [[7, 10, 13, 16, 19], [9, 13, 13, 13, 17], [13, 13, 13, 13, 13]]}, {'lists': [[9, 12, 15, 18, 21], [7, 11, 15, 19, 23], [15, 15, 15, 15, 15]]}, {'lists': [[9, 9, 9, 9, 9], [8, 8, 9, 10, 10], [3, 9, 9, 9, 15]]}, {'lists': [[6, 10, 10, 10, 14], [10, 10, 10, 10, 10], [2, 6, 10, 14, 18]]}, {'lists': [[4, 7, 10, 13, 16], [10, 10, 10, 10, 10], [6, 8, 10, 12, 14]]}, {'lists': [[14, 14, 14, 14, 14], [6, 14, 14, 14, 22], [8, 11, 14, 17, 20]]}, {'lists': [[9, 9, 9, 9, 9], [1, 9, 9, 9, 17], [7, 8, 9, 10, 11]]}, {'lists': [[15, 15, 15, 15, 15], [7, 11, 15, 19, 23], [11, 13, 15, 17, 19]]}, {'lists': [[1, 5, 9, 13, 17], [9, 9, 9, 9, 9], [7, 8, 9, 10, 11]]}, {'lists': [[9, 9, 9, 9, 9], [1, 9, 9, 9, 17], [5, 7, 9, 11, 13]]}, {'lists': [[12, 12, 12, 12, 12], [6, 12, 12, 12, 18], [8, 10, 12, 14, 16]]}, {'lists': [[6, 12, 12, 12, 18], [12, 12, 12, 12, 12], [4, 8, 12, 16, 20]]}, {'lists': [[8, 11, 14, 17, 20], [14, 14, 14, 14, 14], [13, 13, 14, 15, 15]]}, {'lists': [[15, 15, 15, 15, 15], [13, 14, 15, 16, 17], [9, 12, 15, 18, 21]]}, {'lists': [[13, 14, 15, 16, 17], [11, 13, 15, 17, 19], [15, 15, 15, 15, 15]]}]}}, 'problem_type_id': 'compare_standard_deviation', 'required_capabilities': ['compare_standard_deviation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'lists': [[5, 5, 5, 5, 5], [1, 3, 5, 7, 9], [3, 4, 5, 6, 7]]}, {'lists': [[6, 9, 12, 15, 18], [12, 12, 12, 12, 12], [10, 12, 12, 12, 14]]}, {'lists': [[8, 14, 14, 14, 20], [10, 14, 14, 14, 18], [14, 14, 14, 14, 14]]}, {'lists': [[10, 10, 10, 10, 10], [8, 10, 10, 10, 12], [4, 10, 10, 10, 16]]}, {'lists': [[15, 15, 15, 15, 15], [9, 15, 15, 15, 21], [13, 13, 15, 17, 17]]}, {'lists': [[7, 10, 13, 16, 19], [9, 13, 13, 13, 17], [13, 13, 13, 13, 13]]}, {'lists': [[9, 12, 15, 18, 21], [7, 11, 15, 19, 23], [15, 15, 15, 15, 15]]}, {'lists': [[9, 9, 9, 9, 9], [8, 8, 9, 10, 10], [3, 9, 9, 9, 15]]}, {'lists': [[6, 10, 10, 10, 14], [10, 10, 10, 10, 10], [2, 6, 10, 14, 18]]}, {'lists': [[4, 7, 10, 13, 16], [10, 10, 10, 10, 10], [6, 8, 10, 12, 14]]}, {'lists': [[14, 14, 14, 14, 14], [6, 14, 14, 14, 22], [8, 11, 14, 17, 20]]}, {'lists': [[9, 9, 9, 9, 9], [1, 9, 9, 9, 17], [7, 8, 9, 10, 11]]}, {'lists': [[15, 15, 15, 15, 15], [7, 11, 15, 19, 23], [11, 13, 15, 17, 19]]}, {'lists': [[1, 5, 9, 13, 17], [9, 9, 9, 9, 9], [7, 8, 9, 10, 11]]}, {'lists': [[9, 9, 9, 9, 9], [1, 9, 9, 9, 17], [5, 7, 9, 11, 13]]}, {'lists': [[12, 12, 12, 12, 12], [6, 12, 12, 12, 18], [8, 10, 12, 14, 16]]}, {'lists': [[6, 12, 12, 12, 18], [12, 12, 12, 12, 12], [4, 8, 12, 16, 20]]}, {'lists': [[8, 11, 14, 17, 20], [14, 14, 14, 14, 14], [13, 13, 14, 15, 15]]}, {'lists': [[15, 15, 15, 15, 15], [13, 14, 15, 16, 17], [9, 12, 15, 18, 21]]}, {'lists': [[13, 14, 15, 16, 17], [11, 13, 15, 17, 19], [15, 15, 15, 15, 15]]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_VarianceAndStandardDeviation', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['compare_standard_deviation'], 'matched_capabilities': ['compare_standard_deviation'], 'selected_operation': 'compare_standard_deviation', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['compare_standard_deviation', 'grade_distribution_read', 'mean_variance_sd', 'standard_deviation', 'true_false_stat', 'unknown_given_sd'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_VarianceAndStandardDeviation'}), seed)
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
