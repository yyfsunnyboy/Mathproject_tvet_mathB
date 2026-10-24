"""Real-Gemini check of the four Unit 9 parabola-drawing items (12567, 12570, 12576, 12587), on their real canvases.

Reuses ``real_vision_check`` (canvas renderer, key loading through the project's .env mechanism).  Every canvas
spec comes from the generated question payload (same ``axis_range`` the student sees).  Final verdicts are the
formal ``analyze_drawing`` / ``evaluate_parabola_graph`` outcome.

    python reports/gh_unit9_grader/real_vision_check_items.py [--repeat 2]
"""
from __future__ import annotations

import json
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import real_vision_check as R  # noqa: E402  (loads .env like app.py)
from core.services import drawing_answer_analysis_service as svc  # noqa: E402


def payload_for(op_items: dict) -> dict:
    from agent_domains_candidate.function_linear_quadratic.sandbox_harness import register_candidate_in_memory
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    register_candidate_in_memory()
    return dispatch_registered_operation("function.linear_quadratic", "graph_quadratic_functions", seed=0, constraints=op_items)[1]


def canvas_specs(payload: dict) -> list[dict]:
    contract = payload["answer_contract"]
    if contract["answer_type"] == "drawing":
        return [contract["expected_drawing_spec"]]
    return [p["expected_drawing_spec"] for p in contract["parts"] if p["answer_type"] == "drawing"]


def draw_on(spec: dict, parabolas: list[tuple[float, float, float]], rng: random.Random, wobble: float) -> str:
    R.AXIS = dict(spec["axis_range"])
    img, d = R.canvas()
    for a, h, k in parabolas:
        # visible window of this curve inside the canvas
        lo, hi = R.AXIS["x_min"], R.AXIS["x_max"]
        xs = [x / 20 for x in range(int(lo * 20), int(hi * 20) + 1) if R.AXIS["y_min"] <= a * (x / 20 - h) ** 2 + k <= R.AXIS["y_max"]]
        if xs:
            R.stroke(d, lambda x, a=a, h=h, k=k: a * (x - h) ** 2 + k, min(xs), max(xs), rng, wobble=wobble)
    return R.data_url(img)


def expected(spec: dict) -> list[tuple[float, float, float]]:
    return [(e["a"], e["vertex"][0], e["vertex"][1]) for e in spec["expected_parabolas"]]


def judge(spec: dict, parabolas, rng, wobble) -> dict:
    url = draw_on(spec, parabolas, rng, wobble)
    res = svc.analyze_drawing(image_data_url=url, question_text="描繪拋物線", expected_drawing_spec=spec, context={})
    return {"is_correct": res.get("is_correct"), "status": res.get("status"), "confidence": res.get("confidence")}


def graph(*coeffs):
    return {"items": [{"coeffs": list(c)} for c in coeffs], "layout": "single" if len(coeffs) == 1 else "separate", "style": "plain" if len(coeffs) == 1 else "planes",
            "ask_vertex_axis": False}


def main() -> None:
    repeat = int(sys.argv[sys.argv.index("--repeat") + 1]) if "--repeat" in sys.argv else 2
    status = svc._resolve_analyzer_role()
    print("analyzer:", status.get("analyzer"), "available:", status.get("available"))
    if not status.get("available"):
        print("real vision model unavailable; nothing was run")
        return
    rows = []

    def record(item, case, want, spec, parabolas, wobble, rnd):
        out = judge(spec, parabolas, random.Random(f"{item}:{case}:{rnd}"), wobble)
        rows.append({"item": item, "case": case, "round": rnd, "want": want, "got": out["is_correct"], "status": out["status"], "confidence": out["confidence"]})
        print(rows[-1])

    offset = int(sys.argv[sys.argv.index("--seed-offset") + 1]) if "--seed-offset" in sys.argv else 0
    for rnd in range(offset, offset + repeat):
        # 12567: one curve; steeper and flatter curves, both openings, normal and larger hand wobble
        for a in (1, 3, -2, 5, Fraction(1, 2)):
            spec = canvas_specs(payload_for(graph([a, 0, 0])))[0]
            exp = expected(spec)
            record("12567", f"correct a={a}", True, spec, exp, 0.06, rnd)
            record("12567", f"correct a={a} sloppy", True, spec, exp, 0.12, rnd)
            if a in (3, -2):
                record("12567", f"wrong shifted a={a}", False, spec, [(exp[0][0], exp[0][1] + 2, exp[0][2] + 1.5)], 0.06, rnd)
                record("12567", f"wrong opening a={a}", False, spec, [(-exp[0][0], exp[0][1], exp[0][2])], 0.06, rnd)
        # 12570: y=-2x^2+4x+3
        spec = canvas_specs(payload_for({"items": [{"coeffs": [-2, 4, 3]}], "layout": "single", "style": "plain", "ask_vertex_axis": True}))[0]
        exp = expected(spec)
        record("12570", "correct", True, spec, exp, 0.06, rnd)
        record("12570", "wrong shifted", False, spec, [(exp[0][0], exp[0][1] - 2, exp[0][2])], 0.06, rnd)
        # 12576: two independent canvases (a) y=2x^2, (b) y=-x^2
        sa, sb = canvas_specs(payload_for(graph([2, 0, 0], [-1, 0, 0])))
        record("12576", "(a) correct", True, sa, expected(sa), 0.06, rnd)
        record("12576", "(b) correct", True, sb, expected(sb), 0.06, rnd)
        record("12576", "(a) drew (b)'s curve", False, sa, expected(sb), 0.06, rnd)
        record("12576", "(b) drew (a)'s curve", False, sb, expected(sa), 0.06, rnd)
        # 12587: two canvases y=x^2-2x-3 and y=-2x^2+x+3
        s1, s2 = canvas_specs(payload_for({"items": [{"coeffs": [1, -2, -3]}, {"coeffs": [-2, 1, 3]}], "layout": "separate", "style": "list", "ask_vertex_axis": True}))
        record("12587", "(1) correct", True, s1, expected(s1), 0.06, rnd)
        record("12587", "(2) correct", True, s2, expected(s2), 0.06, rnd)
        record("12587", "(1) drew (2)'s curve", False, s1, expected(s2), 0.06, rnd)
        record("12587", "(2) wrong shifted", False, s2, [(expected(s2)[0][0], expected(s2)[0][1] + 2, expected(s2)[0][2] - 1)], 0.06, rnd)

    summary = {
        "analyzer": status.get("analyzer"), "calls": len(rows), "accepted": sum(r["got"] is True for r in rows), "rejected": sum(r["got"] is False for r in rows),
        "uncertain": sum(r["got"] is None for r in rows),
        "false_accept": [f"{r['item']}:{r['case']}" for r in rows if r["want"] is False and r["got"] is True],
        "false_reject": [f"{r['item']}:{r['case']}" for r in rows if r["want"] is True and r["got"] is False],
        "uncertain_cases": [f"{r['item']}:{r['case']}" for r in rows if r["got"] is None],
    }
    by_item = {}
    for r in rows:
        by_item.setdefault(r["item"], []).append(r)
    summary["per_item"] = {k: {"calls": len(v), "exact": sum(x["got"] is x["want"] for x in v)} for k, v in by_item.items()}
    (HERE / "real_vision_check_items_result.json").write_text(json.dumps({**summary, "rows": rows}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
