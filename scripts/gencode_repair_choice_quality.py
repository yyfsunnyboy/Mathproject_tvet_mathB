from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_quality"
REPAIRABLE_ISSUES = {
    "invalid_choice_answer_label",
    "choice_answer_fixed_label_detected",
    "duplicate_choice_options",
    "choice_correct_answer_not_in_choices",
}


def _run_choice_audit(skill_id: str, samples: int) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "gencode_choice_quality_audit.py"),
        "--skill-id",
        skill_id,
        "--samples",
        str(samples),
        "--json",
    ]
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, check=True)
    return json.loads(proc.stdout.strip().splitlines()[-1])


def _normalize_issue(issue: str) -> str:
    return issue.split(":", 1)[0]


def _target_rows(audit_payload: dict[str, Any], skill_id: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in audit_payload.get("results", []):
        row_skill = str(row.get("skill_id", "")).strip()
        if row_skill and row_skill != skill_id:
            continue
        module = str(row.get("module", ""))
        if module.startswith("skills.") or "generated_candidates/" in module:
            out.append(row)
    return out


def _ensure_import(source: str) -> tuple[str, bool]:
    target_import = "from core.domain.choices_unique_validator import repair_choice_payload"
    if target_import in source:
        return source, False
    lines = source.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, target_import)
    return "\n".join(lines) + ("\n" if source.endswith("\n") else ""), True


def _patch_generate_return(source: str) -> tuple[str, bool]:
    old = "    return payload\n"
    if "payload = generate_from_verified_candidate(" not in source or old not in source:
        return source, False
    new = (
        "    if str(payload.get(\"answer_type\", \"\")).strip() in {\"choice\", \"choice_label\"}:\n"
        "        payload = repair_choice_payload(payload, seed=seed)\n"
        "    return payload\n"
    )
    return source.replace(old, new, 1), source != source.replace(old, new, 1)


def _repair_source_file(path: Path) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not path.exists():
        return False, ["source_file_missing"]
    source = path.read_text(encoding="utf-8")
    source2, body_changed = _patch_generate_return(source)
    if not body_changed:
        reasons.append("requires_manual_repair:unsupported_generate_pattern")
        return False, reasons
    source3, _ = _ensure_import(source2)
    if source3 != source:
        path.write_text(source3, encoding="utf-8")
        return True, reasons
    return False, reasons


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_md(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Gencode Choice 品質修復報告",
        "",
        f"- skill_id: {payload.get('skill_id', '')}",
        f"- repair_status: {payload.get('repair_status', '')}",
        f"- audit_status_before: {payload.get('audit_status_before', '')}",
        f"- audit_status_after: {payload.get('audit_status_after', '')}",
        f"- fixed_issues: {payload.get('fixed_issues', [])}",
        f"- requires_manual_repair: {payload.get('requires_manual_repair', [])}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _summary(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "============================================================",
            "Gencode Choice 品質修復摘要",
            "============================================================",
            f"skill_id: {payload.get('skill_id', '')}",
            f"repair_status: {payload.get('repair_status', '')}",
            "",
            "修復前問題:",
            *[f"- {x}" for x in payload.get("issues_before", [])],
            "",
            "已修復:",
            *[f"- {x}" for x in payload.get("fixed_issues", [])],
            "",
            "仍需人工處理:",
            *[f"- {x}" for x in payload.get("requires_manual_repair", [])],
            "",
            "答案 label 分布:",
            f"- 修復前: {payload.get('choice_answer_label_counts_before', {})}",
            f"- 修復後: {payload.get('choice_answer_label_counts_after', {})}",
            "",
            "Audit 狀態:",
            f"- 修復前: {payload.get('audit_status_before', '')}",
            f"- 修復後: {payload.get('audit_status_after', '')}",
            "",
            "修改檔案:",
            *[f"- {x}" for x in payload.get("source_files_modified", [])],
            "",
            "下一步建議:",
            "重新執行：",
            f"python scripts\\gencode_choice_quality_audit.py --skill-id {payload.get('skill_id', '')} --samples {payload.get('samples', 100)}",
            "============================================================",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    skill_id = args.skill_id.strip()
    samples = max(1, int(args.samples))

    before = _run_choice_audit(skill_id, samples)
    rows = _target_rows(before, skill_id)
    issues_before = sorted(
        set(
            _normalize_issue(issue)
            for row in rows
            for issue in (row.get("issues") or [])
            if _normalize_issue(issue) in REPAIRABLE_ISSUES
        )
    )

    source_files_checked: list[str] = []
    source_files_modified: list[str] = []
    manual_repair: list[str] = []
    for row in rows:
        row_issues = {_normalize_issue(x) for x in (row.get("issues") or [])}
        if not (row_issues & REPAIRABLE_ISSUES):
            continue
        p = Path(str(row.get("path", "")))
        source_files_checked.append(str(p))
        modified, reasons = _repair_source_file(p)
        if modified:
            source_files_modified.append(str(p))
        manual_repair.extend(reasons)

    compile_results: dict[str, str] = {}
    for file_path in source_files_modified:
        cmd = [sys.executable, "-m", "py_compile", file_path]
        proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        compile_results[file_path] = "PASS" if proc.returncode == 0 else f"FAIL:{proc.stderr.strip()}"

    after = _run_choice_audit(skill_id, samples)
    rows_after = _target_rows(after, skill_id)
    issues_after = sorted(
        set(_normalize_issue(issue) for row in rows_after for issue in (row.get("issues") or []))
    )
    fixed_issues = [x for x in issues_before if x not in issues_after]

    before_counts = {
        row.get("module", ""): row.get("choice_answer_label_counts", {})
        for row in rows
        if row.get("choice_question_count", 0) > 0
    }
    after_counts = {
        row.get("module", ""): row.get("choice_answer_label_counts", {})
        for row in rows_after
        if row.get("choice_question_count", 0) > 0
    }

    blocking: list[str] = []
    if after.get("status") != "PASS":
        blocking.append("audit_still_failed")
    blocking.extend([x for x in manual_repair if x.startswith("requires_manual_repair")])

    repair_status = "PASS"
    if blocking and fixed_issues:
        repair_status = "PARTIAL"
    elif blocking and not fixed_issues:
        repair_status = "FAIL"

    out_json = REPORT_DIR / f"{skill_id}_choice_quality_repair.json"
    out_md = REPORT_DIR / f"{skill_id}_choice_quality_repair.md"
    payload = {
        "skill_id": skill_id,
        "samples": samples,
        "repair_status": repair_status,
        "source_files_checked": sorted(set(source_files_checked)),
        "source_files_modified": sorted(set(source_files_modified)),
        "issues_before": issues_before,
        "issues_after": issues_after,
        "fixed_issues": fixed_issues,
        "requires_manual_repair": sorted(set(manual_repair)),
        "choice_answer_label_counts_before": before_counts,
        "choice_answer_label_counts_after": after_counts,
        "audit_status_before": before.get("status"),
        "audit_status_after": after.get("status"),
        "py_compile_results": compile_results,
        "pytest_results": {},
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(after.get("warnings", []))),
        "artifact_paths": {
            "audit_before": str(REPORT_DIR / f"{skill_id}_choice_quality_audit.json"),
            "audit_after": str(REPORT_DIR / f"{skill_id}_choice_quality_audit.json"),
            "repair_json": str(out_json),
            "repair_md": str(out_md),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(out_json, payload)
    _write_md(out_md, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else _summary(payload))


if __name__ == "__main__":
    main()
