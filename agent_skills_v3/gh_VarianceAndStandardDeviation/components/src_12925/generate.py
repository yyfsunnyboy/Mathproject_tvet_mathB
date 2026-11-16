from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "standard_deviation"
TEXTBOOK_EXAMPLE_ID = 12925
DEFAULT_COMPONENT_ID = "src_12925" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_VarianceAndStandardDeviation"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "standard_deviation"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['standard_deviation'], 'domain_operation': 'standard_deviation', 'problem_type_id': 'standard_deviation', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'lists': [[2, 5, 6, 9]]}, {'lists': [[19, 15, 16, 12]]}, {'lists': [[1, 4, 5, 7, 13], [19, 18, 10, 3]]}, {'lists': [[9, 6, 13, 18], [8, 8, 4, 4]]}, {'lists': [[9, 9, 13, 13], [5, 11, 13, 19]]}, {'lists': [[20, 5, 5, 20], [5, 11, 3, 5]]}, {'lists': [[17, 9, 11, 3]]}, {'lists': [[2, 9, 6, 5]]}, {'lists': [[15, 12, 7, 16], [1, 4, 5, 7, 13]]}, {'lists': [[13, 10, 9, 6]]}, {'lists': [[15, 15, 19, 3], [1, 4, 5, 7, 13]]}, {'lists': [[8, 7, 4, 11]]}, {'lists': [[1, 4, 5, 7, 13], [13, 9, 9, 13]]}, {'lists': [[1, 4, 5, 7, 13], [20, 20, 15, 15]]}, {'lists': [[17, 13, 13, 1]]}, {'lists': [[7, 20, 7, 20], [7, 4, 16, 7]]}, {'lists': [[14, 13, 14, 13]]}, {'lists': [[16, 20, 13, 5]]}, {'lists': [[12, 18, 12, 10]]}, {'lists': [[1, 4, 5, 7, 13], [19, 2, 14, 7]]}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['standard_deviation'], 'domain_operation': 'standard_deviation', 'problem_type_id': 'standard_deviation', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'lists': [[2, 5, 6, 9]]}, {'lists': [[19, 15, 16, 12]]}, {'lists': [[1, 4, 5, 7, 13], [19, 18, 10, 3]]}, {'lists': [[9, 6, 13, 18], [8, 8, 4, 4]]}, {'lists': [[9, 9, 13, 13], [5, 11, 13, 19]]}, {'lists': [[20, 5, 5, 20], [5, 11, 3, 5]]}, {'lists': [[17, 9, 11, 3]]}, {'lists': [[2, 9, 6, 5]]}, {'lists': [[15, 12, 7, 16], [1, 4, 5, 7, 13]]}, {'lists': [[13, 10, 9, 6]]}, {'lists': [[15, 15, 19, 3], [1, 4, 5, 7, 13]]}, {'lists': [[8, 7, 4, 11]]}, {'lists': [[1, 4, 5, 7, 13], [13, 9, 9, 13]]}, {'lists': [[1, 4, 5, 7, 13], [20, 20, 15, 15]]}, {'lists': [[17, 13, 13, 1]]}, {'lists': [[7, 20, 7, 20], [7, 4, 16, 7]]}, {'lists': [[14, 13, 14, 13]]}, {'lists': [[16, 20, 13, 5]]}, {'lists': [[12, 18, 12, 10]]}, {'lists': [[1, 4, 5, 7, 13], [19, 2, 14, 7]]}]}}, 'problem_type_id': 'standard_deviation', 'required_capabilities': ['standard_deviation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'lists': [[2, 5, 6, 9]]}, {'lists': [[19, 15, 16, 12]]}, {'lists': [[1, 4, 5, 7, 13], [19, 18, 10, 3]]}, {'lists': [[9, 6, 13, 18], [8, 8, 4, 4]]}, {'lists': [[9, 9, 13, 13], [5, 11, 13, 19]]}, {'lists': [[20, 5, 5, 20], [5, 11, 3, 5]]}, {'lists': [[17, 9, 11, 3]]}, {'lists': [[2, 9, 6, 5]]}, {'lists': [[15, 12, 7, 16], [1, 4, 5, 7, 13]]}, {'lists': [[13, 10, 9, 6]]}, {'lists': [[15, 15, 19, 3], [1, 4, 5, 7, 13]]}, {'lists': [[8, 7, 4, 11]]}, {'lists': [[1, 4, 5, 7, 13], [13, 9, 9, 13]]}, {'lists': [[1, 4, 5, 7, 13], [20, 20, 15, 15]]}, {'lists': [[17, 13, 13, 1]]}, {'lists': [[7, 20, 7, 20], [7, 4, 16, 7]]}, {'lists': [[14, 13, 14, 13]]}, {'lists': [[16, 20, 13, 5]]}, {'lists': [[12, 18, 12, 10]]}, {'lists': [[1, 4, 5, 7, 13], [19, 2, 14, 7]]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_VarianceAndStandardDeviation', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['standard_deviation'], 'matched_capabilities': ['standard_deviation'], 'selected_operation': 'standard_deviation', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['compare_standard_deviation', 'grade_distribution_read', 'mean_variance_sd', 'standard_deviation', 'true_false_stat', 'unknown_given_sd'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_VarianceAndStandardDeviation'}), seed)
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
