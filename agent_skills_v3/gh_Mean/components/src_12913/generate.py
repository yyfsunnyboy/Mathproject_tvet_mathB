from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "weighted_mean"
TEXTBOOK_EXAMPLE_ID = 12913
DEFAULT_COMPONENT_ID = "src_12913" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Mean"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "weighted_mean"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['weighted_mean'], 'domain_operation': 'weighted_mean', 'problem_type_id': 'weighted_mean', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'values': [83, 68, 87, 74], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [47, 71, 90, 50], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [59, 61, 45, 73], 'weights': ['0.4', '0.2', '0.2', '0.2']}, {'values': [68, 77, 92, 74], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [65, 58, 41, 73], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [54, 44, 68, 43], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [46, 80, 82, 47], 'weights': ['0.25', '0.25', '0.25', '0.25']}, {'values': [89, 44, 51, 95], 'weights': ['0.4', '0.2', '0.2', '0.2']}, {'values': [87, 55, 40, 78], 'weights': ['0.4', '0.2', '0.2', '0.2']}, {'values': [62, 85, 71, 88], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [75, 60, 91, 79], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [90, 65, 49, 67], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [88, 66, 95, 92], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [46, 41, 86, 82], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [90, 70, 69, 41], 'weights': ['0.25', '0.25', '0.25', '0.25']}, {'values': [55, 43, 85, 83], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [63, 69, 67, 72], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [84, 50, 88, 81], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [81, 83, 47, 73], 'weights': ['0.25', '0.25', '0.25', '0.25']}, {'values': [94, 50, 93, 88], 'weights': ['0.2', '0.3', '0.3', '0.2']}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['weighted_mean'], 'domain_operation': 'weighted_mean', 'problem_type_id': 'weighted_mean', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'values': [83, 68, 87, 74], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [47, 71, 90, 50], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [59, 61, 45, 73], 'weights': ['0.4', '0.2', '0.2', '0.2']}, {'values': [68, 77, 92, 74], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [65, 58, 41, 73], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [54, 44, 68, 43], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [46, 80, 82, 47], 'weights': ['0.25', '0.25', '0.25', '0.25']}, {'values': [89, 44, 51, 95], 'weights': ['0.4', '0.2', '0.2', '0.2']}, {'values': [87, 55, 40, 78], 'weights': ['0.4', '0.2', '0.2', '0.2']}, {'values': [62, 85, 71, 88], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [75, 60, 91, 79], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [90, 65, 49, 67], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [88, 66, 95, 92], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [46, 41, 86, 82], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [90, 70, 69, 41], 'weights': ['0.25', '0.25', '0.25', '0.25']}, {'values': [55, 43, 85, 83], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [63, 69, 67, 72], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [84, 50, 88, 81], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [81, 83, 47, 73], 'weights': ['0.25', '0.25', '0.25', '0.25']}, {'values': [94, 50, 93, 88], 'weights': ['0.2', '0.3', '0.3', '0.2']}]}}, 'problem_type_id': 'weighted_mean', 'required_capabilities': ['weighted_mean'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'values': [83, 68, 87, 74], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [47, 71, 90, 50], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [59, 61, 45, 73], 'weights': ['0.4', '0.2', '0.2', '0.2']}, {'values': [68, 77, 92, 74], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [65, 58, 41, 73], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [54, 44, 68, 43], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [46, 80, 82, 47], 'weights': ['0.25', '0.25', '0.25', '0.25']}, {'values': [89, 44, 51, 95], 'weights': ['0.4', '0.2', '0.2', '0.2']}, {'values': [87, 55, 40, 78], 'weights': ['0.4', '0.2', '0.2', '0.2']}, {'values': [62, 85, 71, 88], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [75, 60, 91, 79], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [90, 65, 49, 67], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [88, 66, 95, 92], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [46, 41, 86, 82], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [90, 70, 69, 41], 'weights': ['0.25', '0.25', '0.25', '0.25']}, {'values': [55, 43, 85, 83], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [63, 69, 67, 72], 'weights': ['0.3', '0.2', '0.2', '0.3']}, {'values': [84, 50, 88, 81], 'weights': ['0.2', '0.3', '0.3', '0.2']}, {'values': [81, 83, 47, 73], 'weights': ['0.25', '0.25', '0.25', '0.25']}, {'values': [94, 50, 93, 88], 'weights': ['0.2', '0.3', '0.3', '0.2']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Mean', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['weighted_mean'], 'matched_capabilities': ['weighted_mean'], 'selected_operation': 'weighted_mean', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['arithmetic_mean', 'geometric_growth_mean', 'geometric_growth_unknown', 'true_false_stat', 'weighted_mean', 'weighted_mean_unknown'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Mean'}), seed)
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
