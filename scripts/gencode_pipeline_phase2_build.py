from __future__ import annotations

import argparse
import json
import subprocess
import sys
from importlib import import_module
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"

from core.gencode.pipeline_state import read_json, utc_timestamp, write_json, write_md


def _run_json_cmd(cmd: list[str], timeout: int = 1200) -> tuple[int, dict[str, Any], str, str]:
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=timeout)
    parsed: dict[str, Any] = {}
    for ln in reversed([x.strip() for x in proc.stdout.splitlines() if x.strip()]):
        try:
            j = json.loads(ln)
        except Exception:
            continue
        if isinstance(j, dict):
            parsed = j
            break
    return proc.returncode, parsed, proc.stdout, proc.stderr


def _probe_bootstrap_wrapper(skill_id: str) -> dict[str, Any]:
    try:
        mod = import_module(f"skills.{skill_id}")
        q1 = mod.generate(level=1)
        q2 = mod.generate(level=2)
        check_ok = isinstance(mod.check(str(q1.get("answer", "")), str(q1.get("correct_answer", ""))), dict)
        ok = isinstance(q1, dict) and isinstance(q2, dict) and check_ok
        return {"ok": ok, "error": "", "sample_problem_types": [q1.get("problem_type_id"), q2.get("problem_type_id")]}
    except Exception as e:
        return {"ok": False, "error": str(e), "sample_problem_types": []}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-id", required=True)
    args = parser.parse_args()
    skill_id = args.skill_id

    phase1_path = REPORT_DIR / f"{skill_id}_phase1_audit.json"
    out_json = REPORT_DIR / f"{skill_id}_phase2_build.json"
    out_md = REPORT_DIR / f"{skill_id}_phase2_build.md"

    p1 = read_json(phase1_path)
    if not p1:
        report = {
            "skill_id": skill_id,
            "phase": "phase2_build",
            "final_status": "BUILD_FAIL",
            "build_mode": "audit_blocked",
            "input_phase1_report": str(phase1_path),
            "blocking_reasons": ["missing_phase1_report"],
            "warnings": [],
            "artifact_paths": {"phase2_json": str(out_json), "phase2_md": str(out_md)},
            "timestamp": utc_timestamp(),
        }
        write_json(out_json, report)
        write_md(out_md, f"Phase2 Build: {skill_id}", [("summary", report)])
        print(json.dumps(report, ensure_ascii=True))
        return

    bootstrap_mode = bool((p1.get("bootstrap_summary") or {}).get("bootstrap_mode"))
    build_mode = "bootstrap" if bootstrap_mode else "normal"

    generated_problem_types: list[str] = []
    verified_problem_types: list[str] = []
    failed_problem_types: list[str] = []
    pending_implementation: list[str] = []
    manual_review_problem_types = list(p1.get("manual_review_problem_types") or [])
    future_ai_judged_problem_types = list(p1.get("future_ai_judged_problem_types") or [])
    checker_implementation_summary: dict[str, Any] = {}
    registry_merge_summary: dict[str, Any] = {"mode": "non_destructive", "updated": False}
    wrapper_summary: dict[str, Any] = {}
    bootstrap_summary: dict[str, Any] = dict(p1.get("bootstrap_summary") or {})
    blocking_reasons: list[str] = []
    warnings: list[str] = []

    if bootstrap_mode:
        probe = _probe_bootstrap_wrapper(skill_id)
        wrapper_summary = {
            "wrapper_import_ok": probe["ok"],
            "wrapper_generate_ok": probe["ok"],
            "wrapper_check_ok": probe["ok"],
            "sample_problem_types": probe["sample_problem_types"],
            "error": probe["error"],
        }
        bootstrap_summary["bootstrap_runtime_status"] = "PASS" if probe["ok"] else "FAIL"
        if not probe["ok"]:
            blocking_reasons.append("bootstrap_wrapper_probe_failed")
        final_status = "BUILD_BOOTSTRAP_PASS" if probe["ok"] else "BUILD_FAIL"
    else:
        cmd = [sys.executable, "scripts/run_skill_gencode_pipeline.py", "--skill-id", skill_id, "--max-rounds", "5"]
        code, parsed, stdout, stderr = _run_json_cmd(cmd, timeout=1800)
        generated_problem_types = list(parsed.get("verified_problem_types") or [])
        verified_problem_types = list(parsed.get("verified_problem_types") or [])
        pending_implementation = list(parsed.get("pending_implementation") or [])
        failed_problem_types = list(parsed.get("failed_problem_types") or [])
        blocking_reasons.extend(list(parsed.get("blocking_reasons") or []))
        wrapper_summary = {
            "pipeline_invoked": True,
            "pipeline_return_code": code,
            "pipeline_final_status": parsed.get("final_status", ""),
        }
        checker_implementation_summary = {
            "missing_checker_key_problem_types": ((parsed.get("semantic_audit_summary") or {}).get("missing_checker_key_problem_types") or []),
        }
        if code != 0 or not parsed:
            blocking_reasons.append("pipeline_run_failed")
            warnings.append(stderr.strip() or stdout.strip())
            final_status = "BUILD_FAIL"
        elif parsed.get("final_status") == "PASS":
            final_status = "BUILD_PASS"
        elif parsed.get("final_status") in {"PARTIAL", "PASS_BOOTSTRAP_ONLY"}:
            final_status = "BUILD_PARTIAL"
        else:
            final_status = "BUILD_FAIL"

    report = {
        "skill_id": skill_id,
        "phase": "phase2_build",
        "final_status": final_status,
        "input_phase1_report": str(phase1_path),
        "build_mode": build_mode,
        "generated_problem_types": generated_problem_types,
        "verified_problem_types": verified_problem_types,
        "failed_problem_types": failed_problem_types,
        "pending_implementation": pending_implementation,
        "manual_review_problem_types": manual_review_problem_types,
        "future_ai_judged_problem_types": future_ai_judged_problem_types,
        "checker_implementation_summary": checker_implementation_summary,
        "answer_contract_summary": p1.get("answer_contract_summary", {}),
        "registry_merge_summary": registry_merge_summary,
        "wrapper_summary": wrapper_summary,
        "bootstrap_summary": bootstrap_summary,
        "blocking_reasons": sorted(set([x for x in blocking_reasons if x])),
        "warnings": sorted(set([x for x in warnings if x])),
        "artifact_paths": {"phase2_json": str(out_json), "phase2_md": str(out_md)},
        "timestamp": utc_timestamp(),
    }
    write_json(out_json, report)
    write_md(out_md, f"Phase2 Build: {skill_id}", [("summary", report)])
    print(json.dumps(report, ensure_ascii=True))


if __name__ == "__main__":
    main()
