# -*- coding: utf-8 -*-
"""Append-only telemetry for the GenCode V3 component code healer.

Every metric shown on the teacher dashboard or exported to CSV is computed by
``compute_healer_metrics`` from the raw rows of
``gencode_v3_healer_telemetry_events``; nothing is stored pre-aggregated.

Rescue unit: (generation_run_id, skill_id, component_id).  Retries, resumes and
multi-round / multi-tier repairs inside one unit count as at most one rescue.
Telemetry writes never raise into the pipeline; failures are logged and kept
on ``V3HealerResult.telemetry["errors"]``.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import os
import re
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Iterable, Mapping

from core.gencode.research_healer.eligibility import (
    ELIGIBILITY_BY_ID,
    RULE_ELIGIBILITY,
    STATUS_ENABLED,
    TIER_PREFLIGHT,
    TIER_RESEARCH_L1,
    TIER_RESEARCH_L2,
)
from core.gencode.schema.gencode_v3_healer_telemetry_inspection import (
    TABLE_NAME,
    healer_telemetry_table_exists,
    load_healer_telemetry_ddl,
)

logger = logging.getLogger(__name__)

TELEMETRY_VERSION = "v3.healer.telemetry.2"
ENVIRONMENT_ENV = "GENCODE_V3_HEALER_ENVIRONMENT"
DATA_ORIGIN_ENV = "GENCODE_V3_HEALER_DATA_ORIGIN"
ENVIRONMENTS = ("production", "staging", "test")
DATA_ORIGINS = ("real_world", "synthetic")
MODES = ("shadow", "repair")
RANGE_DAYS: dict[str, int | None] = {"all": None, "30d": 30, "7d": 7}
TIER_ORDER = (TIER_PREFLIGHT, TIER_RESEARCH_L1, TIER_RESEARCH_L2)
RULE_STATUS_ACTIVE = "ACTIVE"
RULE_STATUS_DISABLED = "DISABLED / NOT ELIGIBLE"
RULE_STATUS_RETIRED = "RETIRED FROM V3"
RECENT_LIMIT = 50

_COLUMNS = (
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
    "eligible",
    "rule_seq",
    "round_index",
    "tier",
    "rule_id",
    "repair_chain",
    "outcome",
    "reason_code",
    "applied_to_pipeline",
    "original_sha256",
    "repaired_sha256",
    "certificate_status",
    "evidence_path",
    "gate_stage",
    "created_at",
    "finished_at",
    "source_version",
)
_SAFE_TOKEN_RE = re.compile(r"[^A-Za-z0-9_.\-]")


# ---------------------------------------------------------------------------
# Context / identity
# ---------------------------------------------------------------------------


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def resolve_telemetry_context(
    env: Mapping[str, str] | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    """environment: production/staging/test; data_origin: real_world/synthetic."""
    source = os.environ if env is None else env
    extra = dict(overrides or {})
    environment = str(extra.get("environment") or source.get(ENVIRONMENT_ENV) or "").strip().lower()
    if environment not in ENVIRONMENTS:
        environment = "test" if source.get("PYTEST_CURRENT_TEST") else "production"
    origin = str(extra.get("data_origin") or source.get(DATA_ORIGIN_ENV) or "").strip().lower()
    if origin not in DATA_ORIGINS:
        origin = "synthetic" if environment == "test" else "real_world"
    return {"environment": environment, "data_origin": origin}


def formal_tier(rule_id: str, research_tier: str | None = None) -> str:
    rule_key = str(rule_id or "")
    if rule_key.startswith("PC-R0"):
        return rule_key[:6]
    meta = ELIGIBILITY_BY_ID.get(rule_key)
    return str(research_tier or (meta.tier if meta else "") or "unknown")


def _catalog_status(rule_id: str) -> str:
    meta = ELIGIBILITY_BY_ID.get(rule_id)
    if meta is None:
        return RULE_STATUS_RETIRED
    return RULE_STATUS_ACTIVE if meta.v3_status == STATUS_ENABLED else RULE_STATUS_DISABLED


def compute_attempt_id(
    *,
    generation_run_id: str,
    skill_id: str,
    component_id: str,
    mode: str,
    original_sha256: str,
) -> str:
    raw = "|".join([generation_run_id, skill_id, component_id, mode, original_sha256])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def reason_code(reason: Any) -> str:
    """Reduce a free-text reason to at most two sanitized tokens (no payload values)."""
    parts = str(reason or "").split(":")
    head = _SAFE_TOKEN_RE.sub("", parts[0])[:80]
    if len(parts) > 1:
        tail = _SAFE_TOKEN_RE.sub("", parts[1])[:60]
        if tail:
            return f"{head}:{tail}"
    return head


def _source_version(result: Any) -> str:
    return "|".join(
        [
            str(getattr(result, "adapter_version", "")),
            str(getattr(result, "ruleset_version", "")),
            str(getattr(result, "research_commit", ""))[:12],
            TELEMETRY_VERSION,
        ]
    )


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


def _in_transaction(conn: Any) -> bool:
    try:
        return bool(conn.in_transaction)
    except Exception:
        driver = getattr(conn, "driver_connection", None) or getattr(conn, "dbapi_connection", None)
        return bool(getattr(driver, "in_transaction", False))


def _ddl_statements() -> list[str]:
    statements: list[str] = []
    buffer = ""
    for line in load_healer_telemetry_ddl().splitlines(keepends=True):
        if line.lstrip().startswith("--") and not buffer.strip():
            continue
        buffer += line
        if sqlite3.complete_statement(buffer):
            statements.append(buffer.strip())
            buffer = ""
    return [s for s in statements if s]


def _ensure_table(conn: Any) -> None:
    if healer_telemetry_table_exists(conn):
        return
    for statement in _ddl_statements():
        conn.execute(statement)


def _insert_events(conn: Any, rows: list[dict[str, Any]]) -> int:
    """Insert rows atomically; only an event_key conflict is ignored, other constraint errors raise."""
    if not rows:
        return 0
    sql = (
        f"INSERT INTO {TABLE_NAME} ({', '.join(_COLUMNS)}) "
        f"VALUES ({', '.join('?' for _ in _COLUMNS)}) "
        "ON CONFLICT(event_key) DO NOTHING"
    )
    defaults = {"eligible": 0, "applied_to_pipeline": 0, "repair_chain": "[]"}
    values = [
        tuple(defaults.get(col) if row.get(col) is None and col in defaults else row.get(col) for col in _COLUMNS)
        for row in rows
    ]
    if _in_transaction(conn):
        conn.execute("SAVEPOINT v3_healer_telemetry")
        try:
            _ensure_table(conn)
            inserted = sum(max(conn.execute(sql, v).rowcount, 0) for v in values)
        except Exception:
            conn.execute("ROLLBACK TO v3_healer_telemetry")
            conn.execute("RELEASE v3_healer_telemetry")
            raise
        conn.execute("RELEASE v3_healer_telemetry")
        return inserted
    try:
        _ensure_table(conn)
        inserted = sum(max(conn.execute(sql, v).rowcount, 0) for v in values)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return inserted


def _certificate_status(result: Any) -> str:
    own = getattr(result, "certificate_status", None)
    if isinstance(own, str) and own:
        return own
    from core.gencode.v3_healer_adapter import verify_certificate

    certificates = list(getattr(result, "certificates", None) or [])
    if not certificates:
        return "none"
    return "verified" if all(not verify_certificate(c) for c in certificates) else "failed"


def _repair_chain(result: Any) -> list[dict[str, str]]:
    return [
        {"rule_id": str(r.get("rule_id")), "tier": formal_tier(str(r.get("rule_id")), r.get("research_tier"))}
        for r in (getattr(result, "rules_applied", None) or [])
    ]


def _rule_decision(attempt: Mapping[str, Any]) -> str:
    text = str(attempt.get("reason") or "")
    if text.startswith("rule_disabled_in_v3"):
        return "DISABLED"
    if text == "unknown_rule":
        return "UNKNOWN"
    return str(attempt.get("decision") or "ABSTAIN")


def record_healer_attempt(
    conn: Any,
    result: Any,
    *,
    generation_run_id: str,
    context: Mapping[str, Any] | None = None,
    started_at: str | None = None,
    finished_at: str | None = None,
) -> dict[str, Any]:
    run_id = str(generation_run_id or "").strip()
    if not run_id:
        raise ValueError("generation_run_id_required")
    ctx = resolve_telemetry_context(overrides=context)
    attempt_id = compute_attempt_id(
        generation_run_id=run_id,
        skill_id=str(result.skill_id),
        component_id=str(result.component_id),
        mode=str(result.mode),
        original_sha256=str(result.original_sha256),
    )
    chain = _repair_chain(result)
    chain_tiers = list(dict.fromkeys(item["tier"] for item in chain))
    finished = finished_at or now_iso()
    base = {
        "attempt_id": attempt_id,
        "generation_run_id": run_id,
        "component_id": str(result.component_id),
        "textbook_example_id": (
            int(result.textbook_example_id) if getattr(result, "textbook_example_id", None) is not None else None
        ),
        "skill_id": str(result.skill_id),
        "mode": str(result.mode),
        "environment": ctx["environment"],
        "data_origin": ctx["data_origin"],
        "failure_category": str(result.failure_category or ""),
        "eligible": 1 if int(getattr(result, "rounds", 0) or 0) >= 1 else 0,
        "repair_chain": json.dumps(chain, ensure_ascii=False),
        "original_sha256": str(result.original_sha256),
        "repaired_sha256": result.repaired_sha256,
        "created_at": started_at or finished,
        "finished_at": finished,
        "source_version": _source_version(result),
    }
    rows = [
        {
            **base,
            "event_key": f"attempt:{attempt_id}",
            "event_type": "attempt",
            "tier": "+".join(chain_tiers) or None,
            "outcome": str(result.status),
            "reason_code": reason_code(result.reason),
            "applied_to_pipeline": 1 if result.applied_to_pipeline else 0,
            "certificate_status": _certificate_status(result),
            "evidence_path": result.evidence_path,
        }
    ]
    for seq, attempt in enumerate(getattr(result, "attempts", None) or []):
        rule_id = str(attempt.get("rule_id") or "")
        rows.append(
            {
                **base,
                "event_key": f"rule:{attempt_id}:{seq}",
                "event_type": "rule",
                "rule_seq": seq,
                "round_index": int(attempt.get("round") or 0),
                "tier": formal_tier(rule_id, attempt.get("research_tier")),
                "rule_id": rule_id,
                "outcome": _rule_decision(attempt),
                "reason_code": reason_code(attempt.get("reason") or attempt.get("guard") or attempt.get("rule_reason")),
            }
        )
    inserted = _insert_events(conn, rows)
    return {
        "attempt_id": attempt_id,
        "generation_run_id": run_id,
        "environment": ctx["environment"],
        "data_origin": ctx["data_origin"],
        "status": "recorded" if inserted else "duplicate",
        "inserted_events": inserted,
    }


def _fetch_attempt_row(conn: Any, attempt_id: str) -> dict[str, Any] | None:
    if not healer_telemetry_table_exists(conn):
        return None
    cursor = conn.execute(
        f"SELECT {', '.join(_COLUMNS)} FROM {TABLE_NAME} WHERE event_key = ?",
        (f"attempt:{attempt_id}",),
    )
    row = cursor.fetchone()
    return dict(zip(_COLUMNS, row)) if row is not None else None


def record_post_repair_gate(conn: Any, result: Any, *, passed: bool, stage: str | None = None) -> dict[str, Any]:
    attempt_id = str((getattr(result, "telemetry", None) or {}).get("attempt_id") or "")
    if not attempt_id:
        return {"status": "skipped:no_attempt_event"}
    attempt = _fetch_attempt_row(conn, attempt_id)
    if attempt is None:
        return {"status": "skipped:no_attempt_event"}
    row = {
        **attempt,
        "event_key": f"gate:{attempt_id}",
        "event_type": "gate",
        "outcome": "passed" if passed else "failed",
        "gate_stage": None if passed else str(stage or "unknown")[:80],
        "reason_code": None,
        "evidence_path": None,
        "created_at": now_iso(),
        "finished_at": now_iso(),
    }
    inserted = _insert_events(conn, [row])
    return {"status": "recorded" if inserted else "duplicate"}


def _note_error(result: Any, stage: str, exc: BaseException) -> None:
    message = f"{stage}:{type(exc).__name__}:{str(exc)[:200]}"
    logger.warning("v3 healer telemetry write failed: %s", message)
    telemetry = getattr(result, "telemetry", None)
    if isinstance(telemetry, dict):
        telemetry.setdefault("errors", []).append(message)


def record_attempt_safely(conn: Any, result: Any, **kwargs: Any) -> None:
    try:
        info = record_healer_attempt(conn, result, **kwargs)
        result.telemetry.update(info)
    except Exception as exc:  # noqa: BLE001 - telemetry must never change pipeline behaviour
        result.telemetry["status"] = "failed"
        _note_error(result, "attempt", exc)


def record_gate_safely(conn: Any, result: Any, *, passed: bool, stage: str | None = None) -> None:
    if conn is None:
        return
    try:
        info = record_post_repair_gate(conn, result, passed=passed, stage=stage)
        result.telemetry["gate_status"] = info.get("status")
    except Exception as exc:  # noqa: BLE001
        result.telemetry["gate_status"] = "failed"
        _note_error(result, "gate", exc)


def record_published_rescues(
    conn: Any,
    *,
    skill_id: str,
    components: Iterable[Mapping[str, Any]],
    publish_status: str,
) -> dict[str, Any]:
    """Publish events only for human-approved repairs with recorded attempt + passed gate evidence."""
    rows: list[dict[str, Any]] = []
    skipped: list[str] = []
    if not healer_telemetry_table_exists(conn):
        return {"inserted": 0, "skipped": ["no_telemetry_table"]}
    for component in components:
        spec = component.get("induced_spec_payload")
        if isinstance(spec, str):
            try:
                spec = json.loads(spec)
            except Exception:
                spec = None
        if not isinstance(spec, dict):
            continue
        healer = spec.get("v3_healer")
        if not isinstance(healer, dict) or healer.get("status") != "REPAIRED":
            continue
        component_id = str(component.get("component_id") or healer.get("component_id") or "")
        if spec.get("v3_healer_human_approved") is not True:
            skipped.append(f"{component_id}:not_human_approved")
            continue
        attempt_id = str((healer.get("telemetry") or {}).get("attempt_id") or "")
        attempt = _fetch_attempt_row(conn, attempt_id) if attempt_id else None
        gate = conn.execute(
            f"SELECT outcome FROM {TABLE_NAME} WHERE event_key = ?",
            (f"gate:{attempt_id}",),
        ).fetchone()
        if attempt is None or gate is None or gate[0] != "passed":
            skipped.append(f"{component_id}:no_event_evidence")
            continue
        rows.append(
            {
                **attempt,
                "event_key": f"publish:{attempt_id}",
                "event_type": "publish",
                "outcome": "published",
                "reason_code": reason_code(publish_status),
                "evidence_path": None,
                "created_at": now_iso(),
                "finished_at": now_iso(),
            }
        )
    return {"inserted": _insert_events(conn, rows), "skipped": skipped, "skill_id": skill_id}


# ---------------------------------------------------------------------------
# Query / metrics (pure recomputation from raw events)
# ---------------------------------------------------------------------------


def normalize_filters(
    *,
    range_key: str | None = None,
    mode: str | None = None,
    environment: str | None = None,
    data_origin: str | None = None,
    **alias: Any,
) -> dict[str, str | None]:
    """Accepts its own output (``range``) so normalized filters can be passed through."""
    unknown = set(alias) - {"range"}
    if unknown:
        raise TypeError(f"unknown telemetry filters: {sorted(unknown)}")

    def _pick(value: str | None, allowed: tuple[str, ...]) -> str | None:
        text = str(value or "").strip().lower()
        return text if text in allowed else None

    key = str(range_key or alias.get("range") or "all").strip().lower()
    return {
        "range": key if key in RANGE_DAYS else "all",
        "mode": _pick(mode, MODES),
        "environment": _pick(environment, ENVIRONMENTS),
        "data_origin": _pick(data_origin, DATA_ORIGINS),
    }


def load_events(conn: Any, *, now: datetime | None = None, **filters: Any) -> list[dict[str, Any]]:
    """All events of the attempts matching the filters; read-only (never creates the table)."""
    if not healer_telemetry_table_exists(conn):
        return []
    f = normalize_filters(**filters)
    clauses = ["event_type = 'attempt'"]
    params: list[Any] = []
    days = RANGE_DAYS[f["range"]]
    if days is not None:
        clauses.append("created_at >= ?")
        params.append(((now or datetime.now()) - timedelta(days=days)).isoformat(timespec="seconds"))
    for column in ("mode", "environment", "data_origin"):
        if f[column]:
            clauses.append(f"{column} = ?")
            params.append(f[column])
    sql = (
        f"SELECT {', '.join(_COLUMNS)} FROM {TABLE_NAME} WHERE attempt_id IN "
        f"(SELECT attempt_id FROM {TABLE_NAME} WHERE {' AND '.join(clauses)}) "
        "ORDER BY created_at, attempt_id, event_type, rule_seq"
    )
    return [dict(zip(_COLUMNS, row)) for row in conn.execute(sql, params).fetchall()]


def _unit(event: Mapping[str, Any]) -> tuple[str, str, str]:
    return (str(event["generation_run_id"]), str(event["skill_id"]), str(event["component_id"]))


def _rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def _chain_tiers(event: Mapping[str, Any]) -> list[str]:
    try:
        chain = json.loads(event.get("repair_chain") or "[]")
    except Exception:
        chain = []
    return list(dict.fromkeys(str(item.get("tier")) for item in chain if isinstance(item, dict)))


def _chain_rules(event: Mapping[str, Any]) -> list[str]:
    try:
        chain = json.loads(event.get("repair_chain") or "[]")
    except Exception:
        chain = []
    return [str(item.get("rule_id")) for item in chain if isinstance(item, dict)]


def _counter() -> dict[str, int]:
    return {
        "triggered": 0,
        "applied": 0,
        "modified": 0,
        "rejected": 0,
        "abstained": 0,
        "disabled_skips": 0,
        "verified_rescues_sole": 0,
        "verified_rescues_contributing": 0,
        "still_failed_contributing": 0,
    }


def _classify(events: list[dict[str, Any]]) -> dict[str, Any]:
    attempts = {e["attempt_id"]: e for e in events if e["event_type"] == "attempt"}
    gates = {e["attempt_id"]: e for e in events if e["event_type"] == "gate" and e["attempt_id"] in attempts}
    published_ids = {e["attempt_id"] for e in events if e["event_type"] == "publish" and e["attempt_id"] in attempts}
    rules = [e for e in events if e["event_type"] == "rule" and e["attempt_id"] in attempts]

    ordered = sorted(attempts.values(), key=lambda a: (str(a["created_at"]), a["attempt_id"]))
    verified_rep: dict[tuple[str, str, str], dict[str, Any]] = {}
    still_failed_rep: dict[tuple[str, str, str], dict[str, Any]] = {}
    shadow_rep: dict[tuple[str, str, str], dict[str, Any]] = {}
    pending: set[tuple[str, str, str]] = set()
    for a in ordered:
        if a["outcome"] != "REPAIRED":
            continue
        unit = _unit(a)
        if a["mode"] == "shadow":
            shadow_rep.setdefault(unit, a)
            continue
        gate = gates.get(a["attempt_id"])
        if gate is not None and gate["outcome"] == "passed":
            verified_rep.setdefault(unit, a)
        elif gate is not None:
            still_failed_rep.setdefault(unit, a)
        elif a["applied_to_pipeline"]:
            pending.add(unit)
    for unit in verified_rep:
        still_failed_rep.pop(unit, None)
        pending.discard(unit)
    pending -= set(still_failed_rep)
    published_units = {unit for unit, a in verified_rep.items() if a["attempt_id"] in published_ids}
    return {
        "attempts": attempts,
        "ordered": ordered,
        "gates": gates,
        "published_ids": published_ids,
        "rules": rules,
        "verified_rep": verified_rep,
        "still_failed_rep": still_failed_rep,
        "shadow_rep": shadow_rep,
        "pending": pending,
        "published_units": published_units,
    }


def compute_healer_metrics(events: list[dict[str, Any]]) -> dict[str, Any]:
    c = _classify(events)
    attempts = list(c["attempts"].values())
    outcomes = {s: sum(1 for a in attempts if a["outcome"] == s) for s in ("UNCHANGED", "REPAIRED", "ABSTAINED", "REJECTED")}
    eligible = sum(1 for a in attempts if a["eligible"])
    repair_eligible = sum(1 for a in attempts if a["eligible"] and a["mode"] == "repair")
    shadow_eligible = sum(1 for a in attempts if a["eligible"] and a["mode"] == "shadow")
    verified = len(c["verified_rep"])
    still_failed = len(c["still_failed_rep"])

    chains: dict[str, int] = {}
    for a in c["verified_rep"].values():
        key = " + ".join(_chain_tiers(a)) or "(none)"
        chains[key] = chains.get(key, 0) + 1
    multi_tier = sum(1 for a in c["verified_rep"].values() if len(_chain_tiers(a)) > 1)

    tier_stats = {tier: _counter() for tier in TIER_ORDER}
    rule_stats: dict[str, dict[str, Any]] = {}
    for meta in RULE_ELIGIBILITY:
        rule_stats[meta.rule_id] = {
            "rule_id": meta.rule_id,
            "tier": meta.tier,
            "status": _catalog_status(meta.rule_id),
            **_counter(),
        }
    for e in c["rules"]:
        rule_id = str(e["rule_id"] or "")
        tier = str(e["tier"] or formal_tier(rule_id))
        stats = rule_stats.setdefault(
            rule_id, {"rule_id": rule_id, "tier": tier, "status": _catalog_status(rule_id), **_counter()}
        )
        tstats = tier_stats.setdefault(tier, _counter())
        decision = str(e["outcome"])
        keys: list[str] = []
        if decision in ("ACCEPT", "REJECT", "ABSTAIN"):
            keys.append("triggered")
        if decision in ("ACCEPT", "REJECT"):
            keys.append("applied")
        keys.append(
            {"ACCEPT": "modified", "REJECT": "rejected", "ABSTAIN": "abstained", "DISABLED": "disabled_skips"}.get(
                decision, "abstained"
            )
        )
        for key in keys:
            stats[key] += 1
            tstats[key] += 1
    for bucket, field_name in ((c["verified_rep"], "verified_rescues_contributing"), (c["still_failed_rep"], "still_failed_contributing")):
        for a in bucket.values():
            tiers = _chain_tiers(a)
            for tier in tiers:
                tier_stats.setdefault(tier, _counter())[field_name] += 1
            if field_name == "verified_rescues_contributing" and len(tiers) == 1:
                tier_stats[tiers[0]]["verified_rescues_sole"] += 1
            for rule_id in dict.fromkeys(_chain_rules(a)):
                if rule_id in rule_stats:
                    rule_stats[rule_id][field_name] += 1

    executable_tiers = {m.tier for m in RULE_ELIGIBILITY if m.v3_status == STATUS_ENABLED}

    def _tier_status(tier: str) -> str:
        if tier in executable_tiers:
            return RULE_STATUS_ACTIVE
        return RULE_STATUS_DISABLED if tier in TIER_ORDER else RULE_STATUS_RETIRED

    tiers_out = [{"tier": tier, "status": _tier_status(tier), **stats} for tier, stats in tier_stats.items()]

    recent = []
    for a in sorted(attempts, key=lambda a: (str(a["created_at"]), a["attempt_id"]), reverse=True)[:RECENT_LIMIT]:
        gate = c["gates"].get(a["attempt_id"])
        recent.append(
            {
                "attempt_id": a["attempt_id"],
                "created_at": a["created_at"],
                "generation_run_id": a["generation_run_id"],
                "skill_id": a["skill_id"],
                "component_id": a["component_id"],
                "mode": a["mode"],
                "environment": a["environment"],
                "data_origin": a["data_origin"],
                "failure_category": a["failure_category"],
                "outcome": a["outcome"],
                "reason_code": a["reason_code"],
                "repair_chain": _chain_rules(a),
                "tiers": _chain_tiers(a),
                "original_sha256": a["original_sha256"],
                "repaired_sha256": a["repaired_sha256"],
                "certificate_status": a["certificate_status"],
                "final_gate": (gate["outcome"] if gate else ("pending" if a["applied_to_pipeline"] else "not_applicable")),
                "gate_stage": gate["gate_stage"] if gate else None,
                "published": a["attempt_id"] in c["published_ids"],
            }
        )

    return {
        "totals": {
            "invocations": len(attempts),
            "eligible_attempts": eligible,
            "repair_eligible_attempts": repair_eligible,
            "shadow_eligible_attempts": shadow_eligible,
            "unchanged": outcomes["UNCHANGED"],
            "repaired_outcomes": outcomes["REPAIRED"],
            "abstained": outcomes["ABSTAINED"],
            "rejected": outcomes["REJECTED"],
            "shadow_candidates": len(c["shadow_rep"]),
            "verified_rescues": verified,
            "multi_tier_verified_rescues": multi_tier,
            "published_rescues": len(c["published_units"]),
            "still_failed": still_failed,
            "gate_pending": len(c["pending"]),
            "verified_rescue_rate": _rate(verified, repair_eligible),
            "shadow_candidate_rate": _rate(len(c["shadow_rep"]), shadow_eligible),
            "abstain_rate": _rate(outcomes["ABSTAINED"], len(attempts)),
            "post_repair_regression_rate": _rate(still_failed, verified + still_failed),
        },
        "chains": [{"chain": k, "verified_rescues": v} for k, v in sorted(chains.items())],
        "tiers": tiers_out,
        "rules": list(rule_stats.values()),
        "recent": recent,
    }


def build_dashboard_payload(conn: Any, *, now: datetime | None = None, **filters: Any) -> dict[str, Any]:
    normalized = normalize_filters(**filters)
    events = load_events(conn, now=now, **normalized)
    return {
        "filters": normalized,
        "table_present": healer_telemetry_table_exists(conn),
        "event_count": len(events),
        "telemetry_version": TELEMETRY_VERSION,
        "healer_config": active_healer_config(),
        "metrics": compute_healer_metrics(events),
    }


def active_healer_config() -> dict[str, Any]:
    from core.gencode.research_healer.adapter import ADAPTER_VERSION, resolve_healer_mode
    from core.gencode.research_healer.eligibility import V3_PRODUCTION_ALLOWLIST

    return {
        "mode": resolve_healer_mode(),
        "adapter_version": ADAPTER_VERSION,
        "enabled_rules": [m.rule_id for m in RULE_ELIGIBILITY if m.v3_status == STATUS_ENABLED],
        "v3_production_allowlist": list(V3_PRODUCTION_ALLOWLIST),
    }


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

SUMMARY_COLUMNS = (
    "period_day",
    "environment",
    "data_origin",
    "mode",
    "failure_category",
    "tier",
    "rule_id",
    "invocations",
    "eligible_attempts",
    "triggered",
    "applied",
    "modified",
    "rejected",
    "abstained",
    "shadow_candidates",
    "verified_rescues",
    "still_failed",
    "published_rescues",
    "trigger_rate",
    "repair_attempt_rate",
    "verified_rescue_rate",
    "abstain_ratio",
    "post_repair_regression_rate",
)


def _csv_text(header: Iterable[str], rows: Iterable[Iterable[Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(list(header))
    for row in rows:
        writer.writerow(["" if v is None else v for v in row])
    return buffer.getvalue()


def export_events_csv(events: list[dict[str, Any]]) -> str:
    return _csv_text(_COLUMNS, ([e.get(col) for col in _COLUMNS] for e in events))


def export_summary_csv(events: list[dict[str, Any]]) -> str:
    """One __ALL__ row per (day, environment, origin, mode, failure_category) plus one row per rule."""
    c = _classify(events)
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for a in c["attempts"].values():
        key = (str(a["created_at"])[:10], a["environment"], a["data_origin"], a["mode"], a["failure_category"] or "")
        groups.setdefault(key, []).append(a)
    rules_by_attempt: dict[str, list[dict[str, Any]]] = {}
    for e in c["rules"]:
        rules_by_attempt.setdefault(e["attempt_id"], []).append(e)

    out: list[list[Any]] = []
    for key in sorted(groups):
        members = groups[key]
        ids = {a["attempt_id"] for a in members}
        units = {_unit(a) for a in members}
        eligible = sum(1 for a in members if a["eligible"])
        patched = sum(1 for a in members if a["repair_chain"] not in (None, "", "[]"))
        abstained = sum(1 for a in members if a["outcome"] == "ABSTAINED")
        rejected = sum(1 for a in members if a["outcome"] == "REJECTED")
        verified = sum(1 for u in units if u in c["verified_rep"] and c["verified_rep"][u]["attempt_id"] in ids)
        still = sum(1 for u in units if u in c["still_failed_rep"] and c["still_failed_rep"][u]["attempt_id"] in ids)
        shadow = sum(1 for u in units if u in c["shadow_rep"] and c["shadow_rep"][u]["attempt_id"] in ids)
        published = sum(1 for u in units if u in c["published_units"] and c["verified_rep"][u]["attempt_id"] in ids)
        repair_eligible = sum(1 for a in members if a["eligible"] and a["mode"] == "repair")
        out.append(
            [*key, "__ALL__", "__ALL__", len(members), eligible, eligible, patched, patched, rejected, abstained,
             shadow, verified, still, published, _rate(eligible, len(members)), _rate(patched, len(members)),
             _rate(verified, repair_eligible), _rate(abstained, len(members)), _rate(still, verified + still)]
        )
        per_rule: dict[tuple[str, str], dict[str, int]] = {}
        for attempt_id in sorted(ids):
            for e in rules_by_attempt.get(attempt_id, []):
                stats = per_rule.setdefault((str(e["tier"]), str(e["rule_id"])), {k: 0 for k in ("triggered", "applied", "modified", "rejected", "abstained")})
                decision = e["outcome"]
                if decision in ("ACCEPT", "REJECT", "ABSTAIN"):
                    stats["triggered"] += 1
                if decision in ("ACCEPT", "REJECT"):
                    stats["applied"] += 1
                stats[{"ACCEPT": "modified", "REJECT": "rejected"}.get(decision, "abstained")] += 1 if decision != "DISABLED" else 0
        for (tier, rule_id), stats in sorted(per_rule.items()):
            with_rule_verified = sum(
                1 for u, a in c["verified_rep"].items() if a["attempt_id"] in ids and rule_id in _chain_rules(a)
            )
            with_rule_still = sum(
                1 for u, a in c["still_failed_rep"].items() if a["attempt_id"] in ids and rule_id in _chain_rules(a)
            )
            out.append(
                [*key, tier, rule_id, len(members), eligible, stats["triggered"], stats["applied"], stats["modified"],
                 stats["rejected"], stats["abstained"], "", with_rule_verified, with_rule_still, "",
                 _rate(stats["triggered"], eligible), _rate(stats["applied"], eligible),
                 _rate(with_rule_verified, stats["triggered"]), _rate(stats["abstained"], stats["triggered"]),
                 _rate(with_rule_still, with_rule_verified + with_rule_still)]
            )
    return _csv_text(SUMMARY_COLUMNS, out)
