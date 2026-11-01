"""L2 production rule: unwrap json.dumps around return correct_answer.

Rule id: L2_CORRECT_ANSWER_JSON_DUMPS_UNWRAP

Status: production_approved (held-out 52-cell no-op regression passed).

Research positioning
--------------------
Contract-shape structural repair (type/wrapping only).

Detects ``correct_answer: json.dumps(<expr>)`` in the generate() return dict
and replaces it with ``correct_answer: <expr>``. The CE115 generator contract
requires ``correct_answer`` to be a JSON-compatible object (dict), not a
serialized string; ``json.dumps`` always yields ``str``.

Does NOT:
- reference task_id / exam numerics / candidate-specific snippets in guards
- read oracle / correct_answer values / evaluator outcomes to decide acceptance
- invent or rewrite the inner expression
"""

from __future__ import annotations

import ast
from typing import Any, Mapping

RULE_ID = "L2_CORRECT_ANSWER_JSON_DUMPS_UNWRAP"
LAYER = "L2"
PRIORITY = 120
PRODUCTION_APPROVED = True
STATUS = "production_approved"


def _generate_fn(tree: ast.AST) -> ast.FunctionDef | None:
    gens = [
        n
        for n in getattr(tree, "body", [])
        if isinstance(n, ast.FunctionDef) and n.name == "generate"
    ]
    return gens[0] if len(gens) == 1 else None


def _is_json_name(node: ast.AST) -> bool:
    return isinstance(node, ast.Name) and node.id == "json"


def _match_json_dumps_call(node: ast.AST) -> ast.AST | None:
    """Return inner expression if node is json.dumps(<expr>) with no kwargs or only ensure_ascii."""
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if not (
        isinstance(func, ast.Attribute)
        and func.attr == "dumps"
        and _is_json_name(func.value)
    ):
        return None
    if len(node.args) != 1:
        return None
    for kw in node.keywords:
        if kw.arg not in {"ensure_ascii", "indent", "sort_keys"}:
            return None
        # allow only constant kwargs (structural; values unused for transform)
        if not isinstance(kw.value, ast.Constant):
            return None
    return node.args[0]


def _return_dict(fn: ast.FunctionDef) -> ast.Dict | None:
    for stmt in reversed(fn.body):
        if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Dict):
            return stmt.value
    return None


def _correct_answer_entry(ret: ast.Dict) -> tuple[ast.AST | None, ast.AST | None, int | None]:
    for i, (k, v) in enumerate(zip(ret.keys, ret.values)):
        if isinstance(k, ast.Constant) and k.value == "correct_answer":
            return k, v, i
    return None, None, None


def _has_import_json(tree: ast.AST) -> bool:
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Import):
            if any(alias.name == "json" for alias in node.names):
                return True
        if isinstance(node, ast.ImportFrom) and node.module == "json":
            return True
    return False


def _node_abs_span(source: str, node: ast.AST) -> tuple[int, int]:
    if getattr(node, "lineno", None) is None or getattr(node, "end_lineno", None) is None:
        raise ValueError("AST node lacks source location")
    lines = source.splitlines(keepends=True)
    start = sum(len(lines[i]) for i in range(node.lineno - 1)) + node.col_offset
    end = sum(len(lines[i]) for i in range(node.end_lineno - 1)) + node.end_col_offset
    return start, end


def analyze_json_dumps_unwrap(source: str) -> dict[str, Any]:
    guards: dict[str, Any] = {
        "parse_ok": False,
        "single_generate": False,
        "return_dict_present": False,
        "correct_answer_present": False,
        "correct_answer_is_json_dumps": False,
        "dumps_single_positional_arg": False,
        "dumps_kwargs_allowed_only": False,
        "import_json_present": False,
        "inner_expr_kind": None,
    }

    try:
        tree = ast.parse(source)
        guards["parse_ok"] = True
    except SyntaxError as exc:
        return {
            "guards": guards,
            "applicable": False,
            "triggered": False,
            "reason": f"parse_error:{exc}",
        }

    fn = _generate_fn(tree)
    guards["single_generate"] = fn is not None
    if fn is None:
        return {
            "guards": guards,
            "applicable": False,
            "triggered": False,
            "reason": "generate_missing_or_ambiguous",
        }

    ret = _return_dict(fn)
    guards["return_dict_present"] = ret is not None
    if ret is None:
        return {
            "guards": guards,
            "applicable": False,
            "triggered": False,
            "reason": "return_dict_missing",
        }

    _k, value, idx = _correct_answer_entry(ret)
    guards["correct_answer_present"] = value is not None
    if value is None:
        return {
            "guards": guards,
            "applicable": False,
            "triggered": False,
            "reason": "correct_answer_missing",
        }

    guards["import_json_present"] = _has_import_json(tree)

    inner = _match_json_dumps_call(value)
    if inner is None:
        # Not applicable unless the dumps-wrap pattern is present (structure-gated).
        return {
            "guards": guards,
            "applicable": False,
            "triggered": False,
            "reason": "correct_answer_not_json_dumps_call",
            "dumps_node": value,
            "entry_index": idx,
        }

    guards["correct_answer_is_json_dumps"] = True
    guards["dumps_single_positional_arg"] = True
    guards["dumps_kwargs_allowed_only"] = True
    guards["inner_expr_kind"] = type(inner).__name__
    applicable = bool(
        guards["parse_ok"]
        and guards["single_generate"]
        and guards["return_dict_present"]
        and guards["correct_answer_present"]
        and guards["correct_answer_is_json_dumps"]
    )

    if not guards["import_json_present"]:
        return {
            "guards": guards,
            "applicable": applicable,
            "triggered": False,
            "reason": "json_import_missing",
            "dumps_node": value,
            "inner": inner,
            "entry_index": idx,
        }

    return {
        "guards": guards,
        "applicable": applicable,
        "triggered": True,
        "reason": "all_transform_guards_ready",
        "dumps_node": value,
        "inner": inner,
        "entry_index": idx,
    }


def is_applicable(source: str, context: Mapping[str, Any]) -> tuple[bool, Mapping[str, Any], str]:
    del context  # structural rule; context unused
    analysis = analyze_json_dumps_unwrap(source)
    return bool(analysis["applicable"]), dict(analysis["guards"]), str(analysis["reason"])


def is_triggered(source: str, context: Mapping[str, Any]) -> tuple[bool, str]:
    del context
    analysis = analyze_json_dumps_unwrap(source)
    if not analysis["applicable"]:
        return False, str(analysis["reason"])
    return bool(analysis["triggered"]), str(analysis["reason"])


def apply(source: str, context: Mapping[str, Any]) -> tuple[str, Mapping[str, Any], str]:
    del context
    analysis = analyze_json_dumps_unwrap(source)
    validation: dict[str, Any] = {
        "rule_id": RULE_ID,
        "production_approved": PRODUCTION_APPROVED,
        "status": STATUS,
        "research_positioning": "contract-shape structural repair (unwrap stringified correct_answer)",
        "oracle_assisted": False,
        "oracle_free_claimed": True,
    }
    if not analysis.get("triggered"):
        return source, validation, f"apply_skipped:{analysis['reason']}"

    dumps_node: ast.AST = analysis["dumps_node"]
    inner: ast.AST = analysis["inner"]

    try:
        start, end = _node_abs_span(source, dumps_node)
        inner_src = ast.get_source_segment(source, inner)
        if inner_src is None:
            validation["reparse_ok"] = False
            return source, validation, "inner_source_segment_missing_rollback"
        new_source = source[:start] + inner_src + source[end:]
    except ValueError as exc:
        validation["reparse_ok"] = False
        validation["span_error"] = str(exc)
        return source, validation, "span_failed_rollback"

    try:
        new_tree = ast.parse(new_source)
        validation["reparse_ok"] = True
    except SyntaxError as exc:
        validation["reparse_ok"] = False
        validation["reparse_error"] = str(exc)
        return source, validation, "reparse_failed_rollback"

    # Post-condition: correct_answer must no longer be json.dumps(...)
    post = analyze_json_dumps_unwrap(new_source)
    if post.get("triggered"):
        validation["post_unwrap_clean"] = False
        return source, validation, "post_condition_still_dumps_rollback"
    validation["post_unwrap_clean"] = True

    # Ensure return still has correct_answer entry
    fn = _generate_fn(new_tree)
    ret = _return_dict(fn) if fn else None
    _k, value, _i = _correct_answer_entry(ret) if ret else (None, None, None)
    if value is None:
        validation["correct_answer_present_after"] = False
        return source, validation, "correct_answer_lost_rollback"
    validation["correct_answer_present_after"] = True
    validation["inner_expr_kind"] = analysis["guards"]["inner_expr_kind"]
    validation["unwrapped_to"] = ast.dump(value, include_attributes=False)
    return new_source, validation, "unwrapped_json_dumps_correct_answer"
