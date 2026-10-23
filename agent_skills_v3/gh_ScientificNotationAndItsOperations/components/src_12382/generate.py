from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "evaluate_scientific_notation_expression"
TEXTBOOK_EXAMPLE_ID = 12382
DEFAULT_COMPONENT_ID = "src_12382" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem': '亞洲是世界上最大的洲，其面積約為 $4.46\\times 10^{7}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $8.54\\times 10^{6}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '4.46'], ['pow', ['n', '10'], ['n', '7']]], ['mul', ['n', '8.54'], ['pow', ['n', '10'], ['n', '6']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $8.77\\times 10^{9}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $4.14\\times 10^{8}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '8.77'], ['pow', ['n', '10'], ['n', '9']]], ['mul', ['n', '4.14'], ['pow', ['n', '10'], ['n', '8']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $5.36\\times 10^{8}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $5.90\\times 10^{7}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '5.36'], ['pow', ['n', '10'], ['n', '8']]], ['mul', ['n', '5.90'], ['pow', ['n', '10'], ['n', '7']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $9.06\\times 10^{8}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $2.25\\times 10^{7}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '9.06'], ['pow', ['n', '10'], ['n', '8']]], ['mul', ['n', '2.25'], ['pow', ['n', '10'], ['n', '7']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $8.96\\times 10^{8}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $8.84\\times 10^{7}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '8.96'], ['pow', ['n', '10'], ['n', '8']]], ['mul', ['n', '8.84'], ['pow', ['n', '10'], ['n', '7']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $6.60\\times 10^{7}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $9.14\\times 10^{6}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '6.60'], ['pow', ['n', '10'], ['n', '7']]], ['mul', ['n', '9.14'], ['pow', ['n', '10'], ['n', '6']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $5.46\\times 10^{7}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $4.54\\times 10^{6}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '5.46'], ['pow', ['n', '10'], ['n', '7']]], ['mul', ['n', '4.54'], ['pow', ['n', '10'], ['n', '6']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $4.01\\times 10^{9}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $7.42\\times 10^{8}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '4.01'], ['pow', ['n', '10'], ['n', '9']]], ['mul', ['n', '7.42'], ['pow', ['n', '10'], ['n', '8']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $4.44\\times 10^{8}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $4.03\\times 10^{7}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '4.44'], ['pow', ['n', '10'], ['n', '8']]], ['mul', ['n', '4.03'], ['pow', ['n', '10'], ['n', '7']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $8.44\\times 10^{9}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $6.46\\times 10^{8}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '8.44'], ['pow', ['n', '10'], ['n', '9']]], ['mul', ['n', '6.46'], ['pow', ['n', '10'], ['n', '8']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $3.78\\times 10^{6}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $6.36\\times 10^{5}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '3.78'], ['pow', ['n', '10'], ['n', '6']]], ['mul', ['n', '6.36'], ['pow', ['n', '10'], ['n', '5']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $6.08\\times 10^{6}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $9.41\\times 10^{5}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '6.08'], ['pow', ['n', '10'], ['n', '6']]], ['mul', ['n', '9.41'], ['pow', ['n', '10'], ['n', '5']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $5.75\\times 10^{8}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $3.99\\times 10^{7}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '5.75'], ['pow', ['n', '10'], ['n', '8']]], ['mul', ['n', '3.99'], ['pow', ['n', '10'], ['n', '7']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $3.11\\times 10^{9}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $3.30\\times 10^{8}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '3.11'], ['pow', ['n', '10'], ['n', '9']]], ['mul', ['n', '3.30'], ['pow', ['n', '10'], ['n', '8']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $3.58\\times 10^{8}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $1.92\\times 10^{7}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '3.58'], ['pow', ['n', '10'], ['n', '8']]], ['mul', ['n', '1.92'], ['pow', ['n', '10'], ['n', '7']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $9.66\\times 10^{6}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $6.87\\times 10^{5}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '9.66'], ['pow', ['n', '10'], ['n', '6']]], ['mul', ['n', '6.87'], ['pow', ['n', '10'], ['n', '5']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $3.68\\times 10^{7}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $2.92\\times 10^{6}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '3.68'], ['pow', ['n', '10'], ['n', '7']]], ['mul', ['n', '2.92'], ['pow', ['n', '10'], ['n', '6']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $4.89\\times 10^{7}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $6.42\\times 10^{6}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '4.89'], ['pow', ['n', '10'], ['n', '7']]], ['mul', ['n', '6.42'], ['pow', ['n', '10'], ['n', '6']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $6.29\\times 10^{7}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $3.45\\times 10^{6}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '6.29'], ['pow', ['n', '10'], ['n', '7']]], ['mul', ['n', '3.45'], ['pow', ['n', '10'], ['n', '6']]]], 'sig': 2, 'show_expr': False}]}, {'stem': '亞洲是世界上最大的洲，其面積約為 $4.84\\times 10^{7}$ 平方公里；大洋洲是世界上最小的洲，其面積約為 $4.56\\times 10^{6}$ 平方公里。試問：亞洲的面積比大洋洲大多少？（將答案取 $2$ 位有效數字並以科學記號表示）', 'items': [{'kind': 'expr', 'tree': ['sub', ['mul', ['n', '4.84'], ['pow', ['n', '10'], ['n', '7']]], ['mul', ['n', '4.56'], ['pow', ['n', '10'], ['n', '6']]]], 'sig': 2, 'show_expr': False}]}]}}), seed)
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
