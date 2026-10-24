from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "evaluate_function_statements"
TEXTBOOK_EXAMPLE_ID = 12601
DEFAULT_COMPONENT_ID = "src_12601" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_QuadraticFunctions"
FIXED_DOMAIN_KEY = "function.linear_quadratic"
DOMAIN_OPERATION = "evaluate_function_statements"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'function.linear_quadratic', 'required_capabilities': ['evaluate_function_statements'], 'domain_operation': 'evaluate_function_statements', 'problem_type_id': 'evaluate_function_statements', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 1, 'k': 5, 'lo': 2, 'hi': 4, 'claim_x': 2}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 3, 'k': 2, 'lo': 5, 'hi': 8, 'claim_x': 5}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': -1, 'k': 6, 'lo': 1, 'hi': 3, 'claim_x': 1}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 0, 'k': 4, 'lo': -2, 'hi': 0, 'claim_x': -2}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 2, 'h': 0, 'k': 2, 'lo': 0, 'hi': 2, 'claim_x': 2}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 1, 'k': 5, 'lo': 0, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 2, 'k': 2, 'lo': 2, 'hi': 4, 'claim_x': 2}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 2, 'k': 3, 'lo': 2, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 2, 'h': 2, 'k': 2, 'lo': 0, 'hi': 1, 'claim_x': 0}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 2, 'k': 1, 'lo': 3, 'hi': 5, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 3, 'k': -2, 'lo': 3, 'hi': 6, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 1, 'k': -1, 'lo': 0, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 1, 'k': 3, 'lo': 0, 'hi': 1, 'claim_x': 1}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 2, 'h': 0, 'k': -2, 'lo': 0, 'hi': 1, 'claim_x': 0}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 3, 'k': -1, 'lo': 2, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 3, 'k': -1, 'lo': 4, 'hi': 5, 'claim_x': 4}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 1, 'k': -3, 'lo': 3, 'hi': 6, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 1, 'h': -1, 'k': 2, 'lo': -1, 'hi': 1, 'claim_x': 1}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 2, 'h': 3, 'k': -3, 'lo': 5, 'hi': 7, 'claim_x': 7}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 3, 'k': 3, 'lo': 2, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}]}}, 'phase1_classification': {'fixed_domain_key': 'function.linear_quadratic', 'required_capabilities': ['evaluate_function_statements'], 'domain_operation': 'evaluate_function_statements', 'problem_type_id': 'evaluate_function_statements', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 1, 'k': 5, 'lo': 2, 'hi': 4, 'claim_x': 2}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 3, 'k': 2, 'lo': 5, 'hi': 8, 'claim_x': 5}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': -1, 'k': 6, 'lo': 1, 'hi': 3, 'claim_x': 1}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 0, 'k': 4, 'lo': -2, 'hi': 0, 'claim_x': -2}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 2, 'h': 0, 'k': 2, 'lo': 0, 'hi': 2, 'claim_x': 2}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 1, 'k': 5, 'lo': 0, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 2, 'k': 2, 'lo': 2, 'hi': 4, 'claim_x': 2}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 2, 'k': 3, 'lo': 2, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 2, 'h': 2, 'k': 2, 'lo': 0, 'hi': 1, 'claim_x': 0}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 2, 'k': 1, 'lo': 3, 'hi': 5, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 3, 'k': -2, 'lo': 3, 'hi': 6, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 1, 'k': -1, 'lo': 0, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 1, 'k': 3, 'lo': 0, 'hi': 1, 'claim_x': 1}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 2, 'h': 0, 'k': -2, 'lo': 0, 'hi': 1, 'claim_x': 0}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 3, 'k': -1, 'lo': 2, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 3, 'k': -1, 'lo': 4, 'hi': 5, 'claim_x': 4}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 1, 'k': -3, 'lo': 3, 'hi': 6, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 1, 'h': -1, 'k': 2, 'lo': -1, 'hi': 1, 'claim_x': 1}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 2, 'h': 3, 'k': -3, 'lo': 5, 'hi': 7, 'claim_x': 7}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 3, 'k': 3, 'lo': 2, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}]}}, 'problem_type_id': 'evaluate_function_statements', 'required_capabilities': ['evaluate_function_statements'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 1, 'k': 5, 'lo': 2, 'hi': 4, 'claim_x': 2}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 3, 'k': 2, 'lo': 5, 'hi': 8, 'claim_x': 5}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': -1, 'k': 6, 'lo': 1, 'hi': 3, 'claim_x': 1}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 0, 'k': 4, 'lo': -2, 'hi': 0, 'claim_x': -2}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 2, 'h': 0, 'k': 2, 'lo': 0, 'hi': 2, 'claim_x': 2}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 1, 'k': 5, 'lo': 0, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 2, 'k': 2, 'lo': 2, 'hi': 4, 'claim_x': 2}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 2, 'k': 3, 'lo': 2, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 2, 'h': 2, 'k': 2, 'lo': 0, 'hi': 1, 'claim_x': 0}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 2, 'k': 1, 'lo': 3, 'hi': 5, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 3, 'k': -2, 'lo': 3, 'hi': 6, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 1, 'k': -1, 'lo': 0, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 1, 'k': 3, 'lo': 0, 'hi': 1, 'claim_x': 1}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 2, 'h': 0, 'k': -2, 'lo': 0, 'hi': 1, 'claim_x': 0}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 3, 'k': -1, 'lo': 2, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 3, 'k': -1, 'lo': 4, 'hi': 5, 'claim_x': 4}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -2, 'h': 1, 'k': -3, 'lo': 3, 'hi': 6, 'claim_x': 3}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 1, 'h': -1, 'k': 2, 'lo': -1, 'hi': 1, 'claim_x': 1}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': 2, 'h': 3, 'k': -3, 'lo': 5, 'hi': 7, 'claim_x': 7}], 'mode': 'truth'}, {'subject': {'type': 'generic'}, 'statements': [{'kind': 'interval_max_claim', 'a': -1, 'h': 3, 'k': 3, 'lo': 2, 'hi': 3, 'claim_x': 3}], 'mode': 'truth'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_QuadraticFunctions', 'fixed_domain_key': 'function.linear_quadratic', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['evaluate_function_statements'], 'matched_capabilities': ['evaluate_function_statements'], 'selected_operation': 'evaluate_function_statements', 'registry_revision': 'promoted-3752585c4f0b', 'domain_module': 'core.domain.promoted.function_linear_quadratic.function_models_domain', 'entrypoint': 'build_function_models_matrix', 'allowed_operations': ['complete_square_items', 'evaluate_function_statements', 'quadratic_always_sign', 'quadratic_extrema', 'quadratic_graph_transformations', 'quadratic_vertex_axis', 'solve_quadratic_applications'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_QuadraticFunctions'}), seed)
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
