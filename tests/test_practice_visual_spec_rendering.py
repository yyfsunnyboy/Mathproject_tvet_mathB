from __future__ import annotations

import json
import importlib
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = PROJECT_ROOT / "static" / "js" / "visual_spec.js"
TEMPLATE_PATH = PROJECT_ROOT / "templates" / "index.html"


def _evaluate(cases: list[dict]) -> list[bool]:
    node_executable = shutil.which("node")
    if not node_executable:
        candidates = sorted(
            (Path.home() / ".cache" / "codex-runtimes").glob(
                "*/dependencies/node/bin/node.exe"
            )
        )
        node_executable = str(candidates[0]) if candidates else None
    assert node_executable, "Node.js runtime is required for frontend visual-spec tests"
    script = (
        "const runtime=require(process.argv[1]);"
        "const cases=JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify(cases.map(runtime.requiresVisualRendering)));"
    )
    completed = subprocess.run(
        [node_executable, "-e", script, str(RUNTIME_PATH), json.dumps(cases)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_no_visual_empty_and_structured_math_specs_do_not_render() -> None:
    results = _evaluate(
        [
            {},
            {"kind": "no_visual"},
            {
                "kind": "coordinate_plane_spec",
                "points": [{"label": "A", "x": 1, "y": 2}],
                "lines": [],
                "x_range": [-10, 10],
                "y_range": [-10, 10],
            },
            {"kind": "graph", "points": [], "lines": []},
        ]
    )
    assert results == [False, False, False, False]


def test_drawable_graph_and_chart_specs_require_rendering() -> None:
    results = _evaluate(
        [
            {
                "kind": "function_graph",
                "points": [[0, -2], [4, 0]],
                "lines": [{"equation": "y=1/2*x-2"}],
            },
            {
                "type": "cumulative_frequency_polygon",
                "data_points": [[10, 2], [20, 8]],
            },
            {
                "kind": "coordinate_plane",
                "render_required": True,
                "points": [{"x": 1, "y": 2, "label": "A"}],
                "lines": [{"through_points": [[0, 0], [2, 2]], "label": "AB"}],
            },
        ]
    )
    assert results == [False, True, True]


def test_midpoint_text_components_do_not_require_visual_rendering() -> None:
    visual_specs = []
    for source_id in (4428, 4429, 4443, 4511):
        module = importlib.import_module(
            "agent_skills_v3.vh_數學B1_MidpointCoordinates"
            f".components.src_{source_id}.generate"
        )
        payload = module.generate(seed=17, component_id=f"src_{source_id}")
        visual_specs.append(payload["visual_spec"])
    assert _evaluate(visual_specs) == [False, False, False, False]


def test_practice_template_uses_shared_visual_render_predicate() -> None:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "js/visual_spec.js" in template
    assert "js/scratchpad_layers.js" in template
    assert "function renderReadonlyVisualSpec(visualSpec)" in template
    assert "runtime.isVisualSpecRenderable(visualSpec)" in template
    assert "layer.setVisualSpecBackground(visualSpec, backgroundCtx" in template
    assert "data.visual_spec && Object.keys(data.visual_spec).length > 0" not in template
    assert "圖表資料需由伺服器渲染" not in template


def test_diagram_math_labels_are_formatted_for_canvas_display() -> None:
    """Canvas fillText cannot MathJax; shared formatter must convert TeX labels."""
    node_executable = shutil.which("node")
    if not node_executable:
        candidates = sorted(
            (Path.home() / ".cache" / "codex-runtimes").glob(
                "*/dependencies/node/bin/node.exe"
            )
        )
        node_executable = str(candidates[0]) if candidates else None
    assert node_executable, "Node.js runtime is required for frontend visual-spec tests"

    cases = [
        {"raw": "A", "expect": "A", "raw_latex": False},
        {"raw": "B", "expect": "B", "raw_latex": False},
        {"raw": "O", "expect": "O", "raw_latex": False},
        {"raw": r"\vec{a}", "expect": "a\u20d7", "raw_latex": False},
        {"raw": r"\vec{b}", "expect": "b\u20d7", "raw_latex": False},
        {"raw": r"-\vec{a}", "expect": "-a\u20d7", "raw_latex": False},
        {"raw": r"\vec{a}+\vec{b}", "expect": "a\u20d7+b\u20d7", "raw_latex": False},
        {
            "raw": r"\frac{1}{3}\vec{a}-\frac{1}{2}\vec{b}",
            "expect": "(1/3)a\u20d7-(1/2)b\u20d7",
            "raw_latex": False,
        },
        {"raw": r"\overrightarrow{AB}", "expect": "AB\u20d7", "raw_latex": False},
    ]
    script = (
        "const runtime=require(process.argv[1]);"
        "const cases=JSON.parse(process.argv[2]);"
        "const out=cases.map(c=>({"
        "raw:c.raw,"
        "got:runtime.formatDiagramLabel(c.raw),"
        "expect:c.expect,"
        "ok:runtime.formatDiagramLabel(c.raw)===c.expect,"
        "exposes:runtime.diagramLabelExposesRawLatex(c.raw)"
        "}));"
        "process.stdout.write(JSON.stringify(out));"
    )
    completed = subprocess.run(
        [node_executable, "-e", script, str(RUNTIME_PATH), json.dumps(cases)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    results = json.loads(completed.stdout)
    assert all(row["ok"] for row in results), results
    assert all(row["exposes"] is False for row in results), results


def test_b2_ch3_vector_diagram_payload_labels_do_not_expose_raw_tex_after_format() -> None:
    node_executable = shutil.which("node")
    if not node_executable:
        candidates = sorted(
            (Path.home() / ".cache" / "codex-runtimes").glob(
                "*/dependencies/node/bin/node.exe"
            )
        )
        node_executable = str(candidates[0]) if candidates else None
    assert node_executable, "Node.js runtime is required for frontend visual-spec tests"

    from core.domain.vector_plane_domain import build_vector_plane_matrix

    labels: list[str] = []
    for op in (
        "express_named_vectors_in_given_basis",
        "construct_linear_combination_choice",
        "identify_equal_vector_mcq",
        "simplify_vector_path_expression",
    ):
        matrix = build_vector_plane_matrix(operation=op, seed=7)
        visual = matrix.get("visual_spec") or {}
        for arrow in visual.get("arrows") or []:
            if isinstance(arrow, dict) and arrow.get("label"):
                labels.append(str(arrow["label"]))
        for point in visual.get("points") or []:
            if isinstance(point, dict) and point.get("label"):
                labels.append(str(point["label"]))
    assert labels
    script = (
        "const runtime=require(process.argv[1]);"
        "const labels=JSON.parse(process.argv[2]);"
        "const out=labels.map(l=>({"
        "raw:l,"
        "display:runtime.formatDiagramLabel(l),"
        "exposes:runtime.diagramLabelExposesRawLatex(l)"
        "}));"
        "process.stdout.write(JSON.stringify(out));"
    )
    completed = subprocess.run(
        [node_executable, "-e", script, str(RUNTIME_PATH), json.dumps(labels)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    results = json.loads(completed.stdout)
    assert all(not row["exposes"] for row in results), results
    assert any("\u20d7" in row["display"] for row in results if "\\vec" in row["raw"]), results


def test_practice_template_renders_answer_contract_parts_and_handwriting_canvas() -> None:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "function resolveMultiPartFields(payload)" in template
    assert "contract.parts" in template
    assert "input.dataset.fieldKey = fieldKey" in template
    assert "payload.user_answer = collected" in template
    assert "isDrawingQuestion(cq)" in template
    assert "uiContract.handwritingEnabled && uiContract.canvasRequired" in template
