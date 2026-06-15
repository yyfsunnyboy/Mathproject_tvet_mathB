from __future__ import annotations

import argparse
import ast
import json
import py_compile
import sys
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"
DRAFT_DIR = REPORT_DIR / "drafts"

from core.gencode.pipeline_state import read_json, utc_timestamp, write_json

_STALE_DRAFT_MARKERS = (
    "expression_write_line_equation_from_point_slope",
    "choice_label_checker",
    "text_short_compute_numeric",
)
_STALE_DRAFT_PRESENTATION_MODES = frozenset({"single_choice"})
_CONTRACT_REQUIRED_FIELDS = (
    "problem_type_id",
    "checker_key",
    "equivalence_type",
    "answer_type",
)


def _artifact_paths(skill_id: str) -> dict[str, Path]:
    return {
        "phase1": REPORT_DIR / f"{skill_id}_phase1_audit.json",
        "phase2_build": REPORT_DIR / f"{skill_id}_phase2_build.json",
        "phase2_generator_summary": REPORT_DIR / f"{skill_id}_phase2_generator_summary.json",
        "phase3_package_summary": REPORT_DIR / f"{skill_id}_phase3_package_summary.json",
        "draft_skill": DRAFT_DIR / f"{skill_id}.py",
    }


def _parse_iso_timestamp(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _file_mtime_dt(path: Path) -> datetime | None:
    if not path.is_file():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def _draft_py_compile_ok(draft_path: Path) -> tuple[bool, str]:
    if not draft_path.is_file():
        return False, "draft_skill_file_missing"
    try:
        py_compile.compile(str(draft_path), doraise=True)
        return True, ""
    except Exception as ex:
        return False, str(ex)


def _load_draft_generator_specs(draft_path: Path) -> list[dict[str, Any]]:
    if not draft_path.is_file():
        return []
    try:
        tree = ast.parse(draft_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "GENERATOR_SPECS":
                try:
                    value = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    return []
                if isinstance(value, list):
                    return [dict(x) for x in value if isinstance(x, dict)]
                return []
    return []


def _generator_spec_contract_complete(spec: dict[str, Any]) -> bool:
    if not isinstance(spec, dict):
        return False
    for field in _CONTRACT_REQUIRED_FIELDS:
        if not str(spec.get(field, "")).strip():
            return False
    return True


def _included_generator_specs(phase3: dict[str, Any]) -> list[dict[str, Any]]:
    specs = phase3.get("generator_specs")
    if isinstance(specs, list) and specs:
        return [dict(x) for x in specs if isinstance(x, dict)]
    included_rows = (
        (phase3.get("packaging_diagnostics") or {}).get("included")
        if isinstance(phase3.get("packaging_diagnostics"), dict)
        else []
    )
    out: list[dict[str, Any]] = []
    if isinstance(included_rows, list):
        for row in included_rows:
            if isinstance(row, dict) and str(row.get("problem_type_id", "")).strip():
                out.append(dict(row))
    return out


def _target_tasks_from_phase3(phase3: dict[str, Any]) -> list[str]:
    tasks: list[str] = []
    for spec in _included_generator_specs(phase3):
        task = str(spec.get("target_task", "")).strip()
        if task:
            tasks.append(task)
    if tasks:
        return sorted(set(tasks))
    for spec in phase3.get("generator_specs") or []:
        if isinstance(spec, dict):
            task = str(spec.get("target_task", "")).strip()
            if task:
                tasks.append(task)
    return sorted(set(tasks))


def _draft_has_stale_markers(draft_path: Path, draft_specs: list[dict[str, Any]]) -> list[str]:
    reasons: list[str] = []
    text = ""
    if draft_path.is_file():
        text = draft_path.read_text(encoding="utf-8", errors="ignore")
    for marker in _STALE_DRAFT_MARKERS:
        if marker in text:
            reasons.append(f"stale_draft_marker:{marker}")
    for spec in draft_specs:
        presentation = str(spec.get("presentation_mode", "")).strip()
        answer_type = str(spec.get("answer_type", "")).strip()
        if presentation in _STALE_DRAFT_PRESENTATION_MODES or answer_type == "single_choice":
            reasons.append("stale_draft_single_choice_presentation")
            break
    return reasons


def _draft_specs_align_with_phase3(
    draft_specs: list[dict[str, Any]],
    phase3: dict[str, Any],
) -> tuple[bool, list[str]]:
    included = _included_generator_specs(phase3)
    if not included:
        return False, ["phase3_included_generators_empty"]
    draft_ids = {str(s.get("problem_type_id", "")).strip() for s in draft_specs if str(s.get("problem_type_id", "")).strip()}
    included_ids = {str(s.get("problem_type_id", "")).strip() for s in included if str(s.get("problem_type_id", "")).strip()}
    if not draft_ids:
        return False, ["draft_generator_specs_missing"]
    if draft_ids != included_ids:
        return False, ["draft_generator_specs_phase3_included_mismatch"]
    return True, []


def _evaluate_phase3_draft_publish_review(
    skill_id: str,
    *,
    paths: dict[str, Path],
    phase3: dict[str, Any] | None,
    phase2_generator_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not isinstance(phase3, dict) or not phase3:
        return {
            "ready": False,
            "blockers": ["phase3_package_summary_missing"],
            "warnings": warnings,
            "included_generators": [],
            "draft_specs": [],
            "binding_tier": "",
        }

    draft_path = paths["draft_skill"]
    publish_check = phase3.get("publish_check") if isinstance(phase3.get("publish_check"), dict) else {}
    publish_blockers = [str(x).strip() for x in (publish_check.get("blockers") or []) if str(x).strip()]
    phase3_blockers = [str(x).strip() for x in (phase3.get("blockers") or []) if str(x).strip()]

    if str(phase3.get("runtime_smoke_status", "")).strip() != "passed":
        blockers.append("phase3_runtime_smoke_not_passed")
    if str(phase3.get("py_compile_status", "")).strip() != "passed":
        blockers.append("phase3_py_compile_not_passed")
    if publish_blockers or phase3_blockers:
        blockers.append("phase3_publish_check_blockers_present")
    if not bool(publish_check.get("can_publish_formal", False)):
        blockers.append("phase3_can_publish_formal_false")

    included = _included_generator_specs(phase3)
    if not included:
        blockers.append("phase3_included_generators_empty")
    incomplete_contracts = [
        str(spec.get("problem_type_id", "")).strip()
        for spec in included
        if not _generator_spec_contract_complete(spec)
    ]
    if incomplete_contracts:
        blockers.append("phase3_included_answer_contract_incomplete")

    draft_ok, draft_reason = _draft_py_compile_ok(draft_path)
    if not draft_ok:
        blockers.append("draft_skill_py_compile_failed" if draft_path.is_file() else "draft_skill_file_missing")
        if draft_reason and draft_reason != "draft_skill_file_missing":
            warnings.append(f"draft_py_compile_error:{draft_reason[:120]}")

    draft_specs = _load_draft_generator_specs(draft_path)
    blockers.extend(_draft_has_stale_markers(draft_path, draft_specs))
    aligned, align_reasons = _draft_specs_align_with_phase3(draft_specs, phase3)
    if not aligned:
        blockers.extend(align_reasons)

    p3_ts = _parse_iso_timestamp(phase3.get("timestamp"))
    p2_ts = _parse_iso_timestamp((phase2_generator_summary or {}).get("timestamp"))
    if p3_ts and p2_ts and p3_ts < p2_ts:
        blockers.append("phase3_package_summary_stale_vs_phase2_generator_summary")

    draft_mtime = _file_mtime_dt(draft_path)
    if p3_ts and draft_mtime and draft_mtime < p3_ts:
        warnings.append("draft_skill_older_than_phase3_package_summary")

    ready = len(blockers) == 0
    return {
        "ready": ready,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "included_generators": included,
        "draft_specs": draft_specs,
        "binding_tier": "draft" if ready else "",
        "answer_contract_gate_status": "PASS" if ready and not incomplete_contracts else "FAIL",
        "candidate_verification_status": "PASS" if ready else "FAIL",
        "verified_problem_types": _target_tasks_from_phase3(phase3),
    }


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
        "phase3_package_summary_missing": "缺少 Phase 3 package summary",
        "phase3_runtime_smoke_not_passed": "Phase 3 runtime smoke 未通過",
        "phase3_py_compile_not_passed": "Phase 3 draft py_compile 未通過",
        "phase3_publish_check_blockers_present": "Phase 3 publish_check 仍有 blockers",
        "phase3_can_publish_formal_false": "Phase 3 can_publish_formal 為 false",
        "phase3_included_generators_empty": "Phase 3 packaging 無 included generator",
        "phase3_included_answer_contract_incomplete": "Phase 3 included generator answer_contract 不完整",
        "draft_skill_py_compile_failed": "draft skill py_compile 失敗",
        "draft_skill_file_missing": "draft skill 檔案不存在",
        "draft_generator_specs_missing": "draft GENERATOR_SPECS 缺失",
        "draft_generator_specs_phase3_included_mismatch": "draft GENERATOR_SPECS 與 Phase 3 included 不一致",
        "phase3_package_summary_stale_vs_phase2_generator_summary": "Phase 3 summary 早於 Phase 2 generator summary，需重跑 packaging",
        "stale_draft_marker:expression_write_line_equation_from_point_slope": "draft 仍含舊 expression_* candidate",
        "stale_draft_marker:choice_label_checker": "draft 仍含 choice_label_checker",
        "stale_draft_marker:text_short_compute_numeric": "draft 仍含 text_short_compute_numeric",
        "stale_draft_single_choice_presentation": "draft 仍為 single_choice presentation",
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
        f"- 是否可進學生端 runtime: {'是' if pbs.get('runtime_binding_status') in {'READY', 'DRAFT_READY'} else '否'}",
        f"- 是否需要人工處理: {'是' if next_action.get('requires_human_review') else '否'}",
        "",
        "## 3. 成功項目",
        f"- Phase 1 例題盤點: {'完成' if success_items.get('phase1_coverage_ok') else '未完成'}",
        f"- Phase 2 candidate verification: {'完成' if success_items.get('phase2_candidate_verification_ok') else '未完成'}",
        f"- verified problem types: {_format_list(success_items.get('verified_problem_types', []))}",
        "",
        "## 4. 未完成 / 失敗項目",
        f"- registry binding: {'完成' if pbs.get('registry_binding_status') in {'BOUND', 'DRAFT_BOUND'} else '未完成'}",
        f"- wrapper binding: {'完成' if pbs.get('wrapper_binding_status') in {'BOUND', 'DRAFT_BOUND'} else '未完成'}",
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
        f"- 是否可進學生端 runtime: {'是' if pbs.get('runtime_binding_status') in {'READY', 'DRAFT_READY'} else '否'}",
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
        f"- registry binding: {'完成' if pbs.get('registry_binding_status') in {'BOUND', 'DRAFT_BOUND'} else '未完成'}",
        f"- wrapper binding: {'完成' if pbs.get('wrapper_binding_status') in {'BOUND', 'DRAFT_BOUND'} else '未完成'}",
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

    paths = _artifact_paths(skill_id)
    phase1_path = paths["phase1"]
    phase2_path = paths["phase2_build"]
    phase2_generator_path = paths["phase2_generator_summary"]
    phase3_path = paths["phase3_package_summary"]
    draft_skill_path = paths["draft_skill"]
    out_json = REPORT_DIR / f"{skill_id}_pipeline_final.json"
    out_md = REPORT_DIR / f"{skill_id}_pipeline_final.md"

    p1 = read_json(phase1_path)
    p2 = read_json(phase2_path)
    p2_gen = read_json(phase2_generator_path)
    p3 = read_json(phase3_path)
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
            "artifact_paths": {
                "phase1_json": str(phase1_path),
                "phase2_json": str(phase2_path),
                "phase2_generator_summary_json": str(phase2_generator_path),
                "phase3_package_summary_json": str(phase3_path),
                "draft_skill_file": str(draft_skill_path),
                "final_json": str(out_json),
                "final_md": str(out_md),
            },
            "timestamp": utc_timestamp(),
        }
        write_json(out_json, report)
        _write_md(out_md, report)
        print(json.dumps(report, ensure_ascii=True) if args.json else _build_summary_stdout(report))
        return

    draft_review = _evaluate_phase3_draft_publish_review(
        skill_id,
        paths=paths,
        phase3=p3,
        phase2_generator_summary=p2_gen,
    )
    draft_publish_review_ready = bool(draft_review.get("ready"))

    runtime = _runtime_probe(skill_id)
    phase2_final_status = str(p2.get("final_status", "")).strip()
    phase2_exec = str((p2.get("build_execution_summary") or {}).get("execution_status", "")).strip()
    verified_problem_types = list(p2.get("verified_problem_types") or [])
    if draft_publish_review_ready:
        verified_problem_types = list(draft_review.get("verified_problem_types") or verified_problem_types)
    pending_implementation = list(p2.get("pending_implementation") or [])
    observed_problem_types = list(p1.get("observed_problem_types") or [])
    manual_review_problem_types = list(p1.get("manual_review_problem_types") or [])
    future_ai_judged_problem_types = list(p1.get("future_ai_judged_problem_types") or [])
    missing_answer_contract_problem_types = list(p1.get("missing_answer_contract_problem_types") or [])
    missing_checker_key_problem_types = list(p1.get("missing_checker_key_problem_types") or [])
    source_coverage_status = str(p1.get("source_coverage_status", "INSUFFICIENT_SOURCE_EXAMPLES"))
    deterministic_expected = sorted([x for x in observed_problem_types if x not in set(manual_review_problem_types) and x not in set(future_ai_judged_problem_types)])

    wrapper_summary = p2.get("wrapper_summary") or {}
    reg_detect = _discover_registry_binding(skill_id)
    formal_registry_binding_status = str(reg_detect.get("registry_binding_status", "NOT_BOUND"))
    formal_wrapper_binding_status = "BOUND"
    if str(wrapper_summary.get("pipeline_final_status", "")).strip() in {"SKIPPED_CANDIDATE_VERIFICATION_MODE", ""}:
        formal_wrapper_binding_status = "NOT_BOUND"

    if draft_publish_review_ready:
        registry_binding_status = "DRAFT_BOUND" if formal_registry_binding_status != "BOUND" else "BOUND"
        wrapper_binding_status = "DRAFT_BOUND" if formal_wrapper_binding_status != "BOUND" else "BOUND"
        runtime_binding_status = "DRAFT_READY"
        candidate_verification_status = str(draft_review.get("candidate_verification_status", "PASS"))
        answer_contract_gate_status = str(draft_review.get("answer_contract_gate_status", "PASS"))
    else:
        registry_binding_status = formal_registry_binding_status
        wrapper_binding_status = formal_wrapper_binding_status
        runtime_binding_status = "READY" if runtime.get("import_ok") and runtime.get("generate_ok") and runtime.get("check_ok") else "NOT_READY"
        candidate_verification_status = "PASS" if (phase2_final_status == "BUILD_PASS" or phase2_exec == "PASS") and bool(verified_problem_types) else "FAIL"
        answer_contract_gate_status = "PASS" if not missing_answer_contract_problem_types else "FAIL"

    runtime_observed = sorted(set(verified_problem_types or [runtime.get("sample_problem_type", "")]) - {""})
    runtime_missing = sorted(set(deterministic_expected) - set(runtime_observed))
    runtime_coverage_status = "pass" if not runtime_missing else "fail"
    if draft_publish_review_ready:
        runtime_coverage_status = "pass"
        runtime_missing = []

    blocking_reasons: list[str] = []
    warnings: list[str] = list(draft_review.get("warnings") or [])
    if draft_publish_review_ready:
        if candidate_verification_status != "PASS":
            blocking_reasons.append("candidate_verification_failed")
        if answer_contract_gate_status != "PASS":
            blocking_reasons.append("answer_contract_gate_failed")
        if phase2_final_status != "BUILD_PASS":
            warnings.append("phase2_build_not_pass_overridden_by_phase3_package_summary")
    else:
        if candidate_verification_status != "PASS":
            blocking_reasons.append("candidate_verification_failed")
        if phase2_final_status != "BUILD_PASS":
            blocking_reasons.append("phase2_not_build_pass")
        if registry_binding_status == "INCOMPLETE":
            blocking_reasons.append("registry_binding_incomplete")
        elif registry_binding_status not in {"BOUND", "DRAFT_BOUND"}:
            blocking_reasons.append("registry_binding_missing")
        if wrapper_binding_status not in {"BOUND", "DRAFT_BOUND"}:
            blocking_reasons.append("wrapper_binding_missing")
        if runtime_binding_status not in {"READY", "DRAFT_READY"}:
            blocking_reasons.append("runtime_binding_missing")
        if runtime_coverage_status != "pass":
            blocking_reasons.append("runtime_coverage_failed")
        if missing_answer_contract_problem_types:
            blocking_reasons.append("answer_contract_gate_failed")
        if missing_checker_key_problem_types:
            blocking_reasons.append("missing_checker_key_problem_types")
        blocking_reasons.extend(list(draft_review.get("blockers") or []))

    if manual_review_problem_types:
        warnings.append("manual_review_present")

    legacy = [x for x in list(p2.get("blocking_reasons") or []) if str(x) in {"import_failed", "generate_failed", "checker_failed"}]
    if legacy and not (runtime.get("error") or runtime_missing) and not draft_publish_review_ready:
        warnings.append("unclear_legacy_failure_reason")

    final_status = "PUBLISH_BINDING_REQUIRED"
    publish_ready = False
    publish_review_mode = ""
    if draft_publish_review_ready and not blocking_reasons:
        final_status = "PUBLISH_REVIEW_READY"
        publish_ready = True
        publish_review_mode = "draft_publish_review"
    elif (
        candidate_verification_status == "PASS"
        and registry_binding_status == "BOUND"
        and wrapper_binding_status == "BOUND"
        and runtime_binding_status == "READY"
        and runtime_coverage_status == "pass"
        and answer_contract_gate_status == "PASS"
    ):
        final_status = "PASS"
        publish_ready = True
        publish_review_mode = "formal_publish_ready"

    bootstrap_summary = dict(p2.get("bootstrap_summary") or p1.get("bootstrap_summary") or {})
    if bool(bootstrap_summary.get("bootstrap_mode")) and str(bootstrap_summary.get("bootstrap_runtime_status", "FAIL")) == "PASS" and not publish_ready:
        final_status = "PASS_BOOTSTRAP_ONLY"
        publish_ready = True

    if final_status in {"PASS", "PUBLISH_REVIEW_READY"}:
        next_action = {
            "next_action_type": "ready_for_publish_review",
            "command": "",
            "reason": "可進人工發布審核（draft packaging / runtime smoke 已通過）。" if final_status == "PUBLISH_REVIEW_READY" else "可進人工發布審核。",
            "should_publish": False if final_status == "PUBLISH_REVIEW_READY" else True,
            "requires_human_review": True,
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
            "reason": "Phase 2 / Phase 3 draft packaging 尚未達 publish review 門檻。",
            "should_publish": False,
            "requires_human_review": True,
        }

    runtime_problem_type_coverage = {
        "expected_problem_types": deterministic_expected,
        "observed_problem_types": runtime_observed,
        "missing_problem_types": runtime_missing,
        "status": runtime_coverage_status,
    }
    publish_binding_summary = {
        "candidate_verification_status": candidate_verification_status,
        "answer_contract_gate_status": answer_contract_gate_status,
        "verified_candidates_count": len(verified_problem_types),
        "verified_problem_types": verified_problem_types,
        "registry_binding_status": registry_binding_status,
        "formal_registry_binding_status": formal_registry_binding_status,
        "registry_path": reg_detect.get("registry_path", ""),
        "registry_entry_found": bool(reg_detect.get("registry_entry_found", False)),
        "registry_entry_valid": bool(reg_detect.get("registry_entry_valid", False)),
        "registry_verified_problem_types": reg_detect.get("registry_verified_problem_types", []),
        "registry_manual_review_exclusions": reg_detect.get("registry_manual_review_exclusions", []),
        "registry_binding_failure_reason": reg_detect.get("registry_binding_failure_reason", ""),
        "wrapper_binding_status": wrapper_binding_status,
        "formal_wrapper_binding_status": formal_wrapper_binding_status,
        "runtime_binding_status": runtime_binding_status,
        "formal_runtime_binding_status": "READY" if runtime_binding_status == "READY" else "NOT_READY",
        "draft_publish_review_ready": draft_publish_review_ready,
        "publish_review_mode": publish_review_mode,
        "binding_required": final_status == "PUBLISH_BINDING_REQUIRED",
        "binding_blockers": sorted(set([x for x in blocking_reasons if x in {
            "registry_binding_missing", "wrapper_binding_missing", "runtime_binding_missing",
            "runtime_coverage_failed", "phase3_runtime_smoke_not_passed",
        }])),
        "publish_exclusions": {
            "manual_review_problem_types": manual_review_problem_types,
            "future_ai_judged_problem_types": future_ai_judged_problem_types,
        },
        "phase3_package_summary_path": str(phase3_path),
        "phase2_generator_summary_path": str(phase2_generator_path),
        "draft_skill_file": str(draft_skill_path),
    }

    success_items = {
        "phase1_coverage_ok": int(p1.get("examples_covered", 0)) == int(p1.get("examples_total", 0)),
        "phase2_candidate_verification_ok": candidate_verification_status == "PASS",
        "phase3_draft_publish_review_ok": draft_publish_review_ready,
        "verified_problem_types": verified_problem_types,
        "answer_contract_gate_ok": answer_contract_gate_status == "PASS",
        "checker_key_gate_ok": not missing_checker_key_problem_types or draft_publish_review_ready,
    }
    incomplete_items = {
        "registry_binding_done": registry_binding_status in {"BOUND", "DRAFT_BOUND"},
        "wrapper_binding_done": wrapper_binding_status in {"BOUND", "DRAFT_BOUND"},
        "runtime_binding_ready": runtime_binding_status in {"READY", "DRAFT_READY"},
        "runtime_coverage_pass": runtime_coverage_status == "pass",
        "formal_registry_binding_done": formal_registry_binding_status == "BOUND",
        "formal_wrapper_binding_done": formal_wrapper_binding_status == "BOUND",
        "formal_runtime_binding_ready": runtime_binding_status == "READY",
    }

    status_message = (
        "Phase 3 draft packaging / runtime smoke 已通過，可進 publish review（尚未 formal publish）。"
        if final_status == "PUBLISH_REVIEW_READY"
        else "candidate 驗證、binding 與 runtime coverage 綜合判讀結果。"
    )

    report = {
        "skill_id": skill_id,
        "phase": "phase3_publish_gate",
        "final_status": final_status,
        "publish_ready": publish_ready,
        "publish_review_mode": publish_review_mode,
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
        "phase3_draft_publish_review": draft_review,
        "next_action": next_action,
        "success_items": success_items,
        "incomplete_items": incomplete_items,
        "status_message": status_message,
        "artifact_paths": {
            "phase1_json": str(phase1_path),
            "phase2_json": str(phase2_path),
            "phase2_generator_summary_json": str(phase2_generator_path),
            "phase3_package_summary_json": str(phase3_path),
            "draft_skill_file": str(draft_skill_path),
            "final_json": str(out_json),
            "final_md": str(out_md),
        },
        "timestamp": utc_timestamp(),
    }
    write_json(out_json, report)
    _write_md(out_md, report)
    print(json.dumps(report, ensure_ascii=True) if args.json else _build_summary_stdout(report))


if __name__ == "__main__":
    main()
