"""Session-scoped, read-only guest review mode."""
from __future__ import annotations

import re
from functools import wraps
from types import SimpleNamespace
from typing import Any, Callable

from flask import abort, current_app, g, has_request_context, jsonify, redirect, request, session, url_for
from flask_login import AnonymousUserMixin, current_user, login_required, logout_user
from sqlalchemy import event

SESSION_KEY = "guest_demo"
_SQL_PREFIX = re.compile(r"^(?:\s|--[^\n]*(?:\n|$)|/\*[\s\S]*?\*/|;)*", re.I)
_READ_SQL = re.compile(r"^SELECT\b", re.I)
_READ_SCHEMA_PRAGMA = re.compile(
    r'^PRAGMA\s+(?:(?:main|temp)\.)?(?:table_xinfo|table_info|index_list|index_xinfo|foreign_key_list)\s*\(',
    re.I,
)

_READ_ONLY_MESSAGE = "此為展示頁面，請登入後再行操作。"
_NEVER_GUEST_GET_ENDPOINTS = frozenset({
    "practice.debug_clear_practice_state",
    "debug_session_key_status",
    "debug_trim_session",
})
_SENSITIVE_GET_PREFIXES = (
    "/admin/check_api_key",
    "/api/runtime_ai_status", "/api/adaptive/rag_settings", "/api/adaptive/rag_hint",
)


class GuestDemoPrincipal(AnonymousUserMixin):
    """Ephemeral display identity; never loaded from or stored in the DB."""

    username = "Guest Demo"
    role = "teacher"
    is_admin = True

    def __init__(self, teacher_id: int) -> None:
        self.id = teacher_id

    @property
    def is_authenticated(self) -> bool:
        return False

    def get_id(self) -> None:
        return None


def is_guest_demo() -> bool:
    return bool(has_request_context() and session.get(SESSION_KEY) is True)


def _is_login_required_wrapper(view: Callable[..., Any]) -> bool:
    code = getattr(view, "__code__", None)
    filename = str(getattr(code, "co_filename", "")).replace("\\", "/").lower()
    return bool(hasattr(view, "__wrapped__") and "flask_login" in filename)


def persistence_denied_response():
    return jsonify(success=False, error="review_demo_read_only", message=_READ_ONLY_MESSAGE), 403


def mask_student_username(value: Any) -> str:
    raw = str(value or "")
    if not is_guest_demo() or not raw:
        return raw
    if any("\u4e00" <= char <= "\u9fff" for char in raw):
        return mask_student_name(raw)
    visible = 3 if len(raw) > 3 else 1 if len(raw) > 1 else 0
    return raw[:visible] + "*" * (len(raw) - visible)


def mask_student_name(value: Any) -> str:
    raw = str(value or "")
    if not is_guest_demo():
        return raw
    raw = raw.strip()
    if not raw:
        return raw
    if raw.isdigit():
        return mask_student_username(raw)
    if len(raw) == 1:
        return "○"
    if len(raw) == 2:
        return raw[0] + "○"
    return raw[0] + "○" * (len(raw) - 2) + raw[-1]


def _admin_record(db):
    from models import User

    return db.session.query(User.id, User.role).filter(User.username == "admin").first()


def _admin_teacher_id(db) -> int:
    admin = _admin_record(db)
    if admin is None or admin.role != "teacher":
        abort(503, description="Review Demo requires admin with teacher role.")
    return admin.id


def guest_demo_allowed(view: Callable[..., Any]) -> Callable[..., Any]:
    authenticated_view = login_required(view)

    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any):
        if current_user.is_authenticated or is_guest_demo():
            return view(*args, **kwargs)
        return authenticated_view(*args, **kwargs)
    return wrapped


def install_guest_demo(app, db) -> None:
    """Install entry route, auth bridge, mutation gate, and SQL backstop."""

    app.add_template_filter(mask_student_name, "review_student_name")
    app.add_template_filter(mask_student_username, "review_student_username")

    @app.route("/review-demo")
    def review_demo_entry():
        _admin_teacher_id(db)
        # Explicitly entering Review replaces any active login, including a
        # remembered login, with the ephemeral guest session.
        if current_user.is_authenticated:
            logout_user()
        session.pop("_user_id", None)
        session.pop("_fresh", None)
        session.pop("_id", None)
        session[SESSION_KEY] = True
        return redirect(url_for("teacher_dashboard"))

    @app.before_request
    def _guest_demo_request_gate():
        if not is_guest_demo():
            return None
        if current_user.is_authenticated:
            session.pop(SESSION_KEY, None)
            return None

        endpoint = request.endpoint or ""
        # Practice questions need no teacher identity; keep student progress
        # lookups in the existing route detached from admin's records.
        teacher_id = _admin_teacher_id(db)
        g._login_user = GuestDemoPrincipal(-1 if endpoint == "practice.next_question" else teacher_id)
        if endpoint == "login" and request.method == "POST":
            session.pop(SESSION_KEY, None)
            return None
        if endpoint == "logout":
            session.pop(SESSION_KEY, None)
            return redirect(url_for("login"))
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            return persistence_denied_response()
        if request.path.startswith("/admin/ai_prompt_settings") and endpoint not in {
            "core.ai_prompt_settings_page", "core.get_ai_prompt_setting",
        }:
            return persistence_denied_response()
        if endpoint == "core.get_ai_prompt_setting":
            # The settings UI needs provider/model structure, never credentials
            # or prompt content from the live admin API.
            from core.ai_settings import get_ai_settings_snapshot, get_google_model_options

            snapshot = get_ai_settings_snapshot()
            return jsonify(
                success=True, prompt="", ai_mode="cloud",
                cloud_model=snapshot["ai_cloud_model"],
                ai_default_provider=snapshot["ai_default_provider"],
                ai_model_roles={}, available_models=[],
                google_model_options=get_google_model_options(),
                has_gemini_api_key=False, masked_gemini_api_key="",
            )
        if request.method in {"GET", "HEAD", "OPTIONS"} and (
            endpoint in _NEVER_GUEST_GET_ENDPOINTS
            or request.path.startswith(_SENSITIVE_GET_PREFIXES)
        ):
            return persistence_denied_response()
        from core.vocational_student_home import VOCATIONAL_KEY

        session["current_curriculum"] = VOCATIONAL_KEY
        if endpoint != "dashboard" and endpoint and any(
            value != VOCATIONAL_KEY for value in request.args.getlist("curriculum")
        ):
            query = request.args.to_dict(flat=True)
            query["curriculum"] = VOCATIONAL_KEY
            return redirect(url_for(endpoint, **(request.view_args or {}), **query))
        if endpoint == "dashboard":
            from core.vocational_student_home import build_vocational_home_context
            from flask import render_template

            volume = request.args.get("volume")
            chapter = request.args.get("chapter")
            requested = request.args.getlist("curriculum")
            if request.args.get("view", "curriculum") != "curriculum" or any(
                value != VOCATIONAL_KEY for value in requested
            ):
                return redirect(url_for("dashboard", view="curriculum", curriculum=VOCATIONAL_KEY))
            if volume or chapter:
                if not requested:
                    return redirect(url_for(
                        "dashboard", view="curriculum", curriculum=VOCATIONAL_KEY,
                        **({"volume": volume} if volume else {}),
                        **({"chapter": chapter} if chapter else {}),
                    ))
            else:
                # Never reuse admin.id or a real student's identity for the preview.
                preview = SimpleNamespace(id=-1, username="展示學生", real_name="")
                context = build_vocational_home_context(preview)
                context.update(
                    class_rows=[], primary_class_name="", primary_seat_no=None,
                    continue_learning=None,
                    weekly_stats={"week_count": 0, "week_correct_rate_label": "—", "recent_label": "尚未開始"},
                )
                for card in context["volume_cards"]:
                    card["recent_skill_name"] = ""
                return render_template("vocational_student_home.html", **context, enrolled_classes=[])

        # Bypass exactly Flask-Login's wrapper for admitted routes. The guest
        # principal remains anonymous and existing in-view role checks remain.
        view = current_app.view_functions.get(endpoint)
        if view is not None and _is_login_required_wrapper(view):
            response = current_app.make_response(view.__wrapped__(**(request.view_args or {})))
            if endpoint == "core.get_class_students" and response.status_code == 200:
                payload = response.get_json(silent=True)
                if isinstance(payload, dict) and isinstance(payload.get("students"), list):
                    for student in payload["students"]:
                        if isinstance(student, dict):
                            for key in ("username", "student_number", "student_no"):
                                if key in student:
                                    student[key] = mask_student_username(student[key])
                            for key in ("real_name", "display_name"):
                                if key in student:
                                    student[key] = mask_student_name(student[key])
                    response.set_data(current_app.json.dumps(payload))
            return response
        return None

    def _deny_guest_sql_writes(conn, cursor, statement, parameters, context, executemany):
        sql = str(statement or "")
        sql = _SQL_PREFIX.sub("", sql, count=1)
        if is_guest_demo() and (";" in sql or not (_READ_SQL.match(sql) or _READ_SCHEMA_PRAGMA.match(sql))):
            raise PermissionError("guest_demo_persistence_denied")

    with app.app_context():
        event.listen(db.engine, "before_cursor_execute", _deny_guest_sql_writes)

    @app.errorhandler(PermissionError)
    def _guest_permission_error(exc):
        if is_guest_demo() and str(exc) == "guest_demo_persistence_denied":
            db.session.rollback()
            return persistence_denied_response()
        raise exc
