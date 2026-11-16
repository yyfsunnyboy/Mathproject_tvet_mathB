from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "arithmetic_mean"
TEXTBOOK_EXAMPLE_ID = 12912
DEFAULT_COMPONENT_ID = "src_12912" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['arithmetic_mean'], 'domain_operation': 'arithmetic_mean', 'problem_type_id': 'arithmetic_mean', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'values': [186, 188, 189, 191, 226]}, {'values': [47, 45, 48, 48, 51]}, {'values': [27, 27, 27, 16, 33, 17]}, {'values': [34, 47, 47, 52]}, {'values': [15, 14, 17, 20]}, {'values': [19, 27, 31, 14, 33, 15]}, {'values': [24, 28, 35, 34, 18, 35]}, {'values': [32, 18, 25, 30, 20, 25]}, {'values': [30, 50, 32, 34, 32, 32]}, {'values': [41, 50, 47, 50, 35, 45]}, {'values': [40, 47, 40, 43, 40, 46]}, {'values': [40, 31, 27, 39]}, {'values': [32, 43, 37, 34, 51]}, {'values': [48, 37, 37, 46, 49, 40]}, {'values': [41, 27, 42, 35]}, {'values': [47, 42, 32, 32, 37]}, {'values': [34, 29, 39, 39, 37]}, {'values': [25, 18, 31, 16, 30]}, {'values': [44, 39, 31, 39, 46]}, {'values': [37, 48, 55, 42, 45]}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['arithmetic_mean'], 'domain_operation': 'arithmetic_mean', 'problem_type_id': 'arithmetic_mean', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'values': [186, 188, 189, 191, 226]}, {'values': [47, 45, 48, 48, 51]}, {'values': [27, 27, 27, 16, 33, 17]}, {'values': [34, 47, 47, 52]}, {'values': [15, 14, 17, 20]}, {'values': [19, 27, 31, 14, 33, 15]}, {'values': [24, 28, 35, 34, 18, 35]}, {'values': [32, 18, 25, 30, 20, 25]}, {'values': [30, 50, 32, 34, 32, 32]}, {'values': [41, 50, 47, 50, 35, 45]}, {'values': [40, 47, 40, 43, 40, 46]}, {'values': [40, 31, 27, 39]}, {'values': [32, 43, 37, 34, 51]}, {'values': [48, 37, 37, 46, 49, 40]}, {'values': [41, 27, 42, 35]}, {'values': [47, 42, 32, 32, 37]}, {'values': [34, 29, 39, 39, 37]}, {'values': [25, 18, 31, 16, 30]}, {'values': [44, 39, 31, 39, 46]}, {'values': [37, 48, 55, 42, 45]}]}}, 'problem_type_id': 'arithmetic_mean', 'required_capabilities': ['arithmetic_mean'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'values': [186, 188, 189, 191, 226]}, {'values': [47, 45, 48, 48, 51]}, {'values': [27, 27, 27, 16, 33, 17]}, {'values': [34, 47, 47, 52]}, {'values': [15, 14, 17, 20]}, {'values': [19, 27, 31, 14, 33, 15]}, {'values': [24, 28, 35, 34, 18, 35]}, {'values': [32, 18, 25, 30, 20, 25]}, {'values': [30, 50, 32, 34, 32, 32]}, {'values': [41, 50, 47, 50, 35, 45]}, {'values': [40, 47, 40, 43, 40, 46]}, {'values': [40, 31, 27, 39]}, {'values': [32, 43, 37, 34, 51]}, {'values': [48, 37, 37, 46, 49, 40]}, {'values': [41, 27, 42, 35]}, {'values': [47, 42, 32, 32, 37]}, {'values': [34, 29, 39, 39, 37]}, {'values': [25, 18, 31, 16, 30]}, {'values': [44, 39, 31, 39, 46]}, {'values': [37, 48, 55, 42, 45]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Mean', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['arithmetic_mean'], 'matched_capabilities': ['arithmetic_mean'], 'selected_operation': 'arithmetic_mean', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['arithmetic_mean', 'geometric_growth_mean', 'geometric_growth_unknown', 'true_false_stat', 'weighted_mean', 'weighted_mean_unknown'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Mean'}), seed)
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
