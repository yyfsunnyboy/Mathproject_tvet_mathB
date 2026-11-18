from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "correlation_from_regression_point"
TEXTBOOK_EXAMPLE_ID = 12965
DEFAULT_COMPONENT_ID = "src_12965" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_LeastSquaresMethodAndRegressionLine"
FIXED_DOMAIN_KEY = "statistics.bivariate_descriptive"
DOMAIN_OPERATION = "correlation_from_regression_point"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['correlation_from_regression_point'], 'domain_operation': 'correlation_from_regression_point', 'problem_type_id': 'correlation_from_regression_point', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'mx': 3, 'my': 2, 'sx': 5, 'sy': 8, 'point': [6, 4]}, {'mx': 4, 'my': 15, 'sx': 2, 'sy': 10, 'point': [1, 14]}, {'mx': 8, 'my': 3, 'sx': 8, 'sy': 10, 'point': [10, 2]}, {'mx': 4, 'my': 11, 'sx': 3, 'sy': 6, 'point': [8, 5]}, {'mx': 1, 'my': 5, 'sx': 5, 'sy': 10, 'point': [5, 10]}, {'mx': 10, 'my': 1, 'sx': 4, 'sy': 8, 'point': [11, 0]}, {'mx': 3, 'my': 7, 'sx': 2, 'sy': 9, 'point': [2, 3]}, {'mx': 8, 'my': 1, 'sx': 5, 'sy': 9, 'point': [12, 4]}, {'mx': 4, 'my': 11, 'sx': 3, 'sy': 9, 'point': [5, 9]}, {'mx': 1, 'my': 8, 'sx': 2, 'sy': 10, 'point': [5, 12]}, {'mx': 8, 'my': 8, 'sx': 3, 'sy': 10, 'point': [5, 7]}, {'mx': 10, 'my': 11, 'sx': 2, 'sy': 6, 'point': [13, 4]}, {'mx': 10, 'my': 13, 'sx': 8, 'sy': 10, 'point': [13, 14]}, {'mx': 3, 'my': 6, 'sx': 3, 'sy': 10, 'point': [5, 2]}, {'mx': 9, 'my': 11, 'sx': 5, 'sy': 3, 'point': [6, 10]}, {'mx': 10, 'my': 8, 'sx': 2, 'sy': 5, 'point': [7, 14]}, {'mx': 9, 'my': 4, 'sx': 3, 'sy': 4, 'point': [13, 3]}, {'mx': 1, 'my': 10, 'sx': 2, 'sy': 4, 'point': [5, 5]}, {'mx': 5, 'my': 10, 'sx': 6, 'sy': 10, 'point': [8, 12]}, {'mx': 6, 'my': 3, 'sx': 2, 'sy': 10, 'point': [5, 6]}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['correlation_from_regression_point'], 'domain_operation': 'correlation_from_regression_point', 'problem_type_id': 'correlation_from_regression_point', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'mx': 3, 'my': 2, 'sx': 5, 'sy': 8, 'point': [6, 4]}, {'mx': 4, 'my': 15, 'sx': 2, 'sy': 10, 'point': [1, 14]}, {'mx': 8, 'my': 3, 'sx': 8, 'sy': 10, 'point': [10, 2]}, {'mx': 4, 'my': 11, 'sx': 3, 'sy': 6, 'point': [8, 5]}, {'mx': 1, 'my': 5, 'sx': 5, 'sy': 10, 'point': [5, 10]}, {'mx': 10, 'my': 1, 'sx': 4, 'sy': 8, 'point': [11, 0]}, {'mx': 3, 'my': 7, 'sx': 2, 'sy': 9, 'point': [2, 3]}, {'mx': 8, 'my': 1, 'sx': 5, 'sy': 9, 'point': [12, 4]}, {'mx': 4, 'my': 11, 'sx': 3, 'sy': 9, 'point': [5, 9]}, {'mx': 1, 'my': 8, 'sx': 2, 'sy': 10, 'point': [5, 12]}, {'mx': 8, 'my': 8, 'sx': 3, 'sy': 10, 'point': [5, 7]}, {'mx': 10, 'my': 11, 'sx': 2, 'sy': 6, 'point': [13, 4]}, {'mx': 10, 'my': 13, 'sx': 8, 'sy': 10, 'point': [13, 14]}, {'mx': 3, 'my': 6, 'sx': 3, 'sy': 10, 'point': [5, 2]}, {'mx': 9, 'my': 11, 'sx': 5, 'sy': 3, 'point': [6, 10]}, {'mx': 10, 'my': 8, 'sx': 2, 'sy': 5, 'point': [7, 14]}, {'mx': 9, 'my': 4, 'sx': 3, 'sy': 4, 'point': [13, 3]}, {'mx': 1, 'my': 10, 'sx': 2, 'sy': 4, 'point': [5, 5]}, {'mx': 5, 'my': 10, 'sx': 6, 'sy': 10, 'point': [8, 12]}, {'mx': 6, 'my': 3, 'sx': 2, 'sy': 10, 'point': [5, 6]}]}}, 'problem_type_id': 'correlation_from_regression_point', 'required_capabilities': ['correlation_from_regression_point'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'mx': 3, 'my': 2, 'sx': 5, 'sy': 8, 'point': [6, 4]}, {'mx': 4, 'my': 15, 'sx': 2, 'sy': 10, 'point': [1, 14]}, {'mx': 8, 'my': 3, 'sx': 8, 'sy': 10, 'point': [10, 2]}, {'mx': 4, 'my': 11, 'sx': 3, 'sy': 6, 'point': [8, 5]}, {'mx': 1, 'my': 5, 'sx': 5, 'sy': 10, 'point': [5, 10]}, {'mx': 10, 'my': 1, 'sx': 4, 'sy': 8, 'point': [11, 0]}, {'mx': 3, 'my': 7, 'sx': 2, 'sy': 9, 'point': [2, 3]}, {'mx': 8, 'my': 1, 'sx': 5, 'sy': 9, 'point': [12, 4]}, {'mx': 4, 'my': 11, 'sx': 3, 'sy': 9, 'point': [5, 9]}, {'mx': 1, 'my': 8, 'sx': 2, 'sy': 10, 'point': [5, 12]}, {'mx': 8, 'my': 8, 'sx': 3, 'sy': 10, 'point': [5, 7]}, {'mx': 10, 'my': 11, 'sx': 2, 'sy': 6, 'point': [13, 4]}, {'mx': 10, 'my': 13, 'sx': 8, 'sy': 10, 'point': [13, 14]}, {'mx': 3, 'my': 6, 'sx': 3, 'sy': 10, 'point': [5, 2]}, {'mx': 9, 'my': 11, 'sx': 5, 'sy': 3, 'point': [6, 10]}, {'mx': 10, 'my': 8, 'sx': 2, 'sy': 5, 'point': [7, 14]}, {'mx': 9, 'my': 4, 'sx': 3, 'sy': 4, 'point': [13, 3]}, {'mx': 1, 'my': 10, 'sx': 2, 'sy': 4, 'point': [5, 5]}, {'mx': 5, 'my': 10, 'sx': 6, 'sy': 10, 'point': [8, 12]}, {'mx': 6, 'my': 3, 'sx': 2, 'sy': 10, 'point': [5, 6]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_LeastSquaresMethodAndRegressionLine', 'fixed_domain_key': 'statistics.bivariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['correlation_from_regression_point'], 'matched_capabilities': ['correlation_from_regression_point'], 'selected_operation': 'correlation_from_regression_point', 'registry_revision': 'promoted-f99c60060e70', 'domain_module': 'core.domain.promoted.bivariate_statistics.bivariate_statistics_domain', 'entrypoint': 'build_bivariate_statistics_matrix', 'allowed_operations': ['correlation_from_regression_point', 'regression_from_summary', 'regression_from_table', 'regression_line_unknown_intercept', 'regression_rounded_from_table', 'regression_statement_selection', 'true_false_bivariate'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_LeastSquaresMethodAndRegressionLine'}), seed)
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
