"""Smoke test: verify image_base64 present and no duplicate direction text for 3 cumulative components."""
import sys
import importlib.util
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

COMPONENTS = {
    "src_3884": (
        "agent_skills_v3/vh_數學B4_StatisticalChartReading/components/src_3884/generate.py",
        "cumulative_above_fail_count",
    ),
    "src_3885": (
        "agent_skills_v3/vh_數學B4_StatisticalChartReading/components/src_3885/generate.py",
        "cumulative_above_interval_count",
    ),
    "src_3886": (
        "agent_skills_v3/vh_數學B4_StatisticalChartReading/components/src_3886/generate.py",
        "cumulative_below_interval_count",
    ),
}

all_pass = True

for cid, (path, op) in COMPONENTS.items():
    spec = importlib.util.spec_from_file_location("gen_" + cid, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print(f"=== {cid} ({op}) ===")
    for seed in range(1, 6):
        p = mod.generate(seed=seed)
        qt = p.get("question_text", "")
        dup = "以上以上" in qt or "以下以下" in qt
        has_img = bool((p.get("image_base64") or "").strip())
        has_vs = bool(p.get("visual_spec"))
        img_len = len(p.get("image_base64") or "")
        ok = has_img and not dup
        if not ok:
            all_pass = False
        status = "PASS" if ok else "FAIL"
        print(
            f"  seed={seed} {status} | dup={dup} | has_img={has_img} | "
            f"has_vs={has_vs} | img_len={img_len}"
        )
        if seed == 1:
            # Print question_text for first seed to verify correctness
            print(f"  question_text: {qt[:80]!r}")
    print()

print("api_call_count=0")
print("ALL_PASS:", all_pass)
sys.exit(0 if all_pass else 1)
