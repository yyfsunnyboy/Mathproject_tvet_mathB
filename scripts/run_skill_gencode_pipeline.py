import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.classifiers.base import DETERMINISTIC_RUNTIME_CATEGORIES, REQUIRED_EXAMPLE_FIELDS

REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"
PENDING_REASON = "closed_loop_generator_not_implemented"
EQUIVALENCE_TYPE_WHITELIST = {
    "exact_string",
    "numeric_exact",
    "rational_equivalent",
    "choice_label",
    "unordered_solution_set",
    "interval_set",
    "algebraic_equivalent",
    "manual_review_or_ai_judged",
}
BOOTSTRAP_ONLY_SKILLS: dict[str, dict[str, str]] = {
    "vh_數學B1_NumberLine": {
        "bootstrap_source_skill_id": "jh_數學1上_NumberLine",
        "source_coverage_status": "INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES",
    }
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
    }
}


def _run_cmd(cmd: list[str], timeout: int = 600) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _parse_json_from_output(output: str) -> dict[str, Any]:
    for line in reversed([ln.strip() for ln in output.splitlines() if ln.strip()]):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return {}


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore

    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _load_registry_verified_problem_types(skill_id: str) -> list[str]:
    reg_path = PROJECT_ROOT / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml"
    reg = _load_yaml(reg_path)
    out: list[str] = []
    for it in reg.get("verified_problem_types", []):
        if not isinstance(it, dict):
            continue
        if str(it.get("skill_id", "")) != skill_id:
            continue
        pt = str(it.get("problem_type_id", "")).strip()
        if pt and pt not in out:
            out.append(pt)
    return out


def _load_registry_review_lists(skill_id: str) -> tuple[list[str], list[str]]:
    reg_path = PROJECT_ROOT / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml"
    reg = _load_yaml(reg_path)
    manual_review: list[str] = []
    visual_or_handwriting: list[str] = []
    for it in (reg.get("manual_review_problem_types", []) or []):
        if not isinstance(it, dict):
            continue
        if str(it.get("skill_id", "")) != skill_id:
            continue
        pt = str(it.get("problem_type_id", "")).strip()
        if pt and pt not in manual_review:
            manual_review.append(pt)
        runtime = str(it.get("runtime_category", "")).strip()
        if runtime in {"visual_or_handwriting", "manual_review"} and pt and pt not in visual_or_handwriting:
            visual_or_handwriting.append(pt)
    return manual_review, visual_or_handwriting


def _resolve_skill_inventory_files(skill_id: str) -> tuple[Path | None, Path | None, Path | None]:
    base = PROJECT_ROOT / "agent_skills_v2"
    for ex_map in base.rglob("examples_map_*.yaml"):
        obj = _load_yaml(ex_map)
        rows = obj.get("examples", [])
        if not isinstance(rows, list):
            continue
        if any(isinstance(r, dict) and str(r.get("skill_id", "")) == skill_id for r in rows):
            parent = ex_map.parent
            pt = next(iter(parent.glob("problem_types_*.yaml")), None)
            sub = next(iter(parent.glob("subskills_*.yaml")), None)
            return ex_map, pt, sub
    return None, None, None


def _is_closed_loop_not_implemented(stderr: str, stdout: str) -> bool:
    msg = f"{stderr}\n{stdout}".lower()
    hints = ["closed_loop_generator_not_implemented", "only supports", "not implemented", "not support"]
    return any(h in msg for h in hints)


def _read_runtime_coverage_from_verify_report(report_path: Path) -> dict[str, Any]:
    if not report_path.exists():
        return {
            "expected_problem_types": [],
            "observed_problem_types": [],
            "missing_problem_types": [],
            "sample_count": 0,
            "status": "fail",
        }
    text = report_path.read_text(encoding="utf-8")
    marker = "## Runtime ProblemType Coverage"
    if marker not in text:
        return {
            "expected_problem_types": [],
            "observed_problem_types": [],
            "missing_problem_types": [],
            "sample_count": 0,
            "status": "fail",
        }
    try:
        chunk = text.split(marker, 1)[1]
        j = chunk.split("```json", 1)[1].split("```", 1)[0]
        data = json.loads(j)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {
        "expected_problem_types": [],
        "observed_problem_types": [],
        "missing_problem_types": [],
        "sample_count": 0,
        "status": "fail",
    }


def _build_report(
    report_path: Path,
    skill_id: str,
    summary: dict[str, Any],
    semantic_audit_summary: dict[str, Any],
    per_pt: list[dict[str, Any]],
    inventory_json: dict[str, Any],
    verify_json: dict[str, Any],
    runtime_coverage: dict[str, Any],
    answer_contract_summary: dict[str, Any],
) -> None:
    lines = [
        f"# Skill Gencode Pipeline Report: {skill_id}",
        "",
        "## Summary",
        "```json",
        json.dumps(summary, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Semantic Audit Summary",
        "```json",
        json.dumps(semantic_audit_summary, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Problem Type Closed Loop",
    ]
    for x in per_pt:
        lines.append(f"- {x['problem_type_id']}: status={x['status']}" + (f", reason={x['reason']}" if x.get("reason") else ""))
    lines += [
        "",
        "## Answer Contract Coverage",
        "```json",
        json.dumps(answer_contract_summary, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Runtime ProblemType Coverage",
        "```json",
        json.dumps(runtime_coverage, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Inventory",
        "```json",
        json.dumps(inventory_json, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Verify",
        "```json",
        json.dumps(verify_json, ensure_ascii=False, indent=2),
        "```",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _bootstrap_runtime_probe(skill_id: str) -> bool:
    try:
        mod = __import__(f"skills.{skill_id}", fromlist=["*"])
        p1 = mod.generate(level=1)
        p2 = mod.generate(level=2)
        if not isinstance(p1, dict) or not isinstance(p2, dict):
            return False
        required = {"skill_id", "question_text", "answer", "correct_answer", "problem_type_id", "answer_contract"}
        if not required.issubset(set(p1.keys())):
            return False
        if not required.issubset(set(p2.keys())):
            return False
        return str(p1.get("skill_id", "")) == skill_id and str(p2.get("skill_id", "")) == skill_id
    except Exception:
        return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--max-rounds", type=int, default=5)
    args = parser.parse_args()

    skill_id = args.skill_id
    report_path = REPORT_DIR / f"{skill_id}_pipeline_report.md"

    inv_cmd = [sys.executable, "scripts/gencode_skill_inventory.py", "--skill-id", skill_id]
    inv_code, inv_out, inv_err = _run_cmd(inv_cmd, timeout=600)
    inv_json = _parse_json_from_output(inv_out)
    inventory_ok = inv_code == 0 and bool(inv_json.get("success"))

    if not inventory_ok:
        final = {
            "success": False,
            "final_status": "FAIL",
            "verified_problem_types": [],
            "pending_implementation": [],
            "failed_problem_types": [],
            "manual_review": [],
            "visual_or_handwriting": [],
            "blocking_reasons": ["inventory_failed"],
            "coverage_status": "INCOMPLETE_PROBLEM_TYPE_COVERAGE",
            "full_skill_coverage": False,
            "semantic_audit_summary": {},
            "runtime_problem_type_coverage": {"status": "fail"},
            "report": str(report_path),
        }
        _build_report(
            report_path,
            skill_id,
            final,
            {},
            [],
            {"stdout": inv_out, "stderr": inv_err, "parsed": inv_json},
            {},
            {"status": "fail"},
            {
                "equivalence_type_whitelist": sorted(EQUIVALENCE_TYPE_WHITELIST),
                "observed_problem_type_answer_contracts": {},
                "missing_answer_contract_problem_types": [],
                "missing_checker_key_problem_types": [],
                "invalid_equivalence_type_problem_types": [],
                "equivalence_test_required_problem_types": [],
            },
        )
        print(json.dumps(final, ensure_ascii=False))
        return

    ex_map_path, pt_path, sub_path = _resolve_skill_inventory_files(skill_id)
    entries = []
    if ex_map_path:
        entries = _load_yaml(ex_map_path).get("examples", [])
        if not isinstance(entries, list):
            entries = []
        entries = [e for e in entries if isinstance(e, dict) and str(e.get("skill_id", "")) == skill_id]

    problem_types = _load_yaml(pt_path).get("items", []) if pt_path else []
    if not isinstance(problem_types, list):
        problem_types = []

    db_examples_total = int(inv_json.get("examples_count", 0)) if isinstance(inv_json.get("examples_count"), int) else 0
    examples_covered = len(entries)

    missing_required_fields_count = 0
    audit_pass_count = 0
    audit_review_required_count = 0
    examples_with_risk_flags = []
    possible_missing_problem_types = []
    observed_det_from_examples = set()

    for e in entries:
        missing = [f for f in REQUIRED_EXAMPLE_FIELDS if f not in e]
        if missing:
            missing_required_fields_count += 1
        status = str(e.get("semantic_audit_status", "")).strip()
        if status == "pass":
            audit_pass_count += 1
        elif status == "review_required":
            audit_review_required_count += 1
        flags = e.get("semantic_risk_flags") if isinstance(e.get("semantic_risk_flags"), list) else []
        if flags:
            examples_with_risk_flags.append({"example_id": e.get("example_id"), "flags": flags})
        if "possible_missing_problem_type" in flags:
            possible_missing_problem_types.append(int(e.get("example_id")) if isinstance(e.get("example_id"), int) else e.get("example_id"))
        runtime = str(e.get("runtime_category", "")).strip()
        pt = str(e.get("problem_type_id", "")).strip()
        if runtime in DETERMINISTIC_RUNTIME_CATEGORIES and pt and pt != "unknown":
            observed_det_from_examples.add(pt)

    deterministic_pts = sorted(observed_det_from_examples)
    declared_pts = {
        str(x.get("problem_type_id", "")).strip()
        for x in problem_types
        if isinstance(x, dict) and str(x.get("runtime_category", "")).strip() in DETERMINISTIC_RUNTIME_CATEGORIES
    }
    deterministic_pts = sorted(set(deterministic_pts) | {p for p in declared_pts if p})
    pt_map = {
        str(x.get("problem_type_id", "")).strip(): x
        for x in problem_types
        if isinstance(x, dict) and str(x.get("problem_type_id", "")).strip()
    }

    observed_answer_contracts: dict[str, Any] = {}
    missing_answer_contract_problem_types: list[str] = []
    missing_checker_key_problem_types: list[str] = []
    invalid_equivalence_type_problem_types: list[str] = []
    equivalence_test_required_problem_types: list[str] = []
    for pt in deterministic_pts:
        row = pt_map.get(pt, {})
        contract = row.get("answer_contract") if isinstance(row, dict) else None
        if not isinstance(contract, dict):
            contract = (ANSWER_CONTRACT_DEFAULTS.get(skill_id, {}) or {}).get(pt)
        if not isinstance(contract, dict):
            missing_answer_contract_problem_types.append(pt)
            observed_answer_contracts[pt] = None
            continue
        observed_answer_contracts[pt] = contract
        checker_key = str(contract.get("checker_key", "")).strip()
        if not checker_key:
            missing_checker_key_problem_types.append(pt)
        eq_type = str(contract.get("equivalence_type", "")).strip()
        if eq_type and eq_type not in EQUIVALENCE_TYPE_WHITELIST:
            invalid_equivalence_type_problem_types.append(pt)
        if eq_type not in {"exact_string", "numeric_exact"}:
            equivalence_test_required_problem_types.append(pt)

    per_pt_results: list[dict[str, Any]] = []
    verified_problem_types = _load_registry_verified_problem_types(skill_id)
    pending_implementation: list[str] = []
    failed_problem_types: list[str] = []
    manual_review_problem_types, visual_or_handwriting_problem_types = _load_registry_review_lists(skill_id)

    for pt in deterministic_pts:
        if not any(isinstance(i, dict) and str(i.get("problem_type_id", "")).strip() == pt for i in problem_types):
            if pt not in pending_implementation and pt not in verified_problem_types:
                pending_implementation.append(pt)
                per_pt_results.append({"problem_type_id": pt, "status": "pending_implementation", "reason": PENDING_REASON})
            continue
        cmd = [
            sys.executable,
            "scripts/gencode_problem_type_closed_loop.py",
            "--skill-id",
            skill_id,
            "--problem-type-id",
            pt,
            "--max-rounds",
            str(args.max_rounds),
        ]
        code, out, err = _run_cmd(cmd, timeout=1200)
        parsed = _parse_json_from_output(out)
        if code == 0 and str(parsed.get("status", "")).lower() == "verified":
            if pt not in verified_problem_types:
                verified_problem_types.append(pt)
            per_pt_results.append({"problem_type_id": pt, "status": "verified"})
        elif _is_closed_loop_not_implemented(err, out):
            if pt not in pending_implementation:
                pending_implementation.append(pt)
            per_pt_results.append({"problem_type_id": pt, "status": "pending_implementation", "reason": PENDING_REASON})
        else:
            if pt not in failed_problem_types:
                failed_problem_types.append(pt)
            per_pt_results.append({"problem_type_id": pt, "status": "failed", "reason": str(parsed.get("first_error", "")).strip() or "closed_loop_failed"})

    verify_cmd = [sys.executable, "scripts/verify_skill_gencode.py", "--skill-id", skill_id]
    v_code, v_out, v_err = _run_cmd(verify_cmd, timeout=1200)
    v_json = _parse_json_from_output(v_out)
    verify_ok = v_code == 0 and bool(v_json.get("success"))
    runtime_coverage = {
        "expected_problem_types": v_json.get("runtime_problem_type_coverage", {}).get("expected_problem_types", []),
        "observed_problem_types": v_json.get("runtime_problem_type_coverage", {}).get("observed_problem_types", []),
        "missing_problem_types": v_json.get("runtime_problem_type_coverage", {}).get("missing_problem_types", []),
        "sample_count": v_json.get("runtime_problem_type_coverage", {}).get("sample_count", 0),
        "status": v_json.get("runtime_problem_type_coverage", {}).get("status", "fail"),
    }
    if runtime_coverage["status"] not in {"pass", "fail"}:
        runtime_coverage["status"] = "pass" if verify_ok else "fail"

    contract_target_pts = sorted(
        set(deterministic_pts)
        | set(runtime_coverage.get("expected_problem_types", []) or [])
        | set(runtime_coverage.get("observed_problem_types", []) or [])
    )
    observed_answer_contracts = {}
    missing_answer_contract_problem_types = []
    missing_checker_key_problem_types = []
    invalid_equivalence_type_problem_types = []
    equivalence_test_required_problem_types = []
    for pt in contract_target_pts:
        row = pt_map.get(pt, {})
        contract = row.get("answer_contract") if isinstance(row, dict) else None
        if not isinstance(contract, dict):
            contract = (ANSWER_CONTRACT_DEFAULTS.get(skill_id, {}) or {}).get(pt)
        if not isinstance(contract, dict):
            missing_answer_contract_problem_types.append(pt)
            observed_answer_contracts[pt] = None
            continue
        observed_answer_contracts[pt] = contract
        checker_key = str(contract.get("checker_key", "")).strip()
        if not checker_key:
            missing_checker_key_problem_types.append(pt)
        eq_type = str(contract.get("equivalence_type", "")).strip()
        if eq_type and eq_type not in EQUIVALENCE_TYPE_WHITELIST:
            invalid_equivalence_type_problem_types.append(pt)
        if eq_type not in {"exact_string", "numeric_exact"}:
            equivalence_test_required_problem_types.append(pt)

    all_observed_deterministic_verified = set(deterministic_pts).issubset(set(verified_problem_types))

    semantic_audit_summary = {
        "examples_total": db_examples_total,
        "examples_covered": examples_covered,
        "required_fields_missing_count": missing_required_fields_count,
        "audit_pass_count": audit_pass_count,
        "audit_review_required_count": audit_review_required_count,
        "examples_with_risk_flags": examples_with_risk_flags,
        "possible_missing_problem_types": possible_missing_problem_types,
        "answer_contract_equivalence_type_whitelist": sorted(EQUIVALENCE_TYPE_WHITELIST),
        "observed_problem_type_answer_contracts": observed_answer_contracts,
        "missing_answer_contract_problem_types": sorted(missing_answer_contract_problem_types),
        "missing_checker_key_problem_types": sorted(missing_checker_key_problem_types),
        "invalid_equivalence_type_problem_types": sorted(invalid_equivalence_type_problem_types),
        "equivalence_test_required_problem_types": sorted(equivalence_test_required_problem_types),
    }

    blocking_reasons: list[str] = []
    if examples_covered != db_examples_total:
        blocking_reasons.append("missing_examples_map_fields")
    if missing_required_fields_count > 0:
        blocking_reasons.append("missing_examples_map_fields")
    if audit_review_required_count > 0:
        blocking_reasons.append("manual_review_not_resolved")
    if possible_missing_problem_types:
        blocking_reasons.append("possible_missing_problem_type")
    if missing_answer_contract_problem_types:
        blocking_reasons.append("missing_answer_contract_problem_types")
    if missing_checker_key_problem_types:
        blocking_reasons.append("missing_checker_key_problem_types")
    if invalid_equivalence_type_problem_types:
        blocking_reasons.append("invalid_equivalence_type_problem_types")
    if not all_observed_deterministic_verified:
        blocking_reasons.append("unverified_observed_problem_type")
    if pending_implementation:
        blocking_reasons.append("pending_implementation_not_empty")
    if failed_problem_types:
        blocking_reasons.append("failed_problem_type_not_empty")
    if manual_review_problem_types or visual_or_handwriting_problem_types:
        blocking_reasons.append("manual_review_not_resolved")
    if not verify_ok:
        blocking_reasons.append("skill_verify_failed")
    if runtime_coverage.get("status") != "pass":
        blocking_reasons.append("runtime_missing_verified_problem_types")

    coverage_ready = (
        examples_covered == db_examples_total
        and missing_required_fields_count == 0
        and audit_review_required_count == 0
        and len(possible_missing_problem_types) == 0
        and not missing_answer_contract_problem_types
        and not missing_checker_key_problem_types
        and not invalid_equivalence_type_problem_types
        and all_observed_deterministic_verified
        and not pending_implementation
        and not failed_problem_types
        and not manual_review_problem_types
        and not visual_or_handwriting_problem_types
        and verify_ok
        and runtime_coverage.get("status") == "pass"
    )

    bootstrap_cfg = BOOTSTRAP_ONLY_SKILLS.get(skill_id)
    bootstrap_runtime_ok = _bootstrap_runtime_probe(skill_id) if bootstrap_cfg else False

    if bootstrap_cfg and bootstrap_runtime_ok:
        final_status = "PASS_BOOTSTRAP_ONLY"
    elif (not inventory_ok) or (not verify_ok) or (len(verified_problem_types) == 0):
        final_status = "FAIL"
    elif coverage_ready:
        final_status = "PASS"
    else:
        final_status = "PARTIAL"

    final = {
        "success": final_status in {"PASS", "PARTIAL", "PASS_BOOTSTRAP_ONLY"},
        "final_status": final_status,
        "verified_problem_types": sorted(verified_problem_types),
        "pending_implementation": sorted(pending_implementation),
        "failed_problem_types": sorted(failed_problem_types),
        "manual_review": sorted(manual_review_problem_types),
        "visual_or_handwriting": sorted(visual_or_handwriting_problem_types),
        "blocking_reasons": sorted(set(blocking_reasons)),
        "coverage_status": "FULL_OBSERVED_COVERAGE" if coverage_ready else "INCOMPLETE_PROBLEM_TYPE_COVERAGE",
        "full_skill_coverage": coverage_ready,
        "full_observed_coverage": coverage_ready,
        "semantic_audit_summary": semantic_audit_summary,
        "runtime_problem_type_coverage": runtime_coverage,
        "report": str(report_path),
    }
    if bootstrap_cfg:
        final["bootstrap_summary"] = {
            "bootstrap_mode": True,
            "bootstrap_source_skill_id": bootstrap_cfg["bootstrap_source_skill_id"],
            "bootstrap_runtime_status": "PASS" if bootstrap_runtime_ok else "FAIL",
            "source_coverage_status": bootstrap_cfg["source_coverage_status"],
            "full_observed_coverage": False,
            "warning": "Bootstrap-only runtime ready; not full DB observed textbook coverage.",
        }
        final["bootstrap_mode"] = True
        final["bootstrap_source_skill_id"] = bootstrap_cfg["bootstrap_source_skill_id"]
        final["bootstrap_runtime_status"] = "PASS" if bootstrap_runtime_ok else "FAIL"
        final["source_coverage_status"] = bootstrap_cfg["source_coverage_status"]

    _build_report(
        report_path=report_path,
        skill_id=skill_id,
        summary=final,
        semantic_audit_summary=semantic_audit_summary,
        per_pt=per_pt_results,
        inventory_json={"stdout": inv_out, "stderr": inv_err, "parsed": inv_json},
        verify_json={"stdout": v_out, "stderr": v_err, "parsed": v_json},
        runtime_coverage=runtime_coverage,
        answer_contract_summary={
            "equivalence_type_whitelist": sorted(EQUIVALENCE_TYPE_WHITELIST),
            "observed_problem_type_answer_contracts": observed_answer_contracts,
            "missing_answer_contract_problem_types": sorted(missing_answer_contract_problem_types),
            "missing_checker_key_problem_types": sorted(missing_checker_key_problem_types),
            "invalid_equivalence_type_problem_types": sorted(invalid_equivalence_type_problem_types),
            "equivalence_test_required_problem_types": sorted(equivalence_test_required_problem_types),
        },
    )
    print(json.dumps(final, ensure_ascii=False))


if __name__ == "__main__":
    main()
