from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "numeric_or_radical"
PROBLEM_TYPE_ID = "evaluate_conditional_exponent_values"
TEXTBOOK_EXAMPLE_ID = 12353
DEFAULT_COMPONENT_ID = "src_12353" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RationalExponentsAndLaws"
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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '4']}, 'roots': ['((4 + (1)*sqrt(12))/2)', '((4 + (-1)*sqrt(12))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '21']}, 'roots': ['((21 + (1)*sqrt(437))/2)', '((21 + (-1)*sqrt(437))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '10']}, 'roots': ['((10 + (1)*sqrt(96))/2)', '((10 + (-1)*sqrt(96))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '3']}, 'roots': ['((3 + (1)*sqrt(5))/2)', '((3 + (-1)*sqrt(5))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '14']}, 'roots': ['((14 + (1)*sqrt(192))/2)', '((14 + (-1)*sqrt(192))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '17']}, 'roots': ['((17 + (1)*sqrt(285))/2)', '((17 + (-1)*sqrt(285))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '8']}, 'roots': ['((8 + (1)*sqrt(60))/2)', '((8 + (-1)*sqrt(60))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '20']}, 'roots': ['((20 + (1)*sqrt(396))/2)', '((20 + (-1)*sqrt(396))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '22']}, 'roots': ['((22 + (1)*sqrt(480))/2)', '((22 + (-1)*sqrt(480))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '5']}, 'roots': ['((5 + (1)*sqrt(21))/2)', '((5 + (-1)*sqrt(21))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '15']}, 'roots': ['((15 + (1)*sqrt(221))/2)', '((15 + (-1)*sqrt(221))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '7']}, 'roots': ['((7 + (1)*sqrt(45))/2)', '((7 + (-1)*sqrt(45))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '19']}, 'roots': ['((19 + (1)*sqrt(357))/2)', '((19 + (-1)*sqrt(357))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '13']}, 'roots': ['((13 + (1)*sqrt(165))/2)', '((13 + (-1)*sqrt(165))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '18']}, 'roots': ['((18 + (1)*sqrt(320))/2)', '((18 + (-1)*sqrt(320))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '12']}, 'roots': ['((12 + (1)*sqrt(140))/2)', '((12 + (-1)*sqrt(140))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '16']}, 'roots': ['((16 + (1)*sqrt(252))/2)', '((16 + (-1)*sqrt(252))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '6']}, 'roots': ['((6 + (1)*sqrt(32))/2)', '((6 + (-1)*sqrt(32))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '9']}, 'roots': ['((9 + (1)*sqrt(77))/2)', '((9 + (-1)*sqrt(77))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}, {'stem_prefix': '已知 $a>0$ 且 ', 'var': 'a', 'condition': {'lhs': ['add', ['sym', 'a'], ['pow', ['sym', 'a'], ['n', '-1']]], 'rhs': ['n', '11']}, 'roots': ['((11 + (1)*sqrt(117))/2)', '((11 + (-1)*sqrt(117))/2)'], 'targets': [['add', ['pow', ['sym', 'a'], ['n', '1/2']], ['pow', ['sym', 'a'], ['n', '-1/2']]]], 'assume_positive': True}]}}), seed)
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
