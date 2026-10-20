from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "solve_exponent_blank_equations"
TEXTBOOK_EXAMPLE_ID = 12341
DEFAULT_COMPONENT_ID = "src_12341" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PositiveIntegerExponentsAndLaws"
FIXED_DOMAIN_KEY = "algebra.exponent_laws"
DOMAIN_OPERATION = "solve_exponent_blank_equations"


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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['-3', 4], ['-3', 5]], 'result_base': '-3'}, {'kind': 'power_power', 'base': '2', 'inner': 4, 'outer': None, 'result_base': '2', 'result_exp': 20}, {'kind': 'merge_bases', 'factors': [['2', 10], ['-3', 5]], 'common_exponent': 5}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['2', 2], ['2', 4]], 'result_base': '2'}, {'kind': 'power_power', 'base': '3', 'inner': 3, 'outer': None, 'result_base': '3', 'result_exp': 18}, {'kind': 'merge_bases', 'factors': [['2', 12], ['-5', 4]], 'common_exponent': 4}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['-5', 2], ['-5', 4]], 'result_base': '-5'}, {'kind': 'power_power', 'base': '5', 'inner': 4, 'outer': None, 'result_base': '5', 'result_exp': 12}, {'kind': 'merge_bases', 'factors': [['5', 6], ['-7', 3]], 'common_exponent': 3}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['3', 5], ['3', 6]], 'result_base': '3'}, {'kind': 'power_power', 'base': '5', 'inner': 4, 'outer': None, 'result_base': '5', 'result_exp': 36}, {'kind': 'merge_bases', 'factors': [['2', 4], ['-7', 4]], 'common_exponent': 4}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['-2', 7], ['-2', 5]], 'result_base': '-2'}, {'kind': 'power_power', 'base': '2', 'inner': 2, 'outer': None, 'result_base': '2', 'result_exp': 12}, {'kind': 'merge_bases', 'factors': [['5', 6], ['-2', 3]], 'common_exponent': 3}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['2', 2], ['2', 4]], 'result_base': '2'}, {'kind': 'power_power', 'base': '5', 'inner': 4, 'outer': None, 'result_base': '5', 'result_exp': 24}, {'kind': 'merge_bases', 'factors': [['3', 3], ['-7', 3]], 'common_exponent': 3}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['2', 3], ['2', 5]], 'result_base': '2'}, {'kind': 'power_power', 'base': '2', 'inner': 3, 'outer': None, 'result_base': '2', 'result_exp': 21}, {'kind': 'merge_bases', 'factors': [['3', 12], ['-7', 4]], 'common_exponent': 4}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['3', 4], ['3', 6]], 'result_base': '3'}, {'kind': 'power_power', 'base': '2', 'inner': 2, 'outer': None, 'result_base': '2', 'result_exp': 8}, {'kind': 'merge_bases', 'factors': [['2', 9], ['-7', 3]], 'common_exponent': 3}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['-5', 4], ['-5', 5]], 'result_base': '-5'}, {'kind': 'power_power', 'base': '3', 'inner': 4, 'outer': None, 'result_base': '3', 'result_exp': 16}, {'kind': 'merge_bases', 'factors': [['2', 4], ['-7', 4]], 'common_exponent': 4}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['-5', 2], ['-5', 2]], 'result_base': '-5'}, {'kind': 'power_power', 'base': '2', 'inner': 2, 'outer': None, 'result_base': '2', 'result_exp': 16}, {'kind': 'merge_bases', 'factors': [['2', 12], ['-3', 4]], 'common_exponent': 4}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['5', 2], ['5', 3]], 'result_base': '5'}, {'kind': 'power_power', 'base': '5', 'inner': 4, 'outer': None, 'result_base': '5', 'result_exp': 36}, {'kind': 'merge_bases', 'factors': [['5', 6], ['3', 3]], 'common_exponent': 3}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['-2', 4], ['-2', 6]], 'result_base': '-2'}, {'kind': 'power_power', 'base': '3', 'inner': 2, 'outer': None, 'result_base': '3', 'result_exp': 6}, {'kind': 'merge_bases', 'factors': [['2', 5], ['-7', 5]], 'common_exponent': 5}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['-3', 6], ['-3', 2]], 'result_base': '-3'}, {'kind': 'power_power', 'base': '5', 'inner': 4, 'outer': None, 'result_base': '5', 'result_exp': 12}, {'kind': 'merge_bases', 'factors': [['5', 10], ['-3', 5]], 'common_exponent': 5}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['2', 7], ['2', 7]], 'result_base': '2'}, {'kind': 'power_power', 'base': '2', 'inner': 2, 'outer': None, 'result_base': '2', 'result_exp': 10}, {'kind': 'merge_bases', 'factors': [['5', 4], ['-7', 4]], 'common_exponent': 4}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['-3', 6], ['-3', 4]], 'result_base': '-3'}, {'kind': 'power_power', 'base': '3', 'inner': 3, 'outer': None, 'result_base': '3', 'result_exp': 9}, {'kind': 'merge_bases', 'factors': [['3', 5], ['-2', 5]], 'common_exponent': 5}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['-3', 4], ['-3', 7]], 'result_base': '-3'}, {'kind': 'power_power', 'base': '5', 'inner': 2, 'outer': None, 'result_base': '5', 'result_exp': 16}, {'kind': 'merge_bases', 'factors': [['5', 4], ['-3', 4]], 'common_exponent': 4}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['2', 4], ['2', 7]], 'result_base': '2'}, {'kind': 'power_power', 'base': '2', 'inner': 3, 'outer': None, 'result_base': '2', 'result_exp': 18}, {'kind': 'merge_bases', 'factors': [['2', 12], ['3', 4]], 'common_exponent': 4}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['3', 6], ['3', 4]], 'result_base': '3'}, {'kind': 'power_power', 'base': '5', 'inner': 3, 'outer': None, 'result_base': '5', 'result_exp': 9}, {'kind': 'merge_bases', 'factors': [['3', 6], ['-2', 3]], 'common_exponent': 3}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['3', 5], ['3', 4]], 'result_base': '3'}, {'kind': 'power_power', 'base': '5', 'inner': 3, 'outer': None, 'result_base': '5', 'result_exp': 24}, {'kind': 'merge_bases', 'factors': [['2', 15], ['-7', 5]], 'common_exponent': 5}]}, {'stem': '利用指數律完成下列填空：', 'items': [{'kind': 'product_to_base', 'factors': [['3', 2], ['3', 7]], 'result_base': '3'}, {'kind': 'power_power', 'base': '5', 'inner': 3, 'outer': None, 'result_base': '5', 'result_exp': 12}, {'kind': 'merge_bases', 'factors': [['5', 6], ['-2', 3]], 'common_exponent': 3}]}]}}), seed)
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
