from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "median_lists"
TEXTBOOK_EXAMPLE_ID = 12918
DEFAULT_COMPONENT_ID = "src_12918" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MedianAndPercentiles"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "median_lists"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['median_lists'], 'domain_operation': 'median_lists', 'problem_type_id': 'median_lists', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'lists': [[8, 4, 9, 1, 6], [8, 4, 9, 1, 6, 8]]}, {'lists': [[20, 19, 12, 2, 12], [7, 3, 7, 13, 14, 11]]}, {'lists': [[5, 15, 13, 13, 7], [1, 17, 3, 19, 1, 5]]}, {'lists': [[4, 14, 11, 3, 11], [7, 8, 3, 13, 3, 19]]}, {'lists': [[7, 18, 17, 19, 6], [15, 11, 20, 6, 20, 15]]}, {'lists': [[9, 9, 7, 13, 13], [8, 9, 7, 15, 10, 7]]}, {'lists': [[20, 5, 15, 10, 20], [14, 10, 20, 7, 19, 10]]}, {'lists': [[20, 7, 16, 17, 16], [14, 18, 17, 17, 2, 19]]}, {'lists': [[8, 19, 8, 13, 19], [7, 4, 3, 2, 15, 12]]}, {'lists': [[7, 9, 6, 4, 18], [18, 17, 6, 8, 1, 4]]}, {'lists': [[11, 8, 3, 18, 16], [12, 2, 2, 4, 10, 16]]}, {'lists': [[7, 8, 5, 12, 16], [5, 8, 20, 10, 16, 19]]}, {'lists': [[18, 13, 15, 18, 5], [1, 12, 13, 4, 9, 8]]}, {'lists': [[5, 16, 2, 20, 10], [19, 20, 11, 18, 11, 10]]}, {'lists': [[4, 19, 18, 17, 7], [14, 7, 14, 18, 1, 9]]}, {'lists': [[13, 5, 12, 8, 5], [20, 9, 5, 4, 15, 2]]}, {'lists': [[17, 11, 3, 11, 10], [8, 14, 8, 3, 1, 6]]}, {'lists': [[2, 20, 2, 6, 20], [1, 20, 11, 17, 1, 9]]}, {'lists': [[4, 8, 4, 7, 17], [14, 14, 15, 8, 4, 5]]}, {'lists': [[10, 3, 5, 5, 16], [16, 5, 16, 19, 18, 17]]}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['median_lists'], 'domain_operation': 'median_lists', 'problem_type_id': 'median_lists', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'lists': [[8, 4, 9, 1, 6], [8, 4, 9, 1, 6, 8]]}, {'lists': [[20, 19, 12, 2, 12], [7, 3, 7, 13, 14, 11]]}, {'lists': [[5, 15, 13, 13, 7], [1, 17, 3, 19, 1, 5]]}, {'lists': [[4, 14, 11, 3, 11], [7, 8, 3, 13, 3, 19]]}, {'lists': [[7, 18, 17, 19, 6], [15, 11, 20, 6, 20, 15]]}, {'lists': [[9, 9, 7, 13, 13], [8, 9, 7, 15, 10, 7]]}, {'lists': [[20, 5, 15, 10, 20], [14, 10, 20, 7, 19, 10]]}, {'lists': [[20, 7, 16, 17, 16], [14, 18, 17, 17, 2, 19]]}, {'lists': [[8, 19, 8, 13, 19], [7, 4, 3, 2, 15, 12]]}, {'lists': [[7, 9, 6, 4, 18], [18, 17, 6, 8, 1, 4]]}, {'lists': [[11, 8, 3, 18, 16], [12, 2, 2, 4, 10, 16]]}, {'lists': [[7, 8, 5, 12, 16], [5, 8, 20, 10, 16, 19]]}, {'lists': [[18, 13, 15, 18, 5], [1, 12, 13, 4, 9, 8]]}, {'lists': [[5, 16, 2, 20, 10], [19, 20, 11, 18, 11, 10]]}, {'lists': [[4, 19, 18, 17, 7], [14, 7, 14, 18, 1, 9]]}, {'lists': [[13, 5, 12, 8, 5], [20, 9, 5, 4, 15, 2]]}, {'lists': [[17, 11, 3, 11, 10], [8, 14, 8, 3, 1, 6]]}, {'lists': [[2, 20, 2, 6, 20], [1, 20, 11, 17, 1, 9]]}, {'lists': [[4, 8, 4, 7, 17], [14, 14, 15, 8, 4, 5]]}, {'lists': [[10, 3, 5, 5, 16], [16, 5, 16, 19, 18, 17]]}]}}, 'problem_type_id': 'median_lists', 'required_capabilities': ['median_lists'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'lists': [[8, 4, 9, 1, 6], [8, 4, 9, 1, 6, 8]]}, {'lists': [[20, 19, 12, 2, 12], [7, 3, 7, 13, 14, 11]]}, {'lists': [[5, 15, 13, 13, 7], [1, 17, 3, 19, 1, 5]]}, {'lists': [[4, 14, 11, 3, 11], [7, 8, 3, 13, 3, 19]]}, {'lists': [[7, 18, 17, 19, 6], [15, 11, 20, 6, 20, 15]]}, {'lists': [[9, 9, 7, 13, 13], [8, 9, 7, 15, 10, 7]]}, {'lists': [[20, 5, 15, 10, 20], [14, 10, 20, 7, 19, 10]]}, {'lists': [[20, 7, 16, 17, 16], [14, 18, 17, 17, 2, 19]]}, {'lists': [[8, 19, 8, 13, 19], [7, 4, 3, 2, 15, 12]]}, {'lists': [[7, 9, 6, 4, 18], [18, 17, 6, 8, 1, 4]]}, {'lists': [[11, 8, 3, 18, 16], [12, 2, 2, 4, 10, 16]]}, {'lists': [[7, 8, 5, 12, 16], [5, 8, 20, 10, 16, 19]]}, {'lists': [[18, 13, 15, 18, 5], [1, 12, 13, 4, 9, 8]]}, {'lists': [[5, 16, 2, 20, 10], [19, 20, 11, 18, 11, 10]]}, {'lists': [[4, 19, 18, 17, 7], [14, 7, 14, 18, 1, 9]]}, {'lists': [[13, 5, 12, 8, 5], [20, 9, 5, 4, 15, 2]]}, {'lists': [[17, 11, 3, 11, 10], [8, 14, 8, 3, 1, 6]]}, {'lists': [[2, 20, 2, 6, 20], [1, 20, 11, 17, 1, 9]]}, {'lists': [[4, 8, 4, 7, 17], [14, 14, 15, 8, 4, 5]]}, {'lists': [[10, 3, 5, 5, 16], [16, 5, 16, 19, 18, 17]]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MedianAndPercentiles', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['median_lists'], 'matched_capabilities': ['median_lists'], 'selected_operation': 'median_lists', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['list_summary_stats', 'median_consecutive', 'median_lists', 'percentile_frequency', 'quartile_frequency', 'statement_selection', 'true_false_stat'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MedianAndPercentiles'}), seed)
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
