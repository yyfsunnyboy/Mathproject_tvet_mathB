# -*- coding: utf-8 -*-
"""Inspection / ensure helpers for gencode_v3_orchestrator_jobs."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DDL_PATH = Path(__file__).resolve().parent / "gencode_v3_orchestrator_jobs.sql"

REQUIRED_COLUMNS = (
    "id",
    "job_id",
    "skill_id",
    "stage",
    "status",
    "started_at",
    "updated_at",
    "payload_json",
)


def load_orchestrator_jobs_ddl() -> str:
    return DDL_PATH.read_text(encoding="utf-8")


def apply_orchestrator_jobs_ddl(conn: sqlite3.Connection) -> None:
    conn.executescript(load_orchestrator_jobs_ddl())


def orchestrator_jobs_table_exists(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name='gencode_v3_orchestrator_jobs'"
    ).fetchone()
    return row is not None


def ensure_gencode_v3_orchestrator_jobs_table(conn: sqlite3.Connection) -> bool:
    """Create job table when missing; never drop or truncate existing data."""
    if orchestrator_jobs_table_exists(conn):
        return False
    apply_orchestrator_jobs_ddl(conn)
    try:
        conn.commit()
    except Exception:
        pass
    return True


def inspect_gencode_v3_orchestrator_jobs_schema(conn: sqlite3.Connection) -> dict[str, Any]:
    if not orchestrator_jobs_table_exists(conn):
        raise ValueError("gencode_v3_orchestrator_jobs table not found")
    column_rows = conn.execute("PRAGMA table_info(gencode_v3_orchestrator_jobs)").fetchall()
    columns = {str(row[1]): row for row in column_rows}
    missing = [name for name in REQUIRED_COLUMNS if name not in columns]
    return {
        "table": "gencode_v3_orchestrator_jobs",
        "columns": sorted(columns),
        "missing_required_columns": missing,
        "ok": not missing,
    }
