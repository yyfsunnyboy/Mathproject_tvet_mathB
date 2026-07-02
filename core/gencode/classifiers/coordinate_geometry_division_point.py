from __future__ import annotations

import hashlib
import re
from typing import Any

from .base import ClassificationResult, ClassifierContext


_POINT_COORDINATE = re.compile(r"[A-Z]\s*(?:\\left)?\s*\(\s*[^)]+\s*(?:\\right)?\s*\)", re.I)
_CENTROID = re.compile(r"重心|centroid|形心|�ߧ��", re.I)
_SEGMENT_RATIO = re.compile(
    r"\\overline\{\s*[A-Z]{2}\s*\}\s*:\s*\\overline\{\s*[A-Z]{2}\s*\}"
    r"|(?:\d+\s*)?\\overline\{\s*[A-Z]{2}\s*\}\s*=\s*(?:\d+\s*)?\\overline\{\s*[A-Z]{2}\s*\}"
    r"|\b[A-Z]{2}\s*:\s*[A-Z]{2}\s*=\s*\d+\s*:\s*\d+"
    r"|\b[A-Z]{2}\s*=\s*\d+\s*[A-Z]{2}\b",
    re.I,
)
_CHOICE_MARKER = re.compile(r"\([A-D]\)", re.I)
_COORDINATE_CHOICE = re.compile(
    r"\([A-D]\)\s*\$?\s*(?:\\left)?\s*\(\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?",
    re.I,
)


class CoordinateGeometryDivisionPointClassifier:
    def classify_examples(
        self,
        examples: list[dict[str, Any]],
        context: ClassifierContext,
    ) -> ClassificationResult:
        rows = [_classify_example(example, context.skill_id) for example in examples]
        package_dir = context.project_root / "agent_skills_v2" / "_generated" / context.skill_id
        return ClassificationResult(package_dir=package_dir, examples_map_entries=rows)


def is_division_point_coordinate_skill(skill_id: str) -> bool:
    return str(skill_id or "").strip().endswith("_DivisionPointCoordinates")


def _classify_example(example: dict[str, Any], skill_id: str) -> dict[str, Any]:
    text = " ".join(
        str(example.get(key) or "").strip()
        for key in ("problem_text", "detailed_solution", "correct_answer")
        if str(example.get(key) or "").strip()
    )
    has_choices = bool(_CHOICE_MARKER.search(text))
    coordinate_choices = bool(_COORDINATE_CHOICE.search(text))

    if _CENTROID.search(text) and len(_POINT_COORDINATE.findall(text)) >= 3:
        operation = "compute_centroid_coordinates"
        answer_type = "coordinate_pair"
        checker_key = "coordinate_pair_checker"
        equivalence_type = "coordinate_pair_equivalence"
        runtime_category = "deterministic_expression"
        rule_id = "coordinate_geometry.division_point.centroid"
    elif _SEGMENT_RATIO.search(text) and has_choices and not coordinate_choices:
        operation = "compute_section_point_distance_from_origin"
        answer_type = "choice"
        checker_key = "choice_label_checker"
        equivalence_type = "choice_label"
        runtime_category = "deterministic_choice"
        rule_id = "coordinate_geometry.division_point.origin_distance_choice"
    elif (
        _SEGMENT_RATIO.search(text)
        or len(_POINT_COORDINATE.findall(text)) >= 3
    ) and len(_POINT_COORDINATE.findall(text)) >= 2:
        operation = "compute_internal_division_point_coordinates"
        if has_choices:
            answer_type = "choice"
            checker_key = "choice_label_checker"
            equivalence_type = "choice_label"
            runtime_category = "deterministic_choice"
        else:
            answer_type = "coordinate_pair"
            checker_key = "coordinate_pair_checker"
            equivalence_type = "coordinate_pair_equivalence"
            runtime_category = "deterministic_expression"
        rule_id = "coordinate_geometry.division_point.internal_section"
    else:
        operation = "unknown"
        answer_type = ""
        checker_key = ""
        equivalence_type = ""
        runtime_category = "manual_review"
        rule_id = "coordinate_geometry.division_point.unmatched"

    resolved = operation != "unknown"
    return {
        "example_id": example.get("id"),
        "title": str(example.get("title") or ""),
        "source_type": str(example.get("problem_type") or "textbook_example"),
        "source_chapter": str(example.get("source_chapter") or ""),
        "source_section": str(example.get("source_section") or ""),
        "problem_preview": text[:200],
        "problem_text_hash": hashlib.sha1(text.encode("utf-8")).hexdigest() if text else "",
        "skill_id": skill_id,
        "subskill_id": operation,
        "problem_type_id": operation,
        "selected_operation": operation,
        "required_domain_capabilities": [operation] if resolved else [],
        "presentation_mode": "single_choice" if has_choices else "short_answer",
        "answer_type": answer_type,
        "checker_key": checker_key,
        "equivalence_type": equivalence_type,
        "runtime_category": runtime_category,
        "classification_rule_id": rule_id,
        "classification_reason": (
            "Matched coordinate-geometry centroid or section-ratio structure."
            if resolved
            else "No supported centroid or section-ratio structure matched."
        ),
        "classifier_confidence": "high" if resolved else "low",
        "semantic_risk_flags": [] if resolved else ["weak_classifier_match"],
        "semantic_audit_status": "pass" if resolved else "review_required",
        "generator_status": "candidate" if resolved else "manual_review",
        "manual_review_reason": "" if resolved else "Coordinate geometry rule unmatched.",
    }
