from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "cubic_from_conditions"
TEXTBOOK_EXAMPLE_ID = 12614
DEFAULT_COMPONENT_ID = "src_12614" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_GraphsOfCubicFunctions"
FIXED_DOMAIN_KEY = "function.cubic_graph"
DOMAIN_OPERATION = "cubic_from_conditions"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'function.cubic_graph', 'required_capabilities': ['cubic_from_conditions'], 'domain_operation': 'cubic_from_conditions', 'problem_type_id': 'cubic_from_conditions', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 25], 'B': [7, 7], 'C_x': 9}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -6], 'B': [3, -6], 'C_x': 7}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 38], 'B': [4, 28], 'C_x': 7}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 21], 'B': [3, 39], 'C_x': 4}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 3], 'B': [3, -15], 'C_x': 6}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [3, 84], 'B': [7, 56], 'C_x': 13}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 28], 'B': [4, 8], 'C_x': 5}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 8], 'B': [4, -8], 'C_x': 8}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 224], 'B': [8, 416], 'C_x': 11}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 28], 'B': [5, 20], 'C_x': 9}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -3], 'B': [3, 3], 'C_x': 4}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [3, 90], 'B': [5, 70], 'C_x': 9}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -59], 'B': [9, -171], 'C_x': 11}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [3, 24], 'B': [5, 0], 'C_x': 11}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -25], 'B': [5, -65], 'C_x': 7}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [3, 252], 'B': [7, 308], 'C_x': 13}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -46], 'B': [9, -54], 'C_x': 11}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 42], 'B': [4, 36], 'C_x': 9}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 23], 'B': [5, 55], 'C_x': 8}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -4], 'B': [3, 0], 'C_x': 5}]}]}}, 'phase1_classification': {'fixed_domain_key': 'function.cubic_graph', 'required_capabilities': ['cubic_from_conditions'], 'domain_operation': 'cubic_from_conditions', 'problem_type_id': 'cubic_from_conditions', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 25], 'B': [7, 7], 'C_x': 9}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -6], 'B': [3, -6], 'C_x': 7}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 38], 'B': [4, 28], 'C_x': 7}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 21], 'B': [3, 39], 'C_x': 4}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 3], 'B': [3, -15], 'C_x': 6}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [3, 84], 'B': [7, 56], 'C_x': 13}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 28], 'B': [4, 8], 'C_x': 5}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 8], 'B': [4, -8], 'C_x': 8}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 224], 'B': [8, 416], 'C_x': 11}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 28], 'B': [5, 20], 'C_x': 9}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -3], 'B': [3, 3], 'C_x': 4}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [3, 90], 'B': [5, 70], 'C_x': 9}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -59], 'B': [9, -171], 'C_x': 11}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [3, 24], 'B': [5, 0], 'C_x': 11}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -25], 'B': [5, -65], 'C_x': 7}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [3, 252], 'B': [7, 308], 'C_x': 13}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -46], 'B': [9, -54], 'C_x': 11}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 42], 'B': [4, 36], 'C_x': 9}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 23], 'B': [5, 55], 'C_x': 8}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -4], 'B': [3, 0], 'C_x': 5}]}]}}, 'problem_type_id': 'cubic_from_conditions', 'required_capabilities': ['cubic_from_conditions'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 25], 'B': [7, 7], 'C_x': 9}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -6], 'B': [3, -6], 'C_x': 7}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 38], 'B': [4, 28], 'C_x': 7}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 21], 'B': [3, 39], 'C_x': 4}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 3], 'B': [3, -15], 'C_x': 6}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [3, 84], 'B': [7, 56], 'C_x': 13}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 28], 'B': [4, 8], 'C_x': 5}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 8], 'B': [4, -8], 'C_x': 8}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 224], 'B': [8, 416], 'C_x': 11}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 28], 'B': [5, 20], 'C_x': 9}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -3], 'B': [3, 3], 'C_x': 4}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [3, 90], 'B': [5, 70], 'C_x': 9}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -59], 'B': [9, -171], 'C_x': 11}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [3, 24], 'B': [5, 0], 'C_x': 11}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -25], 'B': [5, -65], 'C_x': 7}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [3, 252], 'B': [7, 308], 'C_x': 13}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -46], 'B': [9, -54], 'C_x': 11}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [2, 42], 'B': [4, 36], 'C_x': 9}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, 23], 'B': [5, 55], 'C_x': 8}]}, {'items': [{'kind': 'symmetric_pair_origin', 'A': [1, -4], 'B': [3, 0], 'C_x': 5}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_GraphsOfCubicFunctions', 'fixed_domain_key': 'function.cubic_graph', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['cubic_from_conditions'], 'matched_capabilities': ['cubic_from_conditions'], 'selected_operation': 'cubic_from_conditions', 'registry_revision': 'promoted-870e318c51b6', 'domain_module': 'core.domain.promoted.function_cubic.cubic_domain', 'entrypoint': 'build_cubic_graph_matrix', 'allowed_operations': ['cubic_center_form', 'cubic_curve_matching', 'cubic_from_conditions', 'cubic_statements'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_GraphsOfCubicFunctions'}), seed)
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
