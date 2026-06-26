# -*- coding: utf-8 -*-
"""Teacher-facing semantic review contract."""

from __future__ import annotations

from typing import Any

from core.gencode.domain_bootstrap.candidate_store import CandidateStore
from core.gencode.domain_bootstrap.models import DomainGapReport

TEACHER_QUESTIONS: tuple[dict[str, str], ...] = (
    {"id": "angle_unit", "prompt": "角度採用度數或弧度？"},
    {"id": "formula_scope", "prompt": "公式採母體或樣本？"},
    {"id": "answer_precision", "prompt": "答案採精確值或近似值？"},
    {"id": "decimal_places", "prompt": "若為近似值，需精確到小數第幾位？"},
    {"id": "all_solutions", "prompt": "是否要求列出全部解？"},
    {"id": "difficulty_range", "prompt": "可接受的難度範圍？"},
    {"id": "source_isomorphism", "prompt": "題目是否需與教材同構？"},
)


def build_teacher_review_package(
    *,
    store: CandidateStore,
    gap_report: DomainGapReport,
    validation_summary: dict[str, Any],
) -> dict[str, Any]:
    gap_id = gap_report.gap_id
    preview_samples: list[dict[str, Any]] = []
    if store.candidate_file_exists(gap_id, "preview_samples.json"):
        import json

        raw = json.loads(store.read_candidate_file(gap_id, "preview_samples.json"))
        preview_samples = list(raw.get("samples") or [])

    manifest: dict[str, Any] = {}
    if store.candidate_file_exists(gap_id, "domain_manifest.json"):
        import json

        manifest = json.loads(store.read_candidate_file(gap_id, "domain_manifest.json"))

    return {
        "gap_id": gap_id,
        "teacher_message": "偵測到新的數學能力，系統已建立可重用出題能力候選，請確認教學語意。",
        "questions": list(TEACHER_QUESTIONS),
        "preview": {
            "samples": preview_samples[:5],
            "capabilities": list(manifest.get("capabilities") or gap_report.missing_capabilities or []),
            "operations": list(manifest.get("operations") or []),
            "formula_summary": "sum(values)",
            "validation_summary": validation_summary,
            "affected_example_count": len(gap_report.source_example_ids or []),
        },
    }


def validate_teacher_answers(answers: dict[str, Any]) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    if not isinstance(answers, dict):
        return False, ["teacher_answers_invalid"]
    if str(answers.get("approved", "")).strip().lower() not in {"1", "true", "yes", "approve", "核准"}:
        if answers.get("approved") is not True:
            blockers.append("teacher_not_approved")
    return len(blockers) == 0, blockers
