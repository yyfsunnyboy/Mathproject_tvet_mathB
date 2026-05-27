from __future__ import annotations

import argparse
import json
import sys
from importlib import import_module
from pathlib import Path
from typing import Any
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"

from core.gencode.pipeline_state import read_json, utc_timestamp, write_json


def _runtime_probe(skill_id: str) -> dict[str, Any]:
    try:
        mod = import_module(f"skills.{skill_id}")
        q = mod.generate(level=1)
        answer = str(q.get("answer", ""))
        check_result = mod.check(answer, str(q.get("correct_answer", answer)))
        return {
            "import_ok": True,
            "generate_ok": isinstance(q, dict),
            "check_ok": isinstance(check_result, dict) and bool(check_result.get("correct")),
            "sample_problem_type": str(q.get("problem_type_id", "")),
        }
    except Exception as e:
        return {"import_ok": False, "generate_ok": False, "check_ok": False, "error": str(e), "sample_problem_type": ""}


def _format_list(xs: list[Any]) -> str:
    return "-" if not xs else ", ".join(str(x) for x in xs)


def _registry_candidates() -> list[Path]:
    base = PROJECT_ROOT / "configs" / "generated_registry"
    if not base.exists():
        return []
    out: list[Path] = []
    for pat in ["*.yaml", "*.yml", "*.json"]:
        out.extend(sorted(base.glob(pat)))
    return out


def _load_registry_obj(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    else:
        try:
            obj = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return obj if isinstance(obj, dict) else {}


def _find_skill_entry_in_registry(obj: dict[str, Any], skill_id: str) -> dict[str, Any]:
    if skill_id in obj and isinstance(obj[skill_id], dict):
        e = dict(obj[skill_id])
        e["skill_id"] = skill_id
        return e
    for key in ["skills", "bindings", "runtime_bindings", "verified_problem_types"]:
        rows = obj.get(key)
        if isinstance(rows, list):
            for it in rows:
                if isinstance(it, dict) and str(it.get("skill_id", "")).strip() == skill_id:
                    return it
    for v in obj.values():
        if isinstance(v, list):
            for it in v:
                if isinstance(it, dict) and str(it.get("skill_id", "")).strip() == skill_id:
                    return it
    return {}


def _discover_registry_binding(skill_id: str) -> dict[str, Any]:
    for path in _registry_candidates():
        obj = _load_registry_obj(path)
        if not obj:
            continue
        entry = _find_skill_entry_in_registry(obj, skill_id)
        if not entry:
            continue
        wrapper_path = str(entry.get("wrapper_path", "")).strip()
        vpts = entry.get("verified_problem_types")
        if not isinstance(vpts, list):
            vpts = []
        mre = entry.get("manual_review_exclusions")
        if mre is None:
            mre = []
        if not isinstance(mre, list):
            mre = []
        valid = bool(str(entry.get("skill_id", "")).strip() == skill_id and wrapper_path and vpts)
        return {
            "registry_path": str(path),
            "registry_entry_found": True,
            "registry_entry_valid": valid,
            "registry_binding_status": "BOUND" if valid else "INCOMPLETE",
            "registry_verified_problem_types": vpts,
            "registry_manual_review_exclusions": mre,
            "registry_binding_failure_reason": "" if valid else "registry_binding_incomplete",
        }
    return {
        "registry_path": "",
        "registry_entry_found": False,
        "registry_entry_valid": False,
        "registry_binding_status": "NOT_BOUND",
        "registry_verified_problem_types": [],
        "registry_manual_review_exclusions": [],
        "registry_binding_failure_reason": "registry_binding_missing",
    }


def _reason_zh_map(code: str) -> str:
    mapping = {
        "registry_binding_missing": "candidate 尚未 non-destructive merge 到 registry",
        "wrapper_binding_missing": "skill wrapper 尚未接上 verified candidates",
        "runtime_binding_missing": "學生 runtime 尚未能抽到 verified problem types",
        "runtime_coverage_failed": "runtime 題型覆蓋未通過",
        "candidate_verification_failed": "Phase 2 candidate 驗證未通過",
        "phase2_not_build_pass": "Phase 2 尚未 BUILD_PASS",
        "manual_review_present": "仍有人工審查題型，但不一定阻塞 deterministic runtime",
        "answer_contract_gate_failed": "answer_contract gate 未通過",
        "missing_checker_key_problem_types": "checker_key gate 未通過",
        "missing_phase_reports": "缺少 Phase 1/Phase 2 報告",
        "import_failed": "runtime 匯入失敗",
        "generate_failed": "runtime 生成失敗",
        "checker_failed": "runtime 檢查失敗",
        "unclear_legacy_failure_reason": "舊版錯誤原因不明，需人工確認",
    }
    return mapping.get(code, code)


def _write_md(path: Path, report: dict[str, Any]) -> None:
    rts = report.get("runtime_problem_type_coverage", {})
    pbs = report.get("publish_binding_summary", {})
    next_action = report.get("next_action", {})
    success_items = report.get("success_items", {})
    incomplete_items = report.get("incomplete_items", {})
    lines = [
        "# Gencode 第三階段發布門檻報告",
        "",
        "## 1. 摘要",
        f"- skill_id: {report.get('skill_id', '')}",
        f"- final_status: {report.get('final_status', '')}",
        f"- publish_ready: {str(bool(report.get('publish_ready', False))).lower()}",
        "",
        "## 2. 整體判讀",
        f"- 狀態說明: {report.get('status_message', '')}",
        f"- 是否可發布: {'是' if report.get('publish_ready') else '否'}",
        f"- 是否可進學生端 runtime: {'是' if pbs.get('runtime_binding_status') == 'READY' else '否'}",
        f"- 是否需要人工處理: {'是' if next_action.get('requires_human_review') else '否'}",
        "",
        "## 3. 成功項目",
        f"- Phase 1 例題盤點: {'完成' if success_items.get('phase1_coverage_ok') else '未完成'}",
        f"- Phase 2 candidate verification: {'完成' if success_items.get('phase2_candidate_verification_ok') else '未完成'}",
        f"- verified problem types: {_format_list(success_items.get('verified_problem_types', []))}",
        "",
        "## 4. 未完成 / 失敗項目",
        f"- registry binding: {'完成' if pbs.get('registry_binding_status') == 'BOUND' else '未完成'}",
        f"- wrapper binding: {'完成' if pbs.get('wrapper_binding_status') == 'BOUND' else '未完成'}",
        f"- runtime coverage: {'通過' if rts.get('status') == 'pass' else '未通過'}",
        f"- missing runtime problem types: {_format_list(rts.get('missing_problem_types', []))}",
        f"- blocking reasons: {_format_list(report.get('blocking_reasons', []))}",
        "",
        "## 5. 發布排除題型",
        f"- manual_review problem types: {_format_list((pbs.get('publish_exclusions') or {}).get('manual_review_problem_types', []))}",
        "  說明：manual_review 題型不應列入 deterministic runtime coverage。",
        f"- future_ai_judged problem types: {_format_list((pbs.get('publish_exclusions') or {}).get('future_ai_judged_problem_types', []))}",
        "",
        "## 6. Runtime Coverage",
        f"- expected_problem_types: {_format_list(rts.get('expected_problem_types', []))}",
        f"- observed_problem_types: {_format_list(rts.get('observed_problem_types', []))}",
        f"- missing_problem_types: {_format_list(rts.get('missing_problem_types', []))}",
        f"- coverage_status: {rts.get('status', '')}",
        "",
        "## 7. Registry / Wrapper / Runtime Binding 狀態",
        f"- registry_binding_status: {pbs.get('registry_binding_status', '')}",
        f"- wrapper_binding_status: {pbs.get('wrapper_binding_status', '')}",
        f"- runtime_binding_status: {pbs.get('runtime_binding_status', '')}",
        "",
        "## 8. 阻塞原因與說明",
    ]
    for x in report.get("blocking_reasons", []):
        lines.append(f"- {x}: {_reason_zh_map(str(x))}")
    if not report.get("blocking_reasons"):
        lines.append("- 無")
    lines += [
        "",
        "## 9. 下一步建議",
        f"- next_action_type: {next_action.get('next_action_type', '')}",
        f"- command: {next_action.get('command', '')}",
        f"- reason: {next_action.get('reason', '')}",
        f"- should_publish: {str(bool(next_action.get('should_publish', False))).lower()}",
        f"- requires_human_review: {str(bool(next_action.get('requires_human_review', False))).lower()}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_summary_stdout(report: dict[str, Any]) -> str:
    rts = report.get("runtime_problem_type_coverage", {})
    pbs = report.get("publish_binding_summary", {})
    next_action = report.get("next_action", {})
    success_items = report.get("success_items", {})
    lines = [
        "============================================================",
        "Gencode 第三階段發布門檻摘要",
        "============================================================",
        f"skill_id: {report.get('skill_id', '')}",
        f"階段狀態: {report.get('final_status', '')}",
        f"publish_ready: {str(bool(report.get('publish_ready', False))).lower()}",
        "",
        "一、整體判讀",
        f"- 狀態說明: {report.get('status_message', '')}",
        f"- 是否可發布: {'是' if report.get('publish_ready') else '否'}",
        f"- 是否可進學生端 runtime: {'是' if pbs.get('runtime_binding_status') == 'READY' else '否'}",
        f"- 是否需要人工處理: {'是' if next_action.get('requires_human_review') else '否'}",
        "",
        "二、成功項目",
        f"- Phase 1 例題盤點: {'完成' if success_items.get('phase1_coverage_ok') else '未完成'}",
        f"- Phase 2 candidate verification: {'完成' if success_items.get('phase2_candidate_verification_ok') else '未完成'}",
        "- verified problem types:",
    ]
    for i, x in enumerate(success_items.get("verified_problem_types", []), 1):
        lines.append(f"  {i}. {x}")
    if not success_items.get("verified_problem_types", []):
        lines.append("  -")
    lines += [
        "",
        "三、未完成 / 失敗項目",
        f"- registry binding: {'完成' if pbs.get('registry_binding_status') == 'BOUND' else '未完成'}",
        f"- wrapper binding: {'完成' if pbs.get('wrapper_binding_status') == 'BOUND' else '未完成'}",
        f"- runtime coverage: {'通過' if rts.get('status') == 'pass' else '未通過'}",
        f"- missing runtime problem types: {_format_list(rts.get('missing_problem_types', []))}",
        f"- blocking reasons: {_format_list(report.get('blocking_reasons', []))}",
        "",
        "四、發布排除題型",
        f"- manual_review problem types: {_format_list((pbs.get('publish_exclusions') or {}).get('manual_review_problem_types', []))}",
        "  說明：manual_review 題型不應列入 deterministic runtime coverage。",
        f"- future_ai_judged problem types: {_format_list((pbs.get('publish_exclusions') or {}).get('future_ai_judged_problem_types', []))}",
        "",
        "五、Runtime Coverage",
        f"- expected_problem_types: {_format_list(rts.get('expected_problem_types', []))}",
        f"- observed_problem_types: {_format_list(rts.get('observed_problem_types', []))}",
        f"- missing_problem_types: {_format_list(rts.get('missing_problem_types', []))}",
        f"- coverage_status: {rts.get('status', '')}",
        "",
        "六、Binding 狀態",
        f"- registry_binding_status: {pbs.get('registry_binding_status', '')}",
        f"- registry_path: {pbs.get('registry_path', '')}",
        f"- registry_entry_found: {str(bool(pbs.get('registry_entry_found', False))).lower()}",
        f"- registry_entry_valid: {str(bool(pbs.get('registry_entry_valid', False))).lower()}",
        f"- wrapper_binding_status: {pbs.get('wrapper_binding_status', '')}",
        f"- runtime_binding_status: {pbs.get('runtime_binding_status', '')}",
        "",
        "七、下一步建議",
        f"- 建議動作: {next_action.get('next_action_type', '')}",
        "- 指令:",
        f"  {next_action.get('command', '') or '-'}",
        "============================================================",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    skill_id = args.skill_id

    phase1_path = REPORT_DIR / f"{skill_id}_phase1_audit.json"
    phase2_path = REPORT_DIR / f"{skill_id}_phase2_build.json"
    out_json = REPORT_DIR / f"{skill_id}_pipeline_final.json"
    out_md = REPORT_DIR / f"{skill_id}_pipeline_final.md"

    p1 = read_json(phase1_path)
    p2 = read_json(phase2_path)
    if not p1 or not p2:
        report = {
            "skill_id": skill_id,
            "phase": "phase3_publish_gate",
            "final_status": "FAIL",
            "publish_ready": False,
            "blocking_reasons": ["missing_phase_reports"],
            "warnings": [],
            "publish_binding_summary": {
                "candidate_verification_status": "FAIL",
                "verified_candidates_count": 0,
                "verified_problem_types": [],
                "registry_binding_status": "UNKNOWN",
                "wrapper_binding_status": "UNKNOWN",
                "runtime_binding_status": "UNKNOWN",
                "binding_required": True,
                "binding_blockers": ["missing_phase_reports"],
                "publish_exclusions": {"manual_review_problem_types": [], "future_ai_judged_problem_types": []},
            },
            "next_action": {
                "next_action_type": "rerun_or_fix_phase2",
                "command": f"python scripts\\gencode_pipeline_phase2_build.py --skill-id {skill_id}",
                "reason": "Phase 報告不足，請先完成 Phase 1/2。",
                "should_publish": False,
                "requires_human_review": True,
            },
            "artifact_paths": {"phase1_json": str(phase1_path), "phase2_json": str(phase2_path), "final_json": str(out_json), "final_md": str(out_md)},
            "timestamp": utc_timestamp(),
        }
        write_json(out_json, report)
        _write_md(out_md, report)
        print(json.dumps(report, ensure_ascii=True) if args.json else _build_summary_stdout(report))
        return

    runtime = _runtime_probe(skill_id)
    phase2_final_status = str(p2.get("final_status", "")).strip()
    phase2_exec = str((p2.get("build_execution_summary") or {}).get("execution_status", "")).strip()
    verified_problem_types = list(p2.get("verified_problem_types") or [])
    pending_implementation = list(p2.get("pending_implementation") or [])
    observed_problem_types = list(p1.get("observed_problem_types") or [])
    manual_review_problem_types = list(p1.get("manual_review_problem_types") or [])
    future_ai_judged_problem_types = list(p1.get("future_ai_judged_problem_types") or [])
    missing_answer_contract_problem_types = list(p1.get("missing_answer_contract_problem_types") or [])
    missing_checker_key_problem_types = list(p1.get("missing_checker_key_problem_types") or [])
    source_coverage_status = str(p1.get("source_coverage_status", "INSUFFICIENT_SOURCE_EXAMPLES"))
    deterministic_expected = sorted([x for x in observed_problem_types if x not in set(manual_review_problem_types) and x not in set(future_ai_judged_problem_types)])

    registry_merge = p2.get("registry_merge_summary") or {}
    wrapper_summary = p2.get("wrapper_summary") or {}
    reg_detect = _discover_registry_binding(skill_id)
    registry_binding_status = str(reg_detect.get("registry_binding_status", "NOT_BOUND"))
    wrapper_binding_status = "BOUND"
    if str(wrapper_summary.get("pipeline_final_status", "")).strip() in {"SKIPPED_CANDIDATE_VERIFICATION_MODE", ""}:
        wrapper_binding_status = "NOT_BOUND"

    runtime_observed = sorted(set(verified_problem_types or [runtime.get("sample_problem_type", "")]) - {""})
    runtime_missing = sorted(set(deterministic_expected) - set(runtime_observed))
    runtime_coverage_status = "pass" if not runtime_missing else "fail"
    runtime_binding_status = "READY" if runtime.get("import_ok") and runtime.get("generate_ok") and runtime.get("check_ok") and runtime_coverage_status == "pass" else "NOT_READY"

    candidate_verification_status = "PASS" if (phase2_final_status == "BUILD_PASS" or phase2_exec == "PASS") and bool(verified_problem_types) else "FAIL"

    blocking_reasons: list[str] = []
    warnings: list[str] = []
    if candidate_verification_status != "PASS":
        blocking_reasons.append("candidate_verification_failed")
    if phase2_final_status != "BUILD_PASS":
        blocking_reasons.append("phase2_not_build_pass")
    if registry_binding_status == "INCOMPLETE":
        blocking_reasons.append("registry_binding_incomplete")
    elif registry_binding_status != "BOUND":
        blocking_reasons.append("registry_binding_missing")
    if wrapper_binding_status != "BOUND":
        blocking_reasons.append("wrapper_binding_missing")
    if runtime_binding_status != "READY":
        blocking_reasons.append("runtime_binding_missing")
    if runtime_coverage_status != "pass":
        blocking_reasons.append("runtime_coverage_failed")
    if missing_answer_contract_problem_types:
        blocking_reasons.append("answer_contract_gate_failed")
    if missing_checker_key_problem_types:
        blocking_reasons.append("missing_checker_key_problem_types")
    if manual_review_problem_types:
        warnings.append("manual_review_present")

    legacy = [x for x in list(p2.get("blocking_reasons") or []) if str(x) in {"import_failed", "generate_failed", "checker_failed"}]
    if legacy and not (runtime.get("error") or runtime_missing):
        warnings.append("unclear_legacy_failure_reason")

    final_status = "PUBLISH_BINDING_REQUIRED"
    publish_ready = False
    if candidate_verification_status == "PASS" and registry_binding_status == "BOUND" and wrapper_binding_status == "BOUND" and runtime_binding_status == "READY":
        final_status = "PASS"
        publish_ready = True
    bootstrap_summary = dict(p2.get("bootstrap_summary") or p1.get("bootstrap_summary") or {})
    if bool(bootstrap_summary.get("bootstrap_mode")) and str(bootstrap_summary.get("bootstrap_runtime_status", "FAIL")) == "PASS" and not publish_ready:
        final_status = "PASS_BOOTSTRAP_ONLY"
        publish_ready = True

    if final_status == "PASS":
        next_action = {
            "next_action_type": "ready_for_publish_review",
            "command": "",
            "reason": "可進人工發布審核。",
            "should_publish": True,
            "requires_human_review": bool(manual_review_problem_types),
        }
    elif final_status == "PASS_BOOTSTRAP_ONLY":
        next_action = {
            "next_action_type": "bootstrap_publish_review",
            "command": "",
            "reason": "可上線，但需標示 bootstrap-only。",
            "should_publish": True,
            "requires_human_review": True,
        }
    elif candidate_verification_status == "PASS":
        next_action = {
            "next_action_type": "repair_publish_binding",
            "command": f"python scripts\\gencode_repair_build_gap.py --skill-id {skill_id} --gap missing_runtime_binding",
            "reason": "candidate 已驗證，但 registry / wrapper / runtime 尚未接線。",
            "should_publish": False,
            "requires_human_review": bool(manual_review_problem_types),
        }
    else:
        next_action = {
            "next_action_type": "rerun_or_fix_phase2",
            "command": f"python scripts\\gencode_pipeline_phase2_build.py --skill-id {skill_id}",
            "reason": "Phase 2 尚未 BUILD_PASS 或 candidate 驗證未通過。",
            "should_publish": False,
            "requires_human_review": bool(manual_review_problem_types),
        }

    runtime_problem_type_coverage = {
        "expected_problem_types": deterministic_expected,
        "observed_problem_types": runtime_observed,
        "missing_problem_types": runtime_missing,
        "status": runtime_coverage_status,
    }
    publish_binding_summary = {
        "candidate_verification_status": candidate_verification_status,
        "verified_candidates_count": len(verified_problem_types),
        "verified_problem_types": verified_problem_types,
        "registry_binding_status": registry_binding_status,
        "registry_path": reg_detect.get("registry_path", ""),
        "registry_entry_found": bool(reg_detect.get("registry_entry_found", False)),
        "registry_entry_valid": bool(reg_detect.get("registry_entry_valid", False)),
        "registry_verified_problem_types": reg_detect.get("registry_verified_problem_types", []),
        "registry_manual_review_exclusions": reg_detect.get("registry_manual_review_exclusions", []),
        "registry_binding_failure_reason": reg_detect.get("registry_binding_failure_reason", ""),
        "wrapper_binding_status": wrapper_binding_status,
        "runtime_binding_status": runtime_binding_status,
        "binding_required": final_status == "PUBLISH_BINDING_REQUIRED",
        "binding_blockers": sorted(set([x for x in blocking_reasons if x in {"registry_binding_missing", "wrapper_binding_missing", "runtime_binding_missing", "runtime_coverage_failed"}])),
        "publish_exclusions": {
            "manual_review_problem_types": manual_review_problem_types,
            "future_ai_judged_problem_types": future_ai_judged_problem_types,
        },
    }

    success_items = {
        "phase1_coverage_ok": int(p1.get("examples_covered", 0)) == int(p1.get("examples_total", 0)),
        "phase2_candidate_verification_ok": candidate_verification_status == "PASS",
        "verified_problem_types": verified_problem_types,
        "answer_contract_gate_ok": not missing_answer_contract_problem_types,
        "checker_key_gate_ok": not missing_checker_key_problem_types,
    }
    incomplete_items = {
        "registry_binding_done": registry_binding_status == "BOUND",
        "wrapper_binding_done": wrapper_binding_status == "BOUND",
        "runtime_binding_ready": runtime_binding_status == "READY",
        "runtime_coverage_pass": runtime_coverage_status == "pass",
    }

    report = {
        "skill_id": skill_id,
        "phase": "phase3_publish_gate",
        "final_status": final_status,
        "publish_ready": publish_ready,
        "full_observed_coverage": runtime_coverage_status == "pass",
        "source_coverage_status": source_coverage_status,
        "bootstrap_summary": bootstrap_summary,
        "examples_total": p1.get("examples_total", 0),
        "examples_covered": p1.get("examples_covered", 0),
        "observed_problem_types": observed_problem_types,
        "verified_problem_types": verified_problem_types,
        "pending_implementation": pending_implementation,
        "manual_review_problem_types": manual_review_problem_types,
        "future_ai_judged_problem_types": future_ai_judged_problem_types,
        "answer_contract_summary": p1.get("answer_contract_summary", {}),
        "missing_answer_contract_problem_types": missing_answer_contract_problem_types,
        "missing_checker_key_problem_types": missing_checker_key_problem_types,
        "equivalence_test_required_problem_types": list(p1.get("equivalence_test_required_problem_types") or []),
        "runtime_problem_type_coverage": runtime_problem_type_coverage,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "warnings": sorted(set(warnings)),
        "publish_binding_summary": publish_binding_summary,
        "next_action": next_action,
        "success_items": success_items,
        "incomplete_items": incomplete_items,
        "status_message": "candidate 驗證、binding 與 runtime coverage 綜合判讀結果。",
        "artifact_paths": {"phase1_json": str(phase1_path), "phase2_json": str(phase2_path), "final_json": str(out_json), "final_md": str(out_md)},
        "timestamp": utc_timestamp(),
    }
    write_json(out_json, report)
    _write_md(out_md, report)
    print(json.dumps(report, ensure_ascii=True) if args.json else _build_summary_stdout(report))


if __name__ == "__main__":
    main()
