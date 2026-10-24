"""Sandbox gate for 普高數學1 Unit 9 (一次與二次函數): per-component contract, oracle, grading and figure checks.

Runs against ``tmp/gh_unit9_sandbox_dryrun`` (built by ``build_sandbox.build_all``) with the candidate domain
registered in memory only.  Source oracles are the textbook's worked solutions or hand-derived values
(independent of the domain code).
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from fractions import Fraction
from pathlib import Path

import pytest
import sympy as sp
from sympy.parsing.sympy_parser import convert_xor, implicit_multiplication_application, parse_expr, standard_transformations

from agent_domains_candidate.function_linear_quadratic.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.function_linear_quadratic.unit9_specs import COMPONENTS, DEFERRED, OP, SKILLS, STATIC_COMPONENTS
from agent_domains_candidate.function_linear_quadratic.verification import verify_payload
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = PROJECT_ROOT / "tmp" / "gh_unit9_sandbox_dryrun"
DB = PROJECT_ROOT / "instance" / "kumon_math.db"
SEEDS = range(20)
SURFACE_FLOOR = 18
FIGURE_COMPONENTS = {12566, 12573, 12584, 12591, 12592, 12595, 12596, 12597}
register_candidate_in_memory()

CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]
_T = standard_transformations + (implicit_multiplication_application, convert_xor)


def _load(skill_id: str, cid: int, filename: str):
    path = DRYRUN / skill_id / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"u9_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gen(cid: int, seed: int = 0) -> dict:
    return _load(SKILLS[COMPONENTS[cid][0]], cid, "generate.py").generate(seed=seed)


def _answers(cid: int):
    return _gen(cid)["correct_answer"]


def _same(a: str, b: str) -> bool:
    return sp.simplify(parse_expr(a, transformations=_T) - parse_expr(b, transformations=_T)) == 0


@pytest.mark.parametrize(("cid", "skill_id", "operation"), CASES)
def test_component_contract_oracle_and_grading(cid, skill_id, operation):
    directory = DRYRUN / skill_id / "components" / f"src_{cid}"
    assert {p.name for p in directory.iterdir() if p.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    assert (directory / "get_hint.py").read_text(encoding="utf-8") == _build_get_hint_py()
    generator = _load(skill_id, cid, "generate.py")
    metadata = _load(skill_id, cid, "metadata.py")
    assert metadata.TEXTBOOK_EXAMPLE_ID == cid and metadata.DOMAIN_OPERATION == operation

    surfaces, shapes = set(), set()
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        assert payload == generator.generate(seed=seed)  # deterministic
        assert payload["domain_operation"] == operation and payload["textbook_example_id"] == cid
        assert payload["fixed_domain_key"] == "function.linear_quadratic"
        text = payload["question_text"]
        assert "$$" not in text and "\\\\(" not in text and "承例題" not in text
        assert bool(payload.get("visual_spec")) == (cid in FIGURE_COMPONENTS)
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], (seed, text[:60])
        surfaces.add(json.dumps([text, payload.get("visual_spec"), payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
        contract = payload["answer_contract"]
        shapes.add((contract["answer_type"], contract.get("checker"), tuple((p["key"], p["checker"]) for p in contract.get("parts", []))))
    assert len(shapes) == 1, shapes
    assert len(surfaces) >= (2 if cid in STATIC_COMPONENTS else SURFACE_FLOOR)


def test_coverage_and_deferred_items_are_explicit():
    assert set(COMPONENTS) | set(DEFERRED) == set(range(12560, 12603))
    assert not set(COMPONENTS) & set(DEFERRED)
    assert set(DEFERRED) == {12567, 12568, 12570, 12576, 12587}
    counts = {key: sum(1 for spec in COMPONENTS.values() if spec[0] == key) for key in SKILLS}
    assert counts == {"lin": 8, "quad": 30}


def test_skill_bindings_follow_the_formal_database():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = dict(con.execute("select id, skill_id from textbook_examples where id between 12560 and 12602").fetchall())
    finally:
        con.close()
    assert {cid: SKILLS[spec[0]] for cid, spec in COMPONENTS.items()} == {cid: rows[cid] for cid in COMPONENTS}
    assert all(rows[cid].startswith("gh_") for cid in DEFERRED)


# --- source oracles: the textbook's worked solutions / hand-derived values -------------------------------------------

def test_source_oracles_linear():
    a = _answers(12560)
    assert _same(a["part_1"], "2x-3") and a["part_3"] == "6"
    assert _answers(12561) == "6" and _answers(12565) == "13/4"
    assert _same(_answers(12563), "(2*sqrt(2)+sqrt(5))/3")
    assert _same(_answers(12564), "-2x-3")
    assert _answers(12562) == [3, 4] and _answers(12566) == [1, 3, 4] and _answers(12598) == "B"


def test_source_oracles_quadratic_algebra():
    a = _answers(12569)
    assert [a[f"part_{i}"] for i in range(1, 10)] == ["1", "-1", "3", "3", "2", "-4", "-2", "-3/4", "17/8"]
    a = _answers(12579)
    assert [a[f"part_{i}"] for i in range(1, 10)] == ["1", "-2", "-3", "2", "-1", "-2", "-1", "3/2", "5/4"]
    assert _answers(12571) == {"part_1": "13/4", "part_2": "3/2"} and _answers(12582) == {"part_1": "3/4", "part_2": "-1/2"}
    assert _answers(12583) == "3"
    a = _answers(12572)
    assert [a[f"part_{i}"] for i in range(1, 7)] == ["15", "5", "5", "-1", "5", "-3"]
    a = _answers(12589)
    assert [a[f"part_{i}"] for i in range(1, 5)] == ["8", "-4", "23", "-1"]
    a = _answers(12580)
    assert a == {"part_1": "(-3,2)", "part_2": "x=-3"}
    assert [_answers(c) for c in (12575, 12586, 12590)] == ["k>9", "k<-5", "k<-1"]
    assert _same(_answers(12577).split("=")[1], "3x^2") and _same(_answers(12581), "2x^2+16x+34")
    assert _answers(12578) == {"part_1": "1", "part_2": "-2", "part_3": "-3"} and _answers(12588) == {"part_1": "2", "part_2": "9"}


def test_source_oracles_applications():
    a = _answers(12573)
    assert _same(a["part_1"], "10x^2-20x+240") and a["part_2"] == "1" and a["part_3"] == "230"
    assert _answers(12574) == {"part_1": "-1/5", "part_2": "10", "part_3": "20", "part_4": "75"}
    assert _answers(12585) == {"part_1": "50", "part_2": "300"}
    a = _answers(12584)
    assert _same(a["part_1"], "3*pi") and a["part_2"] == "2"
    assert _answers(12595) == "144" and _answers(12596) == "61/20" and _answers(12597) == "2/3"
    assert _answers(12592) == {"part_1": ["1", "3"], "part_2": "4", "part_3": "2", "part_4": "20"}
    a = _answers(12593)
    assert _same(a["part_1"], "x^2+10x+9") and a["part_2"] == "(-5,-16)"
    assert _answers(12594) == {"part_1": "-1", "part_2": "6"}
    assert _answers(12591) == [1, 2] and [_answers(c) for c in (12599, 12600, 12601, 12602)] == ["A"] * 4


# --- special-attention components --------------------------------------------------------------------------------

def test_12592_keeps_the_three_sub_questions_and_the_complete_conditions():
    p = _gen(12592)
    text = p["question_text"]
    assert all(m in text for m in ("(1)", "(2)", "(3)", "-5x^{2}+20x", "15", "如圖")) and len(p["answer_contract"]["parts"]) == 4


@pytest.mark.parametrize("seed", SEEDS)
def test_12574_table_follows_the_generated_parameters(seed):
    p = _gen(12574, seed)
    g = p["math_core"]["givens"]["items"][0]
    (x1, y1), (x2, y2) = g["revenue"]["points"]
    text = p["question_text"]
    assert f"訂單數量（千個）\t{x1}\t{x2}\n收入（萬元）\t{y1}\t{y2}" in text
    a, b = (sp.Rational(p["correct_answer"][k]) for k in ("part_1", "part_2"))
    assert a * x1 ** 2 + b * x1 == sp.Rational(str(y1)) and a * x2 ** 2 + b * x2 == sp.Rational(str(y2))


@pytest.mark.parametrize("seed", SEEDS)
def test_12573_and_12591_figures_match_the_generated_numbers(seed):
    p = _gen(12591, seed)
    sub = p["math_core"]["givens"]["subject"]
    fig = p["visual_spec"]
    a, r1, r2 = (float(Fraction(str(sub[k]))) for k in ("a", "root1", "root2"))
    assert len(fig["points"]) == 2 and sorted(pt["x"] for pt in fig["points"]) == sorted([r1, r2])
    pts = fig["curves"][0]["points"]
    for r in (r1, r2):  # the drawn curve passes through both labelled x-intercepts
        nearest = min(pts, key=lambda q: abs(q[0] - r))
        assert abs(nearest[1]) <= 0.6 * max(abs(q[1]) for q in pts)
    middle = min(pts, key=lambda q: abs(q[0] - (r1 + r2) / 2))
    assert (middle[1] > 0) == (a < 0)  # between the roots the curve is above the axis exactly when it opens downward
    t = _gen(12573, seed)
    assert {pt["label"] for pt in t["visual_spec"]["points"]} == set("ABCDEF") and "在圖(a)中" in t["question_text"]


@pytest.mark.parametrize("seed", SEEDS)
def test_12566_lines_are_drawn_with_the_generated_slopes(seed):
    p = _gen(12566, seed)
    lines = p["math_core"]["givens"]["subject"]["lines"]
    drawn = p["visual_spec"]["lines"]
    assert len(drawn) == 3
    for (a, b), line in zip(lines, drawn):
        (x1, y1), (x2, y2) = line["through_points"]
        assert float(Fraction(str(a))) == pytest.approx((y2 - y1) / (x2 - x1))
        assert float(Fraction(str(b))) == pytest.approx(y1 - (y2 - y1) / (x2 - x1) * x1)


@pytest.mark.parametrize("seed", SEEDS)
def test_12571_derivation_is_the_textbook_completing_the_square_chain(seed):
    p = _gen(12571, seed)
    steps = " ".join(p["explanation_steps"])
    assert steps.count("=") >= 4 and "\left(x^{2}" in steps  # y = poly = a(x^2+..) = a(x^2+..+(..)^2).. = a(x-h)^2+k


def test_12560_drawing_part_is_a_formal_line_graph_through_the_given_points():
    p = _gen(12560)
    part = p["answer_contract"]["parts"][1]
    spec = part["expected_drawing_spec"]
    assert part["answer_type"] == "drawing" and spec["drawing_type"] == "line_graph"
    assert spec["expected_line"]["points"] == [[2.0, 1.0], [4.0, 5.0]] and spec["slope"] == 2.0 and spec["y_intercept"] == -3.0


def test_parabola_drawing_items_are_deferred_with_a_reason():
    assert all("拋物線" in reason for reason in DEFERRED.values())
