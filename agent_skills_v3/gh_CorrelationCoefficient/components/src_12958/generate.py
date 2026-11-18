from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "true_false_bivariate"
TEXTBOOK_EXAMPLE_ID = 12958
DEFAULT_COMPONENT_ID = "src_12958" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CorrelationCoefficient"
FIXED_DOMAIN_KEY = "statistics.bivariate_descriptive"
DOMAIN_OPERATION = "true_false_bivariate"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['true_false_bivariate'], 'domain_operation': 'true_false_bivariate', 'problem_type_id': 'true_false_bivariate', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'claim': {'kind': 'points_on_line', 'a': 2, 'b': -1, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-3', 'b': 5, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-3', 'b': -1, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-4', 'b': 5, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-4', 'b': 3, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '2', 'b': 1, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-1/2', 'b': -2, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '1', 'b': -4, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '1/2', 'b': 0, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '1/2', 'b': 6, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-1', 'b': 4, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-3/2', 'b': -4, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-4', 'b': -3, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '3/2', 'b': 4, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-1/2', 'b': -5, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '4', 'b': -1, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-1/2', 'b': 6, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-1/2', 'b': -6, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-4', 'b': -6, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-3/2', 'b': 2, 'stated': -1}}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['true_false_bivariate'], 'domain_operation': 'true_false_bivariate', 'problem_type_id': 'true_false_bivariate', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'claim': {'kind': 'points_on_line', 'a': 2, 'b': -1, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-3', 'b': 5, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-3', 'b': -1, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-4', 'b': 5, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-4', 'b': 3, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '2', 'b': 1, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-1/2', 'b': -2, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '1', 'b': -4, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '1/2', 'b': 0, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '1/2', 'b': 6, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-1', 'b': 4, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-3/2', 'b': -4, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-4', 'b': -3, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '3/2', 'b': 4, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-1/2', 'b': -5, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '4', 'b': -1, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-1/2', 'b': 6, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-1/2', 'b': -6, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-4', 'b': -6, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-3/2', 'b': 2, 'stated': -1}}]}}, 'problem_type_id': 'true_false_bivariate', 'required_capabilities': ['true_false_bivariate'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'claim': {'kind': 'points_on_line', 'a': 2, 'b': -1, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-3', 'b': 5, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-3', 'b': -1, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-4', 'b': 5, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-4', 'b': 3, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '2', 'b': 1, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-1/2', 'b': -2, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '1', 'b': -4, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '1/2', 'b': 0, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '1/2', 'b': 6, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-1', 'b': 4, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-3/2', 'b': -4, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-4', 'b': -3, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '3/2', 'b': 4, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-1/2', 'b': -5, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '4', 'b': -1, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-1/2', 'b': 6, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-1/2', 'b': -6, 'stated': -1}}, {'claim': {'kind': 'points_on_line', 'a': '-4', 'b': -6, 'stated': 1}}, {'claim': {'kind': 'points_on_line', 'a': '-3/2', 'b': 2, 'stated': -1}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_CorrelationCoefficient', 'fixed_domain_key': 'statistics.bivariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['true_false_bivariate'], 'matched_capabilities': ['true_false_bivariate'], 'selected_operation': 'true_false_bivariate', 'registry_revision': 'promoted-f99c60060e70', 'domain_module': 'core.domain.promoted.bivariate_statistics.bivariate_statistics_domain', 'entrypoint': 'build_bivariate_statistics_matrix', 'allowed_operations': ['correlation_change_add_point', 'correlation_from_table', 'correlation_remove_point', 'correlation_rescale', 'true_false_bivariate'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_CorrelationCoefficient'}), seed)
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
