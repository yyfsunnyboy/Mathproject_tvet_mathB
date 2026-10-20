from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "evaluate_conditional_exponent_values"
TEXTBOOK_EXAMPLE_ID = 12349
DEFAULT_COMPONENT_ID = "src_12349" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_IntegerExponentsAndLaws"
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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '2']}, 'roots': ['(2 + sqrt(8))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '24']}, 'roots': ['(24 + sqrt(580))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '31']}, 'roots': ['(31 + sqrt(965))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '23']}, 'roots': ['(23 + sqrt(533))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '5']}, 'roots': ['(5 + sqrt(29))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '16']}, 'roots': ['(16 + sqrt(260))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '10']}, 'roots': ['(10 + sqrt(104))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '39']}, 'roots': ['(39 + sqrt(1525))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '13']}, 'roots': ['(13 + sqrt(173))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '25']}, 'roots': ['(25 + sqrt(629))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '38']}, 'roots': ['(38 + sqrt(1448))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '40']}, 'roots': ['(40 + sqrt(1604))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '36']}, 'roots': ['(36 + sqrt(1300))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '34']}, 'roots': ['(34 + sqrt(1160))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '8']}, 'roots': ['(8 + sqrt(68))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '4']}, 'roots': ['(4 + sqrt(20))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '21']}, 'roots': ['(21 + sqrt(445))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '18']}, 'roots': ['(18 + sqrt(328))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '35']}, 'roots': ['(35 + sqrt(1229))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['sub', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '32']}, 'roots': ['(32 + sqrt(1028))/2'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '2']], ['pow', ['sym', 'a'], ['n', '-2']]], ['add', ['pow', ['sym', 'a'], ['n', '4']], ['pow', ['sym', 'a'], ['n', '-4']]]], 'assume_positive': True}]}}), seed)
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
