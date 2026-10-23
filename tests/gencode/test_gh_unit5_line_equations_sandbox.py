"""Sandbox gate for 普高數學1 Unit 5 (直線方程式): per-component contract, oracle and grading checks.

Runs against ``reports/gencode_v3_dryrun`` with the candidate domain registered in memory only.
"""

from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import pytest

from agent_domains_candidate.analytic_geometry_lines.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.analytic_geometry_lines.unit5_specs import COMPONENTS, DEFERRED, OP, SKILLS
from core.gencode.answer_payload import validate_answer_contract_consistency
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.services.v3_question_integrity_validator import validate_component_payload
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = PROJECT_ROOT / "tmp" / "gh_unit5_sandbox_dryrun"
SEEDS = range(20)
register_candidate_in_memory()

CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]
DRAWING = {cid for cid, spec in COMPONENTS.items() if spec[1] == "graph_inequality_system"}
MULTI_DRAWING = {12428, 12447}  # multi_part answers with independent canvas parts
FIGURE_WITHOUT_CUE = {12446}  # the book prints the castle figure but the stem never says 如圖
MIN_VARIANTS = {12431: 10, 12444: 16}  # natural input domains: 5 shapes x 2 claims; 4 x 4 lengths


def _load(skill_id: str, cid: int, filename: str):
    path = DRYRUN / skill_id / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"u5_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


from agent_domains_candidate.analytic_geometry_lines.verification import (  # noqa: E402
    equivalent_value as _equivalent_value,
    grade as _grade,
    parts_of as _parts,
    wrong_value as _wrong_value,
)


@pytest.mark.parametrize(("cid", "skill_id", "operation"), CASES)
def test_component_contract_oracle_and_grading(cid, skill_id, operation):
    directory = DRYRUN / skill_id / "components" / f"src_{cid}"
    assert {p.name for p in directory.iterdir() if p.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    assert (directory / "get_hint.py").read_text(encoding="utf-8") == _build_get_hint_py()
    generator = _load(skill_id, cid, "generate.py")
    metadata = _load(skill_id, cid, "metadata.py")
    assert metadata.TEXTBOOK_EXAMPLE_ID == cid and metadata.DOMAIN_OPERATION == operation

    surfaces = set()
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        assert payload == generator.generate(seed=seed)  # deterministic
        assert payload["domain_operation"] == operation and payload["textbook_example_id"] == cid
        assert payload["fixed_domain_key"] == "analytic_geometry.line_equations"
        assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
        assert validate_answer_contract_consistency(payload) == []
        assert validate_answer_contract_consistency(payload["answer_contract"]) == []
        integrity = validate_component_payload(payload, component_id=f"src_{cid}")
        assert integrity["passed"], integrity["blockers"]
        surfaces.add(json.dumps([payload["question_text"], payload.get("visual_spec"), payload.get("table_data"), payload["correct_answer"]],
                                sort_keys=True, ensure_ascii=False, default=str))
        text = payload["question_text"]
        assert "$$" not in text and "\\\\(" not in text
        # a figure is rendered exactly when the stem points at one
        mentions_figure = any(k in text for k in ("如圖", "右圖"))
        assert mentions_figure == bool(payload.get("visual_spec")) or cid in DRAWING or cid in FIGURE_WITHOUT_CUE, (cid, text[:40])

        if cid in DRAWING or cid in MULTI_DRAWING:
            continue
        # canonical answer accepted, every wrong part rejected
        assert _grade(payload, payload["correct_answer"], skill_id)
        parts = _parts(payload)
        if payload["answer_contract"]["answer_type"] in {"multi_part", "table_fill"}:
            for part in parts:
                bad = dict(payload["correct_answer"])
                bad[part["key"]] = _wrong_value(part)
                assert not _grade(payload, bad, skill_id), (seed, part["key"], bad)
                equivalent = _equivalent_value(part)
                if equivalent is not None:
                    good = dict(payload["correct_answer"])
                    good[part["key"]] = equivalent
                    assert _grade(payload, good, skill_id), (seed, part["key"], good)
        else:
            assert not _grade(payload, _wrong_value(parts[0]), skill_id)
            equivalent = _equivalent_value(parts[0])
            if equivalent is not None:
                assert _grade(payload, equivalent, skill_id), (seed, equivalent)
    assert len(surfaces) >= MIN_VARIANTS.get(cid, 18)


def test_nothing_is_deferred_any_more():
    assert DEFERRED == {}


def test_all_forty_six_textbook_rows_are_accounted_for():
    assert set(COMPONENTS) == set(range(12403, 12449))


@pytest.mark.parametrize("cid", sorted(MULTI_DRAWING))
def test_multi_part_with_independent_canvases(cid):
    from agent_domains_candidate.analytic_geometry_lines.verification import verify_payload

    skill_id = SKILLS[COMPONENTS[cid][0]]
    generator = _load(skill_id, cid, "generate.py")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        contract = payload["answer_contract"]
        assert contract["answer_type"] == "multi_part" and contract["checker"] == "multi_part_answer_checker"
        drawings = [p for p in contract["parts"] if p["answer_type"] == "drawing"]
        assert len(drawings) == (3 if cid == 12428 else 1)
        assert len({p["key"] for p in drawings}) == len(drawings)  # one independent canvas each
        assert all(p["input_type"] == "canvas" and p["text_answer_enabled"] is False for p in drawings)
        if cid == 12447:
            count = [p for p in contract["parts"] if p["answer_type"] != "drawing"][0]
            assert count["checker"] == "rational_checker"
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], seed


def test_12428_and_12447_source_oracles():
    """Hand-derived: (1) y<=3x/2+3 (2) y>=-x/2 (3) x>=2, all solid; 12447 quadrilateral (0,2),(0,6),(3,0),(2,0) with 13 lattice points."""
    g = _load(SKILLS["ineq"], 12428, "generate.py").generate(seed=0)
    specs = [p["expected_drawing_spec"] for p in g["answer_contract"]["parts"]]
    assert [s["relations"][0]["boundary"] for s in specs] == ["solid"] * 3
    assert [tuple(s["relations"][0]["line"]) for s in specs] == [(3, -2, 6), (1, 2, 0), (1, 0, -2)]
    # shaded side checked with points: (1) origin satisfies 3x-2y+6>=0; (2) (0,1) satisfies x+2y>=0, (0,-1) does not; (3) (3,0) yes
    assert 3 * 0 - 2 * 0 + 6 >= 0 and 0 + 2 * 1 >= 0 and not 0 + 2 * -1 >= 0 and 3 - 2 >= 0
    h = _load(SKILLS["ineq"], 12447, "generate.py").generate(seed=0)
    spec = [p for p in h["answer_contract"]["parts"] if p["answer_type"] == "drawing"][0]["expected_drawing_spec"]
    assert sorted(tuple(map(Fraction, v)) for v in spec["region_polygon"]) == sorted([(0, 2), (0, 6), (3, 0), (2, 0)])
    assert h["correct_answer"]["part_2"] == "13"


@pytest.mark.parametrize("cid", sorted(DRAWING))
def test_drawing_components_use_the_formal_drawing_contract(cid):
    skill_id = SKILLS[COMPONENTS[cid][0]]
    generator = _load(skill_id, cid, "generate.py")
    from core.services import drawing_answer_analysis_service as svc

    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        contract = payload["answer_contract"]
        ui = contract["ui_contract"]
        assert contract["answer_type"] == "drawing" and contract["checker"] == "free_response_drawing_checker"
        assert contract["answer_equivalence"] == "drawing_equivalence" and payload["presentation_mode"] == "canvas"
        assert ui["drawing_required"] and ui["ai_check_required"] and ui["success_dialog_required"] and ui["canvas_required"]
        assert not ui["text_answer_enabled"] and not ui["text_input_enabled"] and not ui["submit_button_enabled"] and not ui["normal_submit_enabled"]
        spec = contract["expected_drawing_spec"]
        assert spec["drawing_type"] in svc.SUPPORTED_DRAWING_TYPES and spec["drawing_type"] in svc.DRAWING_EVALUATOR_REGISTRY
        assert payload["visual_spec"]["kind"] == "cartesian_canvas" and payload["visual_spec"]["editable"] is True
        assert payload["visual_spec"]["axis_range"] == spec["axis_range"]
        # the canonical drawing is accepted by the shared evaluator and its mirror image is rejected
        probes = svc.inequality_region_probe_points(spec)
        assert any(p["expected"] for p in probes) and any(not p["expected"] for p in probes)
        features = {
            "recognized_type": "linear_inequality_region", "required_elements": {"x_axis": True, "y_axis": True},
            "lines": [{"points_on_line": _two_points(r["line"]), "style": r["boundary"]} for r in spec["relations"]],
            "shaded_region_detected": True, "confidence": 0.95,
            "probe_points": [{"x": p["x"], "y": p["y"], "shaded": p["expected"]} for p in probes],
        }
        assert svc.evaluate_linear_inequality_region(features, spec)["is_correct"] is True
        features["probe_points"] = [{**p, "shaded": not p["shaded"]} for p in features["probe_points"]]
        assert svc.evaluate_linear_inequality_region(features, spec)["is_correct"] is False
        # no image -> never graded as correct, reported as a system condition rather than a wrong answer
        assert not check_answer({}, payload["correct_answer"], payload=payload, answer_contract=contract, skill_id=skill_id)
        # independent truth: probe flags agree with the written relations
        for p in probes:
            holds = all(r["line"][0] * p["x"] + r["line"][1] * p["y"] + r["line"][2] > 0 for r in spec["relations"])
            assert holds == p["expected"]


def _two_points(line):
    a, b, c = line
    if b != 0:
        return [[x, (-a * x - c) / b] for x in (-3.0, 0.0, 3.0)]
    return [[-c / a, y] for y in (-3.0, 0.0, 3.0)]


def test_table_fill_component_renders_cells_inline_without_internal_keys():
    skill_id = SKILLS["eq"]
    payload = _load(skill_id, 12410, "generate.py").generate(seed=0)
    from core.gencode.table_question_contract import normalize_table_question_payload

    normalized = normalize_table_question_payload(payload)
    table = normalized["table_data"]
    assert table["interaction_mode"] == "inline_input" and table["show_blank_labels"] is False
    assert len(table["blank_cells"]) == 7
    cells = {(c["row"], c["col"]) for c in table["blank_cells"]}
    assert len(cells) == 7
    flat = json.dumps(table["display_rows"], ensure_ascii=False)
    assert "cell_" not in flat
    for row, col in cells:
        assert table["display_rows"][row][col] == ""
    assert "求" not in payload["question_text"] or "a" not in payload["question_text"].split("求")[-1][:3]


def test_figures_show_what_the_stem_says():
    """Spot-check the generated figure of a few components against their own givens."""
    payload = _load(SKILLS["ls"], 12403, "generate.py").generate(seed=0)
    spec = payload["visual_spec"]
    assert spec["kind"] == "coordinate_plane" and spec["render_required"] is True
    assert len(spec["lines"]) == 5 and spec["lines"][0]["label"] == "L₁"
    assert {p.get("label") for p in spec["points"]} >= {"A", "(2,2)", "(3,2)", "(3,1)", "(3,0)", "(2,0)"}
    payload = _load(SKILLS["ineq"], 12443, "generate.py").generate(seed=0)
    spec = payload["visual_spec"]
    labels = {p.get("label") for p in spec["points"]}
    assert {"O", "A(2,6)", "B(5,0)"} <= labels and spec["shade"]["test_point"]
    payload = _load(SKILLS["ineq"], 12430, "generate.py").generate(seed=0)
    spec = payload["visual_spec"]
    assert len(spec["lines"]) == 2 and spec["shade"]["test_point"]
    a, b, c = spec["lines"][0]["a"], spec["lines"][0]["b"], spec["lines"][0]["c"]
    x, y = spec["shade"]["test_point"]
    assert a * x + b * y + c > 0  # the shaded probe lies on the >= 0 side of the first inequality


@pytest.mark.parametrize("cid", [12427, 12430, 12443])
def test_shaded_figures_use_abc_boundary_lines(cid):
    """The renderer clips ``shade`` against each line's a/b/c; through-point lines would shade the whole viewport."""
    generator = _load(SKILLS[COMPONENTS[cid][0]], cid, "generate.py")
    for seed in range(5):
        spec = generator.generate(seed=seed)["visual_spec"]
        assert spec["shade"]["test_point"]
        assert spec["lines"] and all({"a", "b", "c"} <= set(line) for line in spec["lines"])
        x, y = spec["shade"]["test_point"]
        sides = [line["a"] * x + line["b"] * y + line["c"] for line in spec["lines"]]
        assert all(abs(v) > 1e-6 for v in sides)  # the probe lies strictly inside the region


def test_skill_distribution_matches_stage1_bindings():
    import sqlite3

    con = sqlite3.connect(f"file:{(PROJECT_ROOT / 'instance' / 'kumon_math.db').as_posix()}?mode=ro", uri=True)
    try:
        rows = dict(con.execute("select id, skill_id from textbook_examples where id between 12403 and 12448"))
    finally:
        con.close()
    assert len(rows) == 46
    for cid, spec in COMPONENTS.items():
        assert rows[cid] == SKILLS[spec[0]], cid
