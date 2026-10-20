from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "evaluate_exponent_statement_truth"
TEXTBOOK_EXAMPLE_ID = 12364
DEFAULT_COMPONENT_ID = "src_12364" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RationalExponentsAndLaws"
FIXED_DOMAIN_KEY = "algebra.exponent_laws"
DOMAIN_OPERATION = "evaluate_exponent_statement_truth"


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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '10']], 'rhs': ['n', '8']}, {'lhs': ['pow', ['sym', 'b'], ['n', '30']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['n', '2'], ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '2']]], 'rhs': ['pow', ['n', '2'], ['n', '1.32']]}, {'lhs': ['div', ['sym', 'a'], ['jux', ['n', '2'], ['sym', 'b']]], 'rhs': ['pow', ['n', '2'], ['n', '0.28']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.3']], 'b': ['pow', ['n', '2'], ['n', '0.01']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '5']], 'rhs': ['pow', ['n', '2'], ['n', '2.5']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '25']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '1']]], 'rhs': ['pow', ['n', '2'], ['n', '0.52']]}, {'lhs': ['div', ['sym', 'a'], ['sym', 'b']], 'rhs': ['pow', ['n', '2'], ['n', '0.48']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.5']], 'b': ['pow', ['n', '2'], ['n', '0.02']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '5']], 'rhs': ['pow', ['n', '2'], ['n', '1.5']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '10']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '2']]], 'rhs': ['pow', ['n', '2'], ['n', '0.38']]}, {'lhs': ['div', ['sym', 'a'], ['sym', 'b']], 'rhs': ['pow', ['n', '2'], ['n', '0.26']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.3']], 'b': ['pow', ['n', '2'], ['n', '0.04']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '10']], 'rhs': ['pow', ['n', '2'], ['n', '5.5']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '25']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '2']]], 'rhs': ['pow', ['n', '2'], ['n', '0.55']]}, {'lhs': ['div', ['sym', 'a'], ['sym', 'b']], 'rhs': ['pow', ['n', '2'], ['n', '0.48']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.5']], 'b': ['pow', ['n', '2'], ['n', '0.02']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '20']], 'rhs': ['pow', ['n', '2'], ['n', '12.5']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '30']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['n', '2'], ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '1']]], 'rhs': ['pow', ['n', '2'], ['n', '1.63']]}, {'lhs': ['div', ['sym', 'a'], ['jux', ['n', '2'], ['sym', 'b']]], 'rhs': ['pow', ['n', '2'], ['n', '-0.42']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.6']], 'b': ['pow', ['n', '2'], ['n', '0.02']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '20']], 'rhs': ['pow', ['n', '2'], ['n', '6']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '6']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['n', '2'], ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '1']]], 'rhs': ['pow', ['n', '2'], ['n', '1.35']]}, {'lhs': ['div', ['sym', 'a'], ['jux', ['n', '2'], ['sym', 'b']]], 'rhs': ['pow', ['n', '2'], ['n', '-0.75']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.3']], 'b': ['pow', ['n', '2'], ['n', '0.05']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '5']], 'rhs': ['pow', ['n', '2'], ['n', '2.5']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '40']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['n', '2'], ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '3']]], 'rhs': ['pow', ['n', '2'], ['n', '1.44']]}, {'lhs': ['div', ['sym', 'a'], ['jux', ['n', '2'], ['sym', 'b']]], 'rhs': ['pow', ['n', '2'], ['n', '-0.61']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.4']], 'b': ['pow', ['n', '2'], ['n', '0.01']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '20']], 'rhs': ['pow', ['n', '2'], ['n', '4.5']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '10']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['n', '2'], ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '1']]], 'rhs': ['pow', ['n', '2'], ['n', '1.23']]}, {'lhs': ['div', ['sym', 'a'], ['jux', ['n', '2'], ['sym', 'b']]], 'rhs': ['pow', ['n', '2'], ['n', '-0.82']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.2']], 'b': ['pow', ['n', '2'], ['n', '0.02']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '5']], 'rhs': ['pow', ['n', '2'], ['n', '4.5']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '40']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '3']]], 'rhs': ['pow', ['n', '2'], ['n', '0.87']]}, {'lhs': ['div', ['sym', 'a'], ['sym', 'b']], 'rhs': ['pow', ['n', '2'], ['n', '0.78']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.8']], 'b': ['pow', ['n', '2'], ['n', '0.02']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '20']], 'rhs': ['pow', ['n', '2'], ['n', '4']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '10']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '2']]], 'rhs': ['pow', ['n', '2'], ['n', '0.24']]}, {'lhs': ['div', ['sym', 'a'], ['sym', 'b']], 'rhs': ['pow', ['n', '2'], ['n', '0.18']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.2']], 'b': ['pow', ['n', '2'], ['n', '0.02']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '20']], 'rhs': ['pow', ['n', '2'], ['n', '12']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '15']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['n', '2'], ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '1']]], 'rhs': ['pow', ['n', '2'], ['n', '1.64']]}, {'lhs': ['div', ['sym', 'a'], ['jux', ['n', '2'], ['sym', 'b']]], 'rhs': ['pow', ['n', '2'], ['n', '-0.44']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.6']], 'b': ['pow', ['n', '2'], ['n', '0.04']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '5']], 'rhs': ['pow', ['n', '2'], ['n', '4.5']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '20']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '1']]], 'rhs': ['pow', ['n', '2'], ['n', '0.85']]}, {'lhs': ['div', ['sym', 'a'], ['sym', 'b']], 'rhs': ['pow', ['n', '2'], ['n', '0.76']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.8']], 'b': ['pow', ['n', '2'], ['n', '0.04']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '10']], 'rhs': ['pow', ['n', '2'], ['n', '5.5']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '25']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['n', '2'], ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '3']]], 'rhs': ['pow', ['n', '2'], ['n', '1.57']]}, {'lhs': ['div', ['sym', 'a'], ['jux', ['n', '2'], ['sym', 'b']]], 'rhs': ['pow', ['n', '2'], ['n', '-0.52']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.5']], 'b': ['pow', ['n', '2'], ['n', '0.02']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '10']], 'rhs': ['pow', ['n', '2'], ['n', '7.5']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '35']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '1']]], 'rhs': ['pow', ['n', '2'], ['n', '0.73']]}, {'lhs': ['div', ['sym', 'a'], ['sym', 'b']], 'rhs': ['pow', ['n', '2'], ['n', '0.68']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.7']], 'b': ['pow', ['n', '2'], ['n', '0.02']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '4']], 'rhs': ['pow', ['n', '2'], ['n', '2.4']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '15']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['n', '2'], ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '2']]], 'rhs': ['pow', ['n', '2'], ['n', '1.68']]}, {'lhs': ['div', ['sym', 'a'], ['jux', ['n', '2'], ['sym', 'b']]], 'rhs': ['pow', ['n', '2'], ['n', '-0.44']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.6']], 'b': ['pow', ['n', '2'], ['n', '0.04']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '5']], 'rhs': ['pow', ['n', '2'], ['n', '4']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '16']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '1']]], 'rhs': ['pow', ['n', '2'], ['n', '0.85']]}, {'lhs': ['div', ['sym', 'a'], ['sym', 'b']], 'rhs': ['pow', ['n', '2'], ['n', '0.75']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.8']], 'b': ['pow', ['n', '2'], ['n', '0.05']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '4']], 'rhs': ['pow', ['n', '2'], ['n', '2.9']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '15']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['n', '2'], ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '3']]], 'rhs': ['pow', ['n', '2'], ['n', '1.73']]}, {'lhs': ['div', ['sym', 'a'], ['jux', ['n', '2'], ['sym', 'b']]], 'rhs': ['pow', ['n', '2'], ['n', '-0.44']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.6']], 'b': ['pow', ['n', '2'], ['n', '0.04']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '5']], 'rhs': ['pow', ['n', '2'], ['n', '2']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '10']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '1']]], 'rhs': ['pow', ['n', '2'], ['n', '0.35']]}, {'lhs': ['div', ['sym', 'a'], ['sym', 'b']], 'rhs': ['pow', ['n', '2'], ['n', '0.26']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.3']], 'b': ['pow', ['n', '2'], ['n', '0.04']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '20']], 'rhs': ['pow', ['n', '2'], ['n', '18.5']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '10']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['n', '2'], ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '3']]], 'rhs': ['pow', ['n', '2'], ['n', '2.03']]}, {'lhs': ['div', ['sym', 'a'], ['jux', ['n', '2'], ['sym', 'b']]], 'rhs': ['pow', ['n', '2'], ['n', '-0.14']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.9']], 'b': ['pow', ['n', '2'], ['n', '0.04']]}}, {'statements': [{'lhs': ['pow', ['sym', 'a'], ['n', '5']], 'rhs': ['pow', ['n', '2'], ['n', '2']]}, {'lhs': ['pow', ['sym', 'b'], ['n', '20']], 'rhs': ['sym', 'a']}, {'lhs': ['jux', ['n', '2'], ['sym', 'a'], ['pow', ['sym', 'b'], ['n', '2']]], 'rhs': ['pow', ['n', '2'], ['n', '1.44']]}, {'lhs': ['div', ['sym', 'a'], ['jux', ['n', '2'], ['sym', 'b']]], 'rhs': ['pow', ['n', '2'], ['n', '-0.62']]}], 'definitions': {'a': ['pow', ['n', '2'], ['n', '0.4']], 'b': ['pow', ['n', '2'], ['n', '0.02']]}}]}}), seed)
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
