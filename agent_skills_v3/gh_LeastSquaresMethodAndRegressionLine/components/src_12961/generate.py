from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "equation"
PROBLEM_TYPE_ID = "regression_from_summary"
TEXTBOOK_EXAMPLE_ID = 12961
DEFAULT_COMPONENT_ID = "src_12961" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_LeastSquaresMethodAndRegressionLine"
FIXED_DOMAIN_KEY = "statistics.bivariate_descriptive"
DOMAIN_OPERATION = "regression_from_summary"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['regression_from_summary'], 'domain_operation': 'regression_from_summary', 'problem_type_id': 'regression_from_summary', 'presentation_mode': 'short_answer', 'answer_type': 'equation', 'generation_constraints': {'variants': [{'mx': 6, 'my': 9, 'sx': 3, 'sy': 5, 'r': '-0.8'}, {'mx': 10, 'my': 16, 'sx': 2, 'sy': 2, 'r': '0.3'}, {'mx': 9, 'my': 17, 'sx': 8, 'sy': 10, 'r': '0.8'}, {'mx': 7, 'my': 20, 'sx': 5, 'sy': 8, 'r': '0.3'}, {'mx': 3, 'my': 20, 'sx': 4, 'sy': 2, 'r': '0.9'}, {'mx': 7, 'my': 10, 'sx': 8, 'sy': 10, 'r': '-0.6'}, {'mx': 1, 'my': 7, 'sx': 2, 'sy': 3, 'r': '-0.2'}, {'mx': 7, 'my': 19, 'sx': 6, 'sy': 5, 'r': '-0.9'}, {'mx': 1, 'my': 8, 'sx': 5, 'sy': 6, 'r': '-0.2'}, {'mx': 2, 'my': 14, 'sx': 8, 'sy': 10, 'r': '0.2'}, {'mx': 3, 'my': 14, 'sx': 2, 'sy': 3, 'r': '-0.1'}, {'mx': 2, 'my': 16, 'sx': 4, 'sy': 8, 'r': '0.6'}, {'mx': 6, 'my': 3, 'sx': 4, 'sy': 5, 'r': '0.4'}, {'mx': 3, 'my': 13, 'sx': 5, 'sy': 5, 'r': '0.7'}, {'mx': 1, 'my': 12, 'sx': 8, 'sy': 5, 'r': '0.6'}, {'mx': 6, 'my': 17, 'sx': 3, 'sy': 10, 'r': '-0.5'}, {'mx': 6, 'my': 14, 'sx': 2, 'sy': 2, 'r': '0.3'}, {'mx': 1, 'my': 11, 'sx': 4, 'sy': 4, 'r': '-0.6'}, {'mx': 5, 'my': 18, 'sx': 4, 'sy': 4, 'r': '0.7'}, {'mx': 6, 'my': 7, 'sx': 5, 'sy': 4, 'r': '-0.8'}]}}, 'phase1_classification': {'fixed_domain_key': 'statistics.bivariate_descriptive', 'required_capabilities': ['regression_from_summary'], 'domain_operation': 'regression_from_summary', 'problem_type_id': 'regression_from_summary', 'presentation_mode': 'short_answer', 'answer_type': 'equation', 'generation_constraints': {'variants': [{'mx': 6, 'my': 9, 'sx': 3, 'sy': 5, 'r': '-0.8'}, {'mx': 10, 'my': 16, 'sx': 2, 'sy': 2, 'r': '0.3'}, {'mx': 9, 'my': 17, 'sx': 8, 'sy': 10, 'r': '0.8'}, {'mx': 7, 'my': 20, 'sx': 5, 'sy': 8, 'r': '0.3'}, {'mx': 3, 'my': 20, 'sx': 4, 'sy': 2, 'r': '0.9'}, {'mx': 7, 'my': 10, 'sx': 8, 'sy': 10, 'r': '-0.6'}, {'mx': 1, 'my': 7, 'sx': 2, 'sy': 3, 'r': '-0.2'}, {'mx': 7, 'my': 19, 'sx': 6, 'sy': 5, 'r': '-0.9'}, {'mx': 1, 'my': 8, 'sx': 5, 'sy': 6, 'r': '-0.2'}, {'mx': 2, 'my': 14, 'sx': 8, 'sy': 10, 'r': '0.2'}, {'mx': 3, 'my': 14, 'sx': 2, 'sy': 3, 'r': '-0.1'}, {'mx': 2, 'my': 16, 'sx': 4, 'sy': 8, 'r': '0.6'}, {'mx': 6, 'my': 3, 'sx': 4, 'sy': 5, 'r': '0.4'}, {'mx': 3, 'my': 13, 'sx': 5, 'sy': 5, 'r': '0.7'}, {'mx': 1, 'my': 12, 'sx': 8, 'sy': 5, 'r': '0.6'}, {'mx': 6, 'my': 17, 'sx': 3, 'sy': 10, 'r': '-0.5'}, {'mx': 6, 'my': 14, 'sx': 2, 'sy': 2, 'r': '0.3'}, {'mx': 1, 'my': 11, 'sx': 4, 'sy': 4, 'r': '-0.6'}, {'mx': 5, 'my': 18, 'sx': 4, 'sy': 4, 'r': '0.7'}, {'mx': 6, 'my': 7, 'sx': 5, 'sy': 4, 'r': '-0.8'}]}}, 'problem_type_id': 'regression_from_summary', 'required_capabilities': ['regression_from_summary'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'mx': 6, 'my': 9, 'sx': 3, 'sy': 5, 'r': '-0.8'}, {'mx': 10, 'my': 16, 'sx': 2, 'sy': 2, 'r': '0.3'}, {'mx': 9, 'my': 17, 'sx': 8, 'sy': 10, 'r': '0.8'}, {'mx': 7, 'my': 20, 'sx': 5, 'sy': 8, 'r': '0.3'}, {'mx': 3, 'my': 20, 'sx': 4, 'sy': 2, 'r': '0.9'}, {'mx': 7, 'my': 10, 'sx': 8, 'sy': 10, 'r': '-0.6'}, {'mx': 1, 'my': 7, 'sx': 2, 'sy': 3, 'r': '-0.2'}, {'mx': 7, 'my': 19, 'sx': 6, 'sy': 5, 'r': '-0.9'}, {'mx': 1, 'my': 8, 'sx': 5, 'sy': 6, 'r': '-0.2'}, {'mx': 2, 'my': 14, 'sx': 8, 'sy': 10, 'r': '0.2'}, {'mx': 3, 'my': 14, 'sx': 2, 'sy': 3, 'r': '-0.1'}, {'mx': 2, 'my': 16, 'sx': 4, 'sy': 8, 'r': '0.6'}, {'mx': 6, 'my': 3, 'sx': 4, 'sy': 5, 'r': '0.4'}, {'mx': 3, 'my': 13, 'sx': 5, 'sy': 5, 'r': '0.7'}, {'mx': 1, 'my': 12, 'sx': 8, 'sy': 5, 'r': '0.6'}, {'mx': 6, 'my': 17, 'sx': 3, 'sy': 10, 'r': '-0.5'}, {'mx': 6, 'my': 14, 'sx': 2, 'sy': 2, 'r': '0.3'}, {'mx': 1, 'my': 11, 'sx': 4, 'sy': 4, 'r': '-0.6'}, {'mx': 5, 'my': 18, 'sx': 4, 'sy': 4, 'r': '0.7'}, {'mx': 6, 'my': 7, 'sx': 5, 'sy': 4, 'r': '-0.8'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_LeastSquaresMethodAndRegressionLine', 'fixed_domain_key': 'statistics.bivariate_descriptive', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['regression_from_summary'], 'matched_capabilities': ['regression_from_summary'], 'selected_operation': 'regression_from_summary', 'registry_revision': 'promoted-f99c60060e70', 'domain_module': 'core.domain.promoted.bivariate_statistics.bivariate_statistics_domain', 'entrypoint': 'build_bivariate_statistics_matrix', 'allowed_operations': ['correlation_from_regression_point', 'regression_from_summary', 'regression_from_table', 'regression_line_unknown_intercept', 'regression_rounded_from_table', 'regression_statement_selection', 'true_false_bivariate'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_LeastSquaresMethodAndRegressionLine'}), seed)
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
