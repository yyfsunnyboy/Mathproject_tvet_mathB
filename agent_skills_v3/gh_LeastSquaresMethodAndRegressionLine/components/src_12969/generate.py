from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "regression_from_table"
TEXTBOOK_EXAMPLE_ID = 12969
DEFAULT_COMPONENT_ID = "src_12969" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['regression_from_table'], 'domain_operation': 'regression_from_table', 'problem_type_id': 'regression_from_table', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'x': [16, 17, 18, 19, 20], 'y': [9, 10, 8, 6, 7], 'x0': '17.5', 'scene': 'price_demand'}, {'x': [26, 27, 28, 29, 30], 'y': [3, 3, 7, 5, 11], 'x0': '29.5', 'scene': 'price_demand'}, {'x': [24, 25, 26, 27, 28], 'y': [6, 8, 4, 8, 8], 'x0': '26.5', 'scene': 'price_demand'}, {'x': [13, 14, 15, 16, 17], 'y': [9, 6, 11, 7, 10], 'x0': '14.5', 'scene': 'price_demand'}, {'x': [19, 20, 21, 22, 23], 'y': [8, 10, 3, 8, 3], 'x0': '22.5', 'scene': 'price_demand'}, {'x': [20, 21, 22, 23, 24], 'y': [9, 12, 11, 4, 9], 'x0': '20.5', 'scene': 'price_demand'}, {'x': [22, 23, 24, 25, 26], 'y': [6, 4, 9, 7, 9], 'x0': '23.5', 'scene': 'price_demand'}, {'x': [14, 15, 16, 17, 18], 'y': [5, 4, 12, 6, 8], 'x0': '16.5', 'scene': 'price_demand'}, {'x': [23, 24, 25, 26, 27], 'y': [9, 5, 6, 12, 5], 'x0': '26.5', 'scene': 'price_demand'}, {'x': [24, 25, 26, 27, 28], 'y': [11, 12, 12, 10, 6], 'x0': '24.5', 'scene': 'price_demand'}, {'x': [10, 11, 12, 13, 14, 15], 'y': [6, 7, 4, 10, 9, 12], 'x0': '13.5', 'scene': 'price_demand'}, {'x': [23, 24, 25, 26, 27], 'y': [5, 11, 3, 4, 8], 'x0': '25.5', 'scene': 'price_demand'}, {'x': [11, 12, 13, 14, 15], 'y': [7, 3, 7, 5, 3], 'x0': '12.5', 'scene': 'price_demand'}, {'x': [11, 12, 13, 14, 15], 'y': [3, 8, 8, 7, 9], 'x0': '13.5', 'scene': 'price_demand'}, {'x': [19, 20, 21, 22, 23], 'y': [7, 10, 3, 9, 3], 'x0': '19.5', 'scene': 'price_demand'}, {'x': [25, 26, 27, 28, 29], 'y': [5, 7, 5, 12, 11], 'x0': '26.5', 'scene': 'price_demand'}, {'x': [22, 23, 24, 25, 26], 'y': [8, 9, 6, 11, 10], 'x0': '23.5', 'scene': 'price_demand'}, {'x': [26, 27, 28, 29, 30], 'y': [8, 6, 4, 4, 6], 'x0': '28.5', 'scene': 'price_demand'}, {'x': [29, 30, 31, 32, 33], 'y': [10, 3, 11, 3, 12], 'x0': '30.5', 'scene': 'price_demand'}, {'x': [23, 24, 25, 26, 27], 'y': [9, 5, 5, 9, 6], 'x0': '25.5', 'scene': 'price_demand'}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['regression_from_table'], 'domain_operation': 'regression_from_table', 'problem_type_id': 'regression_from_table', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'x': [16, 17, 18, 19, 20], 'y': [9, 10, 8, 6, 7], 'x0': '17.5', 'scene': 'price_demand'}, {'x': [26, 27, 28, 29, 30], 'y': [3, 3, 7, 5, 11], 'x0': '29.5', 'scene': 'price_demand'}, {'x': [24, 25, 26, 27, 28], 'y': [6, 8, 4, 8, 8], 'x0': '26.5', 'scene': 'price_demand'}, {'x': [13, 14, 15, 16, 17], 'y': [9, 6, 11, 7, 10], 'x0': '14.5', 'scene': 'price_demand'}, {'x': [19, 20, 21, 22, 23], 'y': [8, 10, 3, 8, 3], 'x0': '22.5', 'scene': 'price_demand'}, {'x': [20, 21, 22, 23, 24], 'y': [9, 12, 11, 4, 9], 'x0': '20.5', 'scene': 'price_demand'}, {'x': [22, 23, 24, 25, 26], 'y': [6, 4, 9, 7, 9], 'x0': '23.5', 'scene': 'price_demand'}, {'x': [14, 15, 16, 17, 18], 'y': [5, 4, 12, 6, 8], 'x0': '16.5', 'scene': 'price_demand'}, {'x': [23, 24, 25, 26, 27], 'y': [9, 5, 6, 12, 5], 'x0': '26.5', 'scene': 'price_demand'}, {'x': [24, 25, 26, 27, 28], 'y': [11, 12, 12, 10, 6], 'x0': '24.5', 'scene': 'price_demand'}, {'x': [10, 11, 12, 13, 14, 15], 'y': [6, 7, 4, 10, 9, 12], 'x0': '13.5', 'scene': 'price_demand'}, {'x': [23, 24, 25, 26, 27], 'y': [5, 11, 3, 4, 8], 'x0': '25.5', 'scene': 'price_demand'}, {'x': [11, 12, 13, 14, 15], 'y': [7, 3, 7, 5, 3], 'x0': '12.5', 'scene': 'price_demand'}, {'x': [11, 12, 13, 14, 15], 'y': [3, 8, 8, 7, 9], 'x0': '13.5', 'scene': 'price_demand'}, {'x': [19, 20, 21, 22, 23], 'y': [7, 10, 3, 9, 3], 'x0': '19.5', 'scene': 'price_demand'}, {'x': [25, 26, 27, 28, 29], 'y': [5, 7, 5, 12, 11], 'x0': '26.5', 'scene': 'price_demand'}, {'x': [22, 23, 24, 25, 26], 'y': [8, 9, 6, 11, 10], 'x0': '23.5', 'scene': 'price_demand'}, {'x': [26, 27, 28, 29, 30], 'y': [8, 6, 4, 4, 6], 'x0': '28.5', 'scene': 'price_demand'}, {'x': [29, 30, 31, 32, 33], 'y': [10, 3, 11, 3, 12], 'x0': '30.5', 'scene': 'price_demand'}, {'x': [23, 24, 25, 26, 27], 'y': [9, 5, 5, 9, 6], 'x0': '25.5', 'scene': 'price_demand'}]}}, 'problem_type_id': 'regression_from_table', 'required_capabilities': ['regression_from_table'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'x': [16, 17, 18, 19, 20], 'y': [9, 10, 8, 6, 7], 'x0': '17.5', 'scene': 'price_demand'}, {'x': [26, 27, 28, 29, 30], 'y': [3, 3, 7, 5, 11], 'x0': '29.5', 'scene': 'price_demand'}, {'x': [24, 25, 26, 27, 28], 'y': [6, 8, 4, 8, 8], 'x0': '26.5', 'scene': 'price_demand'}, {'x': [13, 14, 15, 16, 17], 'y': [9, 6, 11, 7, 10], 'x0': '14.5', 'scene': 'price_demand'}, {'x': [19, 20, 21, 22, 23], 'y': [8, 10, 3, 8, 3], 'x0': '22.5', 'scene': 'price_demand'}, {'x': [20, 21, 22, 23, 24], 'y': [9, 12, 11, 4, 9], 'x0': '20.5', 'scene': 'price_demand'}, {'x': [22, 23, 24, 25, 26], 'y': [6, 4, 9, 7, 9], 'x0': '23.5', 'scene': 'price_demand'}, {'x': [14, 15, 16, 17, 18], 'y': [5, 4, 12, 6, 8], 'x0': '16.5', 'scene': 'price_demand'}, {'x': [23, 24, 25, 26, 27], 'y': [9, 5, 6, 12, 5], 'x0': '26.5', 'scene': 'price_demand'}, {'x': [24, 25, 26, 27, 28], 'y': [11, 12, 12, 10, 6], 'x0': '24.5', 'scene': 'price_demand'}, {'x': [10, 11, 12, 13, 14, 15], 'y': [6, 7, 4, 10, 9, 12], 'x0': '13.5', 'scene': 'price_demand'}, {'x': [23, 24, 25, 26, 27], 'y': [5, 11, 3, 4, 8], 'x0': '25.5', 'scene': 'price_demand'}, {'x': [11, 12, 13, 14, 15], 'y': [7, 3, 7, 5, 3], 'x0': '12.5', 'scene': 'price_demand'}, {'x': [11, 12, 13, 14, 15], 'y': [3, 8, 8, 7, 9], 'x0': '13.5', 'scene': 'price_demand'}, {'x': [19, 20, 21, 22, 23], 'y': [7, 10, 3, 9, 3], 'x0': '19.5', 'scene': 'price_demand'}, {'x': [25, 26, 27, 28, 29], 'y': [5, 7, 5, 12, 11], 'x0': '26.5', 'scene': 'price_demand'}, {'x': [22, 23, 24, 25, 26], 'y': [8, 9, 6, 11, 10], 'x0': '23.5', 'scene': 'price_demand'}, {'x': [26, 27, 28, 29, 30], 'y': [8, 6, 4, 4, 6], 'x0': '28.5', 'scene': 'price_demand'}, {'x': [29, 30, 31, 32, 33], 'y': [10, 3, 11, 3, 12], 'x0': '30.5', 'scene': 'price_demand'}, {'x': [23, 24, 25, 26, 27], 'y': [9, 5, 5, 9, 6], 'x0': '25.5', 'scene': 'price_demand'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_LeastSquaresMethodAndRegressionLine', 'fixed_domain_key': 'statistics.bivariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['regression_from_table'], 'matched_capabilities': ['regression_from_table'], 'selected_operation': 'regression_from_table', 'registry_revision': 'promoted-f99c60060e70', 'domain_module': 'core.domain.promoted.bivariate_statistics.bivariate_statistics_domain', 'entrypoint': 'build_bivariate_statistics_matrix', 'allowed_operations': ['correlation_from_regression_point', 'regression_from_summary', 'regression_from_table', 'regression_line_unknown_intercept', 'regression_rounded_from_table', 'regression_statement_selection', 'true_false_bivariate'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_LeastSquaresMethodAndRegressionLine'}), seed)
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
