from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_md(path: Path, title: str, sections: list[tuple[str, Any]]) -> None:
    lines = [f"# {title}", ""]
    for name, data in sections:
        lines.append(f"## {name}")
        lines.append("```json")
        lines.append(json.dumps(data, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def determine_next_repair_action(phase2_report: dict[str, Any]) -> dict[str, Any]:
    skill_id = str(phase2_report.get("skill_id", "")).strip()
    dep = phase2_report.get("build_dependency_plan") or {}
    missing_checkers = dep.get("missing_checkers") or []
    missing_verifiers = dep.get("missing_verifiers") or []
    missing_domain_functions = dep.get("missing_domain_functions") or []
    missing_generators = dep.get("missing_generators") or []
    manual_review_problem_types = dep.get("excluded_manual_review_problem_types") or phase2_report.get("manual_review_problem_types") or []
    final_status = str(phase2_report.get("final_status", "")).strip()
    preflight_status = str(phase2_report.get("preflight_status", "")).strip()
    build_execution_status = str(phase2_report.get("build_execution_status", "")).strip()

    def _repair_action(gap: str, reason: str) -> dict[str, Any]:
        return {
            "next_action_type": "repair_gap",
            "gap": gap,
            "command": f"python scripts\\gencode_repair_build_gap.py --skill-id {skill_id} --gap {gap}",
            "reason": reason,
            "should_run_phase3": False,
            "requires_human_review": False,
        }

    if missing_checkers:
        return _repair_action("missing_checker", "build_dependency_plan shows unresolved missing_checkers.")
    if missing_verifiers:
        return _repair_action("missing_verifier", "missing_checkers resolved, but missing_verifiers remains.")
    if missing_domain_functions:
        return _repair_action("missing_domain_function", "checker/verifier are ready, but missing_domain_functions remains.")
    if missing_generators:
        return _repair_action("missing_generator", "foundation components are ready, but missing_generators remains.")

    if preflight_status == "PASS" and build_execution_status in {"EXECUTED", "SKIPPED"} and final_status in {
        "BUILD_PASS",
        "BUILD_PARTIAL",
        "BUILD_BOOTSTRAP_PASS",
        "BUILD_PLAN_READY",
    }:
        return {
            "next_action_type": "phase3_publish_gate",
            "gap": "",
            "command": f"python scripts\\gencode_pipeline_phase3_publish_gate.py --skill-id {skill_id}",
            "reason": "No blocking build dependency gaps detected and phase2 status is publish-gate eligible.",
            "should_run_phase3": True,
            "requires_human_review": False,
        }

    if manual_review_problem_types:
        return {
            "next_action_type": "human_review",
            "gap": "",
            "command": "",
            "reason": "Manual-review problem types remain, but they do not block deterministic build foundation.",
            "should_run_phase3": False,
            "requires_human_review": True,
        }

    return {
        "next_action_type": "human_review",
        "gap": "",
        "command": "",
        "reason": "Unable to determine next action from build_dependency_plan.",
        "should_run_phase3": False,
        "requires_human_review": True,
    }

