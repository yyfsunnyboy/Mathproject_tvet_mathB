"""Canonical active-mistake persistence for the student notebook."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from flask import has_request_context, session

from models import MistakeNotebookEntry, PracticeAttempt, SkillCurriculum, db


_QUESTION_KEYS = (
    "question_text", "new_question_text", "display_question", "question",
    "choices", "choices_display", "subquestions", "visual_spec", "diagram_spec",
    "visual_aids", "image_assets", "table_data", "table_question", "table",
    "table_title", "answer_type", "answer_input_type", "answer_contract",
    "presentation_mode", "ui_contract",
    "stem_structure", "metadata",
)
_GENERATOR_KEYS = (
    "problem_type_id", "problem_type", "component_id", "generator_key",
    "variant", "template_variant", "difficulty", "current_level", "source_kind",
    "generator_mode", "seed",
)


def _curriculum_binding(skill_id: str, question: dict[str, Any] | None = None) -> dict[str, str | None]:
    metadata = question.get("metadata") if isinstance(question, dict) and isinstance(question.get("metadata"), dict) else {}
    curriculum = str((question or {}).get("curriculum") or metadata.get("curriculum") or "").strip()
    if not curriculum and has_request_context():
        curriculum = str(session.get("current_curriculum") or "").strip()
    query = db.session.query(SkillCurriculum).filter(SkillCurriculum.skill_id == skill_id)
    if curriculum:
        row = query.filter(SkillCurriculum.curriculum == curriculum).order_by(
            SkillCurriculum.display_order, SkillCurriculum.id
        ).first()
    else:
        row = query.order_by(SkillCurriculum.display_order, SkillCurriculum.id).first()
    if row is None:
        return {"curriculum": curriculum or None, "volume": None, "chapter": None, "section": None}
    return {
        "curriculum": row.curriculum,
        "volume": row.volume,
        "chapter": row.chapter,
        "section": row.section,
    }


def _question_snapshot(question: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(question, dict):
        return {}
    return {key: question[key] for key in _QUESTION_KEYS if key in question}


def _generator_metadata(question: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(question, dict):
        return {}
    metadata = question.get("metadata") if isinstance(question.get("metadata"), dict) else {}
    result = {key: question[key] for key in _GENERATOR_KEYS if question.get(key) not in (None, "")}
    for key in _GENERATOR_KEYS:
        if key not in result and metadata.get(key) not in (None, ""):
            result[key] = metadata[key]
    if result.get("problem_type_id") and not result.get("problem_type"):
        result["problem_type"] = result["problem_type_id"]
    return result


def create_active_mistake(*, student_id: int, attempt: PracticeAttempt, question: dict[str, Any], user_answer: Any) -> MistakeNotebookEntry:
    """Create/update one active record per generated question for this student."""
    question_uid = str(attempt.question_uid or "").strip()
    active = db.session.query(MistakeNotebookEntry).filter_by(
        student_id=student_id, resolved_at=None,
    )
    existing = (
        active.filter(MistakeNotebookEntry.source_question_uid == question_uid).first()
        if question_uid else active.filter(MistakeNotebookEntry.source_attempt_id == attempt.id).first()
    )
    if existing is not None:
        existing.user_answer = attempt.user_answer if attempt.user_answer is not None else str(user_answer or "")
        existing.updated_at = datetime.utcnow()
        return existing
    binding = _curriculum_binding(attempt.skill_id, question)
    metadata = _generator_metadata(question)
    entry = MistakeNotebookEntry(
        student_id=student_id,
        source_type=attempt.source or "practice",
        source_attempt_id=attempt.id,
        source_question_uid=question_uid or None,
        source_session_id=attempt.session_id,
        skill_id=attempt.skill_id,
        problem_type_id=str(attempt.problem_type_id) if attempt.problem_type_id is not None else None,
        component_id=metadata.get("component_id"),
        generator_key=metadata.get("generator_key"),
        variant=metadata.get("variant"),
        template_variant=metadata.get("template_variant"),
        question_text=attempt.question_text,
        question_data=_question_snapshot(question),
        user_answer=attempt.user_answer if attempt.user_answer is not None else str(user_answer or ""),
        expected_answer=attempt.expected_answer,
        generator_metadata=metadata,
        **binding,
    )
    db.session.add(entry)
    return entry


def active_review_mistake(*, mistake_id: int, student_id: int) -> MistakeNotebookEntry | None:
    return db.session.query(MistakeNotebookEntry).filter_by(
        id=mistake_id,
        student_id=student_id,
        resolved_at=None,
    ).first()


def resolve_active_mistake(*, mistake_id: int, student_id: int, resolved_attempt: PracticeAttempt) -> bool:
    entry = active_review_mistake(mistake_id=mistake_id, student_id=student_id)
    if entry is None:
        return False
    entry.resolved_at = datetime.utcnow()
    entry.resolved_attempt_id = resolved_attempt.id
    entry.resolution_method = "retry_correct"
    return True


def record_active_review_verdict(
    *,
    mistake_id: int,
    student_id: int,
    retry_attempt: PracticeAttempt,
    current_question: dict[str, Any] | None,
    is_correct: bool,
) -> tuple[bool, bool]:
    """Record one authoritative retry verdict, scoped to exactly one active row.

    The browser never supplies the verdict or the target entry.  This verifies
    ownership and the persisted skill/type/component context against the new
    canonical attempt before changing lifecycle state.
    """
    entry = active_review_mistake(mistake_id=mistake_id, student_id=student_id)
    if entry is None or retry_attempt.student_id != student_id:
        return False, False
    if str(retry_attempt.skill_id or "") != str(entry.skill_id or ""):
        return False, False
    if entry.problem_type_id and str(retry_attempt.problem_type_id or "") != str(entry.problem_type_id):
        return False, False
    metadata = _generator_metadata(current_question)
    runtime_component = str(metadata.get("component_id") or "")
    if entry.component_id and runtime_component and runtime_component != str(entry.component_id):
        return False, False

    entry.retry_count = int(entry.retry_count or 0) + 1
    entry.last_retry_at = datetime.utcnow()
    entry.updated_at = datetime.utcnow()
    if is_correct:
        entry.resolved_at = datetime.utcnow()
        entry.resolved_attempt_id = retry_attempt.id
        entry.resolution_method = "retry_correct"
        return True, True
    return True, False
