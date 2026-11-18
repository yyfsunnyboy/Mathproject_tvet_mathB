from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "correlation_remove_point"
TEXTBOOK_EXAMPLE_ID = 12959
DEFAULT_COMPONENT_ID = "src_12959" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CorrelationCoefficient"
FIXED_DOMAIN_KEY = "statistics.bivariate_descriptive"
DOMAIN_OPERATION = "correlation_remove_point"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['correlation_remove_point'], 'domain_operation': 'correlation_remove_point', 'problem_type_id': 'correlation_remove_point', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [2, 4, 5, 10, 10], 'y': [3, 4, 6, 1, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [10, 10, 5, 1, 11], 'y': [4, 9, 7, 9, 7]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [3, 7, 8, 10, 12], 'y': [1, 2, 11, 7, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [6, 2, 10, 6, 8], 'y': [9, 3, 9, 2, 6]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [6, 4, 4, 9, 6], 'y': [3, 1, 6, 3, 1]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [9, 12, 5, 2, 8], 'y': [11, 4, 7, 3, 6]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [9, 3, 2, 4, 8], 'y': [5, 8, 12, 3, 6]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [1, 1, 6, 5, 1], 'y': [4, 5, 5, 5, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [6, 2, 7, 10, 9], 'y': [1, 11, 12, 9, 3]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [9, 10, 11, 5, 2], 'y': [4, 8, 12, 10, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [11, 10, 12, 7, 10], 'y': [5, 9, 8, 3, 12]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [7, 11, 10, 5, 3], 'y': [10, 3, 4, 10, 5]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [2, 3, 8, 8, 5], 'y': [5, 1, 12, 11, 12]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [8, 12, 7, 11, 12], 'y': [3, 4, 9, 4, 3]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [1, 8, 8, 6, 11], 'y': [11, 4, 1, 3, 2]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [11, 8, 12, 5, 1], 'y': [6, 11, 1, 7, 12]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [10, 8, 11, 6, 5], 'y': [8, 10, 2, 8, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [6, 3, 2, 10, 10], 'y': [6, 12, 9, 10, 7]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [2, 6, 6, 3, 7], 'y': [11, 10, 10, 7, 7]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [1, 2, 10, 8, 3], 'y': [12, 7, 10, 1, 6]}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['correlation_remove_point'], 'domain_operation': 'correlation_remove_point', 'problem_type_id': 'correlation_remove_point', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [2, 4, 5, 10, 10], 'y': [3, 4, 6, 1, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [10, 10, 5, 1, 11], 'y': [4, 9, 7, 9, 7]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [3, 7, 8, 10, 12], 'y': [1, 2, 11, 7, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [6, 2, 10, 6, 8], 'y': [9, 3, 9, 2, 6]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [6, 4, 4, 9, 6], 'y': [3, 1, 6, 3, 1]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [9, 12, 5, 2, 8], 'y': [11, 4, 7, 3, 6]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [9, 3, 2, 4, 8], 'y': [5, 8, 12, 3, 6]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [1, 1, 6, 5, 1], 'y': [4, 5, 5, 5, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [6, 2, 7, 10, 9], 'y': [1, 11, 12, 9, 3]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [9, 10, 11, 5, 2], 'y': [4, 8, 12, 10, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [11, 10, 12, 7, 10], 'y': [5, 9, 8, 3, 12]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [7, 11, 10, 5, 3], 'y': [10, 3, 4, 10, 5]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [2, 3, 8, 8, 5], 'y': [5, 1, 12, 11, 12]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [8, 12, 7, 11, 12], 'y': [3, 4, 9, 4, 3]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [1, 8, 8, 6, 11], 'y': [11, 4, 1, 3, 2]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [11, 8, 12, 5, 1], 'y': [6, 11, 1, 7, 12]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [10, 8, 11, 6, 5], 'y': [8, 10, 2, 8, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [6, 3, 2, 10, 10], 'y': [6, 12, 9, 10, 7]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [2, 6, 6, 3, 7], 'y': [11, 10, 10, 7, 7]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [1, 2, 10, 8, 3], 'y': [12, 7, 10, 1, 6]}]}}, 'problem_type_id': 'correlation_remove_point', 'required_capabilities': ['correlation_remove_point'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [2, 4, 5, 10, 10], 'y': [3, 4, 6, 1, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [10, 10, 5, 1, 11], 'y': [4, 9, 7, 9, 7]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [3, 7, 8, 10, 12], 'y': [1, 2, 11, 7, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [6, 2, 10, 6, 8], 'y': [9, 3, 9, 2, 6]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [6, 4, 4, 9, 6], 'y': [3, 1, 6, 3, 1]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [9, 12, 5, 2, 8], 'y': [11, 4, 7, 3, 6]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [9, 3, 2, 4, 8], 'y': [5, 8, 12, 3, 6]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [1, 1, 6, 5, 1], 'y': [4, 5, 5, 5, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [6, 2, 7, 10, 9], 'y': [1, 11, 12, 9, 3]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [9, 10, 11, 5, 2], 'y': [4, 8, 12, 10, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [11, 10, 12, 7, 10], 'y': [5, 9, 8, 3, 12]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [7, 11, 10, 5, 3], 'y': [10, 3, 4, 10, 5]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [2, 3, 8, 8, 5], 'y': [5, 1, 12, 11, 12]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [8, 12, 7, 11, 12], 'y': [3, 4, 9, 4, 3]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [1, 8, 8, 6, 11], 'y': [11, 4, 1, 3, 2]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [11, 8, 12, 5, 1], 'y': [6, 11, 1, 7, 12]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [10, 8, 11, 6, 5], 'y': [8, 10, 2, 8, 11]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [6, 3, 2, 10, 10], 'y': [6, 12, 9, 10, 7]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [2, 6, 6, 3, 7], 'y': [11, 10, 10, 7, 7]}, {'labels': ['A', 'B', 'C', 'D', 'E'], 'x': [1, 2, 10, 8, 3], 'y': [12, 7, 10, 1, 6]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_CorrelationCoefficient', 'fixed_domain_key': 'statistics.bivariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['correlation_remove_point'], 'matched_capabilities': ['correlation_remove_point'], 'selected_operation': 'correlation_remove_point', 'registry_revision': 'promoted-f99c60060e70', 'domain_module': 'core.domain.promoted.bivariate_statistics.bivariate_statistics_domain', 'entrypoint': 'build_bivariate_statistics_matrix', 'allowed_operations': ['correlation_change_add_point', 'correlation_from_table', 'correlation_remove_point', 'correlation_rescale', 'true_false_bivariate'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_CorrelationCoefficient'}), seed)
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
