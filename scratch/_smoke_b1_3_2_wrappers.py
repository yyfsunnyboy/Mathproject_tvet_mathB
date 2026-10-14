# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    "rebuild_b1_3_2_execute", ROOT / "scratch" / "_rebuild_b1_3_2_execute.py"
)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

FIN = json.loads((ROOT / "scratch/_b1_3_2_finalize_results.json").read_text(encoding="utf-8"))
verified = {
    skill: sorted(x["component_id"] for x in FIN["results"] if x["skill_id"] == skill and x["status"] == "VERIFIED")
    for skill in ("vh_數學B1_RemainderTheorem", "vh_數學B1_FactorTheorem")
}

out = {"smoke": [], "wrappers": {}}
for skill in ("vh_數學B1_RemainderTheorem", "vh_數學B1_FactorTheorem"):
    smoke = mod._smoke_skill(skill, 40)
    wrap = mod._load_module(ROOT / "skills" / f"{skill}.py", f"wrap_{skill}")
    keys = list(getattr(wrap, "GENERATOR_KEYS", []) or [])
    extra = sorted(set(keys) - set(verified[skill]))
    missing = sorted(set(verified[skill]) - set(keys))
    print("SMOKE", skill, smoke["passed"], "/", smoke["samples"], "failed", smoke["failed"])
    print("  hits", smoke.get("hits"))
    print("  missing_in_40", smoke.get("missing_in_40"), "targeted", smoke.get("targeted"))
    print("WRAPPER", skill, "keys", keys)
    print("  extra", extra, "missing_verified", missing)
    out["smoke"].append(smoke)
    out["wrappers"][skill] = {
        "keys": keys,
        "extra_non_verified": extra,
        "missing_verified": missing,
    }

(ROOT / "scratch/_b1_3_2_smoke_final.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
)
