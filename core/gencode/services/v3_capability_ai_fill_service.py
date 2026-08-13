# -*- coding: utf-8 -*-
"""System AI capability fill (phase-1): isolated candidates only, no promotion/core writes.

Uses existing roles ``architect`` / ``coder`` via ``get_ai_client``.
Must NEVER call ``resolve_gencode_ai_client`` (forces Gemini/cloud_fallback).
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from core.ai_settings import get_ai_settings_snapshot, get_effective_model_config
from core.ai_wrapper import get_ai_client
from core.gencode.services.v3_capability_handoff_service import compute_gap_fingerprint
from core.gencode.services.v3_skill_capability_preflight_service import (
    CAPABILITY_READY,
    evaluate_skill_v3_capability,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CANDIDATE_ROOT = PROJECT_ROOT / "reports" / "gencode_capability_candidates"

STATE_ARCHITECT = "architect_running"
STATE_CODER_1 = "coder_round_1"
STATE_VALIDATE_1 = "validating_round_1"
STATE_CODER_2 = "coder_round_2"
STATE_VALIDATE_2 = "validating_round_2"
STATE_AWAITING = "awaiting_admin_confirm"
STATE_BLOCKED = "blocked"

ACTIVE_STATES = frozenset(
    {
        STATE_ARCHITECT,
        STATE_CODER_1,
        STATE_VALIDATE_1,
        STATE_CODER_2,
        STATE_VALIDATE_2,
        STATE_AWAITING,
    }
)

ClientFactory = Callable[[str], Any]


class CapabilityAiFillError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _safe_endpoint(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    # Strip query/fragment that may carry secrets; never log API keys.
    text = re.sub(r"(?i)([?&](?:key|api_key|apikey|token|access_token)=)[^&]+", r"\1***", text)
    text = re.sub(r"(?i)(Bearer\s+)\S+", r"\1***", text)
    return text[:300]


def _provider_of(cfg: dict[str, Any]) -> str:
    return str(cfg.get("provider") or "").strip().lower()


def _is_cloud_provider(provider: str) -> bool:
    return provider in ("google", "gemini")


def assert_edge_roles_are_local() -> dict[str, Any]:
    """Edge (local_first): architect and coder must resolve to local; else block."""
    snapshot = get_ai_settings_snapshot()
    strategy = str(snapshot.get("ai_global_strategy") or "")
    roles_meta: dict[str, Any] = {"strategy": strategy, "roles": {}}
    if strategy != "local_first":
        for role in ("architect", "coder"):
            cfg = get_effective_model_config(role)
            roles_meta["roles"][role] = {
                "provider": _provider_of(cfg),
                "model": cfg.get("model"),
                "preset_key": cfg.get("preset_key"),
                "source": cfg.get("_resolved_source"),
            }
        return roles_meta

    blocked: list[str] = []
    for role in ("architect", "coder"):
        cfg = get_effective_model_config(role)
        provider = _provider_of(cfg)
        roles_meta["roles"][role] = {
            "provider": provider,
            "model": cfg.get("model"),
            "preset_key": cfg.get("preset_key"),
            "source": cfg.get("_resolved_source"),
        }
        if _is_cloud_provider(provider):
            blocked.append(role)
    if blocked:
        raise CapabilityAiFillError(
            "edge_cloud_role_blocked",
            f"Edge mode resolved cloud provider for: {', '.join(blocked)}",
            details=roles_meta,
        )
    return roles_meta


def _default_client_factory(role: str) -> Any:
    # Intentional: role-based factory only. Never resolve_gencode_ai_client.
    return get_ai_client(role=role)


def _load_example_briefs(conn: sqlite3.Connection, skill_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, problem_text, correct_answer, problem_type, source_description
        FROM textbook_examples
        WHERE skill_id = ?
        ORDER BY id ASC
        """,
        (str(skill_id).strip(),),
    ).fetchall()
    briefs: list[dict[str, Any]] = []
    for row in rows:
        if hasattr(row, "keys"):
            d = dict(row)
        else:
            d = {
                "id": row[0],
                "problem_text": row[1],
                "correct_answer": row[2],
                "problem_type": row[3],
                "source_description": row[4],
            }
        briefs.append(
            {
                "textbook_example_id": int(d.get("id") or 0),
                "source_id": f"src_{int(d.get('id') or 0)}",
                "problem_type": str(d.get("problem_type") or ""),
                "problem_text": str(d.get("problem_text") or "")[:800],
                "correct_answer": str(d.get("correct_answer") or "")[:300],
                "source_description": str(d.get("source_description") or ""),
            }
        )
    return briefs


def _find_reusable_job(
    root: Path,
    *,
    skill_id: str,
    fingerprint: str,
) -> Path | None:
    if not root.is_dir():
        return None
    candidates = sorted([p for p in root.iterdir() if p.is_dir()], key=lambda p: p.name, reverse=True)
    for folder in candidates:
        job_path = folder / "job.json"
        if not job_path.is_file():
            continue
        try:
            job = json.loads(job_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if str(job.get("skill_id") or "") != skill_id:
            continue
        if str(job.get("gap_fingerprint") or "") != fingerprint:
            continue
        status = str(job.get("status") or "")
        if status in ACTIVE_STATES:
            return folder
    return None


def _write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _update_job(job_dir: Path, **fields: Any) -> dict[str, Any]:
    job_path = job_dir / "job.json"
    job = json.loads(job_path.read_text(encoding="utf-8")) if job_path.is_file() else {}
    job.update(fields)
    job["updated_at"] = _utc_now()
    _write_json(job_path, job)
    return job


def _extract_json_object(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        pass
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, flags=re.DOTALL)
    if fence:
        try:
            parsed = json.loads(fence.group(1))
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            pass
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(raw[start : end + 1])
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _call_role(
    *,
    role: str,
    prompt: str,
    job_dir: Path,
    client_factory: ClientFactory,
    validator_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cfg = get_effective_model_config(role)
    provider = _provider_of(cfg)
    model = str(cfg.get("model") or "")
    preset_key = str(cfg.get("preset_key") or "")
    client = client_factory(role)

    endpoint = ""
    if hasattr(client, "api_url"):
        endpoint = _safe_endpoint(str(getattr(client, "api_url") or ""))
    elif "Google" in type(client).__name__:
        endpoint = "google_api"

    started = time.perf_counter()
    started_at = _utc_now()
    status = "ok"
    response_text = ""
    error = ""
    try:
        resp = client.generate_content(prompt)
        response_text = str(getattr(resp, "text", None) or resp or "")
    except Exception as exc:
        status = "error"
        error = f"{type(exc).__name__}:{exc}"
        response_text = ""
    latency_ms = int((time.perf_counter() - started) * 1000)

    evidence = {
        "role": role,
        "provider": provider,
        "model": model,
        "preset_key": preset_key,
        "endpoint": endpoint,
        "request_result": status,
        "error": error,
        "latency_ms": latency_ms,
        "prompt_sha256": _sha256_text(prompt),
        "response_sha256": _sha256_text(response_text),
        "timestamp": started_at,
        "finished_at": _utc_now(),
        "validator_summary": validator_summary or {},
        "resolved_source": cfg.get("_resolved_source"),
    }
    _append_jsonl(job_dir / "model_call_evidence.jsonl", evidence)
    if status != "ok":
        raise CapabilityAiFillError(
            "model_call_failed",
            f"{role} call failed: {error}",
            details=evidence,
        )
    return {"text": response_text, "evidence": evidence}


def _architect_prompt(preflight: dict[str, Any], briefs: list[dict[str, Any]]) -> str:
    return (
        "你是系統角色 architect。請分析整個 skill 題群，設計共用 domain capability。\n"
        "只輸出 JSON（勿 markdown），欄位：\n"
        "skill_id, capability_status, domain_key_suggestion, required_operations (list),\n"
        "missing_layers, isomorphism_groups (list of {group_key, textbook_example_ids}),\n"
        "candidate_plan (object: files list + summary), constraints (list).\n"
        "硬限制：不得要求修改正式 core／DB／tracker／production；只規劃隔離 candidate。\n\n"
        f"preflight={json.dumps(preflight, ensure_ascii=False)}\n"
        f"examples={json.dumps(briefs, ensure_ascii=False)}"
    )


def _coder_prompt(spec: dict[str, Any], *, round_no: int, validation: dict[str, Any] | None) -> str:
    repair = ""
    if round_no > 1 and validation:
        repair = f"\n上一輪 validator 失敗：{json.dumps(validation, ensure_ascii=False)}\n請修正 candidate。\n"
    return (
        "你是系統角色 coder。依 capability_spec 產生隔離 candidate 檔案內容。\n"
        "只輸出 JSON：{ \"files\": [ {\"path\": \"relative/path.py\", \"content\": \"...\"} ], "
        "\"notes\": \"...\" }\n"
        "path 必須相對 candidate 根，禁止絕對路徑與 .. 跳出。\n"
        f"{repair}\n"
        f"capability_spec={json.dumps(spec, ensure_ascii=False)}"
    )


def _sanitize_rel_path(raw: str) -> str | None:
    text = str(raw or "").replace("\\", "/").strip().lstrip("/")
    if not text or text.startswith("..") or "/../" in f"/{text}/":
        return None
    if Path(text).is_absolute():
        return None
    return text


def _write_candidate_files(job_dir: Path, files: list[dict[str, Any]]) -> list[str]:
    written: list[str] = []
    cand_root = job_dir / "candidate"
    cand_root.mkdir(parents=True, exist_ok=True)
    for item in files:
        if not isinstance(item, dict):
            continue
        rel = _sanitize_rel_path(str(item.get("path") or ""))
        if not rel:
            continue
        target = cand_root / rel
        # Ensure still under cand_root
        try:
            target.resolve().relative_to(cand_root.resolve())
        except Exception:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(item.get("content") or ""), encoding="utf-8")
        written.append(rel)
    return written


def validate_candidate_workspace(job_dir: Path, spec: dict[str, Any]) -> dict[str, Any]:
    """Structural validator only — no core/DB/production writes."""
    blockers: list[str] = []
    cand_root = job_dir / "candidate"
    if not cand_root.is_dir():
        blockers.append("missing_candidate_dir")
    files = sorted(str(p.relative_to(cand_root)).replace("\\", "/") for p in cand_root.rglob("*") if p.is_file()) if cand_root.is_dir() else []
    if not files:
        blockers.append("no_candidate_files")

    required_ops = list(spec.get("required_operations") or [])
    if not required_ops:
        blockers.append("spec_missing_required_operations")
    if not str(spec.get("domain_key_suggestion") or spec.get("domain_key") or "").strip():
        blockers.append("spec_missing_domain_key_suggestion")

    # Syntax check for python candidate files
    for rel in files:
        if not rel.endswith(".py"):
            continue
        src = (cand_root / rel).read_text(encoding="utf-8")
        try:
            compile(src, rel, "exec")
        except SyntaxError as exc:
            blockers.append(f"python_syntax_error:{rel}:{exc.msg}")

    # Guard: candidate tree must stay under allowed root
    try:
        cand_root.resolve().relative_to(job_dir.resolve())
    except Exception:
        blockers.append("candidate_escaped_job_dir")

    passed = not blockers
    result = {
        "passed": passed,
        "blockers": blockers,
        "file_count": len(files),
        "files": files,
        "checked_at": _utc_now(),
    }
    _append_jsonl(job_dir / "validator_results.jsonl", result)
    return result


def run_system_ai_capability_fill(
    conn: sqlite3.Connection,
    skill_id: str,
    *,
    candidate_root: str | Path | None = None,
    client_factory: ClientFactory | None = None,
    force_new: bool = False,
) -> dict[str, Any]:
    """
    Phase-1 fill: architect → coder(+1 repair) → await admin confirm.

    Never promotes, never writes core/DB/tracker/production, never rebuilds skill.
    """
    skill_key = str(skill_id or "").strip()
    if not skill_key:
        raise CapabilityAiFillError("missing_skill_id", "missing_skill_id")

    preflight = evaluate_skill_v3_capability(conn, skill_key, probe_examples=True)
    if preflight.get("capability_status") == CAPABILITY_READY:
        raise CapabilityAiFillError(
            "capability_already_ready",
            "skill is ready; use V3 deterministic rebuild",
            details={"capability_status": CAPABILITY_READY},
        )

    fingerprint = compute_gap_fingerprint(preflight)
    root = Path(candidate_root) if candidate_root else DEFAULT_CANDIDATE_ROOT
    root.mkdir(parents=True, exist_ok=True)

    if not force_new:
        reused = _find_reusable_job(root, skill_id=skill_key, fingerprint=fingerprint)
        if reused is not None:
            job = json.loads((reused / "job.json").read_text(encoding="utf-8"))
            return {
                "ok": True,
                "reused": True,
                "job_id": job.get("job_id"),
                "status": job.get("status"),
                "job_dir": str(reused),
                "gap_fingerprint": fingerprint,
                "skill_id": skill_key,
                "preflight": preflight,
            }

    # Edge safety gate before any model call
    try:
        role_meta = assert_edge_roles_are_local()
    except CapabilityAiFillError as blocked:
        job_id = f"{skill_key}__{fingerprint[:12]}__{uuid.uuid4().hex[:8]}"
        job_dir = root / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        _write_json(job_dir / "preflight.json", preflight)
        job = {
            "job_id": job_id,
            "skill_id": skill_key,
            "gap_fingerprint": fingerprint,
            "status": STATE_BLOCKED,
            "block_reason": blocked.code,
            "block_details": blocked.details,
            "created_at": _utc_now(),
            "updated_at": _utc_now(),
            "phase": "phase1_awaiting_admin_confirm_only",
            "promotion": False,
            "writes_core": False,
            "writes_db": False,
            "writes_tracker": False,
            "writes_production": False,
        }
        _write_json(job_dir / "job.json", job)
        return {
            "ok": False,
            "reused": False,
            "job_id": job_id,
            "status": STATE_BLOCKED,
            "job_dir": str(job_dir),
            "gap_fingerprint": fingerprint,
            "skill_id": skill_key,
            "error": blocked.code,
            "message": str(blocked),
            "preflight": preflight,
        }

    factory = client_factory or _default_client_factory
    job_id = f"{skill_key}__{fingerprint[:12]}__{uuid.uuid4().hex[:8]}"
    job_dir = root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    _write_json(job_dir / "preflight.json", preflight)
    job = {
        "job_id": job_id,
        "skill_id": skill_key,
        "gap_fingerprint": fingerprint,
        "status": STATE_ARCHITECT,
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
        "phase": "phase1_awaiting_admin_confirm_only",
        "promotion": False,
        "writes_core": False,
        "writes_db": False,
        "writes_tracker": False,
        "writes_production": False,
        "role_resolution": role_meta,
        "coder_rounds_max": 2,
    }
    _write_json(job_dir / "job.json", job)

    briefs = _load_example_briefs(conn, skill_key)

    try:
        _update_job(job_dir, status=STATE_ARCHITECT)
        arch = _call_role(
            role="architect",
            prompt=_architect_prompt(preflight, briefs),
            job_dir=job_dir,
            client_factory=factory,
        )
        spec = _extract_json_object(arch["text"])
        if not spec:
            spec = {
                "skill_id": skill_key,
                "capability_status": preflight.get("capability_status"),
                "domain_key_suggestion": preflight.get("domain_key") or f"candidate_{skill_key}",
                "required_operations": list(preflight.get("supported_operations") or []) or ["unresolved_operation"],
                "missing_layers": list(preflight.get("missing_layers") or []),
                "isomorphism_groups": [],
                "candidate_plan": {"summary": "fallback_spec_from_preflight", "files": ["domain_module.py"]},
                "constraints": ["isolated_candidate_only"],
                "raw_architect_text_sha256": _sha256_text(arch["text"]),
            }
        spec.setdefault("skill_id", skill_key)
        _write_json(job_dir / "capability_spec.json", spec)

        # Round 1 coder + validate
        _update_job(job_dir, status=STATE_CODER_1)
        coder1 = _call_role(
            role="coder",
            prompt=_coder_prompt(spec, round_no=1, validation=None),
            job_dir=job_dir,
            client_factory=factory,
        )
        payload1 = _extract_json_object(coder1["text"])
        files1 = list(payload1.get("files") or [])
        if not files1:
            # Minimal deterministic scaffold if model returned prose
            files1 = [
                {
                    "path": "domain_module.py",
                    "content": (
                        '"""Isolated capability candidate (phase-1)."""\n\n'
                        f"DOMAIN_KEY = {spec.get('domain_key_suggestion')!r}\n"
                        f"REQUIRED_OPERATIONS = {list(spec.get('required_operations') or [])!r}\n\n"
                        "def build_fixture_matrix():\n"
                        "    return {\"operations\": REQUIRED_OPERATIONS}\n"
                    ),
                },
                {
                    "path": "README.md",
                    "content": "# Isolated candidate\n\nAwaiting admin confirm. Do not promote automatically.\n",
                },
            ]
        written = _write_candidate_files(job_dir, files1)
        _write_json(job_dir / "candidate_manifest.json", {"round": 1, "files": written, "notes": payload1.get("notes")})

        _update_job(job_dir, status=STATE_VALIDATE_1)
        validation1 = validate_candidate_workspace(job_dir, spec)
        if validation1.get("passed"):
            job = _update_job(job_dir, status=STATE_AWAITING, validation_passed=True, coder_rounds_used=1)
            return {
                "ok": True,
                "reused": False,
                "job_id": job_id,
                "status": STATE_AWAITING,
                "job_dir": str(job_dir),
                "gap_fingerprint": fingerprint,
                "skill_id": skill_key,
                "coder_rounds_used": 1,
                "preflight": preflight,
            }

        # Round 2 (one repair only)
        _update_job(job_dir, status=STATE_CODER_2)
        coder2 = _call_role(
            role="coder",
            prompt=_coder_prompt(spec, round_no=2, validation=validation1),
            job_dir=job_dir,
            client_factory=factory,
            validator_summary={"round": 1, "passed": False, "blockers": validation1.get("blockers")},
        )
        payload2 = _extract_json_object(coder2["text"])
        files2 = list(payload2.get("files") or [])
        if files2:
            written2 = _write_candidate_files(job_dir, files2)
            _write_json(
                job_dir / "candidate_manifest.json",
                {"round": 2, "files": written2, "notes": payload2.get("notes")},
            )

        _update_job(job_dir, status=STATE_VALIDATE_2)
        validation2 = validate_candidate_workspace(job_dir, spec)
        if validation2.get("passed"):
            job = _update_job(job_dir, status=STATE_AWAITING, validation_passed=True, coder_rounds_used=2)
            return {
                "ok": True,
                "reused": False,
                "job_id": job_id,
                "status": STATE_AWAITING,
                "job_dir": str(job_dir),
                "gap_fingerprint": fingerprint,
                "skill_id": skill_key,
                "coder_rounds_used": 2,
                "preflight": preflight,
            }

        job = _update_job(
            job_dir,
            status=STATE_BLOCKED,
            validation_passed=False,
            block_reason="validator_failed_after_repair",
            coder_rounds_used=2,
            last_validation=validation2,
        )
        return {
            "ok": False,
            "reused": False,
            "job_id": job_id,
            "status": STATE_BLOCKED,
            "job_dir": str(job_dir),
            "gap_fingerprint": fingerprint,
            "skill_id": skill_key,
            "coder_rounds_used": 2,
            "error": "validator_failed_after_repair",
            "last_validation": validation2,
            "preflight": preflight,
        }
    except CapabilityAiFillError as exc:
        _update_job(
            job_dir,
            status=STATE_BLOCKED,
            block_reason=exc.code,
            block_details=exc.details,
            error_message=str(exc),
        )
        return {
            "ok": False,
            "reused": False,
            "job_id": job_id,
            "status": STATE_BLOCKED,
            "job_dir": str(job_dir),
            "gap_fingerprint": fingerprint,
            "skill_id": skill_key,
            "error": exc.code,
            "message": str(exc),
            "preflight": preflight,
        }
    except Exception as exc:
        _update_job(
            job_dir,
            status=STATE_BLOCKED,
            block_reason="unexpected_error",
            error_message=f"{type(exc).__name__}:{exc}",
        )
        return {
            "ok": False,
            "reused": False,
            "job_id": job_id,
            "status": STATE_BLOCKED,
            "job_dir": str(job_dir),
            "gap_fingerprint": fingerprint,
            "skill_id": skill_key,
            "error": "unexpected_error",
            "message": str(exc),
            "preflight": preflight,
        }


# Explicit guard for tests / greps: this module must not reference resolve_gencode_ai_client.
FORBIDDEN_GENCODE_AI_RESOLVE = "resolve_gencode_ai_client"
