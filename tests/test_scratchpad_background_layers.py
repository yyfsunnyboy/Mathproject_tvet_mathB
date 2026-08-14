from __future__ import annotations

import importlib
import json
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VISUAL_SPEC_PATH = PROJECT_ROOT / "static" / "js" / "visual_spec.js"
SCRATCHPAD_LAYERS_PATH = PROJECT_ROOT / "static" / "js" / "scratchpad_layers.js"
INDEX_TEMPLATE_PATH = PROJECT_ROOT / "templates" / "index.html"
ADAPTIVE_TEMPLATE_PATH = PROJECT_ROOT / "templates" / "adaptive_practice_v2.html"


def _node_executable() -> str:
    node_executable = shutil.which("node")
    if node_executable:
        return node_executable
    candidates = sorted(
        (Path.home() / ".cache" / "codex-runtimes").glob("*/dependencies/node/bin/node.exe")
    )
    assert candidates, "Node.js runtime is required for scratchpad layer tests"
    return str(candidates[0])


def _run_node(script: str, *args: str) -> str:
    import os
    import tempfile

    argv = [_node_executable(), "-e", script]
    temp_files: list[str] = []
    for arg in args:
        if len(arg) > 7000:
            handle, path = tempfile.mkstemp(suffix=".json", text=True)
            os.close(handle)
            Path(path).write_text(arg, encoding="utf-8")
            temp_files.append(path)
            argv.append(path)
        else:
            argv.append(arg)
    try:
        completed = subprocess.run(
            argv,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    finally:
        for path in temp_files:
            Path(path).unlink(missing_ok=True)
    return (completed.stdout or "").strip()


def test_compute_question_background_region_uses_top_left_quarter() -> None:
    script = (
        "const layers=require(process.argv[1]);"
        "const region=layers.computeQuestionBackgroundRegion(800,600);"
        "process.stdout.write(JSON.stringify(region));"
    )
    region = json.loads(_run_node(script, str(SCRATCHPAD_LAYERS_PATH)))
    assert region["x"] == region["edgePadding"]
    assert region["y"] == region["edgePadding"]
    assert abs(region["quadrantWidth"] - 400) < 0.01
    assert abs(region["quadrantHeight"] - 300) < 0.01
    assert region["width"] <= region["quadrantWidth"]
    assert region["height"] <= region["quadrantHeight"]


def test_visual_spec_equal_unit_scale_keeps_square_grid_cells() -> None:
    script = (
        "const runtime=require(process.argv[1]);"
        "const mapper=runtime.buildEqualScalePlotMapper({x:0,y:0,width:200,height:200,showLabel:false},-5,5,-5,5,{padding:10});"
        "const dx=Math.abs(mapper.mapX(1)-mapper.mapX(0));"
        "const dy=Math.abs(mapper.mapY(1)-mapper.mapY(0));"
        "process.stdout.write(JSON.stringify({dx,dy,unitScale:mapper.unitScale,unitScaleX:mapper.unitScaleX,unitScaleY:mapper.unitScaleY,scaleMode:mapper.scaleMode}));"
    )
    payload = json.loads(_run_node(script, str(VISUAL_SPEC_PATH)))
    assert abs(payload["dx"] - payload["dy"]) < 0.01
    assert payload["unitScale"] > 0
    assert payload["unitScaleX"] == payload["unitScaleY"]
    assert payload["scaleMode"] == "cartesian_equal_units"


def test_visual_spec_independent_axes_allows_different_unit_scales() -> None:
    script = (
        "const runtime=require(process.argv[1]);"
        "const mapper=runtime.buildIndependentAxesPlotMapper({x:0,y:0,width:240,height:160,showLabel:false},0,100,0,50,{padding:10});"
        "const dx=Math.abs(mapper.mapX(10)-mapper.mapX(0));"
        "const dy=Math.abs(mapper.mapY(10)-mapper.mapY(0));"
        "process.stdout.write(JSON.stringify({dx,dy,unitScaleX:mapper.unitScaleX,unitScaleY:mapper.unitScaleY,scaleMode:mapper.scaleMode}));"
    )
    payload = json.loads(_run_node(script, str(VISUAL_SPEC_PATH)))
    assert payload["scaleMode"] == "chart_independent_axes"
    assert abs(payload["unitScaleX"] - payload["unitScaleY"]) > 0.01


def _resolve_scale_mode_for_component(skill_id: str, component_id: str) -> dict:
    if component_id == "src_4520":
        from tests.domain.test_slope_of_a_line_domain import _build
        from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

        matrix = _build("classify_and_compare_figure_slopes", seed=4)
        payload = convert_line_equation_matrix_to_question_payload(
            matrix,
            presentation_mode="short_answer",
            domain_operation="classify_and_compare_figure_slopes",
            answer_type="multi_part",
        )
    else:
        mod = importlib.import_module(
            f"agent_skills_v3.{skill_id}.components.{component_id}.generate"
        )
        from core.gencode.domain_matrix_adapter import _apply_line_equation_practice_surface

        payload = mod.generate(seed=1, component_id=component_id)
        if skill_id.startswith("vh_數學B1_PropertiesOf") or skill_id.startswith("vh_數學B1_SlopeOf"):
            payload = _apply_line_equation_practice_surface(payload)
    visual_spec = payload["visual_spec"]
    script = (
        "const runtime=require(process.argv[1]);"
        "const spec=JSON.parse(process.argv[2]);"
        "const normalized=runtime.normalizeVisualSpecForRendering(spec);"
        "process.stdout.write(JSON.stringify({"
        "scaleMode:runtime.resolveScaleMode(spec),"
        "normalizedScaleMode:normalized && normalized.scale_mode,"
        "kind:runtime.getVisualKind(spec)"
        "}));"
    )
    return json.loads(_run_node(script, str(VISUAL_SPEC_PATH), json.dumps(visual_spec)))


def test_4536_4424_4520_use_cartesian_equal_units_scale_mode() -> None:
    cases = [
        ("vh_數學B1_PropertiesOfPerpendicularLines", "src_4536"),
        ("vh_數學B1_LinearFunction", "src_4424"),
        ("vh_數學B1_SlopeOfALine", "src_4520"),
    ]
    for skill_id, component_id in cases:
        result = _resolve_scale_mode_for_component(skill_id, component_id)
        assert result["scaleMode"] == "cartesian_equal_units", component_id


def test_3884_uses_chart_independent_axes_scale_mode() -> None:
    result = _resolve_scale_mode_for_component(
        "vh_數學B4_StatisticalChartReading", "src_3884"
    )
    assert result["scaleMode"] == "chart_independent_axes"
    assert result["normalizedScaleMode"] == "chart_independent_axes"


def test_4445_tiered_linear_with_mixed_axis_labels_uses_independent_axes() -> None:
    result = _resolve_scale_mode_for_component("vh_數學B1_LinearFunction", "src_4445")
    assert result["scaleMode"] == "chart_independent_axes"
    assert result["normalizedScaleMode"] == "chart_independent_axes"


def test_render_meta_reports_equal_units_for_cartesian_and_not_for_chart() -> None:
    script = (
        "const runtime=require(process.argv[1]);"
        "const cartesian={kind:'coordinate_plane',render_required:true,"
        "points:[{x:1,y:2}],lines:[{through_points:[[0,0],[2,2]]}],x_range:[-5,5],y_range:[-5,5]};"
        "const chart={kind:'cumulative_frequency_chart',render_required:true,scale_mode:'chart_independent_axes',"
        "data_points:[{x:10,y:2},{x:20,y:5},{x:30,y:8}]};"
        "const ctx={fillRect(){},clearRect(){},setTransform(){},beginPath(){},moveTo(){},"
        "lineTo(){},stroke(){},arc(){},fill(){},canvas:{width:320,height:220}};"
        "runtime.renderToContext(ctx,cartesian,320,220,{padding:20,visualOpacity:0.62,backgroundFill:'#ffffff'});"
        "const cartMeta=runtime.getLastRenderMeta();"
        "runtime.renderToContext(ctx,chart,320,220,{padding:20,visualOpacity:0.62,backgroundFill:'#ffffff'});"
        "const chartMeta=runtime.getLastRenderMeta();"
        "process.stdout.write(JSON.stringify({cartMeta,chartMeta}));"
    )
    payload = json.loads(_run_node(script, str(VISUAL_SPEC_PATH)))
    assert payload["cartMeta"]["scaleMode"] == "cartesian_equal_units"
    assert payload["cartMeta"]["equalUnits"] is True
    assert payload["cartMeta"]["unitScaleX"] == payload["cartMeta"]["unitScaleY"]
    assert payload["chartMeta"]["scaleMode"] == "chart_independent_axes"
    assert payload["chartMeta"]["equalUnits"] is False
    assert payload["chartMeta"]["unitScaleX"] != payload["chartMeta"]["unitScaleY"]


def test_visual_spec_compute_contain_rect_centers_within_region() -> None:
    script = (
        "const layers=require(process.argv[1]);"
        "const rect=layers.computeContainRect(800,400,300,200,14,14,14);"
        "process.stdout.write(JSON.stringify(rect));"
    )
    rect = json.loads(_run_node(script, str(SCRATCHPAD_LAYERS_PATH)))
    assert rect["x"] >= 14
    assert rect["y"] >= 14
    assert rect["width"] <= 300
    assert rect["height"] <= 200


def test_visual_spec_renders_faded_coordinate_plane_to_fixed_canvas() -> None:
    script_dom = (
        "const runtime=require(process.argv[1]);"
        "const ok=runtime.renderToContext("
        "{fillRect(){},clearRect(){},setTransform(){},beginPath(){},moveTo(){},"
        "lineTo(){},stroke(){},arc(){},fill(){},canvas:{width:320,height:220}},"
        "{kind:'coordinate_plane',render_required:true,points:[{x:1,y:2}],"
        "lines:[{through_points:[[0,0],[2,2]]}],x_range:[-5,5],y_range:[-5,5]},"
        "320,220,{padding:20,visualOpacity:0.62,backgroundFill:'#ffffff'});"
        "process.stdout.write(JSON.stringify({ok}));"
    )
    payload = json.loads(_run_node(script_dom, str(VISUAL_SPEC_PATH)))
    assert payload["ok"] is True


def test_4526_text_slope_spec_is_not_renderable() -> None:
    mod = importlib.import_module(
        "agent_skills_v3.vh_數學B1_PropertiesOfPerpendicularLines.components.src_4526.generate"
    )
    from core.gencode.domain_matrix_adapter import _apply_line_equation_practice_surface

    payload = _apply_line_equation_practice_surface(
        mod.generate(seed=1, component_id="src_4526")
    )
    visual_spec = payload["visual_spec"]
    script = (
        "const runtime=require(process.argv[1]);"
        "const spec=JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify({"
        "renderable:runtime.isVisualSpecRenderable(spec),"
        "legacy:runtime.requiresVisualRendering(spec)"
        "}));"
    )
    result = json.loads(_run_node(script, str(VISUAL_SPEC_PATH), json.dumps(visual_spec)))
    assert result["renderable"] is False
    assert result["legacy"] is False


def test_4536_coordinate_spec_is_renderable() -> None:
    mod = importlib.import_module(
        "agent_skills_v3.vh_數學B1_PropertiesOfPerpendicularLines.components.src_4536.generate"
    )
    from core.gencode.domain_matrix_adapter import _apply_line_equation_practice_surface

    payload = _apply_line_equation_practice_surface(
        mod.generate(seed=1, component_id="src_4536")
    )
    visual_spec = payload["visual_spec"]
    script = (
        "const runtime=require(process.argv[1]);"
        "const spec=JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify(runtime.isVisualSpecRenderable(spec)));"
    )
    assert json.loads(_run_node(script, str(VISUAL_SPEC_PATH), json.dumps(visual_spec))) is True


def test_4520_multi_figure_builds_six_panels_and_desktop_grid() -> None:
    from tests.domain.test_slope_of_a_line_domain import _build
    from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

    matrix = _build("classify_and_compare_figure_slopes", seed=4)
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        domain_operation="classify_and_compare_figure_slopes",
        answer_type="multi_part",
    )
    visual_spec = payload["visual_spec"]
    assert visual_spec["kind"] == "coordinate_plane_multi_figure"
    script = (
        "const runtime=require(process.argv[1]);"
        "const spec=JSON.parse(process.argv[2]);"
        "const panels=runtime.buildMultiFigurePanels(spec);"
        "const grid=runtime.computeMultiFigureGrid(panels.length,960,540,16);"
        "process.stdout.write(JSON.stringify({"
        "renderable:runtime.isVisualSpecRenderable(spec),"
        "panelCount:panels.length,"
        "cols:grid.cols,rows:grid.rows,cellCount:grid.cells.length"
        "}));"
    )
    result = json.loads(_run_node(script, str(VISUAL_SPEC_PATH), json.dumps(visual_spec)))
    assert result["renderable"] is True
    assert result["panelCount"] == 6
    assert result["cols"] == 3
    assert result["rows"] == 2
    assert result["cellCount"] == 6


def test_4520_mobile_grid_uses_two_columns() -> None:
    from tests.domain.test_slope_of_a_line_domain import _build
    from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

    matrix = _build("classify_and_compare_figure_slopes", seed=4)
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        domain_operation="classify_and_compare_figure_slopes",
        answer_type="multi_part",
    )
    script = (
        "const runtime=require(process.argv[1]);"
        "const layers=require(process.argv[2]);"
        "const region=layers.computeQuestionBackgroundRegion(390,844);"
        "const grid=runtime.computeMultiFigureGrid(6,region.width,region.height,region.edgePadding);"
        "process.stdout.write(JSON.stringify({cols:grid.cols,rows:grid.rows,region}));"
    )
    result = json.loads(_run_node(script, str(VISUAL_SPEC_PATH), str(SCRATCHPAD_LAYERS_PATH)))
    assert result["cols"] == 2
    assert result["rows"] == 3


def test_scratchpad_layer_clear_background_keeps_state_for_redraw() -> None:
    script = (
        "const runtime=require(process.argv[1]);"
        "const layers=require(process.argv[2]);"
        "const visual={kind:'coordinate_plane',render_required:true,"
        "points:[{x:0,y:0},{x:2,y:2}],lines:[{through_points:[[0,0],[2,2]]}],"
        "x_range:[-3,3],y_range:[-3,3]};"
        "const calls=[];"
        "const ctx={"
        "canvas:{width:300,height:200,clientWidth:300,clientHeight:200},"
        "setTransform(){},clearRect(){calls.push('clear');},"
        "fillRect(){calls.push('fill');},save(){},restore(){},"
        "drawImage(){calls.push('image');},"
        "get fillStyle(){return '#fff';},set fillStyle(_){},"
        "get globalAlpha(){return 1;},set globalAlpha(_){},"
        "beginPath(){},moveTo(){},lineTo(){},stroke(){},arc(){},fill(){},"
        "get font(){return ''},set font(_){},"
        "fillText(){},get textAlign(){return 'left'},set textAlign(_){},"
        "get textBaseline(){return 'top'},set textBaseline(_){}"
        "};"
        "layers.setVisualSpecBackground(visual,ctx,300,200,runtime);"
        "layers.clearInkLayer({clearRect(){calls.push('ink-clear');}},300,200);"
        "layers.redrawQuestionBackground(ctx,300,200,runtime);"
        "process.stdout.write(JSON.stringify({"
        "hasBg:layers.hasQuestionBackground(),calls"
        "}));"
    )
    payload = json.loads(_run_node(script, str(VISUAL_SPEC_PATH), str(SCRATCHPAD_LAYERS_PATH)))
    assert payload["hasBg"] is True
    assert "ink-clear" in payload["calls"]
    assert payload["calls"].count("clear") >= 2


def test_non_renderable_visual_spec_does_not_store_background() -> None:
    mod = importlib.import_module(
        "agent_skills_v3.vh_數學B1_PropertiesOfPerpendicularLines.components.src_4526.generate"
    )
    from core.gencode.domain_matrix_adapter import _apply_line_equation_practice_surface

    payload = _apply_line_equation_practice_surface(
        mod.generate(seed=1, component_id="src_4526")
    )
    script = (
        "const runtime=require(process.argv[1]);"
        "const layers=require(process.argv[2]);"
        "const spec=JSON.parse(process.argv[3]);"
        "const ctx={canvas:{width:300,height:200},setTransform(){},clearRect(){},fillRect(){}};"
        "const ok=layers.setVisualSpecBackground(spec,ctx,300,200,runtime);"
        "process.stdout.write(JSON.stringify({ok,hasBg:layers.hasQuestionBackground()}));"
    )
    result = json.loads(
        _run_node(
            script,
            str(VISUAL_SPEC_PATH),
            str(SCRATCHPAD_LAYERS_PATH),
            json.dumps(payload["visual_spec"]),
        )
    )
    assert result["ok"] is False
    assert result["hasBg"] is False


def test_practice_templates_use_shared_scratchpad_background_layer() -> None:
    index_html = INDEX_TEMPLATE_PATH.read_text(encoding="utf-8")
    adaptive_html = ADAPTIVE_TEMPLATE_PATH.read_text(encoding="utf-8")
    for template in (index_html, adaptive_html):
        assert "js/scratchpad_layers.js" in template
        assert "applyQuestionScratchpadBackground" in template
        assert "redrawScratchpadQuestionBackground" in template
        assert "getScratchpadBackgroundLayer" in template


def test_practice_template_no_duplicate_question_media_canvas_for_visual_spec() -> None:
    index_html = INDEX_TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "readonlyCanvas = document.createElement('canvas')" not in index_html
    assert "layer.hideQuestionMediaContainer(qmc)" in index_html
    adaptive_html = ADAPTIVE_TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "runtime.renderToCanvas(questionVisualCanvas, visualSpec)" not in adaptive_html
