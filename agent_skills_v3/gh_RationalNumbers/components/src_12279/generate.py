from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "evaluate_rationality_statements"
TEXTBOOK_EXAMPLE_ID = 12279
DEFAULT_COMPONENT_ID = "src_12279" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RationalNumbers"
FIXED_DOMAIN_KEY = "number_system.rational_numbers"
DOMAIN_OPERATION = "evaluate_rationality_statements"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'number_system.rational_numbers', 'required_capabilities': ['rational_numbers'], 'domain_operation': 'evaluate_rationality_statements', 'problem_type_id': 'evaluate_rationality_statements', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'finite_decimal', 'value': '1.414'}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(2)'}, {'kind': 'repeating_decimal', 'value': '0.(3)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '8/7', 'upper': '17/14'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 2}, {'kind': 'sqrt', 'radicand': 8}, {'kind': 'sqrt', 'radicand': 18}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 2, 'right_radicand': 3}]}, {'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'sqrt', 'radicand': 5}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(4)'}, {'kind': 'repeating_decimal', 'value': '0.(5)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '10/9', 'upper': '21/18'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 3}, {'kind': 'sqrt', 'radicand': 12}, {'kind': 'sqrt', 'radicand': 27}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 5, 'right_radicand': 7}]}, {'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'finite_decimal', 'value': '3.1416'}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(6)'}, {'kind': 'repeating_decimal', 'value': '0.(7)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '12/11', 'upper': '25/22'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 6}, {'kind': 'sqrt', 'radicand': 24}, {'kind': 'sqrt', 'radicand': 54}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 6, 'right_radicand': 10}]}, {'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'sqrt', 'radicand': 11}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(1)'}, {'kind': 'repeating_decimal', 'value': '0.(8)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '14/13', 'upper': '29/26'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 7}, {'kind': 'sqrt', 'radicand': 28}, {'kind': 'sqrt', 'radicand': 63}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 7, 'right_radicand': 15}]}, {'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'finite_decimal', 'value': '2.236'}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(3)'}, {'kind': 'repeating_decimal', 'value': '0.(6)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '16/15', 'upper': '33/30'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 10}, {'kind': 'sqrt', 'radicand': 40}, {'kind': 'sqrt', 'radicand': 90}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 10, 'right_radicand': 13}]}]}}, 'phase1_classification': {'fixed_domain_key': 'number_system.rational_numbers', 'required_capabilities': ['rational_numbers'], 'domain_operation': 'evaluate_rationality_statements', 'problem_type_id': 'evaluate_rationality_statements', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'finite_decimal', 'value': '1.414'}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(2)'}, {'kind': 'repeating_decimal', 'value': '0.(3)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '8/7', 'upper': '17/14'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 2}, {'kind': 'sqrt', 'radicand': 8}, {'kind': 'sqrt', 'radicand': 18}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 2, 'right_radicand': 3}]}, {'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'sqrt', 'radicand': 5}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(4)'}, {'kind': 'repeating_decimal', 'value': '0.(5)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '10/9', 'upper': '21/18'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 3}, {'kind': 'sqrt', 'radicand': 12}, {'kind': 'sqrt', 'radicand': 27}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 5, 'right_radicand': 7}]}, {'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'finite_decimal', 'value': '3.1416'}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(6)'}, {'kind': 'repeating_decimal', 'value': '0.(7)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '12/11', 'upper': '25/22'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 6}, {'kind': 'sqrt', 'radicand': 24}, {'kind': 'sqrt', 'radicand': 54}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 6, 'right_radicand': 10}]}, {'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'sqrt', 'radicand': 11}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(1)'}, {'kind': 'repeating_decimal', 'value': '0.(8)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '14/13', 'upper': '29/26'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 7}, {'kind': 'sqrt', 'radicand': 28}, {'kind': 'sqrt', 'radicand': 63}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 7, 'right_radicand': 15}]}, {'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'finite_decimal', 'value': '2.236'}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(3)'}, {'kind': 'repeating_decimal', 'value': '0.(6)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '16/15', 'upper': '33/30'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 10}, {'kind': 'sqrt', 'radicand': 40}, {'kind': 'sqrt', 'radicand': 90}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 10, 'right_radicand': 13}]}]}}, 'problem_type_id': 'evaluate_rationality_statements', 'required_capabilities': ['rational_numbers'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'finite_decimal', 'value': '1.414'}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(2)'}, {'kind': 'repeating_decimal', 'value': '0.(3)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '8/7', 'upper': '17/14'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 2}, {'kind': 'sqrt', 'radicand': 8}, {'kind': 'sqrt', 'radicand': 18}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 2, 'right_radicand': 3}]}, {'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'sqrt', 'radicand': 5}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(4)'}, {'kind': 'repeating_decimal', 'value': '0.(5)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '10/9', 'upper': '21/18'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 3}, {'kind': 'sqrt', 'radicand': 12}, {'kind': 'sqrt', 'radicand': 27}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 5, 'right_radicand': 7}]}, {'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'finite_decimal', 'value': '3.1416'}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(6)'}, {'kind': 'repeating_decimal', 'value': '0.(7)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '12/11', 'upper': '25/22'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 6}, {'kind': 'sqrt', 'radicand': 24}, {'kind': 'sqrt', 'radicand': 54}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 6, 'right_radicand': 10}]}, {'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'sqrt', 'radicand': 11}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(1)'}, {'kind': 'repeating_decimal', 'value': '0.(8)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '14/13', 'upper': '29/26'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 7}, {'kind': 'sqrt', 'radicand': 28}, {'kind': 'sqrt', 'radicand': 63}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 7, 'right_radicand': 15}]}, {'statements': [{'predicate': 'is_irrational', 'value': {'kind': 'finite_decimal', 'value': '2.236'}}, {'predicate': 'equals', 'left': {'kind': 'sum', 'terms': [{'kind': 'repeating_decimal', 'value': '0.(3)'}, {'kind': 'repeating_decimal', 'value': '0.(6)'}]}, 'right': {'kind': 'rational', 'value': '1/1'}}, {'predicate': 'no_rational_between', 'lower': '16/15', 'upper': '33/30'}, {'predicate': 'all_irrational', 'values': [{'kind': 'sqrt', 'radicand': 10}, {'kind': 'sqrt', 'radicand': 40}, {'kind': 'sqrt', 'radicand': 90}]}, {'predicate': 'sqrt_difference_identity', 'left_radicand': 10, 'right_radicand': 13}]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_RationalNumbers', 'fixed_domain_key': 'number_system.rational_numbers', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': [], 'matched_capabilities': [], 'selected_operation': 'evaluate_rationality_statements', 'registry_revision': 'promoted-9e9699385420', 'domain_module': 'core.domain.promoted.number_system_rational_numbers.rational_numbers_domain', 'entrypoint': 'build_rational_numbers_matrix', 'allowed_operations': ['plot_rational_points_on_number_line', 'evaluate_rationality_statements', 'identify_rational_numbers'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_RationalNumbers'}), seed)
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
