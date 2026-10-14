# -*- coding: utf-8 -*-
"""Force all pytest runs onto an isolated SQLite DB.

create_app() -> init_db() rebuilds skill_family_bridge whenever skills_info is
non-empty. Tests that import ``from app import app`` must never point at
instance/kumon_math.db.

Additionally:
- production DB file is marked read-only for the pytest session
- sqlite3.connect() to production without mode=ro is rejected
"""

from __future__ import annotations

import os
import sqlite3
import stat
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_PROD_DB = (_ROOT / "instance" / "kumon_math.db").resolve()
_ISOLATED_DIR = _ROOT / "tmp" / "pytest_db_isolation_20260923"
_ISOLATED_DIR.mkdir(parents=True, exist_ok=True)
_ISOLATED_DB = (_ISOLATED_DIR / "pytest_isolated.db").resolve()

# Always override — do not inherit a shell URI that might target production.
if _ISOLATED_DB.exists():
    try:
        _ISOLATED_DB.unlink()
    except OSError:
        pass
_ISOLATED_URI = f"sqlite:///{_ISOLATED_DB.as_posix()}"
os.environ["MATHPROJECT_DATABASE_URI"] = _ISOLATED_URI

_ORIGINAL_SQLITE_CONNECT = sqlite3.connect
_PROD_MODE = None


def _normalize_sqlite_path(uri_or_path: object) -> Path | None:
    text = str(uri_or_path or "").strip()
    if not text:
        return None
    if text.startswith("sqlite:///"):
        text = text[len("sqlite:///") :]
    if text.startswith("file:"):
        text = text[len("file:") :]
        if "?" in text:
            text = text.split("?", 1)[0]
    if text in {":memory:", ""}:
        return None
    try:
        return Path(text).resolve()
    except OSError:
        return None


def _is_production_db_uri(uri: str) -> bool:
    path = _normalize_sqlite_path(uri)
    return path is not None and path == _PROD_DB


def _is_ro_sqlite_target(database: object, uri: bool) -> bool:
    text = str(database or "")
    if "mode=ro" in text:
        return True
    if uri and text.startswith("file:") and "mode=ro" in text:
        return True
    return False


def _guarded_sqlite_connect(database, *args, **kwargs):
    path = _normalize_sqlite_path(database)
    uri = bool(kwargs.get("uri")) or str(database).startswith("file:")
    if path is not None and path == _PROD_DB:
        if not (_is_ro_sqlite_target(database, uri) or kwargs.get("uri") and "mode=ro" in str(database)):
            # Allow explicit read-only URI forms only.
            if not (uri and "mode=ro" in str(database)):
                raise RuntimeError(
                    f"Refusing writable sqlite connect to production DB during pytest: {database!r}. "
                    "Use file:...?mode=ro or an isolated temp DB."
                )
    return _ORIGINAL_SQLITE_CONNECT(database, *args, **kwargs)


def pytest_configure(config):  # noqa: ARG001
    if _is_production_db_uri(os.environ.get("MATHPROJECT_DATABASE_URI", "")):
        raise RuntimeError(
            "Refusing to run pytest against production DB "
            f"({_PROD_DB}). Set MATHPROJECT_DATABASE_URI to an isolated path."
        )
    import config as app_config

    app_config.Config.SQLALCHEMY_DATABASE_URI = _ISOLATED_URI
    config._mathproject_prod_db = _PROD_DB
    if _PROD_DB.exists():
        stat_before = _PROD_DB.stat()
        config._mathproject_prod_mtime_ns = stat_before.st_mtime_ns
        config._mathproject_prod_size = stat_before.st_size
        config._mathproject_prod_mode = stat_before.st_mode
        # Lock production DB read-only for the session (best-effort on Windows).
        try:
            os.chmod(_PROD_DB, stat.S_IREAD)
        except OSError:
            pass
    else:
        config._mathproject_prod_mtime_ns = None
        config._mathproject_prod_size = None
        config._mathproject_prod_mode = None

    sqlite3.connect = _guarded_sqlite_connect  # type: ignore[assignment]


@pytest.fixture(scope="session", autouse=True)
def _seed_isolated_admin_user():
    """Ensure Flask-Login session `_user_id=1` resolves on the empty isolated DB."""
    from app import app
    from models import User, db

    with app.app_context():
        user = db.session.get(User, 1)
        if user is None:
            db.session.add(
                User(
                    username="pytest_isolation_admin",
                    password_hash="x",
                    role="admin",
                )
            )
            db.session.commit()
            user = db.session.get(User, 1)
        if user is None or int(user.id) != 1:
            raise RuntimeError("Failed to seed isolated admin user id=1 for pytest auth")


def pytest_sessionfinish(session, exitstatus):  # noqa: ARG001
    sqlite3.connect = _ORIGINAL_SQLITE_CONNECT  # type: ignore[assignment]
    prod = getattr(session.config, "_mathproject_prod_db", None)
    before_mtime = getattr(session.config, "_mathproject_prod_mtime_ns", None)
    before_size = getattr(session.config, "_mathproject_prod_size", None)
    prev_mode = getattr(session.config, "_mathproject_prod_mode", None)
    if prod is not None and Path(prod).exists() and prev_mode is not None:
        try:
            os.chmod(prod, prev_mode | stat.S_IWRITE)
        except OSError:
            try:
                os.chmod(prod, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
    if prod is None or before_mtime is None or not Path(prod).exists():
        return
    after = Path(prod).stat()
    if after.st_mtime_ns != before_mtime or after.st_size != before_size:
        raise RuntimeError(
            "Production DB changed during pytest "
            f"(mtime/size before={before_mtime}/{before_size} "
            f"after={after.st_mtime_ns}/{after.st_size}). Isolation failed."
        )
