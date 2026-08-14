from __future__ import annotations

import importlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from core.gencode.domain_matrix_adapter import _apply_line_equation_practice_surface
from core.routes.practice import _finalize_practice_question_api_fields

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VISUAL_SPEC_PATH = PROJECT_ROOT / "static" / "js" / "visual_spec.js"
SCRATCHPAD_LAYERS_PATH = PROJECT_ROOT / "static" / "js" / "scratchpad_layers.js"

BLANK_KINDS = {
    "(empty)",
    "cartesian_canvas",
    "no_visual",
    "line_graph_choices",
    "cumulative_frequency_table",
}

FIXTURES = [
    ("vh_數學B1_PropertiesOfPerpendicularLines", "src_4536", "coordinate_plane", "visual_spec"),
    ("vh_數學B1_SlopeOfALine", "src_4520", "coordinate_plane_multi_figure", "visual_spec"),
    ("vh_數學B1_PropertiesOfPerpendicularLines", "src_4526", "(blank)", "none"),
    ("vh_數學B1_LinearFunction", "src_4424", "coordinate_line_graph", "visual_spec"),
    ("vh_數學B1_LinearFunction", "src_4445", "tiered_linear_graph", "visual_spec"),
    ("vh_數學B1_LinearFunction", "src_4442", "linear_application_graph", "visual_spec"),
    ("vh_數學B1_LinearFunction", "src_4426", "collinear_points", "visual_spec"),
    ("vh_數學B1_LinearFunction", "src_4433", "cartesian_canvas", "none"),
    ("vh_數學B1_LinearFunction", "src_4516", "line_graph_choices", "none"),
    ("vh_數學B4_StatisticalChartReading", "src_3884", "cumulative_frequency_polygon", "visual_spec"),
    ("vh_數學B4_CumulativeFrequencyTablesAndGraphs", "src_3830", "cumulative_frequency_graph", "visual_spec"),
    ("vh_數學B4_HistogramsAndFrequencyPolygons", "src_3826", "table", "image"),
    ("vh_數學B4_NormalDistributionAndEmpiricalRule", "src_3859", "visual_spec.image_base64", "image"),
]


def _node_executable() -> str:
    node_executable = shutil.which("node")
    if node_executable:
        return node_executable
    candidates = sorted(
        (Path.home() / ".cache" / "codex-runtimes").glob("*/dependencies/node/bin/node.exe")
    )
    assert candidates, "Node.js runtime is required"
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


def _slim_payload_for_strategy(payload: dict) -> dict:
    slim: dict = {}
    visual_spec = payload.get("visual_spec")
    placeholder = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    if isinstance(visual_spec, dict):
        slim_vs = {
            key: value
            for key, value in visual_spec.items()
            if key != "image_base64"
        }
        if str(visual_spec.get("image_base64") or "").strip():
            slim_vs["image_base64"] = placeholder
        if slim_vs:
            slim["visual_spec"] = slim_vs
    for key in ("table_data", "visual_aids", "image_url"):
        if payload.get(key):
            slim[key] = payload[key]
    if str(payload.get("image_base64") or "").strip():
        slim["image_base64"] = placeholder
    return slim


def _load_payload(skill_id: str, component_id: str) -> dict:
    if component_id == "src_4520":
        from tests.domain.test_slope_of_a_line_domain import _build
        from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

        matrix = _build("classify_and_compare_figure_slopes", seed=4)
        return convert_line_equation_matrix_to_question_payload(
            matrix,
            presentation_mode="short_answer",
            domain_operation="classify_and_compare_figure_slopes",
            answer_type="multi_part",
        )
    mod = importlib.import_module(
        f"agent_skills_v3.{skill_id}.components.{component_id}.generate"
    )
    raw = mod.generate(seed=1, component_id=component_id)
    if skill_id.startswith("vh_數學B1_PropertiesOf") or skill_id.startswith("vh_數學B1_SlopeOf"):
        try:
            raw = _apply_line_equation_practice_surface(raw)
        except Exception:
            pass
    return _finalize_practice_question_api_fields(raw, skill_id=skill_id)


def _background_strategy(payload: dict) -> dict:
    script = (
        "const fs=require('fs');"
        "const runtime=require(process.argv[1]);"
        "const layers=require(process.argv[2]);"
        "const raw=process.argv[3];"
        "const payload=raw.endsWith('.json')?JSON.parse(fs.readFileSync(raw,'utf8')):JSON.parse(raw);"
        "process.stdout.write(JSON.stringify("
        "layers.shouldRenderBackgroundForPayload(payload,runtime)));"
    )
    return json.loads(
        _run_node(
            script,
            str(VISUAL_SPEC_PATH),
            str(SCRATCHPAD_LAYERS_PATH),
            json.dumps(_slim_payload_for_strategy(payload)),
        )
    )


@pytest.mark.parametrize(("skill_id", "component_id", "kind_label", "expected_kind"), FIXTURES)
def test_production_visual_background_strategy(
    skill_id: str, component_id: str, kind_label: str, expected_kind: str
) -> None:
    payload = _load_payload(skill_id, component_id)
    strategy = _background_strategy(payload)
    if expected_kind == "none":
        assert strategy["kind"] == "none"
        return
    assert strategy["kind"] == expected_kind
    if expected_kind == "visual_spec":
        assert payload.get("visual_spec")
        renderable = json.loads(
            _run_node(
                "const r=require(process.argv[1]);const s=JSON.parse(process.argv[2]);"
                "process.stdout.write(JSON.stringify(r.isVisualSpecRenderable(s)));",
                str(VISUAL_SPEC_PATH),
                json.dumps(payload["visual_spec"]),
            )
        )
        assert renderable is True


def test_all_non_blank_production_visual_kinds_have_background_strategy() -> None:
    inventory_path = PROJECT_ROOT / "reports" / "_inventory_visual_kinds.json"
    if not inventory_path.exists():
        pytest.skip("inventory report missing; run scripts/inventory_production_visual_kinds.py first")
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    unsupported: list[str] = []
    for sample in inventory["samples"]:
        kind = sample["kind"]
        if kind in BLANK_KINDS:
            continue
        media = sample["media"]
        has_image = any(
            media.get(key)
            for key in ("payload_image", "vs_image", "table_image", "visual_aids", "image_url")
        )
        if kind in {"table", "visual_spec.image_base64"}:
            assert has_image, f"{sample['component_id']} expected image fallback media"
            continue
        if kind.startswith("cumulative_frequency") and has_image:
            continue
        if kind in {
            "coordinate_plane",
            "coordinate_plane_spec",
            "coordinate_plane_multi_figure",
            "coordinate_line_graph",
            "tiered_linear_graph",
            "linear_application_graph",
            "collinear_points",
            "cumulative_frequency_polygon",
            "cumulative_frequency_graph",
        }:
            continue
        unsupported.append(f"{sample['skill_id']}:{sample['component_id']}:{kind}")
    assert unsupported == [], "Unhandled production visual kinds: " + ", ".join(unsupported[:20])


def test_image_fallback_priority_visual_spec_before_payload() -> None:
    script = (
        "const runtime=require(process.argv[1]);"
        "const layers=require(process.argv[2]);"
        "const payload={"
        "visual_spec:{type:'cumulative_frequency_polygon',rows:[['10',2],['20',4]],cumulative_values:[2,4]},"
        "image_base64:'fallback-should-not-win'"
        "};"
        "process.stdout.write(JSON.stringify(layers.shouldRenderBackgroundForPayload(payload,runtime)));"
    )
    strategy = json.loads(_run_node(script, str(VISUAL_SPEC_PATH), str(SCRATCHPAD_LAYERS_PATH)))
    assert strategy["kind"] == "visual_spec"


def test_visual_spec_and_table_image_fallback_sources() -> None:
    script = (
        "const layers=require(process.argv[1]);"
        "const payloadVs={visual_spec:{image_base64:'vs-image'}};"
        "const payloadTable={table_data:{image_base64:'table-image'}};"
        "process.stdout.write(JSON.stringify({"
        "vs:layers.extractImageFromPayload(payloadVs),"
        "table:layers.extractImageFromPayload(payloadTable)"
        "}));"
    )
    result = json.loads(_run_node(script, str(SCRATCHPAD_LAYERS_PATH)))
    assert result["vs"] == "vs-image"
    assert result["table"] == "table-image"
