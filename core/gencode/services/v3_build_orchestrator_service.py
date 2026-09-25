# -*- coding: utf-8 -*-
"""One-click Gencode V3 build orchestrator with durable job state."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.gencode.schema.gencode_component_tracker_inspection import (
    ensure_gencode_component_tracker_table,
)
from core.gencode.schema.gencode_v3_orchestrator_jobs_inspection import (
    ensure_gencode_v3_orchestrator_jobs_table,
)
from core.gencode.services.v3_example_disposition import (
    disposition_from_phase1_probe,
    summarize_dispositions,
)
from core.gencode.services.v3_skill_capability_preflight_service import (
    CAPABILITY_INVALID,
    CAPABILITY_MISSING,
    CAPABILITY_NEEDS_CAPABILITY,
    CAPABILITY_READY,
    evaluate_skill_v3_capability,
)
from core.gencode.services.v3_skill_coverage_service import get_v3_skill_component_coverage
from core.textbook_processor import is_outline_skill_id

STAGES = (
    "LOAD_EXAMPLES",
    "PREFLIGHT",
    "CAPABILITY_MATCH",
    "COMPONENT_BUILD",
    "VALIDATION",
    "SMOKE_TEST",
    "PUBLISH",
    "FINALIZE",
)

STAGE_LABELS = {
    "LOAD_EXAMPLES": "教材分析",
    "PREFLIGHT": "Preflight",
    "CAPABILITY_MATCH": "Capability matching",
    "COMPONENT_BUILD": "Components",
    "VALIDATION": "Validation",
    "SMOKE_TEST": "Smoke",
    "PUBLISH": "Publish",
    "FINALIZE": "Finalize",
}

JOB_STATUS_RUNNING = "running"
JOB_STATUS_READY = "ready"
JOB_STATUS_FAILED = "failed"
JOB_STATUS_NEEDS_CAPABILITY = "needs_capability"
JOB_STATUS_BLOCKED = "blocked"
JOB_STATUS_ACCEPTED = "accepted"

# Keep DDL alias for backward-compatible imports/tests.
DDL = (
    Path(__file__).resolve().parents[1]
    / "schema"
    / "gencode_v3_orchestrator_jobs.sql"
).read_text(encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_orchestrator_jobs_table(conn: sqlite3.Connection) -> None:
    ensure_gencode_v3_orchestrator_jobs_table(conn)


def _stage_done(payload: dict[str, Any], stage: str) -> bool:
    entry = (payload.get("stages") or {}).get(stage) or {}
    return str(entry.get("status") or "") in {"done", "skipped", "needs_capability"}


def _stage_index(stage: str) -> int:
    try:
        return STAGES.index(stage)
    except ValueError:
        return -1


def _empty_counts() -> dict[str, int]:
    return {
        "example_count": 0,
        "eligible_count": 0,
        "published_count": 0,
        "skip_count": 0,
        "missing_count": 0,
        "needs_capability_count": 0,
    }


def _default_stage_map() -> dict[str, dict[str, Any]]:
    return {
        stage: {
            "name": stage,
            "label": STAGE_LABELS[stage],
            "status": "pending",
            "reason": "",
            "started_at": None,
            "finished_at": None,
        }
        for stage in STAGES
    }


def _new_payload(skill_id: str) -> dict[str, Any]:
    return {
        "skill_id": skill_id,
        "stages": _default_stage_map(),
        "counts": _empty_counts(),
        "errors": [],
        "skip_examples": [],
        "needs_capability_examples": [],
        "resume_from": None,
        "dryrun_result": None,
        "publish_result": None,
        "production_preserved": True,
        "idempotent": False,
        "final_status": None,
        "allow_v3_rebuild": False,
    }


def _load_job_row(conn: sqlite3.Connection, skill_id: str) -> dict[str, Any] | None:
    ensure_orchestrator_jobs_table(conn)
    row = conn.execute(
        """
        SELECT job_id, skill_id, stage, status, started_at, updated_at, payload_json
        FROM gencode_v3_orchestrator_jobs
        WHERE skill_id = ?
        ORDER BY updated_at DESC, id DESC
        LIMIT 1
        """,
        (skill_id,),
    ).fetchone()
    if not row:
        return None
    if hasattr(row, "keys"):
        payload_raw = row["payload_json"]
        data = {
            "job_id": row["job_id"],
            "skill_id": row["skill_id"],
            "stage": row["stage"],
            "status": row["status"],
            "started_at": row["started_at"],
            "updated_at": row["updated_at"],
        }
    else:
        payload_raw = row[6]
        data = {
            "job_id": row[0],
            "skill_id": row[1],
            "stage": row[2],
            "status": row[3],
            "started_at": row[4],
            "updated_at": row[5],
        }
    try:
        payload = json.loads(payload_raw or "{}")
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    data["payload"] = payload
    return data


def get_orchestrator_job(conn: sqlite3.Connection, skill_id: str) -> dict[str, Any] | None:
    row = _load_job_row(conn, str(skill_id or "").strip())
    if not row:
        return None
    payload = row.get("payload") or {}
    return {
        "job_id": row["job_id"],
        "skill_id": row["skill_id"],
        "stage": row["stage"],
        "status": row["status"],
        "started_at": row["started_at"],
        "updated_at": row["updated_at"],
        "counts": payload.get("counts") or _empty_counts(),
        "errors": payload.get("errors") or [],
        "skip_examples": payload.get("skip_examples") or [],
        "needs_capability_examples": payload.get("needs_capability_examples") or [],
        "stages": payload.get("stages") or _default_stage_map(),
        "final_status": payload.get("final_status") or row["status"],
        "allow_v3_rebuild": bool(payload.get("allow_v3_rebuild")),
        "production_preserved": bool(payload.get("production_preserved", True)),
        "idempotent": bool(payload.get("idempotent")),
    }


def _save_job(
    conn: sqlite3.Connection,
    *,
    job_id: str,
    skill_id: str,
    stage: str,
    status: str,
    started_at: str,
    payload: dict[str, Any],
) -> None:
    ensure_orchestrator_jobs_table(conn)
    updated_at = _now_iso()
    payload = dict(payload)
    payload["final_status"] = status if status != JOB_STATUS_RUNNING else payload.get("final_status")
    existing = conn.execute(
        "SELECT id FROM gencode_v3_orchestrator_jobs WHERE job_id = ?",
        (job_id,),
    ).fetchone()
    payload_json = json.dumps(payload, ensure_ascii=False)
    if existing:
        conn.execute(
            """
            UPDATE gencode_v3_orchestrator_jobs
            SET stage = ?, status = ?, updated_at = ?, payload_json = ?
            WHERE job_id = ?
            """,
            (stage, status, updated_at, payload_json, job_id),
        )
    else:
        conn.execute(
            """
            INSERT INTO gencode_v3_orchestrator_jobs (
                job_id, skill_id, stage, status, started_at, updated_at, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (job_id, skill_id, stage, status, started_at, updated_at, payload_json),
        )
    try:
        conn.commit()
    except Exception:
        pass


def _mark_stage(
    payload: dict[str, Any],
    stage: str,
    status: str,
    *,
    reason: str = "",
) -> None:
    stages = payload.setdefault("stages", _default_stage_map())
    entry = stages.setdefault(
        stage,
        {"name": stage, "label": STAGE_LABELS.get(stage, stage), "status": "pending"},
    )
    entry["status"] = status
    entry["reason"] = reason
    now = _now_iso()
    if status == "running":
        entry["started_at"] = now
    if status in {"done", "failed", "skipped", "needs_capability"}:
        entry["finished_at"] = now


def _append_error(payload: dict[str, Any], *, stage: str, code: str, message: str) -> None:
    errors = payload.setdefault("errors", [])
    errors.append({"stage": stage, "code": code, "message": message})


def _public_result(
    *,
    job_id: str,
    skill_id: str,
    stage: str,
    status: str,
    started_at: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    counts = payload.get("counts") or _empty_counts()
    return {
        "ok": status in {JOB_STATUS_READY, JOB_STATUS_NEEDS_CAPABILITY} or (
            status == JOB_STATUS_READY
        ),
        "success": status == JOB_STATUS_READY,
        "job_id": job_id,
        "skill_id": skill_id,
        "stage": stage,
        "status": status,
        "final_status": str(payload.get("final_status") or status).upper()
        if status != JOB_STATUS_RUNNING
        else "RUNNING",
        "started_at": started_at,
        "updated_at": _now_iso(),
        "counts": counts,
        "errors": payload.get("errors") or [],
        "skip_examples": payload.get("skip_examples") or [],
        "needs_capability_examples": payload.get("needs_capability_examples") or [],
        "stages": [
            {
                "name": name,
                "label": STAGE_LABELS[name],
                **(payload.get("stages") or {}).get(name, {}),
            }
            for name in STAGES
        ],
        "allow_v3_rebuild": bool(payload.get("allow_v3_rebuild")),
        "production_preserved": bool(payload.get("production_preserved", True)),
        "idempotent": bool(payload.get("idempotent")),
        "ui_status": _ui_status_from_job(status, payload),
    }


def _ui_status_from_job(status: str, payload: dict[str, Any]) -> str:
    if status == JOB_STATUS_RUNNING:
        return "建置中"
    if status == JOB_STATUS_NEEDS_CAPABILITY:
        return "NEEDS_CAPABILITY"
    if status == JOB_STATUS_FAILED:
        return "FAILED"
    if status == JOB_STATUS_READY:
        return "READY"
    if status == JOB_STATUS_BLOCKED:
        return "BLOCKED"
    if payload.get("allow_v3_rebuild"):
        return "REBUILD"
    return "建立 V3"


def derive_skill_v3_ui_status(
    *,
    capability_status: str,
    coverage: dict[str, Any] | None,
    job: dict[str, Any] | None = None,
    production_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive /skills CTA status from capability + coverage + latest job."""
    if job and str(job.get("status") or "") == JOB_STATUS_RUNNING:
        return {
            "ui_status": "建置中",
            "cta_label": "建置中",
            "allow_v3_rebuild": False,
            "primary_action": "poll_job",
        }
    if job and str(job.get("status") or "") == JOB_STATUS_NEEDS_CAPABILITY:
        return {
            "ui_status": "NEEDS_CAPABILITY",
            "cta_label": "NEEDS_CAPABILITY",
            "allow_v3_rebuild": False,
            "primary_action": "show_needs_capability",
            "needs_capability_examples": job.get("needs_capability_examples") or [],
        }
    if job and str(job.get("status") or "") == JOB_STATUS_FAILED:
        return {
            "ui_status": "FAILED",
            "cta_label": "重試建立 V3",
            "allow_v3_rebuild": False,
            "primary_action": "retry_build",
        }

    coverage = coverage or {}
    production_info = production_info or {}
    eligible = int(coverage.get("eligible_count") or 0)
    if eligible < 1:
        # Prefer explicit eligible; fall back to total - intentional skips.
        total = int(coverage.get("total_examples") or 0)
        skips = int(coverage.get("intentional_skip_count") or 0)
        eligible = max(0, total - skips)
    published = int(coverage.get("verified_count") or coverage.get("published_count") or 0)
    missing = int(coverage.get("missing_tracker_count") or 0)
    needs_cap = int(
        (job or {}).get("counts", {}).get("needs_capability_count")
        if job
        else 0
    )
    cap = str(capability_status or "").strip()
    prod_components = int(production_info.get("production_component_count") or 0)
    prod_package = bool(production_info.get("v3_package_exists"))
    prod_wrapper = bool(production_info.get("production_wrapper_exists"))

    if cap == CAPABILITY_NEEDS_CAPABILITY or needs_cap > 0:
        return {
            "ui_status": "NEEDS_CAPABILITY",
            "cta_label": "NEEDS_CAPABILITY",
            "allow_v3_rebuild": False,
            "primary_action": "show_needs_capability",
        }

    tracker_ready = (
        cap == CAPABILITY_READY
        and missing == 0
        and (eligible == 0 or published == eligible)
        and bool(coverage.get("publish_ready", published == eligible and missing == 0))
    )
    # Published on disk but tracker not yet mirrored into this DB (common after
    # isolated publish). Still treat as READY when capability + package cover eligible.
    package_ready = (
        cap == CAPABILITY_READY
        and prod_package
        and prod_wrapper
        and eligible > 0
        and prod_components >= eligible
    )
    if tracker_ready or package_ready or (cap == CAPABILITY_READY and published == eligible and missing == 0):
        return {
            "ui_status": "READY",
            "cta_label": "REBUILD",
            "allow_v3_rebuild": True,
            "primary_action": "rebuild",
        }
    if cap == CAPABILITY_READY:
        return {
            "ui_status": "建立 V3",
            "cta_label": "建立 V3",
            "allow_v3_rebuild": True,
            "primary_action": "build",
        }
    return {
        "ui_status": "建立 V3",
        "cta_label": "建立 V3",
        "allow_v3_rebuild": False,
        "primary_action": "build",
    }


def _list_production_component_ids(project_root: str | Path, skill_id: str) -> set[str]:
    root = Path(project_root) / "agent_skills_v3" / skill_id / "components"
    if not root.is_dir():
        return set()
    return {p.name for p in root.iterdir() if p.is_dir() and (p / "generate.py").is_file()}


def _eligible_component_ids(example_ids: list[int], skip_ids: set[int]) -> set[str]:
    return {f"src_{eid}" for eid in example_ids if eid not in skip_ids}


def run_v3_build_orchestrator(
    conn: sqlite3.Connection,
    skill_id: str,
    *,
    project_root: str,
    staging_root: str,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    mode: str = "auto",
    force: bool = False,
    smoke: bool = True,
    resume: bool = True,
    job_id: str | None = None,
    seed: int | None = 42,
) -> dict[str, Any]:
    """
    Run the one-click V3 build pipeline.

    Uses only already-registered domain capabilities. Never invents new Python
    domain / registry / YAML capability code.

    Persists after every stage. When ``resume=True``, completed stages are not
    re-executed; failed/running jobs continue from the unfinished stage.
    """
    from core.gencode.services.admin_gencode_action_service import (
        run_admin_v3_dryrun_for_skill,
        run_admin_v3_publish_for_skill,
        _prepare_publish_staging_components,
    )
    from core.gencode.services.v3_publish_eligibility import evaluate_v3_publish_eligibility

    ensure_gencode_component_tracker_table(conn)
    ensure_orchestrator_jobs_table(conn)

    skill_key = str(skill_id or "").strip()
    if not skill_key:
        raise ValueError("missing_skill_id")
    if is_outline_skill_id(skill_key):
        raise ValueError("outline_skill_not_supported_for_v3_build")

    previous = _load_job_row(conn, skill_key) if resume else None
    if previous and job_id and str(previous.get("job_id") or "") != str(job_id):
        # Prefer explicit job_id match when provided.
        row = conn.execute(
            "SELECT job_id, skill_id, stage, status, started_at, updated_at, payload_json "
            "FROM gencode_v3_orchestrator_jobs WHERE job_id = ?",
            (str(job_id),),
        ).fetchone()
        if row:
            previous = _load_job_row(conn, skill_key)  # fallback latest
            # rebuild previous from job_id row
            if hasattr(row, "keys"):
                payload_raw = row["payload_json"]
                previous = {
                    "job_id": row["job_id"],
                    "skill_id": row["skill_id"],
                    "stage": row["stage"],
                    "status": row["status"],
                    "started_at": row["started_at"],
                    "updated_at": row["updated_at"],
                    "payload": json.loads(payload_raw or "{}")
                    if isinstance(payload_raw, str)
                    else (payload_raw or {}),
                }
            else:
                previous = {
                    "job_id": row[0],
                    "skill_id": row[1],
                    "stage": row[2],
                    "status": row[3],
                    "started_at": row[4],
                    "updated_at": row[5],
                    "payload": json.loads(row[6] or "{}"),
                }

    resume_stage = None
    if (
        resume
        and previous
        and str(previous.get("status") or "") in {JOB_STATUS_FAILED, JOB_STATUS_RUNNING, JOB_STATUS_ACCEPTED}
        and not force
    ):
        resume_stage = str(previous.get("stage") or "") or None
        job_id = str(previous.get("job_id") or job_id or uuid.uuid4().hex)
        started_at = str(previous.get("started_at") or _now_iso())
        payload = dict(previous.get("payload") or _new_payload(skill_key))
        # Clear failed marker on the resume stage so it can re-run.
        if resume_stage and str((payload.get("stages") or {}).get(resume_stage, {}).get("status")) == "failed":
            (payload.setdefault("stages", {})).setdefault(resume_stage, {})["status"] = "pending"
            (payload["stages"][resume_stage])["reason"] = "resuming"
    else:
        job_id = str(job_id or uuid.uuid4().hex)
        started_at = _now_iso()
        payload = _new_payload(skill_key)

    payload["resume_from"] = resume_stage
    stage = "LOAD_EXAMPLES"
    if not _stage_done(payload, stage):
        _mark_stage(payload, stage, "running")
    _save_job(
        conn,
        job_id=job_id,
        skill_id=skill_key,
        stage=stage if not resume_stage else (resume_stage or stage),
        status=JOB_STATUS_RUNNING,
        started_at=started_at,
        payload=payload,
    )

    dryrun_result: dict[str, Any] = dict(payload.get("dryrun_result") or {})

    try:
        # 1-3) LOAD / PREFLIGHT / CAPABILITY_MATCH
        if not (
            _stage_done(payload, "LOAD_EXAMPLES")
            and _stage_done(payload, "PREFLIGHT")
            and _stage_done(payload, "CAPABILITY_MATCH")
        ):
            rows = conn.execute(
                """
                SELECT id FROM textbook_examples
                WHERE skill_id = ? AND skill_id NOT LIKE 'outline_%'
                ORDER BY id ASC
                """,
                (skill_key,),
            ).fetchall()
            example_ids = [int(r[0] if not hasattr(r, "keys") else r["id"]) for r in rows]
            if not _stage_done(payload, "LOAD_EXAMPLES"):
                stage = "LOAD_EXAMPLES"
                _mark_stage(payload, stage, "running")
                payload["counts"]["example_count"] = len(example_ids)
                _mark_stage(payload, "LOAD_EXAMPLES", "done")
                _save_job(
                    conn,
                    job_id=job_id,
                    skill_id=skill_key,
                    stage=stage,
                    status=JOB_STATUS_RUNNING,
                    started_at=started_at,
                    payload=payload,
                )

            if not _stage_done(payload, "PREFLIGHT"):
                stage = "PREFLIGHT"
                _mark_stage(payload, stage, "running")
                _save_job(
                    conn,
                    job_id=job_id,
                    skill_id=skill_key,
                    stage=stage,
                    status=JOB_STATUS_RUNNING,
                    started_at=started_at,
                    payload=payload,
                )
                capability = evaluate_skill_v3_capability(conn, skill_key, probe_examples=True)
                payload["capability"] = {
                    "capability_status": capability.get("capability_status"),
                    "domain_key": capability.get("domain_key"),
                    "allow_v3_rebuild": capability.get("allow_v3_rebuild"),
                }
                _mark_stage(payload, "PREFLIGHT", "done")
                _save_job(
                    conn,
                    job_id=job_id,
                    skill_id=skill_key,
                    stage=stage,
                    status=JOB_STATUS_RUNNING,
                    started_at=started_at,
                    payload=payload,
                )
            else:
                capability = {
                    "capability_status": (payload.get("capability") or {}).get("capability_status"),
                    "example_probes": [],
                    "allow_v3_rebuild": (payload.get("capability") or {}).get("allow_v3_rebuild"),
                }
                # Re-probe only when capability_match not done.
                if not _stage_done(payload, "CAPABILITY_MATCH"):
                    capability = evaluate_skill_v3_capability(conn, skill_key, probe_examples=True)

            if not _stage_done(payload, "CAPABILITY_MATCH"):
                stage = "CAPABILITY_MATCH"
                _mark_stage(payload, stage, "running")
                _save_job(
                    conn,
                    job_id=job_id,
                    skill_id=skill_key,
                    stage=stage,
                    status=JOB_STATUS_RUNNING,
                    started_at=started_at,
                    payload=payload,
                )
                if not capability.get("example_probes"):
                    capability = evaluate_skill_v3_capability(conn, skill_key, probe_examples=True)
                dispositions = [
                    disposition_from_phase1_probe(probe)
                    for probe in (capability.get("example_probes") or [])
                ]
                # When domain registry binding is absent/invalid, preflight skips
                # per-example probes but still classifies every textbook row as
                # needs_capability. Prefer that preflight summary over an empty
                # probe-derived disposition list (which would zero the counts and
                # incorrectly fail FINALIZE as CAPABILITY_MATCH: missing).
                if dispositions:
                    summary = summarize_dispositions(dispositions)
                else:
                    summary = {
                        "example_count": int(
                            capability.get("textbook_example_count") or len(example_ids)
                        ),
                        "eligible_count": int(
                            capability.get("eligible_example_count") or len(example_ids)
                        ),
                        "skip_count": int(capability.get("intentional_skip_count") or 0),
                        "needs_capability_count": int(
                            capability.get("needs_capability_count") or 0
                        ),
                        "skip_examples": list(capability.get("skip_examples") or []),
                        "needs_capability_examples": list(
                            capability.get("needs_capability_examples") or []
                        ),
                    }
                payload["counts"].update(
                    {
                        "example_count": int(summary.get("example_count") or len(example_ids)),
                        "eligible_count": int(summary.get("eligible_count") or 0),
                        "skip_count": int(summary.get("skip_count") or 0),
                        "needs_capability_count": int(summary.get("needs_capability_count") or 0),
                        "missing_count": 0,
                    }
                )
                payload["skip_examples"] = list(summary.get("skip_examples") or [])
                payload["needs_capability_examples"] = list(
                    summary.get("needs_capability_examples") or []
                )
                payload["capability"] = {
                    "capability_status": capability.get("capability_status"),
                    "domain_key": capability.get("domain_key"),
                    "allow_v3_rebuild": capability.get("allow_v3_rebuild"),
                    "missing_layers": list(capability.get("missing_layers") or []),
                    "wiring_error": capability.get("wiring_error") or "",
                }
                _mark_stage(payload, "CAPABILITY_MATCH", "done")
                _save_job(
                    conn,
                    job_id=job_id,
                    skill_id=skill_key,
                    stage=stage,
                    status=JOB_STATUS_RUNNING,
                    started_at=started_at,
                    payload=payload,
                )

                cap_status = str(capability.get("capability_status") or "").strip()
                soft_capability_block = cap_status in {
                    CAPABILITY_NEEDS_CAPABILITY,
                    CAPABILITY_MISSING,
                    CAPABILITY_INVALID,
                }
                if int(summary.get("needs_capability_count") or 0) > 0 or soft_capability_block:
                    _mark_stage(payload, "COMPONENT_BUILD", "skipped", reason="needs_capability")
                    _mark_stage(payload, "VALIDATION", "skipped", reason="needs_capability")
                    _mark_stage(payload, "SMOKE_TEST", "skipped", reason="needs_capability")
                    _mark_stage(payload, "PUBLISH", "skipped", reason="needs_capability")
                    _mark_stage(payload, "FINALIZE", "needs_capability")
                    payload["allow_v3_rebuild"] = False
                    payload["final_status"] = JOB_STATUS_NEEDS_CAPABILITY
                    payload["production_preserved"] = True
                    _save_job(
                        conn,
                        job_id=job_id,
                        skill_id=skill_key,
                        stage="FINALIZE",
                        status=JOB_STATUS_NEEDS_CAPABILITY,
                        started_at=started_at,
                        payload=payload,
                    )
                    return _public_result(
                        job_id=job_id,
                        skill_id=skill_key,
                        stage="FINALIZE",
                        status=JOB_STATUS_NEEDS_CAPABILITY,
                        started_at=started_at,
                        payload=payload,
                    )

                if capability.get("capability_status") != CAPABILITY_READY:
                    _append_error(
                        payload,
                        stage="CAPABILITY_MATCH",
                        code="CAPABILITY_NOT_READY",
                        message=str(capability.get("capability_status") or "not_ready"),
                    )
                    _mark_stage(payload, "FINALIZE", "failed", reason="capability_not_ready")
                    payload["final_status"] = JOB_STATUS_FAILED
                    _save_job(
                        conn,
                        job_id=job_id,
                        skill_id=skill_key,
                        stage="FINALIZE",
                        status=JOB_STATUS_FAILED,
                        started_at=started_at,
                        payload=payload,
                    )
                    return _public_result(
                        job_id=job_id,
                        skill_id=skill_key,
                        stage="FINALIZE",
                        status=JOB_STATUS_FAILED,
                        started_at=started_at,
                        payload=payload,
                    )
        else:
            example_ids = [
                int(r[0] if not hasattr(r, "keys") else r["id"])
                for r in conn.execute(
                    """
                    SELECT id FROM textbook_examples
                    WHERE skill_id = ? AND skill_id NOT LIKE 'outline_%'
                    ORDER BY id ASC
                    """,
                    (skill_key,),
                ).fetchall()
            ]

        # 4) COMPONENT_BUILD
        if not _stage_done(payload, "COMPONENT_BUILD"):
            stage = "COMPONENT_BUILD"
            _mark_stage(payload, stage, "running")
            _save_job(
                conn,
                job_id=job_id,
                skill_id=skill_key,
                stage=stage,
                status=JOB_STATUS_RUNNING,
                started_at=started_at,
                payload=payload,
            )
            operation_mode = "regenerate" if force else (mode or "auto")

            skip_ids = {
                int(item.get("example_id") or 0)
                for item in (payload.get("skip_examples") or [])
                if int(item.get("example_id") or 0)
            }
            coverage_now = get_v3_skill_component_coverage(conn, skill_key)
            for eid in coverage_now.get("intentional_skip_ids") or []:
                skip_ids.add(int(eid))
            eligible_ids = [eid for eid in example_ids if eid not in skip_ids]
            prod_components = _list_production_component_ids(project_root, skill_key)
            eligible_component_ids = _eligible_component_ids(example_ids, skip_ids)
            package_complete = (
                not force
                and operation_mode != "regenerate"
                and bool(eligible_component_ids)
                and eligible_component_ids.issubset(prod_components)
                and (Path(project_root) / "skills" / f"{skill_key}.py").is_file()
            )

            if package_complete:
                dryrun_result = {
                    "success": True,
                    "rebuilt_count": 0,
                    "skipped_count": len(eligible_ids),
                    "intentional_skip_count": len(skip_ids),
                    "failed_count": 0,
                    "user_message": "production_package_reused",
                }
                payload["idempotent"] = True
                payload["dryrun_result"] = dryrun_result
                _mark_stage(payload, stage, "done", reason="production_package_reused")
                for later in ("VALIDATION", "SMOKE_TEST", "PUBLISH"):
                    _mark_stage(payload, later, "done", reason="idempotent_package_ready")
                stage = "FINALIZE"
                _mark_stage(payload, stage, "running")
                payload["counts"].update(
                    {
                        "example_count": len(example_ids),
                        "eligible_count": len(eligible_ids),
                        "published_count": len(eligible_ids),
                        "skip_count": len(skip_ids),
                        "missing_count": 0,
                        "needs_capability_count": 0,
                    }
                )
                payload["allow_v3_rebuild"] = True
                payload["final_status"] = JOB_STATUS_READY
                payload["production_preserved"] = True
                _mark_stage(payload, stage, "done")
                _save_job(
                    conn,
                    job_id=job_id,
                    skill_id=skill_key,
                    stage=stage,
                    status=JOB_STATUS_READY,
                    started_at=started_at,
                    payload=payload,
                )
                return _public_result(
                    job_id=job_id,
                    skill_id=skill_key,
                    stage=stage,
                    status=JOB_STATUS_READY,
                    started_at=started_at,
                    payload=payload,
                )

            dryrun_result = run_admin_v3_dryrun_for_skill(
                conn,
                skill_key,
                smoke=False,
                verify=True,
                force=bool(force),
                mode=operation_mode,
                dryrun_base_dir=dryrun_base_dir,
                seed=seed,
            )
            payload["dryrun_result"] = {
                "success": bool(dryrun_result.get("success")),
                "rebuilt_count": int(dryrun_result.get("rebuilt_count") or 0),
                "skipped_count": int(dryrun_result.get("skipped_count") or 0),
                "intentional_skip_count": int(dryrun_result.get("intentional_skip_count") or 0),
                "failed_count": int(dryrun_result.get("failed_count") or 0),
            }
            if not dryrun_result.get("success"):
                _append_error(
                    payload,
                    stage="COMPONENT_BUILD",
                    code="COMPONENT_BUILD_FAILED",
                    message=str(dryrun_result.get("user_message") or "component_build_failed"),
                )
                _mark_stage(payload, stage, "failed")
                payload["final_status"] = JOB_STATUS_FAILED
                payload["production_preserved"] = True
                _save_job(
                    conn,
                    job_id=job_id,
                    skill_id=skill_key,
                    stage=stage,
                    status=JOB_STATUS_FAILED,
                    started_at=started_at,
                    payload=payload,
                )
                return _public_result(
                    job_id=job_id,
                    skill_id=skill_key,
                    stage=stage,
                    status=JOB_STATUS_FAILED,
                    started_at=started_at,
                    payload=payload,
                )
            _mark_stage(payload, stage, "done")
            _save_job(
                conn,
                job_id=job_id,
                skill_id=skill_key,
                stage=stage,
                status=JOB_STATUS_RUNNING,
                started_at=started_at,
                payload=payload,
            )
        else:
            dryrun_result = dict(payload.get("dryrun_result") or {"rebuilt_count": 0, "success": True})

        rebuilt_count = int(dryrun_result.get("rebuilt_count") or 0)

        # 5) VALIDATION
        if not _stage_done(payload, "VALIDATION"):
            stage = "VALIDATION"
            _mark_stage(payload, stage, "running")
            _save_job(
                conn,
                job_id=job_id,
                skill_id=skill_key,
                stage=stage,
                status=JOB_STATUS_RUNNING,
                started_at=started_at,
                payload=payload,
            )
            coverage = get_v3_skill_component_coverage(conn, skill_key)
            eligibility = evaluate_v3_publish_eligibility(conn, skill_key, coverage=coverage)
            payload["counts"].update(
                {
                    "published_count": int(coverage.get("verified_count") or 0),
                    "skip_count": int(
                        coverage.get("intentional_skip_count")
                        or payload["counts"].get("skip_count")
                        or 0
                    ),
                    "missing_count": int(coverage.get("missing_tracker_count") or 0),
                    "eligible_count": int(
                        coverage.get("eligible_count")
                        or payload["counts"].get("eligible_count")
                        or 0
                    ),
                    "example_count": int(
                        coverage.get("total_examples")
                        or payload["counts"].get("example_count")
                        or 0
                    ),
                }
            )
            # When production package already covers eligible, allow even if tracker missing.
            package_ok = bool(payload.get("idempotent")) and int(
                payload["counts"].get("missing_count") or 0
            ) >= 0
            gate_fail = (not eligibility.get("allowed") and not package_ok) or (
                int(coverage.get("missing_tracker_count") or 0) > 0 and not payload.get("idempotent")
            )
            if gate_fail and not payload.get("idempotent"):
                _append_error(
                    payload,
                    stage="VALIDATION",
                    code="VALIDATION_FAILED",
                    message=str(eligibility.get("reason") or "validation_failed"),
                )
                _mark_stage(payload, stage, "failed")
                payload["final_status"] = JOB_STATUS_FAILED
                payload["production_preserved"] = True
                _save_job(
                    conn,
                    job_id=job_id,
                    skill_id=skill_key,
                    stage=stage,
                    status=JOB_STATUS_FAILED,
                    started_at=started_at,
                    payload=payload,
                )
                return _public_result(
                    job_id=job_id,
                    skill_id=skill_key,
                    stage=stage,
                    status=JOB_STATUS_FAILED,
                    started_at=started_at,
                    payload=payload,
                )
            _mark_stage(payload, stage, "done")
            _save_job(
                conn,
                job_id=job_id,
                skill_id=skill_key,
                stage=stage,
                status=JOB_STATUS_RUNNING,
                started_at=started_at,
                payload=payload,
            )

        # 6) SMOKE_TEST
        if not _stage_done(payload, "SMOKE_TEST"):
            stage = "SMOKE_TEST"
            _mark_stage(payload, stage, "running")
            _save_job(
                conn,
                job_id=job_id,
                skill_id=skill_key,
                stage=stage,
                status=JOB_STATUS_RUNNING,
                started_at=started_at,
                payload=payload,
            )
            if smoke and rebuilt_count > 0:
                smoke_result = run_admin_v3_dryrun_for_skill(
                    conn,
                    skill_key,
                    smoke=True,
                    verify=True,
                    force=False,
                    mode="verify_existing",
                    dryrun_base_dir=dryrun_base_dir,
                    seed=seed,
                )
                if not smoke_result.get("success"):
                    _append_error(
                        payload,
                        stage="SMOKE_TEST",
                        code="SMOKE_FAILED",
                        message=str(smoke_result.get("user_message") or "smoke_failed"),
                    )
                    _mark_stage(payload, stage, "failed")
                    payload["final_status"] = JOB_STATUS_FAILED
                    payload["production_preserved"] = True
                    _save_job(
                        conn,
                        job_id=job_id,
                        skill_id=skill_key,
                        stage=stage,
                        status=JOB_STATUS_FAILED,
                        started_at=started_at,
                        payload=payload,
                    )
                    return _public_result(
                        job_id=job_id,
                        skill_id=skill_key,
                        stage=stage,
                        status=JOB_STATUS_FAILED,
                        started_at=started_at,
                        payload=payload,
                    )
                _mark_stage(payload, stage, "done")
            else:
                _mark_stage(payload, stage, "done", reason="skipped_verified_reuse")
            _save_job(
                conn,
                job_id=job_id,
                skill_id=skill_key,
                stage=stage,
                status=JOB_STATUS_RUNNING,
                started_at=started_at,
                payload=payload,
            )

        # 7) PUBLISH
        if not _stage_done(payload, "PUBLISH"):
            stage = "PUBLISH"
            _mark_stage(payload, stage, "running")
            _save_job(
                conn,
                job_id=job_id,
                skill_id=skill_key,
                stage=stage,
                status=JOB_STATUS_RUNNING,
                started_at=started_at,
                payload=payload,
            )
            coverage = get_v3_skill_component_coverage(conn, skill_key)
            eligibility = evaluate_v3_publish_eligibility(conn, skill_key, coverage=coverage)
            if (
                rebuilt_count == 0
                and (
                    bool(coverage.get("publish_ready"))
                    or bool(payload.get("idempotent"))
                )
                and (bool(eligibility.get("allowed")) or bool(payload.get("idempotent")))
            ):
                payload["idempotent"] = True
                payload["publish_result"] = {
                    "published": True,
                    "reason": "already_published_idempotent",
                }
                _mark_stage(payload, stage, "done", reason="idempotent_skip_publish")
            else:
                try:
                    _prepare_publish_staging_components(
                        skill_id=skill_key,
                        dryrun_base_dir=dryrun_base_dir,
                        staging_root=staging_root,
                    )
                    publish_result = run_admin_v3_publish_for_skill(
                        conn=conn,
                        skill_id=skill_key,
                        project_root=project_root,
                        staging_root=staging_root,
                        force_publish=True,
                        strict_coverage=False,
                    )
                    publish_status = str(publish_result.get("status") or "").strip()
                    publish_ok = bool(
                        publish_result.get("published")
                        or publish_result.get("ok")
                        or publish_result.get("success")
                        or publish_status
                        in {
                            "production_published",
                            "partial_published",
                            "runtime_ready_with_variation_warning",
                        }
                        or publish_result.get("production_smoke_status") == "passed"
                    )
                    payload["publish_result"] = {
                        "published": publish_ok,
                        "status": publish_status,
                        "reason": str(
                            publish_result.get("reason")
                            or publish_status
                            or ""
                        ),
                    }
                    if not publish_ok:
                        raise ValueError(
                            str(
                                publish_result.get("error")
                                or publish_result.get("reason")
                                or publish_status
                                or "publish_failed"
                            )
                        )
                    _mark_stage(payload, stage, "done")
                    payload["production_preserved"] = True
                except Exception as exc:
                    _append_error(
                        payload,
                        stage="PUBLISH",
                        code="PUBLISH_FAILED",
                        message=str(exc),
                    )
                    _mark_stage(payload, stage, "failed", reason=str(exc))
                    payload["final_status"] = JOB_STATUS_FAILED
                    payload["production_preserved"] = True
                    _save_job(
                        conn,
                        job_id=job_id,
                        skill_id=skill_key,
                        stage=stage,
                        status=JOB_STATUS_FAILED,
                        started_at=started_at,
                        payload=payload,
                    )
                    return _public_result(
                        job_id=job_id,
                        skill_id=skill_key,
                        stage=stage,
                        status=JOB_STATUS_FAILED,
                        started_at=started_at,
                        payload=payload,
                    )
            _save_job(
                conn,
                job_id=job_id,
                skill_id=skill_key,
                stage=stage,
                status=JOB_STATUS_RUNNING,
                started_at=started_at,
                payload=payload,
            )

        # 8) FINALIZE
        stage = "FINALIZE"
        _mark_stage(payload, stage, "running")
        coverage = get_v3_skill_component_coverage(conn, skill_key)
        if payload.get("idempotent") and int(payload["counts"].get("published_count") or 0) > 0:
            # Keep package-based counts; tracker may be empty after isolated publish.
            payload["counts"]["needs_capability_count"] = 0
            payload["counts"]["missing_count"] = 0
            if int(payload["counts"].get("eligible_count") or 0) < 1:
                payload["counts"]["eligible_count"] = int(coverage.get("eligible_count") or 0)
            if int(payload["counts"].get("example_count") or 0) < 1:
                payload["counts"]["example_count"] = int(coverage.get("total_examples") or 0)
            if int(payload["counts"].get("skip_count") or 0) < 1:
                payload["counts"]["skip_count"] = int(coverage.get("intentional_skip_count") or 0)
        else:
            payload["counts"].update(
                {
                    "published_count": int(coverage.get("verified_count") or 0),
                    "skip_count": int(coverage.get("intentional_skip_count") or 0),
                    "missing_count": int(coverage.get("missing_tracker_count") or 0),
                    "eligible_count": int(coverage.get("eligible_count") or 0),
                    "example_count": int(coverage.get("total_examples") or 0),
                    "needs_capability_count": 0,
                }
            )
        ready = bool(payload.get("idempotent")) or (
            int(payload["counts"]["missing_count"]) == 0
            and int(payload["counts"]["needs_capability_count"]) == 0
            and int(payload["counts"]["published_count"]) == int(payload["counts"]["eligible_count"])
        )
        if not ready:
            _append_error(
                payload,
                stage="FINALIZE",
                code="NOT_READY",
                message="published_ne_eligible_or_missing",
            )
            _mark_stage(payload, stage, "failed")
            payload["final_status"] = JOB_STATUS_FAILED
            _save_job(
                conn,
                job_id=job_id,
                skill_id=skill_key,
                stage=stage,
                status=JOB_STATUS_FAILED,
                started_at=started_at,
                payload=payload,
            )
            return _public_result(
                job_id=job_id,
                skill_id=skill_key,
                stage=stage,
                status=JOB_STATUS_FAILED,
                started_at=started_at,
                payload=payload,
            )

        _mark_stage(payload, stage, "done")
        payload["allow_v3_rebuild"] = True
        payload["final_status"] = JOB_STATUS_READY
        _save_job(
            conn,
            job_id=job_id,
            skill_id=skill_key,
            stage=stage,
            status=JOB_STATUS_READY,
            started_at=started_at,
            payload=payload,
        )
        return _public_result(
            job_id=job_id,
            skill_id=skill_key,
            stage=stage,
            status=JOB_STATUS_READY,
            started_at=started_at,
            payload=payload,
        )
    except Exception as exc:
        _append_error(payload, stage=stage, code=type(exc).__name__, message=str(exc))
        _mark_stage(payload, stage, "failed", reason=str(exc))
        payload["final_status"] = JOB_STATUS_FAILED
        payload["production_preserved"] = True
        _save_job(
            conn,
            job_id=job_id,
            skill_id=skill_key,
            stage=stage,
            status=JOB_STATUS_FAILED,
            started_at=started_at,
            payload=payload,
        )
        return _public_result(
            job_id=job_id,
            skill_id=skill_key,
            stage=stage,
            status=JOB_STATUS_FAILED,
            started_at=started_at,
            payload=payload,
        )


def start_v3_build_job(
    conn: sqlite3.Connection,
    skill_id: str,
    *,
    project_root: str,
    staging_root: str,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    mode: str = "auto",
    force: bool = False,
    smoke: bool = True,
    resume: bool = True,
    async_mode: bool = True,
    app=None,
    database_uri: str | None = None,
    seed: int | None = 42,
) -> dict[str, Any]:
    """
    Start or resume a V3 build job.

    async_mode=True (default for UI):
      - persist accepted/running job immediately
      - run orchestrator in a daemon thread
      - return HTTP-friendly accepted payload for polling

    async_mode=False:
      - run synchronously (tests / maintenance)
    """
    import threading

    ensure_orchestrator_jobs_table(conn)
    skill_key = str(skill_id or "").strip()
    if not skill_key:
        raise ValueError("missing_skill_id")
    if is_outline_skill_id(skill_key):
        raise ValueError("outline_skill_not_supported_for_v3_build")

    existing = get_orchestrator_job(conn, skill_key)
    if (
        existing
        and str(existing.get("status") or "") == JOB_STATUS_RUNNING
        and not force
    ):
        return {
            "ok": True,
            "accepted": True,
            "already_running": True,
            "async": True,
            "job_id": existing.get("job_id"),
            "skill_id": skill_key,
            "stage": existing.get("stage"),
            "status": JOB_STATUS_RUNNING,
            "final_status": "RUNNING",
            "counts": existing.get("counts") or _empty_counts(),
            "stages": existing.get("stages") or list(_default_stage_map().values()),
            "errors": existing.get("errors") or [],
            "skip_examples": existing.get("skip_examples") or [],
            "needs_capability_examples": existing.get("needs_capability_examples") or [],
            "allow_v3_rebuild": False,
            "production_preserved": True,
            "poll_url_hint": f"/admin/skills/{skill_key}/gencode_v3_build_status",
        }

    if not async_mode:
        result = run_v3_build_orchestrator(
            conn,
            skill_key,
            project_root=project_root,
            staging_root=staging_root,
            dryrun_base_dir=dryrun_base_dir,
            mode=mode,
            force=force,
            smoke=smoke,
            resume=resume,
            seed=seed,
        )
        result["accepted"] = True
        result["async"] = False
        return result

    # Seed durable job row before returning so status polls always see something.
    previous = _load_job_row(conn, skill_key) if resume and not force else None
    if (
        previous
        and str(previous.get("status") or "") in {JOB_STATUS_FAILED, JOB_STATUS_RUNNING, JOB_STATUS_ACCEPTED}
        and not force
    ):
        job_id = str(previous.get("job_id") or uuid.uuid4().hex)
        started_at = str(previous.get("started_at") or _now_iso())
        payload = dict(previous.get("payload") or _new_payload(skill_key))
        stage = str(previous.get("stage") or "LOAD_EXAMPLES")
    else:
        job_id = uuid.uuid4().hex
        started_at = _now_iso()
        payload = _new_payload(skill_key)
        stage = "LOAD_EXAMPLES"
    _mark_stage(payload, stage, "running")
    _save_job(
        conn,
        job_id=job_id,
        skill_id=skill_key,
        stage=stage,
        status=JOB_STATUS_RUNNING,
        started_at=started_at,
        payload=payload,
    )

    def _worker() -> None:
        worker_conn: sqlite3.Connection | None = None
        try:
            if app is not None:
                with app.app_context():
                    from models import db as _db

                    worker_conn = _db.engine.raw_connection()
                    run_v3_build_orchestrator(
                        worker_conn,
                        skill_key,
                        project_root=project_root,
                        staging_root=staging_root,
                        dryrun_base_dir=dryrun_base_dir,
                        mode=mode,
                        force=force,
                        smoke=smoke,
                        resume=True,
                        job_id=job_id,
                        seed=seed,
                    )
            else:
                uri = str(database_uri or "").strip()
                if uri.startswith("sqlite:///"):
                    path = uri[len("sqlite:///") :]
                    worker_conn = sqlite3.connect(path)
                else:
                    worker_conn = sqlite3.connect(uri or ":memory:")
                worker_conn.row_factory = sqlite3.Row
                run_v3_build_orchestrator(
                    worker_conn,
                    skill_key,
                    project_root=project_root,
                    staging_root=staging_root,
                    dryrun_base_dir=dryrun_base_dir,
                    mode=mode,
                    force=force,
                    smoke=smoke,
                    resume=True,
                    job_id=job_id,
                    seed=seed,
                )
        except Exception as exc:  # pragma: no cover - defensive
            try:
                if worker_conn is None:
                    return
                ensure_orchestrator_jobs_table(worker_conn)
                fail_payload = dict(payload)
                _append_error(
                    fail_payload,
                    stage=stage,
                    code=type(exc).__name__,
                    message=str(exc),
                )
                _mark_stage(fail_payload, stage, "failed", reason=str(exc))
                fail_payload["final_status"] = JOB_STATUS_FAILED
                fail_payload["production_preserved"] = True
                _save_job(
                    worker_conn,
                    job_id=job_id,
                    skill_id=skill_key,
                    stage=stage,
                    status=JOB_STATUS_FAILED,
                    started_at=started_at,
                    payload=fail_payload,
                )
            except Exception:
                pass
        finally:
            if worker_conn is not None:
                try:
                    worker_conn.close()
                except Exception:
                    pass

    threading.Thread(target=_worker, name=f"v3-build-{skill_key}", daemon=True).start()

    return {
        "ok": True,
        "accepted": True,
        "already_running": False,
        "async": True,
        "job_id": job_id,
        "skill_id": skill_key,
        "stage": stage,
        "status": JOB_STATUS_RUNNING,
        "final_status": "RUNNING",
        "started_at": started_at,
        "updated_at": _now_iso(),
        "counts": payload.get("counts") or _empty_counts(),
        "stages": [
            {
                "name": name,
                "label": STAGE_LABELS[name],
                **(payload.get("stages") or {}).get(name, {}),
            }
            for name in STAGES
        ],
        "errors": [],
        "skip_examples": [],
        "needs_capability_examples": [],
        "allow_v3_rebuild": False,
        "production_preserved": True,
        "poll_url_hint": f"/admin/skills/{skill_key}/gencode_v3_build_status",
        "ui_status": "建置中",
    }
