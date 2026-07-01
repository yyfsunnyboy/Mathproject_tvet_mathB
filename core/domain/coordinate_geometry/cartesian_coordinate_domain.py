from __future__ import annotations

import ast
import re
import random
from typing import Any

def evaluate_ast_sign(node: ast.AST, var_signs: dict[str, str], comparisons: set[tuple[str, str, str]]) -> str:
    """Evaluate sign of an AST node. Returns '+', '-', '0', or '?'."""
    if isinstance(node, ast.Expression):
        return evaluate_ast_sign(node.body, var_signs, comparisons)
        
    elif isinstance(node, ast.Name):
        return var_signs.get(node.id, "?")
        
    elif isinstance(node, ast.Constant):
        val = node.value
        if not isinstance(val, (int, float)):
            raise ValueError("Unsupported constant type")
        if val > 0:
            return "+"
        elif val < 0:
            return "-"
        else:
            return "0"
            
    elif isinstance(node, ast.UnaryOp):
        operand_sign = evaluate_ast_sign(node.operand, var_signs, comparisons)
        if isinstance(node.op, ast.USub):
            if operand_sign == "+":
                return "-"
            elif operand_sign == "-":
                return "+"
            elif operand_sign == "0":
                return "0"
            return "?"
        elif isinstance(node.op, ast.UAdd):
            return operand_sign
        raise ValueError("Unsupported unary operator")
        
    elif isinstance(node, ast.BinOp):
        left = evaluate_ast_sign(node.left, var_signs, comparisons)
        right = evaluate_ast_sign(node.right, var_signs, comparisons)
        
        if isinstance(node.op, ast.Mult):
            if left == "0" or right == "0":
                return "0"
            if left == "?" or right == "?":
                return "?"
            if left == right:
                return "+"
            return "-"
            
        elif isinstance(node.op, ast.Div):
            if right == "0":
                raise ValueError("Division by zero")
            if left == "0":
                return "0"
            if left == "?" or right == "?":
                return "?"
            if left == right:
                return "+"
            return "-"
            
        elif isinstance(node.op, ast.Add):
            if left == "0":
                return right
            if right == "0":
                return left
            if left == right and left in ("+", "-"):
                return left
            return "?"
            
        elif isinstance(node.op, ast.Sub):
            if right == "0":
                return left
            if left == "0":
                if right == "+":
                    return "-"
                elif right == "-":
                    return "+"
                return right
            if left == "+" and right == "-":
                return "+"
            if left == "-" and right == "+":
                return "-"
            # check comparisons if signs are same
            if left == right and left in ("+", "-"):
                if isinstance(node.left, ast.Name) and isinstance(node.right, ast.Name):
                    name_l = node.left.id
                    name_r = node.right.id
                    if (name_l, "<", name_r) in comparisons:
                        return "-"
                    if (name_l, ">", name_r) in comparisons or (name_r, "<", name_l) in comparisons:
                        return "+"
            return "?"
            
        elif isinstance(node.op, ast.Pow):
            if isinstance(node.right, ast.Constant):
                exp = node.right.value
                if isinstance(exp, int):
                    if exp == 0:
                        return "+"
                    if exp % 2 == 0:
                        # even exponent: positive if base is non-zero
                        if left in ("+", "-"):
                            return "+"
                        elif left == "0":
                            return "0"
                        return "?"
                    else:
                        # odd exponent: preserves sign
                        return left
            return "?"
            
    raise ValueError("Unsupported AST node")


def parse_conditions(cond_str: str) -> tuple[dict[str, str], set[tuple[str, str, str]]]:
    """Parse conditions string to signs and comparisons."""
    var_signs = {}
    comparisons = set()
    
    s = cond_str.replace(" ", "").replace("，", ",").replace("且", ",")
    parts = s.split(",")
    for p in parts:
        if not p:
            continue
        # Check chain like a < b < 0
        m_chain = re.match(r"^([a-zA-Z]+)<([a-zA-Z]+)<0$", p)
        if m_chain:
            v1, v2 = m_chain.groups()
            var_signs[v1] = "-"
            var_signs[v2] = "-"
            comparisons.add((v1, "<", v2))
            continue
            
        m_chain2 = re.match(r"^0<([a-zA-Z]+)<([a-zA-Z]+)$", p)
        if m_chain2:
            v1, v2 = m_chain2.groups()
            var_signs[v1] = "+"
            var_signs[v2] = "+"
            comparisons.add((v1, "<", v2))
            continue

        # Single inequalities
        m_ineq = re.match(r"^([a-zA-Z]+)(<|>|==|<=|>=)([\-]?\d+)$", p)
        if m_ineq:
            var_name, op, val_str = m_ineq.groups()
            val = int(val_str)
            if val == 0:
                if op == ">":
                    var_signs[var_name] = "+"
                elif op == "<":
                    var_signs[var_name] = "-"
                elif op == "==":
                    var_signs[var_name] = "0"
            continue
            
        # Comparison between variables
        m_comp = re.match(r"^([a-zA-Z]+)(<|>)([a-zA-Z]+)$", p)
        if m_comp:
            v1, op, v2 = m_comp.groups()
            comparisons.add((v1, op, v2))
            continue
            
    return var_signs, comparisons


def deduce_sign(expr_str: str, var_signs: dict[str, str], comparisons: set[tuple[str, str, str]]) -> str:
    """Parse and evaluate sign of expression string."""
    expr_str = expr_str.replace("^", "**").strip()
    try:
        tree = ast.parse(expr_str, mode="eval")
    except Exception as e:
        raise ValueError(f"Invalid expression: {expr_str}") from e
    return evaluate_ast_sign(tree.body, var_signs, comparisons)


def build_cartesian_coordinate_matrix(
    *,
    seed: int | None,
    domain_operation: str,
    curriculum_profile: str = "vocational_high_b",
    difficulty_profile: str = "easy",
    constraints: dict[str, object] | None = None,
    line_type: str | None = None,
) -> dict[str, Any]:
    """Domain entrypoint to reason about coordinate quadrants and signs."""
    op = str(domain_operation or line_type or "").strip()
    if op != "cartesian_coordinate_quadrant_symbol_reasoning":
        raise ValueError(f"Unsupported operation: {op}")
        
    rng = random.Random(0 if seed is None else seed)
    extra = dict(constraints or {})
    
    spec = extra.get("v3_induced_spec") or extra.get("phase1_classification") or {}
    if not isinstance(spec, dict):
        spec = {}
        
    # Get parameters
    var_conds = extra.get("variable_conditions") or spec.get("variable_conditions")
    x_expr = extra.get("x_expression") or spec.get("x_expression")
    y_expr = extra.get("y_expression") or spec.get("y_expression")
    
    # If not supplied, generate a random template
    if not var_conds or not x_expr or not y_expr:
        templates = [
            ("a > 0, b > 0, a < b", "a - b", "a**2 * b"),
            ("a < b < 0", "a * b", "a + b"),
            ("a > 0, b < 0", "a - b", "b**2"),
        ]
        var_conds, x_expr, y_expr = rng.choice(templates)
        
    var_signs, comparisons = parse_conditions(str(var_conds))
    x_sign = deduce_sign(str(x_expr), var_signs, comparisons)
    y_sign = deduce_sign(str(y_expr), var_signs, comparisons)
    
    if x_sign == "+" and y_sign == "+":
        quadrant = "第一象限"
    elif x_sign == "-" and y_sign == "+":
        quadrant = "第二象限"
    elif x_sign == "-" and y_sign == "-":
        quadrant = "第三象限"
    elif x_sign == "+" and y_sign == "-":
        quadrant = "第四象限"
    else:
        # If coordinate is 0 or signs are undetermined, reject generation
        raise ValueError("unresolved_quadrant_signs")
        
    all_quads = ["第一象限", "第二象限", "第三象限", "第四象限"]
    distractors = [q for q in all_quads if q != quadrant]
    
    return {
        "givens": {
            "variable_conditions": var_conds,
            "x_expression": x_expr,
            "y_expression": y_expr,
        },
        "answer": {
            "canonical_form": quadrant,
            "general_form": quadrant,
        },
        "distractors": distractors,
        "explanation_steps": [
            f"Analyze variable conditions: {var_conds}.",
            f"Deduce sign of x coordinate: {x_expr} -> {x_sign}.",
            f"Deduce sign of y coordinate: {y_expr} -> {y_sign}.",
            f"Determine the quadrant: {quadrant}.",
        ],
        "validation_facts": {
            "domain_operation": op,
            "task_type": op,
            "line_type": op,
            "curriculum_profile": curriculum_profile,
            "difficulty_profile": difficulty_profile,
            "x_sign": x_sign,
            "y_sign": y_sign,
            "quadrant": quadrant,
            "semantic_answer": quadrant,
        },
    }
