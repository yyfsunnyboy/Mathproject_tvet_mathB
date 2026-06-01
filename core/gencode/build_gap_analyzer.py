from __future__ import annotations

from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EQUIVALENCE_REQUIREMENTS: dict[str, dict[str, list[str]]] = {
    "numeric_exact": {
        "required_checkers": ["integer_checker"],
        "required_verifiers": ["numeric_verifier"],
        "required_domain_functions": [],
    },
    "choice_label": {
        "required_checkers": ["choice_label_checker"],
        "required_verifiers": ["choice_verifier"],
        "required_domain_functions": ["choices_unique_validator"],
    },
    "unordered_solution_set": {
        "required_checkers": ["solution_set_checker"],
        "required_verifiers": ["solution_set_verifier"],
        "required_domain_functions": ["equation_solver_domain_function"],
    },
    "interval_set": {
        "required_checkers": ["interval_checker"],
        "required_verifiers": ["interval_verifier"],
        "required_domain_functions": ["interval_domain_function", "interval_formatter"],
    },
    "rational_equivalent": {
        "required_checkers": ["rational_checker"],
        "required_verifiers": ["rational_verifier"],
        "required_domain_functions": [],
    },
    "algebraic_equivalent": {
        "required_checkers": ["algebraic_equivalence_checker"],
        "required_verifiers": ["algebraic_verifier"],
        "required_domain_functions": ["symbolic_simplifier"],
    },
    "manual_review_or_ai_judged": {
        "required_checkers": ["manual_review_checker"],
        "required_verifiers": [],
        "required_domain_functions": [],
    },
}

EQUIVALENCE_COMPONENTS = {
    "numeric_exact": ["integer_or_numeric_checker", "numeric_generator"],
    "choice_label": ["choice_label_checker", "choice_verifier", "choices_unique_validator"],
    "unordered_solution_set": ["solution_set_checker", "solution_set_verifier", "equation_solver_domain_function"],
    "interval_set": ["interval_checker", "interval_verifier", "interval_domain_function", "interval_formatter"],
    "rational_equivalent": ["rational_checker", "fraction_normalizer", "rational_verifier"],
    "algebraic_equivalent": ["algebraic_equivalence_checker", "symbolic_simplifier", "expression_generator"],
    "manual_review_or_ai_judged": ["manual_review_marker", "future_ai_judged_path"],
}


def _collect_existing(path: Path, suffix: str = ".py") -> set[str]:
    if not path.exists():
        return set()
    out = set()
    for p in path.glob(f"*{suffix}"):
        if p.name.startswith("_"):
            continue
        out.add(p.stem)
    return out


def analyze_build_dependency_plan(phase1_report: dict[str, Any], phase2_report: dict[str, Any]) -> dict[str, Any]:
    answer_contract_summary = phase2_report.get("answer_contract_summary") or phase1_report.get("answer_contract_summary") or {}
    manual_review = set(phase2_report.get("manual_review_problem_types") or phase1_report.get("manual_review_problem_types") or [])
    observed = set(phase1_report.get("observed_problem_types") or answer_contract_summary.keys())
    buildable = sorted([pt for pt in observed if pt not in manual_review])
    blocked = sorted(list(manual_review))

    required_checkers: set[str] = set()
    required_verifiers: set[str] = set()
    required_domain_functions: set[str] = set()
    required_generators: set[str] = set(buildable)

    for pt in buildable:
        c = answer_contract_summary.get(pt, {}) if isinstance(answer_contract_summary.get(pt), dict) else {}
        eq = str(c.get("equivalence_type", "")).strip()
        checker = str(c.get("checker_key", "")).strip()
        req = EQUIVALENCE_REQUIREMENTS.get(eq, {"required_checkers": [], "required_verifiers": [], "required_domain_functions": []})
        required_checkers.update(req["required_checkers"])
        required_verifiers.update(req["required_verifiers"])
        required_domain_functions.update(req["required_domain_functions"])
        if checker:
            required_checkers.add(checker)

    existing_checkers = _collect_existing(PROJECT_ROOT / "core" / "checkers") | {
        "integer_checker",
        "numeric_checker",
        "exact_string_checker",
        "choice_checker",
        "choice_label_checker",
    }
    existing_verifiers = _collect_existing(PROJECT_ROOT / "core" / "verifiers") | {
        "numeric_verifier",
        "rational_verifier",
        "algebraic_verifier",
    }
    existing_domain_functions = _collect_existing(PROJECT_ROOT / "core" / "domain")

    gen_root = PROJECT_ROOT / "generated_candidates" / "vocational_math_b1"
    existing_generators: set[str] = set()
    if gen_root.exists():
        for pt in buildable:
            for sec_dir in gen_root.glob("section_*"):
                if (sec_dir / pt).exists():
                    existing_generators.add(pt)
                    break

    missing_checkers = sorted(required_checkers - existing_checkers)
    missing_verifiers = sorted(required_verifiers - existing_verifiers)
    missing_domain_functions = sorted(required_domain_functions - existing_domain_functions)
    missing_generators = sorted(required_generators - existing_generators)

    foundation_ready = not any([missing_checkers, missing_verifiers, missing_domain_functions, missing_generators])
    preflight_status = "PASS" if foundation_ready else "REPAIR_REQUIRED"
    return {
        "foundation_ready": foundation_ready,
        "required_checkers": sorted(required_checkers),
        "existing_checkers": sorted(existing_checkers),
        "missing_checkers": missing_checkers,
        "required_verifiers": sorted(required_verifiers),
        "missing_verifiers": missing_verifiers,
        "required_domain_functions": sorted(required_domain_functions),
        "missing_domain_functions": missing_domain_functions,
        "required_generators": sorted(required_generators),
        "missing_generators": missing_generators,
        "excluded_manual_review_problem_types": blocked,
        "buildable_problem_types": buildable,
        "blocked_problem_types": blocked,
        "preflight_status": preflight_status,
    }


def analyze_build_gaps(phase1_report: dict[str, Any], phase2_report: dict[str, Any]) -> dict[str, Any]:
    answer_contract_summary = phase2_report.get("answer_contract_summary") or phase1_report.get("answer_contract_summary") or {}
    failed = set(phase2_report.get("failed_problem_types") or [])
    generated = set(phase2_report.get("generated_problem_types") or [])
    manual_review = set(phase2_report.get("manual_review_problem_types") or [])
    blocking_reasons = set(phase2_report.get("blocking_reasons") or [])
    wrapper = phase2_report.get("wrapper_summary") or {}
    dep = phase2_report.get("build_dependency_plan") or {}

    problem_type_gaps: dict[str, Any] = {}
    all_pts = set(answer_contract_summary.keys()) | failed | manual_review
    global_gap_types: set[str] = set()

    for pt in sorted(all_pts):
        c = answer_contract_summary.get(pt, {}) if isinstance(answer_contract_summary.get(pt), dict) else {}
        eq = str(c.get("equivalence_type", "")).strip()
        checker_key = str(c.get("checker_key", "")).strip()
        answer_type = str(c.get("answer_type", "")).strip()
        gaps: list[str] = []
        actions: list[str] = []

        if pt in manual_review:
            gaps.append("manual_review_unresolved")
            actions.append("保留 manual_review 或先修正來源題庫")
        if checker_key and checker_key in set(dep.get("missing_checkers", [])):
            gaps.append("missing_checker")
            actions.append(f"建立或註冊 {checker_key}")
        if eq in {"interval_set", "unordered_solution_set", "algebraic_equivalent"} and dep.get("missing_domain_functions"):
            gaps.append("missing_domain_function")
            actions.append("建立 domain solver / formatter")
        if eq not in {"", "exact_string", "numeric_exact"} and dep.get("missing_verifiers"):
            gaps.append("missing_equivalence_verifier")
            actions.append(f"補上 {eq} verifier tests")
        if pt in set(dep.get("missing_generators", [])) or (pt in failed and pt not in generated and pt not in manual_review):
            gaps.append("missing_generator")
            actions.append("建立 deterministic generator")
        if wrapper.get("pipeline_invoked") is True and str(wrapper.get("pipeline_final_status", "")) == "FAIL":
            gaps.append("missing_wrapper_candidate")
            actions.append("補齊 wrapper 對應 verified candidates")
        if "missing_answer_contract_problem_types" in blocking_reasons:
            p2_missing = phase2_report.get("missing_answer_contract_problem_types", [])
            p1_missing = phase1_report.get("missing_answer_contract_problem_types", [])
            if not p2_missing and not p1_missing and answer_contract_summary:
                gaps.append("possible_gate_inconsistency")
                actions.append("檢查 Phase2 gate 條件與 summary 一致性")
        if not gaps:
            continue
        recommended = EQUIVALENCE_COMPONENTS.get(eq, [])
        severity = "high" if any(g in gaps for g in ["missing_generator", "missing_checker", "missing_wrapper_candidate"]) else "medium"
        problem_type_gaps[pt] = {
            "answer_type": answer_type,
            "equivalence_type": eq,
            "checker_key": checker_key,
            "gap_types": sorted(set(gaps)),
            "recommended_components": recommended,
            "suggested_next_actions": sorted(set(actions)),
            "severity": severity,
        }
        global_gap_types.update(gaps)

    has_build_gaps = bool(problem_type_gaps or global_gap_types)
    steps = [
        {"step_id": "S1", "title": "建立或驗證 checker/verifier", "action_type": "implement_or_register_checker", "target": "equivalence_type 對應 checker/verifier", "reason": "優先打通答案等價判分", "depends_on": [], "safe_to_auto_generate": True, "requires_human_review": False},
        {"step_id": "S2", "title": "建立 domain function", "action_type": "implement_domain_function", "target": "interval/solution_set/algebraic 題型 domain solver", "reason": "支援非單純數值題型", "depends_on": ["S1"], "safe_to_auto_generate": True, "requires_human_review": False},
        {"step_id": "S3", "title": "建立 deterministic generators", "action_type": "implement_generator", "target": "failed deterministic problem types", "reason": "補齊可生成題型", "depends_on": ["S1", "S2"], "safe_to_auto_generate": False, "requires_human_review": True},
        {"step_id": "S4", "title": "修復 wrapper candidates", "action_type": "fix_wrapper_candidate_linking", "target": "verified candidates / wrapper pipeline", "reason": "避免 wrapper verify fail", "depends_on": ["S3"], "safe_to_auto_generate": False, "requires_human_review": True},
        {"step_id": "S5", "title": "重跑 Phase 2", "action_type": "rerun_phase2", "target": "scripts/gencode_pipeline_phase2_build.py", "reason": "驗證缺口是否修復", "depends_on": ["S4"], "safe_to_auto_generate": True, "requires_human_review": False},
    ]
    return {
        "build_gap_summary": {"has_build_gaps": has_build_gaps, "gap_types": sorted(global_gap_types), "problem_type_gaps": problem_type_gaps},
        "repair_plan": {"recommended_next_action": "fix_build_gaps_then_rerun_phase2" if has_build_gaps else "phase2_ready", "steps": steps if has_build_gaps else []},
        "repair_plan_status": "GENERATED" if has_build_gaps else "SKIPPED",
    }

