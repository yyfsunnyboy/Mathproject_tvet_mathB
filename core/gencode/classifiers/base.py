from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

REQUIRED_EXAMPLE_FIELDS = [
    "example_id",
    "title",
    "source_type",
    "source_chapter",
    "source_section",
    "problem_preview",
    "problem_text_hash",
    "skill_id",
    "subskill_id",
    "problem_type_id",
    "runtime_category",
    "classification_rule_id",
    "classification_reason",
    "classifier_confidence",
    "semantic_risk_flags",
    "semantic_audit_status",
    "generator_status",
    "manual_review_reason",
]

DETERMINISTIC_RUNTIME_CATEGORIES = {
    "deterministic_numeric",
    "deterministic_expression",
    "deterministic_choice",
}


@dataclass
class ClassifierContext:
    project_root: Path
    skill_id: str


@dataclass
class ClassificationResult:
    package_dir: Path
    examples_map_entries: list[dict[str, Any]]


class SkillClassifier(Protocol):
    def classify_examples(self, examples: list[dict[str, Any]], context: ClassifierContext) -> ClassificationResult: ...

