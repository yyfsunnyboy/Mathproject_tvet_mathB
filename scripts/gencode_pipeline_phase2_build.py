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

from core.gencode.build_gap_analyzer import analyze_build_dependency_plan, analyze_build_gaps
from core.gencode.pipeline_state import read_json, utc_timestamp, write_json


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


def _format_list(xs: list[Any]) -> str:
    return "無" if not xs else ", ".join(str(x) for x in xs)


def _build_stdout_summary(report: dict[str, Any]) -> str:
    skill_id = str(report.get("skill_id", ""))
    lines = [
        "============================================================",
        "Gencode 第二階段建置摘要",
        "============================================================",
        f"skill_id: {skill_id}",
        f"階段狀態: {report.get('final_status', '')}",
        f"Preflight 狀態: {report.get('preflight_status', '')}",
        f"Build 執行狀態: {report.get('build_execution_status', '')}",
        "",
        "建置依賴規劃:",
        f"- foundation_ready: {str((report.get('build_dependency_plan') or {}).get('foundation_ready', False)).lower()}",
        f"- buildable_problem_types: {_format_list((report.get('build_dependency_plan') or {}).get('buildable_problem_types', []))}",
        f"- excluded_manual_review_problem_types: {_format_list((report.get('build_dependency_plan') or {}).get('excluded_manual_review_problem_types', []))}",
        f"- missing_checkers: {_format_list((report.get('build_dependency_plan') or {}).get('missing_checkers', []))}",
        f"- missing_verifiers: {_format_list((report.get('build_dependency_plan') or {}).get('missing_verifiers', []))}",
        f"- missing_domain_functions: {_format_list((report.get('build_dependency_plan') or {}).get('missing_domain_functions', []))}",
        f"- missing_generators: {_format_list((report.get('build_dependency_plan') or {}).get('missing_generators', []))}",
        "",
        "建置缺口分析:",
        f"- has_build_gaps: {str((report.get('build_gap_summary') or {}).get('has_build_gaps', False)).lower()}",
        f"- 主要缺口: {_format_list((report.get('build_gap_summary') or {}).get('gap_types', []))}",
        "",
        "建議修復順序:",
    ]
    for step in (report.get("repair_plan") or {}).get("steps", []):
        lines.append(f"- {step.get('step_id')}: {step.get('title')}")
    lines += [
        "",
        "判讀說明:",
    ]
    if report.get("build_execution_status") == "SKIPPED":
        lines.append("Phase 2 尚未進入 generator build。")
        lines.append("目前已完成建置規劃，但缺少 foundation 元件，因此需要先執行 repair plan。")
        lines.append("這不是 classifier 失敗，也不是 runtime 發布失敗。")
    else:
        lines.append("Phase 2 已執行 build。")
    lines += [
        "",
        "下一步建議:",
        f"執行 repair：python scripts\\gencode_repair_build_gap.py --skill-id {skill_id} --gap missing_checker",
        "不要跑 Phase 3。",
        "============================================================",
    ]
    return "\n".join(lines)


def _write_phase2_markdown(path: Path, report: dict[str, Any]) -> None:
    dep = report.get("build_dependency_plan") or {}
    gap = report.get("build_gap_summary") or {}
    pt_gaps = gap.get("problem_type_gaps") or {}
    lines = [
        "# Gencode 第二階段建置報告",
        "",
        "## 1. 摘要",
        f"- skill_id: {report.get('skill_id', '')}",
        f"- final_status: {report.get('final_status', '')}",
        f"- build_mode: {report.get('build_mode', '')}",
        f"- input_phase1_report: {report.get('input_phase1_report', '')}",
        "",
        "## 2. Build Dependency Plan",
        f"- foundation_ready: {str(dep.get('foundation_ready', False)).lower()}",
        f"- required_checkers: {_format_list(dep.get('required_checkers', []))}",
        f"- missing_checkers: {_format_list(dep.get('missing_checkers', []))}",
        f"- required_verifiers: {_format_list(dep.get('required_verifiers', []))}",
        f"- missing_verifiers: {_format_list(dep.get('missing_verifiers', []))}",
        f"- required_domain_functions: {_format_list(dep.get('required_domain_functions', []))}",
        f"- missing_domain_functions: {_format_list(dep.get('missing_domain_functions', []))}",
        f"- required_generators: {_format_list(dep.get('required_generators', []))}",
        f"- missing_generators: {_format_list(dep.get('missing_generators', []))}",
        f"- excluded_manual_review_problem_types: {_format_list(dep.get('excluded_manual_review_problem_types', []))}",
        "",
        "## 3. Preflight Result",
        f"- preflight_status: {report.get('preflight_status', '')}",
        "",
        "## 4. Build Execution Status",
        f"- build_execution_status: {report.get('build_execution_status', '')}",
        "",
        "## 8. 建置缺口分析",
        f"- has_build_gaps: {str(gap.get('has_build_gaps', False)).lower()}",
        f"- gap_types: {_format_list(gap.get('gap_types', []))}",
        "",
        "## 9. 修復計畫",
        "",
        "| problem_type_id | gap_types | recommended_components | suggested_next_actions | severity |",
        "| --- | --- | --- | --- | --- |",
    ]
    for pt in sorted(pt_gaps.keys()):
        g = pt_gaps[pt]
        lines.append(
            f"| {pt} | {_format_list(g.get('gap_types', []))} | {_format_list(g.get('recommended_components', []))} | {_format_list(g.get('suggested_next_actions', []))} | {g.get('severity', '')} |"
        )
    if not pt_gaps:
        lines.append("| 無 | 無 | 無 | 無 | 無 |")
    if report.get("build_execution_status") == "SKIPPED":
        lines += ["", "本輪未執行 generator build，因 foundation 缺口尚未修復。"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--json", action="store_true")
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
            "preflight_status": "FAIL",
            "build_execution_status": "FAILED",
            "build_dependency_plan": {},
        }
        gap = analyze_build_gaps({}, report)
        report["build_gap_summary"] = gap.get("build_gap_summary", {})
        report["repair_plan"] = gap.get("repair_plan", {})
        report["repair_plan_status"] = "FAILED"
        write_json(out_json, report)
        _write_phase2_markdown(out_md, report)
        print(json.dumps(report, ensure_ascii=True) if args.json else _build_stdout_summary(report))
        return

    build_mode = "bootstrap" if bool((p1.get("bootstrap_summary") or {}).get("bootstrap_mode")) else "normal"
    dep = analyze_build_dependency_plan(p1, {"answer_contract_summary": p1.get("answer_contract_summary", {}), "manual_review_problem_types": p1.get("manual_review_problem_types", [])})

    preflight_status = dep.get("preflight_status", "REPAIR_REQUIRED")
    build_execution_status = "SKIPPED"
    final_status = "FOUNDATION_REPAIR_REQUIRED"
    generated_problem_types: list[str] = []
    verified_problem_types: list[str] = []
    failed_problem_types: list[str] = []
    pending_implementation: list[str] = []
    checker_implementation_summary: dict[str, Any] = {"missing_checker_key_problem_types": []}
    registry_merge_summary: dict[str, Any] = {"mode": "non_destructive", "updated": False}
    wrapper_summary: dict[str, Any] = {}
    bootstrap_summary: dict[str, Any] = dict(p1.get("bootstrap_summary") or {})
    blocking_reasons: list[str] = []
    warnings: list[str] = []

    if preflight_status == "PASS":
        build_execution_status = "EXECUTED"
        if build_mode == "bootstrap":
            probe = _probe_bootstrap_wrapper(skill_id)
            wrapper_summary = {
                "wrapper_import_ok": probe["ok"],
                "wrapper_generate_ok": probe["ok"],
                "wrapper_check_ok": probe["ok"],
                "sample_problem_types": probe["sample_problem_types"],
                "error": probe["error"],
            }
            bootstrap_summary["bootstrap_runtime_status"] = "PASS" if probe["ok"] else "FAIL"
            final_status = "BUILD_BOOTSTRAP_PASS" if probe["ok"] else "BUILD_FAIL"
            if not probe["ok"]:
                blocking_reasons.append("bootstrap_wrapper_probe_failed")
                build_execution_status = "FAILED"
        else:
            cmd = [sys.executable, "scripts/run_skill_gencode_pipeline.py", "--skill-id", skill_id, "--max-rounds", "5"]
            code, parsed, stdout, stderr = _run_json_cmd(cmd, timeout=1800)
            generated_problem_types = list(parsed.get("verified_problem_types") or [])
            verified_problem_types = list(parsed.get("verified_problem_types") or [])
            pending_implementation = list(parsed.get("pending_implementation") or [])
            failed_problem_types = list(parsed.get("failed_problem_types") or [])
            blocking_reasons.extend(list(parsed.get("blocking_reasons") or []))
            wrapper_summary = {"pipeline_invoked": True, "pipeline_return_code": code, "pipeline_final_status": parsed.get("final_status", "")}
            checker_implementation_summary = {"missing_checker_key_problem_types": ((parsed.get("semantic_audit_summary") or {}).get("missing_checker_key_problem_types") or [])}
            if code != 0 or not parsed:
                blocking_reasons.append("pipeline_run_failed")
                warnings.append(stderr.strip() or stdout.strip())
                final_status = "BUILD_FAIL"
                build_execution_status = "FAILED"
            elif parsed.get("final_status") == "PASS":
                final_status = "BUILD_PASS"
            elif parsed.get("final_status") in {"PARTIAL", "PASS_BOOTSTRAP_ONLY"}:
                final_status = "BUILD_PARTIAL"
            else:
                final_status = "BUILD_FAIL"
                build_execution_status = "FAILED"
    else:
        final_status = "FOUNDATION_REPAIR_REQUIRED"
        blocking_reasons.append("foundation_missing_components")

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
        "manual_review_problem_types": list(p1.get("manual_review_problem_types") or []),
        "future_ai_judged_problem_types": list(p1.get("future_ai_judged_problem_types") or []),
        "checker_implementation_summary": checker_implementation_summary,
        "answer_contract_summary": p1.get("answer_contract_summary", {}),
        "registry_merge_summary": registry_merge_summary,
        "wrapper_summary": wrapper_summary,
        "bootstrap_summary": bootstrap_summary,
        "blocking_reasons": sorted(set([x for x in blocking_reasons if x])),
        "warnings": sorted(set([x for x in warnings if x])),
        "artifact_paths": {"phase2_json": str(out_json), "phase2_md": str(out_md)},
        "timestamp": utc_timestamp(),
        "build_dependency_plan": dep,
        "preflight_status": preflight_status,
        "build_execution_status": build_execution_status,
    }

    gap = analyze_build_gaps(p1, report)
    report["build_gap_summary"] = gap.get("build_gap_summary", {})
    report["repair_plan"] = gap.get("repair_plan", {})
    report["repair_plan_status"] = gap.get("repair_plan_status", "SKIPPED")

    if preflight_status == "PASS" and build_execution_status == "SKIPPED":
        report["final_status"] = "BUILD_PLAN_READY"
    elif report["final_status"] == "FOUNDATION_REPAIR_REQUIRED" and preflight_status == "REPAIR_REQUIRED":
        report["build_execution_status"] = "SKIPPED"

    write_json(out_json, report)
    _write_phase2_markdown(out_md, report)
    print(json.dumps(report, ensure_ascii=True) if args.json else _build_stdout_summary(report))


if __name__ == "__main__":
    main()

