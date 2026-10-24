from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "solve_quadratic_applications"
TEXTBOOK_EXAMPLE_ID = 12585
DEFAULT_COMPONENT_ID = "src_12585" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_QuadraticFunctions"
FIXED_DOMAIN_KEY = "function.linear_quadratic"
DOMAIN_OPERATION = "solve_quadratic_applications"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'function.linear_quadratic', 'required_capabilities': ['solve_quadratic_applications'], 'domain_operation': 'solve_quadratic_applications', 'problem_type_id': 'solve_quadratic_applications', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'profit', 'cost': [200, 30], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 50}}]}, {'items': [{'kind': 'profit', 'cost': [116, 16], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 72}}]}, {'items': [{'kind': 'profit', 'cost': [235, 29], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 52}}]}, {'items': [{'kind': 'profit', 'cost': [286, 12], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 71}}]}, {'items': [{'kind': 'profit', 'cost': [128, 13], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 49}}]}, {'items': [{'kind': 'profit', 'cost': [239, 20], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 62}}]}, {'items': [{'kind': 'profit', 'cost': [100, 40], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 47}}]}, {'items': [{'kind': 'profit', 'cost': [203, 16], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 59}}]}, {'items': [{'kind': 'profit', 'cost': [208, 19], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 46}}]}, {'items': [{'kind': 'profit', 'cost': [223, 17], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 49}}]}, {'items': [{'kind': 'profit', 'cost': [225, 21], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 80}}]}, {'items': [{'kind': 'profit', 'cost': [272, 28], 'revenue': {'mode': 'given', 'a': '-1/4', 'b': 77}}]}, {'items': [{'kind': 'profit', 'cost': [251, 25], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 69}}]}, {'items': [{'kind': 'profit', 'cost': [276, 28], 'revenue': {'mode': 'given', 'a': '-1/4', 'b': 54}}]}, {'items': [{'kind': 'profit', 'cost': [215, 27], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 75}}]}, {'items': [{'kind': 'profit', 'cost': [100, 17], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 79}}]}, {'items': [{'kind': 'profit', 'cost': [158, 24], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 64}}]}, {'items': [{'kind': 'profit', 'cost': [203, 10], 'revenue': {'mode': 'given', 'a': '-1/4', 'b': 78}}]}, {'items': [{'kind': 'profit', 'cost': [247, 10], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 80}}]}, {'items': [{'kind': 'profit', 'cost': [103, 26], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 78}}]}]}}, 'phase1_classification': {'fixed_domain_key': 'function.linear_quadratic', 'required_capabilities': ['solve_quadratic_applications'], 'domain_operation': 'solve_quadratic_applications', 'problem_type_id': 'solve_quadratic_applications', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'profit', 'cost': [200, 30], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 50}}]}, {'items': [{'kind': 'profit', 'cost': [116, 16], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 72}}]}, {'items': [{'kind': 'profit', 'cost': [235, 29], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 52}}]}, {'items': [{'kind': 'profit', 'cost': [286, 12], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 71}}]}, {'items': [{'kind': 'profit', 'cost': [128, 13], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 49}}]}, {'items': [{'kind': 'profit', 'cost': [239, 20], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 62}}]}, {'items': [{'kind': 'profit', 'cost': [100, 40], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 47}}]}, {'items': [{'kind': 'profit', 'cost': [203, 16], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 59}}]}, {'items': [{'kind': 'profit', 'cost': [208, 19], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 46}}]}, {'items': [{'kind': 'profit', 'cost': [223, 17], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 49}}]}, {'items': [{'kind': 'profit', 'cost': [225, 21], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 80}}]}, {'items': [{'kind': 'profit', 'cost': [272, 28], 'revenue': {'mode': 'given', 'a': '-1/4', 'b': 77}}]}, {'items': [{'kind': 'profit', 'cost': [251, 25], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 69}}]}, {'items': [{'kind': 'profit', 'cost': [276, 28], 'revenue': {'mode': 'given', 'a': '-1/4', 'b': 54}}]}, {'items': [{'kind': 'profit', 'cost': [215, 27], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 75}}]}, {'items': [{'kind': 'profit', 'cost': [100, 17], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 79}}]}, {'items': [{'kind': 'profit', 'cost': [158, 24], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 64}}]}, {'items': [{'kind': 'profit', 'cost': [203, 10], 'revenue': {'mode': 'given', 'a': '-1/4', 'b': 78}}]}, {'items': [{'kind': 'profit', 'cost': [247, 10], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 80}}]}, {'items': [{'kind': 'profit', 'cost': [103, 26], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 78}}]}]}}, 'problem_type_id': 'solve_quadratic_applications', 'required_capabilities': ['solve_quadratic_applications'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'kind': 'profit', 'cost': [200, 30], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 50}}]}, {'items': [{'kind': 'profit', 'cost': [116, 16], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 72}}]}, {'items': [{'kind': 'profit', 'cost': [235, 29], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 52}}]}, {'items': [{'kind': 'profit', 'cost': [286, 12], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 71}}]}, {'items': [{'kind': 'profit', 'cost': [128, 13], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 49}}]}, {'items': [{'kind': 'profit', 'cost': [239, 20], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 62}}]}, {'items': [{'kind': 'profit', 'cost': [100, 40], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 47}}]}, {'items': [{'kind': 'profit', 'cost': [203, 16], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 59}}]}, {'items': [{'kind': 'profit', 'cost': [208, 19], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 46}}]}, {'items': [{'kind': 'profit', 'cost': [223, 17], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 49}}]}, {'items': [{'kind': 'profit', 'cost': [225, 21], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 80}}]}, {'items': [{'kind': 'profit', 'cost': [272, 28], 'revenue': {'mode': 'given', 'a': '-1/4', 'b': 77}}]}, {'items': [{'kind': 'profit', 'cost': [251, 25], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 69}}]}, {'items': [{'kind': 'profit', 'cost': [276, 28], 'revenue': {'mode': 'given', 'a': '-1/4', 'b': 54}}]}, {'items': [{'kind': 'profit', 'cost': [215, 27], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 75}}]}, {'items': [{'kind': 'profit', 'cost': [100, 17], 'revenue': {'mode': 'given', 'a': '-1/2', 'b': 79}}]}, {'items': [{'kind': 'profit', 'cost': [158, 24], 'revenue': {'mode': 'given', 'a': '-1/10', 'b': 64}}]}, {'items': [{'kind': 'profit', 'cost': [203, 10], 'revenue': {'mode': 'given', 'a': '-1/4', 'b': 78}}]}, {'items': [{'kind': 'profit', 'cost': [247, 10], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 80}}]}, {'items': [{'kind': 'profit', 'cost': [103, 26], 'revenue': {'mode': 'given', 'a': '-1/5', 'b': 78}}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_QuadraticFunctions', 'fixed_domain_key': 'function.linear_quadratic', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_quadratic_applications'], 'matched_capabilities': ['solve_quadratic_applications'], 'selected_operation': 'solve_quadratic_applications', 'registry_revision': 'promoted-3752585c4f0b', 'domain_module': 'core.domain.promoted.function_linear_quadratic.function_models_domain', 'entrypoint': 'build_function_models_matrix', 'allowed_operations': ['complete_square_items', 'evaluate_function_statements', 'quadratic_always_sign', 'quadratic_extrema', 'quadratic_graph_transformations', 'quadratic_vertex_axis', 'solve_quadratic_applications'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_QuadraticFunctions'}), seed)
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
