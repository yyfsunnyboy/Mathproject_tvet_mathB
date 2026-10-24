from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "graph_cubic_functions"
TEXTBOOK_EXAMPLE_ID = 12613
DEFAULT_COMPONENT_ID = "src_12613" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_GraphsOfCubicFunctions"
FIXED_DOMAIN_KEY = "function.cubic_graph"
DOMAIN_OPERATION = "graph_cubic_functions"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'function.cubic_graph', 'required_capabilities': ['graph_cubic_functions'], 'domain_operation': 'graph_cubic_functions', 'problem_type_id': 'graph_cubic_functions', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'coeffs': [-1, 3, -2, -2]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, 6, -9, 4]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, 3, 2, -4]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, -9, 27, -29]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -6, -9, -1]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -9, -28, -28]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -3, -6, -3]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, 3, 3, 4]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -9, -25, -18]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, -9, 25, -24]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [2, 12, 26, 18]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, -6, 12, -9]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, 3, -4, -1]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-2, 18, -52, 45]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, 3, 4, 4]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, 6, -11, 3]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [2, -12, 27, -18]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, 9, 28, 33]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -9, -30, -35]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, 9, -27, 31]}], 'ask': ['form', 'center']}]}}, 'phase1_classification': {'fixed_domain_key': 'function.cubic_graph', 'required_capabilities': ['graph_cubic_functions'], 'domain_operation': 'graph_cubic_functions', 'problem_type_id': 'graph_cubic_functions', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'items': [{'coeffs': [-1, 3, -2, -2]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, 6, -9, 4]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, 3, 2, -4]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, -9, 27, -29]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -6, -9, -1]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -9, -28, -28]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -3, -6, -3]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, 3, 3, 4]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -9, -25, -18]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, -9, 25, -24]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [2, 12, 26, 18]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, -6, 12, -9]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, 3, -4, -1]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-2, 18, -52, 45]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, 3, 4, 4]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, 6, -11, 3]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [2, -12, 27, -18]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, 9, 28, 33]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -9, -30, -35]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, 9, -27, 31]}], 'ask': ['form', 'center']}]}}, 'problem_type_id': 'graph_cubic_functions', 'required_capabilities': ['graph_cubic_functions'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'items': [{'coeffs': [-1, 3, -2, -2]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, 6, -9, 4]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, 3, 2, -4]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, -9, 27, -29]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -6, -9, -1]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -9, -28, -28]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -3, -6, -3]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, 3, 3, 4]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -9, -25, -18]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, -9, 25, -24]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [2, 12, 26, 18]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, -6, 12, -9]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, 3, -4, -1]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-2, 18, -52, 45]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, 3, 4, 4]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, 6, -11, 3]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [2, -12, 27, -18]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [1, 9, 28, 33]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, -9, -30, -35]}], 'ask': ['form', 'center']}, {'items': [{'coeffs': [-1, 9, -27, 31]}], 'ask': ['form', 'center']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_GraphsOfCubicFunctions', 'fixed_domain_key': 'function.cubic_graph', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['graph_cubic_functions'], 'matched_capabilities': ['graph_cubic_functions'], 'selected_operation': 'graph_cubic_functions', 'registry_revision': 'promoted-2851416d9782', 'domain_module': 'core.domain.promoted.function_cubic.cubic_domain', 'entrypoint': 'build_cubic_graph_matrix', 'allowed_operations': ['cubic_center_form', 'cubic_curve_matching', 'cubic_from_conditions', 'cubic_option_graph', 'cubic_statements', 'graph_cubic_functions'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_GraphsOfCubicFunctions'}), seed)
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
