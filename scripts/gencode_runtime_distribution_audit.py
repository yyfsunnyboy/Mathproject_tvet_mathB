from __future__ import annotations

import argparse
import importlib
import json
from collections import Counter
from pathlib import Path
from typing import Any
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_md(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        f"# Runtime Distribution Audit: {payload.get('skill_id', '')}",
        "",
        f"- status: {payload.get('status', '')}",
        f"- samples: {payload.get('samples', 0)}",
        f"- expected_problem_types: {payload.get('expected_problem_types', [])}",
        f"- observed_problem_types: {payload.get('observed_problem_types', [])}",
        f"- missing_problem_types: {payload.get('missing_problem_types', [])}",
        f"- choice_answer_label_counts: {payload.get('choice_answer_label_counts', {})}",
        f"- blocking_reasons: {payload.get('blocking_reasons', [])}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _summary(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "============================================================",
            "Gencode Runtime 品質稽核摘要",
            "============================================================",
            f"skill_id: {payload.get('skill_id', '')}",
            f"samples: {payload.get('samples', 0)}",
            f"status: {payload.get('status', '')}",
            f"expected_problem_types: {payload.get('expected_problem_types', [])}",
            f"observed_problem_types: {payload.get('observed_problem_types', [])}",
            f"missing_problem_types: {payload.get('missing_problem_types', [])}",
            f"choice_question_count: {payload.get('choice_question_count', 0)}",
            f"choice_answer_label_counts: {payload.get('choice_answer_label_counts', {})}",
            f"choice_answer_fixed_label_detected: {str(bool(payload.get('choice_answer_fixed_label_detected', False))).lower()}",
            f"blocking_reasons: {payload.get('blocking_reasons', [])}",
            "============================================================",
        ]
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-id", required=True)
    p.add_argument("--samples", type=int, default=200)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    skill_id = args.skill_id
    samples = max(1, int(args.samples))
    phase2 = _read_json(REPORT_DIR / f"{skill_id}_phase2_build.json")
    phase3 = _read_json(REPORT_DIR / f"{skill_id}_pipeline_final.json")
    expected_problem_types = sorted(set(list(phase2.get("verified_problem_types") or [])))
    manual_review_exclusions = list((phase3.get("publish_binding_summary") or {}).get("publish_exclusions", {}).get("manual_review_problem_types", []) or phase3.get("manual_review_problem_types") or [])

    mod = importlib.import_module(f"skills.{skill_id}")
    counts: Counter[str] = Counter()
    unexpected: set[str] = set()
    manual_leaked: set[str] = set()
    choice_label_counts: Counter[str] = Counter()
    choice_question_count = 0
    blocking_reasons: list[str] = []
    warnings: list[str] = []

    for i in range(samples):
        q = mod.generate(level=1)
        pt = str(q.get("problem_type_id", "")).strip()
        if pt:
            counts[pt] += 1
        if pt in set(manual_review_exclusions):
            manual_leaked.add(pt)
        if expected_problem_types and pt not in set(expected_problem_types):
            unexpected.add(pt)

        eq = str(((q.get("answer_contract") or {}).get("equivalence_type") or "")).strip()
        if eq == "choice_label":
            choice_question_count += 1
            label = str(q.get("answer", "")).strip().upper()
            if label not in {"A", "B", "C", "D"}:
                blocking_reasons.append("invalid_choice_answer_label")
            else:
                choice_label_counts[label] += 1
            choices = list(q.get("choices", []) or [])
            if len(choices) != len(set(choices)):
                blocking_reasons.append("duplicate_choice_options")
            if label in {"A", "B", "C", "D"} and len(choices) >= 4:
                idx = ord(label) - ord("A")
                if idx >= len(choices):
                    blocking_reasons.append("choice_correct_answer_not_in_choices")

    observed_problem_types = sorted(counts.keys())
    missing_problem_types = sorted(set(expected_problem_types) - set(observed_problem_types))
    if missing_problem_types:
        blocking_reasons.append("runtime_distribution_missing_verified_problem_types")
    if manual_leaked:
        blocking_reasons.append("manual_review_problem_type_leaked")
    if choice_question_count >= 20 and len([k for k, v in choice_label_counts.items() if v > 0]) == 1:
        blocking_reasons.append("choice_answer_fixed_label_detected")
    status = "PASS" if not blocking_reasons else "FAIL"
    payload = {
        "skill_id": skill_id,
        "samples": samples,
        "expected_problem_types": expected_problem_types,
        "observed_problem_types": observed_problem_types,
        "distribution_counts": dict(counts),
        "missing_problem_types": missing_problem_types,
        "unexpected_problem_types": sorted(unexpected),
        "manual_review_exclusions": manual_review_exclusions,
        "manual_review_leaked": sorted(manual_leaked),
        "choice_question_count": choice_question_count,
        "choice_answer_label_counts": dict(choice_label_counts),
        "choice_answer_label_distribution_status": "PASS" if "choice_answer_fixed_label_detected" not in blocking_reasons else "FAIL",
        "choice_answer_fixed_label_detected": "choice_answer_fixed_label_detected" in blocking_reasons,
        "status": status,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "warnings": sorted(set(warnings)),
        "timestamp": _read_json(REPORT_DIR / f"{skill_id}_phase3_publish_gate.json").get("timestamp", ""),
    }
    out_json = REPORT_DIR / f"{skill_id}_runtime_distribution_audit.json"
    out_md = REPORT_DIR / f"{skill_id}_runtime_distribution_audit.md"
    _write_json(out_json, payload)
    _write_md(out_md, payload)
    print(json.dumps(payload, ensure_ascii=True) if args.json else _summary(payload))


if __name__ == "__main__":
    main()
