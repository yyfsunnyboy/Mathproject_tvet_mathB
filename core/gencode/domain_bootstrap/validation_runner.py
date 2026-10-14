# -*- coding: utf-8 -*-
"""Candidate domain validation gates."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

from core.gencode.domain_bootstrap.candidate_store import CandidateStore
from core.gencode.domain_bootstrap.execution_policy import ExecutionPolicy, py_compile_in_workspace
from core.gencode.domain_bootstrap.models import DomainGapReport

FORBIDDEN_LITERAL_PATTERNS = (
    re.compile(r"vh_[\w\u4e00-\u9fff]+"),
    re.compile(r"src_\d{{4,}}"),
)


def _load_module_from_path(module_name: str, file_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module_load_failed:{file_path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _scan_for_forbidden_literals(workspace: Path) -> list[str]:
    blockers: list[str] = []
    for path in workspace.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_LITERAL_PATTERNS:
            if pattern.search(text):
                blockers.append(f"forbidden_literal:{pattern.pattern}:{path.name}")
    return blockers


def validate_candidate_domain(
    *,
    store: CandidateStore,
    gap_report: DomainGapReport,
    policy: ExecutionPolicy | None = None,
) -> dict[str, Any]:
    gap_id = gap_report.gap_id
    workspace = store.candidate_dir(gap_id)
    blockers: list[str] = []
    checks: dict[str, bool] = {}

    if policy is None:
        policy = ExecutionPolicy(workspace_root=workspace)

    manifest_path = workspace / "domain_manifest.json"
    domain_path = workspace / "domain_module.py"
    oracle_path = workspace / "oracle.py"

    if not manifest_path.is_file():
        blockers.append("manifest_missing")
    if not domain_path.is_file():
        blockers.append("domain_module_missing")
    if not oracle_path.is_file():
        blockers.append("oracle_missing")

    if blockers:
        return {"passed": False, "blockers": blockers, "checks": checks}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks["manifest_schema"] = bool(manifest.get("domain_key") and manifest.get("entrypoint"))

    try:
        py_compile_in_workspace(policy, domain_path)
        py_compile_in_workspace(policy, oracle_path)
        checks["py_compile"] = True
    except Exception as exc:
        blockers.append(f"py_compile_failed:{exc}")
        checks["py_compile"] = False

    blockers.extend(_scan_for_forbidden_literals(workspace))
    checks["no_skill_example_literals"] = not any("forbidden_literal" in b for b in blockers)

    domain_mod = _load_module_from_path(f"candidate_domain_{gap_id}", domain_path)
    oracle_mod = _load_module_from_path(f"candidate_oracle_{gap_id}", oracle_path)
    build_fn = getattr(domain_mod, str(manifest.get("entrypoint") or ""), None)
    oracle_fn = getattr(oracle_mod, "oracle_verify_matrix", None)
    if not callable(build_fn):
        blockers.append("operation_not_callable")
    if not callable(oracle_fn):
        blockers.append("oracle_not_callable")

    operation_keys = [str(key).strip() for key in (manifest.get("operations") or [])]
    if not operation_keys or any(not key for key in operation_keys):
        blockers.append("operations_missing")
    elif len(operation_keys) != len(set(operation_keys)):
        blockers.append("operations_duplicate")
    seed_results: list[dict[str, Any]] = []
    if callable(build_fn) and callable(oracle_fn):
        for operation_key in operation_keys:
            for seed in (7, 42, 101):
                try:
                    matrix = build_fn(seed=seed, domain_operation=operation_key, constraints={"values": [1, 2, 3]})
                    if matrix.get("domain_operation") != operation_key:
                        blockers.append(f"operation_identity_mismatch:{operation_key}:seed_{seed}")
                    ok, oracle_blockers = oracle_fn(matrix)
                    seed_results.append({"operation": operation_key, "seed": seed, "passed": ok, "blockers": oracle_blockers})
                    if not ok:
                        blockers.extend([f"oracle_failed:{operation_key}:seed_{seed}:{b}" for b in oracle_blockers])
                except Exception as exc:
                    blockers.append(f"operation_execution_failed:{operation_key}:seed_{seed}:{exc}")

            try:
                seed42 = build_fn(seed=42, domain_operation=operation_key, constraints={"values": [4, 6]})
                seed42b = build_fn(seed=42, domain_operation=operation_key, constraints={"values": [4, 6]})
                reproducible = seed42 == seed42b
                checks[f"seed_reproducible:{operation_key}"] = reproducible
                if not reproducible:
                    blockers.append(f"seed_not_reproducible:{operation_key}")

                varied = build_fn(seed=99, domain_operation=operation_key, constraints={"values": [9, 2, 1]})
                varied_enough = (
                    varied.get("answer") != seed42.get("answer")
                    or varied.get("question_text") != seed42.get("question_text")
                )
                checks[f"seed_variation:{operation_key}"] = varied_enough
                if not varied_enough:
                    blockers.append(f"seed_variation_missing:{operation_key}")
            except Exception as exc:
                blockers.append(f"operation_validation_failed:{operation_key}:{exc}")

    capabilities = list(manifest.get("capabilities") or [])
    required = set(gap_report.missing_capabilities or gap_report.required_capabilities or [])
    covered = required.issubset(set(capabilities))
    checks["capability_coverage"] = covered
    if not covered:
        blockers.append("capability_coverage_missing")

    checks["generator_not_oracle"] = domain_mod.__file__ != oracle_mod.__file__
    if not checks["generator_not_oracle"]:
        blockers.append("generator_oracle_not_separated")

    passed = len(blockers) == 0
    return {
        "passed": passed,
        "blockers": list(dict.fromkeys(blockers)),
        "checks": checks,
        "seed_results": seed_results,
        "artifact_hash": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    }
