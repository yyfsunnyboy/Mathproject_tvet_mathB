from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "event_relation"
TEXTBOOK_EXAMPLE_ID = 12859
DEFAULT_COMPONENT_ID = "src_12859" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Event"
FIXED_DOMAIN_KEY = "discrete.classical_probability"
DOMAIN_OPERATION = "event_relation"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.classical_probability', 'required_capabilities': ['event_relation'], 'domain_operation': 'event_relation', 'problem_type_id': 'event_relation', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'model': 'dice', 'a': {'kind': 'first_even'}, 'b': {'kind': 'sum_odd'}}, {'model': 'dice', 'a': {'kind': 'first_even'}, 'b': {'kind': 'first_odd'}}, {'model': 'dice', 'a': {'kind': 'both_gt', 'n': 4}, 'b': {'kind': 'sum_eq', 'n': 6}}, {'model': 'dice', 'a': {'kind': 'exactly_one_face', 'face': 1}, 'b': {'kind': 'both_gt', 'n': 3}}, {'model': 'dice', 'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'sum_gt', 'n': 9}}, {'model': 'dice', 'a': {'kind': 'first_even'}, 'b': {'kind': 'second_even'}}, {'model': 'dice', 'a': {'kind': 'first_odd'}, 'b': {'kind': 'sum_even'}}, {'model': 'dice', 'a': {'kind': 'faces_equal'}, 'b': {'kind': 'diff_eq', 'n': 1}}, {'model': 'dice', 'a': {'kind': 'sum_eq', 'n': 3}, 'b': {'kind': 'product_eq', 'n': 2}}, {'model': 'dice', 'a': {'kind': 'first_gt_second'}, 'b': {'kind': 'faces_equal'}}, {'model': 'dice', 'a': {'kind': 'diff_eq', 'n': 5}, 'b': {'kind': 'sum_eq', 'n': 7}}, {'model': 'dice', 'a': {'kind': 'both_gt', 'n': 3}, 'b': {'kind': 'diff_eq', 'n': 1}}, {'model': 'dice', 'a': {'kind': 'first_lt_second'}, 'b': {'kind': 'both_gt', 'n': 4}}, {'model': 'dice', 'a': {'kind': 'sum_gt', 'n': 10}, 'b': {'kind': 'faces_equal'}}, {'model': 'dice', 'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'sum_eq', 'n': 8}}, {'model': 'dice', 'a': {'kind': 'faces_equal'}, 'b': {'kind': 'diff_eq', 'n': 2}}, {'model': 'dice', 'a': {'kind': 'first_gt_second'}, 'b': {'kind': 'first_lt_second'}}, {'model': 'dice', 'a': {'kind': 'sum_eq', 'n': 12}, 'b': {'kind': 'sum_eq', 'n': 2}}, {'model': 'dice', 'a': {'kind': 'product_eq', 'n': 12}, 'b': {'kind': 'sum_eq', 'n': 2}}, {'model': 'dice', 'a': {'kind': 'sum_gt', 'n': 9}, 'b': {'kind': 'sum_eq', 'n': 12}}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.classical_probability', 'required_capabilities': ['event_relation'], 'domain_operation': 'event_relation', 'problem_type_id': 'event_relation', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'model': 'dice', 'a': {'kind': 'first_even'}, 'b': {'kind': 'sum_odd'}}, {'model': 'dice', 'a': {'kind': 'first_even'}, 'b': {'kind': 'first_odd'}}, {'model': 'dice', 'a': {'kind': 'both_gt', 'n': 4}, 'b': {'kind': 'sum_eq', 'n': 6}}, {'model': 'dice', 'a': {'kind': 'exactly_one_face', 'face': 1}, 'b': {'kind': 'both_gt', 'n': 3}}, {'model': 'dice', 'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'sum_gt', 'n': 9}}, {'model': 'dice', 'a': {'kind': 'first_even'}, 'b': {'kind': 'second_even'}}, {'model': 'dice', 'a': {'kind': 'first_odd'}, 'b': {'kind': 'sum_even'}}, {'model': 'dice', 'a': {'kind': 'faces_equal'}, 'b': {'kind': 'diff_eq', 'n': 1}}, {'model': 'dice', 'a': {'kind': 'sum_eq', 'n': 3}, 'b': {'kind': 'product_eq', 'n': 2}}, {'model': 'dice', 'a': {'kind': 'first_gt_second'}, 'b': {'kind': 'faces_equal'}}, {'model': 'dice', 'a': {'kind': 'diff_eq', 'n': 5}, 'b': {'kind': 'sum_eq', 'n': 7}}, {'model': 'dice', 'a': {'kind': 'both_gt', 'n': 3}, 'b': {'kind': 'diff_eq', 'n': 1}}, {'model': 'dice', 'a': {'kind': 'first_lt_second'}, 'b': {'kind': 'both_gt', 'n': 4}}, {'model': 'dice', 'a': {'kind': 'sum_gt', 'n': 10}, 'b': {'kind': 'faces_equal'}}, {'model': 'dice', 'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'sum_eq', 'n': 8}}, {'model': 'dice', 'a': {'kind': 'faces_equal'}, 'b': {'kind': 'diff_eq', 'n': 2}}, {'model': 'dice', 'a': {'kind': 'first_gt_second'}, 'b': {'kind': 'first_lt_second'}}, {'model': 'dice', 'a': {'kind': 'sum_eq', 'n': 12}, 'b': {'kind': 'sum_eq', 'n': 2}}, {'model': 'dice', 'a': {'kind': 'product_eq', 'n': 12}, 'b': {'kind': 'sum_eq', 'n': 2}}, {'model': 'dice', 'a': {'kind': 'sum_gt', 'n': 9}, 'b': {'kind': 'sum_eq', 'n': 12}}]}}, 'problem_type_id': 'event_relation', 'required_capabilities': ['event_relation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'model': 'dice', 'a': {'kind': 'first_even'}, 'b': {'kind': 'sum_odd'}}, {'model': 'dice', 'a': {'kind': 'first_even'}, 'b': {'kind': 'first_odd'}}, {'model': 'dice', 'a': {'kind': 'both_gt', 'n': 4}, 'b': {'kind': 'sum_eq', 'n': 6}}, {'model': 'dice', 'a': {'kind': 'exactly_one_face', 'face': 1}, 'b': {'kind': 'both_gt', 'n': 3}}, {'model': 'dice', 'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'sum_gt', 'n': 9}}, {'model': 'dice', 'a': {'kind': 'first_even'}, 'b': {'kind': 'second_even'}}, {'model': 'dice', 'a': {'kind': 'first_odd'}, 'b': {'kind': 'sum_even'}}, {'model': 'dice', 'a': {'kind': 'faces_equal'}, 'b': {'kind': 'diff_eq', 'n': 1}}, {'model': 'dice', 'a': {'kind': 'sum_eq', 'n': 3}, 'b': {'kind': 'product_eq', 'n': 2}}, {'model': 'dice', 'a': {'kind': 'first_gt_second'}, 'b': {'kind': 'faces_equal'}}, {'model': 'dice', 'a': {'kind': 'diff_eq', 'n': 5}, 'b': {'kind': 'sum_eq', 'n': 7}}, {'model': 'dice', 'a': {'kind': 'both_gt', 'n': 3}, 'b': {'kind': 'diff_eq', 'n': 1}}, {'model': 'dice', 'a': {'kind': 'first_lt_second'}, 'b': {'kind': 'both_gt', 'n': 4}}, {'model': 'dice', 'a': {'kind': 'sum_gt', 'n': 10}, 'b': {'kind': 'faces_equal'}}, {'model': 'dice', 'a': {'kind': 'sum_eq', 'n': 7}, 'b': {'kind': 'sum_eq', 'n': 8}}, {'model': 'dice', 'a': {'kind': 'faces_equal'}, 'b': {'kind': 'diff_eq', 'n': 2}}, {'model': 'dice', 'a': {'kind': 'first_gt_second'}, 'b': {'kind': 'first_lt_second'}}, {'model': 'dice', 'a': {'kind': 'sum_eq', 'n': 12}, 'b': {'kind': 'sum_eq', 'n': 2}}, {'model': 'dice', 'a': {'kind': 'product_eq', 'n': 12}, 'b': {'kind': 'sum_eq', 'n': 2}}, {'model': 'dice', 'a': {'kind': 'sum_gt', 'n': 9}, 'b': {'kind': 'sum_eq', 'n': 12}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Event', 'fixed_domain_key': 'discrete.classical_probability', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['event_relation'], 'matched_capabilities': ['event_relation'], 'selected_operation': 'event_relation', 'registry_revision': 'promoted-118ac6ac1753', 'domain_module': 'core.domain.promoted.classical_probability.classical_probability_domain', 'entrypoint': 'build_classical_probability_matrix', 'allowed_operations': ['dice_event_sets', 'event_relation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Event'}), seed)
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
