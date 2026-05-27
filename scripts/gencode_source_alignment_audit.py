from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_text(text: str) -> str:
    return " ".join(str(text or "").replace("\r", " ").replace("\n", " ").split())


def _count_abs_ineq_parts(text: str) -> int:
    s = _normalize_text(text)
    parts = re.split(r"\(\d+\)|[①②③④⑤⑥⑦⑧⑨⑩]", s)
    count = 0
    for part in parts:
        if "|" in part and re.search(r"(<=|>=|<|>|≤|≥)", part):
            count += 1
    return max(count, 0)


def _classify_source_form(text: str) -> str:
    s = _normalize_text(text)
    if not s or "|" not in s:
        return "malformed_or_unknown"
    if "整數" in s and "幾個" in s:
        return "integer_solution_count_choice"
    part_count = _count_abs_ineq_parts(s)
    if part_count >= 2:
        return "multi_part_abs_ineq_solving"
    if re.search(r"\|\s*[1-9]\d*\s*x", s):
        return "single_linear_abs_ineq"
    if re.search(r"\|\s*x\s*[+-]\s*\d+", s):
        return "single_shifted_abs_ineq"
    if re.search(r"\|\s*x\s*\|", s):
        return "single_zero_center_abs_ineq"
    if re.search(r"\|[^|]*x[^|]*\|", s):
        return "single_linear_abs_ineq"
    return "malformed_or_unknown"


def _problem_type_to_source_form(problem_type_id: str) -> str:
    p = str(problem_type_id or "")
    if "integer_solution_count_choice" in p:
        return "integer_solution_count_choice"
    if "shifted_basic" in p:
        return "single_shifted_abs_ineq"
    if "linear_expression_basic" in p:
        return "single_linear_abs_ineq"
    if "zero_center_basic" in p:
        return "single_zero_center_abs_ineq"
    if "malformed_source_review" in p:
        return "malformed_or_unknown"
    return "malformed_or_unknown"


def _runtime_form_from_verified(verified_problem_types: list[str], manual_review: list[str]) -> set[str]:
    forms = set()
    for p in verified_problem_types:
        forms.add(_problem_type_to_source_form(p))
    for p in manual_review:
        if "malformed_source_review" in p:
            forms.add("malformed_or_unknown")
    return forms


def _align_status(
    source_form: str,
    problem_type_id: str,
    runtime_category: str,
    manual_review_reason: str,
    has_verified_generator: bool,
) -> str:
    pt_form = _problem_type_to_source_form(problem_type_id)
    if runtime_category == "manual_review":
        if source_form == "malformed_or_unknown":
            return "MANUAL_REVIEW"
        return "FAIL"
    if not has_verified_generator:
        return "FAIL"
    if source_form == pt_form:
        return "PASS"
    if source_form == "multi_part_abs_ineq_solving" and pt_form in {
        "single_zero_center_abs_ineq",
        "single_shifted_abs_ineq",
        "single_linear_abs_ineq",
    }:
        return "PARTIAL"
    if manual_review_reason and source_form != "malformed_or_unknown":
        return "FAIL"
    return "PARTIAL"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_md(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Gencode Source Alignment Audit",
        "",
        "## 1. 摘要",
        f"- skill_id: {payload.get('skill_id', '')}",
        f"- examples_total: {payload.get('examples_total', 0)}",
        f"- examples_checked: {payload.get('examples_checked', 0)}",
        f"- alignment_status_counts: {payload.get('alignment_status_counts', {})}",
        "",
        "## 2. 例題語意分類統計",
        f"- source_form_counts: {payload.get('source_form_counts', {})}",
        f"- problem_type_counts: {payload.get('problem_type_counts', {})}",
        "",
        "## 3. 逐題對照表",
    ]
    for row in payload.get("example_alignment_table", []):
        lines.extend(
            [
                f"- example_id: {row.get('example_id')}",
                f"  source_form_category: {row.get('source_form_category')}",
                f"  problem_type_id: {row.get('problem_type_id')}",
                f"  alignment_status: {row.get('alignment_status')}",
            ]
        )
    lines.extend(
        [
            "",
            "## 4. 疑似分類錯誤",
            *[f"- {x}" for x in payload.get("possible_classifier_misclassifications", [])],
            "",
            "## 5. Runtime 未覆蓋或低覆蓋題型",
            *[f"- {x}" for x in payload.get("underrepresented_runtime_forms", [])],
            "",
            "## 6. 建議修正",
            *[f"- {x}" for x in payload.get("recommendations", [])],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _summary(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "============================================================",
            "Gencode Source Alignment 稽核摘要",
            "============================================================",
            f"skill_id: {payload.get('skill_id', '')}",
            f"examples_total: {payload.get('examples_total', 0)}",
            f"examples_checked: {payload.get('examples_checked', 0)}",
            f"source_form_counts: {payload.get('source_form_counts', {})}",
            f"alignment_status_counts: {payload.get('alignment_status_counts', {})}",
            f"missing_source_aligned_problem_types: {payload.get('missing_source_aligned_problem_types', [])}",
            f"possible_classifier_misclassifications: {payload.get('possible_classifier_misclassifications', [])}",
            f"underrepresented_runtime_forms: {payload.get('underrepresented_runtime_forms', [])}",
            "============================================================",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    skill_id = args.skill_id.strip()
    phase1 = _load_json(REPORT_DIR / f"{skill_id}_phase1_audit.json")
    phase2 = _load_json(REPORT_DIR / f"{skill_id}_phase2_build.json")
    phase3 = _load_json(REPORT_DIR / f"{skill_id}_pipeline_final.json")
    runtime_audit = _load_json(REPORT_DIR / f"{skill_id}_runtime_distribution_audit.json")

    examples = list(phase1.get("examples_map", []))
    verified_problem_types = list(phase2.get("verified_problem_types", []))
    manual_review_problem_types = list(phase2.get("manual_review_problem_types", []))
    runtime_observed = set(runtime_audit.get("observed_problem_types", []))

    table: list[dict[str, Any]] = []
    source_form_counts: Counter[str] = Counter()
    problem_type_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    missing_source_aligned_problem_types: set[str] = set()
    misclassifications: list[str] = []
    manual_recheck: list[int] = []

    for ex in examples:
        example_id = ex.get("example_id")
        preview = str(ex.get("problem_preview", ""))
        problem_type_id = str(ex.get("problem_type_id", ""))
        runtime_category = str(ex.get("runtime_category", ""))
        manual_review_reason = str(ex.get("manual_review_reason", ""))
        source_form = _classify_source_form(preview)
        has_verified = problem_type_id in verified_problem_types
        alignment = _align_status(source_form, problem_type_id, runtime_category, manual_review_reason, has_verified)

        source_form_counts[source_form] += 1
        problem_type_counts[problem_type_id] += 1
        status_counts[alignment] += 1

        if alignment in {"FAIL", "PARTIAL"} and source_form not in {"malformed_or_unknown"}:
            missing_source_aligned_problem_types.add(source_form)
        if runtime_category == "manual_review" and source_form != "malformed_or_unknown":
            misclassifications.append(
                f"example_id={example_id} problem_type={problem_type_id} source_form={source_form}"
            )
            manual_recheck.append(int(example_id))

        table.append(
            {
                "example_id": example_id,
                "source_preview": preview[:160],
                "classifier_problem_type_id": problem_type_id,
                "problem_type_id": problem_type_id,
                "runtime_category": runtime_category,
                "manual_review_reason": manual_review_reason,
                "verified_generator_exists": has_verified,
                "source_form_category": source_form,
                "alignment_status": alignment,
                "runtime_observed": problem_type_id in runtime_observed,
            }
        )

    runtime_forms = _runtime_form_from_verified(verified_problem_types, manual_review_problem_types)
    underrepresented = sorted(
        form for form, count in source_form_counts.items() if count > 0 and form not in runtime_forms and form != "malformed_or_unknown"
    )

    recommendations: list[str] = []
    if misclassifications:
        recommendations.append("重新檢查 manual_review 分類規則，優先回看疑似誤判 examples。")
    if "multi_part_abs_ineq_solving" in missing_source_aligned_problem_types:
        recommendations.append("新增或擴充 multi-part 絕對值不等式生成能力，避免僅用 single-form 覆蓋。")
    if underrepresented:
        recommendations.append("對 underrepresented source form 建立 source-aligned generator 或 wrapper 出題策略。")
    if not recommendations:
        recommendations.append("目前 source 與 runtime 對齊度良好，維持現行規則並定期抽樣稽核。")

    payload = {
        "skill_id": skill_id,
        "examples_total": int(phase1.get("examples_total", len(examples))),
        "examples_checked": len(examples),
        "source_form_counts": dict(source_form_counts),
        "problem_type_counts": dict(problem_type_counts),
        "alignment_status_counts": dict(status_counts),
        "missing_source_aligned_problem_types": sorted(missing_source_aligned_problem_types),
        "possible_classifier_misclassifications": misclassifications,
        "underrepresented_runtime_forms": underrepresented,
        "manual_review_recheck_needed": sorted(set(manual_recheck)),
        "recommendations": recommendations,
        "example_alignment_table": table,
        "artifact_inputs": {
            "phase1_report": str(REPORT_DIR / f"{skill_id}_phase1_audit.json"),
            "phase2_report": str(REPORT_DIR / f"{skill_id}_phase2_build.json"),
            "phase3_report": str(REPORT_DIR / f"{skill_id}_pipeline_final.json"),
            "runtime_distribution_report": str(REPORT_DIR / f"{skill_id}_runtime_distribution_audit.json"),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    out_json = REPORT_DIR / f"{skill_id}_source_alignment_audit.json"
    out_md = REPORT_DIR / f"{skill_id}_source_alignment_audit.md"
    _write_json(out_json, payload)
    _write_md(out_md, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else _summary(payload))


if __name__ == "__main__":
    main()
