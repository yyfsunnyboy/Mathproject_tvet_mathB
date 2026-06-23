# -*- coding: utf-8 -*-
import json
import logging
import re
from typing import Any, Tuple, Dict
from sympy.parsing.sympy_parser import parse_expr

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

        # 4. Sympy parsing check: parse_error
        checker_key = str(answer_contract.get("checker") or answer_contract.get("checker_key") or "").strip()
        is_math = (
            raw_answer_type in {"expression", "numeric_or_radical", "rational", "fraction", "interval", "solution_set"}
            or "expression" in checker_key
            or "solution_set" in checker_key
            or "interval" in checker_key
        )
        if is_math and correct_answer is not None:
            ans_str = str(correct_answer).strip()
            parts = [ans_str]
            if raw_answer_type in {"solution_set", "interval"} or "set" in checker_key or "interval" in checker_key:
                parts = [p.strip() for p in ans_str.replace("或", ",").split(",") if p.strip()]
            
            for part in parts:
                if raw_answer_type in {"solution_set", "interval"} or "set" in checker_key or "interval" in checker_key:
                    clean_part = part.strip("()[] ")
                else:
                    clean_part = part.strip()
                if "\\" not in part:
                    clean_part = clean_part.strip("{} ")
                else:
                    clean_part = clean_part.strip()
                if not clean_part:
                    continue
                try:
                    from sympy import sqrt
                    from core.checkers.expression_equivalence_checker import normalize_math_expression
                    norm_part = normalize_math_expression(clean_part)
                    parse_expr(norm_part, local_dict={"sqrt": sqrt})
                except Exception as e:
                    error = {
                        "can_continue": False,
                        "error_type": "parse_error",
                        "expected": "valid sympifiable expression",
                        "actual": f"{part} (error: {str(e)})"
                    }
                    return False, error

        return True, {}
