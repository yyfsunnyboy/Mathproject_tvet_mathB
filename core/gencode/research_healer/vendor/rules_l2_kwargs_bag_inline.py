"""L2 production rule: inline unique available frozen bag over empty kwargs bag.

Rule id: L2_KWARGS_EMPTY_BAG_INLINE_UNIQUE_PARAM

Status: production_approved (held-out 52-cell no-op regression passed).

Research positioning
--------------------
Frozen-oracle-assisted deterministic structural repair.

Detects a single pattern where ``generate`` loads a nested parameter bag via
``NAME = kwargs.get(<str>, {})`` (empty-dict default) and then only reads
static string keys from that bag. When the evaluation context exposes exactly
one available parameter mapping that structurally covers those keys
(``context.frozen``), replace the empty kwargs load with a literal of that
mapping.

Does NOT:
- reference task_id / exam numerics / candidate-specific snippets in guards
- read correct_answer / evaluator outcomes to decide acceptance
- invent keys or values beyond the unique covering parameter bag
"""

from __future__ import annotations

import ast
import json
from typing import Any, Mapping

RULE_ID = "L2_KWARGS_EMPTY_BAG_INLINE_UNIQUE_PARAM"
LAYER = "L2"
PRIORITY = 110
PRODUCTION_APPROVED = True
STATUS = "production_approved"

_SCALAR = (int, float, bool, str, type(None))


def _generate_fn(tree: ast.AST) -> ast.FunctionDef | None:
    gens = [
        n
        for n in getattr(tree, "body", [])
        if isinstance(n, ast.FunctionDef) and n.name == "generate"
    ]
    return gens[0] if len(gens) == 1 else None


def _is_empty_dict_literal(node: ast.AST) -> bool:
    return isinstance(node, ast.Dict) and len(node.keys) == 0


def _const_str(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _is_kwargs_name(node: ast.AST) -> bool:
    return isinstance(node, ast.Name) and node.id == "kwargs"


def _match_kwargs_get_empty_default(call: ast.AST) -> str | None:
    """Return kwargs key string if call is kwargs.get('K', {})."""
    if not isinstance(call, ast.Call):
        return None
    func = call.func
    if not (
        isinstance(func, ast.Attribute)
        and func.attr == "get"
        and _is_kwargs_name(func.value)
    ):
        return None
    if len(call.args) != 2 or call.keywords:
        return None
    key = _const_str(call.args[0])
    if key is None or not _is_empty_dict_literal(call.args[1]):
        return None
    return key


def _literal_embeddable(value: Any) -> bool:
    if isinstance(value, _SCALAR):
        return True
    if isinstance(value, list):
        return all(_literal_embeddable(x) for x in value)
    if isinstance(value, dict):
        return all(isinstance(k, str) and _literal_embeddable(v) for k, v in value.items())
    return False


def _value_to_ast(value: Any) -> ast.AST:
    if isinstance(value, dict):
        keys = [ast.Constant(k) for k in value.keys()]
        vals = [_value_to_ast(v) for v in value.values()]
        return ast.Dict(keys=keys, values=vals)
    if isinstance(value, list):
        return ast.List(elts=[_value_to_ast(v) for v in value], ctx=ast.Load())
    if isinstance(value, (int, float, bool, str)) or value is None:
        return ast.Constant(value)
    raise ValueError(f"non-embeddable value type: {type(value)!r}")


def _node_abs_span(source: str, node: ast.AST) -> tuple[int, int]:
    if getattr(node, "lineno", None) is None or getattr(node, "end_lineno", None) is None:
        raise ValueError("AST node lacks source location")
    lines = source.splitlines(keepends=True)
    start = sum(len(lines[i]) for i in range(node.lineno - 1)) + node.col_offset
    end = sum(len(lines[i]) for i in range(node.end_lineno - 1)) + node.end_col_offset
    return start, end


def _correct_answer_fingerprint(source: str) -> tuple[str | None, str | None]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None, None
    fn = _generate_fn(tree)
    if fn is None:
        return None, None
    for stmt in reversed(fn.body):
        if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Dict):
            for k, v in zip(stmt.value.keys, stmt.value.values):
                if isinstance(k, ast.Constant) and k.value == "correct_answer":
                    return ast.dump(v, include_attributes=False), ast.get_source_segment(source, v)
            return None, None
    return None, None


def _collect_bag_key_reads(fn: ast.FunctionDef, bag_name: str) -> tuple[set[str] | None, str]:
    """Return static string keys read from bag_name, or None if unsafe use found."""
    keys: set[str] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Name) and node.id == bag_name and isinstance(node.ctx, ast.Store):
            # allowed only at the single binding site; checked separately
            continue
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == bag_name:
            if not isinstance(node.ctx, ast.Load):
                return None, "bag_subscript_not_load"
            key = _const_str(node.slice) if not isinstance(node.slice, ast.Slice) else None
            # py3.8 compatibility: slice may be Index — but 3.11 uses Constant directly
            if key is None and isinstance(node.slice, ast.Constant):
                key = node.slice.value if isinstance(node.slice.value, str) else None
            if not isinstance(key, str):
                return None, "bag_key_not_static_string"
            keys.add(key)
            continue
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == bag_name:
                # allow bag.get("k") as key read
                if node.func.attr == "get" and node.args:
                    key = _const_str(node.args[0])
                    if key is None:
                        return None, "bag_get_key_not_static_string"
                    keys.add(key)
                    continue
                return None, f"bag_method_not_allowed:{node.func.attr}"
        if isinstance(node, ast.Name) and node.id == bag_name and isinstance(node.ctx, ast.Load):
            # bare name load OK only if parent is Return dict value / Subscript / Attribute.get already handled
            # defer: mark for parent check via walk — allow if used as oracle_payload value
            pass
    # Second pass: bare Name loads must only appear as dict values (e.g. oracle_payload)
    for node in ast.walk(fn):
        if not (isinstance(node, ast.Name) and node.id == bag_name and isinstance(node.ctx, ast.Load)):
            continue
        # Find parent — ast.walk doesn't give parent; rebuild parent map
    parents: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(fn):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    for node in ast.walk(fn):
        if not (isinstance(node, ast.Name) and node.id == bag_name and isinstance(node.ctx, ast.Load)):
            continue
        parent = parents.get(node)
        if parent is None:
            return None, "bag_name_orphaned"
        if isinstance(parent, ast.Subscript) and parent.value is node:
            continue
        if isinstance(parent, ast.Attribute) and parent.value is node:
            continue
        if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Attribute) and parent.func.value is node:
            continue
        # Allow as a dict value entry
        if isinstance(parent, ast.Dict) and node in parent.values:
            continue
        # Allow Name in ast.Starred? no
        return None, f"bag_name_used_unsafely:{type(parent).__name__}"
    return keys, "ok"


def analyze_kwargs_bag_inline(
    source: str,
    frozen: Mapping[str, Any] | None,
) -> dict[str, Any]:
    guards: dict[str, Any] = {
        "parse_ok": False,
        "single_generate": False,
        "exactly_one_kwargs_empty_bag_load": False,
        "bag_name": None,
        "kwargs_key": None,
        "static_keys_read": None,
        "bag_reads_static_only": False,
        "available_param_bags": ["context.frozen"],
        "covering_bags": [],
        "unique_covering_bag": False,
        "frozen_covers_keys": False,
        "frozen_values_embeddable": False,
        "correct_answer_present": False,
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

    load_sites: list[tuple[ast.Assign, str, str]] = []
    for stmt in fn.body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
            continue
        target = stmt.targets[0]
        if not isinstance(target, ast.Name):
            continue
        kwargs_key = _match_kwargs_get_empty_default(stmt.value)
        if kwargs_key is None:
            continue
        load_sites.append((stmt, target.id, kwargs_key))

    guards["exactly_one_kwargs_empty_bag_load"] = len(load_sites) == 1
    applicable = bool(guards["parse_ok"] and guards["single_generate"] and guards["exactly_one_kwargs_empty_bag_load"])
    if not applicable:
        return {
            "guards": guards,
            "applicable": False,
            "triggered": False,
            "reason": "not_applicable_structure",
            "load_site_count": len(load_sites),
        }

    assign, bag_name, kwargs_key = load_sites[0]
    guards["bag_name"] = bag_name
    guards["kwargs_key"] = kwargs_key

    # Disallow later stores to bag_name
    store_count = sum(
        1
        for n in ast.walk(fn)
        if isinstance(n, ast.Name) and n.id == bag_name and isinstance(n.ctx, ast.Store)
    )
    if store_count != 1:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "bag_name_reassigned_or_missing_store",
            "assign": assign,
        }

    keys, key_reason = _collect_bag_key_reads(fn, bag_name)
    if keys is None:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": key_reason,
            "assign": assign,
        }
    guards["static_keys_read"] = sorted(keys)
    guards["bag_reads_static_only"] = True
    if not keys:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "no_static_keys_read_from_bag",
            "assign": assign,
        }

    # correct_answer presence (structural; not used to choose values)
    ca_dump, _ = _correct_answer_fingerprint(source)
    guards["correct_answer_present"] = ca_dump is not None

    if not isinstance(frozen, Mapping):
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "frozen_missing_or_invalid",
            "assign": assign,
        }

    # Available parameter bags: only context.frozen (fail-closed uniqueness universe)
    available = {"context.frozen": dict(frozen)}
    covering = [
        name
        for name, bag in available.items()
        if keys.issubset(set(bag.keys()))
    ]
    guards["covering_bags"] = covering
    guards["unique_covering_bag"] = len(covering) == 1
    guards["frozen_covers_keys"] = "context.frozen" in covering
    guards["frozen_values_embeddable"] = _literal_embeddable(dict(frozen))

    if not guards["unique_covering_bag"]:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "no_unique_covering_param_bag",
            "assign": assign,
        }
    if not guards["frozen_values_embeddable"]:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "frozen_values_not_embeddable",
            "assign": assign,
        }
    if not guards["correct_answer_present"]:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "correct_answer_missing",
            "assign": assign,
        }

    return {
        "guards": guards,
        "applicable": True,
        "triggered": True,
        "reason": "all_transform_guards_ready",
        "assign": assign,
        "inline_bag": dict(frozen),
    }


def is_applicable(source: str, context: Mapping[str, Any]) -> tuple[bool, Mapping[str, Any], str]:
    analysis = analyze_kwargs_bag_inline(source, context.get("frozen"))
    return bool(analysis["applicable"]), dict(analysis["guards"]), str(analysis["reason"])


def is_triggered(source: str, context: Mapping[str, Any]) -> tuple[bool, str]:
    analysis = analyze_kwargs_bag_inline(source, context.get("frozen"))
    if not analysis["applicable"]:
        return False, str(analysis["reason"])
    return bool(analysis["triggered"]), str(analysis["reason"])


def apply(source: str, context: Mapping[str, Any]) -> tuple[str, Mapping[str, Any], str]:
    analysis = analyze_kwargs_bag_inline(source, context.get("frozen"))
    validation: dict[str, Any] = {
        "rule_id": RULE_ID,
        "production_approved": PRODUCTION_APPROVED,
        "status": STATUS,
        "research_positioning": "frozen-oracle-assisted deterministic structural repair",
        "oracle_assisted": True,
        "oracle_free_claimed": False,
    }
    if not analysis.get("triggered"):
        return source, validation, f"apply_skipped:{analysis['reason']}"

    assign: ast.Assign = analysis["assign"]
    inline_bag: dict[str, Any] = analysis["inline_bag"]
    before_ca = _correct_answer_fingerprint(source)

    literal_src = json.dumps(inline_bag, ensure_ascii=False)
    # Prefer AST round-trip for deterministic formatting of simple literals
    try:
        lit_node = _value_to_ast(inline_bag)
        ast.fix_missing_locations(lit_node)
        literal_src = ast.unparse(lit_node)
    except Exception:
        pass

    start, end = _node_abs_span(source, assign.value)
    new_source = source[:start] + literal_src + source[end:]

    try:
        ast.parse(new_source)
        validation["reparse_ok"] = True
    except SyntaxError as exc:
        validation["reparse_ok"] = False
        validation["reparse_error"] = str(exc)
        return source, validation, "reparse_failed_rollback"

    after_ca = _correct_answer_fingerprint(new_source)
    validation["correct_answer_before"] = {"dump": before_ca[0], "segment": before_ca[1]}
    validation["correct_answer_after"] = {"dump": after_ca[0], "segment": after_ca[1]}
    if before_ca != after_ca or before_ca[0] is None:
        validation["correct_answer_guard"] = False
        return source, validation, "correct_answer_changed_or_missing_abort"
    validation["correct_answer_guard"] = True
    validation["inlined_keys"] = sorted(inline_bag.keys())
    validation["kwargs_key_replaced"] = analysis["guards"]["kwargs_key"]
    validation["bag_name"] = analysis["guards"]["bag_name"]
    validation["frozen_oracle_fields_read"] = {
        "keys": sorted(inline_bag.keys()),
        "source": "context.frozen",
    }
    return new_source, validation, "inlined_unique_covering_param_bag"
