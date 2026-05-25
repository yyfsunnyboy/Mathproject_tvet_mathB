from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .base import ClassificationResult, ClassifierContext


class FallbackClassifier:
    def classify_examples(self, examples: list[dict[str, Any]], context: ClassifierContext) -> ClassificationResult:
        package_dir = context.project_root / "agent_skills_v2" / "_generated" / context.skill_id
        rows: list[dict[str, Any]] = []
        for ex in examples:
            text = _example_text(ex)
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
                    "subskill_id": "unknown",
                    "problem_type_id": "unknown",
                    "runtime_category": "manual_review",
                    "classification_rule_id": "fallback.unknown",
                    "classification_reason": "No skill-specific classifier found; fallback classifier routes to manual review.",
                    "classifier_confidence": "low",
                    "semantic_risk_flags": ["possible_missing_problem_type", "weak_classifier_match"],
                    "semantic_audit_status": "review_required",
                    "generator_status": "manual_review",
                    "manual_review_reason": "Skill-specific classifier/rule pack is missing.",
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

