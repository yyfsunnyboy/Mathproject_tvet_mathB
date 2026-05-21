# -*- coding: utf-8 -*-
"""Regex audit for textbook_processor and math_formula_normalizer."""
import ast
import re
import sys
from pathlib import Path

FILES = [
    Path(__file__).resolve().parents[1] / "core" / "textbook_processor.py",
    Path(__file__).resolve().parents[1] / "core" / "math_formula_normalizer.py",
]
GARBLE_MARKERS = ("\ufffd", "銝", "憒", "瘜", "\uf010", "", "嚗", "踐", "兜嗽", "菊", "猾", "嫖", "嚚")
RE_METHODS = {"search", "match", "findall", "finditer", "sub", "compile", "split", "fullmatch"}


def collect_patterns(path: Path):
    src = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in RE_METHODS:
            continue
        if not isinstance(node.func.value, ast.Name) or node.func.value.id != "re":
            continue
        for arg in node.args[:1]:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                out.append((node.lineno, node.func.attr, arg.value))
    return out


def audit_save_to_database_undefined(path: Path):
    src = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(src)
    module_funcs = {
        n.name
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    issues = []
    in_save = False
    local_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "save_to_database":
            in_save = True
            local_names = {node.name}
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    local_names.add(child.name)
            for sub in ast.walk(node):
                if isinstance(sub, ast.FunctionDef) and sub is not node:
                    local_names.add(sub.name)
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                    name = sub.func.id
                    if name.startswith("_") and name not in local_names and name not in module_funcs:
                        if not any(
                            isinstance(p, ast.ImportFrom) and p.module
                            for p in tree.body
                            if isinstance(p, ast.ImportFrom)
                        ):
                            issues.append((sub.lineno, name))
            break
    return issues


def main():
    compile_fail = []
    garble_regex = []
    dead = []
    for f in FILES:
        for lineno, method, pat in collect_patterns(f):
            try:
                re.compile(pat)
            except re.error as e:
                compile_fail.append((f.name, lineno, method, str(e), pat[:80]))
            if pat.strip() in (r"$^", "$^"):
                dead.append((f.name, lineno, pat))
            for g in GARBLE_MARKERS:
                if g in pat:
                    garble_regex.append((f.name, lineno, g, pat[:80]))
                    break

    undef = audit_save_to_database_undefined(FILES[0]) if FILES[0].exists() else []

    print("=== COMPILE FAIL ===")
    for row in compile_fail:
        print(row)
    print("=== GARBLE IN REGEX LITERAL ===")
    for row in garble_regex:
        print(row)
    print("=== DEAD $^ ===")
    for row in dead:
        print(row)
    print("=== SAVE_TO_DATABASE UNDEFINED _ CALLS ===")
    for row in undef:
        print(row)
    print(
        "summary:",
        f"compile_fail={len(compile_fail)}",
        f"garble_regex={len(garble_regex)}",
        f"dead={len(dead)}",
        f"undef={len(undef)}",
    )
    return 1 if compile_fail or garble_regex or dead or undef else 0


if __name__ == "__main__":
    sys.exit(main())
