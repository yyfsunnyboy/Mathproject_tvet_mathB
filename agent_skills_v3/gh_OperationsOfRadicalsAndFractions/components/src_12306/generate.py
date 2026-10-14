from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "evaluate_integer_fraction_part_expression"
TEXTBOOK_EXAMPLE_ID = 12306
DEFAULT_COMPONENT_ID = "src_12306" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_OperationsOfRadicalsAndFractions"
FIXED_DOMAIN_KEY = "algebra.radical_operations"
DOMAIN_OPERATION = "evaluate_integer_fraction_part_expression"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.radical_operations', 'required_capabilities': ['radical_operations'], 'domain_operation': 'evaluate_integer_fraction_part_expression', 'problem_type_id': 'evaluate_integer_fraction_part_expression', 'presentation_mode': 'short_answer', 'answer_type': 'expression', 'generation_constraints': {'variants': [{'root': {'rational': 3, 'radical': [2, 2]}, 'sign': -1}, {'root': {'rational': 22, 'radical': [2, 21]}, 'sign': -1}, {'root': {'rational': 40, 'radical': [2, 39]}, 'sign': -1}, {'root': {'rational': 7, 'radical': [2, 6]}, 'sign': -1}, {'root': {'rational': 16, 'radical': [2, 15]}, 'sign': -1}, {'root': {'rational': 39, 'radical': [2, 38]}, 'sign': -1}, {'root': {'rational': 18, 'radical': [2, 17]}, 'sign': -1}, {'root': {'rational': 4, 'radical': [2, 3]}, 'sign': -1}, {'root': {'rational': 12, 'radical': [2, 11]}, 'sign': -1}, {'root': {'rational': 24, 'radical': [2, 23]}, 'sign': -1}, {'root': {'rational': 38, 'radical': [2, 37]}, 'sign': -1}, {'root': {'rational': 36, 'radical': [2, 35]}, 'sign': -1}, {'root': {'rational': 14, 'radical': [2, 13]}, 'sign': -1}, {'root': {'rational': 32, 'radical': [2, 31]}, 'sign': -1}, {'root': {'rational': 11, 'radical': [2, 10]}, 'sign': -1}, {'root': {'rational': 20, 'radical': [2, 19]}, 'sign': -1}, {'root': {'rational': 34, 'radical': [2, 33]}, 'sign': -1}, {'root': {'rational': 8, 'radical': [2, 7]}, 'sign': -1}, {'root': {'rational': 6, 'radical': [2, 5]}, 'sign': -1}, {'root': {'rational': 15, 'radical': [2, 14]}, 'sign': -1}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.radical_operations', 'required_capabilities': ['radical_operations'], 'domain_operation': 'evaluate_integer_fraction_part_expression', 'problem_type_id': 'evaluate_integer_fraction_part_expression', 'presentation_mode': 'short_answer', 'answer_type': 'expression', 'generation_constraints': {'variants': [{'root': {'rational': 3, 'radical': [2, 2]}, 'sign': -1}, {'root': {'rational': 22, 'radical': [2, 21]}, 'sign': -1}, {'root': {'rational': 40, 'radical': [2, 39]}, 'sign': -1}, {'root': {'rational': 7, 'radical': [2, 6]}, 'sign': -1}, {'root': {'rational': 16, 'radical': [2, 15]}, 'sign': -1}, {'root': {'rational': 39, 'radical': [2, 38]}, 'sign': -1}, {'root': {'rational': 18, 'radical': [2, 17]}, 'sign': -1}, {'root': {'rational': 4, 'radical': [2, 3]}, 'sign': -1}, {'root': {'rational': 12, 'radical': [2, 11]}, 'sign': -1}, {'root': {'rational': 24, 'radical': [2, 23]}, 'sign': -1}, {'root': {'rational': 38, 'radical': [2, 37]}, 'sign': -1}, {'root': {'rational': 36, 'radical': [2, 35]}, 'sign': -1}, {'root': {'rational': 14, 'radical': [2, 13]}, 'sign': -1}, {'root': {'rational': 32, 'radical': [2, 31]}, 'sign': -1}, {'root': {'rational': 11, 'radical': [2, 10]}, 'sign': -1}, {'root': {'rational': 20, 'radical': [2, 19]}, 'sign': -1}, {'root': {'rational': 34, 'radical': [2, 33]}, 'sign': -1}, {'root': {'rational': 8, 'radical': [2, 7]}, 'sign': -1}, {'root': {'rational': 6, 'radical': [2, 5]}, 'sign': -1}, {'root': {'rational': 15, 'radical': [2, 14]}, 'sign': -1}]}}, 'problem_type_id': 'evaluate_integer_fraction_part_expression', 'required_capabilities': ['radical_operations'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'root': {'rational': 3, 'radical': [2, 2]}, 'sign': -1}, {'root': {'rational': 22, 'radical': [2, 21]}, 'sign': -1}, {'root': {'rational': 40, 'radical': [2, 39]}, 'sign': -1}, {'root': {'rational': 7, 'radical': [2, 6]}, 'sign': -1}, {'root': {'rational': 16, 'radical': [2, 15]}, 'sign': -1}, {'root': {'rational': 39, 'radical': [2, 38]}, 'sign': -1}, {'root': {'rational': 18, 'radical': [2, 17]}, 'sign': -1}, {'root': {'rational': 4, 'radical': [2, 3]}, 'sign': -1}, {'root': {'rational': 12, 'radical': [2, 11]}, 'sign': -1}, {'root': {'rational': 24, 'radical': [2, 23]}, 'sign': -1}, {'root': {'rational': 38, 'radical': [2, 37]}, 'sign': -1}, {'root': {'rational': 36, 'radical': [2, 35]}, 'sign': -1}, {'root': {'rational': 14, 'radical': [2, 13]}, 'sign': -1}, {'root': {'rational': 32, 'radical': [2, 31]}, 'sign': -1}, {'root': {'rational': 11, 'radical': [2, 10]}, 'sign': -1}, {'root': {'rational': 20, 'radical': [2, 19]}, 'sign': -1}, {'root': {'rational': 34, 'radical': [2, 33]}, 'sign': -1}, {'root': {'rational': 8, 'radical': [2, 7]}, 'sign': -1}, {'root': {'rational': 6, 'radical': [2, 5]}, 'sign': -1}, {'root': {'rational': 15, 'radical': [2, 14]}, 'sign': -1}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_OperationsOfRadicalsAndFractions', 'fixed_domain_key': 'algebra.radical_operations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': [], 'matched_capabilities': [], 'selected_operation': 'evaluate_integer_fraction_part_expression', 'registry_revision': 'promoted-285211635de3', 'domain_module': 'core.domain.promoted.algebra_radical_operations.radical_operations_domain', 'entrypoint': 'build_radical_operations_matrix', 'allowed_operations': ['simplify_radical_fraction_expressions', 'denest_square_roots', 'evaluate_integer_fraction_part_expression', 'order_radical_numbers', 'evaluate_time_dilation_relations', 'optimize_by_am_gm', 'nearest_integer_from_radical_relation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_OperationsOfRadicalsAndFractions'}), seed)
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
