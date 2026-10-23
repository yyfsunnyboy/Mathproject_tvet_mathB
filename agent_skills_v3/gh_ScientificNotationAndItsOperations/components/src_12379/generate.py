from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "evaluate_scientific_notation_expression"
TEXTBOOK_EXAMPLE_ID = 12379
DEFAULT_COMPONENT_ID = "src_12379" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem': '已知太陽的體積約為 $1.41\\times 10^{18}$ 立方公里，且地球的體積約為 $1.08\\times 10^{12}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '1.41'], ['pow', ['n', '10'], ['n', '18']]], ['mul', ['n', '1.08'], ['pow', ['n', '10'], ['n', '12']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $3.5\\times 10^{19}$ 立方公里，且地球的體積約為 $9.0\\times 10^{8}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '3.5'], ['pow', ['n', '10'], ['n', '19']]], ['mul', ['n', '9.0'], ['pow', ['n', '10'], ['n', '8']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $7.5\\times 10^{16}$ 立方公里，且地球的體積約為 $8.1\\times 10^{11}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '7.5'], ['pow', ['n', '10'], ['n', '16']]], ['mul', ['n', '8.1'], ['pow', ['n', '10'], ['n', '11']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $5.3\\times 10^{16}$ 立方公里，且地球的體積約為 $5.2\\times 10^{12}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '5.3'], ['pow', ['n', '10'], ['n', '16']]], ['mul', ['n', '5.2'], ['pow', ['n', '10'], ['n', '12']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $6.3\\times 10^{15}$ 立方公里，且地球的體積約為 $2.0\\times 10^{13}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '6.3'], ['pow', ['n', '10'], ['n', '15']]], ['mul', ['n', '2.0'], ['pow', ['n', '10'], ['n', '13']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $1.8\\times 10^{16}$ 立方公里，且地球的體積約為 $9.5\\times 10^{9}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '1.8'], ['pow', ['n', '10'], ['n', '16']]], ['mul', ['n', '9.5'], ['pow', ['n', '10'], ['n', '9']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $3.5\\times 10^{17}$ 立方公里，且地球的體積約為 $7.5\\times 10^{8}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '3.5'], ['pow', ['n', '10'], ['n', '17']]], ['mul', ['n', '7.5'], ['pow', ['n', '10'], ['n', '8']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $8.5\\times 10^{20}$ 立方公里，且地球的體積約為 $6.9\\times 10^{12}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '8.5'], ['pow', ['n', '10'], ['n', '20']]], ['mul', ['n', '6.9'], ['pow', ['n', '10'], ['n', '12']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $2.7\\times 10^{19}$ 立方公里，且地球的體積約為 $8.3\\times 10^{12}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '2.7'], ['pow', ['n', '10'], ['n', '19']]], ['mul', ['n', '8.3'], ['pow', ['n', '10'], ['n', '12']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $6.1\\times 10^{17}$ 立方公里，且地球的體積約為 $3.5\\times 10^{9}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '6.1'], ['pow', ['n', '10'], ['n', '17']]], ['mul', ['n', '3.5'], ['pow', ['n', '10'], ['n', '9']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $4.1\\times 10^{16}$ 立方公里，且地球的體積約為 $8.7\\times 10^{12}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '4.1'], ['pow', ['n', '10'], ['n', '16']]], ['mul', ['n', '8.7'], ['pow', ['n', '10'], ['n', '12']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $5.3\\times 10^{19}$ 立方公里，且地球的體積約為 $1.3\\times 10^{10}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '5.3'], ['pow', ['n', '10'], ['n', '19']]], ['mul', ['n', '1.3'], ['pow', ['n', '10'], ['n', '10']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $7.2\\times 10^{15}$ 立方公里，且地球的體積約為 $5.3\\times 10^{8}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '7.2'], ['pow', ['n', '10'], ['n', '15']]], ['mul', ['n', '5.3'], ['pow', ['n', '10'], ['n', '8']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $2.7\\times 10^{19}$ 立方公里，且地球的體積約為 $2.9\\times 10^{8}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '2.7'], ['pow', ['n', '10'], ['n', '19']]], ['mul', ['n', '2.9'], ['pow', ['n', '10'], ['n', '8']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $9.7\\times 10^{14}$ 立方公里，且地球的體積約為 $4.2\\times 10^{8}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '9.7'], ['pow', ['n', '10'], ['n', '14']]], ['mul', ['n', '4.2'], ['pow', ['n', '10'], ['n', '8']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $9.1\\times 10^{19}$ 立方公里，且地球的體積約為 $9.8\\times 10^{8}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '9.1'], ['pow', ['n', '10'], ['n', '19']]], ['mul', ['n', '9.8'], ['pow', ['n', '10'], ['n', '8']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $9.1\\times 10^{18}$ 立方公里，且地球的體積約為 $4.2\\times 10^{8}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '9.1'], ['pow', ['n', '10'], ['n', '18']]], ['mul', ['n', '4.2'], ['pow', ['n', '10'], ['n', '8']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $2.9\\times 10^{18}$ 立方公里，且地球的體積約為 $9.4\\times 10^{10}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '2.9'], ['pow', ['n', '10'], ['n', '18']]], ['mul', ['n', '9.4'], ['pow', ['n', '10'], ['n', '10']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $6.0\\times 10^{16}$ 立方公里，且地球的體積約為 $9.3\\times 10^{12}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '6.0'], ['pow', ['n', '10'], ['n', '16']]], ['mul', ['n', '9.3'], ['pow', ['n', '10'], ['n', '12']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '已知太陽的體積約為 $1.6\\times 10^{14}$ 立方公里，且地球的體積約為 $6.9\\times 10^{10}$ 立方公里，試問：太陽的體積為地球的幾倍？（將答案取 $2$ 位有效數字並以科學記號表示。）', 'items': [{'kind': 'expr', 'tree': ['div', ['mul', ['n', '1.6'], ['pow', ['n', '10'], ['n', '14']]], ['mul', ['n', '6.9'], ['pow', ['n', '10'], ['n', '10']]]], 'sig': 2, 'show_expr': False}]}]}}), seed)
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
