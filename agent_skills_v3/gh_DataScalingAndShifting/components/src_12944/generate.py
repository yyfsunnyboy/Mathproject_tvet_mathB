from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "monthly_mean_sd"
TEXTBOOK_EXAMPLE_ID = 12944
DEFAULT_COMPONENT_ID = "src_12944" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_DataScalingAndShifting"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "monthly_mean_sd"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['monthly_mean_sd'], 'domain_operation': 'monthly_mean_sd', 'problem_type_id': 'monthly_mean_sd', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'values': ['3.0', '3.9', '1.8', '5.7', '7.6', '9.6', '9.3', '8.2', '8.0', '4.0', '3.6', '1.3'], 'places': 1}, {'values': ['2.8', '3.1', '20.8', '15.8', '20.1', '20.6', '9.4', '0.1', '11.5', '11', '1.1', '10.8'], 'places': 1}, {'values': ['15.5', '18.5', '10.9', '2.3', '9.1', '15.8', '1.6', '5.2', '17', '5', '0.6', '1.3'], 'places': 1}, {'values': ['8.5', '16.3', '10.4', '20.1', '1.3', '5.5', '15.9', '10.6', '8.8', '12.6', '9.8', '12.6'], 'places': 1}, {'values': ['15.3', '13.4', '4.5', '10.5', '8', '4.5', '17.6', '18.8', '3', '9.8', '0.8', '9.2'], 'places': 1}, {'values': ['16.7', '16.8', '0.9', '13', '13.7', '15.4', '11.1', '7', '19.1', '6.1', '0.4', '6.9'], 'places': 1}, {'values': ['14.5', '7.3', '20.6', '6.1', '6.2', '17.8', '4.8', '6.9', '13.1', '15.5', '4.2', '17.3'], 'places': 1}, {'values': ['7.2', '2.2', '5.8', '13.5', '9.7', '8.6', '2', '18.3', '20.2', '10.4', '11.7', '16.4'], 'places': 1}, {'values': ['3.1', '14.4', '10.3', '18.7', '6.1', '17', '17.6', '14.3', '15', '14.9', '5.8', '8.7'], 'places': 1}, {'values': ['0.1', '13.4', '18.7', '9', '7.7', '12.7', '1.1', '10', '1.9', '9.8', '8.3', '11.5'], 'places': 1}, {'values': ['20.6', '2.2', '17.4', '13', '1.9', '4', '2.2', '6.7', '14', '13.8', '16.1', '17.4'], 'places': 1}, {'values': ['10.8', '8', '12.7', '7.3', '13.1', '8.5', '15.5', '2.9', '18.4', '7', '12.3', '15.5'], 'places': 1}, {'values': ['13.2', '6.3', '18.1', '11.4', '9.7', '18', '11', '20.4', '0.3', '11.3', '17.6', '18.5'], 'places': 1}, {'values': ['19.6', '14.5', '13.9', '9.2', '18', '17.6', '20.4', '2.4', '13.1', '5.5', '17.9', '15.4'], 'places': 1}, {'values': ['12.2', '9.1', '6.9', '4.6', '15.2', '11.1', '14.6', '7.6', '12.9', '2.3', '6.1', '15.2'], 'places': 1}, {'values': ['1.4', '12.9', '3.3', '1', '5.2', '16.4', '15.4', '0.3', '16.5', '9.6', '2', '8.8'], 'places': 1}, {'values': ['11.5', '16', '9.1', '13.5', '6.4', '4.8', '20.5', '12', '11.6', '14.5', '15.6', '0.8'], 'places': 1}, {'values': ['17', '19.8', '7.9', '2.9', '0.2', '0.8', '3', '2.9', '20.5', '3.6', '19.4', '13.9'], 'places': 1}, {'values': ['15.6', '11.9', '12.1', '8.5', '16.9', '1', '3.4', '13.5', '0', '17', '12.8', '5.8'], 'places': 1}, {'values': ['3.3', '6.5', '20', '12.3', '17.9', '8.2', '20.1', '20.9', '20.1', '1.5', '3.1', '9.5'], 'places': 1}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['monthly_mean_sd'], 'domain_operation': 'monthly_mean_sd', 'problem_type_id': 'monthly_mean_sd', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'values': ['3.0', '3.9', '1.8', '5.7', '7.6', '9.6', '9.3', '8.2', '8.0', '4.0', '3.6', '1.3'], 'places': 1}, {'values': ['2.8', '3.1', '20.8', '15.8', '20.1', '20.6', '9.4', '0.1', '11.5', '11', '1.1', '10.8'], 'places': 1}, {'values': ['15.5', '18.5', '10.9', '2.3', '9.1', '15.8', '1.6', '5.2', '17', '5', '0.6', '1.3'], 'places': 1}, {'values': ['8.5', '16.3', '10.4', '20.1', '1.3', '5.5', '15.9', '10.6', '8.8', '12.6', '9.8', '12.6'], 'places': 1}, {'values': ['15.3', '13.4', '4.5', '10.5', '8', '4.5', '17.6', '18.8', '3', '9.8', '0.8', '9.2'], 'places': 1}, {'values': ['16.7', '16.8', '0.9', '13', '13.7', '15.4', '11.1', '7', '19.1', '6.1', '0.4', '6.9'], 'places': 1}, {'values': ['14.5', '7.3', '20.6', '6.1', '6.2', '17.8', '4.8', '6.9', '13.1', '15.5', '4.2', '17.3'], 'places': 1}, {'values': ['7.2', '2.2', '5.8', '13.5', '9.7', '8.6', '2', '18.3', '20.2', '10.4', '11.7', '16.4'], 'places': 1}, {'values': ['3.1', '14.4', '10.3', '18.7', '6.1', '17', '17.6', '14.3', '15', '14.9', '5.8', '8.7'], 'places': 1}, {'values': ['0.1', '13.4', '18.7', '9', '7.7', '12.7', '1.1', '10', '1.9', '9.8', '8.3', '11.5'], 'places': 1}, {'values': ['20.6', '2.2', '17.4', '13', '1.9', '4', '2.2', '6.7', '14', '13.8', '16.1', '17.4'], 'places': 1}, {'values': ['10.8', '8', '12.7', '7.3', '13.1', '8.5', '15.5', '2.9', '18.4', '7', '12.3', '15.5'], 'places': 1}, {'values': ['13.2', '6.3', '18.1', '11.4', '9.7', '18', '11', '20.4', '0.3', '11.3', '17.6', '18.5'], 'places': 1}, {'values': ['19.6', '14.5', '13.9', '9.2', '18', '17.6', '20.4', '2.4', '13.1', '5.5', '17.9', '15.4'], 'places': 1}, {'values': ['12.2', '9.1', '6.9', '4.6', '15.2', '11.1', '14.6', '7.6', '12.9', '2.3', '6.1', '15.2'], 'places': 1}, {'values': ['1.4', '12.9', '3.3', '1', '5.2', '16.4', '15.4', '0.3', '16.5', '9.6', '2', '8.8'], 'places': 1}, {'values': ['11.5', '16', '9.1', '13.5', '6.4', '4.8', '20.5', '12', '11.6', '14.5', '15.6', '0.8'], 'places': 1}, {'values': ['17', '19.8', '7.9', '2.9', '0.2', '0.8', '3', '2.9', '20.5', '3.6', '19.4', '13.9'], 'places': 1}, {'values': ['15.6', '11.9', '12.1', '8.5', '16.9', '1', '3.4', '13.5', '0', '17', '12.8', '5.8'], 'places': 1}, {'values': ['3.3', '6.5', '20', '12.3', '17.9', '8.2', '20.1', '20.9', '20.1', '1.5', '3.1', '9.5'], 'places': 1}]}}, 'problem_type_id': 'monthly_mean_sd', 'required_capabilities': ['monthly_mean_sd'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'values': ['3.0', '3.9', '1.8', '5.7', '7.6', '9.6', '9.3', '8.2', '8.0', '4.0', '3.6', '1.3'], 'places': 1}, {'values': ['2.8', '3.1', '20.8', '15.8', '20.1', '20.6', '9.4', '0.1', '11.5', '11', '1.1', '10.8'], 'places': 1}, {'values': ['15.5', '18.5', '10.9', '2.3', '9.1', '15.8', '1.6', '5.2', '17', '5', '0.6', '1.3'], 'places': 1}, {'values': ['8.5', '16.3', '10.4', '20.1', '1.3', '5.5', '15.9', '10.6', '8.8', '12.6', '9.8', '12.6'], 'places': 1}, {'values': ['15.3', '13.4', '4.5', '10.5', '8', '4.5', '17.6', '18.8', '3', '9.8', '0.8', '9.2'], 'places': 1}, {'values': ['16.7', '16.8', '0.9', '13', '13.7', '15.4', '11.1', '7', '19.1', '6.1', '0.4', '6.9'], 'places': 1}, {'values': ['14.5', '7.3', '20.6', '6.1', '6.2', '17.8', '4.8', '6.9', '13.1', '15.5', '4.2', '17.3'], 'places': 1}, {'values': ['7.2', '2.2', '5.8', '13.5', '9.7', '8.6', '2', '18.3', '20.2', '10.4', '11.7', '16.4'], 'places': 1}, {'values': ['3.1', '14.4', '10.3', '18.7', '6.1', '17', '17.6', '14.3', '15', '14.9', '5.8', '8.7'], 'places': 1}, {'values': ['0.1', '13.4', '18.7', '9', '7.7', '12.7', '1.1', '10', '1.9', '9.8', '8.3', '11.5'], 'places': 1}, {'values': ['20.6', '2.2', '17.4', '13', '1.9', '4', '2.2', '6.7', '14', '13.8', '16.1', '17.4'], 'places': 1}, {'values': ['10.8', '8', '12.7', '7.3', '13.1', '8.5', '15.5', '2.9', '18.4', '7', '12.3', '15.5'], 'places': 1}, {'values': ['13.2', '6.3', '18.1', '11.4', '9.7', '18', '11', '20.4', '0.3', '11.3', '17.6', '18.5'], 'places': 1}, {'values': ['19.6', '14.5', '13.9', '9.2', '18', '17.6', '20.4', '2.4', '13.1', '5.5', '17.9', '15.4'], 'places': 1}, {'values': ['12.2', '9.1', '6.9', '4.6', '15.2', '11.1', '14.6', '7.6', '12.9', '2.3', '6.1', '15.2'], 'places': 1}, {'values': ['1.4', '12.9', '3.3', '1', '5.2', '16.4', '15.4', '0.3', '16.5', '9.6', '2', '8.8'], 'places': 1}, {'values': ['11.5', '16', '9.1', '13.5', '6.4', '4.8', '20.5', '12', '11.6', '14.5', '15.6', '0.8'], 'places': 1}, {'values': ['17', '19.8', '7.9', '2.9', '0.2', '0.8', '3', '2.9', '20.5', '3.6', '19.4', '13.9'], 'places': 1}, {'values': ['15.6', '11.9', '12.1', '8.5', '16.9', '1', '3.4', '13.5', '0', '17', '12.8', '5.8'], 'places': 1}, {'values': ['3.3', '6.5', '20', '12.3', '17.9', '8.2', '20.1', '20.9', '20.1', '1.5', '3.1', '9.5'], 'places': 1}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_DataScalingAndShifting', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['monthly_mean_sd'], 'matched_capabilities': ['monthly_mean_sd'], 'selected_operation': 'monthly_mean_sd', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['linear_find_scale_sd', 'linear_mean_sd', 'monthly_mean_sd', 'standardize_scores', 'statement_selection', 'true_false_stat'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_DataScalingAndShifting'}), seed)
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
