# -*- coding: utf-8 -*-
"""Server-side practice question store; Flask cookie holds pointers only."""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from typing import Any

from flask import current_app, session

try:
    from flask_login import current_user
except Exception:  # pragma: no cover
    current_user = None  # type: ignore

# owner_key -> question_uid -> payload
_STORE: dict[str, dict[str, dict[str, Any]]] = {}
_MAX_RECENT_QUESTIONS = 3
_COOKIE_TARGET_BYTES = 3500
_PRACTICE_SESSION_TTL_SECONDS = 1800

STATUS_GENERATED = "generated"
STATUS_ANSWERED = "answered"
STATUS_EXPIRED = "expired"
STATUS_SKIPPED = "skipped"

PRACTICE_AUTH_SESSION_KEYS: frozenset[str] = frozenset(
    {
        "_fresh",
        "_id",
        "_user_id",
        "_remember",
        "_remember_seconds",
        "csrf_token",
        "_csrf_token",
        "_flashes",
        "user_id",
        "username",
        "role",
    }
)

PRACTICE_QUERY_SESSION_KEYS: frozenset[str] = frozenset(
    {
        "curriculum",
        "selected_curriculum",
        "current_curriculum",
        "curriculum_code",
        "curriculum_name",
        "education_stage",
        "selected_education_stage",
        "current_education_stage",
        "subject",
        "selected_subject",
        "current_subject",
        "book",
        "selected_book",
        "current_book",
        "book_no",
        "volume",
        "selected_volume",
        "current_volume",
        "volume_no",
        "chapter",
        "selected_chapter",
        "current_chapter",
        "chapter_no",
        "chapter_name",
        "section",
        "selected_section",
        "current_section",
        "section_no",
        "section_name",
        "unit",
        "selected_unit",
        "current_unit",
        "unit_no",
        "unit_name",
        "exam_round",
        "selected_exam_round",
        "current_exam_round",
        "level",
        "selected_level",
        "current_level",
        "difficulty",
        "selected_difficulty",
        "query_params",
    }
)

PRACTICE_MINIMAL_STATE_KEYS: frozenset[str] = frozenset(
    {
        "_practice_owner_sid",
        "current_skill_id",
        "current_question_uid",
        "current_problem_type_id",
        "current_component_id",
        "current_textbook_example_id",
        "current_answer",
        "practice_ref",
        "recent_question_uids",
        "practice_session_touched_at",
        "practice_session_pruned_at",
    }
)

PRACTICE_SESSION_KEEP_KEYS: frozenset[str] = (
    PRACTICE_AUTH_SESSION_KEYS | PRACTICE_QUERY_SESSION_KEYS | PRACTICE_MINIMAL_STATE_KEYS
)

PRACTICE_ALWAYS_PRUNE_SESSION_KEYS: frozenset[str] = frozenset(
    {
        "current_data",
        "current_question",
        "current_question_data",
        "current_question_payload",
        "correct_answer",
        "answer",
        "answer_contract",
        "metadata",
        "choices",
        "choices_display",
        "hint",
        "hints",
        "diagnosis",
        "diagnostic_result",
        "explanation",
        "solution",
        "adaptive_runtime",
        "chat_followup_state",
        "practice_payload",
        "last_question_payload",
        "previous_question_payload",
    }
)

PRACTICE_VOLATILE_SESSION_KEYS: frozenset[str] = frozenset(
    {
        "review_history",
        "review_skill_pool",
        "skill_stats",
        "conversation_history",
    }
)

PRACTICE_PRUNE_SESSION_KEYS: frozenset[str] = (
    PRACTICE_ALWAYS_PRUNE_SESSION_KEYS | PRACTICE_VOLATILE_SESSION_KEYS
)


def get_practice_owner_key() -> str:
    try:
        if current_user is not None and getattr(current_user, "is_authenticated", False):
            return f"user:{current_user.id}"
    except Exception:
        pass
    sid = str(session.get("_practice_owner_sid", "")).strip()
    if not sid:
        sid = str(uuid.uuid4())
        session["_practice_owner_sid"] = sid
    return f"sid:{sid}"


def question_text_hash(question_text: str) -> str:
    text = " ".join(str(question_text or "").split())
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _slim_choices(choices: Any) -> list[dict[str, str]]:
    if not isinstance(choices, list):
        return []
    out: list[dict[str, str]] = []
    for idx, ch in enumerate(choices[:8]):
        if isinstance(ch, dict):
            out.append(
                {
                    "label": str(ch.get("label", chr(ord("A") + idx))).strip(),
                    "text": str(ch.get("text", ch.get("value", ""))).strip()[:200],
                }
            )
        else:
            out.append({"label": chr(ord("A") + idx), "text": str(ch)[:200]})
    return out


def slim_payload_for_store(data: dict[str, Any], *, skill_id: str, question_uid: str) -> dict[str, Any]:
    ac = data.get("answer_contract") if isinstance(data.get("answer_contract"), dict) else {}
    meta = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    slim_meta = {
        k: meta[k]
        for k in (
            "presentation_mode",
            "semantic_answer",
            "semantic_answer_shape",
            "template_variant",
            "ratio_values",
        )
        if k in meta
    }
    return {
        "skill": str(skill_id).strip(),
        "skill_id": str(skill_id).strip(),
        "question_uid": str(question_uid).strip(),
        "question_text_hash": str(data.get("question_text_hash", "")).strip()
        or question_text_hash(str(data.get("question_text", data.get("question", "")))),
        "problem_type_id": str(data.get("problem_type_id", data.get("problem_type", ""))).strip(),
        "question_text": str(data.get("question_text", data.get("question", ""))).strip()[:2000],
        "question": str(data.get("question_text", data.get("question", ""))).strip()[:2000],
        "component_id": str(data.get("component_id", meta.get("component_id", ""))).strip(),
        "textbook_example_id": data.get("textbook_example_id", meta.get("textbook_example_id", "")),
        "presentation_mode": str(data.get("presentation_mode", meta.get("presentation_mode", ""))).strip(),
        "answer": data.get("answer"),
        "correct_answer": data.get("correct_answer", data.get("answer")),
        "display_answer": str(data.get("display_answer", "")).strip(),
        "answer_type": str(data.get("answer_type", ac.get("answer_type", ""))).strip(),
        "checker": str(data.get("checker", data.get("checker_type", ac.get("checker", "")))).strip(),
        "checker_type": str(data.get("checker_type", data.get("checker", ""))).strip(),
        "equivalence": str(
            data.get("equivalence", data.get("equivalence_type", ac.get("answer_equivalence", "")))
        ).strip(),
        "answer_contract": dict(ac),
        "choices": _slim_choices(data.get("choices")),
        "metadata": slim_meta,
        "check_mode": str(data.get("check_mode", data.get("grading_mode", ""))).strip(),
        "grading_mode": str(data.get("grading_mode", data.get("check_mode", ""))).strip(),
        "answer_input_type": str(data.get("answer_input_type", "")).strip(),
        "created_at": time.time(),
        "stored_at": time.time(),
        "status": str(data.get("status", STATUS_GENERATED)).strip() or STATUS_GENERATED,
        "grade_result": None,
    }


def attach_question_identity(payload: dict[str, Any], *, skill_id: str) -> dict[str, Any]:
    out = dict(payload)
    sid = str(skill_id or out.get("skill_id", out.get("skill", ""))).strip()
    qtext = str(out.get("question_text", out.get("question", ""))).strip()
    out["skill_id"] = sid
    out["skill"] = sid
    out["question_uid"] = str(out.get("question_uid", "")).strip() or str(uuid.uuid4())
    out["question_text_hash"] = str(out.get("question_text_hash", "")).strip() or question_text_hash(qtext)
    out["status"] = STATUS_GENERATED
    return out


def _small_session_value(value: Any, limit: int = 160) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple, set)):
        try:
            text = json.dumps(value, ensure_ascii=False, default=str, separators=(",", ":"))
        except Exception:
            text = str(value)
    else:
        text = str(value)
    return text.strip()[:limit]


def _sync_session_pointers(*, skill_id: str, question_uid: str, stored: dict[str, Any] | None = None) -> None:
    sid = str(skill_id).strip()
    uid = str(question_uid).strip()
    session["current_skill_id"] = sid
    session["current_question_uid"] = uid
    stored = stored if isinstance(stored, dict) else {}
    session["current_problem_type_id"] = str(stored.get("problem_type_id", "")).strip()
    session["current_component_id"] = str(stored.get("component_id", "")).strip()
    session["current_textbook_example_id"] = _small_session_value(stored.get("textbook_example_id", ""))
    session["current_answer"] = _small_session_value(stored.get("correct_answer", stored.get("answer")))
    recent = session.get("recent_question_uids")
    if not isinstance(recent, list):
        recent = []
    recent = [str(x).strip() for x in recent if str(x).strip()]
    if uid and uid not in recent:
        recent.append(uid)
    if len(recent) > _MAX_RECENT_QUESTIONS:
        overflow = recent[: len(recent) - _MAX_RECENT_QUESTIONS]
        recent = recent[-_MAX_RECENT_QUESTIONS :]
        _mark_uids_expired(overflow)
    session["recent_question_uids"] = recent
    session["practice_ref"] = {
        "skill_id": sid,
        "question_uid": uid,
        "problem_type_id": session.get("current_problem_type_id", ""),
    }
    session["practice_session_touched_at"] = int(time.time())
    session.pop("current_data", None)
    session.pop("current_question", None)
    session.pop("correct_answer", None)
    session.modified = True


def _mark_uids_expired(uids: list[str]) -> None:
    owner_key = get_practice_owner_key()
    bucket = _STORE.get(owner_key) or {}
    for uid in uids:
        row = bucket.get(uid)
        if isinstance(row, dict) and row.get("status") == STATUS_GENERATED:
            row["status"] = STATUS_EXPIRED


def _compact_practice_ref(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    out = {
        "skill_id": str(value.get("skill_id", "")).strip(),
        "question_uid": str(value.get("question_uid", "")).strip(),
        "problem_type_id": str(value.get("problem_type_id", "")).strip(),
    }
    return {k: v for k, v in out.items() if v}


def _prune_recent_question_uids() -> None:
    recent = session.get("recent_question_uids")
    if not isinstance(recent, list):
        if "recent_question_uids" in session:
            session.pop("recent_question_uids", None)
        return
    compact = [str(x).strip() for x in recent if str(x).strip()][-_MAX_RECENT_QUESTIONS:]
    if compact != recent:
        session["recent_question_uids"] = compact


def _clear_practice_cookie_state() -> list[str]:
    cleared: list[str] = []
    for key in (
        *PRACTICE_DISPLAY_SESSION_KEYS,
        "recent_question_uids",
        "practice_ref",
        "practice_session_touched_at",
        "practice_session_pruned_at",
    ):
        if key in session:
            session.pop(key, None)
            cleared.append(key)
    return cleared


def prune_practice_session(
    max_age_seconds: int = _PRACTICE_SESSION_TTL_SECONDS,
    max_cookie_bytes: int = _COOKIE_TARGET_BYTES,
) -> dict[str, Any]:
    """Prune practice-only client session state while preserving auth and filters."""
    now = time.time()
    before = estimate_session_cookie_bytes()
    removed: list[str] = []

    touched = session.get("practice_session_touched_at")
    try:
        touched_at = float(touched)
    except (TypeError, ValueError):
        touched_at = now

    if max_age_seconds > 0 and now - touched_at > max_age_seconds:
        removed.extend(_clear_practice_cookie_state())
        try:
            clear_practice_cache_for_owner()
        except Exception:
            pass
    else:
        for key in PRACTICE_ALWAYS_PRUNE_SESSION_KEYS:
            if key in session:
                session.pop(key, None)
                removed.append(key)
        _prune_recent_question_uids()
        if isinstance(session.get("practice_ref"), dict):
            compact_ref = _compact_practice_ref(session.get("practice_ref"))
            if compact_ref != session.get("practice_ref"):
                session["practice_ref"] = compact_ref
                removed.append("practice_ref.large_fields")

    session["practice_session_pruned_at"] = int(now)
    after_soft = estimate_session_cookie_bytes()
    if after_soft > max_cookie_bytes:
        for key in PRACTICE_VOLATILE_SESSION_KEYS:
            if key in session:
                session.pop(key, None)
                removed.append(key)
            if estimate_session_cookie_bytes() <= max_cookie_bytes:
                break
        for key in list(session.keys()):
            if key in PRACTICE_SESSION_KEEP_KEYS:
                continue
            session.pop(key, None)
            removed.append(str(key))
            if estimate_session_cookie_bytes() <= max_cookie_bytes:
                break

    after = estimate_session_cookie_bytes()
    if removed:
        session.modified = True
    kept = sorted(str(k) for k in session.keys())
    try:
        current_app.logger.info(
            "[PRACTICE session prune] before=%s after=%s removed=%s kept=%s",
            before,
            after,
            sorted(set(removed)),
            kept,
        )
    except Exception:
        pass
    return {
        "before": before,
        "after": after,
        "removed_keys": sorted(set(removed)),
        "kept_keys": kept,
    }


def get_question_by_uid(
    question_uid: str,
    *,
    owner_key: str | None = None,
    skill_id: str = "",
) -> dict[str, Any] | None:
    uid = str(question_uid or "").strip()
    if not uid:
        return None
    key = str(owner_key or get_practice_owner_key()).strip()
    row = (_STORE.get(key) or {}).get(uid)
    if not isinstance(row, dict):
        return None
    expected_skill = str(skill_id or "").strip()
    if expected_skill:
        stored_skill = str(row.get("skill_id", row.get("skill", ""))).strip()
        if stored_skill and stored_skill != expected_skill:
            return None
    return dict(row)


def clear_practice_cache_for_owner(owner_key: str | None = None) -> None:
    key = str(owner_key or get_practice_owner_key()).strip()
    _STORE.pop(key, None)


# Session keys that hold the currently displayed practice question or grading context.
# Must be cleared when the user navigates to a different skill_id.
PRACTICE_DISPLAY_SESSION_KEYS: tuple[str, ...] = (
    "current_question_uid",
    "current_skill_id",
    "practice_ref",
    "current_data",
    "current_question",
    "correct_answer",
    "current_problem_type_id",
    "current_component_id",
    "current_textbook_example_id",
    "current_answer",
    "review_history",
    "skill_stats",
)


def preview_question_text(text: Any, limit: int = 80) -> str:
    raw = " ".join(str(text or "").split())
    return raw[:limit] + ("…" if len(raw) > limit else "")


def clear_practice_display_state_for_skill_switch(new_skill_id: str) -> dict[str, Any]:
    """Drop stale question pointers when URL skill_id differs from session skill.

    Returns a debug dict with before/after snapshots for logging.
    """
    new_sid = str(new_skill_id or "").strip()
    prev_skill = str(session.get("current_skill_id", "")).strip()
    prev_uid = str(session.get("current_question_uid", "")).strip()
    cleared: list[str] = []

    should_clear = bool(new_sid) and (not prev_skill or prev_skill != new_sid)
    if should_clear:
        for key in PRACTICE_DISPLAY_SESSION_KEYS:
            if key in session:
                session.pop(key, None)
                cleared.append(key)
        # Drop recent uid list so check_answer cannot resolve an old uid from cookie.
        if session.get("recent_question_uids"):
            session.pop("recent_question_uids", None)
            cleared.append("recent_question_uids")
        session.modified = True

    return {
        "requested_skill_id": new_sid,
        "previous_skill_id": prev_skill,
        "previous_question_uid": prev_uid,
        "current_skill_id_after": str(session.get("current_skill_id", "")).strip(),
        "current_question_uid_after": str(session.get("current_question_uid", "")).strip(),
        "cleared_keys": cleared,
        "did_clear": bool(cleared),
    }


def clear_practice_state() -> None:
    """Clear practice-only cookie pointers and server store for current owner.

    This intentionally preserves auth and practice query filters such as
    curriculum, subject, book, chapter, section, unit, exam_round, and level.
    """
    owner_key = get_practice_owner_key()
    _STORE.pop(owner_key, None)
    for k in (
        "current_skill_id",
        "current_question_uid",
        "current_problem_type_id",
        "current_component_id",
        "current_textbook_example_id",
        "current_answer",
        "recent_question_uids",
        "practice_ref",
        "current_data",
        *PRACTICE_DISPLAY_SESSION_KEYS,
    ):
        session.pop(k, None)
    session.modified = True


def persist_current_question(skill_id: str, data: dict[str, Any]) -> tuple[dict[str, str], dict[str, Any]]:
    owner_key = get_practice_owner_key()
    sid = str(skill_id or data.get("skill_id", data.get("skill", ""))).strip()
    enriched = attach_question_identity(data, skill_id=sid)
    uid = str(enriched["question_uid"])
    stored = slim_payload_for_store(enriched, skill_id=sid, question_uid=uid)
    stored["status"] = STATUS_GENERATED
    stored["grade_result"] = None

    bucket = _STORE.setdefault(owner_key, {})
    bucket[uid] = stored
    _sync_session_pointers(skill_id=sid, question_uid=uid, stored=stored)

    ref = {
        "skill_id": sid,
        "question_uid": uid,
        "problem_type_id": str(stored.get("problem_type_id", "")),
    }
    session["practice_ref"] = ref
    return ref, stored


def load_current_question(ref: dict[str, Any] | None = None) -> dict[str, Any]:
    uid = str(session.get("current_question_uid", "")).strip()
    session_skill = str(session.get("current_skill_id", "")).strip()
    if not uid and isinstance(ref, dict):
        uid = str(ref.get("question_uid", "")).strip()
    if not uid:
        cookie_ref = session.get("practice_ref")
        if isinstance(cookie_ref, dict):
            uid = str(cookie_ref.get("question_uid", "")).strip()
            if not session_skill:
                session_skill = str(cookie_ref.get("skill_id", "")).strip()
    if uid:
        loaded = get_question_by_uid(uid, skill_id=session_skill)
        if loaded:
            return loaded
    legacy = session.get("current_data")
    if isinstance(legacy, dict) and legacy:
        legacy_skill = str(legacy.get("skill_id", legacy.get("skill", ""))).strip()
        if session_skill and legacy_skill and legacy_skill != session_skill:
            return {}
        return dict(legacy)
    return {}


def mark_question_answered(question_uid: str, grade_result: dict[str, Any]) -> None:
    uid = str(question_uid or "").strip()
    if not uid:
        return
    owner_key = get_practice_owner_key()
    row = (_STORE.get(owner_key) or {}).get(uid)
    if not isinstance(row, dict):
        return
    row["status"] = STATUS_ANSWERED
    row["grade_result"] = {
        "correct": bool(grade_result.get("correct", False)),
        "result": str(grade_result.get("result", "")),
        "answered_at": time.time(),
    }


def estimate_session_cookie_bytes() -> int:
    try:
        blob = json.dumps(dict(session), ensure_ascii=False, default=str)
        return len(blob.encode("utf-8"))
    except Exception:
        return -1


def stale_question_response(message: str = "題目已更新，請重新載入題目。") -> dict[str, Any]:
    return {
        "correct": False,
        "stale_question": True,
        "stale_question_requires_reload": True,
        "error": "stale_question_requires_reload",
        "message": message,
        "result": message,
    }


def question_expired_response(message: str = "題目已過期，請重新載入題目。") -> dict[str, Any]:
    return {
        "correct": False,
        "stale_question": True,
        "stale_question_requires_reload": True,
        "error": "question_expired",
        "message": message,
        "result": message,
    }


def duplicate_submission_response(
    question_uid: str,
    grade_result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "correct": bool(grade_result.get("correct", False)),
        "duplicate_submission": True,
        "question_uid": str(question_uid),
        "result": str(grade_result.get("result", "")),
        "message": "此題已批改過。",
    }


def _log_stale(reason: str, **fields: Any) -> None:
    try:
        from flask import current_app as ca

        parts = " ".join(f"{k}={v!r}" for k, v in fields.items())
        ca.logger.error("[PRACTICE RUNTIME stale] %s %s", reason, parts)
    except Exception:
        pass


def resolve_check_context(body: dict[str, Any] | None) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Load question by question_uid; validate skill/status. Never trust cookie alone."""
    req = body if isinstance(body, dict) else {}
    req_skill = str(req.get("skill_id", "")).strip()
    req_uid = str(req.get("question_uid", "")).strip()
    session_skill = str(session.get("current_skill_id", "")).strip()

    if not req_uid:
        legacy = session.get("current_data")
        if isinstance(legacy, dict) and legacy.get("skill"):
            legacy_skill = str(legacy.get("skill_id", legacy.get("skill", ""))).strip()
            if req_skill and legacy_skill and req_skill != legacy_skill:
                _log_stale("legacy_skill_mismatch", request_skill=req_skill, legacy_skill=legacy_skill)
                return None, stale_question_response()
            return dict(legacy), None
        _log_stale("missing_question_uid", skill=req_skill)
        return None, stale_question_response("Session state lost. Please reload and try again.")

    # Session skill guard: request must match active session skill when both are known.
    if req_skill and session_skill and req_skill != session_skill:
        _log_stale(
            "session_skill_mismatch",
            request_skill=req_skill,
            session_skill=session_skill,
            uid=req_uid,
        )
        return None, stale_question_response()

    payload = get_question_by_uid(req_uid, skill_id=req_skill or session_skill)
    if not payload:
        _log_stale("question_not_in_store", uid=req_uid, skill=req_skill or session_skill)
        return None, stale_question_response()

    status = str(payload.get("status", STATUS_GENERATED)).strip()
    if status == STATUS_EXPIRED:
        _log_stale("question_expired", uid=req_uid)
        return None, question_expired_response()

    if status == STATUS_ANSWERED:
        cached = payload.get("grade_result")
        if isinstance(cached, dict):
            return None, duplicate_submission_response(req_uid, cached)
        _log_stale("answered_without_cache", uid=req_uid)
        return None, duplicate_submission_response(
            req_uid,
            {"correct": False, "result": "此題已批改過。"},
        )

    payload_skill = str(payload.get("skill_id", payload.get("skill", ""))).strip()
    if not req_skill:
        req_skill = payload_skill
    if req_skill and payload_skill and req_skill != payload_skill:
        _log_stale("skill_mismatch", request_skill=req_skill, payload_skill=payload_skill, uid=req_uid)
        return None, stale_question_response()

    # practice_ref guard
    cookie_ref = session.get("practice_ref")
    if isinstance(cookie_ref, dict):
        ref_skill = str(cookie_ref.get("skill_id", "")).strip()
        ref_uid = str(cookie_ref.get("question_uid", "")).strip()
        if ref_skill and req_skill and ref_skill != req_skill:
            _log_stale("practice_ref_skill_mismatch", request_skill=req_skill, ref_skill=ref_skill, uid=req_uid)
            return None, stale_question_response()
        if ref_uid and req_uid and ref_uid != req_uid:
            _log_stale("practice_ref_uid_mismatch", request_uid=req_uid, ref_uid=ref_uid)
            return None, stale_question_response()

    if not str(payload.get("question_text", "")).strip():
        return None, stale_question_response()

    current_uid = str(session.get("current_question_uid", "")).strip()
    if current_uid and req_uid != current_uid:
        _log_stale("not_current_question", request_uid=req_uid, current_uid=current_uid)
        return None, stale_question_response()

    if session_skill and payload_skill and session_skill != payload_skill:
        _log_stale(
            "session_payload_skill_mismatch",
            session_skill=session_skill,
            payload_skill=payload_skill,
            uid=req_uid,
        )
        return None, stale_question_response()

    return payload, None
