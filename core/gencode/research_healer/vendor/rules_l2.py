"""L2 allowlist rule: frozen-oracle-assisted deterministic structural repair (H3).

Rule id: L2_SINGLE_KEY_ORACLE_PAYLOAD_WRAP

Research positioning
--------------------
This is a **frozen-oracle-assisted deterministic structural repair**.
It reads frozen parameter key/value(s) from the evaluation context to wrap a
bare scalar ``oracle_payload`` into ``{frozen_key: scalar}``.

It is **not** oracle-free. Do not claim "no oracle contamination".
Evidence is limited to the single approved fixture
``fail_radical_ab1_l2`` (schema_failure → passed) and must not be
generalized without new adjudicated cases.

Does not call legacy healer pipelines and does not touch other AST nodes.
"""

from __future__ import annotations

import ast
from typing import Any, Mapping

RULE_ID = "L2_SINGLE_KEY_ORACLE_PAYLOAD_WRAP"
LAYER = "L2"
PRIORITY = 100

_SCALAR_TYPES = (int, float, bool, str, type(None))


def _is_scalar(value: Any) -> bool:
    return isinstance(value, _SCALAR_TYPES)


def _generate_fn(tree: ast.AST) -> ast.FunctionDef | None:
    gens = [
        n
        for n in getattr(tree, "body", [])
        if isinstance(n, ast.FunctionDef) and n.name == "generate"
    ]
    return gens[0] if len(gens) == 1 else None


def _assignments_in_generate(fn: ast.FunctionDef) -> dict[str, ast.AST]:
    """Map name -> last assigned value expr in generate() top-level body only."""
    assigns: dict[str, ast.AST] = {}
    for stmt in fn.body:
        if not isinstance(stmt, ast.Assign):
            continue
        if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
            continue
        assigns[stmt.targets[0].id] = stmt.value
    return assigns


def _const_value(node: ast.AST) -> Any | object:
    if isinstance(node, ast.Constant) and _is_scalar(node.value):
        return node.value
    return _MISSING


_MISSING = object()


def _resolve_scalar(
    expr: ast.AST,
    *,
    assigns: Mapping[str, ast.AST],
    frozen_key: str,
    frozen_value: Any,
    _seen: set[str] | None = None,
) -> Any | object:
    """Statically resolve *expr* to a scalar, or return _MISSING."""
    direct = _const_value(expr)
    if direct is not _MISSING:
        return direct

    if isinstance(expr, ast.Name):
        seen = set() if _seen is None else _seen
        if expr.id in seen:
            return _MISSING
        seen = set(seen)
        seen.add(expr.id)
        assigned = assigns.get(expr.id)
        if assigned is None:
            return _MISSING
        return _resolve_scalar(
            assigned,
            assigns=assigns,
            frozen_key=frozen_key,
            frozen_value=frozen_value,
            _seen=seen,
        )

    # kwargs.get("frozen_key"[, default]) or kwargs["frozen_key"]
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute):
        if (
            isinstance(expr.func.value, ast.Name)
            and expr.func.value.id == "kwargs"
            and expr.func.attr == "get"
            and expr.args
            and isinstance(expr.args[0], ast.Constant)
            and expr.args[0].value == frozen_key
        ):
            if len(expr.args) >= 2:
                default = _const_value(expr.args[1])
                if default is _MISSING:
                    return _MISSING
                if default != frozen_value:
                    return _MISSING
            return frozen_value if _is_scalar(frozen_value) else _MISSING

    if isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Name):
        if expr.value.id == "kwargs":
            sl = expr.slice
            if isinstance(sl, ast.Constant) and sl.value == frozen_key:
                return frozen_value if _is_scalar(frozen_value) else _MISSING

    return _MISSING


def _return_dict(fn: ast.FunctionDef) -> ast.Dict | None:
    """Return the dict literal of the final ``return {.. }`` in generate(), if any."""
    for stmt in reversed(fn.body):
        if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Dict):
            return stmt.value
        if isinstance(stmt, ast.If):
            # ignore complex control flow for H3
            continue
    return None


def _dict_entry(d: ast.Dict, key_name: str) -> tuple[ast.AST | None, ast.AST | None, int | None]:
    for idx, (k, v) in enumerate(zip(d.keys, d.values)):
        if isinstance(k, ast.Constant) and k.value == key_name:
            return k, v, idx
    return None, None, None


def _already_wrapped(value: ast.AST, frozen_key: str, scalar: Any) -> bool:
    if not isinstance(value, ast.Dict) or len(value.keys) != 1:
        return False
    k, v = value.keys[0], value.values[0]
    return (
        isinstance(k, ast.Constant)
        and k.value == frozen_key
        and isinstance(v, ast.Constant)
        and v.value == scalar
    )


def _correct_answer_fingerprint(source: str) -> tuple[str | None, str | None]:
    """Return (ast.dump of correct_answer value, exact source segment) or (None, None)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None, None
    fn = _generate_fn(tree)
    if fn is None:
        return None, None
    ret = _return_dict(fn)
    if ret is None:
        return None, None
    _k, value, _i = _dict_entry(ret, "correct_answer")
    if value is None:
        return None, None
    dump = ast.dump(value, include_attributes=False)
    segment = ast.get_source_segment(source, value)
    return dump, segment


def _node_abs_span(source: str, node: ast.AST) -> tuple[int, int]:
    if getattr(node, "lineno", None) is None or getattr(node, "end_lineno", None) is None:
        raise ValueError("AST node lacks source location")
    lines = source.splitlines(keepends=True)
    start = sum(len(lines[i]) for i in range(node.lineno - 1)) + node.col_offset
    end = sum(len(lines[i]) for i in range(node.end_lineno - 1)) + node.end_col_offset
    return start, end


def analyze_l2_payload_wrap(
    source: str,
    frozen: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Compute per-guard results and derived applicable/triggered flags."""
    guards: dict[str, Any] = {
        "single_frozen_key": False,
        "parse_ok": False,
        "return_has_oracle_payload": False,
        "payload_static_scalar": False,
        "scalar_equals_frozen_value": False,
        "correct_answer_present": False,
        "already_wrapped": False,
        "frozen_key": None,
        "frozen_value": None,
        "resolved_scalar": None,
        "payload_value_kind": None,
    }

    if not isinstance(frozen, Mapping):
        return {
            "guards": guards,
            "applicable": False,
            "triggered": False,
            "reason": "frozen_missing_or_invalid",
        }

    keys = list(frozen.keys())
    guards["single_frozen_key"] = len(keys) == 1
    if guards["single_frozen_key"]:
        guards["frozen_key"] = keys[0]
        guards["frozen_value"] = frozen[keys[0]]

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
    if fn is None:
        return {
            "guards": guards,
            "applicable": False,
            "triggered": False,
            "reason": "generate_missing_or_ambiguous",
        }

    ret = _return_dict(fn)
    if ret is None:
        return {
            "guards": guards,
            "applicable": False,
            "triggered": False,
            "reason": "return_dict_missing",
        }

    _k, payload_value, payload_index = _dict_entry(ret, "oracle_payload")
    guards["return_has_oracle_payload"] = payload_value is not None
    _ck, correct_value, _ci = _dict_entry(ret, "correct_answer")
    guards["correct_answer_present"] = correct_value is not None

    # applicable = structural: parse + generate return carries oracle_payload
    applicable = bool(guards["parse_ok"] and guards["return_has_oracle_payload"])
    if not applicable:
        return {
            "guards": guards,
            "applicable": False,
            "triggered": False,
            "reason": "not_applicable_structure",
            "payload_index": payload_index,
        }

    if not guards["single_frozen_key"]:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "frozen_not_single_key",
            "payload_index": payload_index,
            "payload_value": payload_value,
        }

    frozen_key = guards["frozen_key"]
    frozen_value = guards["frozen_value"]
    assigns = _assignments_in_generate(fn)
    assert payload_value is not None
    guards["payload_value_kind"] = type(payload_value).__name__

    if _already_wrapped(payload_value, frozen_key, frozen_value):
        guards["already_wrapped"] = True
        guards["payload_static_scalar"] = True
        guards["resolved_scalar"] = frozen_value
        guards["scalar_equals_frozen_value"] = True
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "already_wrapped_dict",
            "payload_index": payload_index,
            "payload_value": payload_value,
        }

    resolved = _resolve_scalar(
        payload_value,
        assigns=assigns,
        frozen_key=frozen_key,
        frozen_value=frozen_value,
    )
    if resolved is _MISSING or not _is_scalar(resolved):
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "payload_not_static_scalar",
            "payload_index": payload_index,
            "payload_value": payload_value,
        }

    guards["payload_static_scalar"] = True
    guards["resolved_scalar"] = resolved
    guards["scalar_equals_frozen_value"] = resolved == frozen_value

    if not guards["scalar_equals_frozen_value"]:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "scalar_ne_frozen_value",
            "payload_index": payload_index,
            "payload_value": payload_value,
        }

    if not guards["correct_answer_present"]:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "correct_answer_missing",
            "payload_index": payload_index,
            "payload_value": payload_value,
        }

    return {
        "guards": guards,
        "applicable": True,
        "triggered": True,
        "reason": "all_transform_guards_ready",
        "payload_index": payload_index,
        "payload_value": payload_value,
    }


def is_applicable(source: str, context: Mapping[str, Any]) -> tuple[bool, Mapping[str, Any], str]:
    analysis = analyze_l2_payload_wrap(source, context.get("frozen"))
    return bool(analysis["applicable"]), dict(analysis["guards"]), str(analysis["reason"])


def is_triggered(source: str, context: Mapping[str, Any]) -> tuple[bool, str]:
    analysis = analyze_l2_payload_wrap(source, context.get("frozen"))
    if not analysis["applicable"]:
        return False, str(analysis["reason"])
    return bool(analysis["triggered"]), str(analysis["reason"])


def apply(source: str, context: Mapping[str, Any]) -> tuple[str, Mapping[str, Any], str]:
    """Replace oracle_payload scalar with ``{frozen_key: scalar}`` only."""
    analysis = analyze_l2_payload_wrap(source, context.get("frozen"))
    validation: dict[str, Any] = {"rule_id": RULE_ID}
    if not analysis.get("triggered"):
        return source, validation, f"apply_skipped:{analysis['reason']}"

    payload_value: ast.AST = analysis["payload_value"]
    frozen_key = analysis["guards"]["frozen_key"]
    scalar = analysis["guards"]["resolved_scalar"]
    before_ca = _correct_answer_fingerprint(source)

    replacement = f"{{{frozen_key!r}: {scalar!r}}}"
    start, end = _node_abs_span(source, payload_value)
    new_source = source[:start] + replacement + source[end:]

    # Guard 6: correct_answer AST + text unchanged
    after_ca = _correct_answer_fingerprint(new_source)
    validation["correct_answer_before"] = {"dump": before_ca[0], "segment": before_ca[1]}
    validation["correct_answer_after"] = {"dump": after_ca[0], "segment": after_ca[1]}
    if before_ca != after_ca or before_ca[0] is None:
        validation["correct_answer_guard"] = False
        return source, validation, "correct_answer_changed_or_missing_abort"

    validation["correct_answer_guard"] = True
    validation["wrapped_as"] = {frozen_key: scalar}
    validation["research_positioning"] = (
        "frozen-oracle-assisted deterministic structural repair"
    )
    validation["oracle_assisted"] = True
    validation["oracle_free_claimed"] = False
    validation["frozen_oracle_fields_read"] = {
        "keys": [frozen_key],
        "values": {frozen_key: scalar},
        "source": "context.frozen",
    }
    validation["evidence_scope"] = "single_fixture_fail_radical_ab1_l2_only"

    # Optional evaluator rerun (does not modify evaluator).
    task = context.get("task")
    frozen = context.get("frozen")
    if isinstance(task, Mapping) and isinstance(frozen, Mapping):
        from core.gencode.research_healer.vendor.evaluator_unavailable import classify_response

        outcome, _code, details = classify_response(
            new_source,
            {"oracle_payload": dict(frozen)},
            dict(task),
        )
        validation["evaluator_outcome"] = outcome
        validation["evaluator_rerun"] = True
        validation["evaluator_details_keys"] = sorted(details.keys())
    else:
        validation["evaluator_rerun"] = False

    return new_source, validation, "wrapped_oracle_payload_scalar"
