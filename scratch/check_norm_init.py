# -*- coding: utf-8 -*-
"""Check *_norm vars are assigned before use in save_to_database."""
import ast
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "core" / "textbook_processor.py"
src = path.read_text(encoding="utf-8-sig")
tree = ast.parse(src)

TARGETS = {
    "db_problem_text_norm",
    "practice_problem_norm",
    "answer_text_norm",
    "solution_text_norm",
}

for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name == "save_to_database":
        assigned = set()
        issues = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and sub.id in TARGETS:
                if isinstance(sub.ctx, ast.Store):
                    assigned.add(sub.id)
                elif isinstance(sub.ctx, ast.Load):
                    # simplistic: flag Load if we haven't seen Store on same "path"
                    pass
        # line-order scan within function body only
        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.assigned = set()
                self.issues = []

            def visit_Name(self, node):
                if node.id not in TARGETS:
                    return
                if isinstance(node.ctx, ast.Store):
                    self.assigned.add(node.id)
                elif isinstance(node.ctx, ast.Load) and node.id not in self.assigned:
                    self.issues.append((node.lineno, node.id, "used before assign"))
                self.generic_visit(node)

        v = Visitor()
        for stmt in node.body:
            v.visit(stmt)
        print("save_to_database norm var issues:", v.issues or "(none)")
        break
