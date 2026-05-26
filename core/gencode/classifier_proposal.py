from __future__ import annotations

import re
from collections import defaultdict
from typing import Any


def _norm_text(text: object) -> str:
    s = str(text or "").strip()
    s = s.replace("\\left|", "|").replace("\\right|", "|")
    s = s.replace("\\le", "<=").replace("\\ge", ">=")
    s = s.replace("≤", "<=").replace("≥", ">=")
    return s


def _is_choice_text(s: str) -> bool:
    return any(token in s for token in ["(A)", "(B)", "(C)", "(D)", "（A）", "（B）", "（C）", "（D）"])


def _is_count_question(s: str) -> bool:
    return "共有多少個" in s or "有多少個" in s


def _is_malformed_abs_inequality(s: str) -> bool:
    # e.g. "|x|3" without comparator
    if "|x|3" in s:
        return True
    if re.search(r"\|\s*x\s*\|\s*\$?\s*\d", s):
        return True
    return "|x|" in s and not any(op in s for op in ["<", ">", "<=", ">="])


def _is_zero_center_abs_inequality(s: str) -> bool:
    return bool(re.search(r"\|\s*x\s*\|", s)) and any(op in s for op in ["<", ">", "<=", ">="])


def _is_shifted_abs_inequality(s: str) -> bool:
    return bool(re.search(r"\|\s*x\s*[\+\-]\s*\d+\s*\|", s))


def _is_linear_abs_inequality(s: str) -> bool:
    # |ax+b| with a != 0
    return bool(re.search(r"\|\s*[1-9]\d*\s*x\s*[\+\-]\s*\d+\s*\|", s))


def _proposed_contracts() -> dict[str, dict[str, Any]]:
    return {
        "absolute_value_inequality_zero_center_basic": {
            "answer_type": "interval_set",
            "equivalence_type": "interval_set",
            "checker_key": "interval_checker",
            "order_matters": False,
            "accepted_format_notes": ["x > a", "x < a", "x ≤ a", "x ≥ a", "interval notation"],
            "canonical_answer_schema": {"type": "interval_set"},
        },
        "absolute_value_inequality_shifted_basic": {
            "answer_type": "interval_set",
            "equivalence_type": "interval_set",
            "checker_key": "interval_checker",
            "order_matters": False,
            "accepted_format_notes": ["x > a", "x < a", "x ≤ a", "x ≥ a", "interval notation"],
            "canonical_answer_schema": {"type": "interval_set"},
        },
        "absolute_value_inequality_linear_expression_basic": {
            "answer_type": "interval_set",
            "equivalence_type": "interval_set",
            "checker_key": "interval_checker",
            "order_matters": False,
            "accepted_format_notes": ["x > a", "x < a", "x ≤ a", "x ≥ a", "interval notation"],
            "canonical_answer_schema": {"type": "interval_set"},
        },
        "absolute_value_inequality_integer_solution_count_choice": {
            "answer_type": "choice",
            "equivalence_type": "choice_label",
            "checker_key": "choice_label_checker",
            "order_matters": True,
            "accepted_format_notes": ["A/B/C/D labels"],
            "canonical_answer_schema": {"type": "choice_label"},
        },
        "absolute_value_inequality_malformed_source_review": {
            "answer_type": "manual_review",
            "equivalence_type": "manual_review_or_ai_judged",
            "checker_key": "manual_review_checker",
            "order_matters": False,
            "accepted_format_notes": ["requires source text correction before deterministic generation"],
            "canonical_answer_schema": {"type": "manual_review"},
        },
    }


def build_classifier_proposal(skill_id: str, examples_map: list[dict[str, Any]]) -> dict[str, Any]:
    proposed_example_map: list[dict[str, Any]] = []
    grouped: dict[str, list[int]] = defaultdict(list)
    manual_review_candidates: list[int] = []
    risk_flags: list[str] = []

    for e in examples_map:
        exid = e.get("example_id")
        text = _norm_text(e.get("problem_preview") or e.get("problem_text") or e.get("question_text"))
        pt = "absolute_value_inequality_linear_expression_basic"

        if _is_malformed_abs_inequality(text):
            pt = "absolute_value_inequality_malformed_source_review"
            if isinstance(exid, int):
                manual_review_candidates.append(exid)
        elif _is_choice_text(text) and _is_count_question(text):
            pt = "absolute_value_inequality_integer_solution_count_choice"
        elif _is_linear_abs_inequality(text):
            pt = "absolute_value_inequality_linear_expression_basic"
        elif _is_shifted_abs_inequality(text):
            pt = "absolute_value_inequality_shifted_basic"
        elif _is_zero_center_abs_inequality(text):
            pt = "absolute_value_inequality_zero_center_basic"
        else:
            pt = "absolute_value_inequality_malformed_source_review"
            if isinstance(exid, int):
                manual_review_candidates.append(exid)

        if isinstance(exid, int):
            grouped[pt].append(exid)
        proposed_example_map.append(
            {
                "example_id": exid,
                "proposed_problem_type_id": pt,
                "reason": "heuristic_pattern_match",
                "problem_preview": text[:160],
            }
        )

    if manual_review_candidates:
        risk_flags.append("contains_malformed_or_unclassified_examples")

    proposed_problem_types = sorted(grouped.keys())
    contracts = _proposed_contracts()
    proposed_answer_contracts = {k: contracts[k] for k in proposed_problem_types if k in contracts}

    return {
        "skill_id": skill_id,
        "proposed_problem_types": proposed_problem_types,
        "proposed_example_map": proposed_example_map,
        "proposed_answer_contracts": proposed_answer_contracts,
        "manual_review_candidates": sorted(set(manual_review_candidates)),
        "risk_flags": risk_flags,
    }
