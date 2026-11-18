from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "correlation_change_add_point"
TEXTBOOK_EXAMPLE_ID = 12967
DEFAULT_COMPONENT_ID = "src_12967" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CorrelationCoefficient"
FIXED_DOMAIN_KEY = "statistics.bivariate_descriptive"
DOMAIN_OPERATION = "correlation_change_add_point"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['correlation_change_add_point'], 'domain_operation': 'correlation_change_add_point', 'problem_type_id': 'correlation_change_add_point', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'x': ['24.5', '25', '25', '25.5', '26', '26', '26.5', '27', '27.5', '28'], 'y': [160, 158, 163, 163, 161, 163, 168, 170, 168, 173], 'new_point': ['26', 174]}, {'x': ['24.5', '24.5', '25.5', '25.5', '26', '26', '27', '27', '27.5', '28'], 'y': [155, 162, 158, 162, 164, 164, 170, 166, 168, 167], 'new_point': ['25', 171]}, {'x': ['24', '24', '24.5', '25', '25', '25', '25.5', '27.5', '27.5'], 'y': [159, 155, 164, 166, 164, 160, 162, 166, 168], 'new_point': ['25.5', 154]}, {'x': ['24', '24.5', '25', '25.5', '26.5', '27.5', '27.5', '27.5', '28', '28'], 'y': [153, 156, 164, 165, 169, 168, 174, 166, 174, 169], 'new_point': ['27.5', 160]}, {'x': ['24', '24.5', '25', '25', '25', '26.5', '27', '27.5', '28', '28'], 'y': [158, 157, 162, 159, 157, 171, 164, 168, 175, 172], 'new_point': ['28', 167]}, {'x': ['24', '24', '24.5', '24.5', '25', '25', '26', '27', '27.5'], 'y': [157, 157, 155, 160, 161, 157, 166, 165, 166], 'new_point': ['27.5', 174]}, {'x': ['25', '26', '26', '26', '26.5', '26.5', '26.5', '27', '27', '27.5'], 'y': [166, 167, 163, 160, 166, 167, 163, 168, 166, 172], 'new_point': ['25', 163]}, {'x': ['24', '24.5', '25.5', '26.5', '26.5', '27.5', '27.5', '27.5', '28'], 'y': [155, 164, 164, 169, 167, 172, 168, 172, 176], 'new_point': ['28', 163]}, {'x': ['24', '24', '24.5', '24.5', '25', '25.5', '26.5', '27'], 'y': [155, 160, 158, 157, 163, 158, 166, 164], 'new_point': ['24.5', 153]}, {'x': ['24', '24.5', '24.5', '25', '25.5', '26', '26.5', '27.5', '27.5', '27.5'], 'y': [159, 163, 155, 156, 167, 164, 167, 166, 176, 174], 'new_point': ['26.5', 179]}, {'x': ['24', '24.5', '24.5', '24.5', '25', '25', '25.5', '26', '27'], 'y': [161, 154, 156, 156, 165, 162, 162, 163, 173], 'new_point': ['26', 159]}, {'x': ['24.5', '24.5', '25.5', '26', '26.5', '27', '27.5', '28', '28'], 'y': [157, 155, 160, 160, 172, 172, 176, 172, 168], 'new_point': ['24.5', 150]}, {'x': ['24.5', '24.5', '24.5', '25', '26', '26.5', '27', '27.5', '28', '28'], 'y': [154, 156, 163, 166, 162, 165, 164, 168, 172, 174], 'new_point': ['24.5', 163]}, {'x': ['24', '24.5', '25', '25', '25.5', '26', '27', '27', '28', '28'], 'y': [162, 163, 161, 160, 162, 168, 173, 174, 170, 172], 'new_point': ['27.5', 181]}, {'x': ['24', '24.5', '25', '25.5', '27', '27', '27', '27.5', '28'], 'y': [155, 159, 166, 162, 168, 172, 169, 174, 169], 'new_point': ['26', 154]}, {'x': ['24', '24.5', '24.5', '25', '25', '25.5', '26.5', '26.5', '27', '27'], 'y': [154, 154, 161, 166, 160, 161, 169, 163, 166, 164], 'new_point': ['26.5', 177]}, {'x': ['24', '24', '24.5', '26', '26.5', '26.5', '27.5', '28', '28'], 'y': [155, 156, 161, 166, 163, 172, 174, 176, 172], 'new_point': ['27', 180]}, {'x': ['24.5', '24.5', '25', '25', '25', '25', '26.5', '27.5', '28'], 'y': [156, 157, 157, 163, 158, 164, 170, 172, 176], 'new_point': ['25.5', 173]}, {'x': ['24', '24', '24.5', '25.5', '26', '26', '27', '27.5', '28', '28'], 'y': [162, 159, 155, 162, 166, 161, 170, 172, 170, 177], 'new_point': ['24.5', 164]}, {'x': ['24', '25', '25', '25.5', '25.5', '26.5', '27', '27', '27', '27.5'], 'y': [153, 161, 159, 158, 164, 163, 167, 166, 169, 166], 'new_point': ['28', 184]}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['correlation_change_add_point'], 'domain_operation': 'correlation_change_add_point', 'problem_type_id': 'correlation_change_add_point', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'x': ['24.5', '25', '25', '25.5', '26', '26', '26.5', '27', '27.5', '28'], 'y': [160, 158, 163, 163, 161, 163, 168, 170, 168, 173], 'new_point': ['26', 174]}, {'x': ['24.5', '24.5', '25.5', '25.5', '26', '26', '27', '27', '27.5', '28'], 'y': [155, 162, 158, 162, 164, 164, 170, 166, 168, 167], 'new_point': ['25', 171]}, {'x': ['24', '24', '24.5', '25', '25', '25', '25.5', '27.5', '27.5'], 'y': [159, 155, 164, 166, 164, 160, 162, 166, 168], 'new_point': ['25.5', 154]}, {'x': ['24', '24.5', '25', '25.5', '26.5', '27.5', '27.5', '27.5', '28', '28'], 'y': [153, 156, 164, 165, 169, 168, 174, 166, 174, 169], 'new_point': ['27.5', 160]}, {'x': ['24', '24.5', '25', '25', '25', '26.5', '27', '27.5', '28', '28'], 'y': [158, 157, 162, 159, 157, 171, 164, 168, 175, 172], 'new_point': ['28', 167]}, {'x': ['24', '24', '24.5', '24.5', '25', '25', '26', '27', '27.5'], 'y': [157, 157, 155, 160, 161, 157, 166, 165, 166], 'new_point': ['27.5', 174]}, {'x': ['25', '26', '26', '26', '26.5', '26.5', '26.5', '27', '27', '27.5'], 'y': [166, 167, 163, 160, 166, 167, 163, 168, 166, 172], 'new_point': ['25', 163]}, {'x': ['24', '24.5', '25.5', '26.5', '26.5', '27.5', '27.5', '27.5', '28'], 'y': [155, 164, 164, 169, 167, 172, 168, 172, 176], 'new_point': ['28', 163]}, {'x': ['24', '24', '24.5', '24.5', '25', '25.5', '26.5', '27'], 'y': [155, 160, 158, 157, 163, 158, 166, 164], 'new_point': ['24.5', 153]}, {'x': ['24', '24.5', '24.5', '25', '25.5', '26', '26.5', '27.5', '27.5', '27.5'], 'y': [159, 163, 155, 156, 167, 164, 167, 166, 176, 174], 'new_point': ['26.5', 179]}, {'x': ['24', '24.5', '24.5', '24.5', '25', '25', '25.5', '26', '27'], 'y': [161, 154, 156, 156, 165, 162, 162, 163, 173], 'new_point': ['26', 159]}, {'x': ['24.5', '24.5', '25.5', '26', '26.5', '27', '27.5', '28', '28'], 'y': [157, 155, 160, 160, 172, 172, 176, 172, 168], 'new_point': ['24.5', 150]}, {'x': ['24.5', '24.5', '24.5', '25', '26', '26.5', '27', '27.5', '28', '28'], 'y': [154, 156, 163, 166, 162, 165, 164, 168, 172, 174], 'new_point': ['24.5', 163]}, {'x': ['24', '24.5', '25', '25', '25.5', '26', '27', '27', '28', '28'], 'y': [162, 163, 161, 160, 162, 168, 173, 174, 170, 172], 'new_point': ['27.5', 181]}, {'x': ['24', '24.5', '25', '25.5', '27', '27', '27', '27.5', '28'], 'y': [155, 159, 166, 162, 168, 172, 169, 174, 169], 'new_point': ['26', 154]}, {'x': ['24', '24.5', '24.5', '25', '25', '25.5', '26.5', '26.5', '27', '27'], 'y': [154, 154, 161, 166, 160, 161, 169, 163, 166, 164], 'new_point': ['26.5', 177]}, {'x': ['24', '24', '24.5', '26', '26.5', '26.5', '27.5', '28', '28'], 'y': [155, 156, 161, 166, 163, 172, 174, 176, 172], 'new_point': ['27', 180]}, {'x': ['24.5', '24.5', '25', '25', '25', '25', '26.5', '27.5', '28'], 'y': [156, 157, 157, 163, 158, 164, 170, 172, 176], 'new_point': ['25.5', 173]}, {'x': ['24', '24', '24.5', '25.5', '26', '26', '27', '27.5', '28', '28'], 'y': [162, 159, 155, 162, 166, 161, 170, 172, 170, 177], 'new_point': ['24.5', 164]}, {'x': ['24', '25', '25', '25.5', '25.5', '26.5', '27', '27', '27', '27.5'], 'y': [153, 161, 159, 158, 164, 163, 167, 166, 169, 166], 'new_point': ['28', 184]}]}}, 'problem_type_id': 'correlation_change_add_point', 'required_capabilities': ['correlation_change_add_point'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'x': ['24.5', '25', '25', '25.5', '26', '26', '26.5', '27', '27.5', '28'], 'y': [160, 158, 163, 163, 161, 163, 168, 170, 168, 173], 'new_point': ['26', 174]}, {'x': ['24.5', '24.5', '25.5', '25.5', '26', '26', '27', '27', '27.5', '28'], 'y': [155, 162, 158, 162, 164, 164, 170, 166, 168, 167], 'new_point': ['25', 171]}, {'x': ['24', '24', '24.5', '25', '25', '25', '25.5', '27.5', '27.5'], 'y': [159, 155, 164, 166, 164, 160, 162, 166, 168], 'new_point': ['25.5', 154]}, {'x': ['24', '24.5', '25', '25.5', '26.5', '27.5', '27.5', '27.5', '28', '28'], 'y': [153, 156, 164, 165, 169, 168, 174, 166, 174, 169], 'new_point': ['27.5', 160]}, {'x': ['24', '24.5', '25', '25', '25', '26.5', '27', '27.5', '28', '28'], 'y': [158, 157, 162, 159, 157, 171, 164, 168, 175, 172], 'new_point': ['28', 167]}, {'x': ['24', '24', '24.5', '24.5', '25', '25', '26', '27', '27.5'], 'y': [157, 157, 155, 160, 161, 157, 166, 165, 166], 'new_point': ['27.5', 174]}, {'x': ['25', '26', '26', '26', '26.5', '26.5', '26.5', '27', '27', '27.5'], 'y': [166, 167, 163, 160, 166, 167, 163, 168, 166, 172], 'new_point': ['25', 163]}, {'x': ['24', '24.5', '25.5', '26.5', '26.5', '27.5', '27.5', '27.5', '28'], 'y': [155, 164, 164, 169, 167, 172, 168, 172, 176], 'new_point': ['28', 163]}, {'x': ['24', '24', '24.5', '24.5', '25', '25.5', '26.5', '27'], 'y': [155, 160, 158, 157, 163, 158, 166, 164], 'new_point': ['24.5', 153]}, {'x': ['24', '24.5', '24.5', '25', '25.5', '26', '26.5', '27.5', '27.5', '27.5'], 'y': [159, 163, 155, 156, 167, 164, 167, 166, 176, 174], 'new_point': ['26.5', 179]}, {'x': ['24', '24.5', '24.5', '24.5', '25', '25', '25.5', '26', '27'], 'y': [161, 154, 156, 156, 165, 162, 162, 163, 173], 'new_point': ['26', 159]}, {'x': ['24.5', '24.5', '25.5', '26', '26.5', '27', '27.5', '28', '28'], 'y': [157, 155, 160, 160, 172, 172, 176, 172, 168], 'new_point': ['24.5', 150]}, {'x': ['24.5', '24.5', '24.5', '25', '26', '26.5', '27', '27.5', '28', '28'], 'y': [154, 156, 163, 166, 162, 165, 164, 168, 172, 174], 'new_point': ['24.5', 163]}, {'x': ['24', '24.5', '25', '25', '25.5', '26', '27', '27', '28', '28'], 'y': [162, 163, 161, 160, 162, 168, 173, 174, 170, 172], 'new_point': ['27.5', 181]}, {'x': ['24', '24.5', '25', '25.5', '27', '27', '27', '27.5', '28'], 'y': [155, 159, 166, 162, 168, 172, 169, 174, 169], 'new_point': ['26', 154]}, {'x': ['24', '24.5', '24.5', '25', '25', '25.5', '26.5', '26.5', '27', '27'], 'y': [154, 154, 161, 166, 160, 161, 169, 163, 166, 164], 'new_point': ['26.5', 177]}, {'x': ['24', '24', '24.5', '26', '26.5', '26.5', '27.5', '28', '28'], 'y': [155, 156, 161, 166, 163, 172, 174, 176, 172], 'new_point': ['27', 180]}, {'x': ['24.5', '24.5', '25', '25', '25', '25', '26.5', '27.5', '28'], 'y': [156, 157, 157, 163, 158, 164, 170, 172, 176], 'new_point': ['25.5', 173]}, {'x': ['24', '24', '24.5', '25.5', '26', '26', '27', '27.5', '28', '28'], 'y': [162, 159, 155, 162, 166, 161, 170, 172, 170, 177], 'new_point': ['24.5', 164]}, {'x': ['24', '25', '25', '25.5', '25.5', '26.5', '27', '27', '27', '27.5'], 'y': [153, 161, 159, 158, 164, 163, 167, 166, 169, 166], 'new_point': ['28', 184]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_CorrelationCoefficient', 'fixed_domain_key': 'statistics.bivariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['correlation_change_add_point'], 'matched_capabilities': ['correlation_change_add_point'], 'selected_operation': 'correlation_change_add_point', 'registry_revision': 'promoted-f99c60060e70', 'domain_module': 'core.domain.promoted.bivariate_statistics.bivariate_statistics_domain', 'entrypoint': 'build_bivariate_statistics_matrix', 'allowed_operations': ['correlation_change_add_point', 'correlation_from_table', 'correlation_remove_point', 'correlation_rescale', 'true_false_bivariate'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_CorrelationCoefficient'}), seed)
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
