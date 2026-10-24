"""Isolated sandbox gate for the seven Unit 10 revision-2 items (cubic drawing + five-option graph choice).

Builds ``tmp/gh_unit10_drawing_dryrun`` only.  Drawing parts are graded by the formal ``evaluate_cubic_graph``
evaluator on synthetic analyzer features / a deterministic vision stand-in; the real vision model is reported
separately.  Source oracles are hand-derived values, independent of the domain code.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path
from unittest import mock

import pytest
import sympy as sp

from agent_domains_candidate.function_cubic import build_sandbox as B
from agent_domains_candidate.function_cubic.cubic_specs import COMPONENTS, DEFERRED, OP, REV2_COMPONENTS, SKILLS
from agent_domains_candidate.function_cubic.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.function_cubic.verification import _drawing_value, equivalent_value, grade, verify_payload, wrong_value
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = PROJECT_ROOT / "tmp" / "gh_unit10_drawing_dryrun"
DB = PROJECT_ROOT / "instance" / "kumon_math.db"
SEEDS = range(20)
register_candidate_in_memory()
B.build_all(components=REV2_COMPONENTS, dryrun=DRYRUN)
SKILL = SKILLS["cubic"]
SHAPES = {  # component -> (answer_type, canvases, other parts)
    12603: ("drawing", 1, 0), 12604: ("drawing", 1, 0), 12605: ("drawing", 1, 0), 12606: ("multi_part", 1, 1),
    12607: ("multi_part", 1, 5), 12613: ("multi_part", 1, 5), 12626: ("single_choice", 0, 0),
}


def _load(cid: int, filename: str):
    path = DRYRUN / SKILL / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"u10d_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gen(cid: int, seed: int = 0) -> dict:
    return _load(cid, "generate.py").generate(seed=seed)


def test_revision_two_items_are_exactly_the_seven_deferred_rows():
    assert set(REV2_COMPONENTS) == set(DEFERRED) == {12603, 12604, 12605, 12606, 12607, 12613, 12626}
    assert not set(REV2_COMPONENTS) & set(COMPONENTS)


def test_skill_bindings_follow_the_formal_database():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = dict(con.execute("select id, skill_id from textbook_examples where id between 12603 and 12628").fetchall())
    finally:
        con.close()
    assert all(rows[cid] == SKILL for cid in REV2_COMPONENTS)


@pytest.mark.parametrize("cid", sorted(REV2_COMPONENTS))
def test_component_contract_canvases_and_parts(cid):
    directory = DRYRUN / SKILL / "components" / f"src_{cid}"
    assert {p.name for p in directory.iterdir() if p.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    assert (directory / "get_hint.py").read_text(encoding="utf-8") == _build_get_hint_py()
    answer_type, canvases, others = SHAPES[cid]
    surfaces = set()
    for seed in SEEDS:
        payload = _gen(cid, seed)
        assert payload == _gen(cid, seed) and payload["fixed_domain_key"] == "function.cubic_graph"
        assert "MATH_PARSE_FAILED" not in payload["question_text"] and not payload.get("image_assets")
        contract = payload["answer_contract"]
        assert contract["answer_type"] == answer_type
        assert verify_payload(payload, SKILL, f"src_{cid}") == [], (seed, payload["question_text"][:50])
        parts = contract.get("parts") or []
        drawing_parts = [p for p in parts if p["answer_type"] == "drawing"] if parts else ([contract] if answer_type == "drawing" else [])
        assert len(drawing_parts) == canvases and len(parts) - (len(drawing_parts) if parts else 0) == others
        for part in drawing_parts:
            spec = part["expected_drawing_spec"]
            assert spec["drawing_type"] == "cubic_graph" and len(spec["expected_cubics"]) == 1
            rng, e = spec["axis_range"], spec["expected_cubics"][0]
            seen = [(0, 0), tuple(e["center"])] + [tuple(t) for t in e["turning_points"]] + [(z, 0) for z in e["x_intercepts"]]
            assert all(rng["x_min"] <= x <= rng["x_max"] and rng["y_min"] <= y <= rng["y_max"] for x, y in seen)  # the canvas shows every key feature
            assert all(abs(y - (e["a"] * (x - e["center"][0]) ** 3 + e["p"] * (x - e["center"][0]) + e["center"][1])) < 1e-9 for x, y in e["points"])
        surfaces.add(json.dumps([payload["question_text"], payload.get("visual_spec"), payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
    assert len(surfaces) >= 18


def test_source_oracles():
    x = sp.Symbol("x")

    def spec(cid: int) -> dict:
        c = _gen(cid)["answer_contract"]
        return (c.get("expected_drawing_spec") or next(p["expected_drawing_spec"] for p in c["parts"] if p["answer_type"] == "drawing"))["expected_cubics"][0]

    assert (spec(12603)["a"], spec(12603)["p"], spec(12603)["center"], spec(12603)["turning_points"]) == (1, 0, [0, 0], [])
    assert (spec(12604)["a"], spec(12604)["p"], spec(12604)["turning_points"]) == (1, 2, [])
    e = spec(12605)
    assert (e["a"], e["p"], e["x_intercepts"]) == (1, -1, [-1.0, 0.0, 1.0]) and [round(t[0], 4) for t in e["turning_points"]] == [-0.5774, 0.5774]
    a = _gen(12606)["correct_answer"]
    assert a["part_2"] == "(3,1)" and spec(12606)["center"] == [3, 1]
    a = _gen(12607)["correct_answer"]  # y = x^3-6x^2+11x-3 = (x-2)^3-(x-2)+3
    assert [a[f"part_{i}"] for i in (1, 2, 3, 4)] == ["1", "-1", "2", "3"] and a["part_6"] == "(2,3)"
    a = _gen(12613)["correct_answer"]  # y = -x^3+3x^2-2x-2 = -(x-1)^3+(x-1)-2
    assert [a[f"part_{i}"] for i in (1, 2, 3, 4)] == ["-1", "1", "1", "-2"] and a["part_6"] == "(1,-2)"
    assert _gen(12626)["correct_answer"] == "E"  # a < 0, b > 0: falls, rises, falls = option (5)
    assert sp.expand((x - 2) ** 3 - (x - 2) + 3 - (x ** 3 - 6 * x ** 2 + 11 * x - 3)) == 0


# --- the drawing parts are graded by the formal evaluator, numbers and drawing separately -------------------------------

def _fake(*, image_data_url, expected_drawing_spec, **_kw):
    if not image_data_url:
        return {"is_correct": None, "system_error": True, "status": "missing_image"}
    return {"is_correct": "GOOD" in image_data_url, "system_error": False, "status": "success"}


@pytest.mark.parametrize("cid", [12606, 12607, 12613])
def test_numbers_and_drawing_are_both_required(cid):
    payload = _gen(cid)
    contract = payload["answer_contract"]
    good = {p["key"]: (_drawing_value("GOOD") if p["answer_type"] == "drawing" else p["expected_answer"]) for p in contract["parts"]}
    with mock.patch("core.checkers.free_response_drawing_checker.check_drawing_answer", side_effect=_fake):
        assert grade(payload, good, SKILL)
        for part in contract["parts"]:
            bad = dict(good)
            bad[part["key"]] = _drawing_value("BAD") if part["answer_type"] == "drawing" else wrong_value(part)
            assert not grade(payload, bad, SKILL), part["key"]  # right drawing + wrong number, or wrong drawing + right number
        for part in contract["parts"]:
            if part["answer_type"] != "drawing" and equivalent_value(part) is not None:
                alt = dict(good)
                alt[part["key"]] = equivalent_value(part)
                assert grade(payload, alt, SKILL)


# --- 12626: the option graphs, the given line and the correct answer agree ---------------------------------------------

def _read(points: list) -> tuple[str, int]:
    """End behaviour and number of turning points of a plotted curve, read from the plotted points alone."""
    ys = [p[1] for p in points]
    signs = [1 if b > a else -1 for a, b in zip(ys, ys[1:]) if abs(b - a) > 1e-6]
    turns = sum(1 for s, t in zip(signs, signs[1:]) if s != t)
    if signs[0] != signs[-1] and turns == 1:
        return "parabola", 1
    return ("up" if ys[-1] > ys[-2] else "down"), turns


@pytest.mark.parametrize("seed", SEEDS)
def test_12626_figure_matches_the_line_and_the_correct_option(seed):
    p = _gen(12626, seed)
    givens, answer = p["math_core"]["givens"], p["math_core"]["target"]
    figure = p["visual_spec"]
    assert figure["kind"] == "coordinate_plane_multi_figure" and figure["show_grid"] is False and len(figure["figures"]) == 6
    line = figure["figures"][0]
    (x1, y1), (x2, y2) = line["through_points"] if "through_points" in line else line["lines"][0]["through_points"]
    slope, intercept = (y2 - y1) / (x2 - x1), y1 - (y2 - y1) / (x2 - x1) * x1
    assert slope == pytest.approx(float(sp.Rational(str(givens["slope"])))) and intercept == pytest.approx(float(sp.Rational(str(givens["intercept"]))))
    options = [f for f in figure["figures"][1:]]
    assert [f["label"] for f in options] == [f"({i})" for i in range(1, 6)]
    reads = [_read(f["curves"][0]["points"]) for f in options]
    assert sum(1 for r in reads if r[0] == "parabola") == 1
    want = ("up" if slope > 0 else "down", 0 if slope * intercept > 0 else 2)  # y = a x^3 + b x: 2 turning points iff a*b < 0
    matches = [i + 1 for i, r in enumerate(reads) if r == want]
    assert len(matches) == 1
    letters = "ABCDE"
    assert p["correct_answer"] == letters[matches[0] - 1] and [c["label"] for c in p["choices"]] == list(letters)
    assert all(f["x_range"][0] > 0 and f["y_range"][0] > 0 for f in options)  # no axes are drawn inside the option panels
