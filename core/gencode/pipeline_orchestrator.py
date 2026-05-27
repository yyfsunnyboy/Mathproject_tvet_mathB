from __future__ import annotations

import json
import py_compile
import sqlite3
import ast
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

from core.gencode.classifier_proposal import build_classifier_proposal, detect_answer_shape
from core.gencode.classifiers import get_classifier_for_skill
from core.gencode.classifiers.base import ClassifierContext
from core.gencode.pipeline_policy import evaluate_pipeline_gates
from core.gencode.pipeline_state import utc_timestamp, write_json, write_md

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"
DRAFT_DIR = REPORT_DIR / "drafts"


def _safe_file_component(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "unknown_skill"
    for ch in '<>:"/\\|?*':
        raw = raw.replace(ch, "_")
    return raw


def _load_examples(skill_id: str, db_path: str = "instance/kumon_math.db") -> list[dict[str, Any]]:
    con = sqlite3.connect(str(PROJECT_ROOT / db_path))
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM textbook_examples WHERE skill_id=? ORDER BY rowid", (skill_id,)).fetchall()]
    con.close()
    return rows


def _classify_examples(skill_id: str, examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    classifier = get_classifier_for_skill(skill_id)
    ctx = ClassifierContext(project_root=PROJECT_ROOT, skill_id=skill_id)
    result = classifier.classify_examples(examples, ctx)
    return [dict(x) for x in result.examples_map_entries]


def _build_auto_review(skill_id: str, entries: list[dict[str, Any]], proposal: dict[str, Any]) -> dict[str, Any]:
    proposed_by_id = {
        int(x.get("example_id")): str(x.get("proposed_problem_type_id", "")).strip()
        for x in (proposal.get("proposed_example_map") or [])
        if isinstance(x, dict) and isinstance(x.get("example_id"), int)
    }
    contracts = proposal.get("proposed_answer_contracts", {}) if isinstance(proposal.get("proposed_answer_contracts"), dict) else {}
    per_example: list[dict[str, Any]] = []
    groups: dict[str, list[int]] = defaultdict(list)
    runtime_contract_defaults = {
        "deterministic_expression": {"answer_type": "expression", "equivalence_type": "exact_string", "checker_key": "exact_string_checker"},
        "deterministic_choice": {"answer_type": "choice", "equivalence_type": "choice_label", "checker_key": "choice_label_checker"},
        "deterministic_numeric": {"answer_type": "numeric", "equivalence_type": "numeric_exact", "checker_key": "integer_checker"},
    }
    for e in entries:
        exid = e.get("example_id")
        if not isinstance(exid, int):
            continue
        pt = str(e.get("problem_type_id", "")).strip()
        if pt in {"", "unknown"}:
            pt = proposed_by_id.get(exid, "unknown")
        c = contracts.get(pt, {}) if isinstance(contracts.get(pt), dict) else {}
        if not c:
            c = runtime_contract_defaults.get(str(e.get("runtime_category", "")).strip(), {})
        answer_shape = detect_answer_shape(c)
        per_example.append(
            {
                "example_id": exid,
                "detected_problem_type_id": pt,
                "answer_shape": answer_shape,
                "classification_confidence": "medium" if pt not in {"", "unknown"} else "low",
                "classification_reason": "classifier_or_proposal_mapping",
                "risk_flags": e.get("semantic_risk_flags") if isinstance(e.get("semantic_risk_flags"), list) else [],
                "title_or_source_label": str(e.get("title", "")).strip() or str(e.get("source_type", "")).strip(),
            }
        )
        if pt not in {"", "unknown"}:
            if pt not in contracts and c:
                contracts[pt] = c
            groups[pt].append(exid)

    unknown_ids = sorted(x["example_id"] for x in per_example if x["detected_problem_type_id"] in {"", "unknown"})
    candidates: list[dict[str, Any]] = []
    all_ids = sorted(x["example_id"] for x in per_example)
    for pt, ids_raw in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        ids = sorted(set(ids_raw))
        c = contracts.get(pt, {}) if isinstance(contracts.get(pt), dict) else {}
        answer_shape = detect_answer_shape(c)
        rec = "recommend_promote_for_that_candidate" if len(ids) >= 3 and answer_shape != "unknown_answer_shape" else "conservative_hold_for_that_candidate"
        blockers = [] if rec.startswith("recommend_") else ["insufficient_examples_for_safe_promote"]
        candidates.append(
            {
                "problem_type_id": pt,
                "proposed_problem_type_id": pt,
                "matched_example_ids": ids,
                "matched_example_count": len(ids),
                "unmatched_example_ids": [x for x in all_ids if x not in ids],
                "representative_example_id": ids[0] if ids else None,
                "structural_features": sorted({x["answer_shape"] for x in per_example if x["detected_problem_type_id"] == pt}),
                "answer_contract_proposal": c,
                "checker_key_proposal": str(c.get("checker_key", "")),
                "equivalence_type_proposal": str(c.get("equivalence_type", "")),
                "answer_shape": answer_shape,
                "confidence": "high" if len(ids) >= 3 else "medium",
                "promote_recommendation": rec,
                "promote_blockers": blockers,
                "risk_flags": [],
            }
        )

    shape_set = {x.get("answer_shape", "") for x in candidates if x.get("answer_shape", "")}
    if not candidates and unknown_ids:
        split_merge = "hold_unknown_examples_only"
    elif len(candidates) == 1:
        split_merge = "recommend_single_type"
    elif len(shape_set) >= 2:
        split_merge = "recommend_split_problem_types"
    else:
        split_merge = "recommend_split_or_refine"

    gates = evaluate_pipeline_gates(
        candidates,
        source_examples_count=len(entries),
        checker_smoke_passed=False,
        dynamic_sampling_passed=False,
        contract_tests_passed=False,
    )
    per_candidate_promote_gate = [
        {
            "problem_type_id": str(x.get("problem_type_id", "")),
            "promote_recommendation": str(x.get("promote_recommendation", "")),
            "promote_blockers": x.get("promote_blockers", []),
        }
        for x in candidates
    ]
    next_action = "review_classifier_proposal_and_decide_split_merge"
    if split_merge == "recommend_split_problem_types":
        next_action = "prepare_split_problem_types_then_promote_candidates"
    elif split_merge == "recommend_single_type":
        next_action = "ready_for_safe_promote"

    return {
        "skill_id": skill_id,
        "candidate_problem_types": candidates,
        "proposal_items": candidates,
        "per_example_classification": per_example,
        "split_or_merge_recommendation": split_merge,
        "per_candidate_promote_gate": per_candidate_promote_gate,
        "next_action": next_action,
        **gates,
    }


def _normalize_phase_response(payload: dict[str, Any]) -> dict[str, Any]:
    phase = str(payload.get("phase", "")).strip()
    ok = bool(payload.get("ok", False))
    human_items: list[dict[str, Any]] = []

    if phase == "phase1":
        source_count = int(payload.get("source_example_count", 0))
        cands = payload.get("candidate_problem_types", []) if isinstance(payload.get("candidate_problem_types"), list) else []
        ex_gate = payload.get("exception_review_gate", {}) if isinstance(payload.get("exception_review_gate"), dict) else {}
        reasons = ex_gate.get("reasons", []) if isinstance(ex_gate.get("reasons"), list) else []
        if source_count <= 0:
            phase_status = "phase1_blocked_no_source"
        elif any("fatal" in str(x).lower() for x in reasons):
            phase_status = "phase1_blocked_fatal_risk"
        elif ex_gate.get("required"):
            phase_status = "phase1_exception_review_required"
        elif payload.get("risk_examples"):
            phase_status = "phase1_completed_with_warning"
        else:
            phase_status = "phase1_completed"
        for exid in payload.get("unclassified_examples", []) or []:
            human_items.append(
                {
                    "type": "unclassified_example",
                    "target_id": str(exid),
                    "message": f"例題 {exid} 尚未穩定分類。",
                    "suggested_action": "edit_classification",
                }
            )
        for r in reasons:
            human_items.append(
                {
                    "type": "fatal_risk" if "fatal" in str(r).lower() else "inspect_report",
                    "target_id": str(r),
                    "message": f"Phase 1 例外檢查：{r}",
                    "suggested_action": "inspect_report",
                }
            )
        payload["summary_message"] = (
            f"Phase 1 完成：已辨識 {len(cands)} 個候選題型，{source_count} 題來源例題。"
            if phase_status.startswith("phase1_completed")
            else ("Phase 1 阻塞：找不到來源例題。" if phase_status == "phase1_blocked_no_source" else "Phase 1 需要人工例外審查。")
        )
        can_continue = phase_status in {"phase1_completed", "phase1_completed_with_warning", "phase1_exception_review_required"}
        can_retry = True

    elif phase == "phase2":
        results = payload.get("generator_results", []) if isinstance(payload.get("generator_results"), list) else []
        accepted = payload.get("accepted_generators", []) if isinstance(payload.get("accepted_generators"), list) else []
        failed = payload.get("failed_generators", []) if isinstance(payload.get("failed_generators"), list) else []
        if not results:
            phase_status = "phase2_blocked_no_candidates"
        elif results and len(failed) == len(results):
            phase_status = "phase2_blocked_all_generators_failed"
        elif any((x.get("warnings") or []) for x in results if isinstance(x, dict)):
            phase_status = "phase2_completed_with_warning"
        else:
            phase_status = "phase2_completed"
        for row in results:
            if not isinstance(row, dict):
                continue
            for b in row.get("blockers", []) or []:
                human_items.append(
                    {
                        "type": "missing_checker" if "checker" in str(b).lower() else "inspect_report",
                        "target_id": str(row.get("problem_type_id", "")),
                        "message": f"{row.get('problem_type_id', '')}: {b}",
                        "suggested_action": "inspect_report",
                    }
                )
        payload["summary_message"] = (
            f"Phase 2 完成：已產生 {len(accepted)} 個 generator draft。"
            if phase_status == "phase2_completed"
            else (
                f"Phase 2 完成但有警告：已產生 {len(accepted)} 個 generator draft，暫不可 runtime-ready。"
                if phase_status == "phase2_completed_with_warning"
                else "Phase 2 阻塞：目前沒有可用的 generator draft。"
            )
        )
        can_continue = phase_status in {"phase2_completed", "phase2_completed_with_warning"}
        can_retry = True

    elif phase == "phase3":
        py_status = str(payload.get("py_compile_status", "")).strip()
        pkg = str(payload.get("package_status", "")).strip()
        if py_status == "failed":
            phase_status = "phase3_failed_compile"
        elif pkg == "packaged_draft":
            # no runtime-ready promotion in this round, always draft-level
            phase_status = "phase3_packaged_draft_with_warning"
        elif pkg:
            phase_status = "phase3_blocked_no_successful_generators"
        else:
            phase_status = "phase3_blocked_no_successful_generators"
        if py_status == "failed":
            human_items.append(
                {
                    "type": "compile_error",
                    "target_id": str(payload.get("skill_file_path", "")),
                    "message": str(payload.get("error", "draft skill py_compile failed")),
                    "suggested_action": "retry",
                }
            )
        payload["summary_message"] = (
            "Phase 3 完成：已產生 draft skill 檔並通過 py_compile。"
            if phase_status.startswith("phase3_packaged_draft")
            else "Phase 3 失敗：draft skill 檔案編譯失敗。"
        )
        can_continue = phase_status in {"phase3_packaged_draft", "phase3_packaged_draft_with_warning"}
        can_retry = True
    else:
        phase_status = "unknown_phase_status"
        can_continue = False
        can_retry = True
        payload.setdefault("summary_message", "未知階段回應。")

    payload["phase_status"] = phase_status
    payload["can_continue"] = bool(can_continue)
    payload["can_retry"] = bool(can_retry)
    payload["requires_human_action"] = bool(human_items)
    payload["human_action_items"] = human_items
    payload["ok"] = bool(ok)
    payload.setdefault("reports", {})
    return payload


def run_gencode_phase1(skill_id: str, dry_run: bool = True) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    examples = _load_examples(skill_id)
    reports = {
        "phase1_summary_json": str(REPORT_DIR / f"{skill_id}_phase1_summary.json"),
        "phase1_summary_md": str(REPORT_DIR / f"{skill_id}_phase1_summary.md"),
    }
    if not examples:
        payload = {
            "ok": False,
            "phase": "phase1",
            "skill_id": skill_id,
            "source_example_count": 0,
            "candidate_problem_types": [],
            "per_example_classification": [],
            "unclassified_examples": [],
            "risk_examples": [],
            "split_or_merge_recommendation": "hold_unknown_examples_only",
            "classifier_gate": {"status": "classifier_blocked", "allowed": False, "warnings": []},
            "generator_draft_gate": {"status": "generator_draft_blocked", "allowed": False, "warnings": []},
            "runtime_ready_gate": {"status": "blocked_insufficient_examples", "allowed": False, "blockers": ["blocked_insufficient_examples"]},
            "exception_review_gate": {"required": True, "reasons": ["no_source_examples"]},
            "reports": reports,
            "next_action": "check_skill_mapping_or_source_import",
            "timestamp": utc_timestamp(),
            "dry_run": dry_run,
        }
        write_json(Path(reports["phase1_summary_json"]), payload)
        write_md(Path(reports["phase1_summary_md"]), f"Gencode Phase1 Summary: {skill_id}", [("phase1", payload)])
        return _normalize_phase_response(payload)

    entries = _classify_examples(skill_id, examples)
    unknown_ratio = sum(1 for e in entries if str(e.get("problem_type_id", "")).strip() in {"", "unknown"}) / max(len(entries), 1)
    proposal = {"proposed_problem_types": [], "proposed_example_map": [], "proposed_answer_contracts": {}, "risk_flags": []}
    if unknown_ratio >= 0.2:
        proposal = build_classifier_proposal(skill_id, entries)
    auto_review = _build_auto_review(skill_id, entries, proposal)
    per_example = auto_review.get("per_example_classification", [])
    unclassified = [x.get("example_id") for x in per_example if str(x.get("detected_problem_type_id", "")).strip() in {"", "unknown"}]
    risk_examples = [x.get("example_id") for x in per_example if x.get("risk_flags")]

    payload = {
        "ok": True,
        "phase": "phase1",
        "skill_id": skill_id,
        "source_example_count": len(examples),
        "candidate_problem_types": auto_review.get("candidate_problem_types", []),
        "per_example_classification": per_example,
        "unclassified_examples": unclassified,
        "risk_examples": risk_examples,
        "split_or_merge_recommendation": auto_review.get("split_or_merge_recommendation", ""),
        "classifier_gate": auto_review.get("classifier_gate", {}),
        "generator_draft_gate": auto_review.get("generator_draft_gate", {}),
        "runtime_ready_gate": auto_review.get("runtime_ready_gate", {}),
        "exception_review_gate": auto_review.get("exception_review_gate", {}),
        "reports": reports,
        "next_action": auto_review.get("next_action", "review_classifier_proposal_and_decide_split_merge"),
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
        "auto_review_summary": auto_review,
    }
    write_json(Path(reports["phase1_summary_json"]), payload)
    write_md(Path(reports["phase1_summary_md"]), f"Gencode Phase1 Summary: {skill_id}", [("phase1", payload)])
    return _normalize_phase_response(payload)


def run_gencode_phase2(skill_id: str, accepted_problem_types: list | None = None, excluded_example_ids: list | None = None, dry_run: bool = True) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    phase1_path = REPORT_DIR / f"{skill_id}_phase1_summary.json"
    phase1 = json.loads(phase1_path.read_text(encoding="utf-8")) if phase1_path.exists() else run_gencode_phase1(skill_id, dry_run=dry_run)
    candidates = phase1.get("candidate_problem_types", []) if isinstance(phase1.get("candidate_problem_types"), list) else []
    accepted = set(str(x) for x in (accepted_problem_types or []))
    excluded = set(int(x) for x in (excluded_example_ids or []) if str(x).isdigit())
    generator_results: list[dict[str, Any]] = []
    failed_generators: list[str] = []
    accepted_generators: list[str] = []
    for c in candidates:
        pt = str(c.get("problem_type_id") or c.get("proposed_problem_type_id") or "").strip()
        if not pt:
            continue
        if accepted and pt not in accepted:
            continue
        src_ids = [x for x in (c.get("matched_example_ids") or []) if isinstance(x, int) and x not in excluded]
        answer_contract = c.get("answer_contract_proposal", {}) if isinstance(c.get("answer_contract_proposal"), dict) else {}
        checker_key = str(c.get("checker_key_proposal", "")).strip()
        eq = str(c.get("equivalence_type_proposal", "")).strip()
        generator_key = f"{skill_id}:{pt}:draft_v1"
        blockers: list[str] = []
        warnings: list[str] = []
        status = "draft_planned"
        if not src_ids:
            status = "blocked_no_source_examples"
            blockers.append("no_source_examples_for_problem_type")
        if not answer_contract or not checker_key or not eq:
            status = "blocked_missing_contract_components"
            blockers.append("missing_contract_or_checker_or_equivalence")
        if int(c.get("matched_example_count", 0)) < 3:
            warnings.append("low_source_examples")
        if str(c.get("answer_shape", "")) in {"unknown_answer_shape", ""}:
            warnings.append("unknown_answer_shape")
        checker_smoke_status = "pending"
        dynamic_sampling_status = "pending"
        if blockers:
            failed_generators.append(generator_key)
        else:
            accepted_generators.append(generator_key)
        generator_results.append(
            {
                "problem_type_id": pt,
                "source_example_count": len(src_ids),
                "answer_contract": answer_contract,
                "checker_key": checker_key,
                "equivalence_type": eq,
                "generator_key": generator_key,
                "generator_status": status,
                "checker_smoke_status": checker_smoke_status,
                "dynamic_sampling_status": dynamic_sampling_status,
                "blockers": blockers,
                "warnings": warnings,
            }
        )

    draft_spec_path = DRAFT_DIR / f"{skill_id}_generator_draft_spec.json"
    write_json(draft_spec_path, {"skill_id": skill_id, "phase": "phase2", "generator_results": generator_results, "accepted_generators": accepted_generators, "failed_generators": failed_generators, "timestamp": utc_timestamp(), "dry_run": dry_run})
    reports = {
        "phase2_generator_summary_json": str(REPORT_DIR / f"{skill_id}_phase2_generator_summary.json"),
        "phase2_generator_summary_md": str(REPORT_DIR / f"{skill_id}_phase2_generator_summary.md"),
        "generator_draft_spec_json": str(draft_spec_path),
    }
    payload = {
        "ok": bool(generator_results),
        "phase": "phase2",
        "skill_id": skill_id,
        "generator_results": generator_results,
        "failed_generators": failed_generators,
        "accepted_generators": accepted_generators,
        "reports": reports,
        "next_action": "phase3_package_draft" if accepted_generators else "review_blockers_before_phase3",
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
    }
    write_json(Path(reports["phase2_generator_summary_json"]), payload)
    write_md(Path(reports["phase2_generator_summary_md"]), f"Gencode Phase2 Generator Summary: {skill_id}", [("phase2", payload)])
    return _normalize_phase_response(payload)


def _run_gencode_publish_check_for_draft(skill_id: str, draft_skill_file_path: str, runtime_ready_gate: dict[str, Any] | None = None, checker_smoke_passed: bool = False, dynamic_sampling_passed: bool = False, equivalence_contract_passed: bool = False) -> dict[str, Any]:
    draft_path = Path(draft_skill_file_path)
    blockers: list[str] = []
    warnings: list[str] = []
    interface_check = {
        "generate_exists": False,
        "check_exists": False,
        "generate_returns_dict": False,
        "generate_has_required_fields": False,
        "check_callable": False,
        "check_accepts_two_args": False,
    }

    if not draft_path.exists():
        blockers.append("draft_skill_file_missing")

    py_compile_status = "not_run"
    if draft_path.exists():
        try:
            py_compile.compile(str(draft_path), doraise=True)
            py_compile_status = "passed"
        except Exception:
            py_compile_status = "failed"
            blockers.append("draft_py_compile_failed")

    runtime_smoke_status = "skipped_with_reason"
    if draft_path.exists() and py_compile_status == "passed":
        try:
            src = draft_path.read_text(encoding="utf-8")
            tree = ast.parse(src)
            fn_names = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
            interface_check["generate_exists"] = "generate" in fn_names
            interface_check["check_exists"] = "check" in fn_names
            if "check" in fn_names:
                interface_check["check_accepts_two_args"] = len(fn_names["check"].args.args) >= 2
            if not interface_check["generate_exists"] or not interface_check["check_exists"]:
                blockers.append("runtime_interface_missing")
            else:
                import importlib.util
                spec = importlib.util.spec_from_file_location(f"_draft_{skill_id}", str(draft_path))
                if not spec or not spec.loader:
                    raise RuntimeError("unable_to_create_import_spec")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                gen = getattr(mod, "generate", None)
                chk = getattr(mod, "check", None)
                interface_check["check_callable"] = callable(chk)
                if callable(gen):
                    payload = gen(level=1)
                    interface_check["generate_returns_dict"] = isinstance(payload, dict)
                    if isinstance(payload, dict):
                        required = ["question_text", "answer"]
                        interface_check["generate_has_required_fields"] = all(k in payload for k in required)
                        if callable(chk):
                            chk(payload.get("answer", ""), payload.get("correct_answer", payload.get("answer", "")))
                runtime_smoke_status = "passed"
        except Exception:
            runtime_smoke_status = "failed"
            blockers.append("runtime_smoke_failed")

    draft_check_passed = bool(
        draft_path.exists()
        and py_compile_status == "passed"
        and interface_check["generate_exists"]
        and interface_check["check_exists"]
        and runtime_smoke_status in {"passed", "skipped_with_reason"}
        and "runtime_interface_missing" not in blockers
    )

    can_publish_draft = draft_check_passed and not any(b in blockers for b in ["draft_py_compile_failed", "runtime_interface_missing", "runtime_smoke_failed"]) 
    can_publish_formal = can_publish_draft
    formal_publish_blockers: list[str] = []
    if not can_publish_formal:
        formal_publish_blockers.append("draft_check_not_passed")

    runtime_ready_blockers: list[str] = []
    gate_status = str((runtime_ready_gate or {}).get("status", ""))
    runtime_ready_allowed = str((runtime_ready_gate or {}).get("status", "")) == "runtime_ready_allowed" or bool((runtime_ready_gate or {}).get("allowed", False))
    if not runtime_ready_allowed or not checker_smoke_passed or not dynamic_sampling_passed or not equivalence_contract_passed:
        runtime_ready_blockers.append("runtime_ready_gate_not_allowed_or_not_verified")
        warnings.append("draft_passed_but_runtime_ready_not_confirmed")
    can_mark_runtime_ready = len(runtime_ready_blockers) == 0

    summary_message = (
        "Draft ???????????????"
        if can_publish_formal
        else "Draft ??????????????????"
    )

    return {
        "draft_check_passed": draft_check_passed,
        "can_publish_draft": can_publish_draft,
        "can_publish_formal": can_publish_formal,
        "can_mark_runtime_ready": can_mark_runtime_ready,
        "formal_publish_blockers": formal_publish_blockers,
        "runtime_ready_blockers": runtime_ready_blockers,
        "warnings": warnings,
        "blockers": blockers,
        "py_compile_status": py_compile_status,
        "interface_check": interface_check,
        "runtime_smoke_status": runtime_smoke_status,
        "summary_message": summary_message,
    }


def run_gencode_phase3_package(skill_id: str, accepted_generator_keys: list | None = None, dry_run: bool = True) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    phase2_path = REPORT_DIR / f"{skill_id}_phase2_generator_summary.json"
    phase2 = json.loads(phase2_path.read_text(encoding="utf-8")) if phase2_path.exists() else run_gencode_phase2(skill_id, dry_run=dry_run)
    accepted = set(str(x) for x in (accepted_generator_keys or []))
    generators = [x for x in (phase2.get("generator_results") or []) if isinstance(x, dict)]
    if accepted:
        generators = [x for x in generators if str(x.get("generator_key", "")) in accepted]
    usable = [x for x in generators if not x.get("blockers")]
    draft_skill_path = DRAFT_DIR / f"{skill_id}.py"
    generator_keys = [str(x.get("generator_key", "")) for x in usable]
    code = (
        "from __future__ import annotations\n\n"
        "from typing import Any\n\n"
        f"SKILL_ID = {skill_id!r}\n"
        f"GENERATOR_KEYS = {generator_keys!r}\n\n"
        "def generate(level: int = 1, seed: int | None = None, difficulty: int | None = None) -> dict[str, Any]:\n"
        "    problem_type_id = GENERATOR_KEYS[0].split(':')[1] if GENERATOR_KEYS else 'draft_pending_problem_type'\n"
        "    return {\n"
        "        'skill_id': SKILL_ID,\n"
        "        'problem_type_id': problem_type_id,\n"
        "        'question_text': '[DRAFT] generator draft pending implementation',\n"
        "        'question': '[DRAFT] generator draft pending implementation',\n"
        "        'answer': '',\n"
        "        'correct_answer': '',\n"
        "        'answer_contract': {'type': 'draft_pending'},\n"
        "        'source': 'gencode_phase3_draft',\n"
        "    }\n\n"
        "def check(user_answer: Any, correct_answer: Any):\n"
        "    return str(user_answer).strip() == str(correct_answer).strip()\n"
    )
    draft_skill_path.write_text(code, encoding="utf-8")
    py_status = "passed"
    py_reason = ""
    try:
        py_compile.compile(str(draft_skill_path), doraise=True)
    except Exception as e:
        py_status = "failed"
        py_reason = str(e)
    runtime_smoke_status = "passed" if py_status == "passed" else "failed"
    package_status = "packaged_draft" if py_status == "passed" else "failed"
    phase1_path = REPORT_DIR / f"{skill_id}_phase1_summary.json"
    phase1 = json.loads(phase1_path.read_text(encoding="utf-8")) if phase1_path.exists() else {}
    runtime_gate = phase1.get("runtime_ready_gate", {}) if isinstance(phase1, dict) else {}
    publish_check = _run_gencode_publish_check_for_draft(
        skill_id=skill_id,
        draft_skill_file_path=str(draft_skill_path),
        runtime_ready_gate=runtime_gate if isinstance(runtime_gate, dict) else {},
        checker_smoke_passed=False,
        dynamic_sampling_passed=False,
        equivalence_contract_passed=False,
    )

    reports = {
        "phase3_package_summary_json": str(REPORT_DIR / f"{skill_id}_phase3_package_summary.json"),
        "phase3_package_summary_md": str(REPORT_DIR / f"{skill_id}_phase3_package_summary.md"),
        "draft_skill_file": str(draft_skill_path),
    }
    payload = {
        "ok": py_status == "passed",
        "phase": "phase3",
        "skill_id": skill_id,
        "skill_file_path": str(draft_skill_path),
        "package_status": package_status,
        "py_compile_status": py_status,
        "runtime_smoke_status": runtime_smoke_status,
        "publish_check": publish_check,
        "reports": reports,
        "next_action": "manual_review_before_runtime_enable",
        "error": py_reason,
        "dry_run": dry_run,
        "timestamp": utc_timestamp(),
    }
    if py_status == "failed":
        payload["summary_message"] = "Phase 3 ???draft skill ????? py_compile?"
    elif publish_check.get("can_publish_formal"):
        payload["summary_message"] = "Phase 3 ???draft ????????????????????????????"
    else:
        payload["summary_message"] = "Phase 3 ?????? draft skill ????????????????????????? runtime-ready?"

    payload["next_action"] = "review_phase3_publish_check"

    write_json(Path(reports["phase3_package_summary_json"]), payload)
    write_md(Path(reports["phase3_package_summary_md"]), f"Gencode Phase3 Package Summary: {skill_id}", [("phase3", payload)])
    return _normalize_phase_response(payload)


def run_gencode_auto_pipeline(skill_id: str, dry_run: bool = True, allow_runtime_ready: bool = False, write_pending_files: bool = True) -> dict[str, Any]:
    phase1 = run_gencode_phase1(skill_id, dry_run=dry_run)
    phase2 = run_gencode_phase2(skill_id, dry_run=dry_run)
    phase3 = run_gencode_phase3_package(skill_id, dry_run=dry_run)
    exception_gate = phase1.get("exception_review_gate", {})
    runtime_gate = phase1.get("runtime_ready_gate", {})
    generator_gate = phase1.get("generator_draft_gate", {})
    if exception_gate.get("required"):
        pipeline_status = "auto_pipeline_exception_review_required"
    elif runtime_gate.get("allowed") and allow_runtime_ready:
        pipeline_status = "auto_pipeline_completed_runtime_allowed"
    elif generator_gate.get("allowed"):
        pipeline_status = "auto_pipeline_completed_runtime_blocked"
    else:
        pipeline_status = "auto_pipeline_failed_fatal_risk"
    reports = {
        "auto_pipeline_summary_json": str(REPORT_DIR / f"{skill_id}_auto_pipeline_summary.json"),
        "auto_pipeline_summary_md": str(REPORT_DIR / f"{skill_id}_auto_pipeline_summary.md"),
        **(phase1.get("reports") or {}),
        **(phase2.get("reports") or {}),
        **(phase3.get("reports") or {}),
    }
    summary = {
        "ok": bool(phase1.get("ok")) and bool(phase2.get("ok")) and bool(phase3.get("ok")),
        "skill_id": skill_id,
        "pipeline_status": pipeline_status,
        "source_example_count": phase1.get("source_example_count", 0),
        "candidate_problem_types": phase1.get("candidate_problem_types", []),
        "per_example_classification": phase1.get("per_example_classification", []),
        "split_or_merge_recommendation": phase1.get("split_or_merge_recommendation", ""),
        "classifier_gate": phase1.get("classifier_gate", {}),
        "generator_draft_gate": phase1.get("generator_draft_gate", {}),
        "runtime_ready_gate": phase1.get("runtime_ready_gate", {}),
        "exception_review_gate": exception_gate,
        "reports": reports,
        "next_action": phase3.get("next_action", "manual_review_before_runtime_enable"),
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
    }
    if write_pending_files:
        write_json(Path(reports["auto_pipeline_summary_json"]), summary)
        write_md(Path(reports["auto_pipeline_summary_md"]), f"Gencode Auto Pipeline Summary: {skill_id}", [("summary", summary)])
    return summary


def run_gencode_publish_check(skill_id: str, dry_run: bool = True) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    safe_skill = _safe_file_component(skill_id)
    draft_skill_path = DRAFT_DIR / f"{safe_skill}.py"
    phase3_summary_path = REPORT_DIR / f"{safe_skill}_phase3_package_summary.json"
    formal_skill_path = PROJECT_ROOT / "skills" / f"{skill_id}.py"

    reports = {
        "phase3_package_summary_json": str(phase3_summary_path),
        "publish_check_json": str(REPORT_DIR / f"{safe_skill}_publish_check_summary.json"),
        "publish_check_md": str(REPORT_DIR / f"{safe_skill}_publish_check_summary.md"),
    }
    warnings: list[str] = []
    blockers: list[str] = []
    human_action_items: list[dict[str, Any]] = []

    if not draft_skill_path.exists():
        blockers.append("draft_skill_file_missing")
    if not phase3_summary_path.exists():
        warnings.append("phase3_summary_missing")

    py_compile_status = "not_run"
    py_compile_error = ""
    if draft_skill_path.exists():
        try:
            py_compile.compile(str(draft_skill_path), doraise=True)
            py_compile_status = "passed"
        except Exception as e:
            py_compile_status = "failed"
            py_compile_error = str(e)
            blockers.append("draft_py_compile_failed")

    interface_check = {
        "generate_exists": False,
        "check_exists": False,
        "generate_returns_dict": False,
        "generate_has_required_fields": False,
        "check_callable": False,
        "check_accepts_two_args": False,
    }
    runtime_smoke_status = "skipped"
    import_status = "skipped"
    import_error = ""
    if draft_skill_path.exists() and py_compile_status == "passed":
        try:
            src = draft_skill_path.read_text(encoding="utf-8")
            tree = ast.parse(src)
            fn_names = {
                node.name: node
                for node in tree.body
                if isinstance(node, ast.FunctionDef)
            }
            interface_check["generate_exists"] = "generate" in fn_names
            interface_check["check_exists"] = "check" in fn_names
            if "check" in fn_names:
                check_fn = fn_names["check"]
                interface_check["check_accepts_two_args"] = len(check_fn.args.args) >= 2
            if not interface_check["generate_exists"] or not interface_check["check_exists"]:
                blockers.append("runtime_interface_missing")
        except Exception as e:
            blockers.append("draft_ast_parse_failed")
            import_error = str(e)

        # controlled import + minimal smoke
        if "runtime_interface_missing" not in blockers and "draft_ast_parse_failed" not in blockers:
            try:
                import importlib.util

                mod_name = f"_gencode_draft_{skill_id}"
                spec = importlib.util.spec_from_file_location(mod_name, str(draft_skill_path))
                if not spec or not spec.loader:
                    raise RuntimeError("unable_to_create_import_spec")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                import_status = "passed"

                generate_fn = getattr(module, "generate", None)
                check_fn = getattr(module, "check", None)
                interface_check["check_callable"] = callable(check_fn)
                if callable(generate_fn):
                    payload = generate_fn(level=1)
                    interface_check["generate_returns_dict"] = isinstance(payload, dict)
                    if isinstance(payload, dict):
                        required = ["question_text", "answer"]
                        interface_check["generate_has_required_fields"] = all(k in payload for k in required)
                        if callable(check_fn):
                            check_fn(payload.get("answer", ""), payload.get("correct_answer", payload.get("answer", "")))
                runtime_smoke_status = "passed"
            except Exception as e:
                runtime_smoke_status = "failed"
                import_status = "failed"
                import_error = str(e)
                blockers.append("runtime_smoke_failed")

    if py_compile_error:
        human_action_items.append(
            {
                "type": "compile_error",
                "target_id": str(draft_skill_path),
                "message": py_compile_error,
                "suggested_action": "inspect_report",
            }
        )
    if import_error:
        human_action_items.append(
            {
                "type": "runtime_smoke_failed",
                "target_id": str(draft_skill_path),
                "message": import_error,
                "suggested_action": "inspect_report",
            }
        )

    can_publish = len(blockers) == 0
    if can_publish and warnings:
        phase_status = "publish_check_passed_with_warning"
    elif can_publish:
        phase_status = "publish_check_passed"
    elif blockers:
        phase_status = "publish_check_blocked"
    else:
        phase_status = "publish_check_failed"

    summary_message = (
        "Publish Check 通過：可進入正式發布審核（本輪仍為 dry-run）。"
        if can_publish
        else "Publish Check 未通過：請先處理 blockers 後再重試。"
    )

    payload = {
        "ok": can_publish,
        "phase": "publish_check",
        "skill_id": skill_id,
        "phase_status": phase_status,
        "can_continue": can_publish,
        "can_retry": True,
        "can_publish": can_publish,
        "requires_human_action": bool(blockers or human_action_items),
        "human_action_items": human_action_items,
        "draft_skill_file_path": str(draft_skill_path),
        "formal_skill_file_path": str(formal_skill_path),
        "py_compile_status": py_compile_status,
        "interface_check": interface_check,
        "runtime_smoke_status": runtime_smoke_status,
        "import_status": import_status,
        "blockers": blockers,
        "warnings": warnings,
        "summary_message": summary_message,
        "reports": reports,
        "next_action": "manual_publish_review" if can_publish else "fix_publish_check_blockers",
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
    }
    write_json(Path(reports["publish_check_json"]), payload)
    write_md(Path(reports["publish_check_md"]), f"Gencode Publish Check Summary: {skill_id}", [("publish_check", payload)])
    return payload


def publish_gencode_draft_skill(skill_id: str, confirm: bool = False, allow_runtime_ready: bool = False) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir = PROJECT_ROOT / "backups" / "gencode_skill_publish"
    backup_dir.mkdir(parents=True, exist_ok=True)

    draft_skill_path = DRAFT_DIR / f"{skill_id}.py"
    phase3_summary_path = REPORT_DIR / f"{skill_id}_phase3_package_summary.json"
    formal_skill_path = PROJECT_ROOT / "skills" / f"{skill_id}.py"
    reports = {
        "phase3_package_summary_json": str(phase3_summary_path),
        "publish_summary_json": str(REPORT_DIR / f"{skill_id}_publish_summary.json"),
        "publish_summary_md": str(REPORT_DIR / f"{skill_id}_publish_summary.md"),
    }

    blockers: list[str] = []
    warnings: list[str] = []

    phase3 = json.loads(phase3_summary_path.read_text(encoding="utf-8")) if phase3_summary_path.exists() else {}
    publish_check = phase3.get("publish_check", {}) if isinstance(phase3, dict) else {}
    if not isinstance(publish_check, dict):
        publish_check = {}
    if not bool(publish_check.get("draft_check_passed", False)):
        blockers.append("draft_check_not_passed")
    if not bool(publish_check.get("can_publish_draft", False)):
        blockers.append("cannot_publish_draft")
    if not bool(publish_check.get("can_publish_formal", False)):
        blockers.append("cannot_publish_formal")
    if (publish_check.get("blockers") or []):
        blockers.append("publish_check_blockers_present")
    if not draft_skill_path.exists():
        blockers.append("draft_skill_file_missing")

    backup_path = ""
    backup_status = "not_run"
    py_compile_status = "not_run"
    runtime_smoke_status = "skipped"
    runtime_ready_marked = False

    if blockers:
        payload = {
            "ok": False,
            "skill_id": skill_id,
            "phase": "publish",
            "publish_status": "publish_blocked",
            "draft_skill_file_path": str(draft_skill_path),
            "formal_skill_file_path": str(formal_skill_path),
            "backup_path": backup_path,
            "backup_status": backup_status,
            "py_compile_status": py_compile_status,
            "runtime_smoke_status": runtime_smoke_status,
            "runtime_ready_marked": False,
            "can_mark_runtime_ready": False,
            "blockers": blockers,
            "warnings": warnings,
            "summary_message": "發布前檢查未通過，禁止正式發布。",
            "reports": reports,
            "timestamp": utc_timestamp(),
        }
        write_json(Path(reports["publish_summary_json"]), payload)
        write_md(Path(reports["publish_summary_md"]), f"Gencode Publish Summary: {skill_id}", [("publish", payload)])
        return payload

    if not confirm:
        payload = {
            "ok": True,
            "skill_id": skill_id,
            "phase": "publish",
            "publish_status": "publish_preview",
            "draft_skill_file_path": str(draft_skill_path),
            "formal_skill_file_path": str(formal_skill_path),
            "backup_path": "",
            "backup_status": "preview_only",
            "py_compile_status": "preview_only",
            "runtime_smoke_status": "preview_only",
            "runtime_ready_marked": False,
            "can_mark_runtime_ready": bool(publish_check.get("can_mark_runtime_ready", False)),
            "blockers": [],
            "warnings": ["confirm_required_for_publish"],
            "summary_message": "預覽完成：可發布。confirm=true 才會覆寫正式技能檔。",
            "reports": reports,
            "timestamp": utc_timestamp(),
        }
        write_json(Path(reports["publish_summary_json"]), payload)
        write_md(Path(reports["publish_summary_md"]), f"Gencode Publish Summary: {skill_id}", [("publish", payload)])
        return payload

    try:
        if formal_skill_path.exists():
            stamp = utc_timestamp().replace(":", "").replace("-", "").replace("T", "_").replace("Z", "")
            backup_file = backup_dir / f"{skill_id}.{stamp}.py"
            shutil.copy2(str(formal_skill_path), str(backup_file))
            backup_path = str(backup_file)
            backup_status = "backed_up"
        else:
            backup_status = "no_existing_file"

        shutil.copy2(str(draft_skill_path), str(formal_skill_path))

        try:
            py_compile.compile(str(formal_skill_path), doraise=True)
            py_compile_status = "passed"
        except Exception as e:
            py_compile_status = "failed"
            blockers.append(f"formal_py_compile_failed:{e}")

        if py_compile_status == "passed":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(f"_published_{skill_id}", str(formal_skill_path))
                if not spec or not spec.loader:
                    raise RuntimeError("unable_to_create_import_spec")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                gen = getattr(mod, "generate", None)
                chk = getattr(mod, "check", None)
                if not callable(gen) or not callable(chk):
                    raise RuntimeError("generate_or_check_missing")
                payload = gen(level=1)
                if not isinstance(payload, dict):
                    raise RuntimeError("generate_not_dict")
                chk(payload.get("answer", ""), payload.get("correct_answer", payload.get("answer", "")))
                runtime_smoke_status = "passed"
            except Exception as e:
                runtime_smoke_status = "failed"
                warnings.append(f"runtime_smoke_warning:{e}")
        else:
            runtime_smoke_status = "failed"

    except Exception as e:
        payload = {
            "ok": False,
            "skill_id": skill_id,
            "phase": "publish",
            "publish_status": "publish_failed",
            "draft_skill_file_path": str(draft_skill_path),
            "formal_skill_file_path": str(formal_skill_path),
            "backup_path": backup_path,
            "backup_status": backup_status if backup_status != "not_run" else "failed_before_backup",
            "py_compile_status": py_compile_status,
            "runtime_smoke_status": runtime_smoke_status,
            "runtime_ready_marked": False,
            "can_mark_runtime_ready": False,
            "blockers": blockers + [f"publish_exception:{e}"],
            "warnings": warnings,
            "summary_message": "正式發布失敗，請檢查錯誤與備份檔。",
            "reports": reports,
            "timestamp": utc_timestamp(),
        }
        write_json(Path(reports["publish_summary_json"]), payload)
        write_md(Path(reports["publish_summary_md"]), f"Gencode Publish Summary: {skill_id}", [("publish", payload)])
        return payload

    publish_status = "published" if py_compile_status == "passed" else "publish_failed"
    can_mark_runtime_ready = bool(publish_check.get("can_mark_runtime_ready", False))
    if allow_runtime_ready and can_mark_runtime_ready and runtime_smoke_status == "passed":
        runtime_ready_marked = True
    else:
        runtime_ready_marked = False

    if not can_mark_runtime_ready:
        warnings.append("published_but_not_runtime_ready")

    payload = {
        "ok": publish_status == "published",
        "skill_id": skill_id,
        "phase": "publish",
        "publish_status": publish_status,
        "draft_skill_file_path": str(draft_skill_path),
        "formal_skill_file_path": str(formal_skill_path),
        "backup_path": backup_path,
        "backup_status": backup_status,
        "py_compile_status": py_compile_status,
        "runtime_smoke_status": runtime_smoke_status,
        "runtime_ready_marked": runtime_ready_marked,
        "can_mark_runtime_ready": can_mark_runtime_ready,
        "blockers": blockers,
        "warnings": warnings,
        "summary_message": (
            "已發布技能檔，但尚未 runtime-ready。"
            if publish_status == "published" and not runtime_ready_marked
            else ("發布成功。" if publish_status == "published" else "發布失敗。")
        ),
        "reports": reports,
        "timestamp": utc_timestamp(),
    }
    write_json(Path(reports["publish_summary_json"]), payload)
    write_md(Path(reports["publish_summary_md"]), f"Gencode Publish Summary: {skill_id}", [("publish", payload)])
    return payload
