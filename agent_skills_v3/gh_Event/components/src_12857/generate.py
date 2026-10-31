from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "dice_event_sets"
TEXTBOOK_EXAMPLE_ID = 12857
DEFAULT_COMPONENT_ID = "src_12857" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Event"
FIXED_DOMAIN_KEY = "discrete.classical_probability"
DOMAIN_OPERATION = "dice_event_sets"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.classical_probability', 'required_capabilities': ['dice_event_sets'], 'domain_operation': 'dice_event_sets', 'problem_type_id': 'dice_event_sets', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'product_eq', 'n': 12}}, {'a': {'kind': 'sum_eq', 'n': 10}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'both_gt', 'n': 2}, 'b': {'kind': 'sum_gt', 'n': 9}}, {'a': {'kind': 'sum_eq', 'n': 5}, 'b': {'kind': 'product_eq', 'n': 6}}, {'a': {'kind': 'sum_eq', 'n': 10}, 'b': {'kind': 'product_eq', 'n': 24}}, {'a': {'kind': 'sum_gt', 'n': 10}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_eq', 'n': 8}, 'b': {'kind': 'product_eq', 'n': 12}}, {'a': {'kind': 'both_gt', 'n': 3}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_gt', 'n': 9}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_gt', 'n': 8}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_gt', 'n': 6}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'product_eq', 'n': 6}}, {'a': {'kind': 'sum_eq', 'n': 4}, 'b': {'kind': 'product_eq', 'n': 4}}, {'a': {'kind': 'diff_eq', 'n': 1}, 'b': {'kind': 'sum_eq', 'n': 7}}, {'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'product_eq', 'n': 10}}, {'a': {'kind': 'sum_eq', 'n': 6}, 'b': {'kind': 'product_eq', 'n': 5}}, {'a': {'kind': 'sum_eq', 'n': 8}, 'b': {'kind': 'product_eq', 'n': 15}}, {'a': {'kind': 'sum_eq', 'n': 9}, 'b': {'kind': 'product_eq', 'n': 18}}, {'a': {'kind': 'exactly_one_face', 'face': 6}, 'b': {'kind': 'sum_eq', 'n': 9}}, {'a': {'kind': 'first_even'}, 'b': {'kind': 'faces_equal'}}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.classical_probability', 'required_capabilities': ['dice_event_sets'], 'domain_operation': 'dice_event_sets', 'problem_type_id': 'dice_event_sets', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'product_eq', 'n': 12}}, {'a': {'kind': 'sum_eq', 'n': 10}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'both_gt', 'n': 2}, 'b': {'kind': 'sum_gt', 'n': 9}}, {'a': {'kind': 'sum_eq', 'n': 5}, 'b': {'kind': 'product_eq', 'n': 6}}, {'a': {'kind': 'sum_eq', 'n': 10}, 'b': {'kind': 'product_eq', 'n': 24}}, {'a': {'kind': 'sum_gt', 'n': 10}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_eq', 'n': 8}, 'b': {'kind': 'product_eq', 'n': 12}}, {'a': {'kind': 'both_gt', 'n': 3}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_gt', 'n': 9}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_gt', 'n': 8}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_gt', 'n': 6}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'product_eq', 'n': 6}}, {'a': {'kind': 'sum_eq', 'n': 4}, 'b': {'kind': 'product_eq', 'n': 4}}, {'a': {'kind': 'diff_eq', 'n': 1}, 'b': {'kind': 'sum_eq', 'n': 7}}, {'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'product_eq', 'n': 10}}, {'a': {'kind': 'sum_eq', 'n': 6}, 'b': {'kind': 'product_eq', 'n': 5}}, {'a': {'kind': 'sum_eq', 'n': 8}, 'b': {'kind': 'product_eq', 'n': 15}}, {'a': {'kind': 'sum_eq', 'n': 9}, 'b': {'kind': 'product_eq', 'n': 18}}, {'a': {'kind': 'exactly_one_face', 'face': 6}, 'b': {'kind': 'sum_eq', 'n': 9}}, {'a': {'kind': 'first_even'}, 'b': {'kind': 'faces_equal'}}]}}, 'problem_type_id': 'dice_event_sets', 'required_capabilities': ['dice_event_sets'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'product_eq', 'n': 12}}, {'a': {'kind': 'sum_eq', 'n': 10}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'both_gt', 'n': 2}, 'b': {'kind': 'sum_gt', 'n': 9}}, {'a': {'kind': 'sum_eq', 'n': 5}, 'b': {'kind': 'product_eq', 'n': 6}}, {'a': {'kind': 'sum_eq', 'n': 10}, 'b': {'kind': 'product_eq', 'n': 24}}, {'a': {'kind': 'sum_gt', 'n': 10}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_eq', 'n': 8}, 'b': {'kind': 'product_eq', 'n': 12}}, {'a': {'kind': 'both_gt', 'n': 3}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_gt', 'n': 9}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_gt', 'n': 8}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_gt', 'n': 6}, 'b': {'kind': 'faces_equal'}}, {'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'product_eq', 'n': 6}}, {'a': {'kind': 'sum_eq', 'n': 4}, 'b': {'kind': 'product_eq', 'n': 4}}, {'a': {'kind': 'diff_eq', 'n': 1}, 'b': {'kind': 'sum_eq', 'n': 7}}, {'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'product_eq', 'n': 10}}, {'a': {'kind': 'sum_eq', 'n': 6}, 'b': {'kind': 'product_eq', 'n': 5}}, {'a': {'kind': 'sum_eq', 'n': 8}, 'b': {'kind': 'product_eq', 'n': 15}}, {'a': {'kind': 'sum_eq', 'n': 9}, 'b': {'kind': 'product_eq', 'n': 18}}, {'a': {'kind': 'exactly_one_face', 'face': 6}, 'b': {'kind': 'sum_eq', 'n': 9}}, {'a': {'kind': 'first_even'}, 'b': {'kind': 'faces_equal'}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Event', 'fixed_domain_key': 'discrete.classical_probability', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['dice_event_sets'], 'matched_capabilities': ['dice_event_sets'], 'selected_operation': 'dice_event_sets', 'registry_revision': 'promoted-118ac6ac1753', 'domain_module': 'core.domain.promoted.classical_probability.classical_probability_domain', 'entrypoint': 'build_classical_probability_matrix', 'allowed_operations': ['dice_event_sets', 'event_relation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Event'}), seed)
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
