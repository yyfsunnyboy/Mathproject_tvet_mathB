from __future__ import annotations

import json
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "static" / "js" / "triangle_diagram.js"
TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "index.html"


def test_triangle_svg_uses_spec_labels_and_does_not_show_answer():
    spec = {
        "version": 1,
        "type": "triangle",
        "vertices": ["A", "B", "C"],
        "parameters": {"angles_deg": {"A": 45, "C": 120}, "sides": {"a": "4"}},
        "side_vertices": {"a": ["B", "C"], "b": ["C", "A"], "c": ["A", "B"]},
        "show": {"angles": ["A", "C"], "sides": ["a"], "unknown_sides": ["c"]},
    }
    code = "const r=require(process.argv[1]);process.stdout.write(r.createSvgMarkup(JSON.parse(process.argv[2])));"
    result = subprocess.run(
        ["node", "-e", code, str(SCRIPT), json.dumps(spec)],
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    svg = result.stdout
    assert "<svg" in svg
    assert "45°" in svg and "120°" in svg
    assert "a = 4" in svg
    assert "c = ?" in svg
    assert "2√6" not in svg and "sqrt(6)" not in svg


def test_practice_template_prioritizes_triangle_diagram_before_image_fallback():
    template = TEMPLATE.read_text(encoding="utf-8")
    assert "js/triangle_diagram.js" in template
    diagram_branch = template.index("else if (renderQuestionDiagramSpec(data))")
    image_fallback = template.index("applyQuestionScratchpadBackground(data)", diagram_branch)
    assert diagram_branch < image_fallback


def test_triangle_uses_scratchpad_background_once_and_keeps_canvas_contract():
    template = TEMPLATE.read_text(encoding="utf-8")
    branch = template.split("function renderQuestionDiagramSpec(payload) {", 1)[1].split("function collectTableAnswers", 1)[0]
    assert "setReferenceDiagramBackground(image, backgroundCtx" in branch
    assert "runtime.render(qmc" not in branch
    assert template.count('id="drawing-background-canvas"') == 1
    assert template.count('id="handwriting-canvas"') == 1
    assert 'id="analyze-handwriting-button"' in template
    assert "cctx.drawImage(backgroundCanvas" in template


def test_question_change_clears_old_reference_before_rendering_new_diagram():
    template = TEMPLATE.read_text(encoding="utf-8")
    load_branch = template.split("function loadQuestion() {", 1)[1].split("function isChoiceQuestionPayload", 1)[0]
    assert load_branch.index("resetScratchpadForNextQuestion();") < load_branch.index("renderQuestionDiagramSpec(data)")
    diagram_branch = load_branch.split("} else if (renderQuestionDiagramSpec(data)) {", 1)[1].split("} else {", 1)[0]
    assert "resetQuestionBackground" not in diagram_branch


def test_triangle_svg_has_viewbox_without_large_fixed_dimensions():
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'viewBox="0 0 380 235"' in source
    assert 'width="900"' not in source
    assert 'height="600"' not in source
    layers = (SCRIPT.parent / "scratchpad_layers.js").read_text(encoding="utf-8")
    assert "Math.min(240, cssWidth * 0.45)" in layers
    assert "Math.min(300, cssWidth * 0.32)" in layers
    assert "Math.min(220," in layers
