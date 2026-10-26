from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "geometric_from_terms"
TEXTBOOK_EXAMPLE_ID = 12674
DEFAULT_COMPONENT_ID = "src_12674" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_Sequence"
FIXED_DOMAIN_KEY = "sequence.progression"
DOMAIN_OPERATION = "geometric_from_terms"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'sequence.progression', 'required_capabilities': ['geometric_from_terms'], 'domain_operation': 'geometric_from_terms', 'problem_type_id': 'geometric_from_terms', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'style': 'list', 'terms': ['3', '-6', '12'], 'ask_k': 5, 'target': -384}, {'style': 'list', 'terms': ['2', '-6', '18'], 'ask_k': 6, 'target': '1458'}, {'style': 'list', 'terms': ['768', '-384', '192'], 'ask_k': 6, 'target': '12'}, {'style': 'list', 'terms': ['2', '4', '8'], 'ask_k': 5, 'target': '128'}, {'style': 'list', 'terms': ['5', '20', '80'], 'ask_k': 6, 'target': '81920'}, {'style': 'list', 'terms': ['2', '-4', '8'], 'ask_k': 6, 'target': '32'}, {'style': 'list', 'terms': ['2', '-4', '8'], 'ask_k': 4, 'target': '-64'}, {'style': 'list', 'terms': ['2', '-4', '8'], 'ask_k': 4, 'target': '32'}, {'style': 'list', 'terms': ['3', '-9', '27'], 'ask_k': 4, 'target': '243'}, {'style': 'list', 'terms': ['1', '-4', '16'], 'ask_k': 4, 'target': '4096'}, {'style': 'list', 'terms': ['1', '-2', '4'], 'ask_k': 5, 'target': '64'}, {'style': 'list', 'terms': ['2', '6', '18'], 'ask_k': 6, 'target': '486'}, {'style': 'list', 'terms': ['3', '-12', '48'], 'ask_k': 6, 'target': '768'}, {'style': 'list', 'terms': ['4', '-12', '36'], 'ask_k': 5, 'target': '2916'}, {'style': 'list', 'terms': ['-3', '-6', '-12'], 'ask_k': 6, 'target': '-48'}, {'style': 'list', 'terms': ['2', '6', '18'], 'ask_k': 4, 'target': '4374'}, {'style': 'list', 'terms': ['5', '15', '45'], 'ask_k': 6, 'target': '10935'}, {'style': 'list', 'terms': ['-2', '-8', '-32'], 'ask_k': 4, 'target': '-8192'}, {'style': 'list', 'terms': ['1536', '-768', '384'], 'ask_k': 5, 'target': '-12'}, {'style': 'list', 'terms': ['1', '-3', '9'], 'ask_k': 4, 'target': '729'}]}}, 'phase1_classification': {'fixed_domain_key': 'sequence.progression', 'required_capabilities': ['geometric_from_terms'], 'domain_operation': 'geometric_from_terms', 'problem_type_id': 'geometric_from_terms', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'style': 'list', 'terms': ['3', '-6', '12'], 'ask_k': 5, 'target': -384}, {'style': 'list', 'terms': ['2', '-6', '18'], 'ask_k': 6, 'target': '1458'}, {'style': 'list', 'terms': ['768', '-384', '192'], 'ask_k': 6, 'target': '12'}, {'style': 'list', 'terms': ['2', '4', '8'], 'ask_k': 5, 'target': '128'}, {'style': 'list', 'terms': ['5', '20', '80'], 'ask_k': 6, 'target': '81920'}, {'style': 'list', 'terms': ['2', '-4', '8'], 'ask_k': 6, 'target': '32'}, {'style': 'list', 'terms': ['2', '-4', '8'], 'ask_k': 4, 'target': '-64'}, {'style': 'list', 'terms': ['2', '-4', '8'], 'ask_k': 4, 'target': '32'}, {'style': 'list', 'terms': ['3', '-9', '27'], 'ask_k': 4, 'target': '243'}, {'style': 'list', 'terms': ['1', '-4', '16'], 'ask_k': 4, 'target': '4096'}, {'style': 'list', 'terms': ['1', '-2', '4'], 'ask_k': 5, 'target': '64'}, {'style': 'list', 'terms': ['2', '6', '18'], 'ask_k': 6, 'target': '486'}, {'style': 'list', 'terms': ['3', '-12', '48'], 'ask_k': 6, 'target': '768'}, {'style': 'list', 'terms': ['4', '-12', '36'], 'ask_k': 5, 'target': '2916'}, {'style': 'list', 'terms': ['-3', '-6', '-12'], 'ask_k': 6, 'target': '-48'}, {'style': 'list', 'terms': ['2', '6', '18'], 'ask_k': 4, 'target': '4374'}, {'style': 'list', 'terms': ['5', '15', '45'], 'ask_k': 6, 'target': '10935'}, {'style': 'list', 'terms': ['-2', '-8', '-32'], 'ask_k': 4, 'target': '-8192'}, {'style': 'list', 'terms': ['1536', '-768', '384'], 'ask_k': 5, 'target': '-12'}, {'style': 'list', 'terms': ['1', '-3', '9'], 'ask_k': 4, 'target': '729'}]}}, 'problem_type_id': 'geometric_from_terms', 'required_capabilities': ['geometric_from_terms'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'style': 'list', 'terms': ['3', '-6', '12'], 'ask_k': 5, 'target': -384}, {'style': 'list', 'terms': ['2', '-6', '18'], 'ask_k': 6, 'target': '1458'}, {'style': 'list', 'terms': ['768', '-384', '192'], 'ask_k': 6, 'target': '12'}, {'style': 'list', 'terms': ['2', '4', '8'], 'ask_k': 5, 'target': '128'}, {'style': 'list', 'terms': ['5', '20', '80'], 'ask_k': 6, 'target': '81920'}, {'style': 'list', 'terms': ['2', '-4', '8'], 'ask_k': 6, 'target': '32'}, {'style': 'list', 'terms': ['2', '-4', '8'], 'ask_k': 4, 'target': '-64'}, {'style': 'list', 'terms': ['2', '-4', '8'], 'ask_k': 4, 'target': '32'}, {'style': 'list', 'terms': ['3', '-9', '27'], 'ask_k': 4, 'target': '243'}, {'style': 'list', 'terms': ['1', '-4', '16'], 'ask_k': 4, 'target': '4096'}, {'style': 'list', 'terms': ['1', '-2', '4'], 'ask_k': 5, 'target': '64'}, {'style': 'list', 'terms': ['2', '6', '18'], 'ask_k': 6, 'target': '486'}, {'style': 'list', 'terms': ['3', '-12', '48'], 'ask_k': 6, 'target': '768'}, {'style': 'list', 'terms': ['4', '-12', '36'], 'ask_k': 5, 'target': '2916'}, {'style': 'list', 'terms': ['-3', '-6', '-12'], 'ask_k': 6, 'target': '-48'}, {'style': 'list', 'terms': ['2', '6', '18'], 'ask_k': 4, 'target': '4374'}, {'style': 'list', 'terms': ['5', '15', '45'], 'ask_k': 6, 'target': '10935'}, {'style': 'list', 'terms': ['-2', '-8', '-32'], 'ask_k': 4, 'target': '-8192'}, {'style': 'list', 'terms': ['1536', '-768', '384'], 'ask_k': 5, 'target': '-12'}, {'style': 'list', 'terms': ['1', '-3', '9'], 'ask_k': 4, 'target': '729'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_Sequence', 'fixed_domain_key': 'sequence.progression', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['geometric_from_terms'], 'matched_capabilities': ['geometric_from_terms'], 'selected_operation': 'geometric_from_terms', 'registry_revision': 'promoted-9863553f3bfd', 'domain_module': 'core.domain.promoted.sequence_progression.sequence_progression_domain', 'entrypoint': 'build_sequence_progression_matrix', 'allowed_operations': ['arithmetic_from_terms', 'geometric_from_relations', 'geometric_from_terms', 'progression_three_numbers', 'sequence_statements', 'sequence_terms_from_formula'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_Sequence'}), seed)
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
