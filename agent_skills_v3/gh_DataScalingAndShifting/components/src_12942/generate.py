from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "linear_mean_sd"
TEXTBOOK_EXAMPLE_ID = 12942
DEFAULT_COMPONENT_ID = "src_12942" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_DataScalingAndShifting"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "linear_mean_sd"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['linear_mean_sd'], 'domain_operation': 'linear_mean_sd', 'problem_type_id': 'linear_mean_sd', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'mean': 30, 'sd': '6.5', 'a': '9/5', 'b': 32}, {'mean': 40, 'sd': '5', 'a': '1/2', 'b': 6}, {'mean': 40, 'sd': '8', 'a': '9/5', 'b': 34}, {'mean': 38, 'sd': '8', 'a': '1/2', 'b': 14}, {'mean': 20, 'sd': '5', 'a': '2', 'b': 1}, {'mean': 36, 'sd': '8', 'a': '9/5', 'b': 14}, {'mean': 29, 'sd': '10', 'a': '1/2', 'b': 21}, {'mean': 28, 'sd': '5', 'a': '9/5', 'b': 16}, {'mean': 24, 'sd': '5', 'a': '5/4', 'b': 35}, {'mean': 39, 'sd': '10', 'a': '5/4', 'b': 13}, {'mean': 20, 'sd': '10', 'a': '2', 'b': 1}, {'mean': 30, 'sd': '10', 'a': '2', 'b': 3}, {'mean': 24, 'sd': '6.5', 'a': '5/4', 'b': 11}, {'mean': 28, 'sd': '6.5', 'a': '9/5', 'b': 38}, {'mean': 29, 'sd': '8', 'a': '5/4', 'b': 36}, {'mean': 40, 'sd': '6.5', 'a': '1/2', 'b': 14}, {'mean': 23, 'sd': '5', 'a': '9/5', 'b': 23}, {'mean': 32, 'sd': '5', 'a': '2', 'b': 3}, {'mean': 22, 'sd': '5', 'a': '5/4', 'b': 17}, {'mean': 25, 'sd': '10', 'a': '1/2', 'b': 33}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['linear_mean_sd'], 'domain_operation': 'linear_mean_sd', 'problem_type_id': 'linear_mean_sd', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'mean': 30, 'sd': '6.5', 'a': '9/5', 'b': 32}, {'mean': 40, 'sd': '5', 'a': '1/2', 'b': 6}, {'mean': 40, 'sd': '8', 'a': '9/5', 'b': 34}, {'mean': 38, 'sd': '8', 'a': '1/2', 'b': 14}, {'mean': 20, 'sd': '5', 'a': '2', 'b': 1}, {'mean': 36, 'sd': '8', 'a': '9/5', 'b': 14}, {'mean': 29, 'sd': '10', 'a': '1/2', 'b': 21}, {'mean': 28, 'sd': '5', 'a': '9/5', 'b': 16}, {'mean': 24, 'sd': '5', 'a': '5/4', 'b': 35}, {'mean': 39, 'sd': '10', 'a': '5/4', 'b': 13}, {'mean': 20, 'sd': '10', 'a': '2', 'b': 1}, {'mean': 30, 'sd': '10', 'a': '2', 'b': 3}, {'mean': 24, 'sd': '6.5', 'a': '5/4', 'b': 11}, {'mean': 28, 'sd': '6.5', 'a': '9/5', 'b': 38}, {'mean': 29, 'sd': '8', 'a': '5/4', 'b': 36}, {'mean': 40, 'sd': '6.5', 'a': '1/2', 'b': 14}, {'mean': 23, 'sd': '5', 'a': '9/5', 'b': 23}, {'mean': 32, 'sd': '5', 'a': '2', 'b': 3}, {'mean': 22, 'sd': '5', 'a': '5/4', 'b': 17}, {'mean': 25, 'sd': '10', 'a': '1/2', 'b': 33}]}}, 'problem_type_id': 'linear_mean_sd', 'required_capabilities': ['linear_mean_sd'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'mean': 30, 'sd': '6.5', 'a': '9/5', 'b': 32}, {'mean': 40, 'sd': '5', 'a': '1/2', 'b': 6}, {'mean': 40, 'sd': '8', 'a': '9/5', 'b': 34}, {'mean': 38, 'sd': '8', 'a': '1/2', 'b': 14}, {'mean': 20, 'sd': '5', 'a': '2', 'b': 1}, {'mean': 36, 'sd': '8', 'a': '9/5', 'b': 14}, {'mean': 29, 'sd': '10', 'a': '1/2', 'b': 21}, {'mean': 28, 'sd': '5', 'a': '9/5', 'b': 16}, {'mean': 24, 'sd': '5', 'a': '5/4', 'b': 35}, {'mean': 39, 'sd': '10', 'a': '5/4', 'b': 13}, {'mean': 20, 'sd': '10', 'a': '2', 'b': 1}, {'mean': 30, 'sd': '10', 'a': '2', 'b': 3}, {'mean': 24, 'sd': '6.5', 'a': '5/4', 'b': 11}, {'mean': 28, 'sd': '6.5', 'a': '9/5', 'b': 38}, {'mean': 29, 'sd': '8', 'a': '5/4', 'b': 36}, {'mean': 40, 'sd': '6.5', 'a': '1/2', 'b': 14}, {'mean': 23, 'sd': '5', 'a': '9/5', 'b': 23}, {'mean': 32, 'sd': '5', 'a': '2', 'b': 3}, {'mean': 22, 'sd': '5', 'a': '5/4', 'b': 17}, {'mean': 25, 'sd': '10', 'a': '1/2', 'b': 33}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_DataScalingAndShifting', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['linear_mean_sd'], 'matched_capabilities': ['linear_mean_sd'], 'selected_operation': 'linear_mean_sd', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['linear_find_scale_sd', 'linear_mean_sd', 'monthly_mean_sd', 'standardize_scores', 'statement_selection', 'true_false_stat'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_DataScalingAndShifting'}), seed)
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
