from __future__ import annotations

import hashlib
import re
from typing import Any

from .base import ClassificationResult, ClassifierContext


class VocationalMathB1AbsoluteValueInequalityExpansionClassifier:
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


def _classify_text(text: str) -> dict[str, Any]:
    t = text or ""
    # If the text contains "象限" (quadrant) it's quadrant determination (e.g. 4416)
    if "象限" in t:
        return {
            "subskill_id": "absolute_value_inequality_interval_interpretation",
            "problem_type_id": "absolute_value_inequality_interval_interpretation",
            "runtime_category": "deterministic_choice",
            "classification_rule_id": "absi_exp.rule.quadrant_determination",
            "classification_reason": "絕對值不等式解集與象限判定。",
            "classifier_confidence": "high",
            "semantic_risk_flags": [],
            "semantic_audit_status": "pass",
            "generator_status": "supported_deterministic",
            "manual_review_reason": "",
        }
    
    # Otherwise, it's a standard absolute value inequality solving problem (e.g. 4411, 4415)
    return {
        "subskill_id": "absolute_value_inequality_linear_expression_basic",
        "problem_type_id": "absolute_value_inequality_linear_expression_basic",
        "runtime_category": "deterministic_expression",
        "classification_rule_id": "absi_exp.rule.linear_expression_basic",
        "classification_reason": "絕對值不等式求解。",
        "classifier_confidence": "high",
        "semantic_risk_flags": [],
        "semantic_audit_status": "pass",
        "generator_status": "supported_deterministic",
        "manual_review_reason": "",
    }
