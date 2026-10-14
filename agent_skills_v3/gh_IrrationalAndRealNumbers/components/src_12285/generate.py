from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "approximate_square_root_by_decimal_search"
TEXTBOOK_EXAMPLE_ID = 12285
DEFAULT_COMPONENT_ID = "src_12285" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_IrrationalAndRealNumbers"
FIXED_DOMAIN_KEY = "number_system.real_numbers"
DOMAIN_OPERATION = "approximate_square_root_by_decimal_search"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'number_system.real_numbers', 'required_capabilities': ['real_numbers'], 'domain_operation': 'approximate_square_root_by_decimal_search', 'problem_type_id': 'approximate_square_root_by_decimal_search', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'radicand': 3, 'places': 2, 'mode': 'truncate'}, {'radicand': 18, 'places': 2, 'mode': 'truncate'}, {'radicand': 22, 'places': 2, 'mode': 'truncate'}, {'radicand': 8, 'places': 2, 'mode': 'truncate'}, {'radicand': 11, 'places': 2, 'mode': 'truncate'}, {'radicand': 23, 'places': 2, 'mode': 'truncate'}, {'radicand': 19, 'places': 2, 'mode': 'truncate'}, {'radicand': 27, 'places': 2, 'mode': 'truncate'}, {'radicand': 6, 'places': 2, 'mode': 'truncate'}, {'radicand': 2, 'places': 2, 'mode': 'truncate'}, {'radicand': 20, 'places': 2, 'mode': 'truncate'}, {'radicand': 24, 'places': 2, 'mode': 'truncate'}, {'radicand': 28, 'places': 2, 'mode': 'truncate'}, {'radicand': 13, 'places': 2, 'mode': 'truncate'}, {'radicand': 17, 'places': 2, 'mode': 'truncate'}, {'radicand': 7, 'places': 2, 'mode': 'truncate'}, {'radicand': 12, 'places': 2, 'mode': 'truncate'}, {'radicand': 14, 'places': 2, 'mode': 'truncate'}, {'radicand': 10, 'places': 2, 'mode': 'truncate'}, {'radicand': 15, 'places': 2, 'mode': 'truncate'}]}}, 'phase1_classification': {'fixed_domain_key': 'number_system.real_numbers', 'required_capabilities': ['real_numbers'], 'domain_operation': 'approximate_square_root_by_decimal_search', 'problem_type_id': 'approximate_square_root_by_decimal_search', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'radicand': 3, 'places': 2, 'mode': 'truncate'}, {'radicand': 18, 'places': 2, 'mode': 'truncate'}, {'radicand': 22, 'places': 2, 'mode': 'truncate'}, {'radicand': 8, 'places': 2, 'mode': 'truncate'}, {'radicand': 11, 'places': 2, 'mode': 'truncate'}, {'radicand': 23, 'places': 2, 'mode': 'truncate'}, {'radicand': 19, 'places': 2, 'mode': 'truncate'}, {'radicand': 27, 'places': 2, 'mode': 'truncate'}, {'radicand': 6, 'places': 2, 'mode': 'truncate'}, {'radicand': 2, 'places': 2, 'mode': 'truncate'}, {'radicand': 20, 'places': 2, 'mode': 'truncate'}, {'radicand': 24, 'places': 2, 'mode': 'truncate'}, {'radicand': 28, 'places': 2, 'mode': 'truncate'}, {'radicand': 13, 'places': 2, 'mode': 'truncate'}, {'radicand': 17, 'places': 2, 'mode': 'truncate'}, {'radicand': 7, 'places': 2, 'mode': 'truncate'}, {'radicand': 12, 'places': 2, 'mode': 'truncate'}, {'radicand': 14, 'places': 2, 'mode': 'truncate'}, {'radicand': 10, 'places': 2, 'mode': 'truncate'}, {'radicand': 15, 'places': 2, 'mode': 'truncate'}]}}, 'problem_type_id': 'approximate_square_root_by_decimal_search', 'required_capabilities': ['real_numbers'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'radicand': 3, 'places': 2, 'mode': 'truncate'}, {'radicand': 18, 'places': 2, 'mode': 'truncate'}, {'radicand': 22, 'places': 2, 'mode': 'truncate'}, {'radicand': 8, 'places': 2, 'mode': 'truncate'}, {'radicand': 11, 'places': 2, 'mode': 'truncate'}, {'radicand': 23, 'places': 2, 'mode': 'truncate'}, {'radicand': 19, 'places': 2, 'mode': 'truncate'}, {'radicand': 27, 'places': 2, 'mode': 'truncate'}, {'radicand': 6, 'places': 2, 'mode': 'truncate'}, {'radicand': 2, 'places': 2, 'mode': 'truncate'}, {'radicand': 20, 'places': 2, 'mode': 'truncate'}, {'radicand': 24, 'places': 2, 'mode': 'truncate'}, {'radicand': 28, 'places': 2, 'mode': 'truncate'}, {'radicand': 13, 'places': 2, 'mode': 'truncate'}, {'radicand': 17, 'places': 2, 'mode': 'truncate'}, {'radicand': 7, 'places': 2, 'mode': 'truncate'}, {'radicand': 12, 'places': 2, 'mode': 'truncate'}, {'radicand': 14, 'places': 2, 'mode': 'truncate'}, {'radicand': 10, 'places': 2, 'mode': 'truncate'}, {'radicand': 15, 'places': 2, 'mode': 'truncate'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_IrrationalAndRealNumbers', 'fixed_domain_key': 'number_system.real_numbers', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': [], 'matched_capabilities': [], 'selected_operation': 'approximate_square_root_by_decimal_search', 'registry_revision': 'promoted-efbd928b05fd', 'domain_module': 'core.domain.promoted.number_system_real_numbers.real_numbers_domain', 'entrypoint': 'build_real_numbers_matrix', 'allowed_operations': ['solve_rational_unknowns_from_radical_identity', 'approximate_square_root_by_decimal_search'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_IrrationalAndRealNumbers'}), seed)
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
