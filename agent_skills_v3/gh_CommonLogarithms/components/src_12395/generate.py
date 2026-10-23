from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice_label"
PROBLEM_TYPE_ID = "evaluate_exponent_statement_truth"
TEXTBOOK_EXAMPLE_ID = 12395
DEFAULT_COMPONENT_ID = "src_12395" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_CommonLogarithms"
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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'statements': [{'lhs': ['n', '7'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '7']]]}]}, {'statements': [{'lhs': ['log', ['pow', ['n', '10'], ['n', '89']]], 'rhs': ['n', '89']}]}, {'statements': [{'lhs': ['n', '99'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '103']]]}]}, {'statements': [{'lhs': ['n', '99'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '104']]]}]}, {'statements': [{'lhs': ['log', ['pow', ['n', '10'], ['n', '44']]], 'rhs': ['n', '45']}]}, {'statements': [{'lhs': ['n', '5'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '5']]]}]}, {'statements': [{'lhs': ['n', '74'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '79']]]}]}, {'statements': [{'lhs': ['n', '11'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '14']]]}]}, {'statements': [{'lhs': ['log', ['pow', ['n', '10'], ['n', '21']]], 'rhs': ['n', '21']}]}, {'statements': [{'lhs': ['n', '8'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '8']]]}]}, {'statements': [{'lhs': ['n', '91'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '94']]]}]}, {'statements': [{'lhs': ['log', ['pow', ['n', '10'], ['n', '63']]], 'rhs': ['n', '64']}]}, {'statements': [{'lhs': ['n', '19'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '19']]]}]}, {'statements': [{'lhs': ['n', '20'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '25']]]}]}, {'statements': [{'lhs': ['n', '48'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '48']]]}]}, {'statements': [{'lhs': ['n', '85'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '85']]]}]}, {'statements': [{'lhs': ['n', '41'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '44']]]}]}, {'statements': [{'lhs': ['log', ['pow', ['n', '10'], ['n', '45']]], 'rhs': ['n', '46']}]}, {'statements': [{'lhs': ['n', '33'], 'rhs': ['pow', ['n', '10'], ['log', ['n', '38']]]}]}, {'statements': [{'lhs': ['log', ['pow', ['n', '10'], ['n', '7']]], 'rhs': ['n', '7']}]}]}}), seed)
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
