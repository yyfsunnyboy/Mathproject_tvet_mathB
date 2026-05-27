from __future__ import annotations

import argparse
import json
import sys
from importlib import import_module
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"

from core.gencode.build_gap_analyzer import analyze_build_dependency_plan, analyze_build_gaps
from core.gencode.candidate_discovery import discover_generator_candidates, verify_generator_candidate
from core.gencode.pipeline_state import determine_next_repair_action, read_json, utc_timestamp, write_json
from core.gencode.repair_catalog import GENERATOR_REPAIR_CATALOG


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
    return "-" if not xs else ", ".join(str(x) for x in xs)


def _run_candidate_build_execution(skill_id: str, p1: dict[str, Any], dep: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], list[str], list[str], list[str], list[str]]:
    answer_contract_summary = p1.get("answer_contract_summary", {}) if isinstance(p1.get("answer_contract_summary"), dict) else {}
    buildable_pts = list(dep.get("buildable_problem_types", []) or [])
    discovery = discover_generator_candidates(skill_id, buildable_pts, GENERATOR_REPAIR_CATALOG)
    verified_candidates: list[str] = []
    failed_candidates: list[str] = []
    candidate_failure_reasons: dict[str, list[str]] = {}
    sample_total = 0

    for item in discovery.get("discovered_candidates", []):
        if not isinstance(item, dict):
            continue
        pt = str(item.get("problem_type_id", "")).strip()
        module_path = str(item.get("module_path", "")).strip()
        res = verify_generator_candidate(module_path, skill_id, pt, answer_contract_summary.get(pt, {}), sample_count=10)
        sample_total += int(res.get("sample_count", 0))
        if bool(res.get("ok")):
            verified_candidates.append(pt)
        else:
            failed_candidates.append(pt)
            candidate_failure_reasons[pt] = list(res.get("failure_reasons", []) or [])

    for item in discovery.get("missing_candidate_files", []):
        if isinstance(item, dict):
            pt = str(item.get("problem_type_id", "")).strip()
            if pt:
                failed_candidates.append(pt)
                candidate_failure_reasons.setdefault(pt, []).append("candidate_file_missing")

    for pt in discovery.get("unsupported_candidate_problem_types", []):
        p = str(pt).strip()
        if p:
            failed_candidates.append(p)
            candidate_failure_reasons.setdefault(p, []).append("unsupported_candidate_problem_type")

    verified_set = sorted(set(verified_candidates))
    failed_set = sorted(set(failed_candidates))
    pending = sorted([pt for pt in buildable_pts if pt not in set(verified_set) and pt not in set(failed_set)])
    failure_reasons_flat = sorted({r for rs in candidate_failure_reasons.values() for r in rs})
    execution_status = "PASS" if len(verified_set) == len(buildable_pts) and not failed_set and not pending else ("FAIL" if not verified_set and failed_set else "PARTIAL")

    candidate_discovery_summary = {
        "discovered_candidates": discovery.get("discovered_candidates", []),
        "missing_candidate_files": discovery.get("missing_candidate_files", []),
        "unsupported_candidate_problem_types": discovery.get("unsupported_candidate_problem_types", []),
        "verified_candidates": verified_set,
        "failed_candidates": failed_set,
        "candidate_failure_reasons": candidate_failure_reasons,
        "sample_count": sample_total,
    }
    build_execution_summary = {
        "execution_attempted": True,
        "execution_status": execution_status,
        "verified_problem_types": verified_set,
        "failed_problem_types": failed_set,
        "pending_problem_types": pending,
        "failure_reasons": failure_reasons_flat,
    }

    blocking_reasons: list[str] = []
    warnings: list[str] = []
    if verified_set and (discovery.get("unsupported_candidate_problem_types") or discovery.get("missing_candidate_files")):
        blocking_reasons.append("candidate_verified_but_not_registered")
        warnings.append("candidate 已通過，但尚未完成 registry/wrapper binding。")
    if failed_set:
        blocking_reasons.append("wrapper_missing_candidate_binding")

    return candidate_discovery_summary, build_execution_summary, verified_set, failed_set, pending, blocking_reasons + warnings


def _build_stdout_summary(report: dict[str, Any]) -> str:
    next_action = report.get("next_action") or {}
    cds = report.get("candidate_discovery_summary") or {}
    bes = report.get("build_execution_summary") or {}
    lines = [
        "============================================================",
        "Gencode Phase 2 Build 摘要",
        "============================================================",
        f"skill_id: {report.get('skill_id', '')}",
        f"最終狀態: {report.get('final_status', '')}",
        f"Preflight 狀態: {report.get('preflight_status', '')}",
        f"Build 執行狀態: {report.get('build_execution_status', '')}",
        "",
        "Build Dependency Plan:",
        f"- foundation_ready: {str((report.get('build_dependency_plan') or {}).get('foundation_ready', False)).lower()}",
        f"- buildable_problem_types: {_format_list((report.get('build_dependency_plan') or {}).get('buildable_problem_types', []))}",
        f"- excluded_manual_review_problem_types: {_format_list((report.get('build_dependency_plan') or {}).get('excluded_manual_review_problem_types', []))}",
        f"- missing_checkers: {_format_list((report.get('build_dependency_plan') or {}).get('missing_checkers', []))}",
        f"- missing_verifiers: {_format_list((report.get('build_dependency_plan') or {}).get('missing_verifiers', []))}",
        f"- missing_domain_functions: {_format_list((report.get('build_dependency_plan') or {}).get('missing_domain_functions', []))}",
        f"- missing_generators: {_format_list((report.get('build_dependency_plan') or {}).get('missing_generators', []))}",
        "",
        "Candidate Discovery:",
        f"- discovered_candidates: {_format_list([x.get('problem_type_id') for x in (cds.get('discovered_candidates') or []) if isinstance(x, dict)])}",
        f"- verified_candidates: {_format_list(cds.get('verified_candidates', []))}",
        f"- failed_candidates: {_format_list(cds.get('failed_candidates', []))}",
        f"- missing_candidate_files: {_format_list([x.get('problem_type_id') for x in (cds.get('missing_candidate_files') or []) if isinstance(x, dict)])}",
        f"- unsupported_candidate_problem_types: {_format_list(cds.get('unsupported_candidate_problem_types', []))}",
        "",
        "Build Execution:",
        f"- execution_status: {bes.get('execution_status', '')}",
        f"- verified_problem_types: {_format_list(bes.get('verified_problem_types', []))}",
        f"- failed_problem_types: {_format_list(bes.get('failed_problem_types', []))}",
        f"- failure_reasons: {_format_list(bes.get('failure_reasons', []))}",
        "",
        "下一步建議:",
        f"- 類型: {next_action.get('next_action_type', '')}",
        f"- 缺口: {next_action.get('gap', '-') or '-'}",
        f"- 原因: {next_action.get('reason', '')}",
    ]
    cmd = str(next_action.get("command", "")).strip()
    if cmd:
        lines.extend(["- 指令:", f"  {cmd}"])
    lines.append(f"- should_run_phase3: {str(bool(next_action.get('should_run_phase3', False))).lower()}")
    if not bool(next_action.get("should_run_phase3", False)):
        lines.append("不要跑 Phase 3。")
    lines.append("============================================================")
    return "\n".join(lines)


def _write_phase2_markdown(path: Path, report: dict[str, Any]) -> None:
    dep = report.get("build_dependency_plan") or {}
    gap = report.get("build_gap_summary") or {}
    pt_gaps = gap.get("problem_type_gaps") or {}
    next_action = report.get("next_action") or {}
    cds = report.get("candidate_discovery_summary") or {}
    bes = report.get("build_execution_summary") or {}
    lines = [
        "# Gencode Phase 2 Build Report",
        "",
        "## 1. Overview",
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
        "## 4.1 Candidate Discovery",
        f"- discovered_candidates: {_format_list([x.get('problem_type_id') for x in (cds.get('discovered_candidates') or []) if isinstance(x, dict)])}",
        f"- missing_candidate_files: {_format_list([x.get('problem_type_id') for x in (cds.get('missing_candidate_files') or []) if isinstance(x, dict)])}",
        f"- unsupported_candidate_problem_types: {_format_list(cds.get('unsupported_candidate_problem_types', []))}",
        f"- verified_candidates: {_format_list(cds.get('verified_candidates', []))}",
        f"- failed_candidates: {_format_list(cds.get('failed_candidates', []))}",
        f"- sample_count: {cds.get('sample_count', 0)}",
        "",
        "## 4.2 Build Execution Summary",
        f"- execution_attempted: {str(bool(bes.get('execution_attempted', False))).lower()}",
        f"- execution_status: {bes.get('execution_status', '')}",
        f"- verified_problem_types: {_format_list(bes.get('verified_problem_types', []))}",
        f"- failed_problem_types: {_format_list(bes.get('failed_problem_types', []))}",
        f"- pending_problem_types: {_format_list(bes.get('pending_problem_types', []))}",
        f"- failure_reasons: {_format_list(bes.get('failure_reasons', []))}",
        "",
        "## 5. Build Gap Summary",
        f"- has_build_gaps: {str(gap.get('has_build_gaps', False)).lower()}",
        f"- gap_types: {_format_list(gap.get('gap_types', []))}",
        "",
        "## 6. Problem Type Gaps",
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
        lines.append("| - | - | - | - | - |")
    lines += [
        "",
        "## 下一步建議",
        f"- next_action_type: {next_action.get('next_action_type', '')}",
        f"- gap: {next_action.get('gap', '')}",
        f"- reason: {next_action.get('reason', '')}",
        f"- command: {next_action.get('command', '')}",
        f"- should_run_phase3: {str(bool(next_action.get('should_run_phase3', False))).lower()}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_base_report(skill_id: str, phase1_path: Path, out_json: Path, out_md: Path, p1: dict[str, Any]) -> dict[str, Any]:
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
            "candidate_discovery_summary": {
                "discovered_candidates": [],
                "missing_candidate_files": [],
                "unsupported_candidate_problem_types": [],
                "verified_candidates": [],
                "failed_candidates": [],
                "candidate_failure_reasons": {},
                "sample_count": 0,
            },
            "build_execution_summary": {
                "execution_attempted": False,
                "execution_status": "SKIPPED",
                "verified_problem_types": [],
                "failed_problem_types": [],
                "pending_problem_types": [],
                "failure_reasons": [],
            },
        }
        gap = analyze_build_gaps({}, report)
        report["build_gap_summary"] = gap.get("build_gap_summary", {})
        report["repair_plan"] = gap.get("repair_plan", {})
        report["repair_plan_status"] = "FAILED"
        return report

    build_mode = "bootstrap" if bool((p1.get("bootstrap_summary") or {}).get("bootstrap_mode")) else "normal"
    dep = analyze_build_dependency_plan(
        p1,
        {"answer_contract_summary": p1.get("answer_contract_summary", {}), "manual_review_problem_types": p1.get("manual_review_problem_types", [])},
    )
    preflight_status = dep.get("preflight_status", "REPAIR_REQUIRED")
    build_execution_status = "SKIPPED"
    final_status = "FOUNDATION_REPAIR_REQUIRED"
    verified_problem_types: list[str] = []
    failed_problem_types: list[str] = []
    pending_implementation: list[str] = []
    checker_implementation_summary: dict[str, Any] = {"missing_checker_key_problem_types": []}
    registry_merge_summary: dict[str, Any] = {"mode": "non_destructive", "updated": False}
    wrapper_summary: dict[str, Any] = {}
    bootstrap_summary: dict[str, Any] = dict(p1.get("bootstrap_summary") or {})
    blocking_reasons: list[str] = []
    warnings: list[str] = []
    candidate_discovery_summary = {
        "discovered_candidates": [],
        "missing_candidate_files": [],
        "unsupported_candidate_problem_types": [],
        "verified_candidates": [],
        "failed_candidates": [],
        "candidate_failure_reasons": {},
        "sample_count": 0,
    }
    build_execution_summary = {
        "execution_attempted": False,
        "execution_status": "SKIPPED",
        "verified_problem_types": [],
        "failed_problem_types": [],
        "pending_problem_types": [],
        "failure_reasons": [],
    }

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
            build_execution_summary = {
                "execution_attempted": True,
                "execution_status": "PASS" if probe["ok"] else "FAIL",
                "verified_problem_types": list(probe.get("sample_problem_types", [])),
                "failed_problem_types": [] if probe["ok"] else ["bootstrap_wrapper"],
                "pending_problem_types": [],
                "failure_reasons": [] if probe["ok"] else [str(probe.get("error", ""))],
            }
            if not probe["ok"]:
                blocking_reasons.append("bootstrap_wrapper_probe_failed")
                failed_problem_types = ["bootstrap_wrapper"]
        else:
            candidate_discovery_summary, build_execution_summary, verified_problem_types, failed_problem_types, pending_implementation, extras = _run_candidate_build_execution(skill_id, p1, dep)
            for x in extras:
                if x == "candidate_verified_but_not_registered" or x == "wrapper_missing_candidate_binding":
                    blocking_reasons.append(x)
                else:
                    warnings.append(x)
            wrapper_summary = {
                "pipeline_invoked": False,
                "pipeline_return_code": 0,
                "pipeline_final_status": "SKIPPED_CANDIDATE_VERIFICATION_MODE",
            }
            if build_execution_summary["execution_status"] == "PASS":
                final_status = "BUILD_PASS"
            elif build_execution_summary["execution_status"] == "PARTIAL":
                final_status = "BUILD_PARTIAL"
            else:
                final_status = "BUILD_FAIL"
    else:
        blocking_reasons.append("foundation_missing_components")

    report = {
        "skill_id": skill_id,
        "phase": "phase2_build",
        "final_status": final_status,
        "input_phase1_report": str(phase1_path),
        "build_mode": build_mode,
        "generated_problem_types": verified_problem_types,
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
        "candidate_discovery_summary": candidate_discovery_summary,
        "build_execution_summary": build_execution_summary,
    }

    gap = analyze_build_gaps(p1, report)
    report["build_gap_summary"] = gap.get("build_gap_summary", {})
    report["repair_plan"] = gap.get("repair_plan", {})
    report["repair_plan_status"] = gap.get("repair_plan_status", "SKIPPED")

    return report


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
    report = _build_base_report(skill_id, phase1_path, out_json, out_md, p1)
    report["next_action"] = determine_next_repair_action(report)

    write_json(out_json, report)
    _write_phase2_markdown(out_md, report)
    print(json.dumps(report, ensure_ascii=True) if args.json else _build_stdout_summary(report))


if __name__ == "__main__":
    main()
