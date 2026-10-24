"""Real-Gemini check of Unit 9 item 12568 (three parabolas y=3x^2, 3(x-2)^2, 3(x-2)^2+4 on one canvas)."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
import real_vision_check_items as I  # noqa: E402

repeat = int(sys.argv[sys.argv.index("--repeat") + 1]) if "--repeat" in sys.argv else 3
spec = I.canvas_specs(I.payload_for({"items": [{"coeffs": [3, 0, 0], "name": "f"}, {"coeffs": [3, -12, 12], "name": "g", "form": "vertex"},
                                             {"coeffs": [3, -12, 16], "name": "h", "form": "vertex"}], "layout": "same_canvas", "style": "same_plane"}))[0]
F, G, H = (3, 0, 0), (3, 2, 0), (3, 2, 4)
CASES = [
    ("all three correct", True, [F, G, H]), ("all three correct, sloppy", True, [F, G, H]),
    ("only two drawn", False, [F, G]), ("same curve repeated x3", False, [F, F, F]),
    ("horizontal shift wrong (g at 3)", False, [F, (3, 3, 0), (3, 3, 4)]),
    ("vertical shift wrong (h at 7)", False, [F, G, (3, 2, 7)]),
    ("opening wrong (h opens down)", False, [F, G, (-3, 2, 11)]),
    ("curvature wrong (a=1)", False, [(1, 0, 0), (1, 2, 0), (1, 2, 4)]),
    ("curvature wrong (a=6)", False, [(6, 0, 0), (6, 2, 0), (6, 2, 4)]),
]
rows = []
for rnd in range(repeat):
    for name, want, curves in CASES:
        out = I.judge(spec, curves, random.Random(f"12568:{name}:{rnd}"), 0.12 if "sloppy" in name else 0.06)
        rows.append({"case": name, "round": rnd, "want": want, "got": out["is_correct"], "status": out["status"], "confidence": out["confidence"]})
        print(rows[-1])
summary = {"calls": len(rows), "exact": sum(r["got"] is r["want"] for r in rows), "uncertain": sum(r["got"] is None for r in rows),
           "false_accept": [r["case"] for r in rows if r["want"] is False and r["got"] is True],
           "false_reject": [r["case"] for r in rows if r["want"] is True and r["got"] is False]}
(HERE / "real_vision_check_12568_result.json").write_text(json.dumps({**summary, "rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
print(summary)
