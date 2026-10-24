"""Sandbox gate for 普高數學1 Unit 11 (多項式不等式): per-component contract, oracle, grading and figure checks.

Builds ``tmp/gh_unit11_sandbox_dryrun`` (build_sandbox.build_all) with the candidate domain registered in memory only.
Source oracles are hand-derived (independent of the domain code).  Every figure is checked against the generated
numbers: a curve is the polynomial the answer describes, a schematic carries the numbers of the stem.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest
import sympy as sp

from agent_domains_candidate.polynomial_inequality import build_sandbox as B
from agent_domains_candidate.polynomial_inequality.polynomial_inequality_specs import COMPONENTS, DEFERRED, OP, SKILLS
from agent_domains_candidate.polynomial_inequality.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.polynomial_inequality.verification import verify_payload
from core.checkers.inequality_solution_checker import parse_real_solution_set, real_solution_sets_equal
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = B.DRYRUN
DB = PROJECT_ROOT / "instance" / "kumon_math.db"
SEEDS = range(20)
SURFACE_FLOOR = 18
FIGURE_COMPONENTS = {12629, 12630, 12635, 12640, 12645, 12661, 12663, 12666}
register_candidate_in_memory()
B.build_all()

CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]
S = sp.Symbol("x", real=True)
X0 = sp.Symbol("x")  # what sympify gives for an answer string


def _load(skill_id: str, cid: int, filename: str):
    path = DRYRUN / skill_id / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"u11_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gen(cid: int, seed: int = 0) -> dict:
    return _load(SKILLS[COMPONENTS[cid][0]], cid, "generate.py").generate(seed=seed)


def _answers(cid: int):
    return _gen(cid)["correct_answer"]


def _is(text: str, expected: sp.Set) -> bool:
    got = parse_real_solution_set(text)
    return got is not None and real_solution_sets_equal(got, expected)


def _iv(lo, hi, lo_open=False, hi_open=False):
    return sp.Interval(lo, hi, lo_open, hi_open)


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
        assert payload["fixed_domain_key"] == "inequality.polynomial"
        text = payload["question_text"]
        assert "$$" not in text and "承例題" not in text and "MATH_PARSE_FAILED" not in text
        assert bool(payload.get("visual_spec")) == (cid in FIGURE_COMPONENTS)
        assert not payload.get("image_assets")  # no stale static picture is ever attached to a varied question
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], (seed, text[:60])
        surfaces.add(json.dumps([text, payload.get("visual_spec"), payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
    assert len(surfaces) >= SURFACE_FLOOR


def test_coverage_and_deferred_items_are_explicit():
    assert set(COMPONENTS) | set(DEFERRED) == set(range(12629, 12667))
    assert not set(COMPONENTS) & set(DEFERRED)
    assert set(DEFERRED) == {12650, 12662, 12664}
    assert len(COMPONENTS) == 35


def test_skill_bindings_follow_the_formal_database():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = dict(con.execute("select id, skill_id from textbook_examples where id between 12629 and 12666").fetchall())
        stems = dict(con.execute("select id, problem_text from textbook_examples where id in (12650, 12662, 12664)").fetchall())
    finally:
        con.close()
    assert {cid: SKILLS[spec[0]] for cid, spec in COMPONENTS.items()} == {cid: rows[cid] for cid in COMPONENTS}
    assert all(rows[cid] == "gh_PolynomialInequalities" for cid in DEFERRED)
    assert all(stems[cid].rstrip().endswith(("。", "？")) for cid in DEFERRED)  # Stage 1 later restored the cut-off tails (built in revision 2)


# --- source oracles: hand-derived solution sets -----------------------------------------------------------------

def test_oracles_graph_questions():
    a = _answers(12629)
    assert a["part_1"] == [1, 3, 5]
    assert _is(a["part_2"], sp.Union(_iv(1, 3, True, True), _iv(5, sp.oo, True, True)))
    assert _is(a["part_3"], sp.Union(_iv(-sp.oo, 1, True, True), _iv(3, 5, True, True)))
    assert _is(a["part_4"], sp.Union(_iv(-sp.oo, 1, True, False), _iv(3, 5)))
    a = _answers(12630)  # W-shaped quartic touching the axis at 3
    assert a["part_1"] == [1, 3, 5]
    assert _is(a["part_2"], sp.Union(_iv(-sp.oo, 1, True, True), _iv(5, sp.oo, True, True)))
    assert _is(a["part_3"], sp.Union(_iv(1, 3, True, True), _iv(3, 5, True, True)))
    assert _is(a["part_4"], _iv(1, 5))


def test_oracles_linear_and_quadratic():
    assert _is(_answers(12631), _iv(-sp.oo, -4, True, True))
    a = _answers(12632)
    r = sp.sqrt(13)
    assert _is(a["part_1"], _iv(1, 3)) and _is(a["part_2"], sp.Union(_iv(-sp.oo, (1 - r) / 2, True, True), _iv((1 + r) / 2, sp.oo, True, True)))
    assert _is(_answers(12633), sp.Union(_iv(-sp.oo, 2, True, True), _iv(2, sp.oo, True, True)))
    assert _answers(12634) == {"part_1": "全體實數", "part_2": "無解"}
    assert _is(_answers(12641), _iv(-3, sp.oo, True, True))
    a = _answers(12642)
    r = sp.sqrt(37)
    assert _is(a["part_1"], sp.Union(_iv(-sp.oo, -6, True, True), _iv(1, sp.oo, True, True))) and _is(a["part_2"], _iv((5 - r) / 2, (5 + r) / 2))
    assert _is(_answers(12643), sp.FiniteSet(sp.Rational(1, 3)))
    assert _answers(12644) == {"part_1": "全體實數", "part_2": "無解"}
    a = _answers(12656)
    r = sp.sqrt(5)
    assert _is(a["part_1"], sp.Union(_iv(-sp.oo, -2, True, True), _iv(5, sp.oo, True, True)))
    assert _is(a["part_2"], _iv((1 - r) / 2, (1 + r) / 2, True, True)) and _is(a["part_3"], sp.FiniteSet(sp.Rational(3, 2))) and a["part_4"] == "全體實數"


def test_oracles_higher_degree():
    a = _answers(12636)
    assert _is(a["part_1"], sp.Union(_iv(1, 2, True, True), _iv(3, sp.oo, True, True)))
    assert _is(a["part_2"], sp.Union(_iv(-sp.oo, 1, True, True), _iv(1, 3, True, True)))
    a = _answers(12637)
    assert _is(a["part_1"], sp.Union(_iv(-2, -1, True, True), _iv(1, 2, True, True)))
    assert _is(a["part_2"], sp.Union(_iv(-sp.oo, 1), _iv(3, sp.oo)))
    assert _is(_answers(12638), sp.Union(_iv(-sp.oo, 1), sp.FiniteSet(3)))
    a = _answers(12646)
    assert _is(a["part_1"], sp.Union(_iv(-2, 1), _iv(3, sp.oo))) and _is(a["part_2"], sp.Union(sp.FiniteSet(-1), _iv(2, sp.oo)))
    assert _is(_answers(12647), sp.Union(_iv(-3, -2), sp.FiniteSet(3)))
    assert _is(_answers(12648), sp.Union(_iv(-sp.oo, 2, True, True), _iv(2, 5, True, True)))
    a = _answers(12657)
    assert _is(a["part_1"], sp.Union(_iv(-sp.oo, -3, True, True), _iv(-2, -1, True, True)))
    assert _is(a["part_2"], sp.Union(_iv(-2, 1), sp.FiniteSet(2), _iv(3, sp.oo))) and _is(a["part_3"], sp.FiniteSet(3))
    assert _is(a["part_4"], sp.Union(_iv(-2, 1), sp.FiniteSet(2)))
    assert _is(_answers(12660), sp.Union(_iv(-sp.oo, -2), sp.FiniteSet(-1), _iv(3, 5)))


def test_oracles_parameters_and_statements():
    assert _answers(12639) == {"part_1": "-1", "part_2": "3", "part_3": "6"}  # -x^3+3x^2+6x-8
    assert _answers(12658) == {"part_1": "-6/5", "part_2": "9/5"}
    assert _is(_answers(12659), _iv(0, 4))
    assert _is(_answers(12649), _iv(2, sp.oo, True, True))
    assert [_answers(c) for c in (12651, 12652, 12653, 12654, 12655)] == ["B", "B", "B", "A", "A"]
    assert _answers(12661) == [1, 3]  # a>0 and c>0 for the S-shaped cubic through (0,0), (1,0), (2,0)


def test_oracles_applications():
    assert _is(_answers(12635), _iv(10, 30))
    assert _is(_answers(12645), _iv(0, 2, True, False))
    assert _is(_answers(12663), _iv(2, 3))
    assert _is(_answers(12665), _iv(6, 8))
    a = _answers(12640)
    assert a["part_1"] == "8*x+4*y=40" and a["part_3"] == "C"  # x - 3 divides f(x) - 36
    assert sp.simplify(sp.sympify(a["part_2"].replace("^", "**")) - (-2 * X0 ** 3 + 10 * X0 ** 2)) == 0
    assert _is(a["part_4"], _iv(3, 1 + sp.sqrt(7)))
    a = _answers(12666)
    assert a["part_1"] == "x^2+4*x*y=32" and a["part_3"] == "B"  # x - 2 divides f(x) - 14
    assert sp.simplify(sp.sympify(a["part_2"].replace("^", "**")) - (-X0 ** 3 / 4 + 8 * X0)) == 0
    assert _is(a["part_4"], _iv(2, -1 + sp.sqrt(29)))


# --- figures follow the generated numbers -----------------------------------------------------------------------

def _curve_sign_at(curve: list, x: float) -> float:
    for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise AssertionError("x outside the plotted window")


@pytest.mark.parametrize("cid", [12629, 12630])
@pytest.mark.parametrize("seed", SEEDS)
def test_graph_figure_is_the_polynomial_and_roots_are_labelled(cid, seed):
    p = _gen(cid, seed)
    spec, item = p["visual_spec"], p["math_core"]["givens"]["items"][0]
    assert spec["show_grid"] is False and len(spec["curves"]) == 1
    curve = spec["curves"][0]["points"]
    roots = [sp.Rational(str(r)) for r, _m in item["roots"]]
    assert sorted(float(pt["x"]) for pt in spec["points"]) == [float(r) for r in roots]
    assert [pt["label"] for pt in sorted(spec["points"], key=lambda t: t["x"])] == [str(r) for r in roots]
    x = S
    f = item["lead"] * sp.Mul(*[(x - sp.Rational(str(r))) ** m for r, m in item["roots"]])
    for (px, py) in curve[::6]:
        value = float(f.subs(x, px))
        assert (py > 0.02) == (value > 1e-9) or (py < -0.02) == (value < -1e-9) or abs(py) <= 0.02
    assert (curve[-1][1] > 0) == (item["lead"] > 0) and (curve[0][1] > 0) == (item["lead"] * (-1) ** sum(m for _r, m in item["roots"]) > 0)
    assert all(root_mark["y"] == 0 for root_mark in spec["points"])


@pytest.mark.parametrize("seed", SEEDS)
def test_12661_curve_passes_through_the_three_named_points(seed):
    p = _gen(12661, seed)
    givens = p["math_core"]["givens"]["subject"]
    curve = p["visual_spec"]["curves"][0]["points"]
    for r in givens["roots"]:
        assert f"({r},0)" in p["question_text"].replace("\\", "").replace("{", "").replace("}", "") or f"{r}" in p["question_text"]
        assert abs(_curve_sign_at(curve, float(r))) < 0.35  # the curve meets the x axis at the named abscissa
    assert (curve[-1][1] > 0) == (givens["lead"] > 0)


def _labels(spec: dict) -> dict:
    return {pt.get("label"): pt for pt in spec["points"]}


@pytest.mark.parametrize("seed", SEEDS)
def test_application_figures_carry_the_numbers_of_the_stem(seed):
    p = _gen(12635, seed)
    g = p["math_core"]["givens"]["items"][0]
    spec = p["visual_spec"]
    xs = sorted({round(float(v), 6) for line in spec["lines"] for pt in line["through_points"] for v in [pt[0]]})
    ys = sorted({round(float(v), 6) for line in spec["lines"] for pt in line["through_points"] for v in [pt[1]]})
    assert max(xs) == g["B"] and max(ys) == g["H"] and str(g["B"]) in {pt.get("label") for pt in spec["points"]}
    p = _gen(12645, seed)
    g = p["math_core"]["givens"]["items"][0]
    pts = _labels(p["visual_spec"])
    assert (pts["A"]["x"], pts["A"]["y"]) == (0, 0) and (pts["C"]["x"], pts["C"]["y"]) == (g["s"], g["s"])
    assert pts["P"]["y"] == 0 and pts["Q"]["x"] == g["s"] and pts["P"]["x"] == pts["Q"]["y"]
    p = _gen(12663, seed)
    g = p["math_core"]["givens"]["items"][0]
    marks = {(pt["x"], pt["y"]): pt["label"] for pt in p["visual_spec"]["points"]}  # a square plot has two equal labels
    assert marks[(g["W"] / 2, g["L"])] == str(g["W"]) and marks[(g["W"], g["L"] / 2)] == str(g["L"])
    assert max(pt[0] for line in p["visual_spec"]["lines"] for pt in line["through_points"]) == g["W"]
    assert max(pt[1] for line in p["visual_spec"]["lines"] for pt in line["through_points"]) == g["L"]
    for cid in (12640, 12666):  # the box is a schematic: twelve edges, one x edge and the y edge labelled
        spec = _gen(cid, seed)["visual_spec"]
        assert len(spec["lines"]) == 12 and {line.get("label") for line in spec["lines"] if line.get("label")} == {"x", "y"}
