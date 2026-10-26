from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "sequence_statements"
TEXTBOOK_EXAMPLE_ID = 12680
DEFAULT_COMPONENT_ID = "src_12680" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Sequence"
FIXED_DOMAIN_KEY = "sequence.progression"
DOMAIN_OPERATION = "sequence_statements"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'sequence.progression', 'required_capabilities': ['sequence_statements'], 'domain_operation': 'sequence_statements', 'problem_type_id': 'sequence_statements', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 5, 'c': -3, 'shown_type': 'arithmetic', 'shown_a1': 5, 'shown_c': -3}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 2, 'c': 2, 'shown_type': 'arithmetic', 'shown_a1': 2, 'shown_c': 2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': -1, 'c': 2, 'shown_type': 'geometric', 'shown_a1': 0, 'shown_c': 2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': -1, 'c': 4, 'shown_type': 'arithmetic', 'shown_a1': -1, 'shown_c': 4}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 2, 'c': 4, 'shown_type': 'arithmetic', 'shown_a1': 2, 'shown_c': 4}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 2, 'c': 5, 'shown_type': 'arithmetic', 'shown_a1': 4, 'shown_c': 5}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 4, 'c': 2, 'shown_type': 'geometric', 'shown_a1': 4, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 5, 'c': -2, 'shown_type': 'geometric', 'shown_a1': 6, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 4, 'c': 2, 'shown_type': 'arithmetic', 'shown_a1': 5, 'shown_c': 2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 4, 'c': 5, 'shown_type': 'arithmetic', 'shown_a1': 4, 'shown_c': 5}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 3, 'c': -2, 'shown_type': 'arithmetic', 'shown_a1': 3, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 4, 'c': 3, 'shown_type': 'geometric', 'shown_a1': 4, 'shown_c': 3}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 2, 'c': 3, 'shown_type': 'geometric', 'shown_a1': 2, 'shown_c': -3}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': -1, 'c': 4, 'shown_type': 'geometric', 'shown_a1': -1, 'shown_c': 4}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 6, 'c': 2, 'shown_type': 'arithmetic', 'shown_a1': 6, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': -1, 'c': 2, 'shown_type': 'geometric', 'shown_a1': -1, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': -1, 'c': 3, 'shown_type': 'arithmetic', 'shown_a1': -1, 'shown_c': 3}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 6, 'c': -2, 'shown_type': 'geometric', 'shown_a1': 8, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 5, 'c': 5, 'shown_type': 'arithmetic', 'shown_a1': 5, 'shown_c': 5}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 5, 'c': 2, 'shown_type': 'geometric', 'shown_a1': 5, 'shown_c': -2}}]}}, 'phase1_classification': {'fixed_domain_key': 'sequence.progression', 'required_capabilities': ['sequence_statements'], 'domain_operation': 'sequence_statements', 'problem_type_id': 'sequence_statements', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 5, 'c': -3, 'shown_type': 'arithmetic', 'shown_a1': 5, 'shown_c': -3}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 2, 'c': 2, 'shown_type': 'arithmetic', 'shown_a1': 2, 'shown_c': 2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': -1, 'c': 2, 'shown_type': 'geometric', 'shown_a1': 0, 'shown_c': 2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': -1, 'c': 4, 'shown_type': 'arithmetic', 'shown_a1': -1, 'shown_c': 4}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 2, 'c': 4, 'shown_type': 'arithmetic', 'shown_a1': 2, 'shown_c': 4}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 2, 'c': 5, 'shown_type': 'arithmetic', 'shown_a1': 4, 'shown_c': 5}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 4, 'c': 2, 'shown_type': 'geometric', 'shown_a1': 4, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 5, 'c': -2, 'shown_type': 'geometric', 'shown_a1': 6, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 4, 'c': 2, 'shown_type': 'arithmetic', 'shown_a1': 5, 'shown_c': 2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 4, 'c': 5, 'shown_type': 'arithmetic', 'shown_a1': 4, 'shown_c': 5}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 3, 'c': -2, 'shown_type': 'arithmetic', 'shown_a1': 3, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 4, 'c': 3, 'shown_type': 'geometric', 'shown_a1': 4, 'shown_c': 3}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 2, 'c': 3, 'shown_type': 'geometric', 'shown_a1': 2, 'shown_c': -3}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': -1, 'c': 4, 'shown_type': 'geometric', 'shown_a1': -1, 'shown_c': 4}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 6, 'c': 2, 'shown_type': 'arithmetic', 'shown_a1': 6, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': -1, 'c': 2, 'shown_type': 'geometric', 'shown_a1': -1, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': -1, 'c': 3, 'shown_type': 'arithmetic', 'shown_a1': -1, 'shown_c': 3}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 6, 'c': -2, 'shown_type': 'geometric', 'shown_a1': 8, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 5, 'c': 5, 'shown_type': 'arithmetic', 'shown_a1': 5, 'shown_c': 5}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 5, 'c': 2, 'shown_type': 'geometric', 'shown_a1': 5, 'shown_c': -2}}]}}, 'problem_type_id': 'sequence_statements', 'required_capabilities': ['sequence_statements'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 5, 'c': -3, 'shown_type': 'arithmetic', 'shown_a1': 5, 'shown_c': -3}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 2, 'c': 2, 'shown_type': 'arithmetic', 'shown_a1': 2, 'shown_c': 2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': -1, 'c': 2, 'shown_type': 'geometric', 'shown_a1': 0, 'shown_c': 2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': -1, 'c': 4, 'shown_type': 'arithmetic', 'shown_a1': -1, 'shown_c': 4}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 2, 'c': 4, 'shown_type': 'arithmetic', 'shown_a1': 2, 'shown_c': 4}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 2, 'c': 5, 'shown_type': 'arithmetic', 'shown_a1': 4, 'shown_c': 5}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 4, 'c': 2, 'shown_type': 'geometric', 'shown_a1': 4, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 5, 'c': -2, 'shown_type': 'geometric', 'shown_a1': 6, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 4, 'c': 2, 'shown_type': 'arithmetic', 'shown_a1': 5, 'shown_c': 2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 4, 'c': 5, 'shown_type': 'arithmetic', 'shown_a1': 4, 'shown_c': 5}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 3, 'c': -2, 'shown_type': 'arithmetic', 'shown_a1': 3, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 4, 'c': 3, 'shown_type': 'geometric', 'shown_a1': 4, 'shown_c': 3}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 2, 'c': 3, 'shown_type': 'geometric', 'shown_a1': 2, 'shown_c': -3}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': -1, 'c': 4, 'shown_type': 'geometric', 'shown_a1': -1, 'shown_c': 4}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 6, 'c': 2, 'shown_type': 'arithmetic', 'shown_a1': 6, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': -1, 'c': 2, 'shown_type': 'geometric', 'shown_a1': -1, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': -1, 'c': 3, 'shown_type': 'arithmetic', 'shown_a1': -1, 'shown_c': 3}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 6, 'c': -2, 'shown_type': 'geometric', 'shown_a1': 8, 'shown_c': -2}}, {'statement': {'kind': 'recurrence_claim', 'type': 'arithmetic', 'a1': 5, 'c': 5, 'shown_type': 'arithmetic', 'shown_a1': 5, 'shown_c': 5}}, {'statement': {'kind': 'recurrence_claim', 'type': 'geometric', 'a1': 5, 'c': 2, 'shown_type': 'geometric', 'shown_a1': 5, 'shown_c': -2}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Sequence', 'fixed_domain_key': 'sequence.progression', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['sequence_statements'], 'matched_capabilities': ['sequence_statements'], 'selected_operation': 'sequence_statements', 'registry_revision': 'promoted-9863553f3bfd', 'domain_module': 'core.domain.promoted.sequence_progression.sequence_progression_domain', 'entrypoint': 'build_sequence_progression_matrix', 'allowed_operations': ['arithmetic_from_terms', 'geometric_from_relations', 'geometric_from_terms', 'progression_three_numbers', 'sequence_statements', 'sequence_terms_from_formula'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Sequence'}), seed)
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
