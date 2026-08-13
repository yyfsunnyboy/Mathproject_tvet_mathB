# -*- coding: utf-8 -*-
"""Skill-level V3 capability preflight (read-only; no tracker/production writes)."""

from __future__ import annotations

import importlib
import sqlite3
from typing import Any

from core.registry.taxonomy_registry import (
    SkillDomainNotRegisteredError,
    resolve_domain_for_skill,
)

CAPABILITY_READY = "ready"
CAPABILITY_PARTIAL = "partial"
CAPABILITY_MISSING = "missing"
CAPABILITY_INVALID = "invalid"

_VALID_STATUSES = frozenset(
    {CAPABILITY_READY, CAPABILITY_PARTIAL, CAPABILITY_MISSING, CAPABILITY_INVALID}
)


def _load_textbook_rows(conn: sqlite3.Connection, skill_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, skill_id, problem_text, correct_answer, detailed_solution,
               source_description, problem_type, notes
        FROM textbook_examples
        WHERE skill_id = ?
        ORDER BY id ASC
        """,
        (str(skill_id).strip(),),
    ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        if hasattr(row, "keys"):
            out.append(dict(row))
        else:
            out.append(
                {
                    "id": row[0],
                    "skill_id": row[1],
                    "problem_text": row[2],
                    "correct_answer": row[3],
                    "detailed_solution": row[4],
                    "source_description": row[5],
                    "problem_type": row[6],
                    "notes": row[7],
                }
            )
    return out


def _check_domain_wiring(skill_id: str) -> dict[str, Any]:
    skill_key = str(skill_id or "").strip()
    try:
        resolved = resolve_domain_for_skill(skill_key)
    except SkillDomainNotRegisteredError as exc:
        return {
            "registered": False,
            "domain_key": "",
            "registry_entry": {},
            "supported_operations": [],
            "domain_module": "",
            "entrypoint": "",
            "registry_revision": "",
            "wiring_ok": False,
            "missing_layers": ["domain_registry_binding"],
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "registered": False,
            "domain_key": "",
            "registry_entry": {},
            "supported_operations": [],
            "domain_module": "",
            "entrypoint": "",
            "registry_revision": "",
            "wiring_ok": False,
            "missing_layers": ["domain_registry_resolve_error"],
            "error": str(exc),
        }

    domain_key = str(resolved.get("fixed_domain_key") or "").strip()
    ops = [str(x).strip() for x in (resolved.get("allowed_operations") or []) if str(x).strip()]
    module_path = str(resolved.get("domain_module") or "").strip()
    entrypoint = str(resolved.get("entrypoint") or "").strip()
    missing_layers: list[str] = []
    wiring_ok = True

    if not domain_key:
        missing_layers.append("fixed_domain_key")
        wiring_ok = False
    if not ops:
        missing_layers.append("allowed_operations")
        wiring_ok = False
    if not module_path:
        missing_layers.append("domain_module")
        wiring_ok = False
    if not entrypoint:
        missing_layers.append("domain_entrypoint")
        wiring_ok = False

    if module_path:
        try:
            module = importlib.import_module(module_path)
            fn = getattr(module, entrypoint, None) if entrypoint else None
            if not callable(fn):
                missing_layers.append("entrypoint_not_callable")
                wiring_ok = False
        except ModuleNotFoundError:
            missing_layers.append("domain_module_import")
            wiring_ok = False
        except Exception as exc:
            missing_layers.append(f"domain_module_error:{type(exc).__name__}")
            wiring_ok = False

    return {
        "registered": True,
        "domain_key": domain_key,
        "registry_entry": {
            "fixed_domain_key": domain_key,
            "domain_module": module_path,
            "entrypoint": entrypoint,
            "registry_revision": str(resolved.get("registry_revision") or ""),
            "allowed_operations": ops,
        },
        "supported_operations": ops,
        "domain_module": module_path,
        "entrypoint": entrypoint,
        "registry_revision": str(resolved.get("registry_revision") or ""),
        "wiring_ok": wiring_ok,
        "missing_layers": missing_layers,
        "error": "",
    }


def _probe_example_resolvable(
    *,
    skill_id: str,
    row: dict[str, Any],
    conn: sqlite3.Connection,
) -> dict[str, Any]:
    """Use the same no-LLM Phase1 authority as Admin V3 (read-only; no tracker writes)."""
    from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example

    example_id = int(row.get("id") or 0)
    try:
        induced = run_v3_no_llm_phase1_for_example(skill_id, row, conn=conn)
    except Exception as exc:
        return {
            "textbook_example_id": example_id,
            "resolvable": False,
            "reason": f"phase1_exception:{type(exc).__name__}",
            "problem_type_id": "",
        }
    status = str(induced.get("classification_status") or "").strip()
    problem_type_id = str(induced.get("problem_type_id") or "").strip()
    ok = status == "resolved" and bool(problem_type_id)
    return {
        "textbook_example_id": example_id,
        "resolvable": ok,
        "reason": "" if ok else str(induced.get("reason") or status or "unresolved"),
        "problem_type_id": problem_type_id,
        "classification_source": str(induced.get("classification_source") or ""),
    }


def _next_action_for(status: str) -> str:
    if status == CAPABILITY_READY:
        return "rebuild_and_verify"
    if status in (CAPABILITY_PARTIAL, CAPABILITY_MISSING, CAPABILITY_INVALID):
        return "start_system_ai_capability_fill"
    return "start_system_ai_capability_fill"


def evaluate_skill_v3_capability(
    conn: sqlite3.Connection,
    skill_id: str,
    *,
    probe_examples: bool = True,
) -> dict[str, Any]:
    """
    Read-only capability preflight for one skill.

    Does not write tracker, dryrun artifacts, or production.
    """
    skill_key = str(skill_id or "").strip()
    wiring = _check_domain_wiring(skill_key)
    rows = _load_textbook_rows(conn, skill_key)
    total = len(rows)

    example_probes: list[dict[str, Any]] = []
    resolvable_ids: list[int] = []
    unresolved_ids: list[int] = []

    if probe_examples and wiring.get("registered") and wiring.get("wiring_ok"):
        for row in rows:
            probe = _probe_example_resolvable(skill_id=skill_key, row=row, conn=conn)
            example_probes.append(probe)
            eid = int(probe["textbook_example_id"])
            if probe.get("resolvable"):
                resolvable_ids.append(eid)
            else:
                unresolved_ids.append(eid)
    elif rows and not wiring.get("registered"):
        unresolved_ids = [int(r.get("id") or 0) for r in rows]
    elif rows and wiring.get("registered") and not wiring.get("wiring_ok"):
        unresolved_ids = [int(r.get("id") or 0) for r in rows]

    missing_layers = list(wiring.get("missing_layers") or [])
    if total == 0:
        missing_layers.append("textbook_examples")
    if wiring.get("registered") and wiring.get("wiring_ok") and unresolved_ids:
        missing_layers.append("example_operation_resolution")

    # Status decision
    if not wiring.get("registered"):
        status = CAPABILITY_MISSING
    elif not wiring.get("wiring_ok"):
        status = CAPABILITY_INVALID
    elif total == 0:
        status = CAPABILITY_PARTIAL
    elif len(unresolved_ids) == 0 and len(resolvable_ids) == total:
        status = CAPABILITY_READY
    elif len(resolvable_ids) == 0:
        # Domain wired but no example maps — treat as incomplete capability coverage
        status = CAPABILITY_PARTIAL
    else:
        status = CAPABILITY_PARTIAL

    allow_rebuild = status == CAPABILITY_READY
    next_action = _next_action_for(status)

    return {
        "skill_id": skill_key,
        "capability_status": status,
        "domain_key": wiring.get("domain_key") or "",
        "registry_entry": wiring.get("registry_entry") or {},
        "supported_operations": list(wiring.get("supported_operations") or []),
        "domain_module": wiring.get("domain_module") or "",
        "entrypoint": wiring.get("entrypoint") or "",
        "registry_revision": wiring.get("registry_revision") or "",
        "textbook_example_count": total,
        "resolvable_example_count": len(resolvable_ids),
        "unresolved_example_count": len(unresolved_ids),
        "resolvable_example_ids": resolvable_ids,
        "unresolved_example_ids": unresolved_ids,
        "missing_layers": list(dict.fromkeys(missing_layers)),
        "allow_v3_rebuild": allow_rebuild,
        "next_action": next_action,
        "wiring_error": wiring.get("error") or "",
        "example_probes": example_probes,
        "ui": {
            "status_label": {
                CAPABILITY_READY: "能力就緒",
                CAPABILITY_PARTIAL: "能力不完整",
                CAPABILITY_MISSING: "尚未建立出題能力",
                CAPABILITY_INVALID: "能力接線錯誤",
            }.get(status, status),
            "primary_action_label": {
                CAPABILITY_READY: "重新建置與驗證",
                CAPABILITY_PARTIAL: "系統AI補全能力",
                CAPABILITY_MISSING: "系統AI補全能力",
                CAPABILITY_INVALID: "系統AI補全能力",
            }.get(status, "系統AI補全能力"),
            "secondary_action_label": "匯出診斷",
            "tooltip": "Gencode V3會使用既有domain能力重新建置，不會自行建立新API。缺口由系統AI角色補全隔離candidate，不會自動寫入正式core。",
        },
    }


def evaluate_skills_v3_capability_map(
    conn: sqlite3.Connection,
    skill_ids: list[str],
    *,
    probe_examples: bool = True,
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for skill_id in skill_ids:
        key = str(skill_id or "").strip()
        if not key:
            continue
        out[key] = evaluate_skill_v3_capability(conn, key, probe_examples=probe_examples)
    return out


def assert_skill_allows_v3_rebuild(
    conn: sqlite3.Connection,
    skill_id: str,
    *,
    maintenance_override: bool = False,
) -> dict[str, Any]:
    """
    Gate for POST dryrun. Returns preflight dict when allowed.
    Raises CapabilityPreflightBlocked when rebuild is not allowed.
    """
    preflight = evaluate_skill_v3_capability(conn, skill_id, probe_examples=True)
    if maintenance_override:
        preflight = dict(preflight)
        preflight["allow_v3_rebuild"] = True
        preflight["maintenance_override"] = True
        return preflight
    if preflight.get("capability_status") != CAPABILITY_READY or not preflight.get("allow_v3_rebuild"):
        raise CapabilityPreflightBlocked(preflight)
    return preflight


class CapabilityPreflightBlocked(Exception):
    def __init__(self, diagnostic: dict[str, Any]):
        self.diagnostic = diagnostic if isinstance(diagnostic, dict) else {}
        status = str(self.diagnostic.get("capability_status") or "blocked")
        super().__init__(f"capability_preflight_blocked:{status}")
