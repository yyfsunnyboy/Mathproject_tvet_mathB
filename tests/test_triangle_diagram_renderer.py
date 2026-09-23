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
