from __future__ import annotations

import hashlib
import re
from typing import Any

from .base import ClassificationResult, ClassifierContext


class VocationalMathB1AbsoluteValueInequalityClassifier:
    def classify_examples(self, examples: list[dict[str, Any]], context: ClassifierContext) -> ClassificationResult:
        package_dir = context.project_root / "agent_skills_v2" / "_generated" / context.skill_id
        rows: list[dict[str, Any]] = []
        for ex in examples:
            text = _example_text(ex)
            c = _classify_text(text)
            rows.append(
                {
                    "example_id": ex.get("id"),
                    "title": str(ex.get("title", "") or ""),
                    "source_type": "textbook_example",
                    "source_chapter": "unknown",
                    "source_section": "unknown",
                    "problem_preview": text[:200],
                    "problem_text_hash": hashlib.sha1(text.encode("utf-8")).hexdigest() if text else "",
                    "skill_id": context.skill_id,
                    "subskill_id": c["subskill_id"],
                    "problem_type_id": c["problem_type_id"],
                    "runtime_category": c["runtime_category"],
                    "classification_rule_id": c["classification_rule_id"],
                    "classification_reason": c["classification_reason"],
                    "classifier_confidence": c["classifier_confidence"],
                    "semantic_risk_flags": c["semantic_risk_flags"],
                    "semantic_audit_status": c["semantic_audit_status"],
                    "generator_status": c["generator_status"],
                    "manual_review_reason": c["manual_review_reason"],
                }
            )
        return ClassificationResult(package_dir=package_dir, examples_map_entries=rows)


def _example_text(ex: dict[str, Any]) -> str:
    parts = []
    for k in ("problem_text", "problem", "question", "stem", "content", "title"):
        val = ex.get(k)
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
    t = " ".join(parts)
    t = t.replace("\\left|", "|").replace("\\right|", "|")
    t = t.replace("\\le", "<=").replace("\\ge", ">=")
    t = t.replace("≤", "<=").replace("≥", ">=")
    return t


def _is_choice_count(t: str) -> bool:
    return ("整數x共有多少個" in t or "整數 x 共有多少個" in t or "共有多少個" in t) and any(
        c in t for c in ["(A)", "(B)", "(C)", "(D)", "（A）", "（B）", "（C）", "（D）"]
    )


def _is_malformed(t: str) -> bool:
    if "|x|3" in t:
        return True
    if re.search(r"\|\s*x\s*\|\s*\$?\s*\d", t):
        return True
    return ("|" in t or "\\left|" in t) and not any(op in t for op in ["<", ">", "<=", ">="])


def _is_linear(t: str) -> bool:
    m = re.search(r"\|\s*([1-9]\d*)\s*x\s*[\+\-]\s*\d+\s*\|", t)
    if not m:
        return False
    return int(m.group(1)) not in {1}


def _is_shifted(t: str) -> bool:
    return bool(re.search(r"\|\s*x\s*[\+\-]\s*\d+\s*\|", t))


def _is_zero_center(t: str) -> bool:
    return bool(re.search(r"\|\s*x\s*\|", t)) and any(op in t for op in ["<", ">", "<=", ">="])


def _classify_text(text: str) -> dict[str, Any]:
    t = text or ""
    if _is_choice_count(t):
        return {
            "subskill_id": "absolute_value_inequality_integer_solution_count_choice",
            "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
            "runtime_category": "deterministic_choice",
            "classification_rule_id": "absi.rule.integer_solution_count_choice",
            "classification_reason": "整數解個數選擇題。",
            "classifier_confidence": "high",
            "semantic_risk_flags": [],
            "semantic_audit_status": "pass",
            "generator_status": "supported_deterministic",
            "manual_review_reason": "",
        }
    if _is_malformed(t):
        return {
            "subskill_id": "absolute_value_inequality_malformed_source_review",
            "problem_type_id": "absolute_value_inequality_malformed_source_review",
            "runtime_category": "manual_review",
            "classification_rule_id": "absi.rule.malformed_source_review",
            "classification_reason": "題幹疑似缺漏或格式錯誤，需人工審查。",
            "classifier_confidence": "medium",
            "semantic_risk_flags": ["source_text_malformed", "needs_import_review"],
            "semantic_audit_status": "review_required",
            "generator_status": "manual_review",
            "manual_review_reason": "Malformed absolute value inequality source text.",
        }
    if _is_linear(t):
        return {
            "subskill_id": "absolute_value_inequality_linear_expression_basic",
            "problem_type_id": "absolute_value_inequality_linear_expression_basic",
            "runtime_category": "deterministic_expression",
            "classification_rule_id": "absi.rule.linear_expression_basic",
            "classification_reason": "|ax+b| 不等式（a 非 1）",
            "classifier_confidence": "high",
            "semantic_risk_flags": [],
            "semantic_audit_status": "pass",
            "generator_status": "supported_deterministic",
            "manual_review_reason": "",
        }
    if _is_shifted(t):
        return {
            "subskill_id": "absolute_value_inequality_shifted_basic",
            "problem_type_id": "absolute_value_inequality_shifted_basic",
            "runtime_category": "deterministic_expression",
            "classification_rule_id": "absi.rule.shifted_basic",
            "classification_reason": "|x-a| / |x+a| 型不等式。",
            "classifier_confidence": "high",
            "semantic_risk_flags": [],
            "semantic_audit_status": "pass",
            "generator_status": "supported_deterministic",
            "manual_review_reason": "",
        }
    if _is_zero_center(t):
        return {
            "subskill_id": "absolute_value_inequality_zero_center_basic",
            "problem_type_id": "absolute_value_inequality_zero_center_basic",
            "runtime_category": "deterministic_expression",
            "classification_rule_id": "absi.rule.zero_center_basic",
            "classification_reason": "|x| 型不等式。",
            "classifier_confidence": "high",
            "semantic_risk_flags": [],
            "semantic_audit_status": "pass",
            "generator_status": "supported_deterministic",
            "manual_review_reason": "",
        }
    return {
        "subskill_id": "absolute_value_inequality_malformed_source_review",
        "problem_type_id": "absolute_value_inequality_malformed_source_review",
        "runtime_category": "manual_review",
        "classification_rule_id": "absi.rule.fallback_manual_review",
        "classification_reason": "無法匹配規則，需人工審查。",
        "classifier_confidence": "low",
        "semantic_risk_flags": ["possible_missing_problem_type", "weak_classifier_match"],
        "semantic_audit_status": "review_required",
        "generator_status": "manual_review",
        "manual_review_reason": "Classifier rule unmatched for this example.",
    }

