from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "binomial_sum_bound"
TEXTBOOK_EXAMPLE_ID = 12841
DEFAULT_COMPONENT_ID = "src_12841" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_BinomialTheorem"
FIXED_DOMAIN_KEY = "discrete.combinations"
DOMAIN_OPERATION = "binomial_sum_bound"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.combinations', 'required_capabilities': ['binomial_sum_bound'], 'domain_operation': 'binomial_sum_bound', 'problem_type_id': 'binomial_sum_bound', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'low': 1000, 'high': 1200, 'start': 1}, {'low': 7000, 'high': 13600, 'start': 0}, {'low': 900, 'high': 1700, 'start': 1}, {'low': 6400, 'high': 11000, 'start': 1}, {'low': 5300, 'high': 13000, 'start': 0}, {'low': 80, 'high': 220, 'start': 1}, {'low': 500, 'high': 950, 'start': 0}, {'low': 190, 'high': 330, 'start': 0}, {'low': 3400, 'high': 4900, 'start': 1}, {'low': 50, 'high': 80, 'start': 1}, {'low': 600, 'high': 1500, 'start': 0}, {'low': 180, 'high': 350, 'start': 1}, {'low': 400, 'high': 620, 'start': 1}, {'low': 3500, 'high': 5600, 'start': 1}, {'low': 2700, 'high': 7600, 'start': 0}, {'low': 13400, 'high': 32600, 'start': 0}, {'low': 50, 'high': 100, 'start': 1}, {'low': 50, 'high': 110, 'start': 1}, {'low': 110, 'high': 240, 'start': 1}, {'low': 7900, 'high': 8600, 'start': 1}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.combinations', 'required_capabilities': ['binomial_sum_bound'], 'domain_operation': 'binomial_sum_bound', 'problem_type_id': 'binomial_sum_bound', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'low': 1000, 'high': 1200, 'start': 1}, {'low': 7000, 'high': 13600, 'start': 0}, {'low': 900, 'high': 1700, 'start': 1}, {'low': 6400, 'high': 11000, 'start': 1}, {'low': 5300, 'high': 13000, 'start': 0}, {'low': 80, 'high': 220, 'start': 1}, {'low': 500, 'high': 950, 'start': 0}, {'low': 190, 'high': 330, 'start': 0}, {'low': 3400, 'high': 4900, 'start': 1}, {'low': 50, 'high': 80, 'start': 1}, {'low': 600, 'high': 1500, 'start': 0}, {'low': 180, 'high': 350, 'start': 1}, {'low': 400, 'high': 620, 'start': 1}, {'low': 3500, 'high': 5600, 'start': 1}, {'low': 2700, 'high': 7600, 'start': 0}, {'low': 13400, 'high': 32600, 'start': 0}, {'low': 50, 'high': 100, 'start': 1}, {'low': 50, 'high': 110, 'start': 1}, {'low': 110, 'high': 240, 'start': 1}, {'low': 7900, 'high': 8600, 'start': 1}]}}, 'problem_type_id': 'binomial_sum_bound', 'required_capabilities': ['binomial_sum_bound'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'low': 1000, 'high': 1200, 'start': 1}, {'low': 7000, 'high': 13600, 'start': 0}, {'low': 900, 'high': 1700, 'start': 1}, {'low': 6400, 'high': 11000, 'start': 1}, {'low': 5300, 'high': 13000, 'start': 0}, {'low': 80, 'high': 220, 'start': 1}, {'low': 500, 'high': 950, 'start': 0}, {'low': 190, 'high': 330, 'start': 0}, {'low': 3400, 'high': 4900, 'start': 1}, {'low': 50, 'high': 80, 'start': 1}, {'low': 600, 'high': 1500, 'start': 0}, {'low': 180, 'high': 350, 'start': 1}, {'low': 400, 'high': 620, 'start': 1}, {'low': 3500, 'high': 5600, 'start': 1}, {'low': 2700, 'high': 7600, 'start': 0}, {'low': 13400, 'high': 32600, 'start': 0}, {'low': 50, 'high': 100, 'start': 1}, {'low': 50, 'high': 110, 'start': 1}, {'low': 110, 'high': 240, 'start': 1}, {'low': 7900, 'high': 8600, 'start': 1}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_BinomialTheorem', 'fixed_domain_key': 'discrete.combinations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['binomial_sum_bound'], 'matched_capabilities': ['binomial_sum_bound'], 'selected_operation': 'binomial_sum_bound', 'registry_revision': 'promoted-848b2241bfec', 'domain_module': 'core.domain.promoted.combinations.combinations_domain', 'entrypoint': 'build_combinations_matrix', 'allowed_operations': ['at_least_k_selection', 'binomial_expansion', 'binomial_sum_bound', 'coefficient_solve_parameter', 'combination_claim', 'general_term_coefficient', 'radical_binomial_power'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_BinomialTheorem'}), seed)
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
