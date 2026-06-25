from __future__ import annotations

import argparse
import base64
import json
import math
import statistics
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from models import User, db

FIXTURE_DIR = ROOT / "tests" / "fixtures" / "drawing_answers" / "histogram_frequency_polygon"
REPORT_DIR = ROOT / "reports" / "drawing_vision_calibration"
REPORT_PATH = REPORT_DIR / "histogram_frequency_polygon_live_validation.md"
SKILL_ID = "vh_\u6578\u5b78B4_HistogramsAndFrequencyPolygons"
PROBLEM_TYPE_ID = "frequency_distribution_chart_construction"
COMPONENT_ID = "src_3827"

CANVAS_W = 720
CANVAS_H = 480
PLOT_LEFT = 90
PLOT_TOP = 50
PLOT_RIGHT = 650
PLOT_BOTTOM = 400


@dataclass(frozen=True)
class FixtureCase:
    name: str
    expected_label: str
    variant: str


CASES = [
    FixtureCase("01_blank_canvas.png", "blank canvas", "blank"),
    FixtureCase("02_random_line.png", "arbitrary single line", "random_line"),
    FixtureCase("03_histogram_only_correct.png", "histogram only, correct bars", "histogram_only"),
    FixtureCase("04_polygon_only_correct.png", "frequency polygon only, correct points", "polygon_only"),
    FixtureCase("05_both_one_bar_wrong.png", "both drawn, one bar height wrong", "one_bar_wrong"),
    FixtureCase("06_both_polygon_wrong_order.png", "both drawn, polygon order wrong", "polygon_wrong_order"),
    FixtureCase("07_complete_correct_neat.png", "complete correct neat", "correct_neat"),
    FixtureCase("08_complete_correct_wobbly.png", "complete correct wobbly", "correct_wobbly"),
    FixtureCase("09_complete_correct_thick.png", "complete correct thick", "correct_thick"),
    FixtureCase("10_complete_correct_shifted.png", "complete correct shifted", "correct_shifted"),
    FixtureCase("11_all_bar_heights_wrong.png", "all bar heights wrong", "all_bars_wrong"),
    FixtureCase("12_polygon_along_bar_edges.png", "polygon follows bar edges", "polygon_along_edges"),
]

BLANK_DETECTION_CASES = [
    FixtureCase("blank_01_white_png.png", "full white PNG", "blank"),
    FixtureCase("blank_02_axes_only.png", "preloaded axes only", "axes_only"),
    FixtureCase("blank_03_tiny_touch.png", "tiny accidental stroke", "tiny_touch"),
    FixtureCase("blank_04_normal_stroke.png", "normal student stroke", "random_line"),
]


def _get_expected_spec(seed: int) -> dict:
    import importlib

    mod = importlib.import_module(
        "agent_skills_v3.vh_\u6578\u5b78B4_HistogramsAndFrequencyPolygons.components.src_3827.generate"
    )
    payload = mod.generate(seed=seed, component_id=COMPONENT_ID)
    return dict(payload["expected_drawing_spec"])


def _scale_for_values(values: list[float]) -> float:
    max_value = max([1.0, *[float(v) for v in values]])
    return math.ceil(max_value / 5.0) * 5.0


def _x_centers(count: int) -> list[float]:
    width = PLOT_RIGHT - PLOT_LEFT
    step = width / max(count, 1)
    return [PLOT_LEFT + step * (i + 0.5) for i in range(count)]


def _y_for_value(value: float, y_max: float) -> float:
    return PLOT_BOTTOM - (float(value) / y_max) * (PLOT_BOTTOM - PLOT_TOP)


def _base_canvas(with_axes: bool = True) -> Image.Image:
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), "white")
    if not with_axes:
        return img
    draw = ImageDraw.Draw(img)
    grid = (222, 226, 230)
    axis = (170, 176, 184)
    for i in range(6):
        y = PLOT_BOTTOM - i * (PLOT_BOTTOM - PLOT_TOP) / 5
        draw.line((PLOT_LEFT, y, PLOT_RIGHT, y), fill=grid, width=1)
    category_count = 4
    for i in range(category_count + 1):
        x = PLOT_LEFT + i * (PLOT_RIGHT - PLOT_LEFT) / category_count
        draw.line((x, PLOT_TOP, x, PLOT_BOTTOM), fill=grid, width=1)
    draw.line((PLOT_LEFT, PLOT_BOTTOM, PLOT_RIGHT, PLOT_BOTTOM), fill=axis, width=2)
    draw.line((PLOT_LEFT, PLOT_TOP, PLOT_LEFT, PLOT_BOTTOM), fill=axis, width=2)
    return img


def _draw_histogram(draw: ImageDraw.ImageDraw, values: list[float], y_max: float, *, wrong: str = "", shift: int = 0, width: int = 3) -> None:
    centers = _x_centers(len(values))
    step = (PLOT_RIGHT - PLOT_LEFT) / max(len(values), 1)
    bar_w = step * 0.72
    draw_values = list(values)
    if wrong == "one":
        draw_values[1] = max(0.5, draw_values[1] + max(2.0, y_max * 0.25))
    elif wrong == "all":
        draw_values = [max(0.5, y_max - float(v)) for v in values]
    for x, value in zip(centers, draw_values):
        left = x - bar_w / 2 + shift
        right = x + bar_w / 2 + shift
        top = _y_for_value(value, y_max)
        draw.rectangle((left, top, right, PLOT_BOTTOM), outline=(20, 20, 20), width=width)


def _draw_polygon(
    draw: ImageDraw.ImageDraw,
    values: list[float],
    y_max: float,
    *,
    wrong_order: bool = False,
    along_edges: bool = False,
    shift: int = 0,
    width: int = 4,
    wobble: bool = False,
) -> None:
    centers = _x_centers(len(values))
    if along_edges:
        step = (PLOT_RIGHT - PLOT_LEFT) / max(len(values), 1)
        centers = [x + step * 0.36 for x in centers]
    points = []
    for idx, (x, value) in enumerate(zip(centers, values)):
        dx = ((-1) ** idx) * 6 if wobble else 0
        dy = (idx % 2) * 4 if wobble else 0
        points.append((x + shift + dx, _y_for_value(value, y_max) + dy))
    if wrong_order and len(points) >= 4:
        points = [points[0], points[2], points[1], points[3]]
    draw.line(points, fill=(20, 20, 20), width=width, joint="curve")
    radius = max(4, width)
    for x, y in points:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(20, 20, 20))


def generate_fixture_image(spec: dict, variant: str) -> Image.Image:
    values = [float(v) for v in spec["expected_values"]]
    y_max = _scale_for_values(values)
    if variant == "blank":
        return _base_canvas(with_axes=False)
    img = _base_canvas(with_axes=True)
    draw = ImageDraw.Draw(img)
    if variant == "axes_only":
        return img
    if variant == "tiny_touch":
        draw.line((PLOT_LEFT + 20, PLOT_BOTTOM - 20, PLOT_LEFT + 23, PLOT_BOTTOM - 22), fill=(20, 20, 20), width=2)
        return img
    if variant == "random_line":
        draw.line((PLOT_LEFT + 30, PLOT_BOTTOM - 30, PLOT_RIGHT - 40, PLOT_TOP + 80), fill=(20, 20, 20), width=4)
        return img
    if variant in {"histogram_only", "one_bar_wrong", "all_bars_wrong", "correct_neat", "correct_wobbly", "correct_thick", "correct_shifted", "polygon_wrong_order", "polygon_along_edges"}:
        wrong = "one" if variant == "one_bar_wrong" else "all" if variant == "all_bars_wrong" else ""
        shift = 12 if variant == "correct_shifted" else 0
        width = 6 if variant == "correct_thick" else 3
        _draw_histogram(draw, values, y_max, wrong=wrong, shift=shift, width=width)
    if variant in {"polygon_only", "one_bar_wrong", "correct_neat", "correct_wobbly", "correct_thick", "correct_shifted", "polygon_wrong_order", "polygon_along_edges", "all_bars_wrong"}:
        shift = 12 if variant == "correct_shifted" else 0
        width = 9 if variant == "correct_thick" else 4
        _draw_polygon(
            draw,
            values,
            y_max,
            wrong_order=variant == "polygon_wrong_order",
            along_edges=variant == "polygon_along_edges",
            shift=shift,
            width=width,
            wobble=variant == "correct_wobbly",
        )
    return img


def generate_fixtures(seed: int) -> dict:
    spec = _get_expected_spec(seed)
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    for case in [*CASES, *BLANK_DETECTION_CASES]:
        generate_fixture_image(spec, case.variant).save(FIXTURE_DIR / case.name)
    (FIXTURE_DIR / "expected_spec_seed.json").write_text(
        json.dumps({"seed": seed, "expected_drawing_spec": spec}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return spec


def _image_data_url(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(username=f"drawing_live_{uuid.uuid4().hex[:10]}", password_hash="test-hash", role="student")
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client


def _get_src_3827_question(client, seed: int) -> dict:
    question = {}
    for offset in range(0, 20):
        candidate_seed = seed + offset
        response = client.get(
            f"/get_next_question?skill={quote(SKILL_ID)}&problem_type={PROBLEM_TYPE_ID}&gen_seed={candidate_seed}&level=1"
        )
        question = response.get_json() or {}
        if question.get("component_id") == COMPONENT_ID:
            return question
    return question


def _raw_stats(raw_text: str, drawing_type: str) -> dict:
    from core.services import drawing_answer_analysis_service as svc

    text = raw_text or ""
    fenced = "```" in text
    first = text.find("{")
    last = text.rfind("}")
    extra = bool(text[:first].strip() or text[last + 1 :].strip()) if first >= 0 and last > first else bool(text.strip())
    parsed = svc.parse_analyzer_json(text)
    schema_valid = False
    confidence = None
    recognized_type = ""
    recognized_features = {}
    if parsed is not None:
        ok, normalized = svc.validate_analyzer_response(parsed, drawing_type=drawing_type)
        schema_valid = ok
        if ok and isinstance(normalized, dict):
            confidence = normalized.get("confidence")
            recognized_type = str(normalized.get("recognized_type") or "")
            recognized_features = normalized
    return {
        "response_length": len(text),
        "json_parse_success": parsed is not None,
        "fenced_json": fenced,
        "extra_text": extra,
        "schema_valid": schema_valid,
        "confidence": confidence,
        "recognized_type": recognized_type,
        "recognized_features": recognized_features,
    }


def run_live_validation(seed: int, repeat_target: str, repeat_count: int) -> dict:
    from core.services import drawing_answer_analysis_service as svc

    client = _logged_client()
    question = _get_src_3827_question(client, seed)
    spec = question.get("answer_contract", {}).get("expected_drawing_spec") or question.get("expected_drawing_spec") or {}
    drawing_type = str(spec.get("drawing_type") or "")
    analyzer_role = svc._resolve_analyzer_role()

    original_call = svc._call_vision_analyzer
    raw_capture: list[dict] = []
    api_call_count = 0

    def wrapped_call(prompt, image_bytes, analyzer_status):
        nonlocal api_call_count
        api_call_count += 1
        started = time.perf_counter()
        try:
            raw = original_call(prompt, image_bytes, analyzer_status)
            raw_capture.append({"latency_ms": round((time.perf_counter() - started) * 1000, 1), "raw": raw, "error": ""})
            return raw
        except Exception as exc:
            raw_capture.append({"latency_ms": round((time.perf_counter() - started) * 1000, 1), "raw": "", "error": type(exc).__name__})
            raise

    svc._call_vision_analyzer = wrapped_call
    try:
        run_plan = list(CASES)
        target_case = next((c for c in CASES if c.name == repeat_target), CASES[6])
        for idx in range(max(0, repeat_count - 1)):
            run_plan.append(FixtureCase(f"{target_case.name}#repeat{idx + 2}", target_case.expected_label, target_case.variant))

        rows = []
        check_answer_calls = 0
        for case in run_plan:
            fixture_name = case.name.split("#", 1)[0]
            raw_capture.clear()
            started = time.perf_counter()
            result = client.post(
                "/check_answer",
                json={
                    "skill_id": question["skill_id"],
                    "question_uid": question["question_uid"],
                    "problem_type_id": question["problem_type_id"],
                    "answer": "[drawing]",
                    "image_data_url": _image_data_url(FIXTURE_DIR / fixture_name),
                },
            ).get_json() or {}
            check_answer_calls += 1
            total_latency = round((time.perf_counter() - started) * 1000, 1)
            raw_info = raw_capture[-1] if raw_capture else {"latency_ms": 0.0, "raw": "", "error": ""}
            stats = _raw_stats(raw_info.get("raw", ""), drawing_type) if raw_info.get("raw") else {
                "response_length": 0,
                "json_parse_success": False,
                "fenced_json": False,
                "extra_text": False,
                "schema_valid": False,
                "confidence": None,
                "recognized_type": "",
                "recognized_features": {},
            }
            rows.append(
                {
                    "fixture": case.name,
                    "expected_label": case.expected_label,
                    "status": result.get("status"),
                    "final_is_correct": result.get("is_correct", result.get("correct")),
                    "score": result.get("score"),
                    "confidence": result.get("confidence"),
                    "feedback": result.get("message") or result.get("feedback") or "",
                    "vision_claimed_is_correct": stats["recognized_features"].get("is_correct") if stats["recognized_features"] else None,
                    "vision_extracted_features": stats["recognized_features"],
                    "latency_ms": raw_info.get("latency_ms") or total_latency,
                    "total_latency_ms": total_latency,
                    "raw_error": raw_info.get("error", ""),
                    **stats,
                }
            )
    finally:
        svc._call_vision_analyzer = original_call

    return {
        "question": question,
        "expected_drawing_spec": spec,
        "analyzer_role": analyzer_role,
        "api_call_count": api_call_count,
        "check_answer_calls": check_answer_calls,
        "rows": rows,
    }


def _pct(num: int, denom: int) -> str:
    return "n/a" if denom == 0 else f"{num / denom * 100:.1f}%"


def write_report(result: dict | None, seed: int, fixture_spec: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Histogram/Frequency Polygon Live Vision Validation")
    lines.append("")
    lines.append(f"- seed: `{seed}`")
    lines.append(f"- fixture_dir: `{FIXTURE_DIR}`")
    lines.append(f"- report_generated_at_epoch: `{int(time.time())}`")
    lines.append("")
    lines.append("## Fixture Spec")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(fixture_spec, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")

    if result is None:
        lines.append("## Live Validation")
        lines.append("")
        lines.append("Live validation was not run.")
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
        return

    rows = result["rows"]
    latencies = [float(r.get("latency_ms") or 0.0) for r in rows if r.get("latency_ms")]
    response_sizes = [int(r.get("response_length") or 0) for r in rows]
    total = len(rows)
    parse_ok = sum(1 for r in rows if r.get("json_parse_success"))
    schema_ok = sum(1 for r in rows if r.get("schema_valid"))
    fenced = sum(1 for r in rows if r.get("fenced_json"))
    extra = sum(1 for r in rows if r.get("extra_text"))
    provider_errors = sum(1 for r in rows if r.get("raw_error"))
    timeouts = sum(1 for r in rows if r.get("raw_error") == "TimeoutError")

    lines.append("## Provider")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(result["analyzer_role"], ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- total_test_calls: `{total}`")
    lines.append(f"- check_answer_calls: `{result['check_answer_calls']}`")
    lines.append(f"- vision_api_calls: `{result['api_call_count']}`")
    lines.append(f"- json_success: `{parse_ok}/{total}` ({_pct(parse_ok, total)})")
    lines.append(f"- schema_valid: `{schema_ok}/{total}` ({_pct(schema_ok, total)})")
    lines.append(f"- fenced_json: `{fenced}`")
    lines.append(f"- extra_text: `{extra}`")
    lines.append(f"- timeout: `{timeouts}`")
    lines.append(f"- provider_error: `{provider_errors}`")
    if latencies:
        p50 = statistics.median(latencies)
        p95 = sorted(latencies)[max(0, math.ceil(len(latencies) * 0.95) - 1)]
        lines.append(f"- latency_avg_ms: `{statistics.mean(latencies):.1f}`")
        lines.append(f"- latency_p50_ms: `{p50:.1f}`")
        lines.append(f"- latency_p95_ms: `{p95:.1f}`")
        lines.append(f"- latency_max_ms: `{max(latencies):.1f}`")
    if response_sizes:
        lines.append(f"- response_size_avg_chars: `{statistics.mean(response_sizes):.1f}`")
    lines.append("- token_usage: `not exposed by current client response`")
    lines.append("- provider_retries: `max_retries=1 configured; retry count not exposed by wrapper`")
    lines.append("")

    lines.append("## Per Fixture")
    lines.append("")
    lines.append("| fixture | expected_label | status | final_is_correct | score | confidence | json | schema | latency_ms | feedback |")
    lines.append("|---|---|---|---:|---:|---:|---|---|---:|---|")
    for row in rows:
        feedback = str(row.get("feedback") or "").replace("|", "/").replace("\n", " ")[:140]
        lines.append(
            f"| {row['fixture']} | {row['expected_label']} | {row.get('status')} | {row.get('final_is_correct')} | "
            f"{row.get('score')} | {row.get('confidence')} | {row.get('json_parse_success')} | "
            f"{row.get('schema_valid')} | {row.get('latency_ms')} | {feedback} |"
        )
    lines.append("")

    lines.append("## Extracted Features")
    for row in rows:
        lines.append("")
        lines.append(f"### {row['fixture']}")
        lines.append("")
        lines.append(f"- vision_claimed_is_correct: `{row.get('vision_claimed_is_correct')}`")
        lines.append(f"- raw_error: `{row.get('raw_error')}`")
        lines.append("```json")
        lines.append(json.dumps(row.get("vision_extracted_features") or {}, ensure_ascii=False, indent=2))
        lines.append("```")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--generate-fixtures", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--repeat-target", default="07_complete_correct_neat.png")
    parser.add_argument("--repeat-count", type=int, default=3)
    args = parser.parse_args()

    spec = generate_fixtures(args.seed) if args.generate_fixtures else _get_expected_spec(args.seed)
    result = run_live_validation(args.seed, args.repeat_target, args.repeat_count) if args.run_live else None
    write_report(result, args.seed, spec)
    print(f"fixtures: {FIXTURE_DIR}")
    print(f"report: {REPORT_PATH}")
    if result is not None:
        print(f"check_answer_calls: {result['check_answer_calls']}")
        print(f"vision_api_calls: {result['api_call_count']}")


if __name__ == "__main__":
    main()
