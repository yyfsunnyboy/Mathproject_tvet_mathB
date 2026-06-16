"""Gencode component tracker shadow-table service (sqlite3 only)."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

ALLOWED_GENCODE_STATUSES = frozenset(
    {
        "pending",
        "usable",
        "generating",
        "draft_written",
        "smoke_passed",
        "verified",
        "failed",
    }
)

_TRACKER_COLUMNS = (
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


def derive_component_id(textbook_example_id: int) -> str:
    """Return canonical component_id for a textbook example."""
    if not isinstance(textbook_example_id, int) or isinstance(textbook_example_id, bool):
        raise ValueError("textbook_example_id must be an integer.")
    return f"src_{textbook_example_id}"


def derive_component_path(
    skill_id: str,
    component_id: str,
    base_dir: str = "agent_skills_v3",
) -> str:
    """Derive on-disk component directory without persisting path in DB."""
    skill_key = str(skill_id or "").strip()
    component_key = str(component_id or "").strip()
    base_key = str(base_dir or "").strip().strip("/\\")
    if not skill_key:
        raise ValueError("skill_id must be provided.")
    if not component_key:
        raise ValueError("component_id must be provided.")
    if not base_key:
        raise ValueError("base_dir must be provided.")
    return f"{base_key}/{skill_key}/components/{component_key}/"


def assert_textbook_example_skill(
    conn: sqlite3.Connection,
    *,
    textbook_example_id: int,
    skill_id: str,
) -> None:
    """Assert tracker skill_id matches textbook_examples administrative ownership."""
    row = conn.execute(
        "SELECT skill_id FROM textbook_examples WHERE id = ?",
        (textbook_example_id,),
    ).fetchone()
    if row is None:
        raise ValueError("textbook_example_not_found")
    example_skill_id = str(row[0] if not hasattr(row, "keys") else row["skill_id"])
    if example_skill_id != str(skill_id):
        raise ValueError("skill_id_mismatch")


def _validate_gencode_status(gencode_status: str) -> str:
    status = str(gencode_status or "").strip()
    if status not in ALLOWED_GENCODE_STATUSES:
        raise ValueError(f"invalid_gencode_status: {status!r}")
    return status


def _serialize_induced_spec_payload(
    induced_spec_payload: dict[str, object] | str | None,
) -> str | None:
    if induced_spec_payload is None:
        return None
    if isinstance(induced_spec_payload, dict):
        return json.dumps(induced_spec_payload, ensure_ascii=False)
    return str(induced_spec_payload)


def _fetch_tracker_row(
    conn: sqlite3.Connection,
    *,
    textbook_example_id: int,
) -> dict[str, object] | None:
    row = conn.execute(
        """
        SELECT
            id,
            textbook_example_id,
            skill_id,
            component_id,
            gencode_status,
            induced_spec_payload,
            gencode_error_log,
            created_at,
            updated_at
        FROM gencode_component_tracker
        WHERE textbook_example_id = ?
        """,
        (textbook_example_id,),
    ).fetchone()
    if row is None:
        return None
    if hasattr(row, "keys"):
        return {key: row[key] for key in _TRACKER_COLUMNS}
    return dict(zip(_TRACKER_COLUMNS, row, strict=True))


def save_tracker_record(
    conn: sqlite3.Connection,
    *,
    textbook_example_id: int,
    skill_id: str,
    gencode_status: str = "pending",
    induced_spec_payload: dict[str, object] | str | None = None,
    gencode_error_log: str | None = None,
) -> dict[str, object]:
    """Insert or upsert a tracker row after administrative ownership assertion."""
    status = _validate_gencode_status(gencode_status)
    assert_textbook_example_skill(
        conn,
        textbook_example_id=textbook_example_id,
        skill_id=skill_id,
    )

    component_id = derive_component_id(textbook_example_id)
    payload_text = _serialize_induced_spec_payload(induced_spec_payload)

    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id,
            skill_id,
            component_id,
            gencode_status,
            induced_spec_payload,
            gencode_error_log,
            created_at,
            updated_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?,
            datetime('now', 'localtime'),
            datetime('now', 'localtime')
        )
        ON CONFLICT(textbook_example_id) DO UPDATE SET
            skill_id = excluded.skill_id,
            component_id = excluded.component_id,
            gencode_status = excluded.gencode_status,
            induced_spec_payload = excluded.induced_spec_payload,
            gencode_error_log = excluded.gencode_error_log,
            updated_at = datetime('now', 'localtime')
        """,
        (
            textbook_example_id,
            str(skill_id),
            component_id,
            status,
            payload_text,
            gencode_error_log,
        ),
    )
    conn.commit()

    saved = _fetch_tracker_row(conn, textbook_example_id=textbook_example_id)
    if saved is None:
        raise RuntimeError("tracker_record_save_failed")
    return saved


def update_status(
    conn: sqlite3.Connection,
    *,
    textbook_example_id: int,
    skill_id: str,
    gencode_status: str,
    gencode_error_log: str | None = None,
) -> dict[str, object]:
    """Update tracker status after administrative ownership assertion."""
    status = _validate_gencode_status(gencode_status)
    assert_textbook_example_skill(
        conn,
        textbook_example_id=textbook_example_id,
        skill_id=skill_id,
    )

    existing = _fetch_tracker_row(conn, textbook_example_id=textbook_example_id)
    if existing is None:
        raise ValueError("tracker_record_not_found")

    conn.execute(
        """
        UPDATE gencode_component_tracker
        SET
            gencode_status = ?,
            gencode_error_log = ?,
            updated_at = datetime('now', 'localtime')
        WHERE textbook_example_id = ?
        """,
        (status, gencode_error_log, textbook_example_id),
    )
    conn.commit()

    updated = _fetch_tracker_row(conn, textbook_example_id=textbook_example_id)
    if updated is None:
        raise RuntimeError("tracker_record_update_failed")
    return updated
