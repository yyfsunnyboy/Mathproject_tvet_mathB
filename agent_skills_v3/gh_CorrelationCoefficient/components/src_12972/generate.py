from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "correlation_rescale"
TEXTBOOK_EXAMPLE_ID = 12972
DEFAULT_COMPONENT_ID = "src_12972" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CorrelationCoefficient"
FIXED_DOMAIN_KEY = "statistics.bivariate_descriptive"
DOMAIN_OPERATION = "correlation_rescale"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['correlation_rescale'], 'domain_operation': 'correlation_rescale', 'problem_type_id': 'correlation_rescale', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'n_questions': 20, 'old_per': 5, 'new_per': 6, 'top': 80, 'r': '0.73'}, {'n_questions': 20, 'old_per': 10, 'new_per': 12, 'top': 180, 'r': '0.02'}, {'n_questions': 20, 'old_per': 4, 'new_per': 5, 'top': 64, 'r': '-0.82'}, {'n_questions': 25, 'old_per': 5, 'new_per': 8, 'top': 105, 'r': '0.33'}, {'n_questions': 20, 'old_per': 5, 'new_per': 7, 'top': 50, 'r': '0.64'}, {'n_questions': 25, 'old_per': 10, 'new_per': 12, 'top': 210, 'r': '-0.25'}, {'n_questions': 20, 'old_per': 10, 'new_per': 12, 'top': 180, 'r': '0.64'}, {'n_questions': 20, 'old_per': 5, 'new_per': 6, 'top': 50, 'r': '-0.56'}, {'n_questions': 10, 'old_per': 2, 'new_per': 3, 'top': 18, 'r': '0.69'}, {'n_questions': 10, 'old_per': 5, 'new_per': 7, 'top': 25, 'r': '0.42'}, {'n_questions': 20, 'old_per': 2, 'new_per': 3, 'top': 36, 'r': '-0.95'}, {'n_questions': 20, 'old_per': 4, 'new_per': 5, 'top': 44, 'r': '0.69'}, {'n_questions': 10, 'old_per': 10, 'new_per': 12, 'top': 90, 'r': '-0.84'}, {'n_questions': 10, 'old_per': 5, 'new_per': 6, 'top': 35, 'r': '0.23'}, {'n_questions': 10, 'old_per': 5, 'new_per': 7, 'top': 30, 'r': '-0.5'}, {'n_questions': 10, 'old_per': 2, 'new_per': 3, 'top': 12, 'r': '0.16'}, {'n_questions': 10, 'old_per': 5, 'new_per': 6, 'top': 30, 'r': '0.64'}, {'n_questions': 10, 'old_per': 10, 'new_per': 12, 'top': 50, 'r': '0.94'}, {'n_questions': 25, 'old_per': 10, 'new_per': 12, 'top': 160, 'r': '0.2'}, {'n_questions': 25, 'old_per': 5, 'new_per': 8, 'top': 70, 'r': '0.79'}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['correlation_rescale'], 'domain_operation': 'correlation_rescale', 'problem_type_id': 'correlation_rescale', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'n_questions': 20, 'old_per': 5, 'new_per': 6, 'top': 80, 'r': '0.73'}, {'n_questions': 20, 'old_per': 10, 'new_per': 12, 'top': 180, 'r': '0.02'}, {'n_questions': 20, 'old_per': 4, 'new_per': 5, 'top': 64, 'r': '-0.82'}, {'n_questions': 25, 'old_per': 5, 'new_per': 8, 'top': 105, 'r': '0.33'}, {'n_questions': 20, 'old_per': 5, 'new_per': 7, 'top': 50, 'r': '0.64'}, {'n_questions': 25, 'old_per': 10, 'new_per': 12, 'top': 210, 'r': '-0.25'}, {'n_questions': 20, 'old_per': 10, 'new_per': 12, 'top': 180, 'r': '0.64'}, {'n_questions': 20, 'old_per': 5, 'new_per': 6, 'top': 50, 'r': '-0.56'}, {'n_questions': 10, 'old_per': 2, 'new_per': 3, 'top': 18, 'r': '0.69'}, {'n_questions': 10, 'old_per': 5, 'new_per': 7, 'top': 25, 'r': '0.42'}, {'n_questions': 20, 'old_per': 2, 'new_per': 3, 'top': 36, 'r': '-0.95'}, {'n_questions': 20, 'old_per': 4, 'new_per': 5, 'top': 44, 'r': '0.69'}, {'n_questions': 10, 'old_per': 10, 'new_per': 12, 'top': 90, 'r': '-0.84'}, {'n_questions': 10, 'old_per': 5, 'new_per': 6, 'top': 35, 'r': '0.23'}, {'n_questions': 10, 'old_per': 5, 'new_per': 7, 'top': 30, 'r': '-0.5'}, {'n_questions': 10, 'old_per': 2, 'new_per': 3, 'top': 12, 'r': '0.16'}, {'n_questions': 10, 'old_per': 5, 'new_per': 6, 'top': 30, 'r': '0.64'}, {'n_questions': 10, 'old_per': 10, 'new_per': 12, 'top': 50, 'r': '0.94'}, {'n_questions': 25, 'old_per': 10, 'new_per': 12, 'top': 160, 'r': '0.2'}, {'n_questions': 25, 'old_per': 5, 'new_per': 8, 'top': 70, 'r': '0.79'}]}}, 'problem_type_id': 'correlation_rescale', 'required_capabilities': ['correlation_rescale'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'n_questions': 20, 'old_per': 5, 'new_per': 6, 'top': 80, 'r': '0.73'}, {'n_questions': 20, 'old_per': 10, 'new_per': 12, 'top': 180, 'r': '0.02'}, {'n_questions': 20, 'old_per': 4, 'new_per': 5, 'top': 64, 'r': '-0.82'}, {'n_questions': 25, 'old_per': 5, 'new_per': 8, 'top': 105, 'r': '0.33'}, {'n_questions': 20, 'old_per': 5, 'new_per': 7, 'top': 50, 'r': '0.64'}, {'n_questions': 25, 'old_per': 10, 'new_per': 12, 'top': 210, 'r': '-0.25'}, {'n_questions': 20, 'old_per': 10, 'new_per': 12, 'top': 180, 'r': '0.64'}, {'n_questions': 20, 'old_per': 5, 'new_per': 6, 'top': 50, 'r': '-0.56'}, {'n_questions': 10, 'old_per': 2, 'new_per': 3, 'top': 18, 'r': '0.69'}, {'n_questions': 10, 'old_per': 5, 'new_per': 7, 'top': 25, 'r': '0.42'}, {'n_questions': 20, 'old_per': 2, 'new_per': 3, 'top': 36, 'r': '-0.95'}, {'n_questions': 20, 'old_per': 4, 'new_per': 5, 'top': 44, 'r': '0.69'}, {'n_questions': 10, 'old_per': 10, 'new_per': 12, 'top': 90, 'r': '-0.84'}, {'n_questions': 10, 'old_per': 5, 'new_per': 6, 'top': 35, 'r': '0.23'}, {'n_questions': 10, 'old_per': 5, 'new_per': 7, 'top': 30, 'r': '-0.5'}, {'n_questions': 10, 'old_per': 2, 'new_per': 3, 'top': 12, 'r': '0.16'}, {'n_questions': 10, 'old_per': 5, 'new_per': 6, 'top': 30, 'r': '0.64'}, {'n_questions': 10, 'old_per': 10, 'new_per': 12, 'top': 50, 'r': '0.94'}, {'n_questions': 25, 'old_per': 10, 'new_per': 12, 'top': 160, 'r': '0.2'}, {'n_questions': 25, 'old_per': 5, 'new_per': 8, 'top': 70, 'r': '0.79'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_CorrelationCoefficient', 'fixed_domain_key': 'statistics.bivariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['correlation_rescale'], 'matched_capabilities': ['correlation_rescale'], 'selected_operation': 'correlation_rescale', 'registry_revision': 'promoted-f99c60060e70', 'domain_module': 'core.domain.promoted.bivariate_statistics.bivariate_statistics_domain', 'entrypoint': 'build_bivariate_statistics_matrix', 'allowed_operations': ['correlation_change_add_point', 'correlation_from_table', 'correlation_remove_point', 'correlation_rescale', 'true_false_bivariate'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_CorrelationCoefficient'}), seed)
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
