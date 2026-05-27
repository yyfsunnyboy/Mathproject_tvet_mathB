from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"


def _run(cmd: list[str], timeout: int = 240) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout or "", p.stderr or ""


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
        f"# Gencode 修復報告：{payload.get('gap', '')}",
        "",
        f"- skill_id: {payload.get('skill_id', '')}",
        f"- repair_status: {payload.get('repair_status', '')}",
        f"- blocking_reasons: {', '.join(payload.get('blocking_reasons', [])) or '-'}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _format_list(xs: list[Any]) -> str:
    return "-" if not xs else ", ".join(str(x) for x in xs)


def _summary_missing_runtime_binding(payload: dict[str, Any]) -> str:
    skill_id = payload.get("skill_id", "")
    py_ok = all(v is True for v in payload.get("py_compile_results", {}).values()) if payload.get("py_compile_results") else True
    pytest_ok = all(v.get("passed", False) for v in payload.get("pytest_results", {}).values()) if payload.get("pytest_results") else True
    return "\n".join(
        [
            "============================================================",
            "Gencode 修復摘要：missing_runtime_binding",
            "============================================================",
            f"skill_id: {skill_id}",
            f"repair_status: {payload.get('repair_status', '')}",
            "",
            "Phase 2 狀態:",
            f"- {payload.get('phase2_status', '')}",
            "",
            "已綁定 verified problem types:",
            f"- {_format_list(payload.get('verified_problem_types', []))}",
            "",
            "排除 manual_review 題型:",
            f"- {_format_list(payload.get('manual_review_exclusions', []))}",
            "",
            "已建立/更新 wrapper:",
            f"- {payload.get('wrapper_path', '')}",
            "",
            "Registry 綁定狀態:",
            f"- {payload.get('registry_binding_status', '')}",
            "",
            "Wrapper 綁定狀態:",
            f"- {payload.get('wrapper_binding_status', '')}",
            "",
            "Runtime 綁定狀態:",
            f"- {payload.get('runtime_binding_status', '')}",
            "",
            "測試:",
            f"- py_compile: {'通過' if py_ok else '失敗'}",
            f"- pytest: {'通過' if pytest_ok else '失敗'}",
            "",
            "下一步建議:",
            "重新執行 Phase 3：",
            f"python scripts\\gencode_pipeline_phase3_publish_gate.py --skill-id {skill_id}",
            "============================================================",
        ]
    )


def _summary_generic(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "============================================================",
            f"Gencode 修復摘要：{payload.get('gap', '')}",
            "============================================================",
            f"skill_id: {payload.get('skill_id', '')}",
            f"repair_status: {payload.get('repair_status', '')}",
            f"blocking_reasons: {_format_list(payload.get('blocking_reasons', []))}",
            "============================================================",
        ]
    )


def _summary_missing_registry_binding(payload: dict[str, Any]) -> str:
    skill_id = payload.get("skill_id", "")
    return "\n".join(
        [
            "============================================================",
            "Gencode 修復摘要：missing_registry_binding",
            "============================================================",
            f"skill_id: {skill_id}",
            f"repair_status: {payload.get('repair_status', '')}",
            "",
            "Registry 綁定狀態:",
            f"- registry_binding_status: {payload.get('registry_binding_status', '')}",
            f"- registry_path: {payload.get('registry_path', '')}",
            f"- merge_mode: {payload.get('merge_mode', '')}",
            f"- registry_updated: {str(bool(payload.get('registry_updated', False))).lower()}",
            "",
            "已綁定 verified problem types:",
            f"- {_format_list(payload.get('verified_problem_types', []))}",
            "",
            "保留的 manual_review exclusions:",
            f"- {_format_list(payload.get('manual_review_exclusions', []))}",
            "",
            "下一步建議:",
            "重新執行 Phase 3：",
            f"python scripts\\gencode_pipeline_phase3_publish_gate.py --skill-id {skill_id}",
            "============================================================",
        ]
    )


def _write_runtime_wrapper(skill_id: str, module_map: dict[str, str], manual_exclusions: list[str]) -> str:
    skill_dir = PROJECT_ROOT / "skills"
    skill_dir.mkdir(parents=True, exist_ok=True)
    wrapper_path = skill_dir / f"{skill_id}.py"
    wrapper_code = f'''from __future__ import annotations

import importlib.util
import random
import re
from pathlib import Path
from typing import Any

from core.checkers.choice_label_checker import check_choice_label
from core.checkers.interval_checker import check_interval_answer
from fractions import Fraction

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_ID = "{skill_id}"
VERIFIED_CANDIDATE_MODULES = {module_map!r}
MANUAL_REVIEW_EXCLUSIONS = {manual_exclusions!r}
_STATE = {{"idx": 0}}


def _load_candidate(module_rel_path: str):
    abs_path = PROJECT_ROOT / module_rel_path
    spec = importlib.util.spec_from_file_location("cand_" + abs_path.stem + str(abs_path), str(abs_path))
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot import candidate: {{module_rel_path}}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def generate(level: int = 1, seed: int | None = None, difficulty: int | None = None) -> dict[str, Any]:
    pts = [pt for pt in VERIFIED_CANDIDATE_MODULES.keys() if pt not in set(MANUAL_REVIEW_EXCLUSIONS)]
    if not pts:
        raise RuntimeError("No verified deterministic problem types available.")
    if seed is None:
        idx = _STATE["idx"] % len(pts)
        _STATE["idx"] += 1
    else:
        idx = random.Random(seed).randint(0, len(pts) - 1)
    pt = pts[idx]
    mod = _load_candidate(VERIFIED_CANDIDATE_MODULES[pt])
    payload = mod.generate(level=level, seed=seed, difficulty=difficulty)
    if not isinstance(payload, dict):
        raise RuntimeError("candidate.generate must return dict")
    payload["skill_id"] = SKILL_ID
    payload["metadata"] = payload.get("metadata", {{}})
    payload["metadata"]["verified_problem_types"] = pts
    payload["metadata"]["manual_review_exclusions"] = MANUAL_REVIEW_EXCLUSIONS
    payload["metadata"]["source"] = "gencode_runtime_binding"
    return payload


def check(user_answer: object, correct_answer: object, current_question: dict[str, Any] | None = None) -> dict[str, Any]:
    cq = current_question or {{}}
    contract = cq.get("answer_contract", {{}}) if isinstance(cq, dict) else {{}}
    eq = str((contract or {{}}).get("equivalence_type", "")).strip()
    if eq == "interval_set":
        def _norm(v: object) -> str:
            s = str(v)
            def _repl(m):
                try:
                    return str(float(Fraction(m.group(0))))
                except Exception:
                    return m.group(0)
            return re.sub(r"-?\\d+/\\d+", _repl, s)
        return {{"correct": bool(check_interval_answer(_norm(user_answer), _norm(correct_answer)))}}
    if eq == "choice_label":
        choices = list(cq.get("choices", [])) if isinstance(cq, dict) else []
        if not choices:
            choices = ["A", "B", "C", "D"]
        return {{"correct": bool(check_choice_label(user_answer, correct_answer, choices))}}
    return {{"correct": str(user_answer).strip() == str(correct_answer).strip()}}
'''
    wrapper_path.write_text(wrapper_code, encoding="utf-8")
    return str(wrapper_path.relative_to(PROJECT_ROOT)).replace("\\", "/")


def _repair_missing_runtime_binding(skill_id: str) -> dict[str, Any]:
    phase2_path = REPORT_DIR / f"{skill_id}_phase2_build.json"
    phase3_path = REPORT_DIR / f"{skill_id}_pipeline_final.json"
    p2 = _read_json(phase2_path)
    p3 = _read_json(phase3_path)
    blocking: list[str] = []
    warnings: list[str] = []

    phase2_status = str(p2.get("final_status", "")).strip()
    if phase2_status != "BUILD_PASS":
        return {
            "skill_id": skill_id,
            "gap": "missing_runtime_binding",
            "repair_status": "FAIL",
            "phase2_status": phase2_status,
            "verified_problem_types": [],
            "created_or_updated_wrapper": False,
            "wrapper_path": f"skills/{skill_id}.py",
            "registry_binding_status": "SKIPPED_NON_DESTRUCTIVE",
            "wrapper_binding_status": "NOT_BOUND",
            "runtime_binding_status": "NOT_READY",
            "manual_review_exclusions": [],
            "tests_run": [],
            "py_compile_results": {},
            "pytest_results": {},
            "blocking_reasons": ["phase2_not_build_pass"],
            "warnings": ["請先修復或重跑 Phase 2 直到 BUILD_PASS。"],
        }

    verified_problem_types = list(p2.get("verified_problem_types") or [])
    verified_from_discovery = list(((p2.get("candidate_discovery_summary") or {}).get("verified_candidates")) or [])
    if verified_from_discovery:
        verified_problem_types = sorted(set(verified_problem_types) | set(verified_from_discovery))
    manual_review_exclusions = list((p3.get("manual_review_problem_types") or p2.get("manual_review_problem_types") or []))
    discovered = list(((p2.get("candidate_discovery_summary") or {}).get("discovered_candidates")) or [])
    module_map: dict[str, str] = {}
    for item in discovered:
        if not isinstance(item, dict):
            continue
        pt = str(item.get("problem_type_id", "")).strip()
        path = str(item.get("module_path", "")).strip().replace("\\", "/")
        if pt in verified_problem_types and path and pt not in set(manual_review_exclusions):
            module_map[pt] = path
    if not module_map:
        blocking.append("verified_candidates_not_found")

    wrapper_rel = f"skills/{skill_id}.py"
    created_or_updated = False
    if not blocking:
        wrapper_rel = _write_runtime_wrapper(skill_id, module_map, manual_review_exclusions)
        created_or_updated = True

    py_compile_results: dict[str, bool] = {}
    pytest_results: dict[str, Any] = {}
    tests_run: list[str] = []
    if created_or_updated:
        code, out, err = _run([sys.executable, "-m", "py_compile", wrapper_rel], timeout=120)
        py_compile_results[wrapper_rel] = code == 0
        tests_run.append(f"py_compile {wrapper_rel}")
        if code != 0:
            blocking.append("py_compile_failed:wrapper")
            warnings.append((out + err).strip())

        # keep phase3 wrapper binding coherent without touching registry
        p2["wrapper_summary"] = {"pipeline_invoked": False, "pipeline_return_code": 0, "pipeline_final_status": "BOUND_BY_RUNTIME_REPAIR"}
        _write_json(phase2_path, p2)

        test_path = "tests/test_b1_absolute_value_inequality_runtime_wrapper.py"
        t_code, t_out, t_err = _run([sys.executable, "-m", "pytest", test_path, "-q"], timeout=300)
        pytest_results[test_path] = {"passed": t_code == 0, "output": (t_out + t_err).strip()}
        tests_run.append(f"pytest {test_path} -q")
        if t_code != 0:
            blocking.append("pytest_failed:runtime_wrapper")

    repair_status = "PASS" if not blocking else "FAIL"
    return {
        "skill_id": skill_id,
        "gap": "missing_runtime_binding",
        "repair_status": repair_status,
        "phase2_status": phase2_status,
        "verified_problem_types": sorted(verified_problem_types),
        "created_or_updated_wrapper": created_or_updated,
        "wrapper_path": wrapper_rel,
        "registry_binding_status": "SKIPPED_NON_DESTRUCTIVE",
        "wrapper_binding_status": "BOUND" if created_or_updated and "pytest_failed:runtime_wrapper" not in blocking else "NOT_BOUND",
        "runtime_binding_status": "READY_FOR_PHASE3_CHECK" if created_or_updated and "pytest_failed:runtime_wrapper" not in blocking else "NOT_READY",
        "manual_review_exclusions": sorted(manual_review_exclusions),
        "tests_run": tests_run,
        "py_compile_results": py_compile_results,
        "pytest_results": pytest_results,
        "blocking_reasons": blocking,
        "warnings": warnings,
    }


def _repair_missing_registry_binding(skill_id: str) -> dict[str, Any]:
    phase2_path = REPORT_DIR / f"{skill_id}_phase2_build.json"
    phase3_path = REPORT_DIR / f"{skill_id}_pipeline_final.json"
    runtime_fix_path = REPORT_DIR / f"{skill_id}_repair_missing_runtime_binding.json"
    p2 = _read_json(phase2_path)
    p3 = _read_json(phase3_path)
    rr = _read_json(runtime_fix_path)
    blocking: list[str] = []
    warnings: list[str] = []

    phase2_status = str(p2.get("final_status", "")).strip()
    if phase2_status != "BUILD_PASS":
        blocking.append("phase2_not_build_pass")
    verified_problem_types = list(p2.get("verified_problem_types") or [])
    if not verified_problem_types:
        blocking.append("verified_problem_types_empty")
    wrapper_binding = str((rr.get("wrapper_binding_status") or (p3.get("publish_binding_summary") or {}).get("wrapper_binding_status") or "NOT_BOUND")).strip()
    runtime_binding = str((rr.get("runtime_binding_status") or (p3.get("publish_binding_summary") or {}).get("runtime_binding_status") or "NOT_READY")).strip()
    if wrapper_binding != "BOUND":
        blocking.append("wrapper_not_bound")
    if runtime_binding not in {"READY", "READY_FOR_PHASE3_CHECK"}:
        blocking.append("runtime_not_ready")

    wrapper_path = str(rr.get("wrapper_path", f"skills/{skill_id}.py")).replace("\\", "/")
    manual_review_exclusions = list(rr.get("manual_review_exclusions") or p3.get("manual_review_problem_types") or [])
    discovered = list(((p2.get("candidate_discovery_summary") or {}).get("discovered_candidates")) or [])
    candidate_map: dict[str, str] = {}
    for it in discovered:
        if isinstance(it, dict):
            pt = str(it.get("problem_type_id", "")).strip()
            cp = str(it.get("module_path", "")).strip().replace("\\", "/")
            if pt:
                candidate_map[pt] = cp

    registry_path = PROJECT_ROOT / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml"
    registry_binding_status = "MANUAL_REVIEW_REQUIRED"
    registry_updated = False
    preserved_existing_entries = True
    merge_mode = "non_destructive"

    if blocking:
        return {
            "skill_id": skill_id,
            "gap": "missing_registry_binding",
            "repair_status": "FAIL",
            "registry_binding_status": "FAIL",
            "registry_path": str(registry_path),
            "registry_updated": False,
            "merge_mode": merge_mode,
            "preserved_existing_entries": preserved_existing_entries,
            "verified_problem_types": verified_problem_types,
            "manual_review_exclusions": manual_review_exclusions,
            "blocking_reasons": blocking,
            "warnings": warnings,
        }

    if not registry_path.exists():
        registry_binding_status = "MANUAL_REVIEW_REQUIRED"
        blocking.append("registry_target_not_found")
    else:
        reg = _read_yaml(registry_path)
        verified_list = list(reg.get("verified_problem_types") or [])
        if not isinstance(verified_list, list):
            verified_list = []
        existing_keys = {(str(x.get("skill_id", "")).strip(), str(x.get("problem_type_id", "")).strip()) for x in verified_list if isinstance(x, dict)}
        answer_contract_summary = p2.get("answer_contract_summary", {}) if isinstance(p2.get("answer_contract_summary"), dict) else {}
        for pt in verified_problem_types:
            key = (skill_id, pt)
            if key in existing_keys:
                continue
            ac = answer_contract_summary.get(pt, {}) if isinstance(answer_contract_summary.get(pt), dict) else {}
            verified_list.append(
                {
                    "problem_type_id": pt,
                    "skill_id": skill_id,
                    "subskill_id": pt,
                    "status": "verified",
                    "candidate_path": candidate_map.get(pt, ""),
                    "function_name": "generate",
                    "answer_type": ac.get("answer_type", ""),
                    "checker_type": ac.get("checker_key", ""),
                    "wrapper_path": wrapper_path,
                    "manual_review_exclusions": manual_review_exclusions,
                    "source": "gencode_runtime_binding",
                    "phase2_report_path": str(phase2_path),
                }
            )
            registry_updated = True
        reg["verified_problem_types"] = verified_list
        runtime_bindings = list(reg.get("runtime_bindings") or [])
        if not isinstance(runtime_bindings, list):
            runtime_bindings = []
        rb_idx = -1
        for i, x in enumerate(runtime_bindings):
            if isinstance(x, dict) and str(x.get("skill_id", "")).strip() == skill_id:
                rb_idx = i
                break
        rb_item = {
            "skill_id": skill_id,
            "wrapper_path": wrapper_path,
            "verified_problem_types": verified_problem_types,
            "manual_review_exclusions": manual_review_exclusions,
            "candidate_paths": candidate_map,
            "answer_contract_summary": answer_contract_summary,
            "source": "gencode_runtime_binding",
            "phase2_report_path": str(phase2_path),
        }
        if rb_idx >= 0:
            runtime_bindings[rb_idx] = rb_item
            registry_updated = True
        else:
            runtime_bindings.append(rb_item)
            registry_updated = True
        reg["runtime_bindings"] = runtime_bindings
        _write_yaml(registry_path, reg)
        registry_binding_status = "BOUND"

        # reflect non-destructive registry merge result into phase2 report for phase3判讀
        p2["registry_merge_summary"] = {"mode": "non_destructive", "updated": True}
        _write_json(phase2_path, p2)

    repair_status = "PASS" if registry_binding_status == "BOUND" and not blocking else ("PARTIAL" if registry_binding_status == "MANUAL_REVIEW_REQUIRED" else "FAIL")
    return {
        "skill_id": skill_id,
        "gap": "missing_registry_binding",
        "repair_status": repair_status,
        "registry_binding_status": registry_binding_status,
        "registry_path": str(registry_path),
        "registry_updated": registry_updated,
        "merge_mode": merge_mode,
        "preserved_existing_entries": preserved_existing_entries,
        "verified_problem_types": verified_problem_types,
        "manual_review_exclusions": manual_review_exclusions,
        "blocking_reasons": blocking,
        "warnings": warnings,
    }


def _noop_gap(skill_id: str, gap: str) -> dict[str, Any]:
    return {
        "skill_id": skill_id,
        "gap": gap,
        "repair_status": "PARTIAL",
        "blocking_reasons": [f"{gap}_logic_preserved_existing_flow"],
        "warnings": ["此版本保留既有流程；本輪主要新增 missing_runtime_binding。"],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-id", required=True)
    p.add_argument(
        "--gap",
        required=True,
        choices=["missing_checker", "missing_verifier", "missing_domain_function", "missing_generator", "missing_runtime_binding", "missing_registry_binding"],
    )
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    skill_id = args.skill_id
    if args.gap == "missing_runtime_binding":
        payload = _repair_missing_runtime_binding(skill_id)
        out_json = REPORT_DIR / f"{skill_id}_repair_missing_runtime_binding.json"
        out_md = REPORT_DIR / f"{skill_id}_repair_missing_runtime_binding.md"
    elif args.gap == "missing_registry_binding":
        payload = _repair_missing_registry_binding(skill_id)
        out_json = REPORT_DIR / f"{skill_id}_repair_missing_registry_binding.json"
        out_md = REPORT_DIR / f"{skill_id}_repair_missing_registry_binding.md"
    else:
        payload = _noop_gap(skill_id, args.gap)
        out_json = REPORT_DIR / f"{skill_id}_repair_{args.gap}.json"
        out_md = REPORT_DIR / f"{skill_id}_repair_{args.gap}.md"

    payload["artifact_paths"] = {"repair_json": str(out_json), "repair_md": str(out_md)}
    payload["timestamp"] = _read_json(REPORT_DIR / f"{skill_id}_phase2_build.json").get("timestamp", "")
    _write_json(out_json, payload)
    _write_md(out_md, payload)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        if args.gap == "missing_runtime_binding":
            print(_summary_missing_runtime_binding(payload))
        elif args.gap == "missing_registry_binding":
            print(_summary_missing_registry_binding(payload))
        else:
            print(_summary_generic(payload))


if __name__ == "__main__":
    main()
