# -*- coding: utf-8 -*-
"""Coordinate-plane numeric ticks / origin O for LinearFunction & Slope graphs."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from core.domain.coordinate_geometry.line_equation_domain import (
    build_draw_constant_function_graph_matrix,
    build_draw_linear_function_graph_matrix,
    build_graph_intercepts_and_linear_equation_matrix,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

ROOT = Path(__file__).resolve().parents[1]
VISUAL_SPEC = ROOT / "static" / "js" / "visual_spec.js"


def _node(script: str, *args: str) -> dict:
    cmd = ["node", "-e", script, str(VISUAL_SPEC), *args]
    out = subprocess.check_output(cmd, text=True, cwd=str(ROOT))
    return json.loads(out)


def _capture_fill_texts(visual_spec: dict) -> dict:
    return _node(
        "const runtime=require(process.argv[1]);"
        "const spec=JSON.parse(process.argv[2]);"
        "const texts=[];"
        "const ctx={"
        "canvas:{width:480,height:360},"
        "save(){},restore(){},beginPath(){},moveTo(){},lineTo(){},stroke(){},"
        "arc(){},fill(){},rect(){},clip(){},setLineDash(){},"
        "clearRect(){},fillRect(){},setTransform(){},"
        "measureText(t){return {width:String(t).length*6};},"
        "fillText(t){texts.push(String(t));}"
        "};"
        "const ok=runtime.renderToContext(ctx,spec,480,360,"
        "{padding:20,visualOpacity:0.85,backgroundFill:'#ffffff'});"
        "const meta=runtime.getLastRenderMeta()||{};"
        "process.stdout.write(JSON.stringify({"
        "ok:!!ok,texts:texts,meta:meta,"
        "step:runtime.chooseNiceTickStep(12,30,28)"
        "}));",
        json.dumps(visual_spec),
    )


def test_choose_nice_tick_step_scales_with_density() -> None:
    payload = _node(
        "const runtime=require(process.argv[1]);"
        "process.stdout.write(JSON.stringify({"
        "dense:runtime.chooseNiceTickStep(12,40,28),"
        "sparse:runtime.chooseNiceTickStep(40,8,28),"
        "tiny:runtime.chooseNiceTickStep(4,80,28)"
        "}));"
    )
    assert payload["dense"] in (1, 2)
    assert payload["sparse"] >= 2
    assert payload["tiny"] <= 1


def test_draw_linear_canvas_has_numeric_ticks_and_origin() -> None:
    matrix = build_draw_linear_function_graph_matrix(seed=7)
    captured = _capture_fill_texts(matrix["visual_spec"])
    assert captured["ok"] is True
    texts = captured["texts"]
    assert "O" in texts
    assert "x" in texts
    assert "y" in texts
    numeric = [t for t in texts if t.lstrip("-").isdigit()]
    assert len(numeric) >= 4
    assert captured["meta"].get("axisTickLabelCount", 0) >= 4


def test_draw_constant_canvas_has_ticks() -> None:
    matrix = build_draw_constant_function_graph_matrix(seed=3)
    captured = _capture_fill_texts(matrix["visual_spec"])
    assert captured["ok"] is True
    assert "O" in captured["texts"]


def test_slope_or_intercept_graph_keeps_ticks_with_line() -> None:
    matrix = build_graph_intercepts_and_linear_equation_matrix(seed=11)
    # Runtime adapter may wrap visual_spec; use matrix visual directly.
    captured = _capture_fill_texts(matrix["visual_spec"])
    assert captured["ok"] is True
    assert "O" in captured["texts"]
    assert any(t.lstrip("-").isdigit() for t in captured["texts"])


def test_linearfunction_runtime_payload_blank_plane_ticks() -> None:
    matrix = build_draw_linear_function_graph_matrix(seed=5)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        domain_operation="draw_linear_function_graph",
        component_id="src_4449",
        textbook_example_id=4449,
    )
    captured = _capture_fill_texts(payload["visual_spec"])
    assert captured["ok"] is True
    assert "O" in captured["texts"]
    # Answer line must not be painted on the blank drawing plane.
    assert payload["visual_spec"].get("blank_drawing_plane") is True or payload["visual_spec"]["kind"] == "cartesian_canvas"
