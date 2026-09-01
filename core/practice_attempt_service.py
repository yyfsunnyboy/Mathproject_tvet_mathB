# -*- coding: utf-8 -*-
"""Persist canonical per-question practice attempt history."""

from __future__ import annotations

import json
from typing import Any

from flask import current_app, session
from flask_login import current_user

from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
    is_b4_chapter2_phase6c1_deterministic_skill,
)
from models import ClassStudent, PracticeAttempt, db

SOURCE_GENERAL_PRACTICE = "general_practice"


def _normalize_answer_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (dict, list, tuple)):
        try:
            return json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(value)
    text = str(value).strip()
    return text if text else None


def _resolve_class_snapshot(student_id: int) -> int | None:
    rows = (
        db.session.query(ClassStudent.class_id)
        .filter(ClassStudent.student_id == student_id)
        .all()
    )
    class_ids = {int(r[0]) for r in rows if r[0] is not None}
    if len(class_ids) == 1:
        return next(iter(class_ids))
    return None


def _extract_question_text(current_question: dict[str, Any] | None) -> str | None:
    if not isinstance(current_question, dict):
        return None
    for key in ("question_text", "display_question", "question", "new_question_text"):
        raw = current_question.get(key)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return None


def _extract_expected_answer(current_question: dict[str, Any] | None) -> str | None:
    if not isinstance(current_question, dict):
        return None
    for key in ("correct_answer", "answer", "display_answer", "semantic_answer"):
        raw = current_question.get(key)
        if raw is not None:
            text = _normalize_answer_text(raw)
            if text:
                return text
    return None


def _extract_problem_type_id(current_question: dict[str, Any] | None) -> str | None:
    if not isinstance(current_question, dict):
        return None
    for key in ("problem_type_id", "problem_type"):
        raw = current_question.get(key)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return None


def _extract_difficulty(current_question: dict[str, Any] | None) -> float | None:
    if not isinstance(current_question, dict):
        return None
    for key in ("difficulty", "level", "difficulty_level"):
        raw = current_question.get(key)
        if raw is None:
            continue
        try:
            return float(raw)
        except (TypeError, ValueError):
            continue
    return None


def _practice_session_id() -> str | None:
    sid = session.get("b4_ch2_audit_sid")
    if isinstance(sid, str) and sid.strip():
        return sid.strip()
    return None


def persist_practice_attempt(
    *,
    skill_id: str,
    is_correct: bool,
    user_answer: Any = None,
    current_question: dict[str, Any] | None = None,
    question_uid: str | None = None,
    source: str = SOURCE_GENERAL_PRACTICE,
) -> PracticeAttempt | None:
    """Write one canonical attempt row. Never raises to caller."""
    sid = str(skill_id or "").strip()
    if not sid:
        return None
    if is_b4_chapter2_phase6c1_deterministic_skill(sid):
        return None
    if not getattr(current_user, "is_authenticated", False):
        return None
    try:
        student_id = int(current_user.id)
    except (TypeError, ValueError):
        return None

    try:
        row = PracticeAttempt(
            student_id=student_id,
            class_id=_resolve_class_snapshot(student_id),
            skill_id=sid,
            problem_type_id=_extract_problem_type_id(current_question),
            question_uid=str(question_uid).strip() if question_uid else None,
            question_text=_extract_question_text(current_question),
            user_answer=_normalize_answer_text(user_answer),
            expected_answer=_extract_expected_answer(current_question),
            is_correct=bool(is_correct),
            source=str(source or SOURCE_GENERAL_PRACTICE),
            session_id=_practice_session_id(),
            difficulty=_extract_difficulty(current_question),
        )
        db.session.add(row)
        db.session.commit()
        return row
    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "[PracticeAttempt] persist failed student_id=%s skill_id=%s source=%s",
            student_id,
            sid,
            source,
        )
        return None
