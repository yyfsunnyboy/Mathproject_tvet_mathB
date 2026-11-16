from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "geometric_growth_mean"
TEXTBOOK_EXAMPLE_ID = 12937
DEFAULT_COMPONENT_ID = "src_12937" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Mean"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "geometric_growth_mean"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['geometric_growth_mean'], 'domain_operation': 'geometric_growth_mean', 'problem_type_id': 'geometric_growth_mean', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'rates': ['0.1', '0.21', '0.331'], 'decimals': 3}, {'rates': ['0.03', '0.035', '0.1', '0.02'], 'decimals': 3}, {'rates': ['0.21', '0.02', '0.21'], 'decimals': 3}, {'rates': ['0.331', '-0.044', '0.028'], 'decimals': 3}, {'rates': ['0.035', '0.05', '0.331', '0.05'], 'decimals': 3}, {'rates': ['0.331', '0.05', '0.028', '-0.044'], 'decimals': 3}, {'rates': ['0.1', '0.035', '0.02', '0.05'], 'decimals': 3}, {'rates': ['0.038', '-0.02', '0.028', '0.05'], 'decimals': 3}, {'rates': ['-0.02', '0.1', '0.038', '0.028'], 'decimals': 3}, {'rates': ['0.035', '-0.02', '-0.044'], 'decimals': 3}, {'rates': ['0.03', '-0.02', '0.05', '0.21'], 'decimals': 3}, {'rates': ['0.21', '0.21', '0.21'], 'decimals': 3}, {'rates': ['-0.02', '-0.044', '0.1', '0.02'], 'decimals': 3}, {'rates': ['0.02', '0.03', '0.028'], 'decimals': 3}, {'rates': ['0.1', '0.05', '0.02', '0.05'], 'decimals': 3}, {'rates': ['-0.044', '0.331', '0.1'], 'decimals': 3}, {'rates': ['0.331', '0.028', '0.035', '0.03'], 'decimals': 3}, {'rates': ['-0.02', '0.03', '0.03'], 'decimals': 3}, {'rates': ['0.02', '0.21', '0.05'], 'decimals': 3}, {'rates': ['0.038', '0.331', '-0.02', '0.038'], 'decimals': 3}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['geometric_growth_mean'], 'domain_operation': 'geometric_growth_mean', 'problem_type_id': 'geometric_growth_mean', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'rates': ['0.1', '0.21', '0.331'], 'decimals': 3}, {'rates': ['0.03', '0.035', '0.1', '0.02'], 'decimals': 3}, {'rates': ['0.21', '0.02', '0.21'], 'decimals': 3}, {'rates': ['0.331', '-0.044', '0.028'], 'decimals': 3}, {'rates': ['0.035', '0.05', '0.331', '0.05'], 'decimals': 3}, {'rates': ['0.331', '0.05', '0.028', '-0.044'], 'decimals': 3}, {'rates': ['0.1', '0.035', '0.02', '0.05'], 'decimals': 3}, {'rates': ['0.038', '-0.02', '0.028', '0.05'], 'decimals': 3}, {'rates': ['-0.02', '0.1', '0.038', '0.028'], 'decimals': 3}, {'rates': ['0.035', '-0.02', '-0.044'], 'decimals': 3}, {'rates': ['0.03', '-0.02', '0.05', '0.21'], 'decimals': 3}, {'rates': ['0.21', '0.21', '0.21'], 'decimals': 3}, {'rates': ['-0.02', '-0.044', '0.1', '0.02'], 'decimals': 3}, {'rates': ['0.02', '0.03', '0.028'], 'decimals': 3}, {'rates': ['0.1', '0.05', '0.02', '0.05'], 'decimals': 3}, {'rates': ['-0.044', '0.331', '0.1'], 'decimals': 3}, {'rates': ['0.331', '0.028', '0.035', '0.03'], 'decimals': 3}, {'rates': ['-0.02', '0.03', '0.03'], 'decimals': 3}, {'rates': ['0.02', '0.21', '0.05'], 'decimals': 3}, {'rates': ['0.038', '0.331', '-0.02', '0.038'], 'decimals': 3}]}}, 'problem_type_id': 'geometric_growth_mean', 'required_capabilities': ['geometric_growth_mean'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'rates': ['0.1', '0.21', '0.331'], 'decimals': 3}, {'rates': ['0.03', '0.035', '0.1', '0.02'], 'decimals': 3}, {'rates': ['0.21', '0.02', '0.21'], 'decimals': 3}, {'rates': ['0.331', '-0.044', '0.028'], 'decimals': 3}, {'rates': ['0.035', '0.05', '0.331', '0.05'], 'decimals': 3}, {'rates': ['0.331', '0.05', '0.028', '-0.044'], 'decimals': 3}, {'rates': ['0.1', '0.035', '0.02', '0.05'], 'decimals': 3}, {'rates': ['0.038', '-0.02', '0.028', '0.05'], 'decimals': 3}, {'rates': ['-0.02', '0.1', '0.038', '0.028'], 'decimals': 3}, {'rates': ['0.035', '-0.02', '-0.044'], 'decimals': 3}, {'rates': ['0.03', '-0.02', '0.05', '0.21'], 'decimals': 3}, {'rates': ['0.21', '0.21', '0.21'], 'decimals': 3}, {'rates': ['-0.02', '-0.044', '0.1', '0.02'], 'decimals': 3}, {'rates': ['0.02', '0.03', '0.028'], 'decimals': 3}, {'rates': ['0.1', '0.05', '0.02', '0.05'], 'decimals': 3}, {'rates': ['-0.044', '0.331', '0.1'], 'decimals': 3}, {'rates': ['0.331', '0.028', '0.035', '0.03'], 'decimals': 3}, {'rates': ['-0.02', '0.03', '0.03'], 'decimals': 3}, {'rates': ['0.02', '0.21', '0.05'], 'decimals': 3}, {'rates': ['0.038', '0.331', '-0.02', '0.038'], 'decimals': 3}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Mean', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['geometric_growth_mean'], 'matched_capabilities': ['geometric_growth_mean'], 'selected_operation': 'geometric_growth_mean', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['arithmetic_mean', 'geometric_growth_mean', 'geometric_growth_unknown', 'true_false_stat', 'weighted_mean', 'weighted_mean_unknown'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Mean'}), seed)
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
