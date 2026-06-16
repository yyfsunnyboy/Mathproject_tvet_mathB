"""Inspection helpers for gencode_component_tracker schema contracts."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DDL_PATH = Path(__file__).resolve().parent / "gencode_component_tracker.sql"
MIGRATION_PATH = (
    PROJECT_ROOT / "migrations" / "versions" / "20250616_0001_create_gencode_component_tracker.py"
)

REQUIRED_COLUMNS = (
    "id",
    "textbook_example_id",
    "skill_id",
    "component_id",
    "gencode_status",
    "induced_spec_payload",
    "gencode_error_log",
    "created_at",
    "updated_at",
)

ALLOWED_GENCODE_STATUSES = (
    "pending",
    "usable",
    "generating",
    "draft_written",
    "smoke_passed",
    "verified",
    "failed",
)

FORBIDDEN_COLUMNS = frozenset({"component_path"})


def load_tracker_ddl() -> str:
    return DDL_PATH.read_text(encoding="utf-8")


def apply_tracker_ddl(conn: sqlite3.Connection) -> None:
    conn.executescript(load_tracker_ddl())


def inspect_gencode_component_tracker_schema(conn: sqlite3.Connection) -> dict[str, Any]:
    """Return a structured inspection report for the tracker table."""
    table_rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='gencode_component_tracker'"
    ).fetchall()
    if not table_rows:
        raise ValueError("gencode_component_tracker table not found")

    column_rows = conn.execute("PRAGMA table_info(gencode_component_tracker)").fetchall()
    columns = {str(row[1]): row for row in column_rows}

    trigger_rows = conn.execute(
        """
        SELECT name, sql
        FROM sqlite_master
        WHERE type='trigger' AND tbl_name='gencode_component_tracker'
        """
    ).fetchall()

    index_rows = conn.execute("PRAGMA index_list(gencode_component_tracker)").fetchall()
    index_sql: list[str] = []
    for index_row in index_rows:
        index_name = str(index_row[1])
        index_info = conn.execute(f"PRAGMA index_info({index_name})").fetchall()
        index_sql.append(f"{index_name}:{index_info}")

    create_sql_row = conn.execute(
        """
        SELECT sql
        FROM sqlite_master
        WHERE type='table' AND name='gencode_component_tracker'
        """
    ).fetchone()
    create_sql = str(create_sql_row[0] if create_sql_row else "")

    missing_columns = [name for name in REQUIRED_COLUMNS if name not in columns]
    forbidden_present = sorted(name for name in FORBIDDEN_COLUMNS if name in columns)

    unique_checks = _verify_unique_constraints(conn)
    status_check = _verify_gencode_status_check(conn)

    return {
        "columns": sorted(columns.keys()),
        "missing_columns": missing_columns,
        "forbidden_columns_present": forbidden_present,
        "trigger_count": len(trigger_rows),
        "create_sql": create_sql,
        "unique_constraints": unique_checks,
        "gencode_status_check": status_check,
        "migration_file_exists": MIGRATION_PATH.is_file(),
        "ddl_file_exists": DDL_PATH.is_file(),
        "index_entries": index_sql,
    }


def assert_tracker_schema_contract(conn: sqlite3.Connection) -> None:
    fresh = sqlite3.connect(":memory:")
    try:
        apply_tracker_ddl(fresh)
        report = inspect_gencode_component_tracker_schema(fresh)
    finally:
        fresh.close()

    if report["missing_columns"]:
        raise AssertionError(f"missing columns: {report['missing_columns']}")
    if report["forbidden_columns_present"]:
        raise AssertionError(
            f"forbidden columns present: {report['forbidden_columns_present']}"
        )
    if report["trigger_count"]:
        raise AssertionError("database triggers must not exist on gencode_component_tracker")
    if not report["unique_constraints"]["textbook_example_id_unique"]:
        raise AssertionError("missing UNIQUE(textbook_example_id)")
    if not report["unique_constraints"]["skill_component_unique"]:
        raise AssertionError("missing UNIQUE(skill_id, component_id)")
    if not report["gencode_status_check"]["enforced"]:
        raise AssertionError("gencode_status CHECK constraint not enforced")


def _verify_unique_constraints(conn: sqlite3.Connection) -> dict[str, bool]:
    import random

    base = random.randint(10_000, 90_000)
    textbook_unique = False
    skill_component_unique = False

    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status
        ) VALUES (?, 'skill_a', ?, 'pending')
        """,
        (base + 1, f"src_{base + 1}"),
    )
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status
        ) VALUES (?, 'skill_a', ?, 'pending')
        """,
        (base + 2, f"src_{base + 2}"),
    )
    conn.commit()

    try:
        conn.execute(
            """
            INSERT INTO gencode_component_tracker (
                textbook_example_id, skill_id, component_id, gencode_status
            ) VALUES (?, 'skill_b', ?, 'pending')
            """,
            (base + 1, f"src_{base + 999}"),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        textbook_unique = True
        conn.rollback()

    try:
        conn.execute(
            """
            INSERT INTO gencode_component_tracker (
                textbook_example_id, skill_id, component_id, gencode_status
            ) VALUES (?, 'skill_a', ?, 'pending')
            """,
            (base + 3, f"src_{base + 2}"),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        skill_component_unique = True
        conn.rollback()

    return {
        "textbook_example_id_unique": textbook_unique,
        "skill_component_unique": skill_component_unique,
    }


def _verify_gencode_status_check(conn: sqlite3.Connection) -> dict[str, Any]:
    import random

    base = random.randint(100_000, 900_000)
    allowed_ok = True
    rejected = False
    for offset, status in enumerate(ALLOWED_GENCODE_STATUSES):
        try:
            conn.execute(
                """
                INSERT INTO gencode_component_tracker (
                    textbook_example_id, skill_id, component_id, gencode_status
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    base + offset,
                    "skill_check",
                    f"src_check_{base + offset}",
                    status,
                ),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            allowed_ok = False
            conn.rollback()

    try:
        conn.execute(
            """
            INSERT INTO gencode_component_tracker (
                textbook_example_id, skill_id, component_id, gencode_status
            ) VALUES (?, 'skill_check', ?, 'random_status')
            """,
            (base + 999, f"src_invalid_{base}"),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        rejected = True
        conn.rollback()

    return {
        "allowed_statuses_insertable": allowed_ok,
        "invalid_status_rejected": rejected,
        "enforced": allowed_ok and rejected,
    }
