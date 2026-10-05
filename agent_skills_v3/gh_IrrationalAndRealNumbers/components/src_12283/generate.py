from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "solve_rational_unknowns_from_radical_identity"
TEXTBOOK_EXAMPLE_ID = 12283
DEFAULT_COMPONENT_ID = "src_12283" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_IrrationalAndRealNumbers"
FIXED_DOMAIN_KEY = "number_system.real_numbers"
DOMAIN_OPERATION = "solve_rational_unknowns_from_radical_identity"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'number_system.real_numbers', 'required_capabilities': ['real_numbers'], 'domain_operation': 'solve_rational_unknowns_from_radical_identity', 'problem_type_id': 'solve_rational_unknowns_from_radical_identity', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'radicand': 2, 'coefficients': {'a': {'rational': 3, 'radical': 5}, 'b': {'rational': 2, 'radical': -1}}, 'rhs': {'rational': -1, 'radical': 7}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 1}, 'b': {'rational': 5, 'radical': -1}}, 'rhs': {'rational': -7, 'radical': -3}}, {'radicand': 2, 'coefficients': {'a': {'rational': 2, 'radical': 6}, 'b': {'rational': 1, 'radical': -2}}, 'rhs': {'rational': 2, 'radical': -14}}, {'radicand': 2, 'coefficients': {'a': {'rational': 5, 'radical': 3}, 'b': {'rational': 6, 'radical': -1}}, 'rhs': {'rational': 8, 'radical': -9}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 2}, 'b': {'rational': 2, 'radical': -1}}, 'rhs': {'rational': 8, 'radical': 11}}, {'radicand': 2, 'coefficients': {'a': {'rational': 1, 'radical': 4}, 'b': {'rational': 2, 'radical': -2}}, 'rhs': {'rational': -7, 'radical': -18}}, {'radicand': 2, 'coefficients': {'a': {'rational': 3, 'radical': 5}, 'b': {'rational': 1, 'radical': -2}}, 'rhs': {'rational': 8, 'radical': -5}}, {'radicand': 2, 'coefficients': {'a': {'rational': 5, 'radical': 5}, 'b': {'rational': 3, 'radical': -2}}, 'rhs': {'rational': -12, 'radical': -17}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 6}, 'b': {'rational': 2, 'radical': -2}}, 'rhs': {'rational': 24, 'radical': 12}}, {'radicand': 2, 'coefficients': {'a': {'rational': 1, 'radical': 4}, 'b': {'rational': 6, 'radical': -2}}, 'rhs': {'rational': -10, 'radical': -14}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 6}, 'b': {'rational': 2, 'radical': -3}}, 'rhs': {'rational': -16, 'radical': -21}}, {'radicand': 2, 'coefficients': {'a': {'rational': 2, 'radical': 1}, 'b': {'rational': 5, 'radical': -2}}, 'rhs': {'rational': -25, 'radical': 1}}, {'radicand': 2, 'coefficients': {'a': {'rational': 4, 'radical': 1}, 'b': {'rational': 4, 'radical': -2}}, 'rhs': {'rational': -16, 'radical': -7}}, {'radicand': 2, 'coefficients': {'a': {'rational': 3, 'radical': 4}, 'b': {'rational': 3, 'radical': -1}}, 'rhs': {'rational': -6, 'radical': 7}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 4}, 'b': {'rational': 4, 'radical': -1}}, 'rhs': {'rational': 16, 'radical': 18}}, {'radicand': 2, 'coefficients': {'a': {'rational': 2, 'radical': 2}, 'b': {'rational': 3, 'radical': -3}}, 'rhs': {'rational': 20, 'radical': -4}}, {'radicand': 2, 'coefficients': {'a': {'rational': 1, 'radical': 4}, 'b': {'rational': 5, 'radical': -3}}, 'rhs': {'rational': -10, 'radical': -17}}, {'radicand': 2, 'coefficients': {'a': {'rational': 3, 'radical': 5}, 'b': {'rational': 3, 'radical': -2}}, 'rhs': {'rational': -6, 'radical': -24}}, {'radicand': 2, 'coefficients': {'a': {'rational': 4, 'radical': 4}, 'b': {'rational': 6, 'radical': -1}}, 'rhs': {'rational': 42, 'radical': 7}}, {'radicand': 2, 'coefficients': {'a': {'rational': 4, 'radical': 1}, 'b': {'rational': 5, 'radical': -3}}, 'rhs': {'rational': 17, 'radical': -17}}]}}, 'phase1_classification': {'fixed_domain_key': 'number_system.real_numbers', 'required_capabilities': ['real_numbers'], 'domain_operation': 'solve_rational_unknowns_from_radical_identity', 'problem_type_id': 'solve_rational_unknowns_from_radical_identity', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'radicand': 2, 'coefficients': {'a': {'rational': 3, 'radical': 5}, 'b': {'rational': 2, 'radical': -1}}, 'rhs': {'rational': -1, 'radical': 7}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 1}, 'b': {'rational': 5, 'radical': -1}}, 'rhs': {'rational': -7, 'radical': -3}}, {'radicand': 2, 'coefficients': {'a': {'rational': 2, 'radical': 6}, 'b': {'rational': 1, 'radical': -2}}, 'rhs': {'rational': 2, 'radical': -14}}, {'radicand': 2, 'coefficients': {'a': {'rational': 5, 'radical': 3}, 'b': {'rational': 6, 'radical': -1}}, 'rhs': {'rational': 8, 'radical': -9}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 2}, 'b': {'rational': 2, 'radical': -1}}, 'rhs': {'rational': 8, 'radical': 11}}, {'radicand': 2, 'coefficients': {'a': {'rational': 1, 'radical': 4}, 'b': {'rational': 2, 'radical': -2}}, 'rhs': {'rational': -7, 'radical': -18}}, {'radicand': 2, 'coefficients': {'a': {'rational': 3, 'radical': 5}, 'b': {'rational': 1, 'radical': -2}}, 'rhs': {'rational': 8, 'radical': -5}}, {'radicand': 2, 'coefficients': {'a': {'rational': 5, 'radical': 5}, 'b': {'rational': 3, 'radical': -2}}, 'rhs': {'rational': -12, 'radical': -17}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 6}, 'b': {'rational': 2, 'radical': -2}}, 'rhs': {'rational': 24, 'radical': 12}}, {'radicand': 2, 'coefficients': {'a': {'rational': 1, 'radical': 4}, 'b': {'rational': 6, 'radical': -2}}, 'rhs': {'rational': -10, 'radical': -14}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 6}, 'b': {'rational': 2, 'radical': -3}}, 'rhs': {'rational': -16, 'radical': -21}}, {'radicand': 2, 'coefficients': {'a': {'rational': 2, 'radical': 1}, 'b': {'rational': 5, 'radical': -2}}, 'rhs': {'rational': -25, 'radical': 1}}, {'radicand': 2, 'coefficients': {'a': {'rational': 4, 'radical': 1}, 'b': {'rational': 4, 'radical': -2}}, 'rhs': {'rational': -16, 'radical': -7}}, {'radicand': 2, 'coefficients': {'a': {'rational': 3, 'radical': 4}, 'b': {'rational': 3, 'radical': -1}}, 'rhs': {'rational': -6, 'radical': 7}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 4}, 'b': {'rational': 4, 'radical': -1}}, 'rhs': {'rational': 16, 'radical': 18}}, {'radicand': 2, 'coefficients': {'a': {'rational': 2, 'radical': 2}, 'b': {'rational': 3, 'radical': -3}}, 'rhs': {'rational': 20, 'radical': -4}}, {'radicand': 2, 'coefficients': {'a': {'rational': 1, 'radical': 4}, 'b': {'rational': 5, 'radical': -3}}, 'rhs': {'rational': -10, 'radical': -17}}, {'radicand': 2, 'coefficients': {'a': {'rational': 3, 'radical': 5}, 'b': {'rational': 3, 'radical': -2}}, 'rhs': {'rational': -6, 'radical': -24}}, {'radicand': 2, 'coefficients': {'a': {'rational': 4, 'radical': 4}, 'b': {'rational': 6, 'radical': -1}}, 'rhs': {'rational': 42, 'radical': 7}}, {'radicand': 2, 'coefficients': {'a': {'rational': 4, 'radical': 1}, 'b': {'rational': 5, 'radical': -3}}, 'rhs': {'rational': 17, 'radical': -17}}]}}, 'problem_type_id': 'solve_rational_unknowns_from_radical_identity', 'required_capabilities': ['real_numbers'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'radicand': 2, 'coefficients': {'a': {'rational': 3, 'radical': 5}, 'b': {'rational': 2, 'radical': -1}}, 'rhs': {'rational': -1, 'radical': 7}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 1}, 'b': {'rational': 5, 'radical': -1}}, 'rhs': {'rational': -7, 'radical': -3}}, {'radicand': 2, 'coefficients': {'a': {'rational': 2, 'radical': 6}, 'b': {'rational': 1, 'radical': -2}}, 'rhs': {'rational': 2, 'radical': -14}}, {'radicand': 2, 'coefficients': {'a': {'rational': 5, 'radical': 3}, 'b': {'rational': 6, 'radical': -1}}, 'rhs': {'rational': 8, 'radical': -9}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 2}, 'b': {'rational': 2, 'radical': -1}}, 'rhs': {'rational': 8, 'radical': 11}}, {'radicand': 2, 'coefficients': {'a': {'rational': 1, 'radical': 4}, 'b': {'rational': 2, 'radical': -2}}, 'rhs': {'rational': -7, 'radical': -18}}, {'radicand': 2, 'coefficients': {'a': {'rational': 3, 'radical': 5}, 'b': {'rational': 1, 'radical': -2}}, 'rhs': {'rational': 8, 'radical': -5}}, {'radicand': 2, 'coefficients': {'a': {'rational': 5, 'radical': 5}, 'b': {'rational': 3, 'radical': -2}}, 'rhs': {'rational': -12, 'radical': -17}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 6}, 'b': {'rational': 2, 'radical': -2}}, 'rhs': {'rational': 24, 'radical': 12}}, {'radicand': 2, 'coefficients': {'a': {'rational': 1, 'radical': 4}, 'b': {'rational': 6, 'radical': -2}}, 'rhs': {'rational': -10, 'radical': -14}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 6}, 'b': {'rational': 2, 'radical': -3}}, 'rhs': {'rational': -16, 'radical': -21}}, {'radicand': 2, 'coefficients': {'a': {'rational': 2, 'radical': 1}, 'b': {'rational': 5, 'radical': -2}}, 'rhs': {'rational': -25, 'radical': 1}}, {'radicand': 2, 'coefficients': {'a': {'rational': 4, 'radical': 1}, 'b': {'rational': 4, 'radical': -2}}, 'rhs': {'rational': -16, 'radical': -7}}, {'radicand': 2, 'coefficients': {'a': {'rational': 3, 'radical': 4}, 'b': {'rational': 3, 'radical': -1}}, 'rhs': {'rational': -6, 'radical': 7}}, {'radicand': 2, 'coefficients': {'a': {'rational': 6, 'radical': 4}, 'b': {'rational': 4, 'radical': -1}}, 'rhs': {'rational': 16, 'radical': 18}}, {'radicand': 2, 'coefficients': {'a': {'rational': 2, 'radical': 2}, 'b': {'rational': 3, 'radical': -3}}, 'rhs': {'rational': 20, 'radical': -4}}, {'radicand': 2, 'coefficients': {'a': {'rational': 1, 'radical': 4}, 'b': {'rational': 5, 'radical': -3}}, 'rhs': {'rational': -10, 'radical': -17}}, {'radicand': 2, 'coefficients': {'a': {'rational': 3, 'radical': 5}, 'b': {'rational': 3, 'radical': -2}}, 'rhs': {'rational': -6, 'radical': -24}}, {'radicand': 2, 'coefficients': {'a': {'rational': 4, 'radical': 4}, 'b': {'rational': 6, 'radical': -1}}, 'rhs': {'rational': 42, 'radical': 7}}, {'radicand': 2, 'coefficients': {'a': {'rational': 4, 'radical': 1}, 'b': {'rational': 5, 'radical': -3}}, 'rhs': {'rational': 17, 'radical': -17}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_IrrationalAndRealNumbers', 'fixed_domain_key': 'number_system.real_numbers', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': [], 'matched_capabilities': [], 'selected_operation': 'solve_rational_unknowns_from_radical_identity', 'registry_revision': 'promoted-efbd928b05fd', 'domain_module': 'core.domain.promoted.number_system_real_numbers.real_numbers_domain', 'entrypoint': 'build_real_numbers_matrix', 'allowed_operations': ['solve_rational_unknowns_from_radical_identity', 'approximate_square_root_by_decimal_search'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_IrrationalAndRealNumbers'}), seed)
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
