"""V3 Cross-Component Audit and Template Collapse Gate Service."""

from __future__ import annotations

import ast
import hashlib
import re
from typing import Any

def calculate_ast_hash(code_text: str) -> str:
    """Calculate a hash of the AST structure, ignoring literal values and formatting."""
    try:
        tree = ast.parse(code_text)
        # Helper to strip literals from the AST representation
        class ASTStripper(ast.NodeTransformer):
            def visit_Constant(self, node):
                return ast.Constant(value=None)
            def visit_Num(self, node): # for python < 3.8 compatibility
                return ast.Num(n=0)
            def visit_Str(self, node): # for python < 3.8 compatibility
                return ast.Str(s="")
        stripped_tree = ASTStripper().visit(tree)
        ast_str = ast.dump(stripped_tree)
        return hashlib.md5(ast_str.encode("utf-8")).hexdigest()
    except Exception:
        # Fallback to simple line-based code hash
        return hashlib.md5(code_text.encode("utf-8")).hexdigest()


def extract_template_signature(question_text: str) -> str:
    """Extract a structural text signature from the question text by replacing numbers/equations."""
    text = str(question_text or "")
    # Replace LaTeX coordinates: \left( -2,3 \right) -> \left( #NUM,#NUM \right)
    text = re.sub(r'\\left\(\s*-?\d+\s*,\s*-?\d+\s*\\right\)', lambda m: '\\left( #NUM,#NUM \\right)', text)
    # Replace standard linear equations Ax + By + C = 0
    text = re.sub(r'([+-]?\s*\d*[xy]\s*){1,2}([+-]?\s*\d+)?\s*=\s*0', '#EQUATION', text)
    # Replace numbers
    text = re.sub(r'-?\d+', '#NUM', text)
    return text.strip()


def check_cross_example_collapse(
    components_info: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Verify all components under the same skill to detect cross-example template collapse.
    
    components_info: list of dicts:
    - textbook_example_id: int
    - problem_type_id: str
    - generate_code: str
    - sample_question_text: str
    """
    if len(components_info) <= 1:
        return {
            "collapse_detected": False,
            "reasons": [],
            "metrics": {
                "unique_problem_type_count": len(components_info),
                "unique_ast_hash_count": len(components_info),
                "unique_template_signature_count": len(components_info),
            }
        }
        
    unique_problem_types = {c["problem_type_id"] for c in components_info}
    unique_ast_hashes = {calculate_ast_hash(c["generate_code"]) for c in components_info}
    non_empty_template_signatures = {
        extract_template_signature(c["sample_question_text"])
        for c in components_info
        if str(c.get("sample_question_text") or "").strip()
    }
    
    collapse_detected = False
    reasons = []
    
    # If there are many examples, but only 1 problem type or 1 ast hash, it is a collapse!
    if len(unique_problem_types) == 1:
        collapse_detected = True
        reasons.append("cross_example_semantic_collapse: only 1 unique problem_type_id detected across all components")
    if len(non_empty_template_signatures) == 1:
        collapse_detected = True
        reasons.append("cross_example_semantic_collapse: only 1 unique template signature detected across all components")
        
    return {
        "collapse_detected": collapse_detected,
        "reasons": reasons,
        "metrics": {
            "unique_problem_type_count": len(unique_problem_types),
            "unique_ast_hash_count": len(unique_ast_hashes),
            "unique_template_signature_count": len(non_empty_template_signatures),
        }
    }
