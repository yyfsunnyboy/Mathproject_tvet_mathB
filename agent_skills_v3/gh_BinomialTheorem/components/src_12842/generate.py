from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "binomial_expansion"
TEXTBOOK_EXAMPLE_ID = 12842
DEFAULT_COMPONENT_ID = "src_12842" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_BinomialTheorem"
FIXED_DOMAIN_KEY = "discrete.combinations"
DOMAIN_OPERATION = "binomial_expansion"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.combinations', 'required_capabilities': ['binomial_expansion'], 'domain_operation': 'binomial_expansion', 'problem_type_id': 'binomial_expansion', 'presentation_mode': 'short_answer', 'answer_type': 'expression', 'generation_constraints': {'variants': [{'a': 1, 'b': 1, 'n': 4, 'vars': ['x', 'y']}, {'a': 1, 'b': -1, 'n': 5, 'vars': ['a', 'b']}, {'a': 1, 'b': -1, 'n': 3, 'vars': ['a', 'b']}, {'a': 1, 'b': -1, 'n': 4, 'vars': ['p', 'q']}, {'a': 1, 'b': -1, 'n': 6, 'vars': ['a', 'b']}, {'a': 1, 'b': -1, 'n': 5, 'vars': ['p', 'q']}, {'a': 1, 'b': -1, 'n': 3, 'vars': ['x', 'y']}, {'a': 1, 'b': -1, 'n': 4, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 5, 'vars': ['x', 'y']}, {'a': 1, 'b': 1, 'n': 4, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 3, 'vars': ['x', 'y']}, {'a': 1, 'b': 1, 'n': 6, 'vars': ['x', 'y']}, {'a': 1, 'b': 1, 'n': 3, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 6, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 5, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 5, 'vars': ['p', 'q']}, {'a': 1, 'b': -1, 'n': 3, 'vars': ['p', 'q']}, {'a': 1, 'b': -1, 'n': 6, 'vars': ['x', 'y']}, {'a': 1, 'b': 1, 'n': 3, 'vars': ['p', 'q']}, {'a': 1, 'b': 1, 'n': 6, 'vars': ['p', 'q']}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.combinations', 'required_capabilities': ['binomial_expansion'], 'domain_operation': 'binomial_expansion', 'problem_type_id': 'binomial_expansion', 'presentation_mode': 'short_answer', 'answer_type': 'expression', 'generation_constraints': {'variants': [{'a': 1, 'b': 1, 'n': 4, 'vars': ['x', 'y']}, {'a': 1, 'b': -1, 'n': 5, 'vars': ['a', 'b']}, {'a': 1, 'b': -1, 'n': 3, 'vars': ['a', 'b']}, {'a': 1, 'b': -1, 'n': 4, 'vars': ['p', 'q']}, {'a': 1, 'b': -1, 'n': 6, 'vars': ['a', 'b']}, {'a': 1, 'b': -1, 'n': 5, 'vars': ['p', 'q']}, {'a': 1, 'b': -1, 'n': 3, 'vars': ['x', 'y']}, {'a': 1, 'b': -1, 'n': 4, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 5, 'vars': ['x', 'y']}, {'a': 1, 'b': 1, 'n': 4, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 3, 'vars': ['x', 'y']}, {'a': 1, 'b': 1, 'n': 6, 'vars': ['x', 'y']}, {'a': 1, 'b': 1, 'n': 3, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 6, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 5, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 5, 'vars': ['p', 'q']}, {'a': 1, 'b': -1, 'n': 3, 'vars': ['p', 'q']}, {'a': 1, 'b': -1, 'n': 6, 'vars': ['x', 'y']}, {'a': 1, 'b': 1, 'n': 3, 'vars': ['p', 'q']}, {'a': 1, 'b': 1, 'n': 6, 'vars': ['p', 'q']}]}}, 'problem_type_id': 'binomial_expansion', 'required_capabilities': ['binomial_expansion'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'a': 1, 'b': 1, 'n': 4, 'vars': ['x', 'y']}, {'a': 1, 'b': -1, 'n': 5, 'vars': ['a', 'b']}, {'a': 1, 'b': -1, 'n': 3, 'vars': ['a', 'b']}, {'a': 1, 'b': -1, 'n': 4, 'vars': ['p', 'q']}, {'a': 1, 'b': -1, 'n': 6, 'vars': ['a', 'b']}, {'a': 1, 'b': -1, 'n': 5, 'vars': ['p', 'q']}, {'a': 1, 'b': -1, 'n': 3, 'vars': ['x', 'y']}, {'a': 1, 'b': -1, 'n': 4, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 5, 'vars': ['x', 'y']}, {'a': 1, 'b': 1, 'n': 4, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 3, 'vars': ['x', 'y']}, {'a': 1, 'b': 1, 'n': 6, 'vars': ['x', 'y']}, {'a': 1, 'b': 1, 'n': 3, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 6, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 5, 'vars': ['a', 'b']}, {'a': 1, 'b': 1, 'n': 5, 'vars': ['p', 'q']}, {'a': 1, 'b': -1, 'n': 3, 'vars': ['p', 'q']}, {'a': 1, 'b': -1, 'n': 6, 'vars': ['x', 'y']}, {'a': 1, 'b': 1, 'n': 3, 'vars': ['p', 'q']}, {'a': 1, 'b': 1, 'n': 6, 'vars': ['p', 'q']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_BinomialTheorem', 'fixed_domain_key': 'discrete.combinations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['binomial_expansion'], 'matched_capabilities': ['binomial_expansion'], 'selected_operation': 'binomial_expansion', 'registry_revision': 'promoted-848b2241bfec', 'domain_module': 'core.domain.promoted.combinations.combinations_domain', 'entrypoint': 'build_combinations_matrix', 'allowed_operations': ['at_least_k_selection', 'binomial_expansion', 'binomial_sum_bound', 'coefficient_solve_parameter', 'combination_claim', 'general_term_coefficient', 'radical_binomial_power'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_BinomialTheorem'}), seed)
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
