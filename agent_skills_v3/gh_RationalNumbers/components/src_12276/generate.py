from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "decimal_to_simplest_fraction"
TEXTBOOK_EXAMPLE_ID = 12276
DEFAULT_COMPONENT_ID = "src_12276" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RationalNumbers"
FIXED_DOMAIN_KEY = "number_system.rational_numbers"
DOMAIN_OPERATION = "decimal_to_simplest_fraction"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'number_system.rational_numbers', 'required_capabilities': ['rational_numbers'], 'domain_operation': 'decimal_to_simplest_fraction', 'problem_type_id': 'decimal_to_simplest_fraction', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'decimals': ['0.732', '5.(12)', '0.1(58)']}, {'decimals': ['0.391', '9.(40)', '0.0(85)']}, {'decimals': ['0.144', '9.(23)', '0.8(86)']}, {'decimals': ['0.323', '9.(26)', '0.4(40)']}, {'decimals': ['0.024', '9.(53)', '0.8(25)']}, {'decimals': ['0.997', '8.(82)', '0.9(48)']}, {'decimals': ['0.151', '4.(92)', '0.2(06)']}, {'decimals': ['0.368', '5.(01)', '0.8(34)']}, {'decimals': ['0.673', '3.(57)', '0.2(46)']}, {'decimals': ['0.981', '3.(12)', '0.1(64)']}, {'decimals': ['0.535', '3.(92)', '0.7(30)']}, {'decimals': ['0.449', '5.(67)', '0.9(36)']}, {'decimals': ['0.356', '9.(79)', '0.2(03)']}, {'decimals': ['0.621', '1.(10)', '0.2(59)']}, {'decimals': ['0.144', '5.(86)', '0.8(20)']}, {'decimals': ['0.797', '2.(49)', '0.3(15)']}, {'decimals': ['0.824', '5.(69)', '0.0(95)']}, {'decimals': ['0.002', '5.(83)', '0.5(83)']}, {'decimals': ['0.716', '6.(39)', '0.8(29)']}, {'decimals': ['0.163', '2.(87)', '0.6(25)']}]}}, 'phase1_classification': {'fixed_domain_key': 'number_system.rational_numbers', 'required_capabilities': ['rational_numbers'], 'domain_operation': 'decimal_to_simplest_fraction', 'problem_type_id': 'decimal_to_simplest_fraction', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'decimals': ['0.732', '5.(12)', '0.1(58)']}, {'decimals': ['0.391', '9.(40)', '0.0(85)']}, {'decimals': ['0.144', '9.(23)', '0.8(86)']}, {'decimals': ['0.323', '9.(26)', '0.4(40)']}, {'decimals': ['0.024', '9.(53)', '0.8(25)']}, {'decimals': ['0.997', '8.(82)', '0.9(48)']}, {'decimals': ['0.151', '4.(92)', '0.2(06)']}, {'decimals': ['0.368', '5.(01)', '0.8(34)']}, {'decimals': ['0.673', '3.(57)', '0.2(46)']}, {'decimals': ['0.981', '3.(12)', '0.1(64)']}, {'decimals': ['0.535', '3.(92)', '0.7(30)']}, {'decimals': ['0.449', '5.(67)', '0.9(36)']}, {'decimals': ['0.356', '9.(79)', '0.2(03)']}, {'decimals': ['0.621', '1.(10)', '0.2(59)']}, {'decimals': ['0.144', '5.(86)', '0.8(20)']}, {'decimals': ['0.797', '2.(49)', '0.3(15)']}, {'decimals': ['0.824', '5.(69)', '0.0(95)']}, {'decimals': ['0.002', '5.(83)', '0.5(83)']}, {'decimals': ['0.716', '6.(39)', '0.8(29)']}, {'decimals': ['0.163', '2.(87)', '0.6(25)']}]}}, 'problem_type_id': 'decimal_to_simplest_fraction', 'required_capabilities': ['rational_numbers'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'decimals': ['0.732', '5.(12)', '0.1(58)']}, {'decimals': ['0.391', '9.(40)', '0.0(85)']}, {'decimals': ['0.144', '9.(23)', '0.8(86)']}, {'decimals': ['0.323', '9.(26)', '0.4(40)']}, {'decimals': ['0.024', '9.(53)', '0.8(25)']}, {'decimals': ['0.997', '8.(82)', '0.9(48)']}, {'decimals': ['0.151', '4.(92)', '0.2(06)']}, {'decimals': ['0.368', '5.(01)', '0.8(34)']}, {'decimals': ['0.673', '3.(57)', '0.2(46)']}, {'decimals': ['0.981', '3.(12)', '0.1(64)']}, {'decimals': ['0.535', '3.(92)', '0.7(30)']}, {'decimals': ['0.449', '5.(67)', '0.9(36)']}, {'decimals': ['0.356', '9.(79)', '0.2(03)']}, {'decimals': ['0.621', '1.(10)', '0.2(59)']}, {'decimals': ['0.144', '5.(86)', '0.8(20)']}, {'decimals': ['0.797', '2.(49)', '0.3(15)']}, {'decimals': ['0.824', '5.(69)', '0.0(95)']}, {'decimals': ['0.002', '5.(83)', '0.5(83)']}, {'decimals': ['0.716', '6.(39)', '0.8(29)']}, {'decimals': ['0.163', '2.(87)', '0.6(25)']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_RationalNumbers', 'fixed_domain_key': 'number_system.rational_numbers', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': [], 'matched_capabilities': [], 'selected_operation': 'decimal_to_simplest_fraction', 'registry_revision': 'promoted-80c3e5401b9c', 'domain_module': 'core.domain.promoted.number_system_rational_numbers.rational_numbers_domain', 'entrypoint': 'build_rational_numbers_matrix', 'allowed_operations': ['plot_rational_points_on_number_line', 'evaluate_rationality_statements', 'identify_rational_numbers', 'fraction_to_decimal_expansion', 'decimal_to_simplest_fraction', 'construct_rational_between_bounds'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_RationalNumbers'}), seed)
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
