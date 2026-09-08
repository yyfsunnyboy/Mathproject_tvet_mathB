from __future__ import annotations

import logging
import math
import re
import unicodedata
from typing import Any

logger = logging.getLogger(__name__)

MAX_INPUT_LEN = 200
_SAFE_CHARS = re.compile(r"^[0-9a-zA-Z+\-*/^=().,_\s\\{}$√]+$")

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
    s = (
        s.replace("$", "")
        .replace("−", "-")
        .replace("－", "-")
        .replace("×", "*")
        .replace("·", "*")
        .replace("（", "(")
        .replace("）", ")")
        .replace("＝", "=")
        .replace("，", ",")
    )
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


_FACTORIZED_FORMS = frozenset({"factorized", "factored", "factorization", "factored_expression", "factorized_expression"})
_FACTORIZED_EQUIVS = frozenset({"factorized_form", "required_factorized_form"})


def contract_requires_factorized_form(
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> bool:
    """Required-form is contract-driven, not skill/example specific."""
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    pl = payload if isinstance(payload, dict) else {}
    required = str(ac.get("required_form") or pl.get("required_form") or "").strip().lower()
    if required in _FACTORIZED_FORMS:
        return True
    shape = str(ac.get("answer_shape") or pl.get("answer_shape") or "").strip().lower()
    if shape in _FACTORIZED_FORMS:
        return True
    equiv = str(
        ac.get("answer_equivalence")
        or ac.get("equivalence_type")
        or pl.get("equivalence")
        or pl.get("equivalence_type")
        or ""
    ).strip().lower()
    if equiv in _FACTORIZED_EQUIVS:
        return True
    problem_type = str(
        ac.get("problem_type_id") or pl.get("problem_type_id") or ""
    ).strip().lower()
    return "factoring" in problem_type or "factorization" in problem_type


def _assignment_lists_equivalent(user_answer: object, correct_answer: object) -> bool | None:
    """Compare comma-separated assignments like a=-1,b=-3 without string identity.

    Returns True/False when both sides look like assignment lists; None otherwise.
    """
    def _parse_map(text: str) -> dict[str, Any] | None:
        norm = normalize_math_expression(text)
        if "," not in norm or "=" not in norm:
            return None
        mapping: dict[str, Any] = {}
        for chunk in norm.split(","):
            if "=" not in chunk:
                return None
            key, raw_val = chunk.split("=", 1)
            if not re.fullmatch(r"[a-z]+", key) or not raw_val:
                return None
            mapping[key] = _parse_sympy(raw_val)
        return mapping or None

    try:
        user_map = _parse_map(str(user_answer or ""))
        correct_map = _parse_map(str(correct_answer or ""))
    except Exception:
        return None
    if user_map is None or correct_map is None:
        return None
    if set(user_map) != set(correct_map):
        return False
    from sympy import simplify

    for key, value in user_map.items():
        if simplify(value - correct_map[key]) != 0 and not _numeric_equal(value, correct_map[key]):
            return False
    return True


def _is_factorized_expression(expr: Any) -> bool:
    """True when the parsed expression is already a product of non-constant factors."""
    try:
        if expr is None:
            return False
        if not getattr(expr, "free_symbols", None):
            return True
        if expr.is_Mul:
            nonconst = [arg for arg in expr.args if getattr(arg, "free_symbols", None)]
            if len(nonconst) >= 2:
                return True
            return any(getattr(arg, "is_Pow", False) and arg.exp != 1 for arg in nonconst)
        if expr.is_Pow and expr.exp != 1:
            return True
        if expr.is_Add:
            try:
                from sympy import degree, Poly

                symbols = list(expr.free_symbols)
                if len(symbols) == 1:
                    return int(degree(Poly(expr, symbols[0]))) <= 1
            except Exception:
                return False
            return False
        return False
    except Exception:
        return False


def check_expression_equivalence_debug(
    user_answer: object,
    correct_answer: object,
    *,
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    require_factorized: bool | None = None,
) -> dict[str, Any]:
    ua_raw = str(user_answer or "").strip()
    ca_raw = str(correct_answer or "").strip()
    out: dict[str, Any] = {
        "correct": False,
        "normalized_user_expression": "",
        "normalized_correct_expression": "",
        "parser_error": "",
        "simplify_result": "",
        "error_code": "",
        "required_form_failed": False,
    }
    if not ua_raw or not ca_raw:
        out["parser_error"] = "empty_answer"
        out["error_code"] = "ANSWER_PARSE_FAILED"
        return out

    out["normalized_user_expression"] = normalize_math_expression(ua_raw)
    out["normalized_correct_expression"] = normalize_math_expression(ca_raw)
    need_form = (
        require_factorized
        if require_factorized is not None
        else contract_requires_factorized_form(answer_contract, payload)
    )

    assign_eq = _assignment_lists_equivalent(ua_raw, ca_raw)
    if assign_eq is True:
        out["correct"] = True
        out["simplify_result"] = "assignment_list_equivalent"
        return out
    if assign_eq is False:
        out["correct"] = False
        out["simplify_result"] = "assignment_list_mismatch"
        return out

    try:
        user_expr = _parse_sympy(ua_raw)
        correct_expr = _parse_sympy(ca_raw)
        from sympy import simplify

        diff = simplify(user_expr - correct_expr)
        out["simplify_result"] = str(diff)
        algebraically_equal = diff == 0 or _numeric_equal(user_expr, correct_expr)
        if not algebraically_equal:
            out["correct"] = False
            return out
        if need_form and not _is_factorized_expression(user_expr):
            out["correct"] = False
            out["required_form_failed"] = True
            out["simplify_result"] = "required_form_failed"
            return out
        out["correct"] = True
        return out
    except Exception as ex:
        if out["normalized_user_expression"] == out["normalized_correct_expression"]:
            out["correct"] = True
            out["simplify_result"] = "normalized_identity"
            return out
        out["parser_error"] = str(ex)
        out["error_code"] = "ANSWER_PARSE_FAILED"
        out["correct"] = False
        return out


def check_expression_equivalence_answer(
    user_answer: object,
    correct_answer: object,
    *,
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    require_factorized: bool | None = None,
) -> bool:
    return bool(
        check_expression_equivalence_debug(
            user_answer,
            correct_answer,
            answer_contract=answer_contract,
            payload=payload,
            require_factorized=require_factorized,
        ).get("correct")
    )


def check_equation_equivalence_debug(
    user_answer: object,
    correct_answer: object,
) -> dict[str, Any]:
    """Equation equivalence: same solution set / constant-multiple of (lhs-rhs)."""
    out: dict[str, Any] = {
        "correct": False,
        "normalized_user_expression": "",
        "normalized_correct_expression": "",
        "parser_error": "",
        "simplify_result": "",
        "error_code": "",
    }
    ua_raw = str(user_answer or "").strip()
    ca_raw = str(correct_answer or "").strip()
    if not ua_raw or not ca_raw:
        out["parser_error"] = "empty_answer"
        out["error_code"] = "ANSWER_PARSE_FAILED"
        return out
    out["normalized_user_expression"] = normalize_math_expression(ua_raw)
    out["normalized_correct_expression"] = normalize_math_expression(ca_raw)
    if "=" not in out["normalized_user_expression"] or "=" not in out["normalized_correct_expression"]:
        out["parser_error"] = "not_an_equation"
        out["error_code"] = "ANSWER_PARSE_FAILED"
        return out

    try:
        from core.checkers.linear_equation_equivalent_checker import check_linear_equation_equivalent_answer

        if check_linear_equation_equivalent_answer(user_answer, correct_answer):
            out["correct"] = True
            out["simplify_result"] = "linear_equation_equivalent"
            return out
    except Exception:
        pass

    try:
        from sympy import simplify

        def _diff_poly(text: str) -> Any:
            left, right = normalize_math_expression(text).split("=", 1)
            return _parse_sympy(left) - _parse_sympy(right)

        user_diff = _diff_poly(ua_raw)
        correct_diff = _diff_poly(ca_raw)
        if simplify(correct_diff) == 0:
            out["correct"] = bool(simplify(user_diff) == 0)
            out["simplify_result"] = "identity_equation"
            return out
        ratio = simplify(user_diff / correct_diff)
        out["simplify_result"] = str(ratio)
        out["correct"] = bool(getattr(ratio, "is_number", False) and ratio != 0)
        return out
    except Exception as ex:
        out["parser_error"] = str(ex)
        out["error_code"] = "ANSWER_PARSE_FAILED"
        out["correct"] = False
        return out


def check_equation_equivalence_answer(user_answer: object, correct_answer: object) -> bool:
    return bool(check_equation_equivalence_debug(user_answer, correct_answer).get("correct"))
