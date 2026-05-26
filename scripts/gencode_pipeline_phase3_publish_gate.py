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

from core.gencode.pipeline_state import read_json, utc_timestamp, write_json, write_md


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-id", required=True)
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
            "artifact_paths": {
                "phase1_json": str(phase1_path),
                "phase2_json": str(phase2_path),
                "final_json": str(out_json),
                "final_md": str(out_md),
            },
            "timestamp": utc_timestamp(),
        }
        write_json(out_json, report)
        write_md(out_md, f"Phase3 Publish Gate: {skill_id}", [("summary", report)])
        print(json.dumps(report, ensure_ascii=True))
        return

    runtime = _runtime_probe(skill_id)
    bootstrap_summary = dict(p2.get("bootstrap_summary") or p1.get("bootstrap_summary") or {})
    bootstrap_mode = bool(bootstrap_summary.get("bootstrap_mode"))
    bootstrap_runtime_status = str(bootstrap_summary.get("bootstrap_runtime_status", "FAIL"))

    missing_answer_contract_problem_types = list(p1.get("missing_answer_contract_problem_types") or [])
    missing_checker_key_problem_types = list(p1.get("missing_checker_key_problem_types") or [])
    equivalence_test_required_problem_types = list(p1.get("equivalence_test_required_problem_types") or [])
    manual_review_problem_types = list(p1.get("manual_review_problem_types") or [])
    future_ai_judged_problem_types = list(p1.get("future_ai_judged_problem_types") or [])
    pending_implementation = list(p2.get("pending_implementation") or [])
    verified_problem_types = list(p2.get("verified_problem_types") or [])
    observed_problem_types = list(p1.get("observed_problem_types") or [])
    source_coverage_status = str(p1.get("source_coverage_status", "INSUFFICIENT_SOURCE_EXAMPLES"))

    full_observed_coverage = (
        source_coverage_status == "FULL_OBSERVED_COVERAGE_CANDIDATE"
        and not missing_answer_contract_problem_types
        and not missing_checker_key_problem_types
        and not pending_implementation
        and not manual_review_problem_types
        and runtime.get("import_ok")
        and runtime.get("generate_ok")
        and runtime.get("check_ok")
    )

    blocking_reasons: list[str] = []
    warnings: list[str] = []
    if not runtime.get("import_ok"):
        blocking_reasons.append("import_failed")
    if not runtime.get("generate_ok"):
        blocking_reasons.append("generate_failed")
    if not runtime.get("check_ok"):
        blocking_reasons.append("checker_failed")
    if missing_answer_contract_problem_types:
        blocking_reasons.append("answer_contract_gate_failed")
    if missing_checker_key_problem_types:
        blocking_reasons.append("missing_checker_key_problem_types")
    if pending_implementation:
        warnings.append("pending_implementation_present")
    if manual_review_problem_types:
        warnings.append("manual_review_problem_types_present")
    if future_ai_judged_problem_types:
        warnings.append("future_ai_judged_problem_types_present")

    if bootstrap_mode and bootstrap_runtime_status == "PASS" and runtime.get("import_ok") and runtime.get("generate_ok"):
        final_status = "PASS_BOOTSTRAP_ONLY"
        publish_ready = True
        full_observed_coverage = False
    elif full_observed_coverage and not blocking_reasons:
        final_status = "PASS"
        publish_ready = True
    elif blocking_reasons:
        final_status = "FAIL"
        publish_ready = False
    else:
        final_status = "PARTIAL"
        publish_ready = False

    runtime_problem_type_coverage = {
        "expected_problem_types": observed_problem_types,
        "observed_problem_types": sorted(set(verified_problem_types or [runtime.get("sample_problem_type", "")]) - {""}),
        "missing_problem_types": sorted(set(observed_problem_types) - set(verified_problem_types)),
        "status": "pass" if final_status in {"PASS", "PASS_BOOTSTRAP_ONLY"} else "fail",
    }

    report = {
        "skill_id": skill_id,
        "phase": "phase3_publish_gate",
        "final_status": final_status,
        "publish_ready": publish_ready,
        "full_observed_coverage": full_observed_coverage,
        "source_coverage_status": source_coverage_status,
        "bootstrap_summary": {
            **bootstrap_summary,
            "bootstrap_mode": bootstrap_mode,
            "bootstrap_runtime_status": bootstrap_runtime_status,
        },
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
        "equivalence_test_required_problem_types": equivalence_test_required_problem_types,
        "runtime_problem_type_coverage": runtime_problem_type_coverage,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "warnings": sorted(set(warnings)),
        "artifact_paths": {
            "phase1_json": str(phase1_path),
            "phase2_json": str(phase2_path),
            "final_json": str(out_json),
            "final_md": str(out_md),
        },
        "timestamp": utc_timestamp(),
    }
    write_json(out_json, report)
    write_md(out_md, f"Phase3 Publish Gate: {skill_id}", [("summary", report)])
    print(json.dumps(report, ensure_ascii=True))


if __name__ == "__main__":
    main()
