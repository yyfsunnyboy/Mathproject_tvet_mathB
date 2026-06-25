"""Read-only V3 skill component coverage helpers."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from core.gencode.schema.gencode_component_tracker_inspection import tracker_table_exists
from core.gencode.services.component_tracker_service import derive_component_id
from core.gencode.v3_error_codes import (
    DOMAIN_BINDING_MISSING,
    PACKAGING_FAILED,
    UNSUPPORTED_TASK_TYPE,
    canonical_error_code,
    is_domain_gap_error,
    is_pipeline_failure_error,
)

_TRACKER_STATUSES = frozenset(
    {
        "missing_tracker",
        "pending",
        "usable",
        "generating",
        "draft_written",
        "smoke_passed",
        "verified",
        "needs_human_review",
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
        "needs_human_review",
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
        SELECT textbook_example_id, component_id, gencode_status, gencode_error_log, induced_spec_payload
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
            "induced_spec_payload": _row_value(row, "induced_spec_payload", 4),
        }
    return mapped


def _payload_error_code(payload_raw: object, error_log: object) -> str:
    payload: dict[str, object] = {}
    if isinstance(payload_raw, dict):
        payload = payload_raw
    elif payload_raw is not None and str(payload_raw).strip():
        try:
            parsed = json.loads(str(payload_raw))
        except Exception:
            parsed = None
        if isinstance(parsed, dict):
            payload = parsed
    code = str(payload.get("error_code") or "").strip()
    if code:
        return canonical_error_code(code)
    text = str(error_log or "").strip()
    if not text:
        return ""
    if ":" in text:
        return canonical_error_code(text.split(":", 1)[0])
    return canonical_error_code(text)


def _build_coverage_payload(
    skill_key: str,
    example_ids: list[int],
    tracker_map: dict[int, dict[str, object]],
) -> dict[str, object]:
    examples: list[dict[str, object]] = []
    verified_count = 0
    missing_tracker_count = 0
    failed_count = 0
    unsupported_count = 0
    domain_gap_count = 0
    bootstrap_failed_count = 0
    pipeline_failed_count = 0
    needs_human_review_count = 0
    unverified_count = 0

    for example_id in example_ids:
        tracker = tracker_map.get(example_id)
        error_log = None
        error_code = ""
        if tracker is None:
            status = "missing_tracker"
            component_id = derive_component_id(example_id)
            missing_tracker_count += 1
            unverified_count += 1
        else:
            status = str(tracker.get("gencode_status") or "missing_tracker")
            component_id = str(tracker.get("component_id") or derive_component_id(example_id))
            error_log = tracker.get("gencode_error_log")
            error_code = _payload_error_code(tracker.get("induced_spec_payload"), error_log)
            if status == "verified":
                verified_count += 1
            elif status == "failed":
                failed_count += 1
                if error_code == UNSUPPORTED_TASK_TYPE:
                    unsupported_count += 1
                elif is_domain_gap_error(error_code):
                    domain_gap_count += 1
                elif is_pipeline_failure_error(error_code):
                    pipeline_failed_count += 1
                elif error_code in {DOMAIN_BINDING_MISSING, PACKAGING_FAILED}:
                    bootstrap_failed_count += 1
                unverified_count += 1
            elif status == "needs_human_review":
                needs_human_review_count += 1
                unverified_count += 1
            elif status in _INCOMPLETE_FOR_PUBLISH:
                unverified_count += 1

        examples.append(
            {
                "textbook_example_id": example_id,
                "component_id": component_id,
                "status": status,
                "gencode_error_log": error_log,
                "error_code": error_code,
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
        "unsupported_count": unsupported_count,
        "domain_gap_count": domain_gap_count,
        "bootstrap_failed_count": bootstrap_failed_count,
        "pipeline_failed_count": pipeline_failed_count,
        "published_count": verified_count,
        "needs_human_review_count": needs_human_review_count,
        "unverified_count": unverified_count,
        "publish_ready": publish_ready,
        "examples": examples,
    }


def _fetch_batch_textbook_example_ids(
    conn: sqlite3.Connection,
    skill_ids: list[str],
) -> dict[str, list[int]]:
    keys = [str(skill_id or "").strip() for skill_id in skill_ids if str(skill_id or "").strip()]
    if not keys:
        return {}
    placeholders = ",".join("?" for _ in keys)
    rows = conn.execute(
        f"""
        SELECT skill_id, id
        FROM textbook_examples
        WHERE skill_id IN ({placeholders})
        ORDER BY skill_id ASC, id ASC
        """,
        keys,
    ).fetchall()
    grouped: dict[str, list[int]] = {key: [] for key in keys}
    for row in rows:
        skill_key = str(_row_value(row, "skill_id", 0))
        grouped.setdefault(skill_key, []).append(int(_row_value(row, "id", 1)))
    return grouped


def _fetch_batch_tracker_by_example_id(
    conn: sqlite3.Connection,
    skill_ids: list[str],
) -> dict[str, dict[int, dict[str, object]]]:
    keys = [str(skill_id or "").strip() for skill_id in skill_ids if str(skill_id or "").strip()]
    if not keys or not tracker_table_exists(conn):
        return {key: {} for key in keys}
    placeholders = ",".join("?" for _ in keys)
    rows = conn.execute(
        f"""
        SELECT skill_id, textbook_example_id, component_id, gencode_status, gencode_error_log, induced_spec_payload
        FROM gencode_component_tracker
        WHERE skill_id IN ({placeholders})
        ORDER BY skill_id ASC, textbook_example_id ASC
        """,
        keys,
    ).fetchall()
    grouped: dict[str, dict[int, dict[str, object]]] = {key: {} for key in keys}
    for row in rows:
        skill_key = str(_row_value(row, "skill_id", 0))
        example_id = int(_row_value(row, "textbook_example_id", 1))
        grouped.setdefault(skill_key, {})[example_id] = {
            "textbook_example_id": example_id,
            "component_id": str(_row_value(row, "component_id", 2)),
            "gencode_status": str(_row_value(row, "gencode_status", 3)),
            "gencode_error_log": _row_value(row, "gencode_error_log", 4),
            "induced_spec_payload": _row_value(row, "induced_spec_payload", 5),
        }
    return grouped


def get_v3_skill_component_coverage(
    conn: sqlite3.Connection,
    skill_id: str,
) -> dict[str, object]:
    """Return textbook-example coverage vs tracker for one skill."""
    skill_key = str(skill_id or "").strip()
    example_ids = _fetch_textbook_example_ids(conn, skill_key)
    tracker_map = _fetch_tracker_by_example_id(conn, skill_key)
    return _build_coverage_payload(skill_key, example_ids, tracker_map)


def get_v3_skills_component_coverage_batch(
    conn: sqlite3.Connection,
    skill_ids: list[str],
) -> dict[str, dict[str, object]]:
    """Return textbook-example coverage vs tracker for many skills with batched SQL."""
    keys = [str(skill_id or "").strip() for skill_id in skill_ids if str(skill_id or "").strip()]
    if not keys:
        return {}
    example_map = _fetch_batch_textbook_example_ids(conn, keys)
    tracker_map = _fetch_batch_tracker_by_example_id(conn, keys)
    return {
        skill_key: _build_coverage_payload(
            skill_key,
            example_map.get(skill_key, []),
            tracker_map.get(skill_key, {}),
        )
        for skill_key in keys
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
