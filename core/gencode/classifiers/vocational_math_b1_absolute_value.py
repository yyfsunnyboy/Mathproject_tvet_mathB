from __future__ import annotations

import hashlib
from typing import Any

from .base import ClassificationResult, ClassifierContext


class VocationalMathB1AbsoluteValueClassifier:
    def classify_examples(self, examples: list[dict[str, Any]], context: ClassifierContext) -> ClassificationResult:
        package_dir = context.project_root / "agent_skills_v2" / "vocational_math_b1" / "chapter_1" / "section_1_1_number_line_absolute_value"
        rows: list[dict[str, Any]] = []
        for ex in examples:
            text = _example_text(ex)
            c = _classify_text(text)
            rows.append(
                {
                    "example_id": ex.get("id"),
                    "title": str(ex.get("title", "") or ""),
                    "source_type": "textbook_example",
                    "source_chapter": "chapter_1",
                    "source_section": "section_1_1_number_line_absolute_value",
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
    return " ".join(parts)


def _classify_text(text: str) -> dict[str, Any]:
    t = text or ""
    if "A\\left(" in t and "B\\left(" in t:
        return {
            "subskill_id": "absolute_value_distance_between_two_points",
            "problem_type_id": "absolute_value_distance_between_two_points",
            "runtime_category": "deterministic_numeric",
            "classification_rule_id": "absv.rule.distance_between_points",
            "classification_reason": "題目要求求數線上兩點距離，可用兩坐標差的絕對值計算。",
            "classifier_confidence": "high",
            "semantic_risk_flags": [],
            "semantic_audit_status": "pass",
            "generator_status": "supported_deterministic",
            "manual_review_reason": "",
        }
    if "|x|" in t or "\\left| x \\right|" in t:
        if "=" in t:
            return {
                "subskill_id": "absolute_value_equation_basic",
                "problem_type_id": "absolute_value_equation_basic",
                "runtime_category": "deterministic_expression",
                "classification_rule_id": "absv.rule.equation_basic",
                "classification_reason": "題目要求解 $|x|=a$ 的基本絕對值方程。",
                "classifier_confidence": "high",
                "semantic_risk_flags": [],
                "semantic_audit_status": "pass",
                "generator_status": "supported_deterministic",
                "manual_review_reason": "",
            }
    if "絕對值" in t and "距離" in t and "0" in t:
        return {
            "subskill_id": "absolute_value_distance_from_zero",
            "problem_type_id": "absolute_value_distance_from_zero",
            "runtime_category": "deterministic_choice",
            "classification_rule_id": "absv.rule.distance_from_zero_meaning",
            "classification_reason": "絕對值語意題：判斷數到 0 的距離。",
            "classifier_confidence": "medium",
            "semantic_risk_flags": [],
            "semantic_audit_status": "pass",
            "generator_status": "supported_deterministic",
            "manual_review_reason": "",
        }
    if "|" in t:
        return {
            "subskill_id": "absolute_value_numeric_evaluation",
            "problem_type_id": "absolute_value_numeric_evaluation",
            "runtime_category": "deterministic_numeric",
            "classification_rule_id": "absv.rule.numeric_eval",
            "classification_reason": "絕對值數值計算題。",
            "classifier_confidence": "medium",
            "semantic_risk_flags": [],
            "semantic_audit_status": "pass",
            "generator_status": "supported_deterministic",
            "manual_review_reason": "",
        }
    return {
        "subskill_id": "unknown",
        "problem_type_id": "unknown",
        "runtime_category": "manual_review",
        "classification_rule_id": "absv.rule.unknown",
        "classification_reason": "無法匹配既有規則，需人工審查。",
        "classifier_confidence": "low",
        "semantic_risk_flags": ["possible_missing_problem_type", "weak_classifier_match"],
        "semantic_audit_status": "review_required",
        "generator_status": "manual_review",
        "manual_review_reason": "Classifier rule unmatched for this example.",
    }

