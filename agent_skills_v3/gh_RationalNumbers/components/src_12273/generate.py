from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "fraction_to_decimal_expansion"
TEXTBOOK_EXAMPLE_ID = 12273
DEFAULT_COMPONENT_ID = "src_12273" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RationalNumbers"
FIXED_DOMAIN_KEY = "number_system.rational_numbers"
DOMAIN_OPERATION = "fraction_to_decimal_expansion"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'number_system.rational_numbers', 'required_capabilities': ['rational_numbers'], 'domain_operation': 'fraction_to_decimal_expansion', 'problem_type_id': 'fraction_to_decimal_expansion', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'fractions': ['11/40', '2/11']}, {'fractions': ['23/50', '2/15']}, {'fractions': ['7/25', '7/11']}, {'fractions': ['3/8', '1/6']}, {'fractions': ['11/25', '2/3']}, {'fractions': ['24/25', '25/44']}, {'fractions': ['7/8', '7/27']}, {'fractions': ['1/40', '15/22']}, {'fractions': ['1/20', '4/33']}, {'fractions': ['6/25', '19/22']}, {'fractions': ['12/25', '1/11']}, {'fractions': ['6/25', '19/44']}, {'fractions': ['33/40', '9/11']}, {'fractions': ['9/20', '1/15']}, {'fractions': ['9/20', '29/37']}, {'fractions': ['24/25', '9/44']}, {'fractions': ['21/40', '1/3']}, {'fractions': ['16/25', '5/22']}, {'fractions': ['41/50', '26/27']}, {'fractions': ['4/25', '15/22']}]}}, 'phase1_classification': {'fixed_domain_key': 'number_system.rational_numbers', 'required_capabilities': ['rational_numbers'], 'domain_operation': 'fraction_to_decimal_expansion', 'problem_type_id': 'fraction_to_decimal_expansion', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'fractions': ['11/40', '2/11']}, {'fractions': ['23/50', '2/15']}, {'fractions': ['7/25', '7/11']}, {'fractions': ['3/8', '1/6']}, {'fractions': ['11/25', '2/3']}, {'fractions': ['24/25', '25/44']}, {'fractions': ['7/8', '7/27']}, {'fractions': ['1/40', '15/22']}, {'fractions': ['1/20', '4/33']}, {'fractions': ['6/25', '19/22']}, {'fractions': ['12/25', '1/11']}, {'fractions': ['6/25', '19/44']}, {'fractions': ['33/40', '9/11']}, {'fractions': ['9/20', '1/15']}, {'fractions': ['9/20', '29/37']}, {'fractions': ['24/25', '9/44']}, {'fractions': ['21/40', '1/3']}, {'fractions': ['16/25', '5/22']}, {'fractions': ['41/50', '26/27']}, {'fractions': ['4/25', '15/22']}]}}, 'problem_type_id': 'fraction_to_decimal_expansion', 'required_capabilities': ['rational_numbers'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'fractions': ['11/40', '2/11']}, {'fractions': ['23/50', '2/15']}, {'fractions': ['7/25', '7/11']}, {'fractions': ['3/8', '1/6']}, {'fractions': ['11/25', '2/3']}, {'fractions': ['24/25', '25/44']}, {'fractions': ['7/8', '7/27']}, {'fractions': ['1/40', '15/22']}, {'fractions': ['1/20', '4/33']}, {'fractions': ['6/25', '19/22']}, {'fractions': ['12/25', '1/11']}, {'fractions': ['6/25', '19/44']}, {'fractions': ['33/40', '9/11']}, {'fractions': ['9/20', '1/15']}, {'fractions': ['9/20', '29/37']}, {'fractions': ['24/25', '9/44']}, {'fractions': ['21/40', '1/3']}, {'fractions': ['16/25', '5/22']}, {'fractions': ['41/50', '26/27']}, {'fractions': ['4/25', '15/22']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_RationalNumbers', 'fixed_domain_key': 'number_system.rational_numbers', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': [], 'matched_capabilities': [], 'selected_operation': 'fraction_to_decimal_expansion', 'registry_revision': 'promoted-4a5f2cab5b55', 'domain_module': 'core.domain.promoted.number_system_rational_numbers.rational_numbers_domain', 'entrypoint': 'build_rational_numbers_matrix', 'allowed_operations': ['plot_rational_points_on_number_line', 'evaluate_rationality_statements', 'identify_rational_numbers', 'fraction_to_decimal_expansion'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_RationalNumbers'}), seed)
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
