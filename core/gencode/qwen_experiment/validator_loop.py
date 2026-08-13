# -*- coding: utf-8 -*-
"""Validation loop for isolated Qwen-generated generate.py (reuses project validators)."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import traceback
from pathlib import Path
from typing import Any, Callable

from core.gencode.domain_bootstrap.execution_policy import ExecutionPolicy
from core.gencode.qwen_experiment.constants import VALIDATION_SEEDS
from core.gencode.qwen_experiment.extract import scan_dangerous_code
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.services.v3_question_integrity_validator import validate_component_payload
from core.gencode.services.v3_variation_audit_service import extract_parameter_signature

# Isolation note: ExecutionPolicy asserts path boundary and disables subprocess by default.
# It does NOT provide full OS sandbox / memory cgroup. We refuse to expand privileges here.


def _load_generate_module(generate_path: Path, policy: ExecutionPolicy) -> Any:
    policy.assert_path_allowed(generate_path)
    mod_name = f"qwen_exp_{hashlib.sha256(str(generate_path).encode()).hexdigest()[:12]}"
    spec = importlib.util.spec_from_file_location(mod_name, generate_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module_load_failed:{generate_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _wrong_answer(correct: Any) -> Any:
    if isinstance(correct, (int, float)):
        return correct + 99991
    text = str(correct or "").strip()
    if not text:
        return "__QWEN_EXP_WRONG__"
    return text + "_WRONG"


def validate_generated_component(
    *,
    generate_path: Path,
    component_id: str,
    skill_id: str,
    workspace_root: Path,
    seeds: tuple[int, ...] | None = None,
    primary_seed: int | None = None,
    generate_runner: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Run static + runtime validation without writing tracker/production.

    Returns structured result suitable for repair prompts (no hidden oracle answers).
    """
    policy = ExecutionPolicy(workspace_root=workspace_root, allow_subprocess=False, timeout_seconds=5.0)
    blockers: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}
    failure_layer = ""

    code = generate_path.read_text(encoding="utf-8")
    danger = scan_dangerous_code(code)
    checks["dangerous_scan"] = {"passed": not danger, "blockers": danger}
    if danger:
        return {
            "passed": False,
            "failure_layer": "dangerous_code",
            "blockers": danger,
            "warnings": warnings,
            "checks": checks,
            "variation_status": "not_run",
        }

    try:
        ast.parse(code)
        checks["ast_parse"] = True
    except SyntaxError as exc:
        return {
            "passed": False,
            "failure_layer": "ast",
            "blockers": [f"syntax_error:{exc.msg}"],
            "warnings": warnings,
            "checks": checks,
            "variation_status": "not_run",
        }

    if "import subprocess" in code or "os.system" in code:
        # Belt-and-suspenders beyond AST.
        blockers.append("dangerous_literal_detected")

    try:
        module = _load_generate_module(generate_path, policy)
        generate_fn = getattr(module, "generate", None)
        if not callable(generate_fn):
            raise RuntimeError("missing_generate_function")
        hint_fn = getattr(module, "get_hint", None)
        checks["import_load"] = True
    except Exception as exc:
        return {
            "passed": False,
            "failure_layer": "import",
            "blockers": [f"import_failed:{exc}"],
            "warnings": warnings,
            "checks": checks,
            "variation_status": "not_run",
        }

    sample_seeds = list(seeds or VALIDATION_SEEDS)
    if primary_seed is not None and int(primary_seed) not in sample_seeds:
        sample_seeds = [int(primary_seed), *sample_seeds]
    sample_seeds = sample_seeds[:5]

    payloads: list[dict[str, Any]] = []
    integrity_failures: list[str] = []
    checker_failures: list[str] = []
    signatures: list[str] = []
    question_texts: list[str] = []

    for seed in sample_seeds:
        try:
            if generate_runner is not None:
                payload = generate_runner(seed=seed, component_id=component_id)
            else:
                payload = policy.run_callable(
                    generate_fn,
                    level=1,
                    seed=int(seed),
                    component_id=component_id,
                )
            if not isinstance(payload, dict):
                raise RuntimeError("generate_did_not_return_dict")
        except Exception as exc:
            integrity_failures.append(f"generate_failed:seed={seed}:{exc}")
            failure_layer = failure_layer or "runtime_generate"
            continue

        payload = dict(payload)
        payload.setdefault("component_id", component_id)
        payload.setdefault("skill_id", skill_id)
        payload.setdefault("seed", seed)
        payloads.append({"seed": seed, "has_question": bool(str(payload.get("question_text") or "").strip())})

        integrity = validate_component_payload(payload, component_id=component_id)
        if not integrity.get("passed"):
            for b in integrity.get("blockers") or []:
                integrity_failures.append(f"seed={seed}:{b}")
            failure_layer = failure_layer or "payload_validator"

        qtext = str(payload.get("question_text") or "").strip()
        question_texts.append(qtext)
        try:
            signatures.append(extract_parameter_signature(payload))
        except Exception:
            signatures.append(hashlib.sha256(qtext.encode("utf-8")).hexdigest()[:16])

        correct = payload.get("answer", payload.get("correct_answer"))
        try:
            ok = bool(
                check_answer(
                    correct,
                    correct,
                    payload=payload,
                    skill_id=skill_id,
                )
            )
            if not ok:
                checker_failures.append(f"checker_reject_correct:seed={seed}")
                failure_layer = failure_layer or "checker_accept"
        except Exception as exc:
            checker_failures.append(f"checker_correct_error:seed={seed}:{exc}")
            failure_layer = failure_layer or "checker_accept"

        try:
            bad = _wrong_answer(correct)
            bad_ok = bool(
                check_answer(
                    bad,
                    correct,
                    payload=payload,
                    skill_id=skill_id,
                )
            )
            if bad_ok:
                checker_failures.append(f"checker_accept_wrong:seed={seed}")
                failure_layer = failure_layer or "checker_reject"
        except Exception as exc:
            # Reject path may raise for some checkers; treat as reject-success if not True.
            warnings.append(f"checker_wrong_path_exception:seed={seed}:{type(exc).__name__}")

        if callable(hint_fn):
            try:
                hint = str(hint_fn(1, payload) or "")
                if not hint.strip():
                    warnings.append(f"empty_hint:seed={seed}")
            except Exception as exc:
                warnings.append(f"hint_error:seed={seed}:{exc}")
        else:
            warnings.append("get_hint_missing")

        # metadata presence
        meta = payload.get("metadata")
        if not isinstance(meta, dict):
            integrity_failures.append(f"seed={seed}:missing_metadata")
            failure_layer = failure_layer or "metadata"
        else:
            for key in ("givens", "target", "derivation"):
                if key not in meta:
                    integrity_failures.append(f"seed={seed}:missing_metadata_{key}")
                    failure_layer = failure_layer or "metadata"

    checks["multi_seed"] = {
        "seeds": sample_seeds,
        "generated_count": len(payloads),
        "integrity_failure_count": len(integrity_failures),
        "checker_failure_count": len(checker_failures),
    }
    # Do NOT embed full payloads / answers into repair-facing structure.
    checks["sample_summary"] = payloads

    unique_sigs = sorted(set(signatures))
    unique_texts = sorted({t for t in question_texts if t})
    if len(payloads) >= 2 and len(unique_sigs) <= 1 and len(unique_texts) <= 1:
        variation_status = "static"
        blockers.append("variation_static_across_seeds")
        failure_layer = failure_layer or "variation"
    elif len(payloads) >= 2 and (len(unique_sigs) > 1 or len(unique_texts) > 1):
        variation_status = "dynamic"
    elif len(payloads) == 1:
        variation_status = "single_sample"
        warnings.append("variation_insufficient_samples")
    else:
        variation_status = "failed"
        failure_layer = failure_layer or "runtime_generate"

    blockers.extend(integrity_failures)
    blockers.extend(checker_failures)
    blockers = list(dict.fromkeys(blockers))
    passed = len(blockers) == 0 and len(payloads) > 0
    if passed and not failure_layer:
        failure_layer = ""
    elif not passed and not failure_layer:
        failure_layer = "validation"

    return {
        "passed": passed,
        "failure_layer": failure_layer if not passed else "",
        "blockers": blockers,
        "warnings": list(dict.fromkeys(warnings)),
        "checks": checks,
        "variation_status": variation_status,
        "rounds_trace": traceback.format_exc() if False else "",  # placeholder kept empty
    }
