from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "standardize_scores"
TEXTBOOK_EXAMPLE_ID = 12943
DEFAULT_COMPONENT_ID = "src_12943" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_DataScalingAndShifting"
FIXED_DOMAIN_KEY = "statistics.univariate_descriptive"
DOMAIN_OPERATION = "standardize_scores"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['standardize_scores'], 'domain_operation': 'standardize_scores', 'problem_type_id': 'standardize_scores', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'means': [68, 60], 'sds': [5, 4], 'scores': [73, 65], 'subjects': ['數學', '英文']}, {'means': [61, 57], 'sds': [8, 3], 'scores': [76, 64], 'subjects': ['數學', '英文']}, {'means': [53, 66], 'sds': [4, 8], 'scores': [56, 78], 'subjects': ['數學', '英文']}, {'means': [59, 59], 'sds': [6, 4], 'scores': [63, 62], 'subjects': ['數學', '英文']}, {'means': [51, 65], 'sds': [4, 3], 'scores': [63, 75], 'subjects': ['數學', '英文']}, {'means': [56, 60], 'sds': [8, 3], 'scores': [62, 61], 'subjects': ['數學', '英文']}, {'means': [58, 53], 'sds': [7, 5], 'scores': [60, 63], 'subjects': ['數學', '英文']}, {'means': [67, 56], 'sds': [6, 8], 'scores': [74, 65], 'subjects': ['數學', '英文']}, {'means': [50, 57], 'sds': [10, 3], 'scores': [54, 62], 'subjects': ['數學', '英文']}, {'means': [51, 62], 'sds': [5, 10], 'scores': [57, 72], 'subjects': ['數學', '英文']}, {'means': [52, 60], 'sds': [8, 4], 'scores': [61, 66], 'subjects': ['數學', '英文']}, {'means': [66, 55], 'sds': [5, 10], 'scores': [75, 59], 'subjects': ['數學', '英文']}, {'means': [56, 64], 'sds': [6, 10], 'scores': [58, 74], 'subjects': ['數學', '英文']}, {'means': [69, 69], 'sds': [4, 3], 'scores': [82, 78], 'subjects': ['數學', '英文']}, {'means': [65, 62], 'sds': [5, 4], 'scores': [66, 69], 'subjects': ['數學', '英文']}, {'means': [59, 53], 'sds': [9, 7], 'scores': [64, 63], 'subjects': ['數學', '英文']}, {'means': [62, 54], 'sds': [6, 4], 'scores': [76, 68], 'subjects': ['數學', '英文']}, {'means': [53, 64], 'sds': [6, 9], 'scores': [64, 74], 'subjects': ['數學', '英文']}, {'means': [63, 55], 'sds': [10, 7], 'scores': [73, 56], 'subjects': ['數學', '英文']}, {'means': [67, 70], 'sds': [7, 8], 'scores': [73, 82], 'subjects': ['數學', '英文']}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.univariate_descriptive', 'required_capabilities': ['standardize_scores'], 'domain_operation': 'standardize_scores', 'problem_type_id': 'standardize_scores', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'means': [68, 60], 'sds': [5, 4], 'scores': [73, 65], 'subjects': ['數學', '英文']}, {'means': [61, 57], 'sds': [8, 3], 'scores': [76, 64], 'subjects': ['數學', '英文']}, {'means': [53, 66], 'sds': [4, 8], 'scores': [56, 78], 'subjects': ['數學', '英文']}, {'means': [59, 59], 'sds': [6, 4], 'scores': [63, 62], 'subjects': ['數學', '英文']}, {'means': [51, 65], 'sds': [4, 3], 'scores': [63, 75], 'subjects': ['數學', '英文']}, {'means': [56, 60], 'sds': [8, 3], 'scores': [62, 61], 'subjects': ['數學', '英文']}, {'means': [58, 53], 'sds': [7, 5], 'scores': [60, 63], 'subjects': ['數學', '英文']}, {'means': [67, 56], 'sds': [6, 8], 'scores': [74, 65], 'subjects': ['數學', '英文']}, {'means': [50, 57], 'sds': [10, 3], 'scores': [54, 62], 'subjects': ['數學', '英文']}, {'means': [51, 62], 'sds': [5, 10], 'scores': [57, 72], 'subjects': ['數學', '英文']}, {'means': [52, 60], 'sds': [8, 4], 'scores': [61, 66], 'subjects': ['數學', '英文']}, {'means': [66, 55], 'sds': [5, 10], 'scores': [75, 59], 'subjects': ['數學', '英文']}, {'means': [56, 64], 'sds': [6, 10], 'scores': [58, 74], 'subjects': ['數學', '英文']}, {'means': [69, 69], 'sds': [4, 3], 'scores': [82, 78], 'subjects': ['數學', '英文']}, {'means': [65, 62], 'sds': [5, 4], 'scores': [66, 69], 'subjects': ['數學', '英文']}, {'means': [59, 53], 'sds': [9, 7], 'scores': [64, 63], 'subjects': ['數學', '英文']}, {'means': [62, 54], 'sds': [6, 4], 'scores': [76, 68], 'subjects': ['數學', '英文']}, {'means': [53, 64], 'sds': [6, 9], 'scores': [64, 74], 'subjects': ['數學', '英文']}, {'means': [63, 55], 'sds': [10, 7], 'scores': [73, 56], 'subjects': ['數學', '英文']}, {'means': [67, 70], 'sds': [7, 8], 'scores': [73, 82], 'subjects': ['數學', '英文']}]}}, 'problem_type_id': 'standardize_scores', 'required_capabilities': ['standardize_scores'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'means': [68, 60], 'sds': [5, 4], 'scores': [73, 65], 'subjects': ['數學', '英文']}, {'means': [61, 57], 'sds': [8, 3], 'scores': [76, 64], 'subjects': ['數學', '英文']}, {'means': [53, 66], 'sds': [4, 8], 'scores': [56, 78], 'subjects': ['數學', '英文']}, {'means': [59, 59], 'sds': [6, 4], 'scores': [63, 62], 'subjects': ['數學', '英文']}, {'means': [51, 65], 'sds': [4, 3], 'scores': [63, 75], 'subjects': ['數學', '英文']}, {'means': [56, 60], 'sds': [8, 3], 'scores': [62, 61], 'subjects': ['數學', '英文']}, {'means': [58, 53], 'sds': [7, 5], 'scores': [60, 63], 'subjects': ['數學', '英文']}, {'means': [67, 56], 'sds': [6, 8], 'scores': [74, 65], 'subjects': ['數學', '英文']}, {'means': [50, 57], 'sds': [10, 3], 'scores': [54, 62], 'subjects': ['數學', '英文']}, {'means': [51, 62], 'sds': [5, 10], 'scores': [57, 72], 'subjects': ['數學', '英文']}, {'means': [52, 60], 'sds': [8, 4], 'scores': [61, 66], 'subjects': ['數學', '英文']}, {'means': [66, 55], 'sds': [5, 10], 'scores': [75, 59], 'subjects': ['數學', '英文']}, {'means': [56, 64], 'sds': [6, 10], 'scores': [58, 74], 'subjects': ['數學', '英文']}, {'means': [69, 69], 'sds': [4, 3], 'scores': [82, 78], 'subjects': ['數學', '英文']}, {'means': [65, 62], 'sds': [5, 4], 'scores': [66, 69], 'subjects': ['數學', '英文']}, {'means': [59, 53], 'sds': [9, 7], 'scores': [64, 63], 'subjects': ['數學', '英文']}, {'means': [62, 54], 'sds': [6, 4], 'scores': [76, 68], 'subjects': ['數學', '英文']}, {'means': [53, 64], 'sds': [6, 9], 'scores': [64, 74], 'subjects': ['數學', '英文']}, {'means': [63, 55], 'sds': [10, 7], 'scores': [73, 56], 'subjects': ['數學', '英文']}, {'means': [67, 70], 'sds': [7, 8], 'scores': [73, 82], 'subjects': ['數學', '英文']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_DataScalingAndShifting', 'fixed_domain_key': 'statistics.univariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['standardize_scores'], 'matched_capabilities': ['standardize_scores'], 'selected_operation': 'standardize_scores', 'registry_revision': 'promoted-0a33ae94fd3a', 'domain_module': 'core.domain.promoted.univariate_statistics.univariate_statistics_domain', 'entrypoint': 'build_univariate_statistics_matrix', 'allowed_operations': ['linear_find_scale_sd', 'linear_mean_sd', 'monthly_mean_sd', 'standardize_scores', 'statement_selection', 'true_false_stat'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_DataScalingAndShifting'}), seed)
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
