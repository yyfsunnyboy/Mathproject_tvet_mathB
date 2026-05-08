# -*- coding: utf-8 -*-
"""Phase 6J: read-only teacher/admin visibility for B4 Chap2 visibility audit logs."""

from __future__ import annotations

import logging

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import desc

from models import B4Chap2VisibilityAuditLog, db

from . import core_bp

_LOG = logging.getLogger(__name__)

ALLOWED_RECORD_KINDS = frozenset({"deterministic_answer", "gated"})
_DEFAULT_LIMIT = 50
_MAX_LIMIT = 200


def _teacher_audit_authorized() -> bool:
    if not getattr(current_user, "is_authenticated", False):
        return False
    if getattr(current_user, "is_admin", False):
        return True
    return getattr(current_user, "role", None) == "teacher"


def _parse_limit(raw: str | None) -> int:
    try:
        n = int(raw) if raw is not None else _DEFAULT_LIMIT
    except (TypeError, ValueError):
        return _DEFAULT_LIMIT
    return max(1, min(_MAX_LIMIT, n))


def _normalize_optional_filter(value: str | None) -> str | None:
    if value is None:
        return None
    s = value.strip()
    return s if s else None


def _build_audit_query(
    *,
    limit: int,
    record_kind: str | None,
    skill_id: str | None,
    problem_type_id: str | None,
):
    q = db.session.query(B4Chap2VisibilityAuditLog)
    if record_kind is not None and record_kind in ALLOWED_RECORD_KINDS:
        q = q.filter(B4Chap2VisibilityAuditLog.record_kind == record_kind)
    if skill_id is not None:
        q = q.filter(B4Chap2VisibilityAuditLog.skill_id == skill_id)
    if problem_type_id is not None:
        q = q.filter(B4Chap2VisibilityAuditLog.problem_type_id == problem_type_id)
    return (
        q.order_by(
            desc(B4Chap2VisibilityAuditLog.created_at),
            desc(B4Chap2VisibilityAuditLog.id),
        ).limit(limit)
    )


def _row_to_json(row: B4Chap2VisibilityAuditLog) -> dict:
    ts = row.created_at
    return {
        "timestamp": ts.isoformat() + "Z" if ts else None,
        "record_kind": row.record_kind,
        "gated_event_type": row.gated_event_type,
        "student_id": row.student_id,
        "session_id": row.session_id,
        "skill_id": row.skill_id,
        "problem_type_id": row.problem_type_id,
        "generator_key": row.generator_key,
        "answer_type": row.answer_type,
        "user_answer": row.user_answer,
        "expected_answer": row.expected_answer,
        "is_correct": row.is_correct,
        "checker_name": row.checker_name,
        "difficulty": row.difficulty,
        "diagnosis_tags": row.diagnosis_tags,
        "public_message": row.public_message,
        "source_phase": row.source_phase,
    }


@core_bp.route("/teacher/b4-chap2-audit", methods=["GET"])
@login_required
def teacher_b4_chap2_audit_page():
    if not _teacher_audit_authorized():
        flash("權限不足", "warning")
        return redirect(url_for("dashboard"))

    limit = _parse_limit(request.args.get("limit"))
    raw_rk = _normalize_optional_filter(request.args.get("record_kind"))
    record_kind = raw_rk if raw_rk in ALLOWED_RECORD_KINDS else None
    skill_id = _normalize_optional_filter(request.args.get("skill_id"))
    problem_type_id = _normalize_optional_filter(request.args.get("problem_type_id"))

    rows: list[B4Chap2VisibilityAuditLog] = []
    try:
        rows = _build_audit_query(
            limit=limit,
            record_kind=record_kind,
            skill_id=skill_id,
            problem_type_id=problem_type_id,
        ).all()
    except Exception as exc:  # pragma: no cover — defensive; no user-facing details
        _LOG.warning("b4 chap2 audit page query failed: %s", exc, exc_info=False)
        rows = []

    return render_template(
        "teacher_b4_chap2_audit.html",
        rows=rows,
        limit=limit,
        filter_record_kind=raw_rk or "",
        filter_skill_id=skill_id or "",
        filter_problem_type_id=problem_type_id or "",
        has_rows=bool(rows),
    )


@core_bp.route("/api/teacher/b4-chap2-audit", methods=["GET"])
@login_required
def teacher_b4_chap2_audit_api():
    if not _teacher_audit_authorized():
        return jsonify({"ok": False, "message": "權限不足"}), 403

    limit = _parse_limit(request.args.get("limit"))
    raw_rk = _normalize_optional_filter(request.args.get("record_kind"))
    record_kind = raw_rk if raw_rk in ALLOWED_RECORD_KINDS else None
    skill_id = _normalize_optional_filter(request.args.get("skill_id"))
    problem_type_id = _normalize_optional_filter(request.args.get("problem_type_id"))

    try:
        rows = _build_audit_query(
            limit=limit,
            record_kind=record_kind,
            skill_id=skill_id,
            problem_type_id=problem_type_id,
        ).all()
        payload = [_row_to_json(r) for r in rows]
    except Exception as exc:
        _LOG.warning("b4 chap2 audit api query failed: %s", exc, exc_info=False)
        payload = []

    return jsonify({"ok": True, "items": payload, "count": len(payload)})
