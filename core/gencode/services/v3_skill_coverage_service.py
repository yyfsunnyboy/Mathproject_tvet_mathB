"""Read-only V3 skill component coverage helpers."""

from __future__ import annotations

import sqlite3
from typing import Any

from core.gencode.schema.gencode_component_tracker_inspection import tracker_table_exists
from core.gencode.services.component_tracker_service import derive_component_id

_TRACKER_STATUSES = frozenset(
    {
        "missing_tracker",
        "pending",
        "usable",
        "generating",
        "draft_written",
        "smoke_passed",
        "verified",
        "failed",
    }
)

_INCOMPLETE_FOR_PUBLISH = frozenset(
    {
        "missing_tracker",
        "draft_written",
        "smoke_passed",
        "failed",
        "pending",
        "usable",
        "generating",
    }
)


def _row_value(row: Any, key: str, index: int) -> Any:
    if hasattr(row, "keys"):
        return row[key]
    return row[index]


def _fetch_textbook_example_ids(conn: sqlite3.Connection, skill_id: str) -> list[int]:
    rows = conn.execute(
        """
        SELECT id
        FROM textbook_examples
        WHERE skill_id = ?
        ORDER BY id ASC
        """,
        (skill_id,),
    ).fetchall()
    return [int(_row_value(row, "id", 0)) for row in rows]


def _fetch_tracker_by_example_id(
    conn: sqlite3.Connection,
    skill_id: str,
) -> dict[int, dict[str, object]]:
    if not tracker_table_exists(conn):
        return {}
    rows = conn.execute(
        """
        SELECT textbook_example_id, component_id, gencode_status, gencode_error_log
        FROM gencode_component_tracker
        WHERE skill_id = ?
        ORDER BY textbook_example_id ASC
        """,
        (skill_id,),
    ).fetchall()
    mapped: dict[int, dict[str, object]] = {}
    for row in rows:
        example_id = int(_row_value(row, "textbook_example_id", 0))
        mapped[example_id] = {
            "textbook_example_id": example_id,
            "component_id": str(_row_value(row, "component_id", 1)),
            "gencode_status": str(_row_value(row, "gencode_status", 2)),
            "gencode_error_log": _row_value(row, "gencode_error_log", 3),
        }
    return mapped


def get_v3_skill_component_coverage(
    conn: sqlite3.Connection,
    skill_id: str,
) -> dict[str, object]:
    """Return textbook-example coverage vs tracker for one skill."""
    skill_key = str(skill_id or "").strip()
    example_ids = _fetch_textbook_example_ids(conn, skill_key)
    tracker_map = _fetch_tracker_by_example_id(conn, skill_key)

    examples: list[dict[str, object]] = []
    verified_count = 0
    missing_tracker_count = 0
    failed_count = 0
    unverified_count = 0

    for example_id in example_ids:
        tracker = tracker_map.get(example_id)
        if tracker is None:
            status = "missing_tracker"
            component_id = derive_component_id(example_id)
            missing_tracker_count += 1
            unverified_count += 1
            error_log = None
        else:
            status = str(tracker.get("gencode_status") or "missing_tracker")
            component_id = str(tracker.get("component_id") or derive_component_id(example_id))
            error_log = tracker.get("gencode_error_log")
            if status == "verified":
                verified_count += 1
            elif status == "failed":
                failed_count += 1
                unverified_count += 1
            elif status in _INCOMPLETE_FOR_PUBLISH:
                unverified_count += 1

        examples.append(
            {
                "textbook_example_id": example_id,
                "component_id": component_id,
                "status": status,
                "gencode_error_log": error_log,
            }
        )

    publish_ready = (
        verified_count >= 1
        and missing_tracker_count == 0
        and failed_count == 0
        and unverified_count == 0
    )

    return {
        "skill_id": skill_key,
        "total_examples": len(example_ids),
        "verified_count": verified_count,
        "missing_tracker_count": missing_tracker_count,
        "failed_count": failed_count,
        "unverified_count": unverified_count,
        "publish_ready": publish_ready,
        "examples": examples,
    }


def build_coverage_warnings(coverage: dict[str, object]) -> list[str]:
    """Build human-readable publish coverage warnings."""
    warnings: list[str] = []
    total = int(coverage.get("total_examples") or 0)
    verified = int(coverage.get("verified_count") or 0)
    if total == 0:
        warnings.append("V3 coverage: no textbook_examples found for skill")
        return warnings

    if verified < total:
        missing_ids = [
            str(row["textbook_example_id"])
            for row in coverage.get("examples", [])
            if isinstance(row, dict) and row.get("status") == "missing_tracker"
        ]
        failed_ids = [
            str(row["textbook_example_id"])
            for row in coverage.get("examples", [])
            if isinstance(row, dict) and row.get("status") == "failed"
        ]
        unverified_ids = [
            str(row["textbook_example_id"])
            for row in coverage.get("examples", [])
            if isinstance(row, dict)
            and row.get("status") not in {"verified", "missing_tracker", "failed"}
        ]
        message = f"V3 coverage incomplete: {verified}/{total} verified"
        if missing_ids:
            message += f", missing examples: {', '.join(missing_ids)}"
        if unverified_ids:
            message += f", unverified examples: {', '.join(unverified_ids)}"
        if failed_ids:
            message += f", failed examples: {', '.join(failed_ids)}"
        warnings.append(message)

    if not coverage.get("publish_ready"):
        warnings.append(
            "publish_ready=False: publish will only include verified tracker components, "
            "not all textbook_examples"
        )
    return warnings
