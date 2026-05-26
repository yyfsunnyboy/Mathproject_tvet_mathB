from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.pipeline_state import utc_timestamp, write_json, write_md
from core.gencode.classifier_proposal import build_classifier_proposal

REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"
BOOTSTRAP_MAP_PATH = PROJECT_ROOT / "configs" / "gencode" / "bootstrap_skill_map.yaml"

REQUIRED_CONTRACT_FIELDS = {
    "answer_type",
    "equivalence_type",
    "checker_key",
    "order_matters",
    "accepted_format_notes",
    "canonical_answer_schema",
}

ANSWER_CONTRACT_DEFAULTS: dict[str, dict[str, dict[str, Any]]] = {
    "vh_數學B1_AbsoluteValue": {
        "absolute_value_numeric_evaluation": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
            "order_matters": True,
            "accepted_format_notes": ["single integer answer"],
            "canonical_answer_schema": "int",
        },
        "absolute_value_distance_from_zero": {
            "answer_type": "choice",
            "equivalence_type": "choice_label",
            "checker_key": "choice_label_checker",
            "order_matters": True,
            "accepted_format_notes": ["A/a/(A)/A./1/choice text aliases accepted by label checker"],
            "canonical_answer_schema": "choice_label",
        },
        "absolute_value_distance_between_two_points": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
            "order_matters": True,
            "accepted_format_notes": ["single integer distance"],
            "canonical_answer_schema": "int",
        },
        "absolute_value_equation_basic": {
            "answer_type": "solution_set",
            "equivalence_type": "unordered_solution_set",
            "checker_key": "solution_set_checker",
            "order_matters": False,
            "accepted_format_notes": ["17,-17", "-17,17", "x=17 或 x=-17", "x=-17 或 x=17", "±17"],
            "canonical_answer_schema": "set[int]",
        },
    },
    "vh_數學B1_NumberLine": {
        "number_line_point_value_reading": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
            "order_matters": False,
            "accepted_format_notes": ["single integer answer"],
            "canonical_answer_schema": {"type": "integer"},
        },
        "number_line_distance_between_points": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
            "order_matters": False,
            "accepted_format_notes": ["single integer answer"],
            "canonical_answer_schema": {"type": "integer"},
        },
    },
    "vh_數學B1_AbsoluteValueInequality": {
        "absolute_value_inequality_zero_center_basic": {
            "answer_type": "interval_set",
            "equivalence_type": "interval_set",
            "checker_key": "interval_checker",
            "order_matters": False,
            "accepted_format_notes": ["x > a", "x < a", "x ≤ a", "x ≥ a", "interval notation"],
            "canonical_answer_schema": {"type": "interval_set"},
        },
        "absolute_value_inequality_shifted_basic": {
            "answer_type": "interval_set",
            "equivalence_type": "interval_set",
            "checker_key": "interval_checker",
            "order_matters": False,
            "accepted_format_notes": ["x > a", "x < a", "x ≤ a", "x ≥ a", "interval notation"],
            "canonical_answer_schema": {"type": "interval_set"},
        },
        "absolute_value_inequality_linear_expression_basic": {
            "answer_type": "interval_set",
            "equivalence_type": "interval_set",
            "checker_key": "interval_checker",
            "order_matters": False,
            "accepted_format_notes": ["x > a", "x < a", "x ≤ a", "x ≥ a", "interval notation"],
            "canonical_answer_schema": {"type": "interval_set"},
        },
        "absolute_value_inequality_integer_solution_count_choice": {
            "answer_type": "choice",
            "equivalence_type": "choice_label",
            "checker_key": "choice_label_checker",
            "order_matters": False,
            "accepted_format_notes": ["A/B/C/D labels"],
            "canonical_answer_schema": {"type": "choice_label"},
        },
        "absolute_value_inequality_malformed_source_review": {
            "answer_type": "manual_review",
            "equivalence_type": "manual_review_or_ai_judged",
            "checker_key": "manual_review_checker",
            "order_matters": False,
            "accepted_format_notes": ["requires source text correction before deterministic generation"],
            "canonical_answer_schema": {"type": "manual_review"},
        },
    },
}


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    obj = yaml.safe_load(path.read_text(encoding="utf-8"))
    return obj if isinstance(obj, dict) else {}


def _load_bootstrap_config(skill_id: str) -> dict[str, Any]:
    data = _load_yaml(BOOTSTRAP_MAP_PATH)
    cfg = data.get(skill_id)
    return cfg if isinstance(cfg, dict) else {}


def _run_json_cmd(cmd: list[str], timeout: int = 600) -> tuple[int, dict[str, Any], str, str]:
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


def _short(s: object, limit: int = 100) -> str:
    t = str(s or "").replace("\n", " ").strip()
    return t if len(t) <= limit else t[: limit - 3] + "..."


def _format_list(xs: list[Any]) -> str:
    return "無" if not xs else ", ".join(str(x) for x in xs)


def _build_problem_type_rows(examples: list[dict[str, Any]], contracts: dict[str, Any]) -> list[dict[str, Any]]:
    by_pt: dict[str, dict[str, Any]] = {}
    for e in examples:
        pt = str(e.get("problem_type_id", "")).strip()
        if not pt or pt == "unknown":
            continue
        by_pt.setdefault(pt, {"example_ids": [], "runtime_category": str(e.get("runtime_category", "")).strip()})
        if isinstance(e.get("example_id"), int):
            by_pt[pt]["example_ids"].append(int(e["example_id"]))
    rows: list[dict[str, Any]] = []
    for pt in sorted(by_pt.keys()):
        c = contracts.get(pt) if isinstance(contracts.get(pt), dict) else {}
        rows.append(
            {
                "problem_type_id": pt,
                "runtime_category": by_pt[pt]["runtime_category"],
                "example_ids": sorted(set(by_pt[pt]["example_ids"])),
                "answer_type": c.get("answer_type", ""),
                "equivalence_type": c.get("equivalence_type", ""),
                "checker_key": c.get("checker_key", ""),
            }
        )
    return rows


def _build_stdout_summary(report: dict[str, Any]) -> str:
    lines: list[str] = []
    skill_id = report.get("skill_id", "")
    lines += [
        "============================================================",
        "Gencode 第一階段盤點摘要",
        "============================================================",
        f"skill_id: {skill_id}",
        f"階段狀態: {report.get('final_status', '')}",
        f"建議下一步: {report.get('recommended_next_phase', '')}",
        "",
        "題庫覆蓋狀態:",
        f"- 題庫例題總數: {report.get('examples_total', 0)}",
        f"- 已分類例題數: {report.get('examples_covered', 0)}",
        f"- 來源覆蓋判定: {report.get('source_coverage_status', '')}",
        f"- 是否可能完整覆蓋: {str(report.get('source_coverage_status', '') == 'FULL_OBSERVED_COVERAGE_CANDIDATE').lower()}",
        "",
        "題型分類結果:",
    ]
    rows = _build_problem_type_rows(report.get("examples_map", []), report.get("answer_contract_summary", {}))
    if not rows:
        lines.append("- none")
    else:
        for idx, r in enumerate(rows, start=1):
            lines += [
                f"{idx}. {r['problem_type_id']}",
                f"   - 對應例題: {_format_list(r['example_ids'])}",
                f"   - 執行類型: {r['runtime_category']}",
                f"   - 答案判分規格: {r['equivalence_type']} / {r['checker_key']}",
            ]
    lines += [
        "",
        "答案規格檢查:",
        f"- 缺少 answer_contract 的題型: {_format_list(report.get('missing_answer_contract_problem_types', []))}",
        f"- 缺少 checker_key 的題型: {_format_list(report.get('missing_checker_key_problem_types', []))}",
        f"- 需要等價答案測試的題型: {_format_list(report.get('equivalence_test_required_problem_types', []))}",
        "",
        "需人工審查:",
    ]
    manual_pts = report.get("manual_review_problem_types", [])
    if manual_pts:
        ex_map = report.get("examples_map", [])
        for pt in manual_pts:
            ids = [str(e.get("example_id")) for e in ex_map if str(e.get("problem_type_id", "")).strip() == pt and e.get("example_id") is not None]
            lines.append(f"- {pt}: 例題 {', '.join(ids) if ids else '無'}")
    else:
        lines.append("- 無")
    lines += [
        "",
        f"阻塞原因:\n- {_format_list(report.get('blocking_reasons', []))}",
        "",
        "警告:",
        "",
        "報告檔案:",
        f"- JSON: reports/gencode_closed_loop/{skill_id}_phase1_audit.json",
        f"- Markdown: reports/gencode_closed_loop/{skill_id}_phase1_audit.md",
        "",
    ]
    warn_map = {
        "manual_review_problem_types_present": "有題型需要人工審查",
        "risk_flags_present": "有來源或分類風險標記",
        "skill_specific_classifier_missing": "缺少 skill-specific classifier",
        "classifier_proposal_generated": "已產生 classifier proposal，待人工審核",
    }
    ws = report.get("warnings", [])
    if ws:
        for w in ws:
            lines.append(f"- {w}：{warn_map.get(str(w), '請檢查此警告')}")
    else:
        lines.append("- 無")
    lines.append("")
    if report.get("final_status") == "AUDIT_PARTIAL" and report.get("recommended_next_phase") == "phase2_build":
        lines += [
            "判讀說明:",
            "Phase 1 分類結果可使用。",
            "目前是 AUDIT_PARTIAL，原因是存在 manual_review 或 risk warning，不是 classifier 失敗。",
            "",
        ]
    lines += [
        "下一步建議:",
    ]
    if report.get("recommended_next_phase") == "phase2_build":
        lines.append(f"執行：\npython scripts\\gencode_pipeline_phase2_build.py --skill-id {skill_id}")
    elif report.get("recommended_next_phase") == "review_classifier_proposal":
        lines.append("請先審核 classifier proposal，再執行 promote。")
    else:
        lines.append(f"- {report.get('recommended_next_phase', '')}")
    lines.append("============================================================")
    return "\n".join(lines)


def _write_phase1_markdown(path: Path, report: dict[str, Any]) -> None:
    rows = _build_problem_type_rows(report.get("examples_map", []), report.get("answer_contract_summary", {}))
    lines: list[str] = [
        "# Gencode 第一階段盤點報告",
        "",
        "## 1. 摘要",
        f"- skill_id: {report.get('skill_id', '')}",
        f"- 階段狀態: {report.get('final_status', '')}",
        f"- 建議下一步: {report.get('recommended_next_phase', '')}",
        f"- 題庫例題總數: {report.get('examples_total', 0)}",
        f"- 已分類例題數: {report.get('examples_covered', 0)}",
        f"- 來源覆蓋判定: {report.get('source_coverage_status', '')}",
        "",
        "## 2. 題型覆蓋表",
        "",
        "| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        status = "manual_review" if r["runtime_category"] == "manual_review" else "classified"
        lines.append(
            f"| {r['problem_type_id']} | {r['runtime_category']} | {', '.join(str(x) for x in r['example_ids'])} | {r['answer_type']} | {r['equivalence_type']} | {r['checker_key']} | {status} |"
        )
    lines += [
        "",
        "## 3. 例題分類表",
        "",
        "| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for e in report.get("examples_map", []):
        lines.append(
            "| {id} | {pt} | {rt} | {cf} | {rf} | {pv} |".format(
                id=e.get("example_id", ""),
                pt=str(e.get("problem_type_id", "")).strip(),
                rt=str(e.get("runtime_category", "")).strip(),
                cf=str(e.get("classifier_confidence", "")).strip(),
                rf=_short(",".join(e.get("semantic_risk_flags", []) if isinstance(e.get("semantic_risk_flags"), list) else []), 60),
                pv=_short(e.get("problem_preview", ""), 110).replace("|", "\\|"),
            )
        )
    lines += [
        "",
        "## 4. 答案規格檢查",
        f"- 缺少 answer_contract 的題型: {_format_list(report.get('missing_answer_contract_problem_types', []))}",
        f"- 缺少 checker_key 的題型: {_format_list(report.get('missing_checker_key_problem_types', []))}",
        f"- 需要等價答案測試的題型: {_format_list(report.get('equivalence_test_required_problem_types', []))}",
        "",
        "## 5. 人工審查與風險標記",
        f"- manual_review_problem_types: {_format_list(report.get('manual_review_problem_types', []))}",
        f"- risk_flags: {_format_list(report.get('risk_flags', []))}",
    ]
    for e in report.get("examples_map", []):
        if str(e.get("runtime_category", "")).strip() == "manual_review":
            lines.append(
                f"- example {e.get('example_id')}: {_short(e.get('manual_review_reason', ''), 120)}"
            )
    cp = report.get("classifier_proposal", {}) if isinstance(report.get("classifier_proposal"), dict) else {}
    lines += [
        "",
        "## 6. Classifier Proposal 狀態",
        f"- classifier_proposal.enabled: {cp.get('enabled', False)}",
        f"- proposal_status: {cp.get('proposal_status', 'SKIPPED')}",
        f"- reason: {cp.get('reason', '')}",
        f"- proposal_path: {cp.get('proposal_path', '')}",
        f"- promote_ready: {cp.get('promote_ready', False)}",
        f"- promote_command_suggestion: {cp.get('promote_command_suggestion', '')}",
        "",
        "## 7. 下一步建議",
    ]
    if report.get("recommended_next_phase") == "phase2_build":
        lines.append(f"python scripts\\gencode_pipeline_phase2_build.py --skill-id {report.get('skill_id', '')}")
    elif report.get("recommended_next_phase") == "review_classifier_proposal":
        lines.append("請先審核 classifier proposal，再執行 promote。")
    else:
        lines.append(str(report.get("recommended_next_phase", "")))
    if report.get("missing_checker_key_problem_types"):
        lines.append("請先實作或註冊 checker。")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    skill_id = args.skill_id

    out_json = REPORT_DIR / f"{skill_id}_phase1_audit.json"
    out_md = REPORT_DIR / f"{skill_id}_phase1_audit.md"
    proposal_json = REPORT_DIR / f"{skill_id}_classifier_proposal.json"
    proposal_md = REPORT_DIR / f"{skill_id}_classifier_proposal.md"

    inv_cmd = [sys.executable, "scripts/gencode_skill_inventory.py", "--skill-id", skill_id]
    code, inv, stdout, stderr = _run_json_cmd(inv_cmd, timeout=900)

    if code != 0 or not inv.get("success"):
        report = {
            "skill_id": skill_id,
            "phase": "phase1_audit",
            "final_status": "AUDIT_FAIL",
            "blocking_reasons": ["inventory_failed"],
            "warnings": [],
            "artifact_paths": {"phase1_json": str(out_json), "phase1_md": str(out_md)},
            "timestamp": utc_timestamp(),
            "raw_inventory_stdout": stdout,
            "raw_inventory_stderr": stderr,
        }
        write_json(out_json, report)
        _write_phase1_markdown(out_md, report)
        if args.json:
            print(json.dumps(report, ensure_ascii=True))
        else:
            print(_build_stdout_summary(report))
        return

    package_dir = Path(str(inv.get("package_dir", "")))
    examples_map_path = next(iter(package_dir.glob("examples_map_*.yaml")), None)
    problem_types_path = next(iter(package_dir.glob("problem_types_*.yaml")), None)
    examples = _load_yaml(examples_map_path).get("examples", []) if examples_map_path else []
    items = _load_yaml(problem_types_path).get("items", []) if problem_types_path else []
    if not isinstance(examples, list):
        examples = []
    if not isinstance(items, list):
        items = []

    examples = [e for e in examples if isinstance(e, dict)]
    items = [i for i in items if isinstance(i, dict)]

    observed_problem_types = sorted(
        {
            str(e.get("problem_type_id", "")).strip()
            for e in examples
            if str(e.get("problem_type_id", "")).strip() and str(e.get("problem_type_id", "")).strip() != "unknown"
        }
    )

    pt_map = {str(i.get("problem_type_id", "")).strip(): i for i in items if str(i.get("problem_type_id", "")).strip()}
    defaults = ANSWER_CONTRACT_DEFAULTS.get(skill_id, {})
    observed_contracts: dict[str, Any] = {}
    missing_answer_contract_problem_types: list[str] = []
    missing_checker_key_problem_types: list[str] = []
    equivalence_test_required_problem_types: list[str] = []
    for pt in observed_problem_types:
        row = pt_map.get(pt, {})
        contract = row.get("answer_contract") if isinstance(row, dict) else None
        if not isinstance(contract, dict):
            contract = defaults.get(pt)
        if not isinstance(contract, dict):
            missing_answer_contract_problem_types.append(pt)
            observed_contracts[pt] = None
            continue
        observed_contracts[pt] = contract
        if not str(contract.get("checker_key", "")).strip():
            missing_checker_key_problem_types.append(pt)
        eq = str(contract.get("equivalence_type", "")).strip()
        if eq not in {"exact_string", "numeric_exact"}:
            equivalence_test_required_problem_types.append(pt)
        missing_fields = sorted(REQUIRED_CONTRACT_FIELDS.difference(set(contract.keys())))
        if missing_fields:
            missing_answer_contract_problem_types.append(pt)

    risk_flags = sorted({flag for e in examples for flag in (e.get("semantic_risk_flags") if isinstance(e.get("semantic_risk_flags"), list) else [])})
    manual_review_problem_types = sorted(
        {
            str(e.get("problem_type_id", "")).strip()
            for e in examples
            if str(e.get("semantic_audit_status", "")).strip() == "review_required" and str(e.get("problem_type_id", "")).strip()
        }
    )
    future_ai_judged_problem_types: list[str] = []

    examples_total = int(inv.get("examples_count", 0))
    examples_covered = len(examples)

    unknown_count = sum(
        1
        for e in examples
        if str(e.get("problem_type_id", "")).strip() in {"", "unknown"}
        or str(e.get("classification_rule_id", "")).strip() == "fallback.unknown"
    )
    unknown_ratio = (unknown_count / max(len(examples), 1)) if examples else 0.0
    classifier_proposal_enabled = (
        examples_total >= 3
        and examples_covered > 0
        and unknown_ratio >= 0.6
    )
    classifier_proposal = {
        "enabled": classifier_proposal_enabled,
        "reason": "",
        "proposal_status": "SKIPPED",
        "proposed_problem_types": [],
        "proposed_example_map": [],
        "proposed_answer_contracts": {},
        "manual_review_candidates": [],
        "risk_flags": [],
        "proposal_path": str(proposal_json),
        "promote_ready": False,
        "promote_command_suggestion": f"python scripts\\gencode_promote_classifier_proposal.py --skill-id {skill_id}",
    }
    if classifier_proposal_enabled:
        try:
            proposal = build_classifier_proposal(skill_id, examples)
            classifier_proposal.update(
                {
                    "reason": "fallback_unknown_majority",
                    "proposal_status": "GENERATED",
                    "proposed_problem_types": proposal.get("proposed_problem_types", []),
                    "proposed_example_map": proposal.get("proposed_example_map", []),
                    "proposed_answer_contracts": proposal.get("proposed_answer_contracts", {}),
                    "manual_review_candidates": proposal.get("manual_review_candidates", []),
                    "risk_flags": proposal.get("risk_flags", []),
                    "promote_ready": True,
                }
            )
            write_json(proposal_json, proposal)
            write_md(proposal_md, f"Classifier Proposal: {skill_id}", [("proposal", proposal)])
        except Exception as e:
            classifier_proposal.update(
                {
                    "proposal_status": "FAILED",
                    "reason": f"proposal_generation_failed: {e}",
                    "promote_ready": False,
                }
            )

    bootstrap_cfg = _load_bootstrap_config(skill_id)
    bootstrap_summary = {
        "bootstrap_mode": bool(bootstrap_cfg.get("bootstrap_mode", False)),
        "bootstrap_source_skill_id": str(bootstrap_cfg.get("bootstrap_source_skill_id", "")),
        "source_coverage_status": str(bootstrap_cfg.get("source_coverage_status", "")),
        "allowed_problem_types": bootstrap_cfg.get("allowed_problem_types", []),
    }

    if bootstrap_summary["bootstrap_mode"]:
        source_coverage_status = bootstrap_summary["source_coverage_status"] or "INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES"
    elif examples_total >= 4 and not manual_review_problem_types:
        source_coverage_status = "FULL_OBSERVED_COVERAGE_CANDIDATE"
    elif examples_total <= 1:
        source_coverage_status = "INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES"
    else:
        source_coverage_status = "INSUFFICIENT_SOURCE_EXAMPLES"

    blocking_reasons: list[str] = []
    warnings: list[str] = []
    if missing_answer_contract_problem_types:
        blocking_reasons.append("missing_answer_contract_problem_types")
    if missing_checker_key_problem_types:
        blocking_reasons.append("missing_checker_key_problem_types")
    if manual_review_problem_types:
        warnings.append("manual_review_problem_types_present")
    if risk_flags:
        warnings.append("risk_flags_present")

    if classifier_proposal.get("proposal_status") == "GENERATED":
        blocking_reasons.append("classifier_proposal_requires_review")
        warnings.extend(["skill_specific_classifier_missing", "classifier_proposal_generated"])

    hard_blocking_reasons = [x for x in blocking_reasons if x != "classifier_proposal_requires_review"]
    if hard_blocking_reasons:
        final_status = "AUDIT_FAIL"
    elif warnings or source_coverage_status != "FULL_OBSERVED_COVERAGE_CANDIDATE":
        final_status = "AUDIT_PARTIAL"
    else:
        final_status = "AUDIT_PASS"

    next_phase = "phase2_build"
    if classifier_proposal.get("proposal_status") == "GENERATED":
        next_phase = "review_classifier_proposal"

    report = {
        "skill_id": skill_id,
        "phase": "phase1_audit",
        "final_status": final_status,
        "examples_total": examples_total,
        "examples_covered": examples_covered,
        "examples_map": examples,
        "observed_problem_types": observed_problem_types,
        "source_coverage_status": source_coverage_status,
        "bootstrap_summary": bootstrap_summary,
        "answer_contract_summary": observed_contracts,
        "missing_answer_contract_problem_types": sorted(set(missing_answer_contract_problem_types)),
        "missing_checker_key_problem_types": sorted(set(missing_checker_key_problem_types)),
        "equivalence_test_required_problem_types": sorted(set(equivalence_test_required_problem_types)),
        "manual_review_problem_types": manual_review_problem_types,
        "future_ai_judged_problem_types": future_ai_judged_problem_types,
        "classifier_proposal": classifier_proposal,
        "risk_flags": risk_flags,
        "recommended_next_phase": next_phase,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "warnings": sorted(set(warnings)),
        "artifact_paths": {
            "phase1_json": str(out_json),
            "phase1_md": str(out_md),
            "inventory_report": str(inv.get("report", "")),
            "classifier_proposal_json": str(proposal_json) if classifier_proposal.get("proposal_status") == "GENERATED" else "",
            "classifier_proposal_md": str(proposal_md) if classifier_proposal.get("proposal_status") == "GENERATED" else "",
        },
        "timestamp": utc_timestamp(),
    }
    write_json(out_json, report)
    _write_phase1_markdown(out_md, report)
    if args.json:
        print(json.dumps(report, ensure_ascii=True))
    else:
        print(_build_stdout_summary(report))


if __name__ == "__main__":
    main()
