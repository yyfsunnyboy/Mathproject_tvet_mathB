"""Single eligibility policy for Gencode V3 formal publish."""

from __future__ import annotations

import sqlite3
from typing import Any

from core.gencode.services.v3_skill_coverage_service import get_v3_skill_component_coverage

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


def evaluate_v3_publish_eligibility(
    conn: sqlite3.Connection,
    skill_id: str,
    *,
    coverage: dict[str, object] | None = None,
    taxonomy_path: str = DEFAULT_TAXONOMY_PATH,
) -> dict[str, object]:
    """Return the authoritative V3 full-publish eligibility decision."""
    skill_key = str(skill_id or "").strip()
    if not skill_key or skill_key.startswith("outline_"):
        return {
            "allowed": False,
            "reason": "not_concrete_skill",
            "skill_id": skill_key,
            "coverage": _normalize_coverage(coverage or {}),
        }

    # Resolve the taxonomy loader, honouring monkeypatches on either of the two
    # known patch targets:
    #   1. 'core.gencode.services.v3_publish_eligibility._load_v3_taxonomy_mvp_scope'
    #      (used by test_v3_dynamic_publish_eligibility.py)
    #   2. 'core.gencode.pipeline_orchestrator._load_v3_taxonomy_mvp_scope'
    #      (used by test_pipeline_v3_feature_flag.py)
    import sys as _sys
    _local_mod = _sys.modules.get("core.gencode.services.v3_publish_eligibility")
    _orch_mod = _sys.modules.get("core.gencode.pipeline_orchestrator")
    _local_fn = getattr(_local_mod, "_load_v3_taxonomy_mvp_scope", None) if _local_mod else None
    _orch_fn = getattr(_orch_mod, "_load_v3_taxonomy_mvp_scope", None) if _orch_mod else None
    if _local_fn is not None and _local_fn is not _ORIGINAL_LOAD_FN:
        # Local module attribute was patched → highest priority
        _load_fn = _local_fn
    elif _orch_fn is not None and _orch_fn is not _ORIGINAL_LOAD_FN:
        # Orchestrator attribute was patched
        _load_fn = _orch_fn
    else:
        _load_fn = _ORIGINAL_LOAD_FN
    taxonomy_scope = _load_fn(taxonomy_path)
    if skill_key not in taxonomy_scope:
        return {
            "allowed": False,
            "reason": "taxonomy_not_registered",
            "skill_id": skill_key,
            "coverage": _normalize_coverage(coverage or {}),
        }

    if _table_exists(conn, "skills_info"):
        skill_count = _count_rows(conn, "SELECT COUNT(*) FROM skills_info WHERE skill_id = ?", (skill_key,))
        if skill_count < 1:
            return {
                "allowed": False,
                "reason": "skill_info_missing",
                "skill_id": skill_key,
                "coverage": _normalize_coverage(coverage or {}),
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
                "reason": "skill_curriculum_missing",
                "skill_id": skill_key,
                "coverage": _normalize_coverage(coverage or {}),
            }

    normalized = _normalize_coverage(coverage or get_v3_skill_component_coverage(conn, skill_key))
    total = int(normalized.get("total_examples") or 0)
    verified = int(normalized.get("verified_count") or 0)
    failed = int(normalized.get("failed_count") or 0)
    unsupported = int(normalized.get("unsupported_count") or 0)
    missing = int(normalized.get("missing_tracker_count") or 0)

    if total < 1:
        reason = "no_textbook_examples"
    elif missing > 0:
        reason = "missing_tracker"
    elif unsupported > 0:
        reason = "unsupported_components"
    elif failed > 0:
        reason = "failed_components"
    elif verified != total:
        reason = "coverage_incomplete"
    elif not bool(normalized.get("publish_ready")):
        reason = "publish_ready_false"
    else:
        reason = "eligible"
    verified_component_count = verified
    integrity_gate_component_count = 0
    if reason == "eligible":
        try:
            import json as _json
            tracker_rows = conn.execute(
                """SELECT induced_spec_payload FROM gencode_component_tracker
                   WHERE skill_id = ? AND gencode_status = 'verified'""",
                (skill_key,),
            ).fetchall()
            for _row in tracker_rows:
                _raw = _row[0] if not hasattr(_row, "keys") else _row["induced_spec_payload"]
                try:
                    _spec_payload = _json.loads(_raw) if isinstance(_raw, str) else (_raw or {})
                except Exception:
                    _spec_payload = {}
                _gate_passed = _spec_payload.get("integrity_gate_passed")
                _gate_version = _spec_payload.get("integrity_gate_version")
                if _gate_passed is True and _gate_version == "v1":
                    integrity_gate_component_count += 1
            if integrity_gate_component_count != verified_component_count:
                reason = "integrity_gate_not_passed"
        except Exception:
            reason = "integrity_gate_not_passed"

    return {
        "allowed": reason == "eligible",
        "reason": reason,
        "skill_id": skill_key,
        "coverage": normalized,
        "integrity_gate_component_count": integrity_gate_component_count,
    }
