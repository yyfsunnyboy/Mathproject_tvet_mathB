# -*- coding: utf-8 -*-
"""Extract Python from Qwen responses and reject dangerous constructs."""

from __future__ import annotations

import ast
import re
from typing import Any

from core.gencode.qwen_experiment.constants import (
    ALLOWED_TOP_LEVEL_IMPORT_PREFIXES,
    FORBIDDEN_CALL_NAMES,
    FORBIDDEN_MODULE_NAMES,
)

_THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", flags=re.DOTALL | re.IGNORECASE)
_THINK_OPEN_RE = re.compile(r"<think>.*", flags=re.DOTALL | re.IGNORECASE)
_FENCE_RE = re.compile(
    r"```(?:python|py)?\s*\n(.*?)```",
    flags=re.DOTALL | re.IGNORECASE,
)


class CodeExtractionError(ValueError):
    """Raised when Python cannot be safely extracted."""


class DangerousCodeError(ValueError):
    """Raised when extracted code contains forbidden operations."""


def strip_think_blocks(text: str) -> str:
    cleaned = _THINK_BLOCK_RE.sub("", str(text or ""))
    cleaned = _THINK_OPEN_RE.sub("", cleaned)
    return cleaned.strip()


def extract_python_code(raw_text: str) -> str:
    text = strip_think_blocks(raw_text)
    if not text:
        raise CodeExtractionError("empty_response_after_think_strip")

    fences = _FENCE_RE.findall(text)
    if fences:
        # Prefer the largest python-looking fence.
        candidates = [c.strip() for c in fences if c.strip()]
        if not candidates:
            raise CodeExtractionError("empty_code_fence")
        code = max(candidates, key=len)
    else:
        code = _extract_bare_python(text)

    code = code.strip()
    if not code:
        raise CodeExtractionError("empty_extracted_code")
    if "def generate" not in code:
        raise CodeExtractionError("missing_generate_function")
    # Reject large trailing prose after the last def/class block heuristically.
    code = _trim_trailing_prose(code)
    return code


def _extract_bare_python(text: str) -> str:
    lines = text.splitlines()
    start = None
    starters = ("from ", "import ", "def ", "class ", "@")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(starters):
            start = i
            break
    if start is None:
        raise CodeExtractionError("no_python_start_marker")
    return "\n".join(lines[start:]).strip()


def _trim_trailing_prose(code: str) -> str:
    lines = code.splitlines()
    last_code_idx = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            last_code_idx = i
            continue
        # Chinese explanatory lines after code are rejected as trailing prose.
        if re.search(r"[\u4e00-\u9fff]", stripped) and not any(
            tok in stripped for tok in ("=", "def ", "return", "import", "class ", ":", "(", ")")
        ):
            continue
        last_code_idx = i
    if last_code_idx < 0:
        return code
    return "\n".join(lines[: last_code_idx + 1]).rstrip()


def scan_dangerous_code(code: str) -> list[str]:
    blockers: list[str] = []
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [f"syntax_error:{exc.msg}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = str(alias.name or "")
                root = name.split(".", 1)[0]
                if root in FORBIDDEN_MODULE_NAMES or name in FORBIDDEN_MODULE_NAMES:
                    blockers.append(f"forbidden_import:{name}")
                elif not _import_allowed(name):
                    blockers.append(f"disallowed_import:{name}")
        elif isinstance(node, ast.ImportFrom):
            mod = str(node.module or "")
            root = mod.split(".", 1)[0] if mod else ""
            if root in FORBIDDEN_MODULE_NAMES or mod in FORBIDDEN_MODULE_NAMES:
                blockers.append(f"forbidden_import_from:{mod}")
            elif mod and not _import_allowed(mod):
                blockers.append(f"disallowed_import_from:{mod}")
        elif isinstance(node, ast.Call):
            blockers.extend(_scan_call(node))
        elif isinstance(node, ast.Attribute):
            if node.attr in {"system", "popen", "remove", "unlink", "rmtree", "rmdir"}:
                blockers.append(f"forbidden_attr:{node.attr}")
    return list(dict.fromkeys(blockers))


def _import_allowed(module_name: str) -> bool:
    name = str(module_name or "").strip()
    if not name:
        return False
    if name == "os":
        # os itself is high-risk; disallow wholesale import.
        return False
    for prefix in ALLOWED_TOP_LEVEL_IMPORT_PREFIXES:
        if name == prefix or name.startswith(prefix + "."):
            return True
    # Allow stdlib modules that are not forbidden and not path/network related.
    safe_stdlib = {
        "__future__",
        "typing",
        "math",
        "random",
        "fractions",
        "decimal",
        "dataclasses",
        "collections",
        "itertools",
        "functools",
        "re",
        "json",
        "copy",
        "hashlib",
        "string",
        "operator",
        "statistics",
        "abc",
        "enum",
        "numbers",
    }
    return name.split(".", 1)[0] in safe_stdlib


def _scan_call(node: ast.Call) -> list[str]:
    blockers: list[str] = []
    func = node.func
    name = ""
    if isinstance(func, ast.Name):
        name = func.id
    elif isinstance(func, ast.Attribute):
        name = func.attr
        if isinstance(func.value, ast.Name) and func.value.id == "os" and func.attr in {
            "system",
            "popen",
            "remove",
            "unlink",
            "rmdir",
        }:
            blockers.append(f"forbidden_call:os.{func.attr}")
    if name in FORBIDDEN_CALL_NAMES:
        blockers.append(f"forbidden_call:{name}")
    if isinstance(func, ast.Name) and func.id == "open":
        # Reject write modes.
        if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
            mode = str(node.args[1].value)
            if any(ch in mode for ch in ("w", "a", "x", "+")):
                blockers.append("forbidden_file_write:open")
        for kw in node.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                mode = str(kw.value.value)
                if any(ch in mode for ch in ("w", "a", "x", "+")):
                    blockers.append("forbidden_file_write:open")
    return blockers


def assert_safe_python(code: str) -> str:
    blockers = scan_dangerous_code(code)
    if any(b.startswith("syntax_error:") for b in blockers):
        raise CodeExtractionError(blockers[0])
    if blockers:
        raise DangerousCodeError(";".join(blockers))
    # Ensure AST parses cleanly.
    ast.parse(code)
    return code


def extract_and_sanitize(raw_text: str) -> dict[str, Any]:
    stripped = strip_think_blocks(raw_text)
    code = extract_python_code(raw_text)
    assert_safe_python(code)
    return {
        "stripped_text": stripped,
        "code": code,
        "think_removed": stripped != str(raw_text or "").strip(),
    }
