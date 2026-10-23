from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "evaluate_scientific_notation_expression"
TEXTBOOK_EXAMPLE_ID = 12383
DEFAULT_COMPONENT_ID = "src_12383" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_ScientificNotationAndItsOperations"
FIXED_DOMAIN_KEY = "algebra.exponent_laws"
DOMAIN_OPERATION = "evaluate_scientific_notation_expression"


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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem': '已知太陽到地球的平均距離為149597870.7公里。', 'items': [{'kind': 'value', 'value': '149597870.7', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '149597870.7', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為535713475.1公里。', 'items': [{'kind': 'value', 'value': '535713475.1', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '535713475.1', 'sig': 4, 'prompt': '將此平均距離取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為451222596.8公里。', 'items': [{'kind': 'value', 'value': '451222596.8', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '451222596.8', 'sig': 4, 'prompt': '將此平均距離取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為87474043.3公里。', 'items': [{'kind': 'value', 'value': '87474043.3', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '87474043.3', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為721218885.2公里。', 'items': [{'kind': 'value', 'value': '721218885.2', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '721218885.2', 'sig': 4, 'prompt': '將此平均距離取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為925007515.8公里。', 'items': [{'kind': 'value', 'value': '925007515.8', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '925007515.8', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為275873497.9公里。', 'items': [{'kind': 'value', 'value': '275873497.9', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '275873497.9', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為672579558.2公里。', 'items': [{'kind': 'value', 'value': '672579558.2', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '672579558.2', 'sig': 4, 'prompt': '將此平均距離取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為287130668.8公里。', 'items': [{'kind': 'value', 'value': '287130668.8', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '287130668.8', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為387310664.6公里。', 'items': [{'kind': 'value', 'value': '387310664.6', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '387310664.6', 'sig': 4, 'prompt': '將此平均距離取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為751276811.2公里。', 'items': [{'kind': 'value', 'value': '751276811.2', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '751276811.2', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為872379358.3公里。', 'items': [{'kind': 'value', 'value': '872379358.3', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '872379358.3', 'sig': 4, 'prompt': '將此平均距離取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為162314197.5公里。', 'items': [{'kind': 'value', 'value': '162314197.5', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '162314197.5', 'sig': 4, 'prompt': '將此平均距離取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為48882522.1公里。', 'items': [{'kind': 'value', 'value': '48882522.1', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '48882522.1', 'sig': 4, 'prompt': '將此平均距離取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為225974164.8公里。', 'items': [{'kind': 'value', 'value': '225974164.8', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '225974164.8', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為233525168.7公里。', 'items': [{'kind': 'value', 'value': '233525168.7', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '233525168.7', 'sig': 4, 'prompt': '將此平均距離取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為303433711.3公里。', 'items': [{'kind': 'value', 'value': '303433711.3', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '303433711.3', 'sig': 4, 'prompt': '將此平均距離取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為992562038.8公里。', 'items': [{'kind': 'value', 'value': '992562038.8', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '992562038.8', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為576655738.5公里。', 'items': [{'kind': 'value', 'value': '576655738.5', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '576655738.5', 'sig': 3, 'prompt': '將此平均距離取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知太陽到地球的平均距離為539830919.2公里。', 'items': [{'kind': 'value', 'value': '539830919.2', 'sig': 2, 'prompt': '將此平均距離取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '539830919.2', 'sig': 4, 'prompt': '將此平均距離取 $4$ 位有效數字並以科學記號表示。'}]}]}}), seed)
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
