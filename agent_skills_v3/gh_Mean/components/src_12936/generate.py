from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "weighted_mean_unknown"
TEXTBOOK_EXAMPLE_ID = 12936
DEFAULT_COMPONENT_ID = "src_12936" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Mean"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "weighted_mean_unknown"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['weighted_mean_unknown'], 'domain_operation': 'weighted_mean_unknown', 'problem_type_id': 'weighted_mean_unknown', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'values': [65, 46, 53, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': 60, 'unknown_index': 3}, {'values': [45, 59, 59, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '125/2', 'unknown_index': 3}, {'values': [80, 75, 80, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '374/5', 'unknown_index': 3}, {'values': [65, 42, 41, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '109/2', 'unknown_index': 3}, {'values': [66, 73, 79, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '362/5', 'unknown_index': 3}, {'values': [49, 51, 61, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '301/5', 'unknown_index': 3}, {'values': [64, 68, 73, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '153/2', 'unknown_index': 3}, {'values': [73, 44, 62, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '239/4', 'unknown_index': 3}, {'values': [56, 60, 65, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '341/5', 'unknown_index': 3}, {'values': [42, 42, 65, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '119/2', 'unknown_index': 3}, {'values': [46, 68, 80, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '69', 'unknown_index': 3}, {'values': [41, 76, 42, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '50', 'unknown_index': 3}, {'values': [53, 66, 49, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '117/2', 'unknown_index': 3}, {'values': [57, 43, 60, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '231/4', 'unknown_index': 3}, {'values': [41, 44, 80, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '557/10', 'unknown_index': 3}, {'values': [59, 75, 72, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '591/10', 'unknown_index': 3}, {'values': [51, 64, 72, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '292/5', 'unknown_index': 3}, {'values': [53, 41, 51, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '95/2', 'unknown_index': 3}, {'values': [71, 63, 68, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '383/5', 'unknown_index': 3}, {'values': [58, 54, 66, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '109/2', 'unknown_index': 3}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['weighted_mean_unknown'], 'domain_operation': 'weighted_mean_unknown', 'problem_type_id': 'weighted_mean_unknown', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'values': [65, 46, 53, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': 60, 'unknown_index': 3}, {'values': [45, 59, 59, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '125/2', 'unknown_index': 3}, {'values': [80, 75, 80, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '374/5', 'unknown_index': 3}, {'values': [65, 42, 41, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '109/2', 'unknown_index': 3}, {'values': [66, 73, 79, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '362/5', 'unknown_index': 3}, {'values': [49, 51, 61, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '301/5', 'unknown_index': 3}, {'values': [64, 68, 73, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '153/2', 'unknown_index': 3}, {'values': [73, 44, 62, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '239/4', 'unknown_index': 3}, {'values': [56, 60, 65, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '341/5', 'unknown_index': 3}, {'values': [42, 42, 65, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '119/2', 'unknown_index': 3}, {'values': [46, 68, 80, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '69', 'unknown_index': 3}, {'values': [41, 76, 42, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '50', 'unknown_index': 3}, {'values': [53, 66, 49, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '117/2', 'unknown_index': 3}, {'values': [57, 43, 60, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '231/4', 'unknown_index': 3}, {'values': [41, 44, 80, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '557/10', 'unknown_index': 3}, {'values': [59, 75, 72, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '591/10', 'unknown_index': 3}, {'values': [51, 64, 72, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '292/5', 'unknown_index': 3}, {'values': [53, 41, 51, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '95/2', 'unknown_index': 3}, {'values': [71, 63, 68, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '383/5', 'unknown_index': 3}, {'values': [58, 54, 66, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '109/2', 'unknown_index': 3}]}}, 'problem_type_id': 'weighted_mean_unknown', 'required_capabilities': ['weighted_mean_unknown'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'values': [65, 46, 53, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': 60, 'unknown_index': 3}, {'values': [45, 59, 59, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '125/2', 'unknown_index': 3}, {'values': [80, 75, 80, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '374/5', 'unknown_index': 3}, {'values': [65, 42, 41, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '109/2', 'unknown_index': 3}, {'values': [66, 73, 79, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '362/5', 'unknown_index': 3}, {'values': [49, 51, 61, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '301/5', 'unknown_index': 3}, {'values': [64, 68, 73, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '153/2', 'unknown_index': 3}, {'values': [73, 44, 62, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '239/4', 'unknown_index': 3}, {'values': [56, 60, 65, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '341/5', 'unknown_index': 3}, {'values': [42, 42, 65, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '119/2', 'unknown_index': 3}, {'values': [46, 68, 80, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '69', 'unknown_index': 3}, {'values': [41, 76, 42, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '50', 'unknown_index': 3}, {'values': [53, 66, 49, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '117/2', 'unknown_index': 3}, {'values': [57, 43, 60, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '231/4', 'unknown_index': 3}, {'values': [41, 44, 80, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '557/10', 'unknown_index': 3}, {'values': [59, 75, 72, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '591/10', 'unknown_index': 3}, {'values': [51, 64, 72, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '292/5', 'unknown_index': 3}, {'values': [53, 41, 51, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '95/2', 'unknown_index': 3}, {'values': [71, 63, 68, 'x'], 'weights': ['0.3', '0.2', '0.2', '0.3'], 'known_mean': '383/5', 'unknown_index': 3}, {'values': [58, 54, 66, 'x'], 'weights': ['0.25', '0.25', '0.25', '0.25'], 'known_mean': '109/2', 'unknown_index': 3}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Mean', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['weighted_mean_unknown'], 'matched_capabilities': ['weighted_mean_unknown'], 'selected_operation': 'weighted_mean_unknown', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['arithmetic_mean', 'geometric_growth_mean', 'geometric_growth_unknown', 'true_false_stat', 'weighted_mean', 'weighted_mean_unknown'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Mean'}), seed)
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
