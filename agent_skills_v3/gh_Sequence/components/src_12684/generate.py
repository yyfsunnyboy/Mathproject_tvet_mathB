from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "solution_set"
PROBLEM_TYPE_ID = "progression_three_numbers"
TEXTBOOK_EXAMPLE_ID = 12684
DEFAULT_COMPONENT_ID = "src_12684" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Sequence"
FIXED_DOMAIN_KEY = "sequence.progression"
DOMAIN_OPERATION = "progression_three_numbers"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'sequence.progression', 'required_capabilities': ['progression_three_numbers'], 'domain_operation': 'progression_three_numbers', 'problem_type_id': 'progression_three_numbers', 'presentation_mode': 'short_answer', 'answer_type': 'solution_set', 'generation_constraints': {'variants': [{'kind': 'arith_geo_chain', 'p': -2, 'q': 18}, {'kind': 'arith_geo_chain', 'p': 3, 'q': -25}, {'kind': 'arith_geo_chain', 'p': -3, 'q': -3}, {'kind': 'arith_geo_chain', 'p': -3, 'q': 27}, {'kind': 'arith_geo_chain', 'p': -3, 'q': 25}, {'kind': 'arith_geo_chain', 'p': -4, 'q': -18}, {'kind': 'arith_geo_chain', 'p': -6, 'q': -2}, {'kind': 'arith_geo_chain', 'p': -6, 'q': -1}, {'kind': 'arith_geo_chain', 'p': -4, 'q': 36}, {'kind': 'arith_geo_chain', 'p': 3, 'q': 3}, {'kind': 'arith_geo_chain', 'p': 2, 'q': -18}, {'kind': 'arith_geo_chain', 'p': -6, 'q': -6}, {'kind': 'arith_geo_chain', 'p': -3, 'q': -25}, {'kind': 'arith_geo_chain', 'p': 4, 'q': -36}, {'kind': 'arith_geo_chain', 'p': -3, 'q': -1}, {'kind': 'arith_geo_chain', 'p': 3, 'q': -27}, {'kind': 'arith_geo_chain', 'p': -1, 'q': -1}, {'kind': 'arith_geo_chain', 'p': -2, 'q': 25}, {'kind': 'arith_geo_chain', 'p': 1, 'q': 1}, {'kind': 'arith_geo_chain', 'p': -1, 'q': 9}]}}, 'phase1_classification': {'fixed_domain_key': 'sequence.progression', 'required_capabilities': ['progression_three_numbers'], 'domain_operation': 'progression_three_numbers', 'problem_type_id': 'progression_three_numbers', 'presentation_mode': 'short_answer', 'answer_type': 'solution_set', 'generation_constraints': {'variants': [{'kind': 'arith_geo_chain', 'p': -2, 'q': 18}, {'kind': 'arith_geo_chain', 'p': 3, 'q': -25}, {'kind': 'arith_geo_chain', 'p': -3, 'q': -3}, {'kind': 'arith_geo_chain', 'p': -3, 'q': 27}, {'kind': 'arith_geo_chain', 'p': -3, 'q': 25}, {'kind': 'arith_geo_chain', 'p': -4, 'q': -18}, {'kind': 'arith_geo_chain', 'p': -6, 'q': -2}, {'kind': 'arith_geo_chain', 'p': -6, 'q': -1}, {'kind': 'arith_geo_chain', 'p': -4, 'q': 36}, {'kind': 'arith_geo_chain', 'p': 3, 'q': 3}, {'kind': 'arith_geo_chain', 'p': 2, 'q': -18}, {'kind': 'arith_geo_chain', 'p': -6, 'q': -6}, {'kind': 'arith_geo_chain', 'p': -3, 'q': -25}, {'kind': 'arith_geo_chain', 'p': 4, 'q': -36}, {'kind': 'arith_geo_chain', 'p': -3, 'q': -1}, {'kind': 'arith_geo_chain', 'p': 3, 'q': -27}, {'kind': 'arith_geo_chain', 'p': -1, 'q': -1}, {'kind': 'arith_geo_chain', 'p': -2, 'q': 25}, {'kind': 'arith_geo_chain', 'p': 1, 'q': 1}, {'kind': 'arith_geo_chain', 'p': -1, 'q': 9}]}}, 'problem_type_id': 'progression_three_numbers', 'required_capabilities': ['progression_three_numbers'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'kind': 'arith_geo_chain', 'p': -2, 'q': 18}, {'kind': 'arith_geo_chain', 'p': 3, 'q': -25}, {'kind': 'arith_geo_chain', 'p': -3, 'q': -3}, {'kind': 'arith_geo_chain', 'p': -3, 'q': 27}, {'kind': 'arith_geo_chain', 'p': -3, 'q': 25}, {'kind': 'arith_geo_chain', 'p': -4, 'q': -18}, {'kind': 'arith_geo_chain', 'p': -6, 'q': -2}, {'kind': 'arith_geo_chain', 'p': -6, 'q': -1}, {'kind': 'arith_geo_chain', 'p': -4, 'q': 36}, {'kind': 'arith_geo_chain', 'p': 3, 'q': 3}, {'kind': 'arith_geo_chain', 'p': 2, 'q': -18}, {'kind': 'arith_geo_chain', 'p': -6, 'q': -6}, {'kind': 'arith_geo_chain', 'p': -3, 'q': -25}, {'kind': 'arith_geo_chain', 'p': 4, 'q': -36}, {'kind': 'arith_geo_chain', 'p': -3, 'q': -1}, {'kind': 'arith_geo_chain', 'p': 3, 'q': -27}, {'kind': 'arith_geo_chain', 'p': -1, 'q': -1}, {'kind': 'arith_geo_chain', 'p': -2, 'q': 25}, {'kind': 'arith_geo_chain', 'p': 1, 'q': 1}, {'kind': 'arith_geo_chain', 'p': -1, 'q': 9}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Sequence', 'fixed_domain_key': 'sequence.progression', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['progression_three_numbers'], 'matched_capabilities': ['progression_three_numbers'], 'selected_operation': 'progression_three_numbers', 'registry_revision': 'promoted-9863553f3bfd', 'domain_module': 'core.domain.promoted.sequence_progression.sequence_progression_domain', 'entrypoint': 'build_sequence_progression_matrix', 'allowed_operations': ['arithmetic_from_terms', 'geometric_from_relations', 'geometric_from_terms', 'progression_three_numbers', 'sequence_statements', 'sequence_terms_from_formula'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Sequence'}), seed)
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
