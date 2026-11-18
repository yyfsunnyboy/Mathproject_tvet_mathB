"""Live smoke after Flask 5001 restart: process up + published facades importable + HTTP home."""
from __future__ import annotations

import importlib
import json
import socket
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).resolve().parent / "deploy_unit9_rev1_live_smoke.json"
SKILLS = ("gh_CorrelationCoefficient", "gh_LeastSquaresMethodAndRegressionLine")
DEFERRED = (12947, 12948, 12954, 12960, 12963)


def port_open(port: int) -> bool:
    with socket.create_connection(("127.0.0.1", port), timeout=3):
        return True


def main() -> None:
    home = requests.get("http://127.0.0.1:5001/", timeout=15)
    facades = {}
    for skill in SKILLS:
        mod = importlib.import_module(f"skills.{skill}")
        importlib.reload(mod)
        payload = mod.generate(seed=0)
        keys = set(getattr(mod, "GENERATOR_KEYS", ()) or ())
        facades[skill] = {
            "keys": sorted(keys),
            "n": len(keys),
            "seed0_id": payload.get("textbook_example_id"),
            "has_answer": payload.get("correct_answer") not in (None, ""),
            "route_ready": (ROOT / "agent_skills_v3" / skill / "component_manifest.json").is_file(),
        }
    # Ensure deferred IDs are absent from published manifests.
    absent = {}
    for skill in SKILLS:
        data = json.loads((ROOT / "agent_skills_v3" / skill / "component_manifest.json").read_text(encoding="utf-8"))
        ids = {int(c["textbook_example_id"]) for c in data.get("components") or [] if isinstance(c, dict)}
        absent[skill] = sorted(set(DEFERRED) & ids)
    report = {
        "port_5001_open": port_open(5001),
        "port_5000_open": port_open(5000),
        "home_status": home.status_code,
        "facades": facades,
        "deferred_absent_from_manifests": absent,
        "scatter_facade_absent": not (ROOT / "skills" / "gh_ScatterPlot.py").exists(),
    }
    report["passed"] = bool(
        report["port_5001_open"]
        and report["port_5000_open"]
        and home.status_code == 200
        and facades["gh_CorrelationCoefficient"]["n"] == 11
        and facades["gh_LeastSquaresMethodAndRegressionLine"]["n"] == 10
        and all(f["has_answer"] and f["route_ready"] for f in facades.values())
        and all(not v for v in absent.values())
        and report["scatter_facade_absent"]
        and 12963 not in facades["gh_LeastSquaresMethodAndRegressionLine"]["keys"]
    )
    # GENERATOR_KEYS use src_ID strings
    report["passed"] = report["passed"] and "src_12963" not in set(facades["gh_LeastSquaresMethodAndRegressionLine"]["keys"])
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "facades": {k: {"n": v["n"], "seed0": v["seed0_id"]} for k, v in facades.items()},
                      "ports": {"5001": report["port_5001_open"], "5000": report["port_5000_open"]}}, ensure_ascii=False, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
