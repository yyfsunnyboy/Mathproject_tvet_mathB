"""Runtime-only SQLite connection safety settings."""

from __future__ import annotations

import logging
import sqlite3

from sqlalchemy import event


SQLITE_BUSY_TIMEOUT_MS = 30_000


def install_sqlite_connection_hardening(engine, *, logger=None) -> bool:
    """Apply required PRAGMAs to every DB-API connection from this engine."""
    if engine.url.get_backend_name() != "sqlite":
        return False
    if getattr(engine, "_mathproject_sqlite_hardening", False):
        return True

    log = logger or logging.getLogger(__name__)

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute(f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}")
            current_mode = str(cursor.execute("PRAGMA journal_mode").fetchone()[0]).lower()
            if current_mode != "wal":
                current_mode = str(
                    cursor.execute("PRAGMA journal_mode=WAL").fetchone()[0]
                ).lower()
            if current_mode != "wal":
                raise RuntimeError(f"SQLite WAL mode unavailable: {current_mode}")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

    @event.listens_for(engine, "handle_error")
    def _log_sqlite_operational_error(exception_context) -> None:
        original = exception_context.original_exception
        if not isinstance(original, sqlite3.OperationalError):
            return
        message = str(original)
        if "locked" in message.lower():
            log.error("SQLite database locked: %s", message)
        else:
            log.error("SQLite OperationalError: %s", message)

    engine._mathproject_sqlite_hardening = True
    return True


def release_db_session_before_external_call(db, *, logger=None) -> None:
    """End the current request transaction and return its connection to the pool."""
    log = logger or logging.getLogger(__name__)
    scoped_session = db.session
    current = scoped_session()
    if current.new or current.dirty or current.deleted:
        log.warning(
            "Rolling back pending ORM state before external AI call: new=%s dirty=%s deleted=%s",
            len(current.new),
            len(current.dirty),
            len(current.deleted),
        )
    current.rollback()
    scoped_session.remove()
