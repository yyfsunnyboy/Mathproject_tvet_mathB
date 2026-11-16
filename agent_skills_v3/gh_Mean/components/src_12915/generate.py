from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "arithmetic_mean"
TEXTBOOK_EXAMPLE_ID = 12915
DEFAULT_COMPONENT_ID = "src_12915" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Mean"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "arithmetic_mean"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['arithmetic_mean'], 'domain_operation': 'arithmetic_mean', 'problem_type_id': 'arithmetic_mean', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'values': [21, 13, 23, 21, 22, 20]}, {'values': [40, 48, 46, 44, 53, 43]}, {'values': [52, 41, 36, 36]}, {'values': [34, 36, 33, 35, 52, 51]}, {'values': [41, 32, 33, 40, 42, 28]}, {'values': [44, 45, 41, 35, 25, 34]}, {'values': [28, 38, 31, 29, 35]}, {'values': [54, 35, 41, 45, 53, 43]}, {'values': [31, 39, 22, 41, 23]}, {'values': [40, 32, 48, 47, 31, 39]}, {'values': [38, 51, 42, 39]}, {'values': [31, 17, 19, 26]}, {'values': [14, 16, 17, 25, 27, 17]}, {'values': [28, 39, 38, 34]}, {'values': [43, 58, 52, 50]}, {'values': [45, 48, 39, 55, 55]}, {'values': [23, 20, 18, 34, 16]}, {'values': [43, 27, 46, 38, 26]}, {'values': [27, 20, 33, 32, 35]}, {'values': [43, 42, 58, 47, 47]}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['arithmetic_mean'], 'domain_operation': 'arithmetic_mean', 'problem_type_id': 'arithmetic_mean', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'values': [21, 13, 23, 21, 22, 20]}, {'values': [40, 48, 46, 44, 53, 43]}, {'values': [52, 41, 36, 36]}, {'values': [34, 36, 33, 35, 52, 51]}, {'values': [41, 32, 33, 40, 42, 28]}, {'values': [44, 45, 41, 35, 25, 34]}, {'values': [28, 38, 31, 29, 35]}, {'values': [54, 35, 41, 45, 53, 43]}, {'values': [31, 39, 22, 41, 23]}, {'values': [40, 32, 48, 47, 31, 39]}, {'values': [38, 51, 42, 39]}, {'values': [31, 17, 19, 26]}, {'values': [14, 16, 17, 25, 27, 17]}, {'values': [28, 39, 38, 34]}, {'values': [43, 58, 52, 50]}, {'values': [45, 48, 39, 55, 55]}, {'values': [23, 20, 18, 34, 16]}, {'values': [43, 27, 46, 38, 26]}, {'values': [27, 20, 33, 32, 35]}, {'values': [43, 42, 58, 47, 47]}]}}, 'problem_type_id': 'arithmetic_mean', 'required_capabilities': ['arithmetic_mean'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'values': [21, 13, 23, 21, 22, 20]}, {'values': [40, 48, 46, 44, 53, 43]}, {'values': [52, 41, 36, 36]}, {'values': [34, 36, 33, 35, 52, 51]}, {'values': [41, 32, 33, 40, 42, 28]}, {'values': [44, 45, 41, 35, 25, 34]}, {'values': [28, 38, 31, 29, 35]}, {'values': [54, 35, 41, 45, 53, 43]}, {'values': [31, 39, 22, 41, 23]}, {'values': [40, 32, 48, 47, 31, 39]}, {'values': [38, 51, 42, 39]}, {'values': [31, 17, 19, 26]}, {'values': [14, 16, 17, 25, 27, 17]}, {'values': [28, 39, 38, 34]}, {'values': [43, 58, 52, 50]}, {'values': [45, 48, 39, 55, 55]}, {'values': [23, 20, 18, 34, 16]}, {'values': [43, 27, 46, 38, 26]}, {'values': [27, 20, 33, 32, 35]}, {'values': [43, 42, 58, 47, 47]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Mean', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['arithmetic_mean'], 'matched_capabilities': ['arithmetic_mean'], 'selected_operation': 'arithmetic_mean', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['arithmetic_mean', 'geometric_growth_mean', 'geometric_growth_unknown', 'true_false_stat', 'weighted_mean', 'weighted_mean_unknown'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Mean'}), seed)
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
