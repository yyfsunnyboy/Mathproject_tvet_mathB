# -*- coding: utf-8 -*-
"""Phase 6I: Chap2 deterministic visibility-only audit logging (no mastery / APR hooks)."""

from __future__ import annotations

import json
import uuid
from typing import Any, Literal

from flask import current_app, session
from flask_login import current_user

from models import db, B4Chap2VisibilityAuditLog

GatedEventType = Literal["not_enabled_skill", "reserved_problem_type"]

B4_CHAP2_VISIBILITY_SOURCE_PHASE = "b4_chap2_phase6i"


def _audit_session_id() -> str | None:
    sid = session.get("b4_ch2_audit_sid")
    if not sid:
        sid = uuid.uuid4().hex
        session["b4_ch2_audit_sid"] = sid
        session.modified = True
    return sid


def _student_id_or_none() -> int | None:
    if not getattr(current_user, "is_authenticated", False):
        return None
    try:
        return int(current_user.id)
    except (TypeError, ValueError):
        return None


def _commit_audit_row(row: B4Chap2VisibilityAuditLog) -> None:
    try:
        db.session.add(row)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.warning(
            "[B4 Chap2 Phase6I] visibility audit persist failed: %s", exc, exc_info=False
        )


def persist_b4_chap2_gated_event(
    *,
    gated_event_type: GatedEventType,
    skill_id: str,
    problem_type_id: str | None,
    public_message: str,
) -> None:
    row = B4Chap2VisibilityAuditLog(
        record_kind="gated",
        gated_event_type=gated_event_type,
        student_id=_student_id_or_none(),
        session_id=_audit_session_id(),
        skill_id=str(skill_id or "").strip(),
        problem_type_id=str(problem_type_id).strip() if problem_type_id else None,
        generator_key=None,
        answer_type=None,
        expected_answer=None,
        user_answer=None,
        is_correct=None,
        checker_name=None,
        difficulty=None,
        diagnosis_tags=None,
        public_message=public_message,
        source_phase=B4_CHAP2_VISIBILITY_SOURCE_PHASE,
    )
    _commit_audit_row(row)


def persist_b4_chap2_deterministic_answer_event(
    *,
    skill_id: str,
    current_question: dict[str, Any],
    user_answer: str,
    is_correct: bool,
    checker_name: str,
) -> None:
    pid = current_question.get("problem_type_id") or current_question.get("problem_type")
    gen_key = current_question.get("generator_key")
    if gen_key is not None:
        gen_key = str(gen_key)[:256]
    ans_type = current_question.get("answer_type")
    diff = current_question.get("difficulty")
    if diff is None:
        diff = current_question.get("difficulty_level")
    try:
        diff_i = int(diff) if diff is not None else None
    except (TypeError, ValueError):
        diff_i = None
    tags = current_question.get("diagnosis_tags")
    tags_s: str | None
    if tags is None:
        tags_s = None
    elif isinstance(tags, str):
        tags_s = tags
    else:
        try:
            tags_s = json.dumps(tags, ensure_ascii=False)
        except (TypeError, ValueError):
            tags_s = None
    exp = current_question.get("correct_answer", current_question.get("answer"))

    row = B4Chap2VisibilityAuditLog(
        record_kind="deterministic_answer",
        gated_event_type=None,
        student_id=_student_id_or_none(),
        session_id=_audit_session_id(),
        skill_id=str(skill_id or "").strip(),
        problem_type_id=str(pid).strip() if pid else None,
        generator_key=gen_key,
        answer_type=str(ans_type) if ans_type else None,
        expected_answer=str(exp) if exp is not None else None,
        user_answer=str(user_answer) if user_answer is not None else None,
        is_correct=is_correct,
        checker_name=checker_name,
        difficulty=diff_i,
        diagnosis_tags=tags_s,
        public_message=None,
        source_phase=B4_CHAP2_VISIBILITY_SOURCE_PHASE,
    )
    _commit_audit_row(row)
