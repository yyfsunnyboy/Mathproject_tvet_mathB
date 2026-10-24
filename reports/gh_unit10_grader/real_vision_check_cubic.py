"""Real-Gemini check of the cubic_graph grader on the six Unit 10 drawing items, on their real canvases.

Reuses the Unit 9 renderer (grid + printed axes + wobbly pen strokes) and the project's .env key loading.  Every canvas
spec comes from a generated question payload (the axis_range the student sees).  The verdict is the formal
``analyze_drawing`` / ``evaluate_cubic_graph`` outcome.

    python reports/gh_unit10_grader/real_vision_check_cubic.py [--repeat 2]
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "reports" / "gh_unit9_grader"))
sys.path.insert(0, str(ROOT))

import real_vision_check as R  # noqa: E402  (loads .env like app.py)
from core.services import drawing_answer_analysis_service as svc  # noqa: E402


def spec_for(item: dict, ask: list | None = None) -> dict:
    from agent_domains_candidate.function_cubic.sandbox_harness import register_candidate_in_memory
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    register_candidate_in_memory()
    payload = dispatch_registered_operation("function.cubic_graph", "graph_cubic_functions", seed=0, constraints={"items": [item], "ask": ask or []})[1]
    contract = payload["answer_contract"]
    if contract["answer_type"] == "drawing":
        return contract["expected_drawing_spec"]
    return next(p["expected_drawing_spec"] for p in contract["parts"] if p["answer_type"] == "drawing")


def cubic(a, p, h, k):
    return lambda x: a * (x - h) ** 3 + p * (x - h) + k


def draw(spec: dict, fn, rng: random.Random, wobble: float, *, parabola: bool = False) -> str:
    R.AXIS = dict(spec["axis_range"])
    img, d = R.canvas()
    lo, hi = R.AXIS["x_min"], R.AXIS["x_max"]
    xs = [x / 20 for x in range(int(lo * 20), int(hi * 20) + 1) if R.AXIS["y_min"] <= fn(x / 20) <= R.AXIS["y_max"]]
    if xs:
        R.stroke(d, fn, min(xs), max(xs), rng, wobble=wobble)
    return R.data_url(img)


def judge(spec: dict, fn, rng, wobble) -> dict:
    res = svc.analyze_drawing(image_data_url=draw(spec, fn, rng, wobble), question_text="描繪三次函數", expected_drawing_spec=spec, context={})
    return {"is_correct": res.get("is_correct"), "status": res.get("status"), "confidence": res.get("confidence")}


ITEMS = {  # name -> (item, expected function params)
    "12603 y=x^3": ({"coeffs": [1, 0, 0, 0]}, (1, 0, 0, 0)),
    "12604 y=x^3+2x": ({"coeffs": [1, 0, 2, 0]}, (1, 2, 0, 0)),
    "12605 y=x^3-x": ({"coeffs": [1, 0, -1, 0]}, (1, -1, 0, 0)),
    "12606 y=(x-3)^3+2(x-3)+1": ({"form": {"a": 1, "p": 2, "h": 3, "k": 1}}, (1, 2, 3, 1)),
    "12607 y=x^3-6x^2+11x-3": ({"coeffs": [1, -6, 11, -3]}, (1, -1, 2, 3)),
    "12613 y=-x^3+3x^2-2x-2": ({"coeffs": [-1, 3, -2, -2]}, (-1, 1, 1, -2)),
}


def main() -> None:
    repeat = int(sys.argv[sys.argv.index("--repeat") + 1]) if "--repeat" in sys.argv else 2
    status = svc._resolve_analyzer_role()
    print("analyzer:", status.get("analyzer"), "available:", status.get("available"))
    if not status.get("available"):
        print("real vision model unavailable; nothing was run")
        return
    rows = []

    def record(item, case, want, spec, fn, wobble, rnd):
        out = judge(spec, fn, random.Random(f"{item}:{case}:{rnd}"), wobble)
        rows.append({"item": item, "case": case, "round": rnd, "want": want, "got": out["is_correct"], "status": out["status"], "confidence": out["confidence"]})
        print(rows[-1], flush=True)

    for rnd in range(repeat):
        for name, (item, (a, p, h, k)) in ITEMS.items():
            spec = spec_for(item, ["center"] if "12606" in name else [])
            record(name, "correct", True, spec, cubic(a, p, h, k), 0.06, rnd)
            record(name, "correct sloppy", True, spec, cubic(a, p, h, k), 0.12, rnd)
            record(name, "mirrored (wrong orientation)", False, spec, cubic(-a, -p, h, k), 0.06, rnd)
            record(name, "centre shifted by (2, 1.5)", False, spec, cubic(a, p, h + 2, k + 1.5), 0.06, rnd)
            record(name, "parabola instead", False, spec, lambda x, h=h, k=k: 0.6 * (x - h) ** 2 + k - 2, 0.06, rnd)
            record(name, "straight line instead", False, spec, lambda x, h=h, k=k: 1.5 * (x - h) + k, 0.06, rnd)
            if p < 0 and a > 0:  # wavy cubic drawn as a monotone one through the same centre
                record(name, "wave missing (monotone)", False, spec, cubic(a, abs(p) + 0.2, h, k), 0.06, rnd)
            elif p > 0 and a < 0:
                record(name, "wave missing (monotone)", False, spec, cubic(a, -abs(p) - 0.2, h, k), 0.06, rnd)
            if p > 0 and a > 0:  # monotone cubic drawn with a wave
                record(name, "wave added", False, spec, cubic(a, -2.5 * p - 1.0, h, k), 0.06, rnd)
    summary = {
        "analyzer": status.get("analyzer"), "calls": len(rows), "exact": sum(r["got"] is r["want"] for r in rows),
        "uncertain": sum(r["got"] is None for r in rows),
        "false_accept": [f"{r['item']}:{r['case']}" for r in rows if r["want"] is False and r["got"] is True],
        "false_reject": [f"{r['item']}:{r['case']}" for r in rows if r["want"] is True and r["got"] is False],
        "uncertain_cases": [f"{r['item']}:{r['case']}" for r in rows if r["got"] is None],
    }
    by_case: dict[str, dict] = {}
    for r in rows:
        c = by_case.setdefault(r["case"], {"calls": 0, "exact": 0, "accepted": 0, "rejected": 0, "uncertain": 0})
        c["calls"] += 1
        c["exact"] += r["got"] is r["want"]
        c["accepted"] += r["got"] is True
        c["rejected"] += r["got"] is False
        c["uncertain"] += r["got"] is None
    summary["per_case"] = by_case
    (HERE / "real_vision_check_cubic_result.json").write_text(json.dumps({**summary, "rows": rows}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "per_case"}, ensure_ascii=False))
    for case, c in by_case.items():
        print(case, c)


if __name__ == "__main__":
    main()
