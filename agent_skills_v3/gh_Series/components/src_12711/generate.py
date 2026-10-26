from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "solution_set"
PROBLEM_TYPE_ID = "geometric_series_relation"
TEXTBOOK_EXAMPLE_ID = 12711
DEFAULT_COMPONENT_ID = "src_12711" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Series"
FIXED_DOMAIN_KEY = "sequence.series_sums"
DOMAIN_OPERATION = "geometric_series_relation"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'sequence.series_sums', 'required_capabilities': ['geometric_series_relation'], 'domain_operation': 'geometric_series_relation', 'problem_type_id': 'geometric_series_relation', 'presentation_mode': 'short_answer', 'answer_type': 'solution_set', 'generation_constraints': {'variants': [{'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 6, 'B': 54, 'n': 5}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 6, 'B': 54, 'n': 7}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 4, 'B': 64, 'n': 5}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 6, 'B': 24, 'n': 5}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': -8, 'B': -32, 'n': 4}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 8, 'B': 32, 'n': 7}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 2, 'B': 8, 'n': 7}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 27, 'B': 243, 'n': 4}, {'kind': 'two_terms', 'p': 2, 'q': 6, 'A': -4, 'B': -1024, 'n': 6}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': -4, 'B': -16, 'n': 6}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 8, 'B': 32, 'n': 6}, {'kind': 'two_terms', 'p': 1, 'q': 3, 'A': 1, 'B': 9, 'n': 5}, {'kind': 'two_terms', 'p': 3, 'q': 7, 'A': -32, 'B': -8192, 'n': 7}, {'kind': 'two_terms', 'p': 3, 'q': 7, 'A': -9, 'B': -729, 'n': 7}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 27, 'B': 243, 'n': 5}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 9, 'B': 81, 'n': 6}, {'kind': 'two_terms', 'p': 1, 'q': 3, 'A': 2, 'B': 8, 'n': 6}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 9, 'B': 81, 'n': 6}, {'kind': 'two_terms', 'p': 3, 'q': 7, 'A': 32, 'B': 8192, 'n': 4}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 16, 'B': 256, 'n': 7}]}}, 'phase1_classification': {'fixed_domain_key': 'sequence.series_sums', 'required_capabilities': ['geometric_series_relation'], 'domain_operation': 'geometric_series_relation', 'problem_type_id': 'geometric_series_relation', 'presentation_mode': 'short_answer', 'answer_type': 'solution_set', 'generation_constraints': {'variants': [{'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 6, 'B': 54, 'n': 5}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 6, 'B': 54, 'n': 7}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 4, 'B': 64, 'n': 5}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 6, 'B': 24, 'n': 5}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': -8, 'B': -32, 'n': 4}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 8, 'B': 32, 'n': 7}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 2, 'B': 8, 'n': 7}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 27, 'B': 243, 'n': 4}, {'kind': 'two_terms', 'p': 2, 'q': 6, 'A': -4, 'B': -1024, 'n': 6}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': -4, 'B': -16, 'n': 6}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 8, 'B': 32, 'n': 6}, {'kind': 'two_terms', 'p': 1, 'q': 3, 'A': 1, 'B': 9, 'n': 5}, {'kind': 'two_terms', 'p': 3, 'q': 7, 'A': -32, 'B': -8192, 'n': 7}, {'kind': 'two_terms', 'p': 3, 'q': 7, 'A': -9, 'B': -729, 'n': 7}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 27, 'B': 243, 'n': 5}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 9, 'B': 81, 'n': 6}, {'kind': 'two_terms', 'p': 1, 'q': 3, 'A': 2, 'B': 8, 'n': 6}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 9, 'B': 81, 'n': 6}, {'kind': 'two_terms', 'p': 3, 'q': 7, 'A': 32, 'B': 8192, 'n': 4}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 16, 'B': 256, 'n': 7}]}}, 'problem_type_id': 'geometric_series_relation', 'required_capabilities': ['geometric_series_relation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 6, 'B': 54, 'n': 5}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 6, 'B': 54, 'n': 7}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 4, 'B': 64, 'n': 5}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 6, 'B': 24, 'n': 5}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': -8, 'B': -32, 'n': 4}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 8, 'B': 32, 'n': 7}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 2, 'B': 8, 'n': 7}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 27, 'B': 243, 'n': 4}, {'kind': 'two_terms', 'p': 2, 'q': 6, 'A': -4, 'B': -1024, 'n': 6}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': -4, 'B': -16, 'n': 6}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 8, 'B': 32, 'n': 6}, {'kind': 'two_terms', 'p': 1, 'q': 3, 'A': 1, 'B': 9, 'n': 5}, {'kind': 'two_terms', 'p': 3, 'q': 7, 'A': -32, 'B': -8192, 'n': 7}, {'kind': 'two_terms', 'p': 3, 'q': 7, 'A': -9, 'B': -729, 'n': 7}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 27, 'B': 243, 'n': 5}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 9, 'B': 81, 'n': 6}, {'kind': 'two_terms', 'p': 1, 'q': 3, 'A': 2, 'B': 8, 'n': 6}, {'kind': 'two_terms', 'p': 2, 'q': 4, 'A': 9, 'B': 81, 'n': 6}, {'kind': 'two_terms', 'p': 3, 'q': 7, 'A': 32, 'B': 8192, 'n': 4}, {'kind': 'two_terms', 'p': 3, 'q': 5, 'A': 16, 'B': 256, 'n': 7}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Series', 'fixed_domain_key': 'sequence.series_sums', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['geometric_series_relation'], 'matched_capabilities': ['geometric_series_relation'], 'selected_operation': 'geometric_series_relation', 'registry_revision': 'promoted-b3fc93095b76', 'domain_module': 'core.domain.promoted.series_summation.series_summation_domain', 'entrypoint': 'build_series_summation_matrix', 'allowed_operations': ['arithmetic_series_items', 'arithmetic_series_relation', 'fish_rows', 'geometric_series_items', 'geometric_series_relation', 'partial_sum_terms', 'series_statements'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Series'}), seed)
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
