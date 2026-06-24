"""Single eligibility policy for Gencode V3 formal publish."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from core.gencode.services.v3_skill_coverage_service import get_v3_skill_component_coverage
from core.gencode.skill_fixed_domain_authority import (
    SkillFixedDomainError,
    resolve_fixed_domain_context,
)
from core.gencode.v3_error_codes import DOMAIN_BINDING_MISSING

# Module-level reference — allows tests to monkeypatch
# 'core.gencode.services.v3_publish_eligibility._load_v3_taxonomy_mvp_scope'
from core.gencode.pipeline_orchestrator import _load_v3_taxonomy_mvp_scope

# Sentinel: the original (un-patched) function captured at import time.
# Used at call time to detect which patch target (local module or orchestrator)
# has been replaced by a test monkeypatch.
_ORIGINAL_LOAD_FN = _load_v3_taxonomy_mvp_scope

DEFAULT_TAXONOMY_PATH = "configs/gencode_taxonomy/k12_component_taxonomy.yaml"


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _count_rows(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> int:
    row = conn.execute(sql, params).fetchone()
    if row is None:
        return 0
    return int(row[0] if not hasattr(row, "keys") else row[0])


def _normalize_coverage(coverage: dict[str, object]) -> dict[str, object]:
    total = int(coverage.get("total_examples") or 0)
    verified = int(coverage.get("verified_count") or 0)
    failed = int(coverage.get("failed_count") or 0)
    unsupported = int(coverage.get("unsupported_count") or 0)
    missing = int(coverage.get("missing_tracker_count") or 0)
    publish_ready = bool(coverage.get("publish_ready"))
    return {
        **coverage,
        "total_examples": total,
        "verified_count": verified,
        "failed_count": failed,
        "unsupported_count": unsupported,
        "missing_tracker_count": missing,
        "publish_ready": publish_ready,
    }


def _resolve_taxonomy_loader():
    import sys as _sys

    _local_mod = _sys.modules.get("core.gencode.services.v3_publish_eligibility")
    _orch_mod = _sys.modules.get("core.gencode.pipeline_orchestrator")
    _local_fn = getattr(_local_mod, "_load_v3_taxonomy_mvp_scope", None) if _local_mod else None
    _orch_fn = getattr(_orch_mod, "_load_v3_taxonomy_mvp_scope", None) if _orch_mod else None
    if _local_fn is not None and _local_fn is not _ORIGINAL_LOAD_FN:
        return _local_fn
    if _orch_fn is not None and _orch_fn is not _ORIGINAL_LOAD_FN:
        return _orch_fn
    return _ORIGINAL_LOAD_FN


def _parse_spec_payload(raw: Any) -> dict[str, Any]:
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else (raw or {})
    except Exception:
        parsed = {}
    return parsed if isinstance(parsed, dict) else {}


def _component_passes_integrity_gate(spec: dict[str, Any]) -> bool:
    return spec.get("integrity_gate_passed") is True and spec.get("integrity_gate_version") == "v1"


def component_publish_blockers(
    *,
    skill_id: str,
    component_skill_id: str,
    component_status: str,
    spec: dict[str, Any],
) -> list[str]:
    """Return publish blockers for one tracker row; empty means publish-eligible."""
    from core.gencode.skill_fixed_domain_authority import validate_publish_component_record

    status = str(component_status or "").strip()
    if status != "verified":
        return ["component_not_verified"]

    blockers = validate_publish_component_record(
        skill_id=skill_id,
        component_skill_id=str(component_skill_id),
        component_fixed_domain_key=str(spec.get("fixed_domain_key") or ""),
        component_operation=str(spec.get("domain_operation") or spec.get("problem_type_id") or ""),
        component_status=status,
    )
    if not _component_passes_integrity_gate(spec):
        blockers.append("integrity_gate_not_passed")
    return blockers


def count_publish_eligible_components(conn: sqlite3.Connection, skill_id: str) -> dict[str, int]:
    """Count verified vs publish-eligible components for a skill."""
    rows = conn.execute(
        """
        SELECT skill_id, gencode_status, induced_spec_payload
        FROM gencode_component_tracker
        WHERE skill_id = ?
        """,
        (skill_id,),
    ).fetchall()

    verified_count = 0
    eligible_count = 0
    domain_blocked_count = 0
    integrity_blocked_count = 0
    for row in rows:
        if hasattr(row, "keys"):
            row_skill = row["skill_id"]
            row_status = row["gencode_status"]
            raw_payload = row["induced_spec_payload"]
        else:
            row_skill, row_status, raw_payload = row[0], row[1], row[2]
        status = str(row_status or "").strip()
        if status != "verified":
            continue
        verified_count += 1
        spec = _parse_spec_payload(raw_payload)
        blockers = component_publish_blockers(
            skill_id=skill_id,
            component_skill_id=str(row_skill),
            component_status=status,
            spec=spec,
        )
        if not blockers:
            eligible_count += 1
            continue
        if "integrity_gate_not_passed" in blockers:
            integrity_blocked_count += 1
        if any(blocker != "integrity_gate_not_passed" for blocker in blockers):
            domain_blocked_count += 1
    return {
        "verified_component_count": verified_count,
        "eligible_component_count": eligible_count,
        "domain_blocked_component_count": domain_blocked_count,
        "integrity_blocked_component_count": integrity_blocked_count,
    }


def evaluate_v3_publish_eligibility(
    conn: sqlite3.Connection,
    skill_id: str,
    *,
    coverage: dict[str, object] | None = None,
    taxonomy_path: str = DEFAULT_TAXONOMY_PATH,
) -> dict[str, object]:
    """Return the authoritative V3 publish eligibility decision."""
    skill_key = str(skill_id or "").strip()
    if not skill_key or skill_key.startswith("outline_"):
        return {
            "allowed": False,
            "full_coverage": False,
            "reason": "not_concrete_skill",
            "skill_id": skill_key,
            "coverage": _normalize_coverage(coverage or {}),
            "eligible_component_count": 0,
        }

    try:
        domain_context = resolve_fixed_domain_context(skill_key)
        fixed_domain_key = domain_context.fixed_domain_key
    except SkillFixedDomainError as exc:
        return {
            "allowed": False,
            "full_coverage": False,
            "reason": DOMAIN_BINDING_MISSING,
            "skill_id": skill_key,
            "coverage": _normalize_coverage(coverage or {}),
            "eligible_component_count": 0,
            "error_code": exc.code or DOMAIN_BINDING_MISSING,
        }

    review_hints: list[str] = []
    try:
        taxonomy_scope = _resolve_taxonomy_loader()(taxonomy_path)
    except Exception:
        taxonomy_scope = set()
        review_hints.append("mvp_taxonomy_scope_unavailable")
    if skill_key not in taxonomy_scope:
        review_hints.append("skill_not_in_v3_mvp_scope")

    if _table_exists(conn, "skills_info"):
        skill_count = _count_rows(conn, "SELECT COUNT(*) FROM skills_info WHERE skill_id = ?", (skill_key,))
        if skill_count < 1:
            return {
                "allowed": False,
                "full_coverage": False,
                "reason": "SKILL_METADATA_MISSING",
                "skill_id": skill_key,
                "coverage": _normalize_coverage(coverage or {}),
                "eligible_component_count": 0,
                "fixed_domain_key": fixed_domain_key,
                "review_hints": review_hints,
            }

    if _table_exists(conn, "skill_curriculum"):
        curriculum_count = _count_rows(
            conn,
            "SELECT COUNT(*) FROM skill_curriculum WHERE skill_id = ?",
            (skill_key,),
        )
        if curriculum_count < 1:
            return {
                "allowed": False,
                "full_coverage": False,
                "reason": "SKILL_METADATA_MISSING",
                "skill_id": skill_key,
                "coverage": _normalize_coverage(coverage or {}),
                "eligible_component_count": 0,
                "fixed_domain_key": fixed_domain_key,
                "review_hints": review_hints,
            }

    normalized = _normalize_coverage(coverage or get_v3_skill_component_coverage(conn, skill_key))
    total = int(normalized.get("total_examples") or 0)
    verified = int(normalized.get("verified_count") or 0)
    failed = int(normalized.get("failed_count") or 0)
    missing = int(normalized.get("missing_tracker_count") or 0)

    component_counts = count_publish_eligible_components(conn, skill_key)
    eligible_count = int(component_counts["eligible_component_count"])
    domain_blocked_count = int(component_counts.get("domain_blocked_component_count") or 0)
    integrity_blocked_count = int(component_counts.get("integrity_blocked_component_count") or 0)
    integrity_gate_component_count = eligible_count

    if total < 1:
        reason = "no_textbook_examples"
        full_coverage = False
    elif eligible_count < 1:
        if verified < 1:
            reason = "NO_VERIFIED_COMPONENTS"
        elif integrity_blocked_count > 0 and domain_blocked_count < 1:
            reason = "COMPONENT_INTEGRITY_FAILED"
        elif failed > 0:
            reason = "COVERAGE_GATE_FAILED"
        else:
            reason = "COMPONENT_DOMAIN_MISMATCH"
        full_coverage = False
    elif missing > 0:
        reason = "eligible"
        full_coverage = False
    elif verified != total:
        reason = "eligible"
        full_coverage = False
    elif eligible_count != total:
        reason = "eligible"
        full_coverage = False
    elif failed > 0:
        reason = "eligible"
        full_coverage = False
    elif not bool(normalized.get("publish_ready")):
        reason = "eligible"
        full_coverage = False
    else:
        reason = "eligible"
        full_coverage = True

    return {
        "allowed": reason == "eligible",
        "full_coverage": full_coverage,
        "reason": reason,
        "skill_id": skill_key,
        "fixed_domain_key": fixed_domain_key,
        "curriculum_profile": domain_context.curriculum_profile,
        "allowed_operations": list(domain_context.allowed_operations),
        "coverage": normalized,
        "eligible_component_count": eligible_count,
        "domain_blocked_component_count": domain_blocked_count,
        "integrity_blocked_component_count": integrity_blocked_count,
        "integrity_gate_component_count": integrity_gate_component_count,
        "review_hints": review_hints,
    }
