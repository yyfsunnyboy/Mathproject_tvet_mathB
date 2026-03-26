# -*- coding: utf-8 -*-
from __future__ import annotations

from fractions import Fraction
import math


def _normalize_text(value: object) -> str:
    text = str(value or "").strip()
    return (
        text.replace(" ", "")
        .replace("$", "")
        .replace("\\left", "")
        .replace("\\right", "")
        .replace("{", "")
        .replace("}", "")
        .lower()
    )


def _as_fraction(value: str) -> Fraction | None:
    cleaned = value.replace("－", "-").replace("／", "/")
    try:
        return Fraction(cleaned)
    except Exception:
        return None


def _as_float(value: str) -> float | None:
    try:
        return float(value)
    except Exception:
        frac = _as_fraction(value)
        return float(frac) if frac is not None else None


def _as_symbolic(value: str):
    try:
        from sympy import Rational, Symbol, sqrt, sympify
        from sympy.parsing.sympy_parser import (
            convert_xor,
            implicit_multiplication_application,
            standard_transformations,
            parse_expr,
        )

        text = _normalize_text(value)
        if not text:
            return None
        local_dict = {
            "x": Symbol("x"),
            "sqrt": sqrt,
            "pi": sympify("pi"),
        }
        transformations = standard_transformations + (
            convert_xor,
            implicit_multiplication_application,
        )
        return parse_expr(text, local_dict=local_dict, transformations=transformations, evaluate=True)
    except Exception:
        return None


def judge_answer(user_answer: object, correct_answer: object) -> bool:
    user_text = _normalize_text(user_answer)
    correct_text = _normalize_text(correct_answer)

    if not user_text or not correct_text:
        return False
    if user_text == correct_text:
        return True

    user_num = _as_float(user_text)
    correct_num = _as_float(correct_text)
    if user_num is not None and correct_num is not None:
        return math.isclose(user_num, correct_num, rel_tol=1e-9, abs_tol=1e-9)

    user_frac = _as_fraction(user_text)
    correct_frac = _as_fraction(correct_text)
    if user_frac is not None and correct_frac is not None:
        return user_frac == correct_frac

    user_sym = _as_symbolic(user_text)
    correct_sym = _as_symbolic(correct_text)
    if user_sym is not None and correct_sym is not None:
        try:
            from sympy import simplify
            return simplify(user_sym - correct_sym) == 0
        except Exception:
            pass

    return False
