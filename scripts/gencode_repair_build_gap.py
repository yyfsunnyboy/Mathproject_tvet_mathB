from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"

from core.gencode.repair_catalog import VERIFIER_REPAIR_CATALOG


def _format_list(xs: list[Any]) -> str:
    return "無" if not xs else ", ".join(str(x) for x in xs)


def _run(cmd: list[str], timeout: int = 240) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


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
        f"# Gencode 修復報告：{payload.get('gap','')}",
        "",
        f"- skill_id: {payload.get('skill_id','')}",
        f"- repair_status: {payload.get('repair_status','')}",
        f"- missing_before: {_format_list(payload.get('missing_verifier_keys_before_repair', payload.get('missing_checker_keys_before_repair', [])))}",
        f"- missing_after: {_format_list(payload.get('missing_verifier_keys_after_repair', payload.get('missing_checker_keys_after_repair', [])))}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _summary_missing_verifier(payload: dict[str, Any]) -> str:
    skill_id = payload.get("skill_id", "")
    py_ok = all(v is True for v in payload.get("py_compile_results", {}).values())
    pytests = payload.get("pytest_results", {})
    pytest_ok = all(v.get("passed", False) for v in pytests.values()) if pytests else True
    return "\n".join(
        [
            "============================================================",
            "Gencode 修復摘要：missing_verifier",
            "============================================================",
            f"skill_id: {skill_id}",
            f"repair_status: {payload.get('repair_status', '')}",
            "",
            "修復前缺少 verifier:",
            f"- {_format_list(payload.get('missing_verifier_keys_before_repair', []))}",
            "",
            "已存在 verifier:",
            f"- {_format_list(payload.get('existing_verifier_keys', []))}",
            "",
            "已建立 verifier:",
            f"- {_format_list(payload.get('created_verifier_files', []))}",
            "",
            "無法支援的 verifier:",
            f"- {_format_list(payload.get('unsupported_verifier_keys', []))}",
            "",
            "因缺少 checker 而暫停:",
            f"- {_format_list(payload.get('blocked_by_missing_checker', []))}",
            "",
            "測試結果:",
            f"- py_compile: {'通過' if py_ok else '失敗'}",
            f"- pytest: {'通過' if pytest_ok else '失敗'}",
            "",
            "修復後仍缺少 verifier:",
            f"- {_format_list(payload.get('missing_verifier_keys_after_repair', []))}",
            "",
            "下一步建議:",
            f"重新執行 Phase 2：\npython scripts\\gencode_pipeline_phase2_build.py --skill-id {skill_id}",
            "============================================================",
        ]
    )


def _summary_missing_checker(payload: dict[str, Any]) -> str:
    skill_id = payload.get("skill_id", "")
    py_ok = all(v is True for v in payload.get("py_compile_results", {}).values())
    pytest_ok = payload.get("pytest_results", {}).get("passed", False)
    return "\n".join(
        [
            "============================================================",
            "Gencode 修復摘要：missing_checker",
            "============================================================",
            f"skill_id: {skill_id}",
            f"repair_status: {payload.get('repair_status', '')}",
            "",
            "修復前缺少 checker:",
            f"- {_format_list(payload.get('missing_checker_keys_before_repair', []))}",
            "",
            "已建立 checker:",
            f"- {_format_list(payload.get('created_checker_files', []))}",
            "",
            "已更新匯出:",
            "- core/checkers/__init__.py",
            "",
            "測試:",
            f"- py_compile: {'通過' if py_ok else '失敗'}",
            f"- pytest tests/test_interval_checker.py: {'通過' if pytest_ok else '失敗'}",
            "",
            "修復後仍缺少 checker:",
            f"- {_format_list(payload.get('missing_checker_keys_after_repair', []))}",
            "",
            "下一步建議:",
            f"重新執行 Phase 2：\npython scripts\\gencode_pipeline_phase2_build.py --skill-id {skill_id}",
            "============================================================",
        ]
    )


def _repair_missing_checker(skill_id: str, phase2_path: Path) -> dict[str, Any]:
    phase2 = _read_json(phase2_path)
    dep = phase2.get("build_dependency_plan", {}) if isinstance(phase2.get("build_dependency_plan"), dict) else {}
    missing_before = list(dep.get("missing_checkers", []) or [])
    created_files: list[str] = []
    warnings: list[str] = []
    blocking: list[str] = []

    if "interval_checker" in missing_before:
        interval_file = PROJECT_ROOT / "core" / "checkers" / "interval_checker.py"
        if not interval_file.exists():
            blocking.append("interval_checker_missing_file")
        else:
            warnings.append("interval_checker_exists")
    else:
        warnings.append("interval_checker_not_required")

    py_compile_results: dict[str, bool] = {}
    for rel in ["scripts/gencode_repair_build_gap.py", "core/checkers/interval_checker.py", "core/checkers/__init__.py"]:
        code, _, _ = _run([sys.executable, "-m", "py_compile", rel], timeout=120)
        py_compile_results[rel] = code == 0
        if code != 0:
            blocking.append(f"py_compile_failed:{rel}")

    t_code, t_out, t_err = _run([sys.executable, "-m", "pytest", "tests/test_interval_checker.py", "-q"], timeout=180)
    pytest_results = {"passed": t_code == 0, "output": (t_out + t_err).strip()}
    if t_code != 0:
        blocking.append("pytest_failed:test_interval_checker")

    _run([sys.executable, "scripts/gencode_pipeline_phase2_build.py", "--skill-id", skill_id], timeout=300)
    phase2_after = _read_json(phase2_path)
    dep_after = phase2_after.get("build_dependency_plan", {}) if isinstance(phase2_after.get("build_dependency_plan"), dict) else {}
    missing_after = list(dep_after.get("missing_checkers", []) or [])

    repair_status = "PASS" if not missing_after and not blocking else ("PARTIAL" if not blocking else "FAIL")
    return {
        "skill_id": skill_id,
        "gap": "missing_checker",
        "repair_status": repair_status,
        "checked_checker_keys": sorted(set(missing_before)),
        "created_checker_files": created_files,
        "existing_checker_keys": dep_after.get("existing_checkers", []),
        "missing_checker_keys_before_repair": missing_before,
        "missing_checker_keys_after_repair": missing_after,
        "tests_run": ["py_compile", "pytest tests/test_interval_checker.py -q", f"phase2_build {skill_id}"],
        "py_compile_results": py_compile_results,
        "pytest_results": pytest_results,
        "blocking_reasons": blocking,
        "warnings": warnings,
    }


def _repair_missing_verifier(skill_id: str, phase2_path: Path) -> dict[str, Any]:
    phase2 = _read_json(phase2_path)
    dep = phase2.get("build_dependency_plan", {}) if isinstance(phase2.get("build_dependency_plan"), dict) else {}
    missing_before = list(dep.get("missing_verifiers", []) or [])
    missing_checkers = set(dep.get("missing_checkers", []) or [])

    created_verifier_files: list[str] = []
    existing_verifier_keys: list[str] = []
    unsupported: list[str] = []
    blocked_by_checker: list[str] = []
    known_not_impl: list[str] = []
    blocking: list[str] = []
    warnings: list[str] = []
    py_compile_results: dict[str, bool] = {}
    pytest_results: dict[str, Any] = {}

    for key in missing_before:
        cfg = VERIFIER_REPAIR_CATALOG.get(key)
        if not cfg:
            unsupported.append(key)
            continue
        if not cfg.get("implemented", False):
            known_not_impl.append(key)
            continue
        deps = set(cfg.get("depends_on_checkers", []))
        if deps & missing_checkers:
            blocked_by_checker.append(key)
            continue
        module_path = PROJECT_ROOT / str(cfg["module_path"])
        if module_path.exists():
            existing_verifier_keys.append(key)
        else:
            blocking.append(f"verifier_module_missing:{key}")
        c_code, _, _ = _run([sys.executable, "-m", "py_compile", str(cfg["module_path"])], timeout=120)
        py_compile_results[str(cfg["module_path"])] = c_code == 0
        if c_code != 0:
            blocking.append(f"py_compile_failed:{cfg['module_path']}")
        test_path = str(cfg["test_path"])
        t_code, t_out, t_err = _run([sys.executable, "-m", "pytest", test_path, "-q"], timeout=180)
        pytest_results[test_path] = {"passed": t_code == 0, "output": (t_out + t_err).strip()}
        if t_code != 0:
            blocking.append(f"pytest_failed:{test_path}")

    _run([sys.executable, "scripts/gencode_pipeline_phase2_build.py", "--skill-id", skill_id], timeout=300)
    phase2_after = _read_json(phase2_path)
    dep_after = phase2_after.get("build_dependency_plan", {}) if isinstance(phase2_after.get("build_dependency_plan"), dict) else {}
    missing_after = list(dep_after.get("missing_verifiers", []) or [])

    repair_status = "PASS"
    if blocking:
        repair_status = "FAIL"
    elif missing_after:
        repair_status = "PARTIAL"

    return {
        "skill_id": skill_id,
        "gap": "missing_verifier",
        "repair_status": repair_status,
        "checked_verifier_keys": sorted(set(missing_before)),
        "created_verifier_files": created_verifier_files,
        "existing_verifier_keys": sorted(set(existing_verifier_keys)),
        "unsupported_verifier_keys": sorted(set(unsupported)),
        "blocked_by_missing_checker": sorted(set(blocked_by_checker)),
        "missing_verifier_keys_before_repair": missing_before,
        "missing_verifier_keys_after_repair": missing_after,
        "catalog_known_but_not_implemented": sorted(set(known_not_impl)),
        "tests_run": ["py_compile verifier modules", "pytest verifier tests", f"phase2_build {skill_id}"],
        "py_compile_results": py_compile_results,
        "pytest_results": pytest_results,
        "blocking_reasons": blocking,
        "warnings": warnings,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-id", required=True)
    p.add_argument("--gap", required=True, choices=["missing_checker", "missing_verifier"])
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    skill_id = args.skill_id
    phase2_path = REPORT_DIR / f"{skill_id}_phase2_build.json"
    if not phase2_path.exists():
        raise RuntimeError(f"找不到 Phase 2 報告: {phase2_path}")

    if args.gap == "missing_checker":
        payload = _repair_missing_checker(skill_id, phase2_path)
        out_json = REPORT_DIR / f"{skill_id}_repair_missing_checker.json"
        out_md = REPORT_DIR / f"{skill_id}_repair_missing_checker.md"
    else:
        payload = _repair_missing_verifier(skill_id, phase2_path)
        out_json = REPORT_DIR / f"{skill_id}_repair_missing_verifier.json"
        out_md = REPORT_DIR / f"{skill_id}_repair_missing_verifier.md"

    payload["artifact_paths"] = {"repair_json": str(out_json), "repair_md": str(out_md), "phase2_json": str(phase2_path)}
    payload["timestamp"] = _read_json(phase2_path).get("timestamp", "")

    _write_json(out_json, payload)
    _write_md(out_md, payload)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(_summary_missing_verifier(payload) if args.gap == "missing_verifier" else _summary_missing_checker(payload))


if __name__ == "__main__":
    main()

