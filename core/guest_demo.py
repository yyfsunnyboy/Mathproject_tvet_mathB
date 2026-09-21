"""Session-scoped, read-only guest review mode."""
from __future__ import annotations

import os
import re
from functools import wraps
from typing import Any, Callable

from flask import abort, current_app, flash, g, has_request_context, jsonify, redirect, request, session, url_for
from flask_login import AnonymousUserMixin, current_user, login_required
from sqlalchemy import event

SESSION_KEY = "guest_demo"
_WRITE_SQL = re.compile(r"^\s*(?:INSERT|UPDATE|DELETE|REPLACE|CREATE|ALTER|DROP|TRUNCATE|VACUUM|REINDEX|ATTACH|DETACH)\b", re.I)

_INTERACTIVE_POST_ENDPOINTS = frozenset({
    "practice.check_answer", "practice.draw_diagram",
    "practice.generate_similar_questions", "practice.generate_quiz_from_image",
    "practice.ai_check_handwriting", "practice.adaptive_submit_and_get_next",
    "practice.api_adv_rag_search", "practice.api_adv_rag_chat",
    "practice.chat_ai", "practice.analyze_handwriting",
    "practice.api_rag_search", "practice.api_rag_chat",
    "practice.tree_diagram_submit_api",
    "core.admin_example_v3_preview_generate",
    "adaptive_review.start_review_session", "adaptive_review.submit_feedback",
    "adaptive_review.check_handwriting", "adaptive_review.chat_with_tutor",
})
_NEVER_GUEST_GET_ENDPOINTS = frozenset({
    "practice.debug_clear_practice_state",
    "core.db_maintenance",
})


class GuestDemoPrincipal(AnonymousUserMixin):
    """Ephemeral display identity; never loaded from or stored in the DB."""

    id = None
    username = "Guest Demo"
    role = "teacher"
    is_admin = True

    @property
    def is_authenticated(self) -> bool:
        return False

    def get_id(self) -> None:
        return None


def is_guest_demo() -> bool:
    return bool(has_request_context() and session.get(SESSION_KEY) is True)


def _enabled() -> bool:
    return str(os.environ.get("REVIEW_DEMO_ENABLED", "")).strip().lower() in {"1", "true", "yes", "on"}


def _is_api_request() -> bool:
    return request.path.startswith("/api/") or request.is_json or request.accept_mimetypes.best == "application/json"


def _is_login_required_wrapper(view: Callable[..., Any]) -> bool:
    code = getattr(view, "__code__", None)
    filename = str(getattr(code, "co_filename", "")).replace("\\", "/").lower()
    return bool(hasattr(view, "__wrapped__") and "flask_login" in filename)


def persistence_denied_response():
    if _is_api_request():
        return jsonify(success=False, error="login_required_for_persistence"), 403
    flash("此功能需要登入後才能儲存。展示模式不會修改系統資料。")
    return redirect(request.referrer or url_for("teacher_dashboard"))


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

    @app.route("/review-demo")
    def review_demo_entry():
        if not _enabled():
            abort(404)
        # Never impersonate a User. Remove any prior Flask-Login identity.
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

        g._login_user = GuestDemoPrincipal()
        endpoint = request.endpoint or ""
        if endpoint == "login" and request.method == "POST":
            session.pop(SESSION_KEY, None)
            return None
        if endpoint == "logout":
            session.pop(SESSION_KEY, None)
            return redirect(url_for("login"))
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and endpoint not in _INTERACTIVE_POST_ENDPOINTS:
            return persistence_denied_response()
        if request.method in {"GET", "HEAD", "OPTIONS"} and endpoint in _NEVER_GUEST_GET_ENDPOINTS:
            return persistence_denied_response()

        # Bypass exactly Flask-Login's wrapper for admitted routes. The guest
        # principal remains anonymous and existing in-view role checks remain.
        view = current_app.view_functions.get(endpoint)
        if view is not None and _is_login_required_wrapper(view):
            return view.__wrapped__(**(request.view_args or {}))
        return None

    def _deny_guest_sql_writes(conn, cursor, statement, parameters, context, executemany):
        if is_guest_demo() and _WRITE_SQL.match(str(statement or "")):
            raise PermissionError("guest_demo_persistence_denied")

    with app.app_context():
        event.listen(db.engine, "before_cursor_execute", _deny_guest_sql_writes)

    @app.errorhandler(PermissionError)
    def _guest_permission_error(exc):
        if is_guest_demo() and str(exc) == "guest_demo_persistence_denied":
            db.session.rollback()
            return persistence_denied_response()
        raise exc
