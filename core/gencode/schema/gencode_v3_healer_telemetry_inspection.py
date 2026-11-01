# -*- coding: utf-8 -*-
"""Inspection / ensure helpers for gencode_v3_healer_telemetry_events."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DDL_PATH = Path(__file__).resolve().parent / "gencode_v3_healer_telemetry.sql"
TABLE_NAME = "gencode_v3_healer_telemetry_events"

REQUIRED_COLUMNS = (
    "id",
    "event_key",
    "event_type",
    "attempt_id",
    "generation_run_id",
    "component_id",
    "textbook_example_id",
    "skill_id",
    "mode",
    "environment",
    "data_origin",
    "failure_category",
    "tier",
    "rule_id",
    "repair_chain",
    "outcome",
    "original_sha256",
    "repaired_sha256",
    "certificate_status",
    "evidence_path",
    "created_at",
    "finished_at",
    "source_version",
)


def load_healer_telemetry_ddl() -> str:
    return DDL_PATH.read_text(encoding="utf-8")


def apply_healer_telemetry_ddl(conn: sqlite3.Connection) -> None:
    conn.executescript(load_healer_telemetry_ddl())


def healer_telemetry_table_exists(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (TABLE_NAME,),
    ).fetchone()
    return row is not None


def ensure_gencode_v3_healer_telemetry_table(conn: sqlite3.Connection) -> bool:
    """Create the telemetry table when missing; never drop or truncate existing data."""
    if healer_telemetry_table_exists(conn):
        return False
    apply_healer_telemetry_ddl(conn)
    try:
        conn.commit()
    except Exception:
        pass
    return True


def inspect_gencode_v3_healer_telemetry_schema(conn: sqlite3.Connection) -> dict[str, Any]:
    if not healer_telemetry_table_exists(conn):
        raise ValueError(f"{TABLE_NAME} table not found")
    columns = {str(row[1]) for row in conn.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall()}
    missing = [name for name in REQUIRED_COLUMNS if name not in columns]
    triggers = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name=?",
        (TABLE_NAME,),
    ).fetchall()
    return {
        "table": TABLE_NAME,
        "columns": sorted(columns),
        "missing_required_columns": missing,
        "append_only_trigger": any(str(t[0]) == "trg_gencode_v3_healer_tel_no_update" for t in triggers),
        "ok": not missing,
    }
