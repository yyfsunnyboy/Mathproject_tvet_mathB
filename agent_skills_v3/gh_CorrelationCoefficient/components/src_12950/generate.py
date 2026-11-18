from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "correlation_from_table"
TEXTBOOK_EXAMPLE_ID = 12950
DEFAULT_COMPONENT_ID = "src_12950" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CorrelationCoefficient"
FIXED_DOMAIN_KEY = "statistics.bivariate_descriptive"
DOMAIN_OPERATION = "correlation_from_table"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['correlation_from_table'], 'domain_operation': 'correlation_from_table', 'problem_type_id': 'correlation_from_table', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'x': [1, 2, 3, 4, 5], 'y': [4, 5, 3, 1, 2], 'scene': 'plain'}, {'x': [4, 8, 11, 12, 15], 'y': [11, 5, 11, 1, 1], 'scene': 'plain'}, {'x': [3, 6, 7, 8, 13], 'y': [8, 11, 1, 6, 6], 'scene': 'plain'}, {'x': [3, 4, 7, 11, 13, 14], 'y': [14, 7, 16, 4, 8, 13], 'scene': 'plain'}, {'x': [1, 5, 10, 12, 13], 'y': [2, 13, 15, 8, 8], 'scene': 'plain'}, {'x': [2, 4, 7, 11, 12, 14], 'y': [6, 15, 7, 14, 3, 7], 'scene': 'plain'}, {'x': [2, 3, 6, 7, 11, 14], 'y': [9, 7, 8, 11, 2, 16], 'scene': 'plain'}, {'x': [3, 4, 5, 11, 12, 15], 'y': [14, 2, 1, 6, 4, 1], 'scene': 'plain'}, {'x': [2, 3, 5, 7, 9], 'y': [15, 1, 3, 2, 7], 'scene': 'plain'}, {'x': [4, 6, 8, 9, 12], 'y': [8, 6, 4, 12, 9], 'scene': 'plain'}, {'x': [2, 3, 5, 8, 10, 13], 'y': [10, 8, 3, 5, 6, 15], 'scene': 'plain'}, {'x': [1, 3, 5, 9, 12, 13], 'y': [16, 15, 7, 9, 9, 3], 'scene': 'plain'}, {'x': [1, 2, 4, 7, 10, 12], 'y': [14, 13, 13, 12, 1, 7], 'scene': 'plain'}, {'x': [2, 3, 6, 8, 11], 'y': [4, 8, 8, 16, 14], 'scene': 'plain'}, {'x': [1, 3, 8, 9, 11, 12], 'y': [11, 14, 2, 7, 9, 13], 'scene': 'plain'}, {'x': [3, 4, 5, 6, 7, 8], 'y': [2, 3, 4, 5, 6, 7], 'scene': 'plain'}, {'x': [1, 2, 3, 5, 9, 11], 'y': [8, 12, 10, 1, 8, 4], 'scene': 'plain'}, {'x': [1, 3, 10, 12, 14, 15], 'y': [15, 5, 11, 3, 5, 11], 'scene': 'plain'}, {'x': [2, 5, 7, 10, 11, 14], 'y': [11, 10, 8, 14, 9, 1], 'scene': 'plain'}, {'x': [2, 5, 8, 9, 11], 'y': [4, 13, 10, 14, 14], 'scene': 'plain'}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['correlation_from_table'], 'domain_operation': 'correlation_from_table', 'problem_type_id': 'correlation_from_table', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'x': [1, 2, 3, 4, 5], 'y': [4, 5, 3, 1, 2], 'scene': 'plain'}, {'x': [4, 8, 11, 12, 15], 'y': [11, 5, 11, 1, 1], 'scene': 'plain'}, {'x': [3, 6, 7, 8, 13], 'y': [8, 11, 1, 6, 6], 'scene': 'plain'}, {'x': [3, 4, 7, 11, 13, 14], 'y': [14, 7, 16, 4, 8, 13], 'scene': 'plain'}, {'x': [1, 5, 10, 12, 13], 'y': [2, 13, 15, 8, 8], 'scene': 'plain'}, {'x': [2, 4, 7, 11, 12, 14], 'y': [6, 15, 7, 14, 3, 7], 'scene': 'plain'}, {'x': [2, 3, 6, 7, 11, 14], 'y': [9, 7, 8, 11, 2, 16], 'scene': 'plain'}, {'x': [3, 4, 5, 11, 12, 15], 'y': [14, 2, 1, 6, 4, 1], 'scene': 'plain'}, {'x': [2, 3, 5, 7, 9], 'y': [15, 1, 3, 2, 7], 'scene': 'plain'}, {'x': [4, 6, 8, 9, 12], 'y': [8, 6, 4, 12, 9], 'scene': 'plain'}, {'x': [2, 3, 5, 8, 10, 13], 'y': [10, 8, 3, 5, 6, 15], 'scene': 'plain'}, {'x': [1, 3, 5, 9, 12, 13], 'y': [16, 15, 7, 9, 9, 3], 'scene': 'plain'}, {'x': [1, 2, 4, 7, 10, 12], 'y': [14, 13, 13, 12, 1, 7], 'scene': 'plain'}, {'x': [2, 3, 6, 8, 11], 'y': [4, 8, 8, 16, 14], 'scene': 'plain'}, {'x': [1, 3, 8, 9, 11, 12], 'y': [11, 14, 2, 7, 9, 13], 'scene': 'plain'}, {'x': [3, 4, 5, 6, 7, 8], 'y': [2, 3, 4, 5, 6, 7], 'scene': 'plain'}, {'x': [1, 2, 3, 5, 9, 11], 'y': [8, 12, 10, 1, 8, 4], 'scene': 'plain'}, {'x': [1, 3, 10, 12, 14, 15], 'y': [15, 5, 11, 3, 5, 11], 'scene': 'plain'}, {'x': [2, 5, 7, 10, 11, 14], 'y': [11, 10, 8, 14, 9, 1], 'scene': 'plain'}, {'x': [2, 5, 8, 9, 11], 'y': [4, 13, 10, 14, 14], 'scene': 'plain'}]}}, 'problem_type_id': 'correlation_from_table', 'required_capabilities': ['correlation_from_table'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'x': [1, 2, 3, 4, 5], 'y': [4, 5, 3, 1, 2], 'scene': 'plain'}, {'x': [4, 8, 11, 12, 15], 'y': [11, 5, 11, 1, 1], 'scene': 'plain'}, {'x': [3, 6, 7, 8, 13], 'y': [8, 11, 1, 6, 6], 'scene': 'plain'}, {'x': [3, 4, 7, 11, 13, 14], 'y': [14, 7, 16, 4, 8, 13], 'scene': 'plain'}, {'x': [1, 5, 10, 12, 13], 'y': [2, 13, 15, 8, 8], 'scene': 'plain'}, {'x': [2, 4, 7, 11, 12, 14], 'y': [6, 15, 7, 14, 3, 7], 'scene': 'plain'}, {'x': [2, 3, 6, 7, 11, 14], 'y': [9, 7, 8, 11, 2, 16], 'scene': 'plain'}, {'x': [3, 4, 5, 11, 12, 15], 'y': [14, 2, 1, 6, 4, 1], 'scene': 'plain'}, {'x': [2, 3, 5, 7, 9], 'y': [15, 1, 3, 2, 7], 'scene': 'plain'}, {'x': [4, 6, 8, 9, 12], 'y': [8, 6, 4, 12, 9], 'scene': 'plain'}, {'x': [2, 3, 5, 8, 10, 13], 'y': [10, 8, 3, 5, 6, 15], 'scene': 'plain'}, {'x': [1, 3, 5, 9, 12, 13], 'y': [16, 15, 7, 9, 9, 3], 'scene': 'plain'}, {'x': [1, 2, 4, 7, 10, 12], 'y': [14, 13, 13, 12, 1, 7], 'scene': 'plain'}, {'x': [2, 3, 6, 8, 11], 'y': [4, 8, 8, 16, 14], 'scene': 'plain'}, {'x': [1, 3, 8, 9, 11, 12], 'y': [11, 14, 2, 7, 9, 13], 'scene': 'plain'}, {'x': [3, 4, 5, 6, 7, 8], 'y': [2, 3, 4, 5, 6, 7], 'scene': 'plain'}, {'x': [1, 2, 3, 5, 9, 11], 'y': [8, 12, 10, 1, 8, 4], 'scene': 'plain'}, {'x': [1, 3, 10, 12, 14, 15], 'y': [15, 5, 11, 3, 5, 11], 'scene': 'plain'}, {'x': [2, 5, 7, 10, 11, 14], 'y': [11, 10, 8, 14, 9, 1], 'scene': 'plain'}, {'x': [2, 5, 8, 9, 11], 'y': [4, 13, 10, 14, 14], 'scene': 'plain'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_CorrelationCoefficient', 'fixed_domain_key': 'statistics.bivariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['correlation_from_table'], 'matched_capabilities': ['correlation_from_table'], 'selected_operation': 'correlation_from_table', 'registry_revision': 'promoted-f99c60060e70', 'domain_module': 'core.domain.promoted.bivariate_statistics.bivariate_statistics_domain', 'entrypoint': 'build_bivariate_statistics_matrix', 'allowed_operations': ['correlation_change_add_point', 'correlation_from_table', 'correlation_remove_point', 'correlation_rescale', 'true_false_bivariate'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_CorrelationCoefficient'}), seed)
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
