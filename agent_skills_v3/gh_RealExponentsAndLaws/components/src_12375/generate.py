from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "evaluate_conditional_exponent_values"
TEXTBOOK_EXAMPLE_ID = 12375
DEFAULT_COMPONENT_ID = "src_12375" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RealExponentsAndLaws"
FIXED_DOMAIN_KEY = "algebra.exponent_laws"
DOMAIN_OPERATION = "evaluate_conditional_exponent_values"


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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '3']}, 'roots': ['log((3 + (1)*sqrt(5))/2)/log(2)', 'log((3 + (-1)*sqrt(5))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '22']}, 'roots': ['log((22 + (1)*sqrt(480))/2)/log(2)', 'log((22 + (-1)*sqrt(480))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '14']}, 'roots': ['log((14 + (1)*sqrt(192))/2)/log(2)', 'log((14 + (-1)*sqrt(192))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '20']}, 'roots': ['log((20 + (1)*sqrt(396))/2)/log(2)', 'log((20 + (-1)*sqrt(396))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '18']}, 'roots': ['log((18 + (1)*sqrt(320))/2)/log(2)', 'log((18 + (-1)*sqrt(320))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '17']}, 'roots': ['log((17 + (1)*sqrt(285))/2)/log(2)', 'log((17 + (-1)*sqrt(285))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '15']}, 'roots': ['log((15 + (1)*sqrt(221))/2)/log(2)', 'log((15 + (-1)*sqrt(221))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '16']}, 'roots': ['log((16 + (1)*sqrt(252))/2)/log(2)', 'log((16 + (-1)*sqrt(252))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '13']}, 'roots': ['log((13 + (1)*sqrt(165))/2)/log(2)', 'log((13 + (-1)*sqrt(165))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '5']}, 'roots': ['log((5 + (1)*sqrt(21))/2)/log(2)', 'log((5 + (-1)*sqrt(21))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '4']}, 'roots': ['log((4 + (1)*sqrt(12))/2)/log(2)', 'log((4 + (-1)*sqrt(12))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '11']}, 'roots': ['log((11 + (1)*sqrt(117))/2)/log(2)', 'log((11 + (-1)*sqrt(117))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '21']}, 'roots': ['log((21 + (1)*sqrt(437))/2)/log(2)', 'log((21 + (-1)*sqrt(437))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '10']}, 'roots': ['log((10 + (1)*sqrt(96))/2)/log(2)', 'log((10 + (-1)*sqrt(96))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '9']}, 'roots': ['log((9 + (1)*sqrt(77))/2)/log(2)', 'log((9 + (-1)*sqrt(77))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '8']}, 'roots': ['log((8 + (1)*sqrt(60))/2)/log(2)', 'log((8 + (-1)*sqrt(60))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '19']}, 'roots': ['log((19 + (1)*sqrt(357))/2)/log(2)', 'log((19 + (-1)*sqrt(357))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '7']}, 'roots': ['log((7 + (1)*sqrt(45))/2)/log(2)', 'log((7 + (-1)*sqrt(45))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '6']}, 'roots': ['log((6 + (1)*sqrt(32))/2)/log(2)', 'log((6 + (-1)*sqrt(32))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}, {'stem_prefix': '已知 ', 'var': 'a', 'condition': {'lhs': ['add', ['pow', ['n', '2'], ['sym', 'a']], ['pow', ['n', '2'], ['neg', ['sym', 'a']]]], 'rhs': ['n', '12']}, 'roots': ['log((12 + (1)*sqrt(140))/2)/log(2)', 'log((12 + (-1)*sqrt(140))/2)/log(2)'], 'targets': [['add', ['pow', ['n', '4'], ['sym', 'a']], ['pow', ['n', '4'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['n', '8'], ['sym', 'a']], ['pow', ['n', '8'], ['neg', ['sym', 'a']]]], ['add', ['pow', ['sqrt', ['n', '2']], ['sym', 'a']], ['pow', ['sqrt', ['n', '2']], ['neg', ['sym', 'a']]]]], 'assume_positive': False}]}}), seed)
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
