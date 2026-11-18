from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "regression_from_table"
TEXTBOOK_EXAMPLE_ID = 12966
DEFAULT_COMPONENT_ID = "src_12966" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_LeastSquaresMethodAndRegressionLine"
FIXED_DOMAIN_KEY = "statistics.bivariate_descriptive"
DOMAIN_OPERATION = "regression_from_table"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['regression_from_table'], 'domain_operation': 'regression_from_table', 'problem_type_id': 'regression_from_table', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'x': [5, 6, 8, 9, 9, 11], 'y': [5, 8, 8, 12, 13, 14], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [4, 5, 7, 8, 10], 'y': [4, 9, 12, 11, 12], 'x0': 5, 'scene': 'eq_achievement'}, {'x': [8, 8, 9, 9, 11, 11], 'y': [5, 12, 9, 16, 16, 18], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [5, 7, 7, 11, 12], 'y': [3, 6, 14, 13, 11], 'x0': 6, 'scene': 'eq_achievement'}, {'x': [5, 5, 6, 6, 13], 'y': [5, 4, 8, 11, 10], 'x0': 11, 'scene': 'eq_achievement'}, {'x': [9, 9, 10, 10, 11], 'y': [4, 10, 10, 14, 17], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [6, 7, 7, 7, 10, 11], 'y': [2, 5, 8, 9, 10, 14], 'x0': 9, 'scene': 'eq_achievement'}, {'x': [10, 10, 12, 12, 13], 'y': [4, 7, 8, 11, 16], 'x0': 11, 'scene': 'eq_achievement'}, {'x': [3, 3, 10, 10, 10, 11, 11], 'y': [7, 6, 9, 12, 9, 11, 10], 'x0': 7, 'scene': 'eq_achievement'}, {'x': [5, 5, 7, 8, 11], 'y': [9, 14, 14, 14, 16], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [6, 6, 9, 11, 11, 13], 'y': [3, 10, 12, 13, 9, 17], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [3, 5, 5, 5, 6, 8], 'y': [6, 6, 9, 14, 15, 17], 'x0': 4, 'scene': 'eq_achievement'}, {'x': [6, 6, 8, 8, 9, 11], 'y': [4, 4, 6, 7, 7, 10], 'x0': 9, 'scene': 'eq_achievement'}, {'x': [8, 8, 9, 10, 12], 'y': [5, 5, 10, 10, 10], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [3, 6, 6, 8, 8, 9], 'y': [5, 5, 9, 11, 15, 16], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [3, 4, 6, 8, 9], 'y': [5, 7, 6, 10, 16], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [4, 5, 6, 6, 9, 9, 10], 'y': [5, 8, 12, 14, 15, 15, 15], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [4, 8, 8, 10, 12], 'y': [3, 2, 12, 11, 15], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [4, 4, 4, 7, 9, 9, 13], 'y': [3, 3, 6, 7, 5, 13, 13], 'x0': 5, 'scene': 'eq_achievement'}, {'x': [5, 5, 6, 7, 8, 8, 13], 'y': [2, 3, 10, 11, 14, 16, 14], 'x0': 7, 'scene': 'eq_achievement'}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['regression_from_table'], 'domain_operation': 'regression_from_table', 'problem_type_id': 'regression_from_table', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'x': [5, 6, 8, 9, 9, 11], 'y': [5, 8, 8, 12, 13, 14], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [4, 5, 7, 8, 10], 'y': [4, 9, 12, 11, 12], 'x0': 5, 'scene': 'eq_achievement'}, {'x': [8, 8, 9, 9, 11, 11], 'y': [5, 12, 9, 16, 16, 18], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [5, 7, 7, 11, 12], 'y': [3, 6, 14, 13, 11], 'x0': 6, 'scene': 'eq_achievement'}, {'x': [5, 5, 6, 6, 13], 'y': [5, 4, 8, 11, 10], 'x0': 11, 'scene': 'eq_achievement'}, {'x': [9, 9, 10, 10, 11], 'y': [4, 10, 10, 14, 17], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [6, 7, 7, 7, 10, 11], 'y': [2, 5, 8, 9, 10, 14], 'x0': 9, 'scene': 'eq_achievement'}, {'x': [10, 10, 12, 12, 13], 'y': [4, 7, 8, 11, 16], 'x0': 11, 'scene': 'eq_achievement'}, {'x': [3, 3, 10, 10, 10, 11, 11], 'y': [7, 6, 9, 12, 9, 11, 10], 'x0': 7, 'scene': 'eq_achievement'}, {'x': [5, 5, 7, 8, 11], 'y': [9, 14, 14, 14, 16], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [6, 6, 9, 11, 11, 13], 'y': [3, 10, 12, 13, 9, 17], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [3, 5, 5, 5, 6, 8], 'y': [6, 6, 9, 14, 15, 17], 'x0': 4, 'scene': 'eq_achievement'}, {'x': [6, 6, 8, 8, 9, 11], 'y': [4, 4, 6, 7, 7, 10], 'x0': 9, 'scene': 'eq_achievement'}, {'x': [8, 8, 9, 10, 12], 'y': [5, 5, 10, 10, 10], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [3, 6, 6, 8, 8, 9], 'y': [5, 5, 9, 11, 15, 16], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [3, 4, 6, 8, 9], 'y': [5, 7, 6, 10, 16], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [4, 5, 6, 6, 9, 9, 10], 'y': [5, 8, 12, 14, 15, 15, 15], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [4, 8, 8, 10, 12], 'y': [3, 2, 12, 11, 15], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [4, 4, 4, 7, 9, 9, 13], 'y': [3, 3, 6, 7, 5, 13, 13], 'x0': 5, 'scene': 'eq_achievement'}, {'x': [5, 5, 6, 7, 8, 8, 13], 'y': [2, 3, 10, 11, 14, 16, 14], 'x0': 7, 'scene': 'eq_achievement'}]}}, 'problem_type_id': 'regression_from_table', 'required_capabilities': ['regression_from_table'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'x': [5, 6, 8, 9, 9, 11], 'y': [5, 8, 8, 12, 13, 14], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [4, 5, 7, 8, 10], 'y': [4, 9, 12, 11, 12], 'x0': 5, 'scene': 'eq_achievement'}, {'x': [8, 8, 9, 9, 11, 11], 'y': [5, 12, 9, 16, 16, 18], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [5, 7, 7, 11, 12], 'y': [3, 6, 14, 13, 11], 'x0': 6, 'scene': 'eq_achievement'}, {'x': [5, 5, 6, 6, 13], 'y': [5, 4, 8, 11, 10], 'x0': 11, 'scene': 'eq_achievement'}, {'x': [9, 9, 10, 10, 11], 'y': [4, 10, 10, 14, 17], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [6, 7, 7, 7, 10, 11], 'y': [2, 5, 8, 9, 10, 14], 'x0': 9, 'scene': 'eq_achievement'}, {'x': [10, 10, 12, 12, 13], 'y': [4, 7, 8, 11, 16], 'x0': 11, 'scene': 'eq_achievement'}, {'x': [3, 3, 10, 10, 10, 11, 11], 'y': [7, 6, 9, 12, 9, 11, 10], 'x0': 7, 'scene': 'eq_achievement'}, {'x': [5, 5, 7, 8, 11], 'y': [9, 14, 14, 14, 16], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [6, 6, 9, 11, 11, 13], 'y': [3, 10, 12, 13, 9, 17], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [3, 5, 5, 5, 6, 8], 'y': [6, 6, 9, 14, 15, 17], 'x0': 4, 'scene': 'eq_achievement'}, {'x': [6, 6, 8, 8, 9, 11], 'y': [4, 4, 6, 7, 7, 10], 'x0': 9, 'scene': 'eq_achievement'}, {'x': [8, 8, 9, 10, 12], 'y': [5, 5, 10, 10, 10], 'x0': 10, 'scene': 'eq_achievement'}, {'x': [3, 6, 6, 8, 8, 9], 'y': [5, 5, 9, 11, 15, 16], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [3, 4, 6, 8, 9], 'y': [5, 7, 6, 10, 16], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [4, 5, 6, 6, 9, 9, 10], 'y': [5, 8, 12, 14, 15, 15, 15], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [4, 8, 8, 10, 12], 'y': [3, 2, 12, 11, 15], 'x0': 8, 'scene': 'eq_achievement'}, {'x': [4, 4, 4, 7, 9, 9, 13], 'y': [3, 3, 6, 7, 5, 13, 13], 'x0': 5, 'scene': 'eq_achievement'}, {'x': [5, 5, 6, 7, 8, 8, 13], 'y': [2, 3, 10, 11, 14, 16, 14], 'x0': 7, 'scene': 'eq_achievement'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_LeastSquaresMethodAndRegressionLine', 'fixed_domain_key': 'statistics.bivariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['regression_from_table'], 'matched_capabilities': ['regression_from_table'], 'selected_operation': 'regression_from_table', 'registry_revision': 'promoted-f99c60060e70', 'domain_module': 'core.domain.promoted.bivariate_statistics.bivariate_statistics_domain', 'entrypoint': 'build_bivariate_statistics_matrix', 'allowed_operations': ['correlation_from_regression_point', 'regression_from_summary', 'regression_from_table', 'regression_line_unknown_intercept', 'regression_rounded_from_table', 'regression_statement_selection', 'true_false_bivariate'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_LeastSquaresMethodAndRegressionLine'}), seed)
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
