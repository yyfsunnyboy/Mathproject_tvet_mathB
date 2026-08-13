# -*- coding: utf-8 -*-
"""System AI capability fill (phase-1): isolated candidates only, no promotion/core writes.

Uses existing roles ``architect`` / ``coder`` via ``get_ai_client``.
Must NEVER call ``resolve_gencode_ai_client`` (forces Gemini/cloud_fallback).
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from core.ai_settings import get_ai_settings_snapshot, get_effective_model_config
from core.ai_wrapper import get_ai_client
from core.gencode.services.v3_capability_compatibility_validator import (
    ALLOWED_OFFICIAL_TARGETS,
    BLOCK_INCOMPATIBLE,
    official_matrix_fields,
    parse_coder_contract as parse_official_coder_contract,
    validate_architect_spec as validate_official_architect_spec,
    validate_official_compatibility,
)
from core.gencode.services.v3_capability_handoff_service import compute_gap_fingerprint
from core.gencode.services.v3_skill_capability_preflight_service import (
    CAPABILITY_READY,
    evaluate_skill_v3_capability,
)
from core.registry.domain_operation_registry import get_domain_spec, list_registered_domains

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CANDIDATE_ROOT = PROJECT_ROOT / "reports" / "gencode_capability_candidates"

STATE_ARCHITECT = "architect_running"
STATE_CODER_1 = "coder_round_1"
STATE_VALIDATE_1 = "validating_round_1"
STATE_CODER_2 = "coder_round_2"
STATE_VALIDATE_2 = "validating_round_2"
STATE_AWAITING = "awaiting_admin_confirm"
STATE_BLOCKED = "blocked"

ORIGIN_ARCHITECT = "architect"
ORIGIN_CODER = "coder"
ORIGIN_DIAGNOSTIC_NON_AI = "diagnostic_non_ai_fallback"
ORIGIN_FALLBACK_SPEC = "fallback_spec_from_preflight"
ORIGIN_SCAFFOLD = "deterministic_scaffold"

IN_FLIGHT_STATES = frozenset(
    {
        STATE_ARCHITECT,
        STATE_CODER_1,
        STATE_VALIDATE_1,
        STATE_CODER_2,
        STATE_VALIDATE_2,
    }
)

ACTIVE_STATES = frozenset(IN_FLIGHT_STATES | {STATE_AWAITING})

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


FILL_LOCAL_THINK_ENABLED = False


def _generate_content_for_fill(client: Any, prompt: str) -> Any:
    """Call-level think=false for fill architect/coder only.

    Other LocalAIClient callers omit think and keep default Ollama behavior.
    Clients that reject the keyword (Google / older mocks) fall back.
    """
    generate = getattr(client, "generate_content")
    try:
        return generate(prompt, think=FILL_LOCAL_THINK_ENABLED)
    except TypeError:
        return generate(prompt)


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
        if not _job_is_reusable(job):
            continue
        return folder
    return None


def _job_is_reusable(job: dict[str, Any]) -> bool:
    status = str(job.get("status") or "")
    if status in IN_FLIGHT_STATES:
        return True
    if status != STATE_AWAITING:
        return False
    if job.get("ai_output_valid") is not True:
        return False
    if job.get("spec_origin") != ORIGIN_ARCHITECT:
        return False
    if job.get("candidate_origin") != ORIGIN_CODER:
        return False
    if job.get("validation_passed") is not True:
        return False
    if job.get("official_compatibility_passed") is not True:
        return False
    if str(job.get("block_reason") or "") == BLOCK_INCOMPATIBLE:
        return False
    return True


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


def _visible_text_from_response(resp: Any) -> tuple[str, bool, bool, bool]:
    """Return (text, empty_model_output, thinking_present, http_ok). Never stringify the client object."""
    raw = getattr(resp, "text", None)
    text = "" if raw is None else str(raw)
    thinking = str(getattr(resp, "thinking", "") or "")
    http_ok = bool(getattr(resp, "http_ok", True))
    flagged_empty = bool(getattr(resp, "empty_model_output", False))
    empty = (not text.strip()) or flagged_empty
    return text, empty, bool(thinking.strip()), http_ok


def validate_architect_spec(
    spec: dict[str, Any],
    *,
    skill_id: str,
    example_ids: list[int] | None = None,
) -> list[str]:
    blockers: list[str] = []
    if not isinstance(spec, dict) or not spec:
        return ["architect_json_missing"]
    origin = str(spec.get("origin") or spec.get("candidate_plan", {}).get("summary") or "")
    if origin in (ORIGIN_FALLBACK_SPEC, ORIGIN_DIAGNOSTIC_NON_AI, ORIGIN_SCAFFOLD):
        blockers.append("non_ai_spec_forbidden_in_official_fill")
    blockers.extend(
        validate_official_architect_spec(
            spec,
            skill_id=skill_id,
            example_ids=list(example_ids or []),
        )
    )
    plan = spec.get("candidate_plan")
    if not isinstance(plan, dict):
        blockers.append("spec_missing_candidate_plan")
    elif not isinstance(plan.get("files"), list) and not str(plan.get("summary") or "").strip():
        blockers.append("spec_missing_candidate_plan")
    constraints = spec.get("constraints")
    if constraints is not None and not isinstance(constraints, list):
        blockers.append("spec_invalid_constraints")
    groups = spec.get("isomorphism_groups")
    if groups is not None and not isinstance(groups, list):
        blockers.append("spec_invalid_isomorphism_groups")
    return list(dict.fromkeys(blockers))


def parse_coder_contract(
    payload: dict[str, Any],
    skill_id: str = "",
) -> tuple[list[dict[str, Any]], list[str]]:
    return parse_official_coder_contract(payload, skill_id=skill_id)


def _assert_awaiting_allowed(
    *,
    spec: dict[str, Any],
    spec_origin: str,
    candidate_origin: str,
    architect_ok: bool,
    coder_ok: bool,
    validator_passed: bool,
) -> None:
    blockers: list[str] = []
    if spec_origin != ORIGIN_ARCHITECT:
        blockers.append("spec_not_from_architect")
    if candidate_origin != ORIGIN_CODER:
        blockers.append("candidate_not_from_coder")
    if not architect_ok:
        blockers.append("architect_evidence_invalid")
    if not coder_ok:
        blockers.append("coder_evidence_invalid")
    if not validator_passed:
        blockers.append("validator_not_passed")
    if spec.get("origin") in (ORIGIN_FALLBACK_SPEC, ORIGIN_DIAGNOSTIC_NON_AI, ORIGIN_SCAFFOLD):
        blockers.append("non_ai_spec_cannot_await")
    if spec.get("ai_generated") is not True:
        blockers.append("spec_not_ai_generated")
    if blockers:
        raise CapabilityAiFillError(
            "awaiting_gate_failed",
            "awaiting_admin_confirm requires valid architect spec, coder candidate, evidence, and validator",
            details={"blockers": blockers},
        )


def build_diagnostic_fallback_spec(preflight: dict[str, Any], *, skill_id: str) -> dict[str, Any]:
    """Non-AI diagnostic spec only. Must never be used by official fill, and must not promote."""
    return {
        "skill_id": skill_id,
        "capability_status": preflight.get("capability_status"),
        "domain_key_suggestion": preflight.get("domain_key") or f"candidate_{skill_id}",
        "required_operations": list(preflight.get("supported_operations") or []) or ["unresolved_operation"],
        "missing_layers": list(preflight.get("missing_layers") or []),
        "isomorphism_groups": [],
        "candidate_plan": {"summary": ORIGIN_DIAGNOSTIC_NON_AI, "files": ["domain_module.py"]},
        "constraints": ["isolated_candidate_only", "non_ai_diagnostic", "promotion_forbidden"],
        "origin": ORIGIN_DIAGNOSTIC_NON_AI,
        "promotion_allowed": False,
        "ai_generated": False,
    }


def build_diagnostic_scaffold_files(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Non-AI diagnostic files only. Must never be treated as coder output."""
    return [
        {
            "path": "domain_module.py",
            "content": (
                '"""Isolated diagnostic scaffold (non-AI). Do not promote."""\n\n'
                f"DOMAIN_KEY = {spec.get('domain_key_suggestion')!r}\n"
                f"REQUIRED_OPERATIONS = {list(spec.get('required_operations') or [])!r}\n"
                f"ORIGIN = {ORIGIN_DIAGNOSTIC_NON_AI!r}\n"
                "PROMOTION_ALLOWED = False\n\n"
                "def build_fixture_matrix():\n"
                "    return {\"operations\": REQUIRED_OPERATIONS, \"origin\": ORIGIN}\n"
            ),
        },
        {
            "path": "README.md",
            "content": (
                "# Diagnostic non-AI scaffold\n\n"
                "This is not architect/coder output. Promotion is forbidden.\n"
            ),
        },
    ]


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
    empty_model_output = False
    thinking_present = False
    http_ok = True
    try:
        resp = _generate_content_for_fill(client, prompt)
        response_text, empty_model_output, thinking_present, http_ok = _visible_text_from_response(resp)
        if not http_ok:
            status = "error"
            error = "model_http_failed"
        elif empty_model_output:
            status = "empty_model_output"
            error = "empty_model_output"
            response_text = ""
    except Exception as exc:
        status = "error"
        error = f"{type(exc).__name__}:{exc}"
        response_text = ""
        empty_model_output = False
        http_ok = False
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
        "empty_model_output": empty_model_output,
        "thinking_present": thinking_present,
        "thinking_enabled": FILL_LOCAL_THINK_ENABLED,
        "http_ok": http_ok,
        "timestamp": started_at,
        "finished_at": _utc_now(),
        "validator_summary": validator_summary or {},
        "resolved_source": cfg.get("_resolved_source"),
    }
    _append_jsonl(job_dir / "model_call_evidence.jsonl", evidence)
    if status == "empty_model_output":
        raise CapabilityAiFillError(
            "empty_model_output",
            f"{role} HTTP succeeded but official text is empty",
            details={k: evidence[k] for k in evidence if k not in ("prompt_sha256",)},
        )
    if status != "ok":
        raise CapabilityAiFillError(
            "model_call_failed",
            f"{role} call failed: {error}",
            details={k: evidence[k] for k in evidence if k not in ("prompt_sha256",)},
        )
    return {"text": response_text, "evidence": evidence}


def _official_architecture_brief() -> dict[str, Any]:
    domains: dict[str, Any] = {}
    for key in list_registered_domains():
        spec = get_domain_spec(key)
        if spec is None:
            continue
        domains[key] = {
            "domain_module": spec.domain_module,
            "entrypoint": spec.entrypoint,
            "operations": list(spec.allowed_operations),
        }
    return {
        "matrix_required_fields": official_matrix_fields(),
        "allowed_official_file_prefixes": list(ALLOWED_OFFICIAL_TARGETS),
        "registered_domains": domains,
        "rules": [
            "skill_id must match the requested skill exactly",
            "reuse an existing domain_key; never invent a new domain or registry format",
            "operations must already exist or be proposed only as a patch to domain_operation_registry.py",
            "candidate files must be mutations of official runtime-read paths plus focused tests and coverage_matrix",
            "do not emit standalone helpers, unused YAML/JSON, placeholders, or pending mappings",
        ],
    }


def _architect_prompt(preflight: dict[str, Any], briefs: list[dict[str, Any]], *, skill_id: str) -> str:
    example_ids = [int(b.get("textbook_example_id") or 0) for b in briefs if int(b.get("textbook_example_id") or 0)]
    return (
        "你是系統角色 architect。請把缺口接到現有 Gencode V3 正式架構，禁止新建獨立 domain。\n"
        "只輸出 JSON（勿 markdown），必填欄位：\n"
        "skill_id (必須與請求完全一致),\n"
        "domain_key (必須是已註冊 domain),\n"
        "domain_module, entrypoint,\n"
        "required_operations (現有 operations 或 registry_operation_proposals),\n"
        "registry_operation_proposals (list，可空),\n"
        "matrix_required_fields (必須等於官方 MATRIX_REQUIRED_FIELDS),\n"
        "answer_schema (object: operation -> schema_key),\n"
        "checker (object: operation -> checker_key),\n"
        "example_coverage (list of {textbook_example_id, operation, answer_contract{checker_key, answer_type, answer_schema_key}}),\n"
        "allowed_official_files (list，只能是正式 runtime／test 路徑),\n"
        "regression_guards (list，至少一個既有 verified skill_id),\n"
        "missing_layers, isomorphism_groups, candidate_plan, constraints.\n"
        "硬限制：不得要求寫入 DB／tracker／production；只規劃隔離 candidate 的正式檔案 patch。\n"
        "禁止自創 registry YAML 格式、runtime 未讀取的 mapping table、獨立 helper engine。\n\n"
        f"requested_skill_id={json.dumps(skill_id, ensure_ascii=False)}\n"
        f"required_example_ids={json.dumps(example_ids)}\n"
        f"official_architecture={json.dumps(_official_architecture_brief(), ensure_ascii=False)}\n"
        f"preflight={json.dumps(preflight, ensure_ascii=False)}\n"
        f"examples={json.dumps(briefs, ensure_ascii=False)}"
    )


def _coder_prompt(spec: dict[str, Any], *, round_no: int, validation: dict[str, Any] | None) -> str:
    repair = ""
    if round_no > 1 and validation:
        repair = f"\n上一輪 validator 失敗：{json.dumps(validation, ensure_ascii=False)}\n請改成正式檔案 mutation proposal。\n"
    return (
        "你是系統角色 coder。請輸出對現有正式檔案的 mutation proposal，不要寫獨立 helper。\n"
        "只輸出 JSON：{\n"
        '  "skill_id": "<exact skill_id>",\n'
        '  "files": [ {"path": "relative/path", "target": "official/repo/path", '
        '"mutation": "upsert_skill_binding|add_focused_tests|patch_existing_file", "content": "..."} ],\n'
        '  "coverage_matrix": [ {"textbook_example_id": 0, "operation": "...", '
        '"answer_contract": {"checker_key": "...", "answer_type": "...", "answer_schema_key": "..."}} ],\n'
        '  "notes": "..."\n'
        "}\n"
        "target 必須是正式 runtime 會讀的檔，或 tests/gencode/ focused tests，"
        "或 candidate_contract/coverage_matrix.json。\n"
        "必須包含：taxonomy／registry 接線 patch、focused tests、12題 coverage_matrix。\n"
        "禁止：獨立 calculator/engine、未載入 YAML/JSON、placeholder、pending、錯誤 skill_id、錯誤 source id。\n"
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
    if cand_root.exists():
        shutil.rmtree(cand_root)
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


def validate_candidate_workspace(
    job_dir: Path,
    spec: dict[str, Any],
    *,
    skill_id: str = "",
    example_ids: list[int] | None = None,
) -> dict[str, Any]:
    """Official compatibility validator — compile-only trees cannot pass."""
    skill_key = str(skill_id or spec.get("skill_id") or "").strip()
    ids = list(example_ids or [])
    compatibility = validate_official_compatibility(
        job_dir,
        spec,
        skill_id=skill_key,
        example_ids=ids,
    )
    result = {
        "passed": bool(compatibility.get("passed")),
        "blockers": list(compatibility.get("blockers") or []),
        "file_count": compatibility.get("file_count"),
        "files": compatibility.get("files") or [],
        "checked_at": _utc_now(),
        "gate": "official_compatibility",
        "runtime_mutation_count": compatibility.get("runtime_mutation_count"),
        "focused_test_count": compatibility.get("focused_test_count"),
    }
    if not result["passed"] and BLOCK_INCOMPATIBLE not in result["blockers"]:
        result["blockers"] = [BLOCK_INCOMPATIBLE, *result["blockers"]]
        result["block_reason"] = BLOCK_INCOMPATIBLE
    elif not result["passed"]:
        result["block_reason"] = BLOCK_INCOMPATIBLE
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
            "block_reason": blocked.code,
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
    example_ids = [
        int(b.get("textbook_example_id") or 0)
        for b in briefs
        if int(b.get("textbook_example_id") or 0)
    ]

    try:
        _update_job(job_dir, status=STATE_ARCHITECT)
        arch = _call_role(
            role="architect",
            prompt=_architect_prompt(preflight, briefs, skill_id=skill_key),
            job_dir=job_dir,
            client_factory=factory,
        )
        spec = _extract_json_object(arch["text"])
        spec_blockers = validate_architect_spec(spec, skill_id=skill_key, example_ids=example_ids)
        if spec_blockers:
            raise CapabilityAiFillError(
                "architect_invalid_spec",
                "architect output is not a valid capability spec",
                details={"blockers": spec_blockers},
            )
        spec["skill_id"] = skill_key
        spec["origin"] = ORIGIN_ARCHITECT
        spec["ai_generated"] = True
        spec["promotion_allowed"] = False
        _write_json(job_dir / "capability_spec.json", spec)
        _update_job(job_dir, spec_origin=ORIGIN_ARCHITECT, architect_evidence_ok=True)

        # Round 1 coder + validate
        _update_job(job_dir, status=STATE_CODER_1)
        coder1 = _call_role(
            role="coder",
            prompt=_coder_prompt(spec, round_no=1, validation=None),
            job_dir=job_dir,
            client_factory=factory,
        )
        payload1 = _extract_json_object(coder1["text"])
        files1, coder_blockers = parse_coder_contract(payload1, skill_id=skill_key)
        if coder_blockers:
            raise CapabilityAiFillError(
                "coder_invalid_contract",
                "coder output is not a valid candidate contract",
                details={"blockers": coder_blockers, "round": 1},
            )
        written = _write_candidate_files(job_dir, files1)
        _write_json(
            job_dir / "candidate_manifest.json",
            {
                "round": 1,
                "files": written,
                "mutations": [
                    {"path": item.get("path"), "target": item.get("target"), "mutation": item.get("mutation")}
                    for item in files1
                ],
                "notes": payload1.get("notes"),
                "origin": ORIGIN_CODER,
                "ai_generated": True,
                "promotion_allowed": False,
            },
        )
        _update_job(job_dir, candidate_origin=ORIGIN_CODER, status=STATE_VALIDATE_1)
        validation1 = validate_candidate_workspace(
            job_dir, spec, skill_id=skill_key, example_ids=example_ids
        )
        if validation1.get("passed"):
            _assert_awaiting_allowed(
                spec=spec,
                spec_origin=ORIGIN_ARCHITECT,
                candidate_origin=ORIGIN_CODER,
                architect_ok=True,
                coder_ok=True,
                validator_passed=True,
            )
            job = _update_job(
                job_dir,
                status=STATE_AWAITING,
                validation_passed=True,
                official_compatibility_passed=True,
                coder_rounds_used=1,
                ai_output_valid=True,
                spec_origin=ORIGIN_ARCHITECT,
                candidate_origin=ORIGIN_CODER,
                block_reason="",
                promotion_allowed=False,
            )
            return {
                "ok": True,
                "reused": False,
                "job_id": job_id,
                "status": STATE_AWAITING,
                "job_dir": str(job_dir),
                "gap_fingerprint": fingerprint,
                "skill_id": skill_key,
                "coder_rounds_used": 1,
                "ai_output_valid": True,
                "spec_origin": ORIGIN_ARCHITECT,
                "candidate_origin": ORIGIN_CODER,
                "preflight": preflight,
            }

        # Round 2 (one repair only) — only when round-1 contract was valid
        _update_job(job_dir, status=STATE_CODER_2)
        coder2 = _call_role(
            role="coder",
            prompt=_coder_prompt(spec, round_no=2, validation=validation1),
            job_dir=job_dir,
            client_factory=factory,
            validator_summary={"round": 1, "passed": False, "blockers": validation1.get("blockers")},
        )
        payload2 = _extract_json_object(coder2["text"])
        files2, coder_blockers2 = parse_coder_contract(payload2, skill_id=skill_key)
        if coder_blockers2:
            raise CapabilityAiFillError(
                "coder_invalid_contract",
                "coder repair output is not a valid candidate contract",
                details={"blockers": coder_blockers2, "round": 2},
            )
        written2 = _write_candidate_files(job_dir, files2)
        _write_json(
            job_dir / "candidate_manifest.json",
            {
                "round": 2,
                "files": written2,
                "mutations": [
                    {"path": item.get("path"), "target": item.get("target"), "mutation": item.get("mutation")}
                    for item in files2
                ],
                "notes": payload2.get("notes"),
                "origin": ORIGIN_CODER,
                "ai_generated": True,
                "promotion_allowed": False,
            },
        )

        _update_job(job_dir, status=STATE_VALIDATE_2)
        validation2 = validate_candidate_workspace(
            job_dir, spec, skill_id=skill_key, example_ids=example_ids
        )
        if validation2.get("passed"):
            _assert_awaiting_allowed(
                spec=spec,
                spec_origin=ORIGIN_ARCHITECT,
                candidate_origin=ORIGIN_CODER,
                architect_ok=True,
                coder_ok=True,
                validator_passed=True,
            )
            job = _update_job(
                job_dir,
                status=STATE_AWAITING,
                validation_passed=True,
                official_compatibility_passed=True,
                coder_rounds_used=2,
                ai_output_valid=True,
                spec_origin=ORIGIN_ARCHITECT,
                candidate_origin=ORIGIN_CODER,
                block_reason="",
                promotion_allowed=False,
            )
            return {
                "ok": True,
                "reused": False,
                "job_id": job_id,
                "status": STATE_AWAITING,
                "job_dir": str(job_dir),
                "gap_fingerprint": fingerprint,
                "skill_id": skill_key,
                "coder_rounds_used": 2,
                "ai_output_valid": True,
                "spec_origin": ORIGIN_ARCHITECT,
                "candidate_origin": ORIGIN_CODER,
                "preflight": preflight,
            }

        fail_reason = BLOCK_INCOMPATIBLE if BLOCK_INCOMPATIBLE in (validation2.get("blockers") or []) else "validator_failed_after_repair"
        job = _update_job(
            job_dir,
            status=STATE_BLOCKED,
            validation_passed=False,
            official_compatibility_passed=False,
            block_reason=fail_reason,
            error_message="validator failed after one coder repair",
            coder_rounds_used=2,
            last_validation=validation2,
            ai_output_valid=False,
            promotion_allowed=False,
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
            "error": fail_reason,
            "block_reason": fail_reason,
            "message": "validator failed after one coder repair",
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
            ai_output_valid=False,
            promotion_allowed=False,
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
            "block_reason": exc.code,
            "message": str(exc),
            "preflight": preflight,
        }
    except Exception as exc:
        _update_job(
            job_dir,
            status=STATE_BLOCKED,
            block_reason="unexpected_error",
            error_message=f"{type(exc).__name__}:{exc}",
            ai_output_valid=False,
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
            "block_reason": "unexpected_error",
            "message": str(exc),
            "preflight": preflight,
        }


# Explicit guard for tests / greps: this module must not reference resolve_gencode_ai_client.
FORBIDDEN_GENCODE_AI_RESOLVE = "resolve_gencode_ai_client"
