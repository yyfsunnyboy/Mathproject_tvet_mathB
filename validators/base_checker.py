# -*- coding: utf-8 -*-
import json
import logging
import re
from typing import Any, Tuple, Dict
from sympy.parsing.sympy_parser import parse_expr

logger = logging.getLogger(__name__)

LABEL_ONLY_PATTERN = re.compile(r"^[\(\[]?\s*[A-Da-d]\s*[\)\]\.]?\s*$")

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

        # 3. Sympy parsing check: parse_error
        checker_key = str(answer_contract.get("checker") or answer_contract.get("checker_key") or "").strip()
        is_math = (
            raw_answer_type in {"expression", "equation", "numeric_or_radical", "rational", "fraction", "interval", "solution_set"}
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
                clean_part = part.strip("()[]{} ")
                if not clean_part:
                    continue
                try:
                    parse_expr(clean_part)
                except Exception as e:
                    error = {
                        "can_continue": False,
                        "error_type": "parse_error",
                        "expected": "valid sympifiable expression",
                        "actual": f"{part} (error: {str(e)})"
                    }
                    return False, error

        return True, {}
