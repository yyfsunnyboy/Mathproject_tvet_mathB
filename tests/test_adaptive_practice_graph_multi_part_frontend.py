from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


TEMPLATE = Path("templates/adaptive_practice_v2.html")
VISUAL_RUNTIME = Path("static/js/visual_spec.js")


def _function_body(source: str, name: str) -> str:
    marker = f"function {name}"
    start = source.index(marker)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[brace : index + 1]
    raise AssertionError(f"function body not found: {name}")


def test_graph_multi_part_uses_visual_spec_renderer() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    body = _function_body(source, "renderReadonlyVisualSpec")
    assert "VisualSpecRuntime" in source
    assert "requiresVisualRendering(visualSpec)" in body
    assert "renderToCanvas(questionVisualCanvas, visualSpec)" in body
    assert "image_base64" not in body
    assert "renderToCanvas" in VISUAL_RUNTIME.read_text(encoding="utf-8")


def test_visual_spec_only_renders_to_readonly_canvas() -> None:
    node = shutil.which("node")
    if not node:
        candidates = sorted(
            (Path.home() / ".cache" / "codex-runtimes").glob(
                "*/dependencies/node/bin/node.exe"
            )
        )
        node = str(candidates[0]) if candidates else None
    assert node, "Node.js runtime is required"
    visual_spec = {
        "kind": "coordinate_line_graph",
        "drawable_primitives": [
            {"type": "line", "equation": {"A": "-4", "B": "3", "C": "12"}},
            {"type": "axes"},
        ],
        "axis_range": {"x_min": -2, "x_max": 5, "y_min": -6, "y_max": 2},
        "points": [["3", "0"], ["0", "-4"]],
    }
    script = """
const runtime = require(process.argv[1]);
const noop = () => {};
const ctx = {
  setTransform: noop, clearRect: noop, fillRect: noop, beginPath: noop,
  moveTo: noop, lineTo: noop, stroke: noop, arc: noop, fill: noop
};
const canvas = {clientWidth: 640, clientHeight: 360, getContext: () => ctx};
process.stdout.write(String(runtime.renderToCanvas(canvas, JSON.parse(process.argv[2]))));
"""
    result = subprocess.run(
        [
            node,
            "-e",
            script,
            str(VISUAL_RUNTIME.resolve()),
            json.dumps(visual_spec),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout == "true"


def test_multi_part_fields_follow_answer_contract_parts() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    render_body = _function_body(source, "renderAnswerFields")
    collect_body = _function_body(source, "collectCurrentAnswer")
    assert "resolveMultiPartFields(question)" in render_body
    assert "input.dataset.fieldKey = String(part.key)" in render_body
    assert "input.dataset.answerOrder" in render_body
    assert "answer[input.dataset.fieldKey]" in collect_body
    assert "user_answer: answer" in source


def test_non_drawing_never_requests_canvas() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    body = _function_body(source, "resolveDrawingUiContract")
    assert "canvasRequired: drawing ? (ui.canvas_required !== false) : false" in body


def test_drawing_dispatch_remains_unchanged() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    assert 'submitDrawingAnswer("ai_check")' in source
    assert 'fetch("/check_answer"' in source
    assert "student_strokes_image_data_url" in source
