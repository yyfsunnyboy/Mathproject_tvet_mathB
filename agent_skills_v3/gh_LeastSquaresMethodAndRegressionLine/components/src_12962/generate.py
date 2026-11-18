from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "regression_from_table"
TEXTBOOK_EXAMPLE_ID = 12962
DEFAULT_COMPONENT_ID = "src_12962" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['regression_from_table'], 'domain_operation': 'regression_from_table', 'problem_type_id': 'regression_from_table', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'x': [33, 31, 29, 27], 'y': [14, 12, 8, 10], 'x0': 30, 'scene': 'temp_sales'}, {'x': [31, 29, 27, 25, 23], 'y': [6, 7, 11, 17, 12], 'x0': 30, 'scene': 'temp_sales'}, {'x': [30, 27, 24, 21, 18], 'y': [12, 18, 19, 9, 15], 'x0': 19, 'scene': 'temp_sales'}, {'x': [30, 28, 26, 24, 22], 'y': [17, 6, 19, 14, 17], 'x0': 28, 'scene': 'temp_sales'}, {'x': [35, 34, 33, 32], 'y': [19, 12, 13, 11], 'x0': 34, 'scene': 'temp_sales'}, {'x': [30, 28, 26, 24, 22], 'y': [8, 17, 17, 17, 6], 'x0': 23, 'scene': 'temp_sales'}, {'x': [36, 34, 32, 30], 'y': [6, 12, 18, 20], 'x0': 32, 'scene': 'temp_sales'}, {'x': [31, 30, 29, 28, 27], 'y': [8, 20, 6, 20, 7], 'x0': 29, 'scene': 'temp_sales'}, {'x': [32, 30, 28, 26, 24], 'y': [18, 14, 13, 18, 20], 'x0': 29, 'scene': 'temp_sales'}, {'x': [33, 31, 29, 27], 'y': [7, 17, 13, 7], 'x0': 29, 'scene': 'temp_sales'}, {'x': [31, 29, 27, 25, 23], 'y': [12, 20, 6, 14, 10], 'x0': 30, 'scene': 'temp_sales'}, {'x': [31, 29, 27, 25, 23], 'y': [8, 17, 18, 6, 6], 'x0': 30, 'scene': 'temp_sales'}, {'x': [32, 31, 30, 29, 28], 'y': [6, 7, 13, 17, 14], 'x0': 30, 'scene': 'temp_sales'}, {'x': [32, 30, 28, 26], 'y': [10, 14, 14, 6], 'x0': 31, 'scene': 'temp_sales'}, {'x': [32, 29, 26, 23, 20], 'y': [10, 15, 13, 18, 10], 'x0': 29, 'scene': 'temp_sales'}, {'x': [35, 33, 31, 29], 'y': [6, 10, 15, 9], 'x0': 30, 'scene': 'temp_sales'}, {'x': [34, 31, 28, 25, 22, 19], 'y': [18, 10, 18, 6, 17, 12], 'x0': 29, 'scene': 'temp_sales'}, {'x': [33, 31, 29, 27], 'y': [18, 9, 10, 13], 'x0': 28, 'scene': 'temp_sales'}, {'x': [34, 31, 28, 25, 22], 'y': [20, 12, 20, 20, 19], 'x0': 25, 'scene': 'temp_sales'}, {'x': [33, 31, 29, 27, 25, 23], 'y': [17, 13, 16, 14, 10, 8], 'x0': 32, 'scene': 'temp_sales'}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['regression_from_table'], 'domain_operation': 'regression_from_table', 'problem_type_id': 'regression_from_table', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'x': [33, 31, 29, 27], 'y': [14, 12, 8, 10], 'x0': 30, 'scene': 'temp_sales'}, {'x': [31, 29, 27, 25, 23], 'y': [6, 7, 11, 17, 12], 'x0': 30, 'scene': 'temp_sales'}, {'x': [30, 27, 24, 21, 18], 'y': [12, 18, 19, 9, 15], 'x0': 19, 'scene': 'temp_sales'}, {'x': [30, 28, 26, 24, 22], 'y': [17, 6, 19, 14, 17], 'x0': 28, 'scene': 'temp_sales'}, {'x': [35, 34, 33, 32], 'y': [19, 12, 13, 11], 'x0': 34, 'scene': 'temp_sales'}, {'x': [30, 28, 26, 24, 22], 'y': [8, 17, 17, 17, 6], 'x0': 23, 'scene': 'temp_sales'}, {'x': [36, 34, 32, 30], 'y': [6, 12, 18, 20], 'x0': 32, 'scene': 'temp_sales'}, {'x': [31, 30, 29, 28, 27], 'y': [8, 20, 6, 20, 7], 'x0': 29, 'scene': 'temp_sales'}, {'x': [32, 30, 28, 26, 24], 'y': [18, 14, 13, 18, 20], 'x0': 29, 'scene': 'temp_sales'}, {'x': [33, 31, 29, 27], 'y': [7, 17, 13, 7], 'x0': 29, 'scene': 'temp_sales'}, {'x': [31, 29, 27, 25, 23], 'y': [12, 20, 6, 14, 10], 'x0': 30, 'scene': 'temp_sales'}, {'x': [31, 29, 27, 25, 23], 'y': [8, 17, 18, 6, 6], 'x0': 30, 'scene': 'temp_sales'}, {'x': [32, 31, 30, 29, 28], 'y': [6, 7, 13, 17, 14], 'x0': 30, 'scene': 'temp_sales'}, {'x': [32, 30, 28, 26], 'y': [10, 14, 14, 6], 'x0': 31, 'scene': 'temp_sales'}, {'x': [32, 29, 26, 23, 20], 'y': [10, 15, 13, 18, 10], 'x0': 29, 'scene': 'temp_sales'}, {'x': [35, 33, 31, 29], 'y': [6, 10, 15, 9], 'x0': 30, 'scene': 'temp_sales'}, {'x': [34, 31, 28, 25, 22, 19], 'y': [18, 10, 18, 6, 17, 12], 'x0': 29, 'scene': 'temp_sales'}, {'x': [33, 31, 29, 27], 'y': [18, 9, 10, 13], 'x0': 28, 'scene': 'temp_sales'}, {'x': [34, 31, 28, 25, 22], 'y': [20, 12, 20, 20, 19], 'x0': 25, 'scene': 'temp_sales'}, {'x': [33, 31, 29, 27, 25, 23], 'y': [17, 13, 16, 14, 10, 8], 'x0': 32, 'scene': 'temp_sales'}]}}, 'problem_type_id': 'regression_from_table', 'required_capabilities': ['regression_from_table'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'x': [33, 31, 29, 27], 'y': [14, 12, 8, 10], 'x0': 30, 'scene': 'temp_sales'}, {'x': [31, 29, 27, 25, 23], 'y': [6, 7, 11, 17, 12], 'x0': 30, 'scene': 'temp_sales'}, {'x': [30, 27, 24, 21, 18], 'y': [12, 18, 19, 9, 15], 'x0': 19, 'scene': 'temp_sales'}, {'x': [30, 28, 26, 24, 22], 'y': [17, 6, 19, 14, 17], 'x0': 28, 'scene': 'temp_sales'}, {'x': [35, 34, 33, 32], 'y': [19, 12, 13, 11], 'x0': 34, 'scene': 'temp_sales'}, {'x': [30, 28, 26, 24, 22], 'y': [8, 17, 17, 17, 6], 'x0': 23, 'scene': 'temp_sales'}, {'x': [36, 34, 32, 30], 'y': [6, 12, 18, 20], 'x0': 32, 'scene': 'temp_sales'}, {'x': [31, 30, 29, 28, 27], 'y': [8, 20, 6, 20, 7], 'x0': 29, 'scene': 'temp_sales'}, {'x': [32, 30, 28, 26, 24], 'y': [18, 14, 13, 18, 20], 'x0': 29, 'scene': 'temp_sales'}, {'x': [33, 31, 29, 27], 'y': [7, 17, 13, 7], 'x0': 29, 'scene': 'temp_sales'}, {'x': [31, 29, 27, 25, 23], 'y': [12, 20, 6, 14, 10], 'x0': 30, 'scene': 'temp_sales'}, {'x': [31, 29, 27, 25, 23], 'y': [8, 17, 18, 6, 6], 'x0': 30, 'scene': 'temp_sales'}, {'x': [32, 31, 30, 29, 28], 'y': [6, 7, 13, 17, 14], 'x0': 30, 'scene': 'temp_sales'}, {'x': [32, 30, 28, 26], 'y': [10, 14, 14, 6], 'x0': 31, 'scene': 'temp_sales'}, {'x': [32, 29, 26, 23, 20], 'y': [10, 15, 13, 18, 10], 'x0': 29, 'scene': 'temp_sales'}, {'x': [35, 33, 31, 29], 'y': [6, 10, 15, 9], 'x0': 30, 'scene': 'temp_sales'}, {'x': [34, 31, 28, 25, 22, 19], 'y': [18, 10, 18, 6, 17, 12], 'x0': 29, 'scene': 'temp_sales'}, {'x': [33, 31, 29, 27], 'y': [18, 9, 10, 13], 'x0': 28, 'scene': 'temp_sales'}, {'x': [34, 31, 28, 25, 22], 'y': [20, 12, 20, 20, 19], 'x0': 25, 'scene': 'temp_sales'}, {'x': [33, 31, 29, 27, 25, 23], 'y': [17, 13, 16, 14, 10, 8], 'x0': 32, 'scene': 'temp_sales'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_LeastSquaresMethodAndRegressionLine', 'fixed_domain_key': 'statistics.bivariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['regression_from_table'], 'matched_capabilities': ['regression_from_table'], 'selected_operation': 'regression_from_table', 'registry_revision': 'promoted-f99c60060e70', 'domain_module': 'core.domain.promoted.bivariate_statistics.bivariate_statistics_domain', 'entrypoint': 'build_bivariate_statistics_matrix', 'allowed_operations': ['correlation_from_regression_point', 'regression_from_summary', 'regression_from_table', 'regression_line_unknown_intercept', 'regression_rounded_from_table', 'regression_statement_selection', 'true_false_bivariate'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_LeastSquaresMethodAndRegressionLine'}), seed)
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
