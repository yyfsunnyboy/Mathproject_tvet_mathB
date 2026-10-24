"""Real vision-model check of the parabola_graph grader (needs a configured Gemini key; run where one exists).

Renders hand-drawn-looking canvases (grid + printed axes + wobbly pen strokes) for representative answers and sends
each through ``analyze_drawing`` with the real analyzer.  The mock evaluator tests are separate
(``tests/test_parabola_graph_drawing_evaluator.py``); this script is the *real-AI* evidence.

    python reports/gh_unit9_grader/real_vision_check.py [--repeat 3]
Writes ``real_vision_check_result.json`` next to this file.
"""
from __future__ import annotations

import base64
import io
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from PIL import Image, ImageDraw  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

# same loading mechanism as app.py: the project's .env populates os.environ (the key itself is never printed or stored)
load_dotenv(ROOT / ".env", override=True)

from core.services import drawing_answer_analysis_service as svc  # noqa: E402

AXIS = {"x_min": -6, "x_max": 6, "y_min": -4, "y_max": 12}
W, H = 720, 480


def px(x: float, y: float) -> tuple[float, float]:
    return ((x - AXIS["x_min"]) / (AXIS["x_max"] - AXIS["x_min"]) * W, H - (y - AXIS["y_min"]) / (AXIS["y_max"] - AXIS["y_min"]) * H)


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    for gx in range(AXIS["x_min"], AXIS["x_max"] + 1):
        d.line([px(gx, AXIS["y_min"]), px(gx, AXIS["y_max"])], fill=(225, 225, 225, 255), width=1)
        d.text((px(gx, 0)[0] + 2, px(0, 0)[1] + 2), str(gx), fill=(90, 90, 90, 255))
    for gy in range(AXIS["y_min"], AXIS["y_max"] + 1):
        d.line([px(AXIS["x_min"], gy), px(AXIS["x_max"], gy)], fill=(225, 225, 225, 255), width=1)
        d.text((px(0, 0)[0] + 3, px(0, gy)[1] - 5), str(gy), fill=(90, 90, 90, 255))
    d.line([px(AXIS["x_min"], 0), px(AXIS["x_max"], 0)], fill=(60, 60, 60, 255), width=2)
    d.line([px(0, AXIS["y_min"]), px(0, AXIS["y_max"])], fill=(60, 60, 60, 255), width=2)
    return img, d


def stroke(d: ImageDraw.ImageDraw, f, lo: float, hi: float, rng: random.Random, wobble: float = 0.06, color=(20, 30, 160, 255)) -> None:
    pts = []
    for i in range(61):
        x = lo + (hi - lo) * i / 60
        pts.append(px(x + rng.uniform(-wobble, wobble), f(x) + rng.uniform(-wobble, wobble)))
    d.line(pts, fill=color, width=4, joint="curve")


def data_url(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def spec(*parabolas) -> dict:
    return {"drawing_type": "parabola_graph", "graph_kind": "parabola_graph", "required_elements": ["x_axis", "y_axis", "parabola_curve"],
            "axis_range": AXIS, "expected_parabolas": [{"a": a, "vertex": [h, k]} for a, h, k in parabolas]}


def case(draw_fn, expected_spec, want):
    return {"draw": draw_fn, "spec": expected_spec, "want": want}


def build_cases(rng: random.Random) -> dict:
    def one(a, h, k, shift=(0, 0), lo=-3.2, hi=3.2):
        def draw(d):
            stroke(d, lambda x: a * (x - h - shift[0]) ** 2 + k + shift[1], lo + h + shift[0], hi + h + shift[0], rng)
        return draw

    def line(d): stroke(d, lambda x: 2 * x + 1, -4, 4, rng)
    def vshape(d): stroke(d, lambda x: 2 * abs(x - 1), -2, 4, rng)
    def blank(d): pass

    def three(d):
        for a, h, k in ((1, 0, 0), (1, 2, 0), (1, 2, 4)):
            stroke(d, lambda x, a=a, h=h, k=k: a * (x - h) ** 2 + k, h - 3.0, h + 3.0, rng)

    def repeated(d):
        for _ in range(3):
            stroke(d, lambda x: x * x, -3.2, 3.2, rng)

    def two_of_three(d):
        for a, h, k in ((1, 0, 0), (1, 2, 0)):
            stroke(d, lambda x, a=a, h=h, k=k: a * (x - h) ** 2 + k, h - 3.0, h + 3.0, rng)

    return {
        "up_correct_y=x^2": case(one(1, 0, 0), spec((1, 0, 0)), True),
        "down_correct_y=-2(x-1)^2+5": case(one(-2, 1, 5, lo=-1.8, hi=1.8), spec((-2, 1, 5)), True),
        "wrong_vertex_shifted": case(one(1, 0, 0, shift=(2, 1)), spec((1, 0, 0)), False),
        "wrong_direction": case(one(-1, 0, 8), spec((1, 0, 0)), False),
        "line_instead": case(line, spec((1, 0, 0)), False),
        "v_shape_instead": case(vshape, spec((2, 1, 0)), False),
        "blank": case(blank, spec((1, 0, 0)), False),
        "three_curves_complete": case(three, spec((1, 0, 0), (1, 2, 0), (1, 2, 4)), True),
        "three_expected_two_drawn": case(two_of_three, spec((1, 0, 0), (1, 2, 0), (1, 2, 4)), False),
        "three_expected_same_curve_x3": case(repeated, spec((1, 0, 0), (1, 2, 0), (1, 2, 4)), False),
    }


def main() -> None:
    repeat = int(sys.argv[sys.argv.index("--repeat") + 1]) if "--repeat" in sys.argv else 1
    status = svc._resolve_analyzer_role()
    print("analyzer:", status)
    if not status.get("available"):
        result = {"ran": False, "reason": status.get("reason"), "analyzer": status.get("analyzer")}
        (HERE / "real_vision_check_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print("real vision model unavailable; nothing was run:", result)
        return
    rows = []
    for round_ in range(repeat):
        for name, c in build_cases(random.Random(round_)).items():
            img, d = canvas()
            c["draw"](d)
            res = svc.analyze_drawing(image_data_url=data_url(img), question_text="描繪拋物線", expected_drawing_spec=c["spec"],
                                      context={"background_image_data_url": ""})
            verdict = res.get("is_correct")
            rows.append({"case": name, "round": round_, "want": c["want"], "got": verdict, "status": res.get("status"),
                         "confidence": res.get("confidence"), "curve_count": (res.get("recognized_features") or {}).get("curve_count"),
                         "ok": verdict is c["want"] or (verdict is None and c["want"] is not None and False)})
            print(rows[-1])
    wrong_pass = [r for r in rows if r["want"] is False and r["got"] is True]
    wrong_fail = [r for r in rows if r["want"] is True and r["got"] is False]
    summary = {"ran": True, "cases": len(rows), "exact": sum(1 for r in rows if r["got"] is r["want"]), "uncertain": sum(1 for r in rows if r["got"] is None),
               "false_accept": [r["case"] for r in wrong_pass], "false_reject": [r["case"] for r in wrong_fail], "rows": rows}
    (HERE / "real_vision_check_result.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print({k: v for k, v in summary.items() if k != "rows"})


if __name__ == "__main__":
    main()
