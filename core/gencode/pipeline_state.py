from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GENCODE_REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"
GENCODE_DRAFT_DIR = GENCODE_REPORT_DIR / "drafts"

_WIN_INVALID_PATH_CHARS = re.compile(r'[<>:"|?*\x00-\x1f]')


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize_path_segment(value: str) -> str:
    """Strip quotes/control chars and Windows-forbidden path symbols."""
    text = str(value or "").strip().strip('"').strip("'")
    text = "".join(ch for ch in text if ch >= " " or ch in "\t")
    text = _WIN_INVALID_PATH_CHARS.sub("_", text)
    return text or "unknown_skill"


def coerce_report_path(path: str | Path) -> Path:
    """Normalize report paths for cross-platform open()/replace() safety."""
    if isinstance(path, Path):
        candidate = path
    else:
        raw = str(path or "").strip().strip('"').strip("'")
        raw = "".join(ch for ch in raw if ch >= " " or ch in "\t")
        candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = (PROJECT_ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()
    return candidate


def phase_summary_path(skill_id: str, artifact: str) -> Path:
    """Canonical Path builder for gencode closed-loop artifacts."""
    safe_skill = sanitize_path_segment(skill_id)
    name = str(artifact or "").strip().lower()
    mapping = {
        "phase1_summary": GENCODE_REPORT_DIR / f"{safe_skill}_phase1_summary.json",
        "phase1_md": GENCODE_REPORT_DIR / f"{safe_skill}_phase1_summary.md",
        "phase2_generator_summary": GENCODE_REPORT_DIR / f"{safe_skill}_phase2_generator_summary.json",
        "phase2_generator_md": GENCODE_REPORT_DIR / f"{safe_skill}_phase2_generator_summary.md",
        "phase3_package_summary": GENCODE_REPORT_DIR / f"{safe_skill}_phase3_package_summary.json",
        "phase3_package_md": GENCODE_REPORT_DIR / f"{safe_skill}_phase3_package_summary.md",
        "generator_draft_spec": GENCODE_DRAFT_DIR / f"{safe_skill}_generator_draft_spec.json",
        "draft_skill": GENCODE_DRAFT_DIR / f"{safe_skill}.py",
        "auto_pipeline_summary": GENCODE_REPORT_DIR / f"{safe_skill}_auto_pipeline_summary.json",
        "auto_pipeline_md": GENCODE_REPORT_DIR / f"{safe_skill}_auto_pipeline_summary.md",
        "publish_check_summary": GENCODE_REPORT_DIR / f"{safe_skill}_publish_check_summary.json",
        "publish_check_md": GENCODE_REPORT_DIR / f"{safe_skill}_publish_check_summary.md",
        "publish_summary": GENCODE_REPORT_DIR / f"{safe_skill}_publish_summary.json",
        "publish_summary_md": GENCODE_REPORT_DIR / f"{safe_skill}_publish_summary.md",
    }
    if name not in mapping:
        raise KeyError(f"unknown_gencode_artifact:{artifact}")
    return mapping[name]


def phase_report_paths(skill_id: str) -> dict[str, Path]:
    """Return canonical Path objects for all standard phase report artifacts."""
    return {
        "phase1_summary_json": phase_summary_path(skill_id, "phase1_summary"),
        "phase1_summary_md": phase_summary_path(skill_id, "phase1_md"),
        "phase1_json": phase_summary_path(skill_id, "phase1_summary"),
        "phase1_md": phase_summary_path(skill_id, "phase1_md"),
        "phase2_generator_summary_json": phase_summary_path(skill_id, "phase2_generator_summary"),
        "phase2_generator_summary_md": phase_summary_path(skill_id, "phase2_generator_md"),
        "phase2_json": phase_summary_path(skill_id, "phase2_generator_summary"),
        "phase2_md": phase_summary_path(skill_id, "phase2_generator_md"),
        "phase3_package_summary_json": phase_summary_path(skill_id, "phase3_package_summary"),
        "phase3_package_summary_md": phase_summary_path(skill_id, "phase3_package_md"),
        "phase3_json": phase_summary_path(skill_id, "phase3_package_summary"),
        "phase3_md": phase_summary_path(skill_id, "phase3_package_md"),
        "final_json": phase_summary_path(skill_id, "phase3_package_summary"),
        "final_md": phase_summary_path(skill_id, "phase3_package_md"),
        "draft_skill_file": phase_summary_path(skill_id, "draft_skill"),
        "generator_draft_spec_json": phase_summary_path(skill_id, "generator_draft_spec"),
        "auto_pipeline_summary_json": phase_summary_path(skill_id, "auto_pipeline_summary"),
        "auto_pipeline_summary_md": phase_summary_path(skill_id, "auto_pipeline_md"),
    }


def reports_dict_from_paths(paths: dict[str, Path]) -> dict[str, str]:
    return {key: str(coerce_report_path(value)) for key, value in paths.items()}


def _atomic_write_text(path: Path, text: str) -> None:
    target = coerce_report_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        
        import gc
        gc.collect()
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                if target.exists():
                    try:
                        target.unlink(missing_ok=True)
                    except OSError:
                        pass
                os.replace(tmp, target)
                break
            except PermissionError as e:
                if attempt == max_retries - 1:
                    # Final attempt fallback: write directly if replace fails
                    try:
                        with open(target, "w", encoding="utf-8", newline="\n") as handle:
                            handle.write(text)
                    except Exception:
                        raise e
                else:
                    time.sleep(0.1 * (attempt + 1))
                    gc.collect()
    finally:
        if tmp.exists():
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass


def read_json(path: str | Path, *, retries: int = 6, retry_delay_s: float = 0.12) -> dict[str, Any]:
    target = coerce_report_path(path)
    if not target.exists():
        return {}
    last_exc: Exception | None = None
    for attempt in range(max(1, retries)):
        try:
            with open(target, "r", encoding="utf-8") as handle:
                obj = json.load(handle)
            return obj if isinstance(obj, dict) else {}
        except (OSError, json.JSONDecodeError, ValueError) as ex:
            last_exc = ex
            if attempt + 1 < retries:
                time.sleep(retry_delay_s * (attempt + 1))
    if last_exc is not None:
        raise last_exc
    return {}


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = coerce_report_path(path)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    _atomic_write_text(target, text)


def write_text_file(path: str | Path, text: str) -> None:
    _atomic_write_text(coerce_report_path(path), text)


def write_md(path: str | Path, title: str, sections: list[tuple[str, Any]]) -> None:
    lines = [f"# {title}", ""]
    for name, data in sections:
        lines.append(f"## {name}")
        lines.append("```json")
        lines.append(json.dumps(data, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")
    write_text_file(path, "\n".join(lines).rstrip() + "\n")


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
