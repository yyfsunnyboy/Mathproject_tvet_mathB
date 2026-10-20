from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice_label"
PROBLEM_TYPE_ID = "evaluate_exponent_statement_truth"
TEXTBOOK_EXAMPLE_ID = 12360
DEFAULT_COMPONENT_ID = "src_12360" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'statements': [{'lhs': ['pow', ['n', '5'], ['n', '-2/3']], 'rhs': ['div', ['n', '1'], ['root', 3, ['n', '25']]]}]}, {'statements': [{'lhs': ['pow', ['n', '7'], ['n', '-2/3']], 'rhs': ['root', 3, ['pow', ['n', '7'], ['n', '-2']]]}]}, {'statements': [{'lhs': ['pow', ['n', '7'], ['n', '-1/2']], 'rhs': ['div', ['n', '1'], ['root', 2, ['pow', ['n', '7'], ['n', '1']]]]}]}, {'statements': [{'lhs': ['pow', ['n', '7'], ['n', '-1/3']], 'rhs': ['div', ['n', '1'], ['root', 3, ['pow', ['n', '7'], ['n', '1']]]]}]}, {'statements': [{'lhs': ['pow', ['n', '7'], ['n', '-2/3']], 'rhs': ['div', ['n', '1'], ['root', 3, ['pow', ['n', '7'], ['n', '2']]]]}]}, {'statements': [{'lhs': ['pow', ['n', '7'], ['n', '-2/5']], 'rhs': ['div', ['n', '1'], ['root', 2, ['pow', ['n', '7'], ['n', '5']]]]}]}, {'statements': [{'lhs': ['pow', ['n', '5'], ['n', '-2/3']], 'rhs': ['root', 3, ['pow', ['n', '5'], ['n', '-2']]]}]}, {'statements': [{'lhs': ['pow', ['n', '3'], ['n', '-3/4']], 'rhs': ['div', ['n', '1'], ['root', 3, ['pow', ['n', '3'], ['n', '4']]]]}]}, {'statements': [{'lhs': ['pow', ['n', '2'], ['n', '-3/4']], 'rhs': ['root', 4, ['pow', ['n', '2'], ['n', '-3']]]}]}, {'statements': [{'lhs': ['pow', ['n', '2'], ['n', '-2/5']], 'rhs': ['neg', ['root', 5, ['pow', ['n', '2'], ['n', '2']]]]}]}, {'statements': [{'lhs': ['pow', ['n', '2'], ['n', '-1/2']], 'rhs': ['neg', ['root', 2, ['pow', ['n', '2'], ['n', '1']]]]}]}, {'statements': [{'lhs': ['pow', ['n', '3'], ['n', '-3/4']], 'rhs': ['div', ['n', '1'], ['root', 4, ['pow', ['n', '3'], ['n', '3']]]]}]}, {'statements': [{'lhs': ['pow', ['n', '2'], ['n', '-1/3']], 'rhs': ['root', 3, ['pow', ['n', '2'], ['n', '-1']]]}]}, {'statements': [{'lhs': ['pow', ['n', '3'], ['n', '-1/3']], 'rhs': ['neg', ['root', 3, ['pow', ['n', '3'], ['n', '1']]]]}]}, {'statements': [{'lhs': ['pow', ['n', '3'], ['n', '-2/3']], 'rhs': ['div', ['n', '1'], ['root', 3, ['pow', ['n', '3'], ['n', '2']]]]}]}, {'statements': [{'lhs': ['pow', ['n', '3'], ['n', '-2/5']], 'rhs': ['div', ['n', '1'], ['root', 5, ['pow', ['n', '3'], ['n', '2']]]]}]}, {'statements': [{'lhs': ['pow', ['n', '5'], ['n', '-2/5']], 'rhs': ['root', 5, ['pow', ['n', '5'], ['n', '-2']]]}]}, {'statements': [{'lhs': ['pow', ['n', '3'], ['n', '-2/3']], 'rhs': ['root', 3, ['pow', ['n', '3'], ['n', '-2']]]}]}, {'statements': [{'lhs': ['pow', ['n', '7'], ['n', '-1/3']], 'rhs': ['div', ['n', '1'], ['root', 1, ['pow', ['n', '7'], ['n', '3']]]]}]}, {'statements': [{'lhs': ['pow', ['n', '2'], ['n', '-2/3']], 'rhs': ['div', ['n', '1'], ['root', 2, ['pow', ['n', '2'], ['n', '3']]]]}]}]}}), seed)
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
