from __future__ import annotations

import logging
import math
import re
import unicodedata
from typing import Any

logger = logging.getLogger(__name__)

MAX_INPUT_LEN = 200
_SAFE_CHARS = re.compile(r"^[0-9a-zA-Z+\-*/^().,_\s\\{}$√]+$")

_SQRT_LATEX_BRACE = re.compile(r"\\sqrt\s*\{([^{}]+)\}", re.IGNORECASE)
_SQRT_LATEX_PAREN = re.compile(r"\\sqrt\s*\(([^()]+)\)", re.IGNORECASE)
_SQRT_LATEX_DIGIT = re.compile(r"\\sqrt\s*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE)
_SQRT_UNICODE = re.compile(r"√\(([^()]+)\)")
_SQRT_UNICODE_DIGIT = re.compile(r"√([0-9]+(?:\.[0-9]+)?)")
_SQRT_ASCII_BRACE = re.compile(r"sqrt\s*\{([^{}]+)\}", re.IGNORECASE)
_IMPLICIT_COEF = re.compile(r"(\d)\s*sqrt", re.IGNORECASE)
_IMPLICIT_AFTER_PAREN = re.compile(r"\)\s*sqrt", re.IGNORECASE)


def normalize_math_expression(text: object) -> str:
    """Normalize LaTeX / ascii / unicode radical forms to sympy-friendly text."""
    s = unicodedata.normalize("NFKC", str(text or "").strip())
    if not s:
        return ""
    s = s.replace("$", "").replace("−", "-").replace("×", "*").replace("·", "*")
    for _ in range(3):
        s = _SQRT_LATEX_BRACE.sub(r"sqrt(\1)", s)
        s = _SQRT_LATEX_PAREN.sub(r"sqrt(\1)", s)
        s = _SQRT_LATEX_DIGIT.sub(r"sqrt(\1)", s)
        s = _SQRT_UNICODE.sub(r"sqrt(\1)", s)
        s = _SQRT_UNICODE_DIGIT.sub(r"sqrt(\1)", s)
        s = _SQRT_ASCII_BRACE.sub(r"sqrt(\1)", s)
    s = s.replace("\\", "")
    s = _IMPLICIT_COEF.sub(r"\1*sqrt", s)
    s = _IMPLICIT_AFTER_PAREN.sub(r")*sqrt", s)
    s = re.sub(r"\s+", "", s)
    return s.lower()


def _looks_safe(text: str) -> bool:
    t = str(text or "").strip()
    if not t or len(t) > MAX_INPUT_LEN:
        return False
    if not _SAFE_CHARS.match(t):
        return False
    balance = 0
    for ch in t:
        if ch == "(":
            balance += 1
        elif ch == ")":
            balance -= 1
            if balance < 0:
                return False
    return balance == 0


def _parse_sympy(text: str) -> Any:
    from sympy import Rational, sqrt, sympify
    from sympy.parsing.sympy_parser import (
        convert_xor,
        implicit_multiplication_application,
        parse_expr,
        standard_transformations,
    )

    norm = normalize_math_expression(text)
    if not norm or not _looks_safe(norm):
        raise ValueError("unsafe_or_empty_expression")
    local_dict = {"sqrt": sqrt, "pi": sympify("pi")}
    transformations = standard_transformations + (
        convert_xor,
        implicit_multiplication_application,
    )
    return parse_expr(norm, local_dict=local_dict, transformations=transformations, evaluate=True)


def _numeric_equal(lhs: Any, rhs: Any, *, tol: float = 1e-9) -> bool:
    try:
        from sympy import N

        a = complex(N(lhs))
        b = complex(N(rhs))
        if math.isfinite(a.real) and math.isfinite(b.real) and abs(a.imag) < tol and abs(b.imag) < tol:
            return math.isclose(float(a.real), float(b.real), rel_tol=tol, abs_tol=tol)
        return math.isclose(a.real, b.real, rel_tol=tol, abs_tol=tol) and math.isclose(
            a.imag, b.imag, rel_tol=tol, abs_tol=tol
        )
    except Exception:
        return False


def check_expression_equivalence_debug(user_answer: object, correct_answer: object) -> dict[str, Any]:
    ua_raw = str(user_answer or "").strip()
    ca_raw = str(correct_answer or "").strip()
    out: dict[str, Any] = {
        "correct": False,
        "normalized_user_expression": "",
        "normalized_correct_expression": "",
        "parser_error": "",
        "simplify_result": "",
    }
    if not ua_raw or not ca_raw:
        out["parser_error"] = "empty_answer"
        return out

    out["normalized_user_expression"] = normalize_math_expression(ua_raw)
    out["normalized_correct_expression"] = normalize_math_expression(ca_raw)

    if ua_raw == ca_raw or out["normalized_user_expression"] == out["normalized_correct_expression"]:
        out["correct"] = True
        out["simplify_result"] = "normalized_string_equal"
        return out

    try:
        user_expr = _parse_sympy(ua_raw)
        correct_expr = _parse_sympy(ca_raw)
        from sympy import simplify

        diff = simplify(user_expr - correct_expr)
        out["simplify_result"] = str(diff)
        if diff == 0:
            out["correct"] = True
            return out
        if _numeric_equal(user_expr, correct_expr):
            out["correct"] = True
            out["simplify_result"] = f"numeric_equal:{out['simplify_result']}"
            return out
        out["correct"] = False
        return out
    except Exception as ex:
        out["parser_error"] = str(ex)
        try:
            u_num = float(out["normalized_user_expression"])
            c_num = float(out["normalized_correct_expression"])
            out["correct"] = math.isclose(u_num, c_num, rel_tol=1e-9, abs_tol=1e-9)
            out["simplify_result"] = "float_fallback"
        except Exception:
            out["correct"] = False
        return out


def check_expression_equivalence_answer(user_answer: object, correct_answer: object) -> bool:
    return bool(check_expression_equivalence_debug(user_answer, correct_answer).get("correct"))
