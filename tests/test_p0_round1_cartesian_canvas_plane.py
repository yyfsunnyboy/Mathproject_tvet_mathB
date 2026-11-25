# -*- coding: utf-8 -*-
"""Drawing canvas must render axes+grid without painting the solution line."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from core.domain.coordinate_geometry.line_equation_domain import (
    build_draw_linear_function_graph_matrix,
)

ROOT = Path(__file__).resolve().parents[1]
VISUAL_SPEC = ROOT / "static" / "js" / "visual_spec.js"


def _node(script: str, *args: str) -> dict:
    cmd = ["node", "-e", script, str(VISUAL_SPEC), *args]
    out = subprocess.check_output(cmd, text=True, cwd=str(ROOT))
    return json.loads(out)


def test_draw_linear_matrix_uses_cartesian_canvas_without_answer_line() -> None:
    matrix = build_draw_linear_function_graph_matrix(seed=7)
    spec = matrix["visual_spec"]
    assert spec["kind"] == "cartesian_canvas"
    assert spec.get("show_grid") is True
    assert "lines" not in spec or not spec.get("lines")
    # Solution stays in expected_drawing_spec only.
    assert matrix["expected_drawing_spec"]["equation"].startswith("y=")


def test_cartesian_canvas_normalizes_to_blank_plane_with_axes() -> None:
    matrix = build_draw_linear_function_graph_matrix(seed=3)
    payload = _node(
        "const runtime=require(process.argv[1]);"
        "const spec=JSON.parse(process.argv[2]);"
        "const normalized=runtime.normalizeVisualSpecForRendering(spec);"
        "process.stdout.write(JSON.stringify({"
        "renderable:runtime.isVisualSpecRenderable(spec),"
        "kind:normalized&&normalized.kind,"
        "blank:normalized&&normalized.blank_drawing_plane,"
        "showGrid:normalized&&normalized.show_grid,"
        "lines:(normalized&&normalized.lines)||[],"
        "points:(normalized&&normalized.points)||[]"
        "}));",
        json.dumps(matrix["visual_spec"]),
    )
    assert payload["renderable"] is True
    assert payload["kind"] == "coordinate_plane"
    assert payload["blank"] is True
    assert payload["showGrid"] is True
    assert payload["lines"] == []
    assert payload["points"] == []
