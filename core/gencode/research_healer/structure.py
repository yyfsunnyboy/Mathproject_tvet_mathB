# -*- coding: utf-8 -*-
"""Structure, safety and edit-scope checks for the V3 research healer adapter."""

from __future__ import annotations

import ast
import difflib
import re
from collections import Counter
from typing import Any

UNSAFE_IMPORTS = frozenset(
    {
        "os",
        "subprocess",
        "shutil",
        "socket",
        "ctypes",
        "pickle",
        "marshal",
        "importlib",
        "builtins",
        "multiprocessing",
        "requests",
        "urllib",
        "http",
    }
)
UNSAFE_CALLS = frozenset({"eval", "exec", "compile", "__import__", "open", "input", "breakpoint"})
_OPERATOR_CHARS = set("+-*/%^<>=!&|~@")
_DELIMITER_CHARS = set("()[]{}")
_CONTROL_FLOW_NODES = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.Try,
    ast.With,
    ast.AsyncWith,
    ast.Return,
    ast.Break,
    ast.Continue,
    ast.Raise,
    ast.IfExp,
    ast.Match,
)
_CONTROL_FLOW_WORD_RE = re.compile(r"\b(if|elif|else|for|while|try|except|finally|with|return|break|continue|raise)\b")


def parse_status(source: str) -> dict[str, Any]:
    try:
        ast.parse(source)
    except SyntaxError as exc:
        return {"parses": False, "error": f"{exc.msg} (line {exc.lineno})", "lineno": exc.lineno}
    except (ValueError, TypeError) as exc:
        return {"parses": False, "error": f"{type(exc).__name__}: {exc}", "lineno": None}
    return {"parses": True, "error": None, "lineno": None}


def safety_findings(source: str) -> list[str]:
    """Static detection only; never edits the source."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, TypeError):
        return []
    findings: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in UNSAFE_IMPORTS:
                    findings.append(f"unsafe_import:{root}")
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            if root in UNSAFE_IMPORTS:
                findings.append(f"unsafe_import:{root}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in UNSAFE_CALLS:
            findings.append(f"unsafe_call:{node.func.id}")
    return sorted(set(findings))


def _ast_profile(tree: ast.AST) -> dict[str, Any]:
    operators: list[str] = []
    control: Counter[str] = Counter()
    functions: list[str] = []
    constants: Counter[str] = Counter()
    names: Counter[str] = Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp):
            operators.append(type(node.op).__name__)
        elif isinstance(node, ast.UnaryOp):
            operators.append(f"U{type(node.op).__name__}")
        elif isinstance(node, ast.BoolOp):
            operators.append(type(node.op).__name__)
        elif isinstance(node, ast.Compare):
            operators.extend(type(op).__name__ for op in node.ops)
        elif isinstance(node, ast.AugAssign):
            operators.append(f"Aug{type(node.op).__name__}")
        if isinstance(node, _CONTROL_FLOW_NODES):
            control[type(node).__name__] += 1
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            functions.append(node.name)
        elif isinstance(node, ast.Constant):
            constants[repr(node.value)] += 1
        elif isinstance(node, ast.Name):
            names[node.id] += 1
    return {
        "operators": sorted(operators),
        "control": dict(control),
        "functions": sorted(functions),
        "constants": constants,
        "names": names,
    }


def _ast_diff(before: str, after: str) -> dict[str, Any] | None:
    try:
        b_tree, a_tree = ast.parse(before), ast.parse(after)
    except (SyntaxError, ValueError, TypeError):
        return None
    b, a = _ast_profile(b_tree), _ast_profile(a_tree)
    return {
        "ast_identical": ast.dump(b_tree) == ast.dump(a_tree),
        "math_operator_changed": b["operators"] != a["operators"],
        "control_flow_changed": b["control"] != a["control"],
        "function_names_changed": b["functions"] != a["functions"],
        "constants_changed": b["constants"] != a["constants"],
        "names_changed": b["names"] != a["names"],
    }


def _char_edits(before: str, after: str) -> tuple[str, str]:
    inserted: list[str] = []
    deleted: list[str] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=before, b=after, autojunk=False).get_opcodes():
        if tag in ("replace", "delete"):
            deleted.append(before[i1:i2])
        if tag in ("replace", "insert"):
            inserted.append(after[j1:j2])
    return "".join(inserted), "".join(deleted)


def _removed_or_commented_lines(before: str, after: str) -> list[str]:
    """Code lines of ``before`` that no longer appear verbatim (including lines turned into comments)."""
    a_set = set(after.splitlines())
    return [
        line.strip()
        for line in before.splitlines()
        if line.strip() and not line.strip().startswith("#") and line not in a_set
    ]


def structural_diff(reference: str, candidate: str) -> dict[str, Any]:
    """Classify how ``candidate`` differs from ``reference`` (the model's own code)."""
    if reference == candidate:
        return {
            "changed": False,
            "math_operator_changed": False,
            "control_flow_changed": False,
            "function_names_changed": False,
            "constants_changed": False,
            "code_deleted": False,
            "delimiter_only": False,
            "verbatim_substring": True,
            "ast_compared": True,
        }
    inserted, deleted = _char_edits(reference, candidate)
    changed_chars = set((inserted + deleted).replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", ""))
    removed_lines = _removed_or_commented_lines(reference, candidate)
    ast_part = _ast_diff(reference, candidate)
    delimiter_only = bool(changed_chars) and changed_chars <= _DELIMITER_CHARS
    result: dict[str, Any] = {
        "changed": True,
        "chars_inserted": len(inserted),
        "chars_deleted": len(deleted),
        "delimiter_only": delimiter_only,
        "verbatim_substring": candidate.strip() != "" and candidate in reference,
        "code_deleted": bool(removed_lines) and not delimiter_only,
        "removed_line_count": len(removed_lines),
        "ast_compared": ast_part is not None,
    }
    if ast_part is not None:
        result.update(ast_part)
    else:
        result.update(
            {
                "math_operator_changed": bool(changed_chars & _OPERATOR_CHARS),
                "control_flow_changed": bool(_CONTROL_FLOW_WORD_RE.search(inserted + deleted))
                or any(_CONTROL_FLOW_WORD_RE.search(line) for line in removed_lines),
                "function_names_changed": bool(re.search(r"\bdef\b|\bclass\b", inserted + deleted)),
                "constants_changed": bool(re.search(r"\d", inserted + deleted)),
            }
        )
    return result


def grouping_alternatives(before: str, after: str) -> int | None:
    """For a single inserted closing delimiter, count distinct parseable placements in that line."""
    if len(after) != len(before) + 1:
        return None
    i = next((k for k in range(len(before)) if before[k] != after[k]), len(before))
    char = after[i]
    if char not in ")]}" or after[:i] + after[i + 1 :] != before:
        return None
    line_start = before.rfind("\n", 0, i) + 1
    line_end = before.find("\n", i)
    line_end = len(before) if line_end < 0 else line_end
    dumps: set[str] = set()
    for pos in range(line_start, line_end + 1):
        trial = before[:pos] + char + before[pos:]
        try:
            dumps.add(ast.dump(ast.parse(trial)))
        except (SyntaxError, ValueError, TypeError):
            continue
    return len(dumps)
