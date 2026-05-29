from __future__ import annotations


def format_x_minus_center(center: int | float) -> str:
    """Format |x - center| inner expression in natural LaTeX."""
    c = int(center)
    if c == 0:
        return "x"
    if c > 0:
        return f"x-{c}"
    return f"x+{abs(c)}"


def format_linear_abs_expr(center: int | float) -> str:
    """Format |x - center| with simplified inner expression."""
    return f"|{format_x_minus_center(center)}|"


def format_abs_inequality_op(op: str) -> str:
    """Map inequality operator to LaTeX comparison symbol."""
    raw = str(op or "").strip()
    mapping = {
        "<=": r"\le",
        ">=": r"\ge",
        "<": "<",
        ">": ">",
    }
    return mapping.get(raw, raw)
