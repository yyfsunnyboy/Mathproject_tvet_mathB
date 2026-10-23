from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "evaluate_scientific_notation_expression"
TEXTBOOK_EXAMPLE_ID = 12380
DEFAULT_COMPONENT_ID = "src_12380" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem': '流感病毒的直徑約為 $100$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-7}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '100'], ['pow', ['n', '10'], ['n', '-7']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $369$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-8}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '369'], ['pow', ['n', '10'], ['n', '-8']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $918$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-8}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '918'], ['pow', ['n', '10'], ['n', '-8']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $786$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-6}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '786'], ['pow', ['n', '10'], ['n', '-6']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $138$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-8}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '138'], ['pow', ['n', '10'], ['n', '-8']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $204$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-9}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '204'], ['pow', ['n', '10'], ['n', '-9']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $932$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-6}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '932'], ['pow', ['n', '10'], ['n', '-6']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $770$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-8}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '770'], ['pow', ['n', '10'], ['n', '-8']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $698$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-8}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '698'], ['pow', ['n', '10'], ['n', '-8']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $916$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-9}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '916'], ['pow', ['n', '10'], ['n', '-9']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $192$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-7}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '192'], ['pow', ['n', '10'], ['n', '-7']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $783$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-9}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '783'], ['pow', ['n', '10'], ['n', '-9']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $534$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-7}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '534'], ['pow', ['n', '10'], ['n', '-7']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $394$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-9}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '394'], ['pow', ['n', '10'], ['n', '-9']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $677$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-7}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '677'], ['pow', ['n', '10'], ['n', '-7']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $389$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-6}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '389'], ['pow', ['n', '10'], ['n', '-6']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $895$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-9}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '895'], ['pow', ['n', '10'], ['n', '-9']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $937$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-6}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '937'], ['pow', ['n', '10'], ['n', '-6']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $443$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-9}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '443'], ['pow', ['n', '10'], ['n', '-9']]], 'sig': 3, 'show_expr': False}]}, {'stem': '流感病毒的直徑約為 $440$ 奈米（3位有效數字）且 $1$ 奈米等於 $10^{-6}$ 公分，問：將其以科學記號表示時為多少公分？', 'items': [{'kind': 'expr', 'tree': ['mul', ['n', '440'], ['pow', ['n', '10'], ['n', '-6']]], 'sig': 3, 'show_expr': False}]}]}}), seed)
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
