from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "fraction_to_decimal_expansion"
TEXTBOOK_EXAMPLE_ID = 12281
DEFAULT_COMPONENT_ID = "src_12281" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'number_system.rational_numbers', 'required_capabilities': ['rational_numbers'], 'domain_operation': 'fraction_to_decimal_expansion', 'problem_type_id': 'fraction_to_decimal_expansion', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'fractions': ['1/37', '9/22']}, {'fractions': ['61/99', '4/15']}, {'fractions': ['38/41', '3/44']}, {'fractions': ['13/33', '7/12']}, {'fractions': ['9/11', '9/22']}, {'fractions': ['2/3', '14/55']}, {'fractions': ['5/11', '3/22']}, {'fractions': ['1/9', '11/18']}, {'fractions': ['8/37', '7/12']}, {'fractions': ['9/37', '7/12']}, {'fractions': ['21/41', '1/24']}, {'fractions': ['2/3', '1/24']}, {'fractions': ['1/33', '17/24']}, {'fractions': ['7/11', '9/22']}, {'fractions': ['24/41', '9/74']}, {'fractions': ['13/27', '7/22']}, {'fractions': ['10/13', '21/22']}, {'fractions': ['4/7', '2/15']}, {'fractions': ['5/7', '15/22']}, {'fractions': ['3/11', '17/24']}]}}, 'phase1_classification': {'fixed_domain_key': 'number_system.rational_numbers', 'required_capabilities': ['rational_numbers'], 'domain_operation': 'fraction_to_decimal_expansion', 'problem_type_id': 'fraction_to_decimal_expansion', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'fractions': ['1/37', '9/22']}, {'fractions': ['61/99', '4/15']}, {'fractions': ['38/41', '3/44']}, {'fractions': ['13/33', '7/12']}, {'fractions': ['9/11', '9/22']}, {'fractions': ['2/3', '14/55']}, {'fractions': ['5/11', '3/22']}, {'fractions': ['1/9', '11/18']}, {'fractions': ['8/37', '7/12']}, {'fractions': ['9/37', '7/12']}, {'fractions': ['21/41', '1/24']}, {'fractions': ['2/3', '1/24']}, {'fractions': ['1/33', '17/24']}, {'fractions': ['7/11', '9/22']}, {'fractions': ['24/41', '9/74']}, {'fractions': ['13/27', '7/22']}, {'fractions': ['10/13', '21/22']}, {'fractions': ['4/7', '2/15']}, {'fractions': ['5/7', '15/22']}, {'fractions': ['3/11', '17/24']}]}}, 'problem_type_id': 'fraction_to_decimal_expansion', 'required_capabilities': ['rational_numbers'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'fractions': ['1/37', '9/22']}, {'fractions': ['61/99', '4/15']}, {'fractions': ['38/41', '3/44']}, {'fractions': ['13/33', '7/12']}, {'fractions': ['9/11', '9/22']}, {'fractions': ['2/3', '14/55']}, {'fractions': ['5/11', '3/22']}, {'fractions': ['1/9', '11/18']}, {'fractions': ['8/37', '7/12']}, {'fractions': ['9/37', '7/12']}, {'fractions': ['21/41', '1/24']}, {'fractions': ['2/3', '1/24']}, {'fractions': ['1/33', '17/24']}, {'fractions': ['7/11', '9/22']}, {'fractions': ['24/41', '9/74']}, {'fractions': ['13/27', '7/22']}, {'fractions': ['10/13', '21/22']}, {'fractions': ['4/7', '2/15']}, {'fractions': ['5/7', '15/22']}, {'fractions': ['3/11', '17/24']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_RationalNumbers', 'fixed_domain_key': 'number_system.rational_numbers', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': [], 'matched_capabilities': [], 'selected_operation': 'fraction_to_decimal_expansion', 'registry_revision': 'promoted-4a5f2cab5b55', 'domain_module': 'core.domain.promoted.number_system_rational_numbers.rational_numbers_domain', 'entrypoint': 'build_rational_numbers_matrix', 'allowed_operations': ['plot_rational_points_on_number_line', 'evaluate_rationality_statements', 'identify_rational_numbers', 'fraction_to_decimal_expansion'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_RationalNumbers'}), seed)
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
