# -*- coding: utf-8 -*-
import json
import logging
import re
from typing import Any, Tuple, Dict

logger = logging.getLogger(__name__)

LABEL_ONLY_PATTERN = re.compile(r"^[\(\[]?\s*[A-Da-d]\s*[\)\]\.]?\s*$")


def _is_linear_equation_contract(answer_contract: dict[str, Any]) -> bool:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    checker_key = str(ac.get("checker") or ac.get("checker_key") or "").strip()
    answer_shape = str(ac.get("answer_shape", "")).strip()
    equiv = str(ac.get("equivalence_type") or ac.get("answer_equivalence", "")).strip()
    answer_type = str(ac.get("answer_type", "")).strip().lower()
    return (
        checker_key == "linear_equation_equivalent_checker"
        or answer_shape == "linear_equation"
        or equiv == "linear_equation_equivalent"
        or answer_type == "equation"
    )


def _validate_linear_equation_answer(correct_answer: Any) -> tuple[bool, dict[str, Any]]:
    from core.checkers.linear_equation_equivalent_checker import (
        canonicalize_linear_equation,
        check_linear_equation_equivalent_answer,
    )

    if correct_answer is None:
        return False, {
            "can_continue": False,
            "error_type": "parse_error",
            "expected": "non-empty linear equation",
            "actual": "None",
        }
    ans_str = str(correct_answer).strip()
    if not ans_str:
        return False, {
            "can_continue": False,
            "error_type": "parse_error",
            "expected": "non-empty linear equation",
            "actual": "",
        }
    if LABEL_ONLY_PATTERN.match(ans_str):
        return False, {
            "can_continue": False,
            "error_type": "parse_error",
            "expected": "linear equation string",
            "actual": ans_str,
        }
    if canonicalize_linear_equation(ans_str) is None:
        return False, {
            "can_continue": False,
            "error_type": "parse_error",
            "expected": "parseable linear equation",
            "actual": ans_str,
        }
    if not check_linear_equation_equivalent_answer(ans_str, ans_str):
        return False, {
            "can_continue": False,
            "error_type": "parse_error",
            "expected": "checker self-test pass",
            "actual": ans_str,
        }
    return True, {}


class BaseChecker:
    """
    Base Checker class for contract validation.
    Provides standard validation framework and upgrades semantic errors to blocker signals.
    """
    def __init__(self):
        pass

    def check(self, payload: Dict[str, Any], spec: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Runs check. Returns (can_continue, error_json).
        """
        answer_contract = spec.get("answer_contract", {}) or spec.get("answer_contract_proposal", {}) or {}
        raw_answer_type = str(answer_contract.get("answer_type", "")).strip().lower()
        
        choices = payload.get("choices") or []
        correct_answer = payload.get("answer") if payload.get("answer") is not None else payload.get("correct_answer")
        
        # 1. Option count check: choice_count_mismatch
        if raw_answer_type in {"choice", "single_choice", "multi_choice", "multiple_choice"}:
            expected_count = int(answer_contract.get("choice_count", 4) or 4)
            actual_count = len(choices)
            if actual_count != expected_count:
                error = {
                    "can_continue": False,
                    "error_type": "choice_count_mismatch",
                    "expected": expected_count,
                    "actual": actual_count
                }
                return False, error

            # 2. Answer not in choices check: answer_not_in_choices
            choices_texts = []
            for ch in choices:
                if isinstance(ch, dict):
                    choices_texts.append(str(ch.get("text", "")).strip())
                else:
                    choices_texts.append(str(ch).strip())

            ans_str = str(correct_answer).strip()
            if LABEL_ONLY_PATTERN.match(ans_str):
                labels = {chr(ord("A") + i) for i in range(len(choices_texts))}
                ans_clean = ans_str.strip("()[] .").upper()
                if ans_clean not in labels:
                    error = {
                        "can_continue": False,
                        "error_type": "answer_not_in_choices",
                        "expected": list(labels),
                        "actual": ans_str
                    }
                    return False, error
            else:
                if ans_str not in choices_texts:
                    error = {
                        "can_continue": False,
                        "error_type": "answer_not_in_choices",
                        "expected": choices_texts,
                        "actual": ans_str
                    }
                    return False, error

        # 3. Linear equation contract: use dedicated checker, not sympy/choice parsers.
        if _is_linear_equation_contract(answer_contract):
            ok, error = _validate_linear_equation_answer(correct_answer)
            if not ok:
                return False, error
            return True, {}

        # 4. Interval / solution-set: do not force sympy expression parsing.
        checker_key = str(answer_contract.get("checker") or answer_contract.get("checker_key") or "").strip()
        is_interval_like = (
            raw_answer_type in {"interval", "solution_set", "interval_set"}
            or "interval" in checker_key
            or "solution_set" in checker_key
        )
        if is_interval_like and correct_answer is not None:
            ans_str = str(correct_answer).strip()
            if not ans_str:
                return False, {
                    "can_continue": False,
                    "error_type": "parse_error",
                    "expected": "non-empty interval or solution set",
                    "actual": "",
                }
            # Lightweight structural gate; official interval_checker handles semantics.
            if any(token in ans_str for token in ("<", ">", "≤", "≥", "[", "]", "(", ")", "∞", "∪", "或", ",")):
                return True, {}
            if ans_str in {"空集合", "∅", "无解", "所有實數", "R", "ℝ"}:
                return True, {}
            return False, {
                "can_continue": False,
                "error_type": "parse_error",
                "expected": "interval/solution-set notation",
                "actual": ans_str,
            }

        # 5. Sympy parsing check: parse_error (expressions / numeric radicals)
        is_math = (
            raw_answer_type in {"expression", "numeric_or_radical", "rational", "fraction"}
            or "expression" in checker_key
        )
        if is_math and correct_answer is not None:
            ans_str = str(correct_answer).strip()
            parts = [ans_str]
            for part in parts:
                clean_part = part.strip()
                if "\\" not in part:
                    clean_part = clean_part.strip("{} ")
                if not clean_part:
                    continue
                # Factored forms like (x+1)(x-2) need an explicit multiply for sympy.
                clean_part = re.sub(r"\)\s*\(", ")*(", clean_part)
                try:
                    from sympy import sqrt
                    from sympy.parsing.sympy_parser import (
                        parse_expr,
                        standard_transformations,
                        implicit_multiplication_application,
                    )
                    from core.checkers.expression_equivalence_checker import normalize_math_expression
                    norm_part = normalize_math_expression(clean_part)
                    transformations = standard_transformations + (implicit_multiplication_application,)
                    parse_expr(
                        norm_part,
                        local_dict={"sqrt": sqrt},
                        transformations=transformations,
                    )
                except ModuleNotFoundError as exc:
                    if "sympy" in str(exc):
                        error = {
                            "can_continue": False,
                            "error_type": "system_error",
                            "error_code": "sympy_dependency_missing",
                            "expected": "sympy package available for symbolic validation",
                            "actual": str(exc),
                        }
                        return False, error
                    raise
                except Exception as e:
                    error = {
                        "can_continue": False,
                        "error_type": "parse_error",
                        "expected": "valid sympifiable expression",
                        "actual": f"{part} (error: {str(e)})"
                    }
                    return False, error

        return True, {}
