# -*- coding: utf-8 -*-
"""Retry affected components after verified domain promotion."""

from __future__ import annotations

import sqlite3
from typing import Any, Callable

from core.gencode.domain_bootstrap.models import DomainGapReport
from core.gencode.services.component_tracker_service import derive_component_id
from core.gencode.v3_error_codes import DOMAIN_CAPABILITY_PARTIAL, DOMAIN_CAPABILITY_UNRESOLVED

DOMAIN_GAP_CODES = frozenset({DOMAIN_CAPABILITY_PARTIAL, DOMAIN_CAPABILITY_UNRESOLVED})


def list_affected_tracker_rows(
    conn: sqlite3.Connection,
    gap_report: DomainGapReport,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    example_ids = {int(x) for x in (gap_report.source_example_ids or [])}
    skill_ids = {str(x) for x in (gap_report.affected_skill_ids or [])}
    if not example_ids and not skill_ids:
        return rows

    query = """
        SELECT textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload, gencode_error_log
        FROM gencode_component_tracker
    """
    for row in conn.execute(query).fetchall():
        example_id = int(row["textbook_example_id"] if hasattr(row, "keys") else row[0])
        skill_id = str(row["skill_id"] if hasattr(row, "keys") else row[1])
        if example_ids and example_id not in example_ids:
            continue
        if skill_ids and skill_id not in skill_ids:
            continue
        payload_raw = row["induced_spec_payload"] if hasattr(row, "keys") else row[4]
        error_log = str(row["gencode_error_log"] if hasattr(row, "keys") else row[5] or "")
        if not _is_domain_gap_row(payload_raw, error_log):
            status = str(row["gencode_status"] if hasattr(row, "keys") else row[3])
            if status == "verified":
                continue
        rows.append(
            {
                "textbook_example_id": example_id,
                "skill_id": skill_id,
                "component_id": str(row["component_id"] if hasattr(row, "keys") else row[2]),
                "gencode_status": str(row["gencode_status"] if hasattr(row, "keys") else row[3]),
            }
        )
    return rows


def _is_domain_gap_row(payload_raw: Any, error_log: str) -> bool:
    import json

    payload: dict[str, Any] = {}
    if isinstance(payload_raw, dict):
        payload = payload_raw
    elif payload_raw:
        try:
            parsed = json.loads(str(payload_raw))
            if isinstance(parsed, dict):
                payload = parsed
        except Exception:
            payload = {}
    code = str(payload.get("error_code") or "").strip()
    if code in DOMAIN_GAP_CODES:
        return True
    lowered = error_log.lower()
    return "domain_capability_unresolved" in lowered or "domain_capability_partial" in lowered


def retry_affected_components(
    conn: sqlite3.Connection,
    *,
    gap_report: DomainGapReport,
    dryrun_runner: Callable[..., dict[str, Any]],
    dryrun_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Retry only components affected by the gap."""
    kwargs = dict(dryrun_kwargs or {})
    affected = list_affected_tracker_rows(conn, gap_report)
    results: list[dict[str, Any]] = []
    success_count = 0
    failed_count = 0

    for row in affected:
        if str(row.get("gencode_status")) == "verified":
            results.append({**row, "status": "skipped_verified"})
            continue
        try:
            outcome = dryrun_runner(
                conn=conn,
                textbook_example_id=int(row["textbook_example_id"]),
                skill_id=str(row["skill_id"]),
                **kwargs,
            )
            status = str(outcome.get("status") or outcome.get("tracker_status") or "processed")
            if status in {"verified", "processed"}:
                success_count += 1
            else:
                failed_count += 1
            results.append({**row, "status": status, "outcome": outcome})
        except Exception as exc:
            failed_count += 1
            results.append({**row, "status": "failed", "error": str(exc)})

    return {
        "gap_id": gap_report.gap_id,
        "affected_count": len(affected),
        "success_count": success_count,
        "failed_count": failed_count,
        "results": results,
    }
