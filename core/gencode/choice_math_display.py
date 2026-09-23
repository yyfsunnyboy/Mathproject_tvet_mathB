"""Canonical choice values with presentation-only LaTeX display fields."""

from __future__ import annotations

import ast
import re
from typing import Any

_INTEGER_OR_DECIMAL = re.compile(r"^[+-]?\d+(?:\.\d+)?$")
_COORDINATE_PAIR = re.compile(
    r"^\(\s*[+-]?\d+(?:\.\d+)?(?:/\d+)?\s*,\s*[+-]?\d+(?:\.\d+)?(?:/\d+)?\s*\)$"
)


def _arithmetic_latex(source: str) -> str:
    """Print bounded numeric syntax without evaluating code or simplifying math."""
    if len(source) > 512 or not re.fullmatch(r"[0-9.sqrt()+*/\-\s]+", source):
        raise ValueError("not numeric arithmetic")
    tree = ast.parse(source, mode="eval")
    if sum(1 for _ in ast.walk(tree)) > 128:
        raise ValueError("expression too large")

    def render(node: ast.AST, parent: int = 0) -> str:
        precedence = 4
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            text = ast.get_source_segment(source, node) or ""
            if not re.fullmatch(r"\d+(?:\.\d+)?", text):
                raise ValueError("unsupported number")
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id == "sqrt" and len(node.args) == 1 and not node.keywords):
            text = rf"\sqrt{{{render(node.args[0])}}}"
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            precedence = 3
            text = ("-" if isinstance(node.op, ast.USub) else "+") + render(node.operand, precedence)
        elif isinstance(node, ast.BinOp):
            if isinstance(node.op, (ast.Add, ast.Sub)):
                precedence = 1
                op = " + " if isinstance(node.op, ast.Add) else " - "
                text = render(node.left, 1) + op + render(node.right, 2)
            elif isinstance(node.op, ast.Mult):
                precedence = 2
                right = render(node.right, 3)
                op = "" if right.startswith((r"\sqrt", r"\left(")) else r" \times "
                text = render(node.left, 2) + op + right
            elif isinstance(node.op, ast.Div):
                text = rf"\frac{{{render(node.left)}}}{{{render(node.right)}}}"
            else:
                raise ValueError("unsupported operator")
        else:
            raise ValueError("unsupported syntax")
        return rf"\left({text}\right)" if precedence < parent else text

    return render(tree.body)


def format_choice_math_display(value: Any) -> str:
    """Return MathJax-ready display text without changing the canonical value."""
    canonical = str(value if value is not None else "").strip()
    if not canonical or "\\" in canonical or "$" in canonical:
        # Preserve the established contract for both wrapped and bare TeX.
        return canonical
    if _INTEGER_OR_DECIMAL.fullmatch(canonical) or _COORDINATE_PAIR.fullmatch(canonical):
        return canonical
    try:
        return rf"\({_arithmetic_latex(canonical)}\)"
    except (ValueError, SyntaxError, RecursionError):
        return canonical


def _choice_text(*values: Any) -> str:
    # Keep numeric zero and the legacy adaptive "content" alias.
    return next((str(value).strip() for value in values if value is not None and value != ""), "")


def normalize_choice_displays(choices: Any) -> list[dict[str, str]]:
    """Normalize choices while separating canonical value and display text."""
    if not isinstance(choices, list):
        return []
    normalized: list[dict[str, str]] = []
    for index, item in enumerate(choices):
        if isinstance(item, dict):
            label = str(item.get("label") or item.get("key") or chr(ord("A") + index)).strip()
            canonical = _choice_text(item.get("value"), item.get("text"), item.get("content"))
            text = _choice_text(item.get("text"), item.get("content"), canonical)
            display = format_choice_math_display(item.get("display") or text)
        else:
            label = chr(ord("A") + index)
            canonical = _choice_text(item)
            text = canonical
            display = format_choice_math_display(canonical)
        normalized.append(
            {
                "key": label,
                "label": label,
                "text": text,
                "value": canonical,
                "display": display,
            }
        )
    return normalized
