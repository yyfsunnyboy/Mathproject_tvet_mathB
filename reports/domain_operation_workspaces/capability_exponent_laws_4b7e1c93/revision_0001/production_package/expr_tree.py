"""Expression-tree DSL shared by the exponent-laws domain.

A tree is a nested list:  ["n","3"] ["n","1/2"] ["sym","a"] ["pi"] ["pow",b,e]
["mul",x,..] ["jux",x,..] ["div",x,y] ["add",x,..] ["sub",x,y] ["neg",x]
["sqrt",x] ["root",k,x].  Exact evaluation (sympy) and numeric evaluation (mpmath)
are separate implementations so that one can audit the other.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

import mpmath as mp
import sympy as sp

mp.mp.dps = 60


def _rational(text: str) -> sp.Rational:
    return sp.Rational(str(text).strip())


def to_sympy(tree: Any, env: dict[str, Any] | None = None) -> sp.Expr:
    env = env or {}
    kind = tree[0]
    if kind == "n":
        return _rational(tree[1])
    if kind == "pi":
        return sp.pi
    if kind == "sym":
        return env[tree[1]] if tree[1] in env else sp.Symbol(tree[1], positive=True)
    args = [to_sympy(t, env) for t in tree[1:]] if kind != "root" else None
    if kind == "pow":
        return sp.Pow(args[0], args[1])
    if kind in ("mul", "jux"):
        return sp.Mul(*args)
    if kind == "div":
        return args[0] / args[1]
    if kind == "add":
        return sp.Add(*args)
    if kind == "sub":
        return args[0] - args[1]
    if kind == "neg":
        return -args[0]
    if kind == "sqrt":
        return sp.sqrt(args[0])
    if kind == "root":
        return sp.Pow(to_sympy(tree[2], env), sp.Rational(1, int(tree[1])))
    raise ValueError(f"unknown_tree_node:{kind}")


def to_mpmath(tree: Any, env: dict[str, Any] | None = None) -> mp.mpf:
    """Independent high-precision evaluation (does not use sympy)."""
    env = env or {}
    kind = tree[0]
    if kind == "n":
        fr = Fraction(str(tree[1]).strip())
        return mp.mpf(fr.numerator) / mp.mpf(fr.denominator)
    if kind == "pi":
        return mp.pi
    if kind == "sym":
        return env[tree[1]]
    if kind == "root":
        return mp.root(to_mpmath(tree[2], env), int(tree[1]))
    vals = [to_mpmath(t, env) for t in tree[1:]]
    if kind == "pow":
        return mp.power(vals[0], vals[1])
    if kind in ("mul", "jux"):
        out = mp.mpf(1)
        for v in vals:
            out *= v
        return out
    if kind == "div":
        return vals[0] / vals[1]
    if kind == "add":
        return mp.fsum(vals)
    if kind == "sub":
        return vals[0] - vals[1]
    if kind == "neg":
        return -vals[0]
    if kind == "sqrt":
        return mp.sqrt(vals[0])
    raise ValueError(f"unknown_tree_node:{kind}")


def symbols_in(tree: Any) -> list[str]:
    if tree[0] == "sym":
        return [tree[1]]
    out: list[str] = []
    for child in tree[1:]:
        if isinstance(child, list):
            for name in symbols_in(child):
                if name not in out:
                    out.append(name)
    return out


# --- LaTeX ---------------------------------------------------------------------

def _num_latex(text: str) -> str:
    text = str(text).strip()
    if "/" in text:
        num, den = text.split("/", 1)
        sign = "-" if num.startswith("-") else ""
        return f"{sign}\\frac{{{num.lstrip('-')}}}{{{den}}}"
    return text


def _needs_wrap_as_base(tree: Any) -> bool:
    kind = tree[0]
    if kind == "n":
        return tree[1].startswith("-") or "/" in tree[1] or "." in tree[1]
    return kind not in ("sym", "pi")


def _wrap(tex: str) -> str:
    return f"\\left({tex}\\right)"


def to_latex(tree: Any) -> str:
    kind = tree[0]
    if kind == "n":
        return _num_latex(tree[1])
    if kind == "pi":
        return "\\pi"
    if kind == "sym":
        return tree[1]
    if kind == "pow":
        base = to_latex(tree[1])
        if _needs_wrap_as_base(tree[1]):
            base = _wrap(base)
        return f"{base}^{{{to_latex(tree[2])}}}"
    if kind in ("mul", "jux"):
        sep = " \\times " if kind == "mul" else " "
        parts = []
        for child in tree[1:]:
            tex = to_latex(child)
            if child[0] in ("add", "sub") or (child[0] == "n" and child[1].startswith("-") and parts):
                tex = _wrap(tex)
            parts.append(tex)
        return sep.join(parts)
    if kind == "div":
        return f"\\frac{{{to_latex(tree[1])}}}{{{to_latex(tree[2])}}}"
    if kind == "add":
        out = to_latex(tree[1])
        for child in tree[2:]:
            out += "+" + to_latex(child)
        return out
    if kind == "sub":
        right = to_latex(tree[2])
        if tree[2][0] in ("add", "sub"):
            right = _wrap(right)
        return f"{to_latex(tree[1])}-{right}"
    if kind == "neg":
        inner = to_latex(tree[1])
        return "-" + (_wrap(inner) if tree[1][0] in ("add", "sub") else inner)
    if kind == "sqrt":
        return f"\\sqrt{{{to_latex(tree[1])}}}"
    if kind == "root":
        return f"\\sqrt[{tree[1]}]{{{to_latex(tree[2])}}}"
    raise ValueError(f"unknown_tree_node:{kind}")


# --- exact value ---------------------------------------------------------------

def exact_simplify(expr: sp.Expr) -> sp.Expr:
    result = sp.simplify(sp.powsimp(sp.expand_power_base(expr, force=True), force=True))
    return sp.simplify(sp.sqrtdenest(sp.radsimp(result)))


def classify(value: sp.Expr) -> str:
    if value.free_symbols:
        return "expression"
    if value.is_Rational:
        return "rational"
    if value.is_algebraic:
        return "radical"
    raise ValueError("non_algebraic_result")


def canonical_text(value: sp.Expr) -> str:
    """Rational as ``p/q``/integer; radicals and expressions as LaTeX."""
    if value.is_Rational:
        return str(value.p) if value.q == 1 else f"{value.p}/{value.q}"
    return sp.latex(value)


def display_latex(value: sp.Expr) -> str:
    if value.is_Rational and value.q != 1:
        sign = "-" if value.p < 0 else ""
        return f"{sign}\\frac{{{abs(value.p)}}}{{{value.q}}}"
    return sp.latex(value)


def numeric_close(a: Any, b: Any, tol: str = "1e-40") -> bool:
    return abs(mp.mpf(a) - mp.mpf(b)) <= mp.mpf(tol) * max(mp.mpf(1), abs(mp.mpf(b)))
