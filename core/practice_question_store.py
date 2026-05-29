# -*- coding: utf-8 -*-
"""Server-side practice question store; Flask cookie holds pointers only."""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from typing import Any

from flask import session

try:
    from flask_login import current_user
except Exception:  # pragma: no cover
    current_user = None  # type: ignore

# owner_key -> question_uid -> payload
_STORE: dict[str, dict[str, dict[str, Any]]] = {}
_MAX_RECENT_QUESTIONS = 20
_COOKIE_TARGET_BYTES = 3500

STATUS_GENERATED = "generated"
STATUS_ANSWERED = "answered"
STATUS_EXPIRED = "expired"
STATUS_SKIPPED = "skipped"


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


def _sync_session_pointers(*, skill_id: str, question_uid: str) -> None:
    sid = str(skill_id).strip()
    uid = str(question_uid).strip()
    session["current_skill_id"] = sid
    session["current_question_uid"] = uid
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
        "question_text_hash": "",
        "problem_type_id": "",
    }
    session.pop("current_data", None)
    session.modified = True


def _mark_uids_expired(uids: list[str]) -> None:
    owner_key = get_practice_owner_key()
    bucket = _STORE.get(owner_key) or {}
    for uid in uids:
        row = bucket.get(uid)
        if isinstance(row, dict) and row.get("status") == STATUS_GENERATED:
            row["status"] = STATUS_EXPIRED


def get_question_by_uid(question_uid: str, *, owner_key: str | None = None) -> dict[str, Any] | None:
    uid = str(question_uid or "").strip()
    if not uid:
        return None
    key = str(owner_key or get_practice_owner_key()).strip()
    row = (_STORE.get(key) or {}).get(uid)
    return dict(row) if isinstance(row, dict) else None


def clear_practice_cache_for_owner(owner_key: str | None = None) -> None:
    key = str(owner_key or get_practice_owner_key()).strip()
    _STORE.pop(key, None)


def clear_practice_state() -> None:
    """Clear cookie pointers and server store for current owner (debug / logout helper)."""
    owner_key = get_practice_owner_key()
    _STORE.pop(owner_key, None)
    for k in (
        "current_skill_id",
        "current_question_uid",
        "recent_question_uids",
        "practice_ref",
        "current_data",
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
    _sync_session_pointers(skill_id=sid, question_uid=uid)

    ref = {
        "skill_id": sid,
        "question_uid": uid,
        "question_text_hash": str(enriched["question_text_hash"]),
        "problem_type_id": str(stored.get("problem_type_id", "")),
    }
    session["practice_ref"] = ref
    return ref, stored


def load_current_question(ref: dict[str, Any] | None = None) -> dict[str, Any]:
    uid = str(session.get("current_question_uid", "")).strip()
    if not uid and isinstance(ref, dict):
        uid = str(ref.get("question_uid", "")).strip()
    if not uid:
        cookie_ref = session.get("practice_ref")
        if isinstance(cookie_ref, dict):
            uid = str(cookie_ref.get("question_uid", "")).strip()
    if uid:
        loaded = get_question_by_uid(uid)
        if loaded:
            return loaded
    legacy = session.get("current_data")
    return dict(legacy) if isinstance(legacy, dict) else {}


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

    if not req_uid:
        legacy = session.get("current_data")
        if isinstance(legacy, dict) and legacy.get("skill"):
            return dict(legacy), None
        _log_stale("missing_question_uid", skill=req_skill)
        return None, stale_question_response("Session state lost. Please reload and try again.")

    payload = get_question_by_uid(req_uid)
    if not payload:
        _log_stale("question_not_in_store", uid=req_uid, skill=req_skill)
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

    if not str(payload.get("question_text", "")).strip():
        return None, stale_question_response()

    current_uid = str(session.get("current_question_uid", "")).strip()
    if current_uid and req_uid != current_uid:
        _log_stale("not_current_question", request_uid=req_uid, current_uid=current_uid)
        return None, stale_question_response()

    return payload, None
