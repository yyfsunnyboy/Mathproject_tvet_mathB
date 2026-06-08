# -*- coding: utf-8 -*-
"""Utilities that keep Flask client-side sessions below browser cookie limits."""

from __future__ import annotations

import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import current_app, flash, session
from markupsafe import escape

COOKIE_WARN_BYTES = 3500
COOKIE_HARD_BYTES = 4093
SERVER_RESULT_DIR = Path("reports") / "runtime_jobs"

KEEP_SESSION_KEYS = {
    "_fresh",
    "_id",
    "_user_id",
    "csrf_token",
    "user_id",
    "username",
    "role",
    "_practice_owner_sid",
    "current_skill_id",
    "current_question_uid",
    "recent_question_uids",
    "last_import_job_id",
    "last_db_maintenance_job_id",
    "last_maintenance_job_id",
    "selected_curriculum",
    "curriculum",
    "curriculum_code",
    "curriculum_name",
    "current_curriculum",
    "selected_syllabus",
    "syllabus",
    "syllabus_code",
    "syllabus_name",
    "selected_volume",
    "volume",
    "book",
    "book_no",
    "volume_no",
    "selected_chapter",
    "chapter",
    "chapter_no",
    "chapter_name",
    "selected_section",
    "section",
    "section_no",
    "section_name",
    "selected_unit",
    "unit",
    "unit_no",
    "unit_name",
    "lesson",
    "test_no",
    "test_number",
    "exam_no",
    "quiz_no",
    "selected_skill_id",
    "skill_id",
    "selected_category",
    "category",
    "selected_difficulty",
    "difficulty",
    "query_params",
    "question_uid",
    "AI_CLOUD_MODEL",
}

_LARGE_SESSION_KEYS = {
    "import_result",
    "import_results",
    "upload_result",
    "db_report",
    "maintenance_report",
    "db_maintenance_report",
    "examples",
    "examples_list",
    "example_rows",
    "preview_rows",
    "failed_rows",
    "current_question",
    "current_data",
    "review_history",
    "adaptive_runtime",
    "chat_followup_state",
    "traceback",
    "raw_log",
    "full_report",
}


def _json_default(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _result_dir() -> Path:
    root = Path(getattr(current_app, "root_path", os.getcwd()))
    path = root / SERVER_RESULT_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def _result_path(kind: str, job_id: str) -> Path:
    safe_kind = "".join(ch for ch in str(kind or "job") if ch.isalnum() or ch in ("_", "-")) or "job"
    safe_job = "".join(ch for ch in str(job_id or "") if ch.isalnum() or ch in ("_", "-"))
    if not safe_job:
        raise ValueError("job_id is required")
    return _result_dir() / f"{safe_kind}_{safe_job}.json"


def estimate_session_cookie_size(app=None) -> int:
    """Estimate the final Set-Cookie byte size for the current session."""
    app = app or current_app
    try:
        cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
        value = app.session_interface.get_signing_serializer(app).dumps(dict(session))
        return len(f"{cookie_name}={value}; Path=/".encode("utf-8"))
    except Exception:
        try:
            return len(json.dumps(dict(session), ensure_ascii=False, default=_json_default).encode("utf-8"))
        except Exception:
            return COOKIE_HARD_BYTES + 1


def trim_session_for_cookie_limit(limit: int = COOKIE_WARN_BYTES, logger=None) -> tuple[int, list[str]]:
    """Remove known large client-session keys when the cookie estimate is too high."""
    before = estimate_session_cookie_size()
    removed: list[str] = []
    if before <= limit:
        return before, removed

    for key in sorted(_LARGE_SESSION_KEYS):
        if key in session:
            session.pop(key, None)
            removed.append(key)

    if "_flashes" in session and estimate_session_cookie_size() > limit:
        flashes = session.get("_flashes") or []
        trimmed_flashes = []
        for category, message in flashes:
            text = str(message)
            if len(text) > 240:
                text = text[:237].rstrip() + "..."
            trimmed_flashes.append((str(category), text))
        session["_flashes"] = trimmed_flashes
        removed.append("_flashes_trimmed")

    if "_flashes" in session and estimate_session_cookie_size() > limit:
        session.pop("_flashes", None)
        removed.append("_flashes")

    if estimate_session_cookie_size() > limit:
        for key in list(session.keys()):
            if key in KEEP_SESSION_KEYS:
                continue
            value = session.get(key)
            try:
                raw_size = len(json.dumps(value, ensure_ascii=False, default=_json_default).encode("utf-8"))
            except Exception:
                raw_size = len(str(value).encode("utf-8", errors="replace"))
            if raw_size > 512:
                session.pop(key, None)
                removed.append(str(key))
            if estimate_session_cookie_size() <= limit:
                break

    if removed:
        session.modified = True
        (logger or current_app.logger).warning(
            "Trimmed large session keys for cookie limit: before=%s after=%s removed=%s",
            before,
            estimate_session_cookie_size(),
            ",".join(removed),
        )
    return before, removed


def trim_session_to_keep_keys() -> dict[str, Any]:
    """Keep only approved short session keys and report what changed."""
    before_keys = list(session.keys())
    removed_keys: list[str] = []
    for key in before_keys:
        if key not in KEEP_SESSION_KEYS:
            session.pop(key, None)
            removed_keys.append(key)

    session.modified = True
    kept_preview = {key: str(session.get(key))[:200] for key in session.keys()}
    return {
        "before_keys": before_keys,
        "after_keys": list(session.keys()),
        "removed_keys": removed_keys,
        "kept_preview": kept_preview,
    }


def safe_flash_message(message: Any, category: str = "message", max_chars: int = 240) -> None:
    """Flash only short text; large details belong in server-side result JSON."""
    text = str(message if message is not None else "")
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if len(text) > max_chars:
        text = text[: max_chars - 3].rstrip() + "..."
    flash(escape(text), category)


def summarize_import_result(result: Any) -> dict[str, Any]:
    """Return a compact import summary suitable for rendering and flashing."""
    if isinstance(result, dict):
        success = bool(result.get("success", result.get("ok", False)))
        message = str(result.get("message", ""))
    elif isinstance(result, (list, tuple)) and len(result) >= 2:
        success = bool(result[0])
        message = str(result[1])
    else:
        success = False
        message = str(result or "")

    lines = [line.strip() for line in message.splitlines() if line.strip()]
    table_lines = [line for line in lines if line.lower().startswith("table ")]
    failed_rows = 0
    imported_rows = 0
    source_rows = 0
    for line in table_lines:
        for token in line.replace(",", " ").split():
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            try:
                number = int(str(value).strip())
            except ValueError:
                continue
            if key == "failed":
                failed_rows += number
            elif key == "imported":
                imported_rows += number
            elif key == "source_rows":
                source_rows += number

    error_lines = [line for line in lines if "row_error" in line or "failed" in line.lower()]
    first_lines = lines[:8]
    return {
        "success": success,
        "line_count": len(lines),
        "table_count": len(table_lines),
        "source_rows": source_rows,
        "imported_rows": imported_rows,
        "failed_rows": failed_rows,
        "error_count": len(error_lines),
        "preview": first_lines,
        "message": "\n".join(first_lines),
    }


def put_large_result_in_server_store(result: Any, *, kind: str = "job", job_id: str | None = None) -> str:
    """Persist large route results outside the signed cookie and return its job id."""
    job_id = job_id or f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"
    payload = {
        "job_id": job_id,
        "kind": kind,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }
    path = _result_path(kind, job_id)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=_json_default)
    return job_id


def get_large_result_from_server_store(job_id: str, *, kind: str = "job") -> dict[str, Any] | None:
    """Load a server-side result JSON by job id."""
    if not job_id:
        return None
    try:
        path = _result_path(kind, job_id)
    except ValueError:
        return None
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
