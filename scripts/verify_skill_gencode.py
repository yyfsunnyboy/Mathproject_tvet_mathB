import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _read_registry(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore

    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-id", required=True)
    p.add_argument("--sample-count", type=int, default=30)
    args = p.parse_args()

    root = PROJECT_ROOT
    reg_path = root / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml"
    reg = _read_registry(reg_path)
    verified = [v for v in (reg.get("verified_problem_types", []) or []) if isinstance(v, dict) and v.get("skill_id") == args.skill_id]

    first_error = ""
    ok_registry = len(verified) > 0
    if not ok_registry:
        first_error = "registry has no verified candidate for skill"
    else:
        for v in verified:
            cp = root / str(v.get("candidate_path", ""))
            if not cp.exists():
                ok_registry = False
                first_error = f"candidate path missing: {cp}"
                break

    samples = []
    unique_pts = set()
    ok_generate = False
    runtime_cov = {
        "expected_problem_types": sorted({str(v.get("problem_type_id", "")).strip() for v in verified if str(v.get("problem_type_id", "")).strip()}),
        "observed_problem_types": [],
        "missing_problem_types": [],
        "sample_count": args.sample_count,
        "status": "fail",
    }

    if ok_registry:
        try:
            mod = importlib.import_module(f"skills.{args.skill_id}")
            for _ in range(args.sample_count):
                q = mod.generate(level=1)
                samples.append(q)
                unique_pts.add(str(q.get("problem_type_id", "")).strip())
            ok_generate = all(bool(str(s.get("question_text", "")).strip()) and str(s.get("answer", "")).strip() != "" for s in samples)
            if not ok_generate and not first_error:
                first_error = "sample question_text/answer empty"
        except Exception as e:
            ok_generate = False
            if not first_error:
                first_error = f"wrapper generate failed: {e}"

    runtime_cov["observed_problem_types"] = sorted([x for x in unique_pts if x])
    runtime_cov["missing_problem_types"] = sorted([x for x in runtime_cov["expected_problem_types"] if x not in unique_pts])
    runtime_cov["status"] = "pass" if len(runtime_cov["missing_problem_types"]) == 0 and ok_generate and ok_registry else "fail"

    pytest_target = "tests/test_b1_absolute_value_skill_wrapper.py"
    if args.skill_id == "vh_數學B1_AbsoluteValueInequality":
        pytest_target = "tests/test_b1_absolute_value_inequality_runtime_wrapper.py"
    elif args.skill_id == "vh_數學B1_DistanceBetweenTwoPointsInPlane":
        pytest_target = "tests/gencode/test_phase1_distance_between_two_points.py"
    elif args.skill_id == "vh_數學B1_MidpointCoordinates":
        pytest_target = "tests/test_gencode_midpoint_coordinates_regression.py"
    test_cmd = [sys.executable, "-m", "pytest", pytest_target, "-q"]
    tr = subprocess.run(test_cmd, cwd=str(root), capture_output=True, text=True, timeout=180)
    ok_pytest = tr.returncode == 0
    if not ok_pytest and not first_error:
        first_error = "pytest failed"

    passed = ok_registry and ok_generate and ok_pytest and runtime_cov["status"] == "pass"
    report = root / "reports" / "gencode_closed_loop" / f"{args.skill_id}_verify_report.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Verify Report: {args.skill_id}",
        "",
        f"- python: {sys.executable}",
        f"- registry: {reg_path}",
        f"- registry_verified_count: {len(verified)}",
        f"- pytest_exit_code: {tr.returncode}",
        f"- unique_problem_type_count: {len(unique_pts)}",
        f"- PASS: {passed}",
    ]
    if first_error:
        lines.append(f"- first_blocking_error: {first_error}")
    lines += [
        "",
        "## Runtime ProblemType Coverage",
        "```json",
        json.dumps(runtime_cov, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Verified Entries",
        "```json",
        json.dumps(verified, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Pytest Output",
        "```text",
        (tr.stdout + tr.stderr).strip(),
        "```",
        "",
        "## Samples",
        "```json",
        json.dumps(samples, ensure_ascii=False, indent=2),
        "```",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "success": passed,
                "report": str(report),
                "first_error": first_error,
                "runtime_problem_type_coverage": runtime_cov,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
